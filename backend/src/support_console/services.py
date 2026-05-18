"""Support console service implementing ticket-first workspace interactions."""

from __future__ import annotations

from dataclasses import replace

from .entities import (
    ConversationMessage,
    CustomerContext,
    EscalationControl,
    QueueItem,
    QueueSort,
    SupportConsoleValidationError,
    SupportWorkspace,
)


class SupportConsoleService:
    def __init__(self) -> None:
        self._queue: dict[str, QueueItem] = {}
        self._messages: dict[str, list[ConversationMessage]] = {}
        self._contexts: dict[str, CustomerContext] = {}

    def upsert_queue_item(self, item: QueueItem) -> QueueItem:
        self._queue[item.ticket_id] = item
        return item

    def add_conversation_message(self, ticket_id: str, message: ConversationMessage) -> ConversationMessage:
        if ticket_id not in self._queue:
            raise SupportConsoleValidationError(f"Unknown ticket_id: {ticket_id}")
        self._messages.setdefault(ticket_id, []).append(message)
        return message

    def set_customer_context(self, ticket_id: str, context: CustomerContext) -> CustomerContext:
        if ticket_id not in self._queue:
            raise SupportConsoleValidationError(f"Unknown ticket_id: {ticket_id}")
        self._contexts[ticket_id] = context
        return context

    def build_workspace(
        self,
        *,
        workspace_id: str,
        selected_ticket_id: str | None,
        queue_sort: QueueSort = "sla_due_asc",
    ) -> SupportWorkspace:
        queue_items = self._sorted_queue(queue_sort)

        if selected_ticket_id and selected_ticket_id not in self._queue:
            raise SupportConsoleValidationError(f"Unknown ticket_id: {selected_ticket_id}")

        active_sla_timer = self._active_sla_timer(selected_ticket_id, queue_items)
        thread = tuple(self._messages.get(selected_ticket_id or "", []))
        context = self._contexts.get(selected_ticket_id or "")
        escalation_controls = self._build_escalation_controls(selected_ticket_id) if selected_ticket_id else None

        workspace = SupportWorkspace(
            workspace_id=workspace_id,
            workflow_name="Case management & SLA",
            read_model="CaseSLAOperationalRM",
            primary_view="queue",
            queue_items=queue_items,
            selected_ticket_id=selected_ticket_id,
            conversation_thread=thread,
            customer_context=context,
            escalation_controls=escalation_controls,
            active_sla_timer=active_sla_timer,
        )
        self._validate_workspace(workspace)
        return workspace

    def perform_escalation_action(self, ticket_id: str, action: str) -> QueueItem:
        if ticket_id not in self._queue:
            raise SupportConsoleValidationError(f"Unknown ticket_id: {ticket_id}")

        controls = self._build_escalation_controls(ticket_id)
        if action not in controls.allowed_actions:
            raise SupportConsoleValidationError(f"Action not allowed for ticket={ticket_id}: {action}")

        item = self._queue[ticket_id]
        if action == "raise_priority" and item.priority != "urgent":
            updated = replace(item, priority="urgent", sla_state="at_risk")
        elif action == "page_on_call":
            updated = replace(item, owner_user_id="on-call-support", sla_state="at_risk")
        elif action == "request_manager_review":
            updated = replace(item, queue_name="manager_review")
        else:
            updated = replace(item, queue_name="escalations")

        self._queue[ticket_id] = updated
        return updated

    def _sorted_queue(self, queue_sort: QueueSort) -> tuple[QueueItem, ...]:
        items = list(self._queue.values())
        if queue_sort == "sla_due_asc":
            items.sort(key=lambda item: (item.response_due_at, item.resolution_due_at, item.ticket_id))
        elif queue_sort == "priority_desc":
            rank = {"urgent": 4, "high": 3, "medium": 2, "low": 1}
            items.sort(key=lambda item: (-rank.get(item.priority, 0), item.response_due_at, item.ticket_id))
        else:
            items.sort(key=lambda item: item.ticket_id)
        return tuple(items)

    def _active_sla_timer(self, selected_ticket_id: str | None, queue_items: tuple[QueueItem, ...]) -> str:
        selected = self._queue.get(selected_ticket_id or "")
        if selected:
            return f"{selected.ticket_id}: response_due={selected.response_due_at}, resolution_due={selected.resolution_due_at}"
        if queue_items:
            first = queue_items[0]
            return f"{first.ticket_id}: response_due={first.response_due_at}, resolution_due={first.resolution_due_at}"
        return "no_active_ticket"

    def _build_escalation_controls(self, ticket_id: str) -> EscalationControl:
        ticket = self._queue[ticket_id]
        if ticket.sla_state == "breached":
            return EscalationControl(
                ticket_id=ticket_id,
                allowed_actions=("page_on_call", "request_manager_review", "reassign"),
                recommended_action="page_on_call",
                rationale="SLA already breached; immediate real-time escalation required.",
            )
        if ticket.sla_state == "at_risk":
            return EscalationControl(
                ticket_id=ticket_id,
                allowed_actions=("raise_priority", "reassign", "request_manager_review"),
                recommended_action="raise_priority",
                rationale="SLA at risk; increase urgency to prevent breach.",
            )
        return EscalationControl(
            ticket_id=ticket_id,
            allowed_actions=("reassign",),
            recommended_action="reassign",
            rationale="Healthy SLA, default to ownership correction only.",
        )

    @staticmethod
    def _validate_workspace(workspace: SupportWorkspace) -> None:
        if "queue_view" not in workspace.views:
            raise SupportConsoleValidationError("Queue view is required")
        if not workspace.active_sla_timer:
            raise SupportConsoleValidationError("SLA visibility must always be present")
