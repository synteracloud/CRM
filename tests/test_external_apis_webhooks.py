from __future__ import annotations

import unittest

from src.external_apis_webhooks import (
    API_ENDPOINTS,
    EventWebhookMapper,
    ExternalApiConnectorService,
    InboundWebhook,
    IntegrationAuth,
    OutboundRequest,
    SecretStore,
    WebhookDeliveryService,
    WebhookReceiverService,
    WebhookSenderService,
    WebhookSubscriptionService,
    run_self_qc,
)


class ExternalApisWebhooksTests(unittest.TestCase):
    def setUp(self) -> None:
        secrets = SecretStore(
            {
                "STRIPE_SECRET_KEY": "sk_test_123",
                "SENDGRID_API_KEY": "sg_key_123",
                "TWILIO_ACCOUNT_SID": "AC123",
                "TWILIO_AUTH_TOKEN": "twilio_token_123",
            }
        )
        self.auth = IntegrationAuth(secrets)

    def test_endpoints_match_contract_and_no_undefined_webhook_path(self) -> None:
        self.assertEqual(API_ENDPOINTS["receive_stripe_webhook"]["path"], "/webhooks/stripe")
        self.assertEqual(API_ENDPOINTS["receive_sendgrid_webhook"]["path"], "/webhooks/sendgrid/events")
        self.assertEqual(API_ENDPOINTS["receive_twilio_webhook"]["path"], "/webhooks/twilio/status")

    def test_outbound_connectors_use_provider_auth(self) -> None:
        connector = ExternalApiConnectorService(self.auth)

        stripe_response = connector.send(
            OutboundRequest(provider="stripe", endpoint_key="payment_intents", payload={"amount": 2000, "currency": "usd"})
        )
        sendgrid_response = connector.send(
            OutboundRequest(provider="sendgrid", endpoint_key="mail_send", payload={"template_id": "tmpl_1"})
        )
        twilio_response = connector.send(
            OutboundRequest(provider="twilio", endpoint_key="messages", payload={"To": "+15551234567"}, account_sid="AC_CUSTOM")
        )

        self.assertEqual(stripe_response.status_code, 202)
        self.assertIn("Bearer sk_test_123", stripe_response.body["auth_headers"]["Authorization"])
        self.assertIn("Bearer sg_key_123", sendgrid_response.body["auth_headers"]["Authorization"])
        self.assertIn("Basic AC_CUSTOM:twilio_token_123", twilio_response.body["auth_headers"]["Authorization"])

    def test_webhook_receiver_verifies_signatures_and_deduplicates(self) -> None:
        receiver = WebhookReceiverService(self.auth)

        first = receiver.receive(
            InboundWebhook(
                provider="stripe",
                headers={"Stripe-Signature": "t=1,v1=abc"},
                payload={"id": "evt_1", "type": "payment_intent.succeeded"},
            )
        )
        duplicate = receiver.receive(
            InboundWebhook(
                provider="stripe",
                headers={"Stripe-Signature": "t=1,v1=abc"},
                payload={"id": "evt_1", "type": "payment_intent.succeeded"},
            )
        )

        self.assertEqual(first["accepted_events"], 1)
        self.assertEqual(duplicate["duplicate_events"], 1)

    def test_event_mapping_routes_to_webhook_sender(self) -> None:
        mapper = EventWebhookMapper()
        connector = ExternalApiConnectorService(self.auth)
        sender = WebhookSenderService(connector, mapper)

        responses = sender.send_for_event("notification.dispatched.v1", {"notification_id": "noti_1"})
        providers = sorted(response.provider for response in responses)

        self.assertEqual(providers, ["sendgrid", "twilio"])

    def test_webhook_subscription_and_delivery_no_gaps(self) -> None:
        subscriptions = WebhookSubscriptionService()
        subscriptions.subscribe("https://a.example.com/hooks", ["notification.dispatched.v1"])
        subscriptions.subscribe("https://b.example.com/hooks", ["notification.dispatched.v1", "notification.failed.v1"])

        deliveries = WebhookDeliveryService(subscriptions).deliver_event(
            "notification.dispatched.v1", {"notification_id": "noti_2"}
        )

        self.assertEqual(len(deliveries), 2)
        self.assertTrue(all(delivery.status == "delivered" for delivery in deliveries))

    def test_delivery_retry_and_dead_letter_after_max_attempts(self) -> None:
        subscriptions = WebhookSubscriptionService()
        sub = subscriptions.subscribe("https://retry.example.com/hooks", ["notification.failed.v1"], max_attempts=3)
        delivery_service = WebhookDeliveryService(subscriptions)

        [delivery] = delivery_service.deliver_event("notification.failed.v1", {"force_fail": True, "subscription": sub.subscription_id})
        self.assertEqual(delivery.status, "failed")

        retry_2 = delivery_service.retry_delivery(delivery.delivery_id)
        retry_3 = delivery_service.retry_delivery(delivery.delivery_id)

        self.assertEqual(retry_2.status, "failed")
        self.assertEqual(retry_3.status, "dead_lettered")
        self.assertEqual(retry_3.attempt_count, 3)

    def test_self_qc_returns_all_green(self) -> None:
        qc = run_self_qc()
        self.assertTrue(all(qc.values()), qc)


if __name__ == "__main__":
    unittest.main()
