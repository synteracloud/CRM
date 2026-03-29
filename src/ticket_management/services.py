"""Services for Ticket lifecycle and SLA enforcement."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .entities import (
    EscalationAction,
    EscalationAuditRecord,
    EscalationRule,
    Ticket,
    TicketNotFoundError,
    TicketStateError,
)


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


class SlaEscalationService:
    """Multi-level SLA escalation engine with prediction hooks and audit trail."""

    def __init__(self, ticket_service: TicketService) -> None:
        self._ticket_service = ticket_service
        self._rules: dict[str, list[EscalationRule]] = {}
        self._audit_log: list[EscalationAuditRecord] = []
        self._next_audit_id = 1

    def register_rules(self, tenant_id: str, rules: list[EscalationRule]) -> None:
        ordered = sorted((r for r in rules if r.active), key=lambda r: (r.level, r.rule_id))
        for idx, rule in enumerate(ordered):
            if rule.level != idx + 1:
                raise TicketStateError("Escalation levels must be contiguous and start at 1.")
            if not rule.route_to:
                raise TicketStateError(f"Rule {rule.rule_id} has no route_to target.")
        self._rules[tenant_id] = ordered

    def get_rules(self, tenant_id: str) -> list[EscalationRule]:
        return list(self._rules.get(tenant_id, []))

    def evaluate_escalations(self, ticket_id: str, now: str) -> list[EscalationAction]:
        ticket = self._ticket_service.get_ticket(ticket_id)
        applicable_rules = self._rules.get(ticket.tenant_id, [])
        if not applicable_rules:
            raise TicketStateError(f"No escalation rules configured for tenant={ticket.tenant_id}")

        actions: list[EscalationAction] = []
        for rule in applicable_rules:
            if self._rule_matches(rule, ticket, now):
                action = EscalationAction(
                    ticket_id=ticket.ticket_id,
                    tenant_id=ticket.tenant_id,
                    rule_id=rule.rule_id,
                    level=rule.level,
                    route_to=rule.route_to,
                    reason=f"{rule.trigger} escalation",
                    escalated_at=now,
                )
                actions.append(action)
                self._append_audit(
                    ticket,
                    now,
                    "escalation.triggered",
                    {
                        "rule_id": rule.rule_id,
                        "level": rule.level,
                        "route_to": rule.route_to,
                        "trigger": rule.trigger,
                    },
                )
        if not actions:
            self._append_audit(ticket, now, "escalation.none", {"reason": "no_rules_matched"})
        return actions

    def predict_breach(self, ticket_id: str, now: str, horizon_minutes: int = 30) -> dict[str, bool | int]:
        ticket = self._ticket_service.get_ticket(ticket_id)
        now_dt = _parse_rfc3339(now)
        response_due = _parse_rfc3339(ticket.response_due_at)
        resolution_due = _parse_rfc3339(ticket.resolution_due_at)
        horizon = now_dt + timedelta(minutes=horizon_minutes)

        prediction = {
            "response_breach_likely": ticket.first_responded_at is None and response_due <= horizon,
            "resolution_breach_likely": ticket.resolved_at is None and resolution_due <= horizon,
            "horizon_minutes": horizon_minutes,
        }
        self._append_audit(ticket, now, "escalation.breach_prediction", prediction)
        return prediction

    def list_audit(self, ticket_id: str) -> list[EscalationAuditRecord]:
        return [entry for entry in self._audit_log if entry.ticket_id == ticket_id]

    def _rule_matches(self, rule: EscalationRule, ticket: Ticket, now: str) -> bool:
        now_dt = _parse_rfc3339(now)
        created_dt = _parse_rfc3339(ticket.created_at)
        threshold_time = created_dt + timedelta(minutes=rule.threshold_minutes)

        if rule.trigger == "time_since_created" and now_dt < threshold_time:
            return False
        if rule.trigger == "response_due" and now_dt < _parse_rfc3339(ticket.response_due_at):
            return False
        if rule.trigger == "resolution_due" and now_dt < _parse_rfc3339(ticket.resolution_due_at):
            return False

        if rule.condition_field:
            value = getattr(ticket, rule.condition_field, None)
            return self._check_condition(value, rule.condition_op, rule.condition_value)
        return True

    @staticmethod
    def _check_condition(value: str | None, op: str | None, expected: str | None) -> bool:
        if op == "eq":
            return value == expected
        if op == "neq":
            return value != expected
        if op == "exists":
            return value is not None
        raise TicketStateError(f"Unsupported condition op={op}")

    def _append_audit(self, ticket: Ticket, now: str, event_type: str, details: dict[str, object]) -> None:
        record = EscalationAuditRecord(
            audit_id=f"audit-{self._next_audit_id}",
            ticket_id=ticket.ticket_id,
            tenant_id=ticket.tenant_id,
            event_type=event_type,
            details=details,
            created_at=now,
        )
        self._next_audit_id += 1
        self._audit_log.append(record)


def _parse_rfc3339(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
