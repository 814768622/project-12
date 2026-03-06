# Okeanos MVP Release Notes

Version: 0.1.0  
Date: 2026-03-05  
Status: MVP implementation baseline complete (code-level)

## 1. Summary

This release delivers the MVP backend baseline for Okeanos AI Platform across architecture, API surface, core domain modules, messaging compliance, reporting, and operations runbooks.

## 2. Delivered Scope

1. Platform foundation:
   - FastAPI service skeleton
   - Celery worker and scheduler
   - PostgreSQL and Redis integration points
   - Alembic migration framework
2. Data layer:
   - P0 schema SQL (`sql/001_p0_schema.sql`)
   - Alembic bootstrap migration applying P0 schema
3. API coverage:
   - All planned MVP endpoints implemented in route layer
4. Domain modules:
   - Leads and webhook ingestion
   - Campaigns, creatives, approvals
   - Budget guardrails and status
   - Audience sync trigger
   - Messaging sequence enrollment and send policy checks
   - Reports generation and retrieval
5. Compliance and governance:
   - CASL-related unsubscribe handling for email and SMS
   - Frequency and send-window policies for messaging
   - Audit log writes for critical flows
6. Reporting and alerts:
   - Weekly report generation service
   - Metric snapshot persistence
   - Baseline anomaly alert generation
7. Operations hardening:
   - Request ID middleware and unified error response schema
   - Readiness endpoint with DB check
   - Runbook, failure drill plan, go-live checklist
   - Standard-library smoke load script

## 3. Endpoint Completion

Implemented MVP endpoints include:
1. `POST /v1/webhooks/cf7/leads`
2. `POST /v1/webhooks/twilio/status`
3. `POST /v1/webhooks/gmail/inbound`
4. `GET /v1/leads`
5. `GET /v1/leads/{lead_id}`
6. `PATCH /v1/leads/{lead_id}`
7. `POST /v1/leads/{lead_id}/tags`
8. `POST /v1/campaigns`
9. `GET /v1/campaigns`
10. `POST /v1/campaigns/{campaign_id}/creatives`
11. `POST /v1/campaigns/{campaign_id}/approval-requests`
12. `POST /v1/approvals/{approval_id}/execute`
13. `POST /v1/budgets/guardrails`
14. `GET /v1/budgets/status`
15. `POST /v1/audiences/sync`
16. `POST /v1/sequences/{sequence_id}/enrollments`
17. `POST /v1/messages/send`
18. `POST /v1/connectors/{platform}/sync-hourly`
19. `POST /v1/reports/weekly/generate`
20. `GET /v1/reports/weekly/{report_id}`

## 4. Known Gaps

1. External integration actions are partially stubbed (manual trigger and queue-ready behavior) and require live credentials for full E2E validation.
2. Automated test execution is currently blocked in this environment due network restrictions preventing dependency download.
3. Some production concerns remain operational tasks:
   - Secret provisioning in Railway
   - Domain mail auth setup (SPF/DKIM/DMARC)
   - Live connector credential rotation and monitoring

## 5. Validation Performed

1. Python syntax compilation checks passed (`py_compile`).
2. Route and module wiring verified locally via static inspection.
3. Runtime tests (`pytest`) not executed due missing installable dependencies in offline environment.

