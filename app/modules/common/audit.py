from sqlalchemy.orm import Session

from app.db.models import AuditLog



def write_audit(
    db: Session,
    *,
    event_type: str,
    entity_type: str,
    entity_id: str,
    actor: str | None = None,
    payload: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor=actor,
            payload_json=payload or {},
        )
    )
