from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.models import (
    AdCreative,
    AdMetricHourly,
    Alert,
    BudgetAllocation,
    BudgetGuardrail,
    Lead,
    MessageSent,
    MetricSnapshot,
    WeeklyReport,
)
from app.modules.common.audit import write_audit

settings = get_settings()


@dataclass
class ReportPeriod:
    period_start: date
    period_end: date
    start_utc: datetime
    end_exclusive_utc: datetime



def resolve_previous_week_period(reference_utc: datetime | None = None) -> ReportPeriod:
    tz = ZoneInfo(settings.tz)
    ref = reference_utc or datetime.now(timezone.utc)
    ref_local = ref.astimezone(tz)

    this_week_monday = (ref_local - timedelta(days=ref_local.weekday())).date()
    period_end = this_week_monday - timedelta(days=1)
    period_start = period_end - timedelta(days=6)

    local_start = datetime.combine(period_start, time.min, tzinfo=tz)
    local_end_exclusive = datetime.combine(period_end + timedelta(days=1), time.min, tzinfo=tz)

    return ReportPeriod(
        period_start=period_start,
        period_end=period_end,
        start_utc=local_start.astimezone(timezone.utc),
        end_exclusive_utc=local_end_exclusive.astimezone(timezone.utc),
    )


def resolve_custom_period(period_start: date, period_end: date) -> ReportPeriod:
    if period_start > period_end:
        raise ValueError("period_start must be <= period_end")

    tz = ZoneInfo(settings.tz)
    local_start = datetime.combine(period_start, time.min, tzinfo=tz)
    local_end_exclusive = datetime.combine(period_end + timedelta(days=1), time.min, tzinfo=tz)

    return ReportPeriod(
        period_start=period_start,
        period_end=period_end,
        start_utc=local_start.astimezone(timezone.utc),
        end_exclusive_utc=local_end_exclusive.astimezone(timezone.utc),
    )


def _sum_decimal(db: Session, stmt) -> Decimal:
    value = db.scalar(stmt)
    if value is None:
        return Decimal("0")
    return Decimal(value)


def _compute_recommendations(avg_cpa: Decimal | None, total_leads: int) -> str:
    messages: list[str] = []

    if avg_cpa is not None and avg_cpa > Decimal("2000"):
        messages.append("CPA above target range; prioritize creative and audience refresh this week.")
    if total_leads < 5:
        messages.append("Lead volume below weekly trajectory; increase top-performing channel budget cautiously.")
    if not messages:
        messages.append("Performance is stable; continue current mix and monitor creative fatigue.")

    return " ".join(messages)


