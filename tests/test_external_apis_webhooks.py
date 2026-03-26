from __future__ import annotations

import unittest

from src.external_apis_webhooks import (
    API_ENDPOINTS,
    PUBLIC_API_ENDPOINTS,
    EventWebhookMapper,
    ExternalApiConnectorService,
    ExternalDeveloperAuthService,
    InboundWebhook,
    IntegrationAuth,
    PublicApiExposureService,
    PublicApiLayer,
    PublicApiSdk,
    PublicApiSdkConfig,
    OutboundRequest,
    SecretStore,
    WebhookReceiverService,
    WebhookSenderService,
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

    def test_self_qc_returns_all_green(self) -> None:
        qc = run_self_qc()
        self.assertTrue(all(qc.values()), qc)


    def test_public_api_requires_valid_bearer_token_and_scope(self) -> None:
        public_api = PublicApiLayer(auth=ExternalDeveloperAuthService(), exposure=PublicApiExposureService())

        create = public_api.create_developer_application(
            {
                "developer_id": "dev_1",
                "app_name": "partner_portal",
                "scopes": ["integrations:read"],
                "created_at": "2026-03-26T12:00:00Z",
            },
            request_id="req_public_1",
        )
        self.assertIn("client_id", create["data"])

        unauthorized = public_api.list_public_integrations(authorization_header=None, request_id="req_public_2")
        self.assertEqual(unauthorized["error"]["code"], "unauthorized")

        token_response = public_api.issue_access_token(
            {
                "client_id": create["data"]["client_id"],
                "client_secret": create["data"]["client_secret"],
                "scopes": ["integrations:read"],
            },
            request_id="req_public_3",
        )
        access_token = token_response["data"]["access_token"]

        authorized = public_api.list_public_integrations(authorization_header=f"Bearer {access_token}", request_id="req_public_4")
        self.assertIn("items", authorized["data"])
        self.assertGreaterEqual(len(authorized["data"]["items"]), 1)

    def test_sdk_scaffold_generates_standardized_requests(self) -> None:
        sdk = PublicApiSdk(PublicApiSdkConfig(base_url="https://public.crm.example", client_id="cid_1", client_secret="sec_1"))

        token_req = sdk.token_request(("integrations:read",))
        self.assertEqual(token_req["method"], "POST")
        self.assertTrue(token_req["url"].endswith(PUBLIC_API_ENDPOINTS["issue_access_token"]["path"]))
        self.assertEqual(token_req["headers"]["Accept"], "application/json")

        integrations_req = sdk.integrations_request(access_token="pat_example", page=1, page_size=25)
        self.assertEqual(integrations_req["method"], "GET")
        self.assertEqual(integrations_req["params"]["page_size"], 25)
        self.assertIn("Bearer pat_example", integrations_req["headers"]["Authorization"])


if __name__ == "__main__":
    unittest.main()
