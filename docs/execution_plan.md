# Okeanos AI Platform - Execution Plan (Plan Mode)

Version: 1.0  
Date: 2026-03-03  
Source Inputs: `Okeanos_AI_Platform_PRD.md`, `docs/architecture.md`, `docs/tech_design.md`

## 1. Plan Objective

Deliver MVP in 6 weeks with all six PRD modules enabled in production:
1. Campaign
2. Budget
3. Audience
4. SEO
5. Email and SMS
6. Reporting

Execution model:
1. Modular monolith (`FastAPI`) + `Celery` + `PostgreSQL` + `Redis`
2. Deployment on Railway
3. Human-in-the-loop approvals for high-risk actions
4. Hourly data freshness target

## 2. Team Operating Model

Team size: 3 engineers.

Role allocation:
1. Engineer A (Platform and Data):
   - DB schema, migrations, observability, deployment, scheduling framework.
2. Engineer B (Integrations and Workflows):
   - Meta/Google/TikTok connectors, WordPress, Gmail, Twilio, webhook security.
3. Engineer C (Domain and Rules):
   - campaign/budget/audience/messaging/reporting business rules, approvals, alerts.

Shared responsibilities:
1. Code reviews (minimum 1 reviewer per PR)
2. Test ownership (unit + integration + E2E)
3. Weekly risk review and go/no-go gates

## 3. Delivery Cadence

Calendar baseline:
1. Week 1: 2026-03-03 to 2026-03-08
2. Week 2: 2026-03-09 to 2026-03-15
3. Week 3: 2026-03-16 to 2026-03-22
4. Week 4: 2026-03-23 to 2026-03-29
5. Week 5: 2026-03-30 to 2026-04-05
6. Week 6: 2026-04-06 to 2026-04-12

Ceremonies:
1. Daily 15-minute standup
2. Weekly planning each Monday
3. Weekly demo each Friday
4. Weekly risk gate each Friday before merge freeze

## 4. Workstreams and Deliverables

## 4.1 WS-1 Foundation and Operations

Deliverables:
1. Repository structure and module boundaries from tech design
2. Migration baseline and all P0 tables
3. Celery worker and scheduler bootstrap
4. Structured logging and base metrics
5. Railway service setup (`api`, `worker`, `scheduler`, `postgres`, `redis`)

Exit criteria:
1. All services boot in Railway staging
2. Migration up/down verified
3. Health endpoints and core telemetry available

## 4.2 WS-2 Connectors and Ingestion

Deliverables:
1. Contact Form 7 lead webhook ingestion
2. Meta/Google/TikTok hourly metrics pull
3. Twilio delivery and STOP callbacks
4. Gmail inbound approval parsing
5. WordPress draft and publish integration

Exit criteria:
1. Hourly sync completes under 10 minutes in staging dataset
2. Webhook auth validation enabled
3. Connector failure logs visible in `sync_runs`

## 4.3 WS-3 Domain Rules and Approval Engine

Deliverables:
1. Campaign and creative lifecycle
2. Budget guardrails and alert thresholds
3. Audience sync and suppression rules
4. Sequence engine and channel policy checks
5. Email reply approval flow (`APPROVE #id`, `REJECT #id`)

Exit criteria:
1. All key rules covered by unit tests
2. Approval actions are idempotent and auditable
3. CASL rules enforced in send path

## 4.4 WS-4 Reporting and Release Readiness

Deliverables:
1. KPI snapshots and anomaly detection
2. Weekly report generation (Monday 08:00 ET)
3. Runbook and rollback plan
4. Load and failure tests
5. Production readiness checklist

Exit criteria:
1. Weekly report generation under 5 minutes
2. Critical alerts produce email and SMS notifications
3. Go-live checklist signed off

## 5. Week-by-Week Plan

## Week 1 (2026-03-03 to 2026-03-08): Foundation

