from app.modules.messaging.policy import settings


def test_sms_window_config_format() -> None:
    start_parts = settings.sms_send_window_start.split(":")
    end_parts = settings.sms_send_window_end.split(":")
    assert len(start_parts) == 2
    assert len(end_parts) == 2
    assert all(part.isdigit() for part in start_parts + end_parts)