def generate_weekly_report(
    db: Session,
    *,
    actor: str = "system",
    period_start: date | None = None,
    period_end: date | None = None,
    delivered_to: list[str] | None = None,
) -> WeeklyReport:
    if period_start and period_end:
        period = resolve_custom_period(period_start, period_end)
    else:
        period = resolve_previous_week_period()

    spend_stmt = select(func.coalesce(func.sum(AdMetricHourly.spend_cad), 0)).where(
        and_(
            AdMetricHourly.hour_bucket >= period.start_utc,
            AdMetricHourly.hour_bucket < period.end_exclusive_utc,
        )
    )
    conversions_stmt = select(func.coalesce(func.sum(AdMetricHourly.conversions), 0)).where(
        and_(
            AdMetricHourly.hour_bucket >= period.start_utc,
            AdMetricHourly.hour_bucket < period.end_exclusive_utc,
        )
    )

    total_spend = _sum_decimal(db, spend_stmt)
    total_conversions = int(db.scalar(conversions_stmt) or 0)
    avg_cpa = (total_spend / Decimal(total_conversions)) if total_conversions > 0 else None

    total_leads = int(
        db.scalar(
            select(func.count(Lead.id)).where(
                and_(Lead.created_at >= period.start_utc, Lead.created_at < period.end_exclusive_utc)
            )
        )
        or 0
    )

    leads_by_source_rows = db.execute(
        select(Lead.source, func.count(Lead.id))
        .where(and_(Lead.created_at >= period.start_utc, Lead.created_at < period.end_exclusive_utc))
        .group_by(Lead.source)
    ).all()
    leads_by_source = {row[0]: int(row[1]) for row in leads_by_source_rows}

    email_sent = int(
        db.scalar(
            select(func.count(MessageSent.id)).where(
                and_(
                    MessageSent.channel == "email",
                    MessageSent.sent_at >= period.start_utc,
                    MessageSent.sent_at < period.end_exclusive_utc,
                )
            )
        )
        or 0
    )
    sms_sent = int(
        db.scalar(
            select(func.count(MessageSent.id)).where(
                and_(
                    MessageSent.channel == "sms",
                    MessageSent.sent_at >= period.start_utc,
                    MessageSent.sent_at < period.end_exclusive_utc,
                )
            )
        )
        or 0
    )

    top_creatives_rows = db.execute(
        select(AdCreative.id, AdCreative.campaign_id, AdCreative.cpa)
        .where(AdCreative.cpa.is_not(None))
        .order_by(AdCreative.cpa.asc())
        .limit(3)
    ).all()
    bottom_creatives_rows = db.execute(
        select(AdCreative.id, AdCreative.campaign_id, AdCreative.cpa)
        .where(AdCreative.cpa.is_not(None))
        .order_by(AdCreative.cpa.desc())
        .limit(3)
    ).all()

    top_creatives = [
        {"creative_id": int(row[0]), "campaign_id": int(row[1]), "cpa": str(row[2])}
        for row in top_creatives_rows
    ]
    bottom_creatives = [
        {"creative_id": int(row[0]), "campaign_id": int(row[1]), "cpa": str(row[2])}
        for row in bottom_creatives_rows
    ]

    recommendations = _compute_recommendations(avg_cpa, total_leads)
    report_json = {
        "kpis": {
            "total_spend_cad": str(total_spend),
            "avg_cpa_cad": str(avg_cpa) if avg_cpa is not None else None,
            "total_leads": total_leads,
            "total_conversions": total_conversions,
        },
        "leads_by_source": leads_by_source,
        "email_sms_summary": {"email_sent": email_sent, "sms_sent": sms_sent},
        "top_creatives": top_creatives,
        "bottom_creatives": bottom_creatives,
    }

    report = WeeklyReport(
        period_start=period.period_start,
        period_end=period.period_end,
        total_spend_cad=total_spend,
        avg_cpa_cad=avg_cpa,
        total_leads=total_leads,
        report_json=report_json,
        recommendations_text=recommendations,
        delivered_to_json=delivered_to or [],
    )
    db.add(report)
    db.flush()

    metric_rows = [
        MetricSnapshot(
            metric_name="total_spend_cad",
            metric_value=total_spend,
            dimension_json={"scope": "weekly_report", "report_id": report.id},
            period_type="weekly",
            period_start=period.period_start,
            period_end=period.period_end,
        ),
        MetricSnapshot(
            metric_name="total_leads",
            metric_value=Decimal(total_leads),
            dimension_json={"scope": "weekly_report", "report_id": report.id},
            period_type="weekly",
            period_start=period.period_start,
            period_end=period.period_end,
        ),
    ]

    if avg_cpa is not None:
        metric_rows.append(
            MetricSnapshot(
                metric_name="avg_cpa_cad",
                metric_value=avg_cpa,
                dimension_json={"scope": "weekly_report", "report_id": report.id},
                period_type="weekly",
                period_start=period.period_start,
                period_end=period.period_end,
            )
        )

    db.add_all(metric_rows)

    write_audit(
        db,
        event_type="report.weekly_generated",
        entity_type="weekly_report",
        entity_id=str(report.id),
        actor=actor,
        payload={
            "period_start": str(period.period_start),
            "period_end": str(period.period_end),
        },
    )

    db.commit()
    db.refresh(report)
    return report


