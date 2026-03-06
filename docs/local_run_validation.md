# Local Run and Validation Guide

Date: 2026-03-05

## 1. Environment Setup

1. Create venv:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install '.[dev]'
   ```
3. Copy env file:
   ```bash
   cp .env.example .env
   ```

## 2. Start Services

1. API:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
2. Worker:
   ```bash
   celery -A app.worker.celery_app.celery_app worker --loglevel=INFO
   ```
3. Scheduler:
   ```bash
   celery -A app.worker.celery_app.celery_app beat --loglevel=INFO
   ```

## 3. Database Migration

```bash
alembic upgrade head
```

## 4. API Smoke Checks

1. Basic health:
   ```bash
   curl -s http://localhost:8000/v1/health
   ```
2. Readiness:
   ```bash
   curl -s http://localhost:8000/v1/health/ready
   ```
3. Manual connector trigger:
   ```bash
   curl -s -X POST http://localhost:8000/v1/connectors/meta/sync-hourly
   ```
4. Weekly report generate:
   ```bash
   curl -s -X POST http://localhost:8000/v1/reports/weekly/generate \\\n+     -H 'Content-Type: application/json' \\\n+     -d '{\"actor\":\"local-test\"}'
   ```

## 5. Test and Static Validation

1. Syntax compile:
   ```bash
   PYTHONPYCACHEPREFIX=/tmp/okeanos_pycache python3 -m py_compile $(rg --files app tests alembic -g '*.py')
   ```
2. Test suite:
   ```bash
   pytest -q
   ```

## 6. Load Smoke

```bash
python scripts/smoke_load.py --base-url http://localhost:8000 --path /v1/health --requests 200 --concurrency 20
```

## 7. Validation Exit Criteria

1. Health and readiness endpoints return success.
2. Worker and scheduler run without startup errors.
3. Weekly report generation endpoint inserts report row.
4. Alert check task executes without unhandled exceptions.
5. Syntax and test checks pass in local environment.

