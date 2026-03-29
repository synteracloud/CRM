"""API contracts for Ticket Management, aligned to docs/api-standards.md."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import EscalationRule, Ticket, TicketNotFoundError, TicketStateError
from .services import SlaEscalationService, TicketService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "list_tickets": {"method": "GET", "path": "/api/v1/tickets"},
    "create_ticket": {"method": "POST", "path": "/api/v1/tickets"},
    "get_ticket": {"method": "GET", "path": "/api/v1/tickets/{ticket_id}"},
    "start_progress": {"method": "POST", "path": "/api/v1/tickets/{ticket_id}/progress"},
    "record_first_response": {"method": "POST", "path": "/api/v1/tickets/{ticket_id}/responses"},
    "resolve_ticket": {"method": "POST", "path": "/api/v1/tickets/{ticket_id}/resolutions"},
    "close_ticket": {"method": "POST", "path": "/api/v1/tickets/{ticket_id}/closures"},
    "register_escalation_rules": {"method": "PUT", "path": "/api/v1/tickets/escalation-rules"},
    "evaluate_escalation": {"method": "POST", "path": "/api/v1/tickets/{ticket_id}/escalations/evaluate"},
    "predict_breach": {"method": "POST", "path": "/api/v1/tickets/{ticket_id}/escalations/predict"},
    "list_escalation_audit": {"method": "GET", "path": "/api/v1/tickets/{ticket_id}/escalations/audit"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": details or []},
        "meta": {"request_id": request_id},
    }


class TicketApi:
    def __init__(self, service: TicketService, escalation_service: SlaEscalationService | None = None) -> None:
        self._service = service
        self._escalation_service = escalation_service

    def list_tickets(self, request_id: str) -> dict[str, Any]:
        return success([asdict(ticket) for ticket in self._service.list_tickets()], request_id)

    def create_ticket(self, ticket: Ticket, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.create_ticket(ticket)), request_id)
        except TicketStateError as exc:
            return error("conflict", str(exc), request_id)

    def get_ticket(self, ticket_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.get_ticket(ticket_id)), request_id)
        except TicketNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def start_progress(self, ticket_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.start_progress(ticket_id)), request_id)
        except TicketNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except TicketStateError as exc:
            return error("conflict", str(exc), request_id)

    def record_first_response(self, ticket_id: str, responded_at: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.record_first_response(ticket_id, responded_at)), request_id)
        except TicketNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except TicketStateError as exc:
            return error("conflict", str(exc), request_id)

    def resolve_ticket(self, ticket_id: str, resolved_at: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.resolve_ticket(ticket_id, resolved_at)), request_id)
        except TicketNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except TicketStateError as exc:
            return error("conflict", str(exc), request_id)

    def close_ticket(self, ticket_id: str, closed_at: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.close_ticket(ticket_id, closed_at)), request_id)
        except TicketNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except TicketStateError as exc:
            return error("conflict", str(exc), request_id)

    def register_escalation_rules(self, tenant_id: str, rules: list[EscalationRule], request_id: str) -> dict[str, Any]:
        try:
            service = self._require_escalation_service()
            service.register_rules(tenant_id, rules)
            return success([asdict(rule) for rule in service.get_rules(tenant_id)], request_id)
        except TicketStateError as exc:
            return error("conflict", str(exc), request_id)

    def evaluate_escalation(self, ticket_id: str, now: str, request_id: str) -> dict[str, Any]:
        try:
            service = self._require_escalation_service()
            actions = service.evaluate_escalations(ticket_id, now)
            return success([asdict(action) for action in actions], request_id)
        except (TicketNotFoundError, TicketStateError) as exc:
            return error("conflict", str(exc), request_id)

    def predict_breach(self, ticket_id: str, now: str, horizon_minutes: int, request_id: str) -> dict[str, Any]:
        try:
            service = self._require_escalation_service()
            return success(service.predict_breach(ticket_id, now, horizon_minutes), request_id)
        except (TicketNotFoundError, TicketStateError) as exc:
            return error("conflict", str(exc), request_id)

    def list_escalation_audit(self, ticket_id: str, request_id: str) -> dict[str, Any]:
        try:
            service = self._require_escalation_service()
            return success([asdict(record) for record in service.list_audit(ticket_id)], request_id)
        except TicketStateError as exc:
            return error("conflict", str(exc), request_id)

    def _require_escalation_service(self) -> SlaEscalationService:
        if self._escalation_service is None:
            raise TicketStateError("SLA escalation service is not configured")
        return self._escalation_service
