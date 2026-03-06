from datetime import datetime, timezone

from app.modules.reporting.service import resolve_custom_period, resolve_previous_week_period


def test_resolve_custom_period_rejects_inverted_dates() -> None:
    try:
        resolve_custom_period(period_start=datetime(2026, 3, 10).date(), period_end=datetime(2026, 3, 1).date())
        assert False, "Expected ValueError"
    except ValueError:
        assert True


def test_resolve_previous_week_period_has_7_days() -> None:
    period = resolve_previous_week_period(datetime(2026, 3, 17, 12, 0, tzinfo=timezone.utc))
    delta = (period.period_end - period.period_start).days
    assert delta == 6
