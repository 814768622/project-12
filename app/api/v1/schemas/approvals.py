from datetime import datetime

from pydantic import BaseModel, Field


class ApprovalRequestCreate(BaseModel):
    approval_type: str = "campaign_change"
    payload_json: dict = Field(default_factory=dict)
    requested_by: str = "api"
    expires_in_hours: int = 24


class ApprovalExecuteRequest(BaseModel):
    decision: str = "approve"
    decided_by: str = "api"
    note: str | None = None


class ApprovalResponse(BaseModel):
    id: int
    approval_type: str
    entity_type: str
    entity_id: str
    payload_json: dict
    payload_hash: str
    status: str
    requested_by: str
    requested_at: datetime
    decided_by: str | None
    decided_at: datetime | None
    expires_at: datetime
    decision_note: str | None

    model_config = {"from_attributes": True}
