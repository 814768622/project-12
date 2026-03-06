# Okeanos AI Marketing Platform - Architecture Baseline

Version: 1.0  
Date: 2026-03-03  
Status: Accepted (MVP baseline)

## 1. Purpose

This document defines the implementation architecture for the Okeanos AI Marketing Platform MVP.
It converts PRD requirements into a buildable technical baseline for a 6-week delivery.

## 2. Confirmed Constraints

1. Timeline: 6 weeks.
2. MVP scope: all six PRD modules in MVP.
3. Team: 3 engineers, Python-first.
4. Existing systems: WordPress website with Contact Form 7.
5. CRM: none at MVP start.
6. Data freshness target: hourly.
7. Delivery mode: manual + semi-automated (human-in-the-loop).
8. Deployment platform: Railway.
9. Channels to integrate in MVP: Meta Ads, Google Ads, TikTok Ads.
10. Email channel: Gmail (direct customer email).
11. SMS channel: Twilio.
12. No web admin UI in MVP.

## 3. Architecture Goals

1. Deliver complete MVP capabilities within 6 weeks with low operational complexity.
2. Keep architecture simple and modular for future split into services.
3. Guarantee auditability for budget, campaign, and messaging actions.
4. Support policy enforcement (CASL, send windows, frequency caps, approval thresholds).
5. Enable deterministic hourly sync and weekly reporting.

## 4. High-Level Architecture

```text
                        +----------------------+
                        |   External Channels  |
                        |----------------------|
                        | Meta / Google / TikTok
                        | WordPress REST
                        | Gmail API
                        | Twilio
                        +----------+-----------+
                                   |
                                   v
 +-------------------+    +--------+---------+    +-------------------+
 | Contact Form 7    |--->| FastAPI API      |--->| PostgreSQL        |
 | (Webhook Source)  |    | (Domain Modules) |    | System of Record  |
 +-------------------+    +--------+---------+    +---------+---------+
                                   |                         ^
                                   v                         |
                           +-------+--------+                |
                           | Celery Worker  |----------------+
                           | Async Jobs     |
                           +-------+--------+
                                   |
                                   v
                           +-------+--------+
                           | Celery Beat    |
                           | Schedules      |
                           +-------+--------+
                                   |
                                   v
                           +-------+--------+
                           | Redis          |
                           | Queue + Cache  |
                           +----------------+
```

## 5. System Style and Boundaries

### 5.1 Chosen Style

Modular monolith:
1. Single deployable backend service (`FastAPI`) for low coordination overhead.
2. Background processing separated via Celery worker and scheduler.
3. Clear module boundaries to avoid "big ball of mud."

### 5.2 Domain Modules

1. `campaign_service`: campaigns, creatives, seasonal templates, A/B state.
2. `budget_service`: guardrails, reallocation suggestions, threshold checks.
3. `audience_service`: segment definitions, hash pipelines, refresh jobs.
4. `seo_service`: keyword tracking, blog drafts, WordPress publishing workflow.
5. `messaging_service`: templates, sequences, enrollments, send policy engine.
6. `reporting_service`: KPI snapshots, anomaly detection, weekly reports.
7. `approval_service`: email-based approval requests and execution authorization.
8. `connector_service`: platform adapters with normalized contracts.

## 6. Data Architecture

### 6.1 Primary Stores

1. PostgreSQL as system of record for business entities, logs, snapshots, and approvals.
2. Redis for queueing, dedupe keys, short-lived locks, and rate-control state.

### 6.2 Data Tiers

1. Operational tier: leads, campaigns, budgets, audiences, templates, sequences.
2. Metrics tier: hourly ad metrics, channel engagement metrics, KPI snapshots.
3. Governance tier: approvals, audit logs, sync run logs, alerts.

### 6.3 Priority Tables

P0 tables (must exist before production):
`users`, `leads`, `lead_stage_history`, `lead_tags`, `campaigns`, `ad_creatives`, `creative_assets`, `ad_metrics_hourly`, `budget_guardrails`, `budget_allocations`, `budget_changes`, `audience_segments`, `retargeting_lists`, `templates`, `sequences`, `sequence_steps`, `sequence_enrollments`, `messages_sent`, `channel_subscriptions`, `approvals`, `alerts`, `metric_snapshots`, `weekly_reports`, `sync_runs`, `audit_logs`.

P1 tables (post-MVP hardening):
`seo_audits`, `keyword_rankings`, `blog_posts`, `competitor_reports`, `attributions`, `forecasts`, `ab_test_results`, `recommendations`.

## 7. Integration Architecture

### 7.1 Connector Contract

Each external platform adapter must implement:
1. `pull_metrics(window_start, window_end)`.
2. `pull_campaign_state()`.
3. `push_campaign_action(action_payload)` (guarded by approval where required).
4. `healthcheck()`.

### 7.2 External Integrations

1. Contact Form 7 webhook -> lead ingestion endpoint.
2. Meta/Google/TikTok APIs -> hourly metrics ingest.
3. WordPress REST -> blog draft create/publish.
4. Gmail API -> customer sends + approval email parsing.
5. Twilio -> outbound SMS + inbound delivery/reply/STOP webhooks.

## 8. Core Business Flows

### 8.1 Lead Ingestion and Nurture

1. CF7 submits lead data to webhook endpoint.
2. API validates and stores lead.
3. Scoring/tagging rules execute.
4. Sequence enrollment decides email and SMS schedule.
5. Worker sends via Gmail/Twilio with policy checks.
6. Delivery and engagement events update `messages_sent` and subscriptions.

### 8.2 Hourly Performance and Budget Guardrails

