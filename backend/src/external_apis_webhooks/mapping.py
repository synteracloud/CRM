"""Mapping from internal CRM events to outbound webhook topics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.event_bus.catalog_events import EVENT_NAMES

EVENT_TO_WEBHOOK_MAP: dict[str, list[dict[str, str]]] = {
    "payment.event.recorded.v1": [
        {"provider": "stripe", "event_type": "payment_intent.succeeded"},
    ],
    "invoice.summary.updated.v1": [
        {"provider": "stripe", "event_type": "invoice.payment_failed"},
    ],
    "subscription.status.changed.v1": [
        {"provider": "stripe", "event_type": "customer.subscription.updated"},
    ],
    "notification.dispatched.v1": [
        {"provider": "sendgrid", "event_type": "processed"},
        {"provider": "twilio", "event_type": "sent"},
    ],
    "notification.failed.v1": [
        {"provider": "sendgrid", "event_type": "bounce"},
        {"provider": "twilio", "event_type": "failed"},
    ],
    "communication.message.engagement.updated.v1": [
        {"provider": "sendgrid", "event_type": "delivered"},
        {"provider": "sendgrid", "event_type": "open"},
        {"provider": "sendgrid", "event_type": "click"},
        {"provider": "twilio", "event_type": "delivered"},
        {"provider": "twilio", "event_type": "undelivered"},
    ],
}


class EventWebhookMappingError(ValueError):
    """Raised for invalid mapping operations."""


@dataclass(frozen=True)
class OutboundWebhookEvent:
    provider: str
    event_name: str
    payload: dict[str, Any]


class EventWebhookMapper:
    def __init__(self, mapping: dict[str, list[dict[str, str]]] | None = None) -> None:
        self._mapping = mapping or EVENT_TO_WEBHOOK_MAP

    def map_event(self, event_name: str, payload: dict[str, Any]) -> list[OutboundWebhookEvent]:
        if event_name not in EVENT_NAMES:
            raise EventWebhookMappingError(f"Unknown catalog event: {event_name}")

        destinations = self._mapping.get(event_name, [])
        return [
            OutboundWebhookEvent(provider=destination["provider"], event_name=destination["event_type"], payload=payload)
            for destination in destinations
        ]

    def validate_contract_coverage(self) -> None:
        for event_name in self._mapping:
            if event_name not in EVENT_NAMES:
                raise EventWebhookMappingError(f"Mapped event not in catalog: {event_name}")
