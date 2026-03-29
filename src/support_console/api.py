"""API contracts for support console workspace."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import ConversationMessage, CustomerContext, QueueItem, SupportConsoleValidationError
from .services import SupportConsoleService

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "upsert_queue_item": {"method": "POST", "path": "/api/v1/support/console/queue"},
    "add_message": {"method": "POST", "path": "/api/v1/support/console/tickets/{ticket_id}/messages"},
    "set_customer_context": {"method": "PUT", "path": "/api/v1/support/console/tickets/{ticket_id}/context"},
    "build_workspace": {"method": "GET", "path": "/api/v1/support/console/workspace"},
    "escalate": {"method": "POST", "path": "/api/v1/support/console/tickets/{ticket_id}/escalate"},
}


class SupportConsoleApi:
    def __init__(self, service: SupportConsoleService) -> None:
        self._service = service

    def upsert_queue_item(self, item: QueueItem, request_id: str) -> dict[str, Any]:
        stored = self._service.upsert_queue_item(item)
        return {"data": asdict(stored), "meta": {"request_id": request_id}}

    def add_message(self, ticket_id: str, message: dict[str, str], request_id: str) -> dict[str, Any]:
        try:
            stored = self._service.add_conversation_message(
                ticket_id=ticket_id,
                message=self._message_from_payload(message),
            )
            return {"data": asdict(stored), "meta": {"request_id": request_id}}
        except SupportConsoleValidationError as exc:
            return self._error("validation_error", str(exc), request_id)

    def set_customer_context(self, ticket_id: str, context: CustomerContext, request_id: str) -> dict[str, Any]:
        try:
            stored = self._service.set_customer_context(ticket_id, context)
            return {"data": asdict(stored), "meta": {"request_id": request_id}}
        except SupportConsoleValidationError as exc:
            return self._error("validation_error", str(exc), request_id)

    def build_workspace(self, request_id: str, selected_ticket_id: str | None = None) -> dict[str, Any]:
        try:
            workspace = self._service.build_workspace(
                workspace_id=f"ws-{request_id}",
                selected_ticket_id=selected_ticket_id,
            )
            return {"data": asdict(workspace), "meta": {"request_id": request_id}}
        except SupportConsoleValidationError as exc:
            return self._error("validation_error", str(exc), request_id)

    def escalate(self, ticket_id: str, action: str, request_id: str) -> dict[str, Any]:
        try:
            updated = self._service.perform_escalation_action(ticket_id, action)
            return {"data": asdict(updated), "meta": {"request_id": request_id}}
        except SupportConsoleValidationError as exc:
            return self._error("validation_error", str(exc), request_id)

    @staticmethod
    def _message_from_payload(payload: dict[str, str]) -> ConversationMessage:
        return ConversationMessage(
            message_id=payload["message_id"],
            sender_type=payload["sender_type"],
            body=payload["body"],
            created_at=payload["created_at"],
        )

    @staticmethod
    def _error(code: str, message: str, request_id: str) -> dict[str, Any]:
        return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}
