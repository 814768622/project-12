# Okeanos AI Platform - Agent Operating Guide

Version: 1.0  
Date: 2026-03-03

## 1. Purpose

This file defines how an engineering agent should implement the Okeanos AI Platform MVP.
It consolidates requirements from:
1. `Okeanos_AI_Platform_PRD.md`
2. `docs/architecture.md`
3. `docs/tech_design.md`
4. `docs/execution_plan.md`

## 2. Source-of-Truth Order

If conflicts occur, use this precedence:
1. `Okeanos_AI_Platform_PRD.md` (business intent and rules)
2. `docs/tech_design.md` (implementation detail)
3. `docs/architecture.md` (system baseline)
4. `docs/execution_plan.md` (delivery sequencing)

## 3. Fixed MVP Constraints

1. Delivery window: 6 weeks, from 2026-03-03 to 2026-04-12.
2. All six modules are in MVP scope:
   - Campaign
   - Budget
   - Audience
   - SEO
   - Email and SMS
   - Reporting
3. Stack:
   - FastAPI
   - PostgreSQL
   - Redis
   - Celery (worker + scheduler)
4. Deployment: Railway.
5. Integrations:
   - Meta Ads
   - Google Ads
   - TikTok Ads
   - WordPress REST (with Contact Form 7 webhook ingest)
   - Gmail API
   - Twilio
6. Delivery mode: manual + semi-automated, with human approval for high-risk actions.
7. No admin UI in MVP.

## 4. System Responsibilities

1. Ingest and process leads from Contact Form 7.
2. Pull ad metrics hourly from all three ad platforms.
3. Execute policy checks for budget, messaging, and compliance.
4. Orchestrate campaign and budget actions with email-based approvals.
5. Run email and SMS sequences with hard send constraints.
6. Generate weekly report every Monday at 08:00 ET.

## 5. Non-Negotiable Business Rules

1. CASL:
   - Every email must include unsubscribe.
   - Every SMS must include STOP instruction.
   - Opt-outs honored within 24 hours.
2. Messaging frequency:
   - Max 3 emails per lead per week.
   - Max 1 SMS per lead per 48 hours.
   - SMS send window: 09:00-20:00 ET only.
3. Budget governance:
   - No spend beyond approved weekly cap without explicit approval.
   - Platform budget concentration above 60% requires manual override.
4. Campaign governance:
   - No campaign launch without at least one approved creative.
   - A/B winner cannot be declared before 72 hours.
5. Reporting:
   - Weekly report must run Monday 08:00 ET.
   - Retain report history for 24 months.

## 6. Required MVP Data and API Baseline

1. P0 tables from `docs/tech_design.md` and `docs/architecture.md` must be implemented before go-live.
2. All 20 MVP endpoints in `docs/tech_design.md` section 5.1 must exist and be tested.
3. Any new endpoint or schema change must update:
   - `docs/tech_design.md`
   - `docs/execution_plan.md` (if schedule impact exists)

## 7. Operational Targets (SLO-like)

1. API p95 latency < 400ms (internal operations).
2. Hourly ingestion p95 duration < 10 minutes.
3. Alert generation latency < 15 minutes from breach.
4. Weekly report generation < 5 minutes.

## 8. Security and Audit Requirements

1. Validate all webhook requests using secret/signature checks.
2. Store secrets only in Railway environment variables.
3. Hash PII (SHA-256) for audience uploads.
4. Apply idempotency for message sends and approval execution.
5. Write immutable audit logs for:
   - campaign changes
   - budget changes
   - messaging sends
   - approval decisions and executions

## 9. Engineering Workflow

For each implementation task:
1. Confirm requirement mapping to PRD section.
2. Implement minimal compliant behavior first.
3. Add tests:
   - unit for rules
   - integration for connectors/webhooks
   - E2E for key business flows
4. Validate observability:
   - structured logs
   - sync/job status
   - error classification
5. Update docs if behavior or contract changed.

## 10. Weekly Execution Priority

1. Week 1 (2026-03-03 to 2026-03-08): foundation, P0 schema, infra.
2. Week 2 (2026-03-09 to 2026-03-15): connector ingestion for Meta/Google/TikTok.
3. Week 3 (2026-03-16 to 2026-03-22): campaign/budget/audience + approval flow.
4. Week 4 (2026-03-23 to 2026-03-29): messaging engine + CASL enforcement.
5. Week 5 (2026-03-30 to 2026-04-05): SEO workflow + reporting + alerts.
6. Week 6 (2026-04-06 to 2026-04-12): hardening, drills, go-live readiness.

## 11. Definition of Done

A feature is done only if all are true:
1. PRD requirement is covered.
2. API/schema contract is documented.
3. Tests pass for normal and failure paths.
4. Audit logs are emitted for critical actions.
5. Alerting/monitoring signals are present.
6. No regression against compliance rules.

## 12. Escalation Rules for the Agent

Escalate immediately if any occurs:
1. Requirement conflict between PRD and existing implementation.
2. Integration credentials missing or invalid.
3. Reliability target repeatedly missed.
4. Compliance rule cannot be enforced with current design.
5. Timeline risk threatens delivery of P0 scope.

