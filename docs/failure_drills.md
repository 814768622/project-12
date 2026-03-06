# Okeanos Failure Drills

Date: 2026-03-03

## Drill 1: Connector Outage

Goal:
1. Verify system behavior when one ad platform is unavailable.

Steps:
1. Invalidate one platform token in staging.
2. Trigger `POST /v1/connectors/{platform}/sync-hourly`.
3. Confirm failure is logged and does not crash worker.
4. Restore token and rerun.

Success criteria:
1. Failure captured in logs and `sync_runs`.
2. Other platform flows continue normally.

## Drill 2: SMS Unsubscribe Compliance

Goal:
1. Verify STOP flow updates subscription within 24h (immediate in system).

Steps:
1. Send Twilio webhook payload with `Body=STOP`.
2. Confirm `channel_subscriptions` for `sms` is `subscribed=false`.
3. Attempt `POST /v1/messages/send` with `channel=sms`.

Success criteria:
1. SMS send is blocked with conflict response.
2. Audit log records unsubscribe event.

## Drill 3: Report Recovery

Goal:
1. Verify manual recovery when scheduled weekly report fails.

Steps:
1. Simulate scheduler job failure.
2. Trigger manual `POST /v1/reports/weekly/generate`.
3. Validate report persistence and returned report id.

Success criteria:
1. Manual report generation succeeds.
2. Stakeholder report delivery can continue.
