from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class BudgetGuardrailUpsertRequest(BaseModel):
    platform: str
    season_name: str
    min_daily_spend: Decimal | None = None
    max_daily_spend: Decimal | None = None
    max_platform_share_pct: Decimal | None = None
    cpa_target_low: Decimal | None = None
    cpa_target_high: Decimal | None = None
    active: bool = True


class BudgetGuardrailResponse(BaseModel):
    id: int
    platform: str
    season_name: str
    min_daily_spend: Decimal | None
    max_daily_spend: Decimal | None
    max_platform_share_pct: Decimal | None
    cpa_target_low: Decimal | None
    cpa_target_high: Decimal | None
    active: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class BudgetAllocationSnapshot(BaseModel):
    id: int
    period_type: str
    period_start: date
    period_end: date
    platform: str
    allocated_amount_cad: Decimal
    spent_amount_cad: Decimal
    remaining_cad: Decimal
    cpa_actual: Decimal | None
    cpa_target: Decimal | None
    status: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class BudgetStatusResponse(BaseModel):
    allocation_count: int
    total_allocated_cad: Decimal
    total_spent_cad: Decimal
    allocations: list[BudgetAllocationSnapshot]
