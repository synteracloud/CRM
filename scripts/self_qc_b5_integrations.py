"""Self-QC checks for B5 integration scope (external APIs, webhooks, communication flows)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.communication_integrations import API_ENDPOINTS as COMMUNICATION_API_ENDPOINTS
from src.communication_integrations import CommunicationIntegrationService, CommunicationMessage, CommunicationThread, LinkedEntityRef
from src.external_apis_webhooks import (
    ALLOWED_PROVIDERS,
    API_ENDPOINTS as EXTERNAL_API_ENDPOINTS,
    EVENT_TO_WEBHOOK_MAP,
    INBOUND_WEBHOOK_ENDPOINTS,
    OUTBOUND_API_CONTRACTS,
    EventWebhookMapper,
    run_self_qc,
)


def assert_integrations_match_contract() -> None:
    providers = set(ALLOWED_PROVIDERS)
    if providers != set(OUTBOUND_API_CONTRACTS) or providers != set(INBOUND_WEBHOOK_ENDPOINTS):
        raise AssertionError("Provider definitions and integration contracts are out of sync.")


def assert_outbound_endpoints_match_contract() -> None:
    stripe = OUTBOUND_API_CONTRACTS["stripe"]["endpoints"]
    sendgrid = OUTBOUND_API_CONTRACTS["sendgrid"]["endpoints"]
    twilio = OUTBOUND_API_CONTRACTS["twilio"]["endpoints"]

    if stripe["payment_intents"]["path"] != "/v1/payment_intents":
        raise AssertionError("Stripe payment intent endpoint mismatch.")
    if stripe["customers"]["path"] != "/v1/customers":
        raise AssertionError("Stripe customer endpoint mismatch.")
    if stripe["subscriptions"]["path"] != "/v1/subscriptions":
        raise AssertionError("Stripe subscription endpoint mismatch.")
    if sendgrid["mail_send"]["path"] != "/v3/mail/send":
        raise AssertionError("SendGrid mail send endpoint mismatch.")
    if twilio["messages"]["path_template"] != "/2010-04-01/Accounts/{account_sid}/Messages.json":
        raise AssertionError("Twilio messages endpoint mismatch.")


def assert_webhooks_mapped_to_expected_paths() -> None:
    expected = {
        "stripe": "/webhooks/stripe",
        "sendgrid": "/webhooks/sendgrid/events",
        "twilio": "/webhooks/twilio/status",
    }
    for provider, path in expected.items():
        if INBOUND_WEBHOOK_ENDPOINTS[provider]["path"] != path:
            raise AssertionError(f"Webhook path mismatch for provider={provider}")


def assert_webhook_events_covered() -> None:
    required_events = {
        "payment_intent.succeeded",
        "invoice.payment_failed",
        "customer.subscription.updated",
        "processed",
        "delivered",
        "bounce",
        "open",
        "click",
        "sent",
        "undelivered",
        "failed",
    }
    mapped_events = {item["event_type"] for events in EVENT_TO_WEBHOOK_MAP.values() for item in events}
    if not required_events.issubset(mapped_events):
        missing = sorted(required_events - mapped_events)
        raise AssertionError(f"Mapped events missing required webhook event types: {missing}")


def assert_event_catalog_alignment() -> None:
    EventWebhookMapper().validate_contract_coverage()


def assert_external_api_endpoints_follow_api_standards() -> None:
    pattern = re.compile(r"^/api/v\d+/[a-z0-9-]+(?:/[a-z0-9{}_-]+)*$")
    send_keys = ("send_stripe_api", "send_sendgrid_api", "send_twilio_api")
    for key in send_keys:
        endpoint = EXTERNAL_API_ENDPOINTS[key]
        if not pattern.match(endpoint["path"]):
            raise AssertionError(f"External endpoint violates API standard path pattern: {endpoint['path']}")


def assert_communication_api_endpoints_follow_api_standards() -> None:
    pattern = re.compile(r"^/api/v\d+/[a-z0-9-]+(?:/[a-z0-9{}_-]+)*$")
    for name, endpoint in COMMUNICATION_API_ENDPOINTS.items():
        if not pattern.match(endpoint["path"]):
            raise AssertionError(f"Communication endpoint {name} violates API path standard: {endpoint['path']}")


def assert_communication_linkage_and_no_orphans() -> None:
    service = CommunicationIntegrationService()
    service.register_valid_entities(tenant_id="tenant-1", lead_ids={"lead-1"}, contact_ids={"contact-1"}, ticket_ids={"ticket-1"})

    thread = CommunicationThread(
        message_thread_id="thr-1",
        tenant_id="tenant-1",
        channel_type="email",
        provider="sendgrid",
        provider_thread_key="sg-thread-1",
        linked_entity_type="contact",
        linked_entity_id="contact-1",
        subject="Welcome",
        participants=("noreply@crm.test", "customer@example.com"),
        status="open",
        created_at="2026-03-26T01:00:00Z",
        updated_at="2026-03-26T01:00:00Z",
    )
    service.create_or_get_thread(thread)

    message = CommunicationMessage(
        message_id="msg-1",
        tenant_id="tenant-1",
        message_thread_id="thr-1",
        provider="sendgrid",
        provider_message_id="sg-msg-1",
        channel_type="email",
        direction="outbound",
        sender="noreply@crm.test",
        recipient="customer@example.com",
        body="Hello",
        status="queued",
        linked_entity_type="contact",
        linked_entity_id="contact-1",
        sent_at="2026-03-26T01:01:00Z",
    )
    service.send_email(message=message, linked_entity=LinkedEntityRef("contact", "contact-1"))

    messages = service.list_messages("thr-1")
    if len(messages) != 1:
        raise AssertionError("Expected one linked message and no orphan messages.")
    if messages[0].message_thread_id != thread.message_thread_id:
        raise AssertionError("Message is orphaned from thread.")


def assert_external_self_qc_green() -> None:
    qc = run_self_qc()
    if not all(qc.values()):
        raise AssertionError(f"external_apis_webhooks self_qc failed: {qc}")


def assert_no_orphan_event_mappings() -> None:
    for event_name, destinations in EVENT_TO_WEBHOOK_MAP.items():
        if not destinations:
            raise AssertionError(f"Event has no downstream mapping: {event_name}")
        for destination in destinations:
            if destination['provider'] not in ALLOWED_PROVIDERS:
                raise AssertionError(f"Event mapped to unsupported provider: {event_name} -> {destination}")


def main() -> None:
    checks = [
        assert_integrations_match_contract,
        assert_outbound_endpoints_match_contract,
        assert_webhooks_mapped_to_expected_paths,
        assert_webhook_events_covered,
        assert_event_catalog_alignment,
        assert_external_api_endpoints_follow_api_standards,
        assert_communication_api_endpoints_follow_api_standards,
        assert_communication_linkage_and_no_orphans,
        assert_external_self_qc_green,
        assert_no_orphan_event_mappings,
    ]

    for idx, check in enumerate(checks, start=1):
        check()
        print(f"{idx}/10 PASS - {check.__name__ if hasattr(check, '__name__') else 'final_regression_gate'}")

    print("Self-QC score: 10/10")


if __name__ == "__main__":
    main()
