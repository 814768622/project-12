# Okeanos AI Platform - Technical Design (MVP)

Version: 1.0  
Date: 2026-03-03  
Status: Ready for Implementation

## 1. Scope

This technical design is derived from:
1. `Okeanos_AI_Platform_PRD.md`
2. `docs/architecture.md`

MVP scope is fixed to all six PRD modules in a 6-week delivery:
1. Campaign Creation and Management
2. Budget Allocation and Optimization
3. Audience Targeting and Segmentation
4. SEO and Content Automation
5. Email and SMS Automation
6. Performance Reporting and Analytics

## 2. Design Principles

1. Deliver complete business coverage with minimal system complexity.
2. Keep strict modular boundaries inside a modular monolith.
3. Human-in-the-loop for high-risk actions in MVP.
4. Every material action must be auditable.
5. Prefer deterministic rules over opaque automation for MVP.

## 3. Runtime Architecture

## 3.1 Services

1. `api`:
   - FastAPI HTTP service for REST APIs and inbound webhooks.
   - Auth, validation, orchestration, command creation.
2. `worker`:
   - Celery workers for async tasks, connector sync, sends, rule checks, report generation.
3. `scheduler`:
   - Celery Beat for periodic jobs.
4. `postgres`:
   - Primary persistence store.
5. `redis`:
   - Broker, transient cache, distributed locks, idempotency keys.

## 3.2 Module Boundaries

1. `modules/campaign`:
   - Campaign CRUD, creative lifecycle, template application, A/B state transitions.
2. `modules/budget`:
   - Guardrail policy evaluation, pacing checks, reallocation proposals.
3. `modules/audience`:
   - Segment management, suppression rules, hashed audience exports.
4. `modules/seo`:
   - Keyword tracking ingestion, blog draft workflow, WordPress publishing.
5. `modules/messaging`:
   - Sequence engine, template rendering, send policy checks, channel dispatch.
6. `modules/reporting`:
   - KPI aggregation, anomaly detection, weekly report composition.
7. `modules/approval`:
   - Approval request creation, email command parsing, execution authorization.
8. `modules/connectors`:
   - External API adapters with normalized contract.
9. `modules/common`:
   - Settings, logging, errors, time utils, enums, idempotency helpers.

## 4. Data Design

## 4.1 P0 Entities (Must Implement Before Go-Live)

1. `users`
2. `leads`
3. `lead_stage_history`
4. `lead_tags`
5. `campaigns`
6. `ad_creatives`
7. `creative_assets`
8. `ad_metrics_hourly`
9. `budget_guardrails`
10. `budget_allocations`
11. `budget_changes`
12. `audience_segments`
13. `retargeting_lists`
14. `templates`
15. `sequences`
16. `sequence_steps`
17. `sequence_enrollments`
18. `messages_sent`
19. `channel_subscriptions`
20. `approvals`
21. `alerts`
22. `metric_snapshots`
23. `weekly_reports`
24. `sync_runs`
25. `audit_logs`

## 4.2 Data Constraints (Critical)

1. `campaigns.platform` in (`meta`, `google`, `tiktok`).
2. `campaigns.status` state-machine validated in service layer.
3. `templates.status` must be `approved` before sequence activation.
4. `messages_sent` unique key on (`channel`, `external_message_id`) for dedupe.
5. `channel_subscriptions` unique key on (`lead_id`, `channel`).
6. `approvals` include TTL and immutable payload hash.
7. `ad_metrics_hourly` unique key on (`platform`, `external_campaign_id`, `hour_bucket`).
8. `audit_logs` append-only.

## 4.3 Required Indexes

1. `leads(created_at)`, `leads(status)`, `leads(score)`.
2. `campaigns(platform, status)`.
3. `ad_metrics_hourly(hour_bucket, platform)`.
4. `budget_allocations(period_start, period_type)`.
5. `sequence_enrollments(status, next_run_at)`.
6. `messages_sent(sent_at, channel)`.
7. `alerts(triggered_at, alert_type)`.
8. `sync_runs(job_name, started_at)`.
9. `audit_logs(created_at, entity_type, entity_id)`.

