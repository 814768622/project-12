from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.schemas.audiences import AudienceSyncRequest, AudienceSyncResponse
from app.db.models import AudienceSegment
from app.db.session import get_db
from app.modules.common.audit import write_audit

router = APIRouter()


@router.post("/audiences/sync", response_model=AudienceSyncResponse)
def sync_audiences(payload: AudienceSyncRequest, db: Session = Depends(get_db)) -> AudienceSyncResponse:
    if payload.segment_ids:
        stmt = select(AudienceSegment).where(AudienceSegment.id.in_(payload.segment_ids))
        segments = db.scalars(stmt).all()
    else:
        segments = db.scalars(select(AudienceSegment).where(AudienceSegment.status == "active")).all()

    write_audit(
        db,
        event_type="audience.sync_requested",
        entity_type="audience_segment",
        entity_id="bulk",
        actor=payload.triggered_by,
        payload={
            "dry_run": payload.dry_run,
            "segment_ids": payload.segment_ids,
            "resolved_count": len(segments),
        },
    )
    db.commit()

    return AudienceSyncResponse(
        status="queued" if not payload.dry_run else "dry_run",
        queued_segments=len(segments),
        dry_run=payload.dry_run,
    )
