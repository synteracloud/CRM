"""Follow-up enforcement domain entities."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import Enum


class FollowupState(str, Enum):
    PENDING = "pending"
    OVERDUE = "overdue"
    COMPLETED = "completed"


class EscalationLevel(str, Enum):
    NONE = "none"
    REMINDER = "reminder"
    WARNING = "warning"
    ESCALATED = "escalated"
    REASSIGNED = "reassigned"


@dataclass(frozen=True)
class LeadSnapshot:
    lead_id: str
    tenant_id: str
    owner_id: str
    status: str
    priority: str
    stage: str
    last_activity_at: datetime
    closure_reason: str | None = None

    def patch(self, **changes: object) -> "LeadSnapshot":
        return replace(self, **changes)


@dataclass(frozen=True)
class FollowupTask:
    task_id: str
    lead_id: str
    tenant_id: str
    owner_id: str
    state: FollowupState
    due_at: datetime
    created_at: datetime
    rule_type: str
    escalation_level: EscalationLevel = EscalationLevel.NONE
    generated_by: str = "Scheduler"
    completed_at: datetime | None = None
    completed_activity_id: str | None = None
    is_canonical: bool = True

    def patch(self, **changes: object) -> "FollowupTask":
        return replace(self, **changes)

    @property
    def is_required(self) -> bool:
        return self.generated_by in {"Scheduler", "EscalationEngine", "SystemRepair"}


@dataclass(frozen=True)
class FollowupPolicy:
    hot_sla_hours: int = 4
    warm_sla_hours: int = 24
    cold_sla_hours: int = 72
    inactivity_hours: int = 48
    warning_after_hours: int = 2
    escalation_after_hours: int = 24
    reassignment_after_hours: int = 48
    overdue_cap_per_owner: int = 8

    def sla_delta(self, priority: str) -> timedelta:
        p = priority.lower()
        if p == "hot":
            return timedelta(hours=self.hot_sla_hours)
        if p == "warm":
            return timedelta(hours=self.warm_sla_hours)
        return timedelta(hours=self.cold_sla_hours)


@dataclass(frozen=True)
class EscalationEvent:
    lead_id: str
    task_id: str
    level: EscalationLevel
    owner_id: str
    generated_at: datetime
    reason: str


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
