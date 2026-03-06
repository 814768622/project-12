from fastapi import APIRouter

from app.api.v1.endpoints.approvals import router as approvals_router
from app.api.v1.endpoints.audiences import router as audiences_router
from app.api.v1.endpoints.budgets import router as budgets_router
from app.api.v1.endpoints.campaigns import router as campaigns_router
from app.api.v1.endpoints.connectors import router as connectors_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.leads import router as leads_router
from app.api.v1.endpoints.messaging import router as messaging_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.webhooks import router as webhooks_router

v1_router = APIRouter()
v1_router.include_router(health_router, tags=["health"])
v1_router.include_router(webhooks_router, tags=["webhooks"])
v1_router.include_router(leads_router, tags=["leads"])
v1_router.include_router(messaging_router, tags=["messaging"])
v1_router.include_router(reports_router, tags=["reports"])
v1_router.include_router(connectors_router, tags=["connectors"])
v1_router.include_router(campaigns_router, tags=["campaigns"])
v1_router.include_router(approvals_router, tags=["approvals"])
v1_router.include_router(budgets_router, tags=["budgets"])
v1_router.include_router(audiences_router, tags=["audiences"])
