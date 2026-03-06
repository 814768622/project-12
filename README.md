# Okeanos AI Platform Backend

MVP backend service for campaign automation, budget controls, audience sync, SEO workflows,
messaging, and reporting.

## Quick Start

1. Create and activate a Python 3.11+ virtualenv.
2. Install dependencies:
   ```bash
   pip install -e '.[dev]'
   ```
3. Copy environment template:
   ```bash
   cp .env.example .env
   ```
4. Run API server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
5. Run Celery worker:
   ```bash
   celery -A app.worker.celery_app.celery_app worker --loglevel=INFO
   ```
6. Run Celery beat:
   ```bash
   celery -A app.worker.celery_app.celery_app beat --loglevel=INFO
   ```

## Migrations

```bash
alembic upgrade head
```

## Docs

1. Architecture: `docs/architecture.md`
2. Technical Design: `docs/tech_design.md`
3. Execution Plan: `docs/execution_plan.md`
4. Runbook: `docs/runbook.md`
5. Failure Drills: `docs/failure_drills.md`
6. Go-Live Checklist: `docs/go_live_checklist.md`
7. Local Run Validation: `docs/local_run_validation.md`
8. Release Notes: `docs/release_notes.md`

## Quick Validation

```bash
# syntax check without external dependencies
PYTHONPYCACHEPREFIX=/tmp/okeanos_pycache python3 -m py_compile $(rg --files app tests alembic -g '*.py')
```

## Smoke Load

```bash
python scripts/smoke_load.py --base-url http://localhost:8000 --path /v1/health --requests 200 --concurrency 20
```
