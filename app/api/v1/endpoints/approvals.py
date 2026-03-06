from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.approvals import ApprovalExecuteRequest, ApprovalResponse
from app.db.models import Approval
from app.db.session import get_db
from app.modules.common.audit import write_audit

router = APIRouter()


@router.post("/approvals/{approval_id}/execute", response_model=ApprovalResponse)
def execute_approval(
    approval_id: int,
    payload: ApprovalExecuteRequest,
    db: Session = Depends(get_db),
) -> ApprovalResponse:
    approval = db.get(Approval, approval_id)
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")

    if approval.status == "executed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Approval already executed")

    if approval.expires_at < datetime.now(timezone.utc):
        approval.status = "expired"
        db.add(approval)
        db.commit()
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Approval expired")

    decision = payload.decision.lower()
    if decision not in {"approve", "approved", "reject", "rejected"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid decision")

    if decision in {"reject", "rejected"}:
        approval.status = "rejected"
        approval.decided_by = payload.decided_by
        approval.decided_at = datetime.now(timezone.utc)
        approval.decision_note = payload.note
        db.add(approval)

        write_audit(
            db,
            event_type="approval.rejected",
            entity_type="approval",
            entity_id=str(approval.id),
            actor=payload.decided_by,
            payload={"note": payload.note},
        )

        db.commit()
        db.refresh(approval)
        return approval

    approval.status = "executed"
    approval.decided_by = payload.decided_by
    approval.decided_at = datetime.now(timezone.utc)
    approval.decision_note = payload.note
    db.add(approval)

    write_audit(
        db,
        event_type="approval.executed",
        entity_type="approval",
        entity_id=str(approval.id),
        actor=payload.decided_by,
        payload={"entity_type": approval.entity_type, "entity_id": approval.entity_id},
    )

    db.commit()
    db.refresh(approval)
    return approval
