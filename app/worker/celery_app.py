from celery import Celery
from celery.schedules import crontab

from app.core.settings import get_settings

settings = get_settings()


def _parse_cron(expr: str):
    parts = expr.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {expr}")
    minute, hour, day_of_month, month_of_year, day_of_week = parts
    return crontab(
        minute=minute,
        hour=hour,
        day_of_month=day_of_month,
        month_of_year=month_of_year,
        day_of_week=day_of_week,
    )

celery_app = Celery(
    "okeanos",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.timezone = settings.tz
celery_app.conf.beat_schedule = {
    "hourly-sync": {
        "task": "app.worker.tasks.hourly_sync_task",
        "schedule": _parse_cron(settings.hourly_sync_cron),
    },
    "alert-check": {
        "task": "app.worker.tasks.alert_check_task",
        "schedule": _parse_cron(settings.alert_check_cron),
    },
    "weekly-report": {
        "task": "app.worker.tasks.weekly_report_task",
        "schedule": _parse_cron(settings.weekly_report_cron),
    },
}

celery_app.autodiscover_tasks(["app.worker"])
