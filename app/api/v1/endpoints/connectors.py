from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.connectors import ConnectorSyncResponse
from app.db.models import SyncRun
from app.db.session import get_db
from app.modules.common.audit import write_audit

router = APIRouter()

ALLOWED_PLATFORMS = {"meta", "google", "tiktok"}


@router.post(
    "/connectors/{platform}/sync-hourly",
    response_model=ConnectorSyncResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def trigger_hourly_sync(platform: str, db: Session = Depends(get_db)) -> ConnectorSyncResponse:
    platform_key = platform.lower().strip()
    if platform_key not in ALLOWED_PLATFORMS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported platform")

    sync_run = SyncRun(
        job_name="manual_hourly_sync",
        platform=platform_key,
        status="running",
        metadata_json={"trigger": "api"},
    )
    db.add(sync_run)
    db.flush()

    write_audit(
        db,
        event_type="connector.sync_requested",
        entity_type="sync_run",
        entity_id=str(sync_run.id),
        actor="api",
        payload={"platform": platform_key},
    )

    db.commit()
    db.refresh(sync_run)

    return ConnectorSyncResponse(
        sync_run_id=sync_run.id,
        platform=platform_key,
        status="accepted",
        started_at=sync_run.started_at,
    )
