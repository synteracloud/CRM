"""Support console entities for ticket-first support operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

QueueSort = Literal["sla_due_asc", "priority_desc", "updated_desc"]
EscalationAction = Literal["reassign", "raise_priority", "page_on_call", "request_manager_review"]


@dataclass(frozen=True)
class QueueItem:
    ticket_id: str
    subject: str
    status: str
    priority: str
    owner_user_id: str
    queue_name: str
    response_due_at: str
    resolution_due_at: str
    sla_state: Literal["healthy", "at_risk", "breached"]


@dataclass(frozen=True)
class ConversationMessage:
    message_id: str
    sender_type: Literal["customer", "agent", "system"]
    body: str
    created_at: str


@dataclass(frozen=True)
class CustomerContext:
    account_id: str
    account_name: str
    contact_id: str
    contact_name: str
    contact_email: str
    open_ticket_count: int
    csat_score: float | None
    plan_tier: str


@dataclass(frozen=True)
class EscalationControl:
    ticket_id: str
    allowed_actions: tuple[EscalationAction, ...]
    recommended_action: EscalationAction
    rationale: str


@dataclass(frozen=True)
class SupportWorkspace:
    workspace_id: str
    workflow_name: str
    read_model: str
    primary_view: Literal["queue"]
    queue_items: tuple[QueueItem, ...]
    selected_ticket_id: str | None
    conversation_thread: tuple[ConversationMessage, ...]
    customer_context: CustomerContext | None
    escalation_controls: EscalationControl | None
    active_sla_timer: str
    views: tuple[str, ...] = field(
        default_factory=lambda: (
            "queue_view",
            "conversation_thread_panel",
            "customer_context_sidebar",
            "escalation_controls",
        )
    )


class SupportConsoleValidationError(ValueError):
    """Raised when support console contracts are invalid."""
