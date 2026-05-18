"""API surface for event tracking and query operations."""

from __future__ import annotations

from typing import Any

from .interfaces import Event
from .store import EventStore, EventValidationError, event_to_dict

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "record_event": {"method": "POST", "path": "/api/v1/events"},
    "get_event": {"method": "GET", "path": "/api/v1/events/{event_id}"},
    "query_events": {"method": "GET", "path": "/api/v1/event-queries"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": []},
        "meta": {"request_id": request_id},
    }


class EventTrackingApi:
    def __init__(self, store: EventStore) -> None:
        self._store = store

    def record_event(self, event: Event, request_id: str) -> dict[str, Any]:
        try:
            return success(event_to_dict(self._store.append(event)), request_id)
        except EventValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def get_event(self, event_id: str, request_id: str) -> dict[str, Any]:
        event = self._store.get(event_id)
        if not event:
            return error("not_found", f"Event not found: {event_id}", request_id)
        return success(event_to_dict(event), request_id)

    def query_events(
        self,
        request_id: str,
        tenant_id: str | None = None,
        event_name: str | None = None,
        occurred_from: str | None = None,
        occurred_to: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        events = self._store.query(
            tenant_id=tenant_id,
            event_name=event_name,
            occurred_from=occurred_from,
            occurred_to=occurred_to,
            limit=limit,
        )
        return success([event_to_dict(event) for event in events], request_id)