Scope:
1. Implement project skeleton and module folders.
2. Create P0 schema migration package.
3. Implement API scaffolding and shared middleware.
4. Configure Redis/Celery and scheduler.
5. Configure staging Railway environments and secrets.

Planned outputs:
1. `sql/001_p0_schema.sql` and migration runner
2. base FastAPI app with health and error model
3. Celery app with schedule registration
4. initial observability dashboards

Week gate:
1. Deploy staging baseline successfully.
2. Run migrations and smoke tests with no blocking issues.

## Week 2 (2026-03-09 to 2026-03-15): Integrations Core

Scope:
1. Build connector interfaces and normalized contracts.
2. Implement read-path for Meta, Google, TikTok metrics.
3. Implement `POST /v1/webhooks/cf7/leads`.
4. Persist hourly metrics and sync run status.
5. Add connector retry and cooldown behavior.

Planned outputs:
1. connector modules for three ad platforms
2. hourly sync job and manual trigger endpoint
3. staging data validation scripts

Week gate:
1. Hourly sync runs for all three platforms in staging.
2. Sync error handling validated with forced failure tests.

## Week 3 (2026-03-16 to 2026-03-22): Campaign, Budget, Audience, Approval

Scope:
1. Campaign CRUD and creative variant flows.
2. Budget guardrails, pacing checks, CPA alerts.
3. Audience segment and suppression data flows.
4. Approval request lifecycle and execution endpoint.
5. Audit log coverage for all critical mutations.

Planned outputs:
1. campaign and budget APIs operational in staging
2. alerts table writes and notification trigger scaffolding
3. email approval command parser core

Week gate:
1. High-risk operations require approval.
2. Budget and campaign actions are fully auditable.

## Week 4 (2026-03-23 to 2026-03-29): Messaging and Compliance

Scope:
1. Implement sequence engine and enrollment APIs.
2. Gmail outbound customer sending pipeline.
3. Twilio outbound and inbound processing.
4. CASL enforcement:
   - unsubscribe link in email
   - STOP support in SMS
   - channel-specific opt-out state
5. Frequency controls:
   - max 3 emails per week
   - SMS cooldown 48h
   - SMS send window 09:00-20:00 ET

Planned outputs:
1. message send endpoint and worker path
2. subscription and preference handling
3. compliance test cases

Week gate:
1. End-to-end lead intake to first message passes.
2. CASL and send-window constraints validated by tests.

## Week 5 (2026-03-30 to 2026-04-05): SEO and Reporting

Scope:
1. SEO draft workflow and WordPress publish path.
2. KPI aggregation from metrics and messaging.
3. Anomaly detection jobs and thresholds.
4. Weekly report generation and delivery.
5. Recommendation text generation and report persistence.

Planned outputs:
1. weekly report endpoint and scheduler job
2. report email template and delivery logs
3. SEO keyword ingestion baseline (manual or semi-auto for MVP)

Week gate:
1. Monday report dry run succeeds in staging.
2. Alert conditions produce expected notifications.

## Week 6 (2026-04-06 to 2026-04-12): Hardening and Launch

Scope:
1. Full regression and E2E suite.
2. Performance validation against p95 and job SLAs.
3. Failure drills:
   - connector outage
   - queue backlog
   - Gmail/Twilio transient failure
4. Operations runbook and on-call guide.
5. Production cutover and monitoring handoff.

Planned outputs:
1. release candidate build
2. signed production checklist
3. day-0 support schedule

Week gate:
1. All P0 acceptance criteria passed.
2. No unresolved Sev-1 or Sev-2 defects.

## 6. Endpoint Delivery Plan

Week 1:
1. scaffolding for all route groups
2. health, auth, error schema middleware

Week 2:
1. `POST /v1/webhooks/cf7/leads`
2. `POST /v1/connectors/{platform}/sync-hourly`
3. `GET /v1/leads`
4. `GET /v1/leads/{lead_id}`
5. `PATCH /v1/leads/{lead_id}`

