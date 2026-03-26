"""API contracts for communication integrations."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import CommunicationContractError, CommunicationMessage, CommunicationNotFoundError, CommunicationThread, LinkedEntityRef
from .services import CommunicationIntegrationService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "list_threads": {"method": "GET", "path": "/api/v1/communications/threads"},
    "create_or_get_thread": {"method": "POST", "path": "/api/v1/communications/threads"},
    "list_messages": {"method": "GET", "path": "/api/v1/communications/threads/{message_thread_id}/messages"},
    "send_email": {"method": "POST", "path": "/api/v1/communications/email/send"},
    "send_sms": {"method": "POST", "path": "/api/v1/communications/sms/send"},
    "send_whatsapp": {"method": "POST", "path": "/api/v1/communications/whatsapp/send"},
    "receive_message": {"method": "POST", "path": "/api/v1/communications/receive"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}


class CommunicationIntegrationApi:
    def __init__(self, service: CommunicationIntegrationService) -> None:
        self._service = service

    def list_threads(self, request_id: str) -> dict[str, Any]:
        return success([asdict(thread) for thread in self._service.list_threads()], request_id)

    def create_or_get_thread(self, thread: CommunicationThread, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.create_or_get_thread(thread)), request_id)
        except CommunicationContractError as exc:
            return error("validation_error", str(exc), request_id)

    def list_messages(self, message_thread_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success([asdict(message) for message in self._service.list_messages(message_thread_id)], request_id)
        except CommunicationNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def send_email(self, message: CommunicationMessage, linked_entity: LinkedEntityRef, request_id: str) -> dict[str, Any]:
        return self._send_with(self._service.send_email, message, linked_entity, request_id)

    def send_sms(self, message: CommunicationMessage, linked_entity: LinkedEntityRef, request_id: str) -> dict[str, Any]:
        return self._send_with(self._service.send_sms, message, linked_entity, request_id)

    def send_whatsapp(self, message: CommunicationMessage, linked_entity: LinkedEntityRef, request_id: str) -> dict[str, Any]:
        return self._send_with(self._service.send_whatsapp, message, linked_entity, request_id)

    def receive_message(self, message: CommunicationMessage, linked_entity: LinkedEntityRef, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.receive_message(message=message, linked_entity=linked_entity)), request_id)
        except (CommunicationContractError, CommunicationNotFoundError) as exc:
            return error("validation_error", str(exc), request_id)

    @staticmethod
    def _send_with(sender: Any, message: CommunicationMessage, linked_entity: LinkedEntityRef, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(sender(message=message, linked_entity=linked_entity)), request_id)
        except (CommunicationContractError, CommunicationNotFoundError) as exc:
            return error("validation_error", str(exc), request_id)
