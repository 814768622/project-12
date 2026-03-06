# Okeanos MVP Runbook

Date: 2026-03-03

## 1. Services

Railway services:
1. `api`
2. `worker`
3. `scheduler`
4. `postgres`
5. `redis`

## 2. Health Checks

API checks:
1. `GET /v1/health`
2. `GET /v1/health/ready`

Expected:
1. `health` returns `{"status":"ok"}`
2. `ready` returns `{"status":"ready"}`

## 3. Core Jobs

1. Hourly sync (`hourly-sync`)
2. Alert check (`alert-check`)
3. Weekly report (`weekly-report`)

Validation:
1. Inspect logs for `task.*.start` and `task.*.done`
2. Confirm DB writes in `sync_runs`, `alerts`, `weekly_reports`

## 4. Incident Playbooks

### 4.1 Ad Connector Failures

Symptoms:
1. Repeated sync failures
2. Missing hourly metrics

Actions:
1. Trigger manual sync: `POST /v1/connectors/{platform}/sync-hourly`
2. Verify credentials and token expiry
3. Keep platform in degraded read-only mode until stable

### 4.2 Messaging Failures

Symptoms:
1. Spike in send errors
2. Queue backlog growth

Actions:
1. Check webhook processing logs for Twilio/Gmail
2. Validate subscription states and frequency policy rejections
3. Pause bulk sends, keep transactional high-priority sends only

### 4.3 Weekly Report Failure

Symptoms:
1. Monday 08:00 ET report missing

Actions:
1. Trigger manual report: `POST /v1/reports/weekly/generate`
2. Validate `weekly_reports` table insert
3. Notify stakeholders and attach generated report ID

## 5. Rollback Strategy

1. Roll back API/worker image to previous Railway release.
2. Keep DB schema backward compatible for one release window.
3. If migration is faulty, restore DB backup snapshot and redeploy previous release.

## 6. Operational Alerts

Minimum alerts:
1. API error rate
2. Queue backlog
3. Sync task failure count
4. Report generation failure
5. DB connectivity errors

## 7. Access and Secrets

1. Store secrets only in Railway environment variables.
2. Rotate integration tokens on incident or quarterly schedule.
3. Maintain least-privilege access for all connectors.