1. Beat triggers hourly sync jobs.
2. Worker pulls platform metrics and writes `ad_metrics_hourly`.
3. Budget rules compute CPA and pacing.
4. If thresholds breach, create `alerts` and optionally `approvals`.
5. Approved actions execute and write `budget_changes` + `audit_logs`.

### 8.3 Approval Workflow (Email Reply)

1. System creates `approval` with action payload and TTL.
2. System emails approver with tokenized reference (`APPROVE #id`).
3. Inbound email parser validates sender and command.
4. Approval state updates to approved or rejected.
5. Worker executes approved action idempotently.
6. All steps logged in `audit_logs`.

### 8.4 Weekly Reporting

1. Scheduler runs Monday 08:00 ET.
2. Reporting module aggregates week-over-week and month-over-month metrics.
3. AI summary composes recommendations text.
4. Report persisted to `weekly_reports`.
5. Email sent to recipient list with retry policy.

## 9. API Surface (MVP First Batch)

Required endpoints (20):
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

## 10. Deployment Topology (Railway)

Services:
1. `api` (FastAPI app).
2. `worker` (Celery worker).
3. `scheduler` (Celery beat).
4. `postgres` (Railway managed PostgreSQL).
5. `redis` (Railway managed Redis).

Deployment principles:
1. Stateless app containers.
2. Rolling deploy for `api`.
3. Worker concurrency tuned after load tests.
4. Strict health checks and startup probes.

## 11. Environment Variables (Baseline)

Core:
`APP_ENV`, `APP_SECRET`, `LOG_LEVEL`, `TZ`, `PORT`.

Data:
`DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`.

WordPress and CF7:
`WORDPRESS_BASE_URL`, `WORDPRESS_USER`, `WORDPRESS_APP_PASSWORD`, `CF7_WEBHOOK_SECRET`.

Meta:
`META_APP_ID`, `META_APP_SECRET`, `META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID`.

Google:
`GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`, `GOOGLE_ADS_CUSTOMER_ID`, `GOOGLE_ADS_LOGIN_CUSTOMER_ID`.

TikTok:
`TIKTOK_APP_ID`, `TIKTOK_APP_SECRET`, `TIKTOK_ACCESS_TOKEN`, `TIKTOK_ADVERTISER_ID`.

Gmail:
`GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`, `GMAIL_SENDER`, `GMAIL_APPROVAL_LABEL`.

Twilio:
`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, `TWILIO_WEBHOOK_SECRET`.

Policy:
`EMAIL_MAX_PER_WEEK`, `SMS_COOLDOWN_HOURS`, `SMS_SEND_WINDOW_START`, `SMS_SEND_WINDOW_END`, `CPA_ALERT_MULTIPLIER`, `CPA_CRITICAL_MULTIPLIER`.

Schedules:
`HOURLY_SYNC_CRON`, `ALERT_CHECK_CRON`, `WEEKLY_REPORT_CRON`.

Observability:
`SENTRY_DSN` (optional).

## 12. Security and Compliance

1. CASL enforcement:
   - Email unsubscribe always included.
   - SMS includes STOP instruction and opt-out honored within 24h.
2. Audience upload privacy:
   - SHA-256 hash for email and phone before ad platform upload.
3. Least privilege:
   - Separate credentials per platform.
   - Environment-scoped secrets in Railway.
4. Boundary validation:
   - Request schema validation at all webhooks and APIs.
   - Signature or shared-secret checks for inbound webhooks.
5. Auditability:
   - Immutable audit log entry for all budget/campaign/send actions.

## 13. Reliability and Observability

1. Idempotency keys for outbound actions and webhook processing.
2. Retry with exponential backoff for transient API failures.
3. Dead-letter queue pattern for persistent task failures.
4. `sync_runs` table for job duration, status, and failure reasons.
5. Alerting for:
   - Sync failures,
   - Delivery spikes,
   - Error-rate anomalies.

## 14. Performance and Scale Targets

MVP targets:
1. API p95 latency under 400 ms for internal operations.
2. Hourly ingestion cycle completes in under 10 minutes for 95th percentile runs.
3. Alert generation latency under 15 minutes from threshold breach.
4. Weekly report generation under 5 minutes.

Scale path:
1. Increase worker replicas first.
2. Add read-optimized snapshot tables as data volume grows.
3. Consider service split only after clear scaling bottlenecks.

## 15. Risks and Mitigations

1. Gmail sender reputation and quota limits.
   - Mitigation: SPF/DKIM/DMARC, warm-up plan, send throttling.
2. Multi-platform API instability (Meta/Google/TikTok in parallel).
   - Mitigation: connector abstraction, feature flags, fallback to read-only mode.
3. No admin UI in MVP may slow operations.
   - Mitigation: structured approval emails, deterministic command format, runbook.
4. No CRM baseline.
   - Mitigation: treat `leads` domain as interim source of truth with clean migration keys.

## 16. Six-Week Delivery Plan

1. Week 1: foundation (FastAPI, DB schema, Celery, Redis, audit framework).
2. Week 2: ad connectors (Meta/Google/TikTok metric ingest).
3. Week 3: campaign, budget, audience domain logic + approvals.
4. Week 4: CF7 ingest, Gmail sequences, Twilio SMS, CASL controls.
5. Week 5: SEO workflows, weekly reports, anomaly alerts.
6. Week 6: end-to-end hardening, load tests, operations runbook, production rollout.

## 17. ADR Backlog

Planned architecture decisions to capture:
1. ADR-001: Modular monolith + Celery for MVP.
2. ADR-002: PostgreSQL + snapshot strategy.
3. ADR-003: Email-based approval command protocol.
4. ADR-004: Twilio as SMS channel.
5. ADR-005: Gmail direct sending in MVP and migration triggers to ESP.

