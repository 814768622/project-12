"""Initial schema bootstrap marker.

Revision ID: 20260303_0001
Revises:
Create Date: 2026-03-03
"""

from pathlib import Path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260303_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    root_dir = Path(__file__).resolve().parents[2]
    schema_file = root_dir / "sql" / "001_p0_schema.sql"
    sql = schema_file.read_text(encoding="utf-8")
    for statement in [x.strip() for x in sql.split(";") if x.strip()]:
        op.execute(sa.text(statement))


def downgrade() -> None:
    table_names = [
        "audit_logs",
        "sync_runs",
        "weekly_reports",
        "metric_snapshots",
        "alerts",
        "approvals",
        "channel_subscriptions",
        "messages_sent",
        "sequence_enrollments",
        "sequence_steps",
        "sequences",
        "templates",
        "retargeting_lists",
        "audience_segments",
        "budget_changes",
        "budget_allocations",
        "budget_guardrails",
        "ad_metrics_hourly",
        "creative_assets",
        "ad_creatives",
        "campaigns",
        "lead_tags",
        "lead_stage_history",
        "leads",
        "users",
    ]

    for table_name in table_names:
        op.execute(sa.text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