## 5. API Design

## 5.1 Public API and Webhook Endpoints (MVP)

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

## 5.2 API Standards

1. Validation: Pydantic request/response models.
2. Error schema:
   - `code` (string)
   - `message` (string)
   - `details` (object or null)
   - `request_id` (string)
3. Idempotency:
   - Required for send endpoints and command endpoints.
   - Header: `Idempotency-Key`.
4. Pagination:
   - Cursor-based for list endpoints.
5. Time:
   - UTC persisted in DB, ET used for business windows in service layer.

## 6. Connector Design

## 6.1 Normalized Data Contract

Each ad connector returns a normalized payload:
1. `platform`
2. `external_campaign_id`
3. `external_ad_id` (optional)
4. `impressions`
5. `clicks`
6. `spend_cad`
7. `conversions`
8. `window_start_utc`
9. `window_end_utc`
10. `fetched_at_utc`

## 6.2 Failure Handling

1. Retry transient errors (network, 429, 5xx) with exponential backoff.
2. Mark permanent failures in `sync_runs` with root cause.
3. Circuit-breaker style cooldown after consecutive failures.
4. Support read-only degraded mode for unstable write operations.

## 7. Messaging and Sequence Engine

## 7.1 Sequence Execution Rules

1. Scheduler picks active enrollments with `next_run_at <= now`.
2. Before send, enforce:
   - channel subscription status
   - weekly email cap (`<= 3`)
   - SMS cooldown (`>= 48h`)
   - SMS local window (`09:00-20:00 ET`)
3. Render template with variables and fallback defaults.
4. Dispatch through channel adapter (Gmail or Twilio).
5. Persist result in `messages_sent`.
6. Advance step pointer and compute next schedule.

## 7.2 CASL Enforcement

1. Email always contains unsubscribe link.
2. SMS always contains STOP instruction.
3. Channel-specific unsubscribe updates `channel_subscriptions` within 24h.
4. Sequence processor must skip unsubscribed channel automatically.

## 8. Approval Design (Email Reply Model)

## 8.1 Lifecycle

1. System creates `approvals` row with:
   - `approval_id`
   - action payload
   - payload hash
   - requester
   - expires_at
2. Email sent to approver:
   - action summary
   - required token format: `APPROVE #<id>` or `REJECT #<id>`
3. Inbound parser validates:
   - sender allowlist
   - command syntax
   - approval status and TTL
4. If valid, mark status and enqueue execute task.
5. Executor checks hash and idempotency before platform call.

## 8.2 Security Controls

1. Shared secret or signature validation on inbound webhook.
2. Sender allowlist.
3. TTL expiration and single-use approval token.
4. Full audit trail across create, decision, execute, outcome.

## 9. Reporting and Alerting

## 9.1 Hourly KPIs

1. Spend by platform.
2. CPA by platform and segment.
3. Leads by source and score band.
4. Creative CTR and conversion rate.
5. Email/SMS engagement.

## 9.2 Alert Rules (MVP)

1. CPA warning: platform CPA > 1.5x seasonal target for > 2 days.
2. CPA critical: platform CPA > 2.0x seasonal target for > 2 days.
3. Spend cap: weekly spend > 90% of budget.
4. Lead drop: daily leads drop > 30% vs trailing 7-day average.
5. Email bounce spike: > 5% in send batch.
6. SEO rank drop: keyword position drops > 10.

## 9.3 Weekly Report Job

1. Schedule: Monday 08:00 ET.
2. Inputs:
   - previous full week metrics
   - month-to-date comparison
3. Output:
   - persisted report JSON in `weekly_reports`
   - email to configured recipients
