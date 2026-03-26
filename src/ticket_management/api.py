"""API contracts for Ticket Management, aligned to docs/api-standards.md."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import Ticket, TicketNotFoundError, TicketStateError
from .services import TicketService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "list_tickets": {"method": "GET", "path": "/api/v1/tickets"},
    "create_ticket": {"method": "POST", "path": "/api/v1/tickets"},
    "get_ticket": {"method": "GET", "path": "/api/v1/tickets/{ticket_id}"},
    "start_progress": {"method": "POST", "path": "/api/v1/tickets/{ticket_id}/progress"},
    "record_first_response": {"method": "POST", "path": "/api/v1/tickets/{ticket_id}/responses"},
    "resolve_ticket": {"method": "POST", "path": "/api/v1/tickets/{ticket_id}/resolutions"},
    "close_ticket": {"method": "POST", "path": "/api/v1/tickets/{ticket_id}/closures"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": details or []},
        "meta": {"request_id": request_id},
    }


class TicketApi:
    def __init__(self, service: TicketService) -> None:
        self._service = service

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
