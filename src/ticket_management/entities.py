"""Ticket domain entities aligned to docs/domain-model.md conventions."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


TICKET_FIELDS: tuple[str, ...] = (
    "ticket_id",
    "tenant_id",
    "account_id",
    "contact_id",
    "owner_user_id",
    "subject",
    "description",
    "priority",
    "status",
    "created_at",
    "response_due_at",
    "resolution_due_at",
    "first_responded_at",
    "resolved_at",
    "closed_at",
)

TICKET_STATUS_SEQUENCE: tuple[str, ...] = ("open", "in_progress", "resolved", "closed")


@dataclass(frozen=True)
class Ticket:
    """Canonical Ticket entity for support lifecycle + SLA tracking."""

    ticket_id: str
    tenant_id: str
    account_id: str
    contact_id: str | None
    owner_user_id: str
    subject: str
    description: str
    priority: str
    status: str
    created_at: str
    response_due_at: str
    resolution_due_at: str
    first_responded_at: str | None = None
    resolved_at: str | None = None
    closed_at: str | None = None

    def patch(self, **changes: Any) -> "Ticket":
        return replace(self, **changes)


@dataclass(frozen=True)
class EscalationRule:
    """Deterministic escalation rule with time and condition triggers."""

    rule_id: str
    tenant_id: str
    level: int
    name: str
    route_to: str
    trigger: str
    threshold_minutes: int
    condition_field: str | None = None
    condition_op: str | None = None
    condition_value: str | None = None
    active: bool = True


@dataclass(frozen=True)
class EscalationAction:
    """Escalation outcome chosen by SLA escalation engine."""

    ticket_id: str
    tenant_id: str
    rule_id: str
    level: int
    route_to: str
    escalation_state: str
    reason: str
    escalated_at: str


@dataclass(frozen=True)
class EscalationAuditRecord:
    """Immutable audit record for escalation decisions and predictions."""

    audit_id: str
    ticket_id: str
    tenant_id: str
    event_type: str
    details: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""


class TicketNotFoundError(KeyError):
    """Raised when a ticket cannot be found for a given ticket_id."""


class TicketStateError(ValueError):
    """Raised when a ticket lifecycle or SLA operation is invalid."""
