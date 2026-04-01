"""Event tracking store with payload validation and query support."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from .catalog_events import EVENT_NAME_SET
from .catalog_schema import load_event_payload_requirements
from .interfaces import Event


class EventValidationError(ValueError):
    """Raised when an event does not satisfy catalog requirements."""


class EventStore:
    def __init__(self) -> None:
        self._events: list[Event] = []
        self._event_by_dedupe_key: dict[tuple[str, str, str], Event] = {}
        self._payload_requirements = load_event_payload_requirements()

    def append(self, event: Event) -> Event:
        self._validate(event)
        dedupe_key = (event.tenant_id, event.event_name, event.event_id)
        if dedupe_key in self._event_by_dedupe_key:
            return self._event_by_dedupe_key[dedupe_key]

        self._events.append(event)
        self._event_by_dedupe_key[dedupe_key] = event
        return event

    def get(self, event_id: str) -> Event | None:
        for event in self._events:
            if event.event_id == event_id:
                return event
        return None

    def query(
        self,
        *,
        tenant_id: str | None = None,
        event_name: str | None = None,
        occurred_from: str | None = None,
        occurred_to: str | None = None,
        limit: int = 100,
    ) -> list[Event]:
        events = self._events
        if tenant_id:
            events = [event for event in events if event.tenant_id == tenant_id]
        if event_name:
            events = [event for event in events if event.event_name == event_name]
        if occurred_from:
            start = _parse_iso(occurred_from)
            events = [event for event in events if _parse_iso(event.occurred_at) >= start]
        if occurred_to:
            end = _parse_iso(occurred_to)
            events = [event for event in events if _parse_iso(event.occurred_at) <= end]

        return events[: max(limit, 0)]

    def _validate(self, event: Event) -> None:
        if event.event_name not in EVENT_NAME_SET:
            raise EventValidationError(f"Unknown event name: {event.event_name}")

        required_payload_fields = self._payload_requirements.get(event.event_name, ())
        missing = [field for field in required_payload_fields if field not in event.payload]
        if missing:
            raise EventValidationError(
                f"Missing payload fields for {event.event_name}: {', '.join(sorted(missing))}"
            )



def _parse_iso(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)



def event_to_dict(event: Event) -> dict[str, object]:
    return asdict(event)
