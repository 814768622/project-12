from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.schemas.leads import LeadPatchRequest, LeadResponse, LeadTagRequest
from app.db.models import Lead, LeadStageHistory, LeadTag
from app.db.session import get_db

router = APIRouter()



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


@router.get("/leads", response_model=list[LeadResponse])
def list_leads(
    db: Session = Depends(get_db),
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    source: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[LeadResponse]:
    stmt = select(Lead).order_by(Lead.created_at.desc()).limit(limit).offset(offset)

    if status_filter:
        stmt = stmt.where(Lead.status == status_filter)
    if source:
        stmt = stmt.where(Lead.source == source)

    rows = db.scalars(stmt).all()
    return [_to_response(x) for x in rows]


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)) -> LeadResponse:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return _to_response(lead)


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
def patch_lead(lead_id: int, payload: LeadPatchRequest, db: Session = Depends(get_db)) -> LeadResponse:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    old_status = lead.status

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)

    if payload.status and payload.status != old_status:
        db.add(
            LeadStageHistory(
                lead_id=lead.id,
                previous_stage=old_status,
                new_stage=payload.status,
                changed_by="api",
            )
        )

    db.add(lead)
    db.commit()
    db.refresh(lead)
    return _to_response(lead)


@router.post("/leads/{lead_id}/tags", response_model=LeadResponse)
def add_lead_tag(lead_id: int, payload: LeadTagRequest, db: Session = Depends(get_db)) -> LeadResponse:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    tag = payload.tag.strip().lower()
    if not tag:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tag is required")

    exists = db.scalar(select(LeadTag).where(LeadTag.lead_id == lead_id, LeadTag.tag == tag))
    if not exists:
        db.add(LeadTag(lead_id=lead_id, tag=tag))
        db.commit()
        db.refresh(lead)

    return _to_response(lead)
