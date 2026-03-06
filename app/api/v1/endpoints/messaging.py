from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.messaging import (
    MessageSendRequest,
    MessageSendResponse,
    SequenceEnrollmentCreateRequest,
    SequenceEnrollmentResponse,
)
from app.db.models import Lead, MessageSent, Sequence, SequenceEnrollment
from app.db.session import get_db
from app.modules.common.audit import write_audit
from app.modules.messaging.policy import (
    check_email_frequency_limit,
    check_sms_cooldown,
    check_sms_window,
    ensure_subscription,
)

router = APIRouter()


@router.post(
    "/sequences/{sequence_id}/enrollments",
    response_model=SequenceEnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sequence_enrollment(
    sequence_id: int,
    payload: SequenceEnrollmentCreateRequest,
    db: Session = Depends(get_db),
) -> SequenceEnrollmentResponse:
    sequence = db.get(Sequence, sequence_id)
    if not sequence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sequence not found")

    lead = db.get(Lead, payload.lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    enrollment = SequenceEnrollment(
        lead_id=payload.lead_id,
        sequence_id=sequence_id,
        status="active",
        current_step=1,
        next_run_at=payload.next_run_at,
    )
    db.add(enrollment)
    db.flush()

    write_audit(
        db,
        event_type="sequence.enrolled",
        entity_type="sequence_enrollment",
        entity_id=str(enrollment.id),
        actor="api",
        payload={"lead_id": payload.lead_id, "sequence_id": sequence_id},
    )

    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.post("/messages/send", response_model=MessageSendResponse, status_code=status.HTTP_201_CREATED)
def send_message(payload: MessageSendRequest, db: Session = Depends(get_db)) -> MessageSendResponse:
    lead = db.get(Lead, payload.lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    channel = payload.channel.lower().strip()
    if channel not in {"email", "sms"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid channel")

    subscription = ensure_subscription(db, payload.lead_id, channel)
    if not subscription.subscribed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lead has unsubscribed from {channel}",
        )

    if channel == "email" and not check_email_frequency_limit(db, payload.lead_id):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Email weekly limit reached")

    if channel == "sms":
        if not check_sms_cooldown(db, payload.lead_id):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="SMS cooldown active")
        if not check_sms_window():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Outside SMS sending window",
            )

    message = MessageSent(
        lead_id=payload.lead_id,
        channel=channel,
        enrollment_id=payload.enrollment_id,
        step_id=payload.step_id,
        external_message_id=payload.external_message_id,
        sent_at=datetime.now(timezone.utc),
        delivered=False,
        opened=False,
        clicked=False,
        replied=False,
        bounced=False,
        unsubscribed=False,
    )

    db.add(message)
    db.flush()

    write_audit(
        db,
        event_type="message.queued",
        entity_type="message",
        entity_id=str(message.id),
        actor="api",
        payload={
            "lead_id": payload.lead_id,
            "channel": channel,
            "enrollment_id": payload.enrollment_id,
        },
    )

    db.commit()

    return MessageSendResponse(
        status="queued",
        message_id=message.id,
        channel=channel,
        lead_id=payload.lead_id,
    )
