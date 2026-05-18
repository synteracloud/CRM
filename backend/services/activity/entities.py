"""Entities for the Activity Control Engine."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ActorContext:
    actor_id: str
    actor_name: str
    actor_role: str
    actor_type: str = "user"
    team_id: str | None = None
    on_behalf_of: str | None = None


@dataclass(frozen=True)
class EntityRecord:
    tenant_id: str
    entity_type: str
    entity_id: str
    owner_id: str
    owner_team_id: str | None = None
    state: str = "active"
    last_activity_at: str | None = None

    def patch(self, **changes: Any) -> "EntityRecord":
        return replace(self, **changes)


@dataclass(frozen=True)
class FieldChange:
    field: str
    before: Any
    after: Any


@dataclass(frozen=True)
class ActivityEvent:
    event_id: str
    tenant_id: str
    event_ts: str
    actor_id: str
    actor_role: str
    entity_type: str
    entity_id: str
    owner_id: str
    action: str
    result: str
    trace_id: str
    request_id: str
    field_changes: tuple[FieldChange, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AuditEvent:
    audit_id: str
    event_id: str
    tenant_id: str
    event_ts: str
    actor_id: str
    entity_type: str
    entity_id: str
    action: str
    prev_hash: str
    hash_value: str
    chain_seq: int
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OwnershipTransfer:
    transfer_id: str
    tenant_id: str
    entity_type: str
    entity_id: str
    from_owner_id: str
    to_owner_id: str
    requested_by: str
    reason_code: str
    reason_note: str
    status: str
    created_at: str


@dataclass(frozen=True)
class AlertRecord:
    alert_id: str
    tenant_id: str
    alert_type: str
    severity: str
    actor_id: str | None
    entity_type: str | None
    entity_id: str | None
    rule_name: str
    details: dict[str, Any]
    created_at: str


class ActivityControlError(ValueError):
    """Base exception for control violations."""


class OwnershipError(ActivityControlError):
    """Raised when ownership rules are violated."""


class PolicyDeniedError(ActivityControlError):
    """Raised when writes are denied by ownership policy."""


class TraceabilityGapError(ActivityControlError):
    """Raised when an operation attempts an untraceable mutation."""


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
