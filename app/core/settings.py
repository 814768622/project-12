from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_secret: str = Field(default="change-me", alias="APP_SECRET")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    tz: str = Field(default="America/Toronto", alias="TZ")
    port: int = Field(default=8000, alias="PORT")

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/okeanos", alias="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND")

    cf7_webhook_secret: str = Field(default="change-me", alias="CF7_WEBHOOK_SECRET")
    twilio_webhook_secret: str = Field(default="change-me", alias="TWILIO_WEBHOOK_SECRET")
    gmail_webhook_secret: str = Field(default="change-me", alias="GMAIL_WEBHOOK_SECRET")
    gmail_approval_label: str = Field(default="Okeanos-Approvals", alias="GMAIL_APPROVAL_LABEL")

    hourly_sync_cron: str = Field(default="0 * * * *", alias="HOURLY_SYNC_CRON")
    alert_check_cron: str = Field(default="15 * * * *", alias="ALERT_CHECK_CRON")
    weekly_report_cron: str = Field(default="0 8 * * 1", alias="WEEKLY_REPORT_CRON")

    email_max_per_week: int = Field(default=3, alias="EMAIL_MAX_PER_WEEK")
    sms_cooldown_hours: int = Field(default=48, alias="SMS_COOLDOWN_HOURS")
    sms_send_window_start: str = Field(default="09:00", alias="SMS_SEND_WINDOW_START")
    sms_send_window_end: str = Field(default="20:00", alias="SMS_SEND_WINDOW_END")
    cpa_alert_multiplier: float = Field(default=1.5, alias="CPA_ALERT_MULTIPLIER")
    cpa_critical_multiplier: float = Field(default=2.0, alias="CPA_CRITICAL_MULTIPLIER")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
