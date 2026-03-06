from datetime import datetime, timedelta, timezone
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.schemas.approvals import ApprovalRequestCreate, ApprovalResponse
from app.api.v1.schemas.campaigns import (
    AdCreativeCreateRequest,
    AdCreativeResponse,
    CampaignCreateRequest,
    CampaignResponse,
)
from app.db.models import AdCreative, Approval, Campaign
from app.db.session import get_db
from app.modules.common.audit import write_audit

router = APIRouter()


@router.post("/campaigns", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(payload: CampaignCreateRequest, db: Session = Depends(get_db)) -> CampaignResponse:
    campaign = Campaign(**payload.model_dump())
    db.add(campaign)
    db.flush()

    write_audit(
        db,
        event_type="campaign.created",
        entity_type="campaign",
        entity_id=str(campaign.id),
        actor=payload.created_by,
        payload=payload.model_dump(mode="json"),
    )

    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("/campaigns", response_model=list[CampaignResponse])
def list_campaigns(
    db: Session = Depends(get_db),
    platform: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[CampaignResponse]:
    stmt = select(Campaign).order_by(Campaign.created_at.desc()).limit(limit).offset(offset)
    if platform:
        stmt = stmt.where(Campaign.platform == platform)
    if status_filter:
        stmt = stmt.where(Campaign.status == status_filter)

    return db.scalars(stmt).all()


@router.post(
    "/campaigns/{campaign_id}/creatives",
    response_model=AdCreativeResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_campaign_creative(
    campaign_id: int,
    payload: AdCreativeCreateRequest,
    db: Session = Depends(get_db),
) -> AdCreativeResponse:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    creative = AdCreative(campaign_id=campaign_id, **payload.model_dump())
    db.add(creative)
    db.flush()

    write_audit(
        db,
        event_type="campaign.creative_added",
        entity_type="campaign",
        entity_id=str(campaign_id),
        actor="api",
        payload={"creative_id": creative.id, **payload.model_dump(mode="json")},
    )

    db.commit()
    db.refresh(creative)
    return creative


@router.post(
    "/campaigns/{campaign_id}/approval-requests",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_campaign_approval(
    campaign_id: int,
    payload: ApprovalRequestCreate,
    db: Session = Depends(get_db),
) -> ApprovalResponse:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    payload_json = payload.payload_json or {"campaign_id": campaign_id}
    payload_hash = hashlib.sha256(json.dumps(payload_json, sort_keys=True).encode("utf-8")).hexdigest()

    approval = Approval(
        approval_type=payload.approval_type,
        entity_type="campaign",
        entity_id=str(campaign_id),
        payload_json=payload_json,
        payload_hash=payload_hash,
        status="pending",
        requested_by=payload.requested_by,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=payload.expires_in_hours),
    )
    db.add(approval)
    db.flush()

    write_audit(
        db,
        event_type="approval.requested",
        entity_type="approval",
        entity_id=str(approval.id),
        actor=payload.requested_by,
        payload={"campaign_id": campaign_id, "approval_type": payload.approval_type},
    )

    db.commit()
    db.refresh(approval)
    return approval
