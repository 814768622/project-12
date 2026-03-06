from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.modules.reporting.service import evaluate_anomaly_alerts, generate_weekly_report
from app.worker.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.worker.tasks.hourly_sync_task")
def hourly_sync_task() -> None:
    logger.info("task.hourly_sync.start")
    logger.info("task.hourly_sync.done")


@celery_app.task(name="app.worker.tasks.alert_check_task")
def alert_check_task() -> None:
    logger.info("task.alert_check.start")
    with SessionLocal() as db:
        created_count = evaluate_anomaly_alerts(db)
    logger.info("task.alert_check.generated", created_count=created_count)
    logger.info("task.alert_check.done")


@celery_app.task(name="app.worker.tasks.weekly_report_task")
def weekly_report_task() -> None:
    logger.info("task.weekly_report.start")
    with SessionLocal() as db:
        report = generate_weekly_report(db, actor="scheduler")
    logger.info("task.weekly_report.generated", report_id=report.id)
    logger.info("task.weekly_report.done")
