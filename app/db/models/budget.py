from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BudgetGuardrail(Base):
    __tablename__ = "budget_guardrails"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    season_name: Mapped[str] = mapped_column(String(20), nullable=False)
    min_daily_spend: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    max_daily_spend: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    max_platform_share_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    cpa_target_low: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    cpa_target_high: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BudgetAllocation(Base):
    __tablename__ = "budget_allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    allocated_amount_cad: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    spent_amount_cad: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    remaining_cad: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    cpa_actual: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    cpa_target: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