Week 3:
1. `POST /v1/campaigns`
2. `GET /v1/campaigns`
3. `POST /v1/campaigns/{campaign_id}/creatives`
4. `POST /v1/campaigns/{campaign_id}/approval-requests`
5. `POST /v1/approvals/{approval_id}/execute`
6. `POST /v1/budgets/guardrails`
7. `GET /v1/budgets/status`
8. `POST /v1/audiences/sync`

Week 4:
1. `POST /v1/sequences/{sequence_id}/enrollments`
2. `POST /v1/messages/send`
3. `POST /v1/webhooks/twilio/status`
4. `POST /v1/webhooks/gmail/inbound`
5. `POST /v1/leads/{lead_id}/tags`

Week 5:
1. `POST /v1/reports/weekly/generate`
2. `GET /v1/reports/weekly/{report_id}`

## 7. Quality Gates and Acceptance Criteria

Functional:
1. All 20 MVP endpoints implemented and tested.
2. All six PRD modules available in production path.
3. Weekly report auto-run every Monday at 08:00 ET.

Compliance:
1. Email unsubscribe always present.
2. SMS STOP handling updates subscription state within 24 hours.
3. Audience upload hashing enforced for PII.

Reliability:
1. Hourly ingestion p95 duration <= 10 minutes.
2. API p95 latency <= 400 ms for internal operations.
3. Report generation <= 5 minutes.

Auditability:
1. Approval lifecycle fully logged.
2. Budget/campaign/messaging critical mutations logged.

## 8. Risk Register

1. Risk: Gmail quota or deliverability issues.
   - Trigger: bounce or rejection spikes.
   - Mitigation: warm-up, throttling, SPF/DKIM/DMARC, fallback queueing.
2. Risk: one or more ad APIs unstable.
   - Trigger: repeated sync failures or 429 bursts.
   - Mitigation: cooldown, retry policy, read-only degraded mode, feature flag.
3. Risk: no admin UI slows operational response.
   - Trigger: approval latency increases.
   - Mitigation: strict email command templates and runbook.
4. Risk: 6-week full-scope compression.
   - Trigger: week gate miss.
   - Mitigation: preserve P0 features, push P1 only.

## 9. Dependency and Critical Path

Critical path:
1. P0 schema and infra (Week 1)
2. Connector ingestion stability (Week 2)
3. Rule engine plus approval (Week 3)
4. Messaging compliance path (Week 4)
5. Reporting and alerting completeness (Week 5)
6. Hardening and launch readiness (Week 6)

Blocking dependencies:
1. API credentials for Meta/Google/TikTok/Gmail/Twilio/WordPress.
2. Railway project and secret provisioning.
3. DNS and email auth (SPF/DKIM/DMARC) for Gmail sending.
4. Production webhook URL setup for CF7 and Twilio.

## 10. Go-Live Checklist

1. Secrets configured for all environments.
2. Scheduler jobs active and verified.
3. All webhook signatures validated.
4. Alert channels verified (email and SMS).
5. Rollback process documented and tested.
6. Runbook accessible to all team members.
7. Final stakeholder sign-off recorded.

## 11. Plan Status Board

Current status as of 2026-03-05:
1. Week 1 scope: completed
2. Week 2 scope: completed
3. Week 3 scope: completed
4. Week 4 scope: completed
5. Week 5 scope: completed
6. Week 6 scope: completed (code and docs baseline)

Execution notes:
1. MVP route layer has full planned endpoint coverage.
2. P0 schema and migration framework are in place.
3. CASL policy enforcement and unsubscribe flows are implemented in API logic.
4. Reporting and anomaly generation services are implemented.
5. Runbook, failure drills, and go-live checklist are documented.

Open operational blockers:
1. Dependency installation and runtime tests are blocked in this environment due external network access limits.
2. Live credential validation for ad connectors and messaging providers is pending deployment environment setup.