def _create_alert_if_needed(
    db: Session,
    *,
    alert_type: str,
    platform: str | None,
    threshold_value: Decimal,
    current_value: Decimal,
) -> bool:
    recent = db.scalar(
        select(Alert)
        .where(
            Alert.alert_type == alert_type,
            Alert.platform == platform,
            Alert.status == "open",
        )
        .order_by(Alert.triggered_at.desc())
        .limit(1)
    )
    if recent:
        return False

    alert = Alert(
        alert_type=alert_type,
        platform=platform,
        threshold_value=threshold_value,
        current_value=current_value,
        status="open",
    )
    db.add(alert)
    return True


def evaluate_anomaly_alerts(db: Session) -> int:
    created = 0
    now_utc = datetime.now(timezone.utc)

    seven_days_ago = now_utc - timedelta(days=7)
    total_spend_7d = _sum_decimal(
        db,
        select(func.coalesce(func.sum(AdMetricHourly.spend_cad), 0)).where(
            and_(AdMetricHourly.hour_bucket >= seven_days_ago, AdMetricHourly.hour_bucket < now_utc)
        ),
    )

    weekly_budget = _sum_decimal(
        db,
        select(func.coalesce(func.sum(BudgetAllocation.allocated_amount_cad), 0)).where(
            and_(BudgetAllocation.period_type == "weekly", BudgetAllocation.period_end >= date.today())
        ),
    )
    if weekly_budget > 0:
        spend_threshold = weekly_budget * Decimal("0.9")
        if total_spend_7d > spend_threshold:
            if _create_alert_if_needed(
                db,
                alert_type="spend_cap",
                platform="total",
                threshold_value=spend_threshold,
                current_value=total_spend_7d,
            ):
                created += 1

    today_start = now_utc - timedelta(hours=24)
    leads_today = int(
        db.scalar(select(func.count(Lead.id)).where(and_(Lead.created_at >= today_start, Lead.created_at < now_utc)))
        or 0
    )
    leads_7d = int(
        db.scalar(select(func.count(Lead.id)).where(and_(Lead.created_at >= seven_days_ago, Lead.created_at < now_utc)))
        or 0
    )
    avg_daily = Decimal(leads_7d) / Decimal("7") if leads_7d > 0 else Decimal("0")
    lead_threshold = avg_daily * Decimal("0.7")
    if avg_daily > 0 and Decimal(leads_today) < lead_threshold:
        if _create_alert_if_needed(
            db,
            alert_type="lead_drop",
            platform="total",
            threshold_value=lead_threshold,
            current_value=Decimal(leads_today),
        ):
            created += 1

    for platform in ("meta", "google", "tiktok"):
        spend = _sum_decimal(
            db,
            select(func.coalesce(func.sum(AdMetricHourly.spend_cad), 0)).where(
                and_(
                    AdMetricHourly.platform == platform,
                    AdMetricHourly.hour_bucket >= seven_days_ago,
                    AdMetricHourly.hour_bucket < now_utc,
                )
            ),
        )
        conversions = int(
            db.scalar(
                select(func.coalesce(func.sum(AdMetricHourly.conversions), 0)).where(
                    and_(
                        AdMetricHourly.platform == platform,
                        AdMetricHourly.hour_bucket >= seven_days_ago,
                        AdMetricHourly.hour_bucket < now_utc,
                    )
                )
            )
            or 0
        )
        if conversions <= 0:
            continue

        cpa = spend / Decimal(conversions)
        guardrail = db.scalar(
            select(BudgetGuardrail)
            .where(BudgetGuardrail.platform == platform, BudgetGuardrail.active.is_(True))
            .order_by(BudgetGuardrail.updated_at.desc())
            .limit(1)
        )
        if not guardrail or guardrail.cpa_target_high is None:
            continue

        threshold = Decimal(guardrail.cpa_target_high) * Decimal(str(settings.cpa_critical_multiplier))
        if cpa > threshold:
            if _create_alert_if_needed(
                db,
                alert_type="cpa_spike",
                platform=platform,
                threshold_value=threshold,
                current_value=cpa,
            ):
                created += 1

    if created > 0:
        write_audit(
            db,
            event_type="alerts.generated",
            entity_type="alert",
            entity_id="bulk",
            actor="system",
            payload={"count": created},
        )

    db.commit()
    return created
