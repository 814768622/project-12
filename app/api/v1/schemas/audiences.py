from pydantic import BaseModel, Field


class AudienceSyncRequest(BaseModel):
    segment_ids: list[int] = Field(default_factory=list)
    dry_run: bool = True
    triggered_by: str = "api"


class AudienceSyncResponse(BaseModel):
    status: str
    queued_segments: int
    dry_run: bool
