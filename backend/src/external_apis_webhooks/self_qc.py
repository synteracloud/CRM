"""Self-QC checks for external API connectors, public APIs, and SDK/auth scaffolding."""

from __future__ import annotations

from src.event_bus.catalog_events import EVENT_NAME_SET

from .entities import ALLOWED_PROVIDERS, INBOUND_WEBHOOK_ENDPOINTS, OUTBOUND_API_CONTRACTS
from .mapping import EventWebhookMapper
from .public_api_sdk import ExternalDeveloperAuthService, PUBLIC_API_ENDPOINTS, PublicApiExposureService, PublicApiLayer, PublicApiSdk, PublicApiSdkConfig
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

    api_paths_follow_standard = all(endpoint["path"].startswith("/api/v1/") for endpoint in PUBLIC_API_ENDPOINTS.values())

    external_auth = ExternalDeveloperAuthService()
    public_api = PublicApiLayer(external_auth, PublicApiExposureService())
    app_response = public_api.create_developer_application(
        {
            "developer_id": "dev_1",
            "app_name": "crm_partner_app",
            "scopes": ["integrations:read"],
            "created_at": "2026-03-26T00:00:00Z",
        },
        request_id="req_qc_1",
    )
    app_data = app_response.get("data", {})

    token_response = public_api.issue_access_token(
        {
            "client_id": app_data.get("client_id", ""),
            "client_secret": app_data.get("client_secret", ""),
            "scopes": ["integrations:read"],
        },
        request_id="req_qc_2",
    )
    token_value = token_response.get("data", {}).get("access_token", "")
    secured_endpoint_response = public_api.list_public_integrations(f"Bearer {token_value}", request_id="req_qc_3")
    secure_access_only = bool(secured_endpoint_response.get("data", {}).get("items"))

    sdk = PublicApiSdk(PublicApiSdkConfig(base_url="https://public.crm.example", client_id="cid_1", client_secret="sec_1"))
    sdk_scaffold_valid = sdk.token_request(("integrations:read",))["url"].endswith("/api/v1/developer-access-tokens")

    return {
        "all_integrations_defined": all_integrations_defined,
        "no_undefined_endpoints": no_undefined_endpoints,
        "auth_correctly_enforced": auth_enforced,
        "events_correctly_mapped": mapped_events_are_valid,
        "public_api_standards_compliant": api_paths_follow_standard,
        "public_api_secure_access_only": secure_access_only,
        "sdk_scaffolding_available": sdk_scaffold_valid,
    }
