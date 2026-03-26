"""Self-QC checks for external API connectors and webhook mappings."""

from __future__ import annotations

from .entities import ALLOWED_PROVIDERS, INBOUND_WEBHOOK_ENDPOINTS, OUTBOUND_API_CONTRACTS
from .mapping import EventWebhookMapper


def run_self_qc() -> dict[str, bool]:
    mapper = EventWebhookMapper()
    mapper.validate_contract_coverage()

    all_integrations_defined = set(ALLOWED_PROVIDERS) == set(OUTBOUND_API_CONTRACTS.keys()) == set(INBOUND_WEBHOOK_ENDPOINTS.keys())

    no_undefined_endpoints = all(
        bool(contract.get("endpoints")) and all("path" in endpoint or "path_template" in endpoint for endpoint in contract["endpoints"].values())
        for contract in OUTBOUND_API_CONTRACTS.values()
    )

    auth_enforced = all(contract.get("auth") in {"bearer", "basic"} for contract in OUTBOUND_API_CONTRACTS.values())

    events_mapped_to_webhooks = len(mapper.map_event("notification.dispatched.v1", {"notification_id": "n-1"})) > 0

    return {
        "all_integrations_defined": all_integrations_defined,
        "no_undefined_endpoints": no_undefined_endpoints,
        "auth_correctly_enforced": auth_enforced,
        "events_correctly_mapped": events_mapped_to_webhooks,
    }
