from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.schemas.leads import CF7LeadPayload, LeadResponse
from app.api.v1.schemas.messaging import GmailInboundPayload, TwilioWebhookPayload
from app.core.settings import get_settings
from app.db.models import ChannelSubscription, Lead
from app.db.session import get_db
from app.modules.common.audit import write_audit

router = APIRouter()
settings = get_settings()



def _to_response(lead: Lead) -> LeadResponse:
    return LeadResponse(
        id=lead.id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        email=lead.email,
        phone=lead.phone,
        source=lead.source,
        status=lead.status,
        score=lead.score,
        notes=lead.notes,
        metadata_json=lead.metadata_json or {},
        tags=[x.tag for x in lead.tags],
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )


def _ensure_subscription(db: Session, lead_id: int, channel: str, source: str) -> None:
    sub = db.scalar(
        select(ChannelSubscription).where(
            ChannelSubscription.lead_id == lead_id,
            ChannelSubscription.channel == channel,
        )
    )
    if not sub:
        db.add(ChannelSubscription(lead_id=lead_id, channel=channel, subscribed=True, source=source))


@router.post("/webhooks/cf7/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def ingest_cf7_lead(
    payload: CF7LeadPayload,
    db: Session = Depends(get_db),
    x_cf7_secret: str | None = Header(default=None, alias="X-CF7-Secret"),
) -> LeadResponse:
    if x_cf7_secret != settings.cf7_webhook_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")

    if not payload.email and not payload.phone:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least email or phone is required",
        )

    lead = Lead(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=str(payload.email) if payload.email else None,
        phone=payload.phone,
        source=payload.source,
        status="new",
        score=0,
        notes=payload.message,
        metadata_json=payload.metadata_json,
    )

    db.add(lead)
    db.flush()

    if lead.email:
        _ensure_subscription(db, lead.id, "email", "cf7")
    if lead.phone:
        _ensure_subscription(db, lead.id, "sms", "cf7")

    write_audit(
        db,
        event_type="lead.ingested_cf7",
        entity_type="lead",
        entity_id=str(lead.id),
        actor="cf7_webhook",
        payload={"source": payload.source},
    )

    db.commit()
    db.refresh(lead)
    return _to_response(lead)


@router.post("/webhooks/twilio/status", status_code=status.HTTP_202_ACCEPTED)
def twilio_status_webhook(
    payload: TwilioWebhookPayload,
    db: Session = Depends(get_db),
    x_twilio_secret: str | None = Header(default=None, alias="X-Twilio-Secret"),
) -> dict[str, str]:
    if x_twilio_secret != settings.twilio_webhook_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")

    lead = db.scalar(select(Lead).where(Lead.phone == payload.from_phone).limit(1))
    if not lead:
        return {"status": "ignored"}

    body = payload.body.strip().upper()
    if body == "STOP":
        sub = db.scalar(
            select(ChannelSubscription).where(
                ChannelSubscription.lead_id == lead.id,
                ChannelSubscription.channel == "sms",
            )
        )
        if sub:
            sub.subscribed = False
            sub.unsubscribed_at = datetime.now(timezone.utc)
            sub.source = "twilio_stop"
            db.add(sub)
        else:
            db.add(
                ChannelSubscription(
                    lead_id=lead.id,
                    channel="sms",
                    subscribed=False,
                    unsubscribed_at=datetime.now(timezone.utc),
                    source="twilio_stop",
                )
            )

        write_audit(
            db,
            event_type="subscription.unsubscribed",
            entity_type="lead",
            entity_id=str(lead.id),
            actor="twilio_webhook",
            payload={"channel": "sms", "reason": "STOP"},
        )
        db.commit()

    return {"status": "accepted"}


@router.post("/webhooks/gmail/inbound", status_code=status.HTTP_202_ACCEPTED)
def gmail_inbound_webhook(
    payload: GmailInboundPayload,
    db: Session = Depends(get_db),
    x_gmail_secret: str | None = Header(default=None, alias="X-Gmail-Secret"),
) -> dict[str, str]:
    if x_gmail_secret != settings.gmail_webhook_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")

    lead = db.scalar(select(Lead).where(Lead.email == str(payload.from_email)).limit(1))
    if not lead:
        return {"status": "ignored"}

    text = f"{payload.subject or ''}\n{payload.body}".upper()
    if "UNSUBSCRIBE" in text or "STOP" in text:
        sub = db.scalar(
            select(ChannelSubscription).where(
                ChannelSubscription.lead_id == lead.id,
                ChannelSubscription.channel == "email",
            )
        )
        if sub:
            sub.subscribed = False
            sub.unsubscribed_at = datetime.now(timezone.utc)
            sub.source = "gmail_unsubscribe"
            db.add(sub)
        else:
            db.add(
                ChannelSubscription(
                    lead_id=lead.id,
                    channel="email",
                    subscribed=False,
                    unsubscribed_at=datetime.now(timezone.utc),
                    source="gmail_unsubscribe",
                )
            )

        write_audit(
            db,
            event_type="subscription.unsubscribed",
            entity_type="lead",
            entity_id=str(lead.id),
            actor="gmail_webhook",
            payload={"channel": "email", "reason": "inbound_unsubscribe"},
        )
        db.commit()

    return {"status": "accepted"}
