# Okeanos Go-Live Checklist

Date: 2026-03-03

## Pre-Launch

1. All required env vars configured in Railway.
2. Migrations applied successfully.
3. `/v1/health` and `/v1/health/ready` pass.
4. Celery worker and scheduler running.
5. Weekly report dry run completed.
6. Alert check dry run completed.
7. CF7/Twilio/Gmail webhook secrets verified.
8. SPF/DKIM/DMARC configured for sending domain.

## Security and Compliance

1. CASL unsubscribe in email templates validated.
2. SMS includes STOP text validated.
3. Opt-out behavior tested for both channels.
4. Audit logs written for critical flows.

## Launch Day

1. Enable production connector credentials.
2. Trigger smoke sync for each platform.
3. Trigger one report generation smoke test.
4. Monitor logs and alert channel for first 2 hours.

## Post-Launch (24h)

1. Review error rate and retry patterns.
2. Confirm first anomaly checks and report records exist.
3. Confirm no compliance regressions in message flows.
