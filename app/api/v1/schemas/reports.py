from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class WeeklyReportGenerateRequest(BaseModel):
    period_start: date | None = None
    period_end: date | None = None
    delivered_to: list[str] = Field(default_factory=list)
    actor: str = "api"


class WeeklyReportResponse(BaseModel):
    id: int
    period_start: date
    period_end: date
    total_spend_cad: Decimal | None
    avg_cpa_cad: Decimal | None
    total_leads: int | None
    report_json: dict
    recommendations_text: str | None
    generated_at: datetime
    delivered_to_json: list

    model_config = {"from_attributes": True}
