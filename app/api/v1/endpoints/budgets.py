from decimal import Decimal

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.schemas.budgets import (
    BudgetAllocationSnapshot,
    BudgetGuardrailResponse,
    BudgetGuardrailUpsertRequest,
    BudgetStatusResponse,
)
from app.db.models import BudgetAllocation, BudgetGuardrail
from app.db.session import get_db
from app.modules.common.audit import write_audit

router = APIRouter()


@router.post(
    "/budgets/guardrails",
    response_model=BudgetGuardrailResponse,
    status_code=status.HTTP_201_CREATED,
)
def upsert_budget_guardrail(
    payload: BudgetGuardrailUpsertRequest,
    db: Session = Depends(get_db),
) -> BudgetGuardrailResponse:
    stmt = select(BudgetGuardrail).where(
        BudgetGuardrail.platform == payload.platform,
        BudgetGuardrail.season_name == payload.season_name,
    )
    guardrail = db.scalar(stmt)
    created = False

    if not guardrail:
        guardrail = BudgetGuardrail(platform=payload.platform, season_name=payload.season_name)
        created = True

    for key, value in payload.model_dump(exclude={"platform", "season_name"}).items():
        setattr(guardrail, key, value)

    db.add(guardrail)
    db.flush()

    write_audit(
        db,
        event_type="budget.guardrail_created" if created else "budget.guardrail_updated",
        entity_type="budget_guardrail",
        entity_id=str(guardrail.id),
        actor="api",
        payload=payload.model_dump(mode="json"),
    )

    db.commit()
    db.refresh(guardrail)
    return guardrail


@router.get("/budgets/status", response_model=BudgetStatusResponse)
def get_budget_status(db: Session = Depends(get_db)) -> BudgetStatusResponse:
    allocations = db.scalars(
        select(BudgetAllocation).order_by(BudgetAllocation.updated_at.desc()).limit(30)
    ).all()

    total_allocated = sum((x.allocated_amount_cad for x in allocations), Decimal("0"))
    total_spent = sum((x.spent_amount_cad for x in allocations), Decimal("0"))

    return BudgetStatusResponse(
        allocation_count=len(allocations),
        total_allocated_cad=total_allocated,
        total_spent_cad=total_spent,
        allocations=[BudgetAllocationSnapshot.model_validate(x) for x in allocations],
    )
