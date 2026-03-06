from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.models import ChannelSubscription, MessageSent

settings = get_settings()


def ensure_subscription(db: Session, lead_id: int, channel: str) -> ChannelSubscription:
    sub = db.scalar(
        select(ChannelSubscription).where(
            ChannelSubscription.lead_id == lead_id,
            ChannelSubscription.channel == channel,
        )
    )
    if sub:
        return sub

    sub = ChannelSubscription(lead_id=lead_id, channel=channel, subscribed=True)
    db.add(sub)
    db.flush()
    return sub


def check_email_frequency_limit(db: Session, lead_id: int) -> bool:
    lookback = datetime.now(timezone.utc) - timedelta(days=7)
    count = db.scalar(
        select(func.count(MessageSent.id)).where(
            and_(
                MessageSent.lead_id == lead_id,
                MessageSent.channel == "email",
                MessageSent.sent_at >= lookback,
            )
        )
    )
    return int(count or 0) < settings.email_max_per_week


def check_sms_cooldown(db: Session, lead_id: int) -> bool:
    latest_sms = db.scalar(
        select(MessageSent)
        .where(MessageSent.lead_id == lead_id, MessageSent.channel == "sms")
        .order_by(MessageSent.sent_at.desc())
        .limit(1)
    )
    if not latest_sms:
        return True

    min_allowed = datetime.now(timezone.utc) - timedelta(hours=settings.sms_cooldown_hours)
    return latest_sms.sent_at <= min_allowed


def check_sms_window() -> bool:
    tz = ZoneInfo(settings.tz)
    now_local = datetime.now(tz).time()
    start_hour, start_minute = [int(x) for x in settings.sms_send_window_start.split(":", 1)]
    end_hour, end_minute = [int(x) for x in settings.sms_send_window_end.split(":", 1)]

    start_time = now_local.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    end_time = now_local.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    return start_time <= now_local <= end_time
