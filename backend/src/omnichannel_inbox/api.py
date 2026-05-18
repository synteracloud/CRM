"""API contracts for Omnichannel Inbox service."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import Message, MessageThread, ThreadNotFoundError, ThreadStateError
from .services import OmnichannelInboxService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "list_threads": {"method": "GET", "path": "/api/v1/omnichannel/threads"},
    "create_or_get_thread": {"method": "POST", "path": "/api/v1/omnichannel/threads"},
    "get_thread": {"method": "GET", "path": "/api/v1/omnichannel/threads/{message_thread_id}"},
    "list_messages": {"method": "GET", "path": "/api/v1/omnichannel/threads/{message_thread_id}/messages"},
    "post_message": {"method": "POST", "path": "/api/v1/omnichannel/threads/{message_thread_id}/messages"},
    "route_thread": {"method": "POST", "path": "/api/v1/omnichannel/threads/{message_thread_id}/routing"},
    "get_thread_routing": {"method": "GET", "path": "/api/v1/omnichannel/threads/{message_thread_id}/routing"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}


class OmnichannelInboxApi:
    def __init__(self, service: OmnichannelInboxService) -> None:
        self._service = service

    def list_threads(self, request_id: str) -> dict[str, Any]:
        return success([asdict(thread) for thread in self._service.list_threads()], request_id)

    def create_or_get_thread(self, thread: MessageThread, request_id: str, dedupe_key: str | None = None) -> dict[str, Any]:
        try:
            stored = self._service.upsert_thread(thread, dedupe_key=dedupe_key)
            return success(asdict(stored), request_id)
        except ThreadStateError as exc:
            return error("conflict", str(exc), request_id)

    def get_thread(self, message_thread_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.get_thread(message_thread_id)), request_id)
        except ThreadNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def list_messages(self, message_thread_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success([asdict(msg) for msg in self._service.list_messages(message_thread_id)], request_id)
        except ThreadNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def post_message(
        self,
        message: Message,
        request_id: str,
        *,
        customer_account_id: str | None = None,
        customer_contact_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            stored = self._service.ingest_message(
                message,
                customer_account_id=customer_account_id,
                customer_contact_id=customer_contact_id,
            )
            return success(asdict(stored), request_id)
        except (ThreadNotFoundError, ThreadStateError) as exc:
            return error("validation_error", str(exc), request_id)

    def route_thread(self, message_thread_id: str, request_id: str, assigned_at: str) -> dict[str, Any]:
        try:
            decision = self._service.route_thread(message_thread_id, assigned_at=assigned_at)
            return success(asdict(decision), request_id)
        except ThreadNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def get_thread_routing(self, message_thread_id: str, request_id: str) -> dict[str, Any]:
        try:
            decision = self._service.get_routing(message_thread_id)
            return success(asdict(decision), request_id)
        except ThreadNotFoundError as exc:
            return error("not_found", str(exc), request_id)
