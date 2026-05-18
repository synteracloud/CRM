"""Entities for employee activity monitoring (discipline + performance)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def parse_rfc3339(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class MonitorEvent:
    event_id: str
    tenant_id: str
    user_id: str
    activity_type: str
    occurred_at: str
    trace_id: str
    request_id: str
    response_seconds: int | None = None
    follow_up_due_at: str | None = None
    follow_up_completed_at: str | None = None
    bypass_attempted: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UserMetrics:
    tenant_id: str
    user_id: str
    follow_up_compliance: float
    average_response_seconds: float
    timeline_events: int
    bypass_count: int


@dataclass(frozen=True)
class PerformanceScore:
    tenant_id: str
    user_id: str
    score: float
    discipline_component: float
    performance_component: float
    weights: dict[str, float]
    grade: str


@dataclass(frozen=True)
class BypassFinding:
    tenant_id: str
    user_id: str
    event_id: str
    reason: str


class MonitorValidationError(ValueError):
    """Raised when activity tracking input is invalid or incomplete."""
