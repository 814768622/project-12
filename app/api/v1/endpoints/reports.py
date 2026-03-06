from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.reports import WeeklyReportGenerateRequest, WeeklyReportResponse
from app.db.models import WeeklyReport
from app.db.session import get_db
from app.modules.reporting.service import generate_weekly_report

router = APIRouter()


@router.post(
    "/reports/weekly/generate",
    response_model=WeeklyReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_report(
    payload: WeeklyReportGenerateRequest,
    db: Session = Depends(get_db),
) -> WeeklyReportResponse:
    if bool(payload.period_start) != bool(payload.period_end):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="period_start and period_end must be provided together",
        )

    report = generate_weekly_report(
        db,
        actor=payload.actor,
        period_start=payload.period_start,
        period_end=payload.period_end,
        delivered_to=payload.delivered_to,
    )
    return report


@router.get("/reports/weekly/{report_id}", response_model=WeeklyReportResponse)
def get_weekly_report(report_id: int, db: Session = Depends(get_db)) -> WeeklyReportResponse:
    report = db.get(WeeklyReport, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
