"""In-memory event bus with retry, idempotency, and dead-letter routing."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from .catalog_events import EVENT_NAME_SET
from .interfaces import Event, EventHandler, EventPublisher, EventSubscriber


class UnknownEventNameError(ValueError):
    """Raised when attempting to publish/subscribe an event not in the catalog."""


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 3


class InMemoryEventBus(EventPublisher, EventSubscriber):
    def __init__(self, retry_policy: RetryPolicy | None = None) -> None:
        self._retry_policy = retry_policy or RetryPolicy()
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._processed_event_keys: set[tuple[str, str, str]] = set()
        self._dead_lettered: list[Event] = []

    @property
    def dead_lettered(self) -> tuple[Event, ...]:
        return tuple(self._dead_lettered)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._validate_event_name(event_name)
        self._handlers[event_name].append(handler)

    def publish(self, event: Event) -> None:
        self._validate_event_name(event.event_name)
        dedupe_key = (event.tenant_id, event.event_name, event.event_id)

        if dedupe_key in self._processed_event_keys:
            return

        handlers = self._handlers.get(event.event_name, [])
        if not handlers:
            self._processed_event_keys.add(dedupe_key)
            return

        for handler in handlers:
            self._dispatch_with_retry(event, handler)

        self._processed_event_keys.add(dedupe_key)

    def _dispatch_with_retry(self, event: Event, handler: EventHandler) -> None:
        attempts = 0
        while True:
            try:
                handler(event)
                return
            except Exception as exc:  # noqa: BLE001 - handler errors are retried.
                attempts += 1
                if attempts > self._retry_policy.max_retries:
                    self._dead_lettered.append(self._build_dead_letter_event(event, exc, attempts - 1))
                    return

    def _build_dead_letter_event(self, source_event: Event, exc: Exception, retry_count: int) -> Event:
        now = datetime.now(timezone.utc).isoformat()
        return Event(
            event_name="eventbus.dead_lettered.v1",
            event_id=f"dead-letter::{source_event.event_id}",
            occurred_at=now,
            tenant_id=source_event.tenant_id,
            payload={
                "source_event_name": source_event.event_name,
                "source_event_id": source_event.event_id,
                "source_service": "in-memory-event-bus",
                "failure_reason": str(exc),
                "retry_count": retry_count,
                "dead_letter_topic": "dead-letter",
            },
        )

    @staticmethod
    def _validate_event_name(event_name: str) -> None:
        if event_name not in EVENT_NAME_SET:
            raise UnknownEventNameError(f"Unknown event name: {event_name}")
