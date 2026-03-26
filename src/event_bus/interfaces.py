"""Event bus interfaces for publish/subscribe contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class Event:
    event_name: str
    event_id: str
    occurred_at: str
    tenant_id: str
    payload: dict[str, Any]


class EventHandler(Protocol):
    def __call__(self, event: Event) -> None: ...


class EventPublisher(Protocol):
    def publish(self, event: Event) -> None: ...


class EventSubscriber(Protocol):
    def subscribe(self, event_name: str, handler: EventHandler) -> None: ...
