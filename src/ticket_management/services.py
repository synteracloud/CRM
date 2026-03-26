"""Services for Ticket lifecycle and SLA enforcement."""

from __future__ import annotations

from datetime import datetime, timezone

from .entities import Ticket, TicketNotFoundError, TicketStateError


class TicketService:
    """In-memory ticket service with deterministic lifecycle and SLA rules."""

    def __init__(self) -> None:
        self._store: dict[str, Ticket] = {}

    def list_tickets(self) -> list[Ticket]:
        return list(self._store.values())

    def create_ticket(self, ticket: Ticket) -> Ticket:
        if ticket.ticket_id in self._store:
            raise TicketStateError(f"Ticket already exists: {ticket.ticket_id}")
        if ticket.status != "open":
            raise TicketStateError("Tickets must be created in open status.")
        self._store[ticket.ticket_id] = ticket
        return ticket

    def get_ticket(self, ticket_id: str) -> Ticket:
        ticket = self._store.get(ticket_id)
        if not ticket:
            raise TicketNotFoundError(f"Ticket not found: {ticket_id}")
        return ticket

    def start_progress(self, ticket_id: str) -> Ticket:
        ticket = self.get_ticket(ticket_id)
        if ticket.status != "open":
            raise TicketStateError(f"Only open tickets can move to in_progress. current={ticket.status}")
        updated = ticket.patch(status="in_progress")
        self._store[ticket_id] = updated
        return updated

    def record_first_response(self, ticket_id: str, responded_at: str) -> Ticket:
        ticket = self.get_ticket(ticket_id)
        if ticket.status not in {"open", "in_progress"}:
            raise TicketStateError(f"Cannot record first response for status={ticket.status}")
        if ticket.first_responded_at:
            raise TicketStateError("First response has already been recorded.")
        if self._is_after(responded_at, ticket.response_due_at):
            raise TicketStateError(
                f"Response SLA breached for ticket={ticket.ticket_id}. responded_at={responded_at}, due_at={ticket.response_due_at}"
            )
        updated = ticket.patch(first_responded_at=responded_at)
        self._store[ticket_id] = updated
        return updated

    def resolve_ticket(self, ticket_id: str, resolved_at: str) -> Ticket:
        ticket = self.get_ticket(ticket_id)
        if ticket.status != "in_progress":
            raise TicketStateError(f"Only in_progress tickets can be resolved. current={ticket.status}")
        if self._is_after(resolved_at, ticket.resolution_due_at):
            raise TicketStateError(
                f"Resolution SLA breached for ticket={ticket.ticket_id}. resolved_at={resolved_at}, due_at={ticket.resolution_due_at}"
            )
        updated = ticket.patch(status="resolved", resolved_at=resolved_at)
        self._store[ticket_id] = updated
        return updated

    def close_ticket(self, ticket_id: str, closed_at: str) -> Ticket:
        ticket = self.get_ticket(ticket_id)
        if ticket.status != "resolved":
            raise TicketStateError(f"Only resolved tickets can be closed. current={ticket.status}")
        if self._is_after(closed_at, ticket.resolution_due_at):
            raise TicketStateError(
                f"Cannot close after resolution SLA due_at={ticket.resolution_due_at}; closed_at={closed_at}"
            )
        updated = ticket.patch(status="closed", closed_at=closed_at)
        self._store[ticket_id] = updated
        return updated

    @staticmethod
    def _is_after(value: str, boundary: str) -> bool:
        return _parse_rfc3339(value) > _parse_rfc3339(boundary)


def _parse_rfc3339(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