4. SLA:
   - generation under 5 minutes
   - single retry path before failure alert

## 10. SEO and WordPress Workflow

1. Weekly keyword check ingestion into `keyword_rankings` (P1 if deferred).
2. Draft blog post generation from approved topic list.
3. Optional approval gate before publish.
4. Publish via WordPress REST with metadata:
   - target keyword
   - CTA link
   - author display name `Okeanos Team`
5. Store WordPress post ID and publish status.

## 11. Scheduling Plan (Celery Beat)

1. Hourly platform sync: `0 * * * *`
2. Hourly alert check: `15 * * * *`
3. Sequence tick: every 5 minutes
4. Daily rollup: `10 0 * * *`
5. Weekly report: `0 8 * * 1` (ET)
6. Weekly audience refresh: `0 4 * * 1`

## 12. Security and Compliance

1. Secrets only in Railway environment variables.
2. Principle of least privilege on all external API credentials.
3. PII at rest in PostgreSQL with strict access control.
4. Hashed PII for audience uploads (`SHA-256`).
5. Input schema validation for all webhooks.
6. IP/source verification where provider supports it.
7. Immutable audit logs for compliance review.

## 13. Observability

## 13.1 Logging

1. Structured JSON logs.
2. Correlation IDs:
   - `request_id`
   - `job_id`
   - `approval_id` (when applicable)
3. Redact sensitive fields (tokens, raw secrets, full phone numbers).

## 13.2 Metrics

1. API latency p95/p99.
2. Task success and failure rates.
3. Connector API error rates by platform.
4. Message delivery and bounce rates.
5. Weekly report job duration.

## 13.3 Alerts

1. Sync job failure bursts.
2. Queue backlog threshold exceeded.
3. SMTP/API send failures above threshold.
4. Database connectivity instability.

## 14. Testing Strategy

1. Unit tests:
   - rule engine
   - sequence scheduling
   - approval parser
   - payload normalization
2. Integration tests:
   - webhook ingest to DB
   - connector sync to metric tables
   - send workflow with mock adapters
3. Contract tests:
   - connector response schema
   - API request and response models
4. E2E tests:
   - lead ingest -> sequence send
   - metric sync -> alert trigger -> approval -> execution
   - weekly report generation and delivery

## 15. Release Plan (6 Weeks)

1. Week 1:
   - project skeleton, migration framework, P0 schema, base observability.
2. Week 2:
   - Meta/Google/TikTok read connectors, hourly ingest pipeline.
3. Week 3:
   - campaign, budget, audience domain services, approval service.
4. Week 4:
   - CF7 lead ingest, messaging engine, Gmail/Twilio adapters, CASL controls.
5. Week 5:
   - SEO workflows, KPI aggregation, weekly report and alerting.
6. Week 6:
   - hardening, load tests, runbooks, go-live checklist and release.

## 16. Risks and Mitigations

1. Gmail deliverability and quota:
   - SPF/DKIM/DMARC, ramp-up, throttling.
2. Parallel integration risk with three ad platforms:
   - connector abstraction, feature flags, staged rollout toggles.
3. No UI in MVP:
   - strict email-command protocol and operator runbook.
4. No CRM baseline:
   - treat internal `leads` as temporary source-of-truth with migration-ready IDs.

## 17. Out of Scope (MVP)

1. Multi-touch attribution.
2. Advanced forecasting models and automated budget optimizer.
3. Full admin dashboard UI.
4. WhatsApp/Instagram DM channels.
5. Full autonomous campaign write-back without approvals.

## 18. Implementation Checklist

1. P0 schema migrations complete.
2. All 20 MVP endpoints implemented and validated.
3. All scheduled jobs configured and verified in Railway.
4. CASL policy checks covered by tests.
5. Approval flow tested with real email replies.
6. Weekly report delivery tested in production-like environment.
7. Runbook prepared for on-call and manual fallback procedures.

