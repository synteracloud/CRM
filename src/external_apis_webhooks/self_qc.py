"""Self-QC checks for external API connectors and webhook mappings."""

from __future__ import annotations

from src.event_bus.catalog_events import EVENT_NAME_SET

from .entities import ALLOWED_PROVIDERS, INBOUND_WEBHOOK_ENDPOINTS, OUTBOUND_API_CONTRACTS
from .mapping import EventWebhookMapper
from .services import WebhookDeliveryService, WebhookSubscriptionService


def run_self_qc() -> dict[str, bool]:
    mapper = EventWebhookMapper()
    mapper.validate_contract_coverage()

    all_integrations_defined = set(ALLOWED_PROVIDERS) == set(OUTBOUND_API_CONTRACTS.keys()) == set(INBOUND_WEBHOOK_ENDPOINTS.keys())

    no_undefined_endpoints = all(
        bool(contract.get("endpoints")) and all("path" in endpoint or "path_template" in endpoint for endpoint in contract["endpoints"].values())
        for contract in OUTBOUND_API_CONTRACTS.values()
    )

    auth_enforced = all(contract.get("auth") in {"bearer", "basic"} for contract in OUTBOUND_API_CONTRACTS.values())

    mapped_events_are_valid = all(event_name in EVENT_NAME_SET for event_name in mapper._mapping)  # noqa: SLF001

    # Gap check: every subscription for an event gets one delivery record.
    subscriptions = WebhookSubscriptionService()
    subscriptions.subscribe("https://example.com/a", ["notification.dispatched.v1", "notification.failed.v1"])
    subscriptions.subscribe("https://example.com/b", ["notification.dispatched.v1"])
    deliveries = WebhookDeliveryService(subscriptions).deliver_event("notification.dispatched.v1", {"notification_id": "n-1"})
    no_delivery_gaps = len(deliveries) == 2 and all(delivery.event_name == "notification.dispatched.v1" for delivery in deliveries)

    return {
        "all_integrations_defined": all_integrations_defined,
        "no_undefined_endpoints": no_undefined_endpoints,
        "auth_correctly_enforced": auth_enforced,
        "all_events_valid": mapped_events_are_valid,
        "no_delivery_gaps": no_delivery_gaps,
    }
