"""SQLAlchemy model registrations."""

from app.db.models.approval import Approval, AuditLog
from app.db.models.audience import AudienceSegment
from app.db.models.budget import BudgetAllocation, BudgetGuardrail
from app.db.models.campaign import AdCreative, Campaign
from app.db.models.lead import ChannelSubscription, Lead, LeadStageHistory, LeadTag
from app.db.models.messaging import MessageSent, Sequence, SequenceEnrollment, SequenceStep, Template
from app.db.models.reporting import AdMetricHourly, Alert, MetricSnapshot, SyncRun, WeeklyReport

__all__ = [
    "AdMetricHourly",
    "AdCreative",
    "Approval",
    "Alert",
    "AudienceSegment",
    "AuditLog",
    "BudgetAllocation",
    "BudgetGuardrail",
    "Campaign",
    "ChannelSubscription",
    "Lead",
    "LeadStageHistory",
    "LeadTag",
    "MessageSent",
    "MetricSnapshot",
    "Sequence",
    "SequenceEnrollment",
    "SequenceStep",
    "SyncRun",
    "Template",
    "WeeklyReport",
]
