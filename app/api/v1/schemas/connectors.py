from datetime import datetime

from pydantic import BaseModel


class ConnectorSyncResponse(BaseModel):
    sync_run_id: int
    platform: str
    status: str
    started_at: datetime
