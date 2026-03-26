"""Service layer for outbound connector calls and inbound webhook processing."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .auth import IntegrationAuth, IntegrationAuthError
from .entities import ALLOWED_PROVIDERS, INBOUND_WEBHOOK_ENDPOINTS, OUTBOUND_API_CONTRACTS, InboundWebhook, OutboundRequest, OutboundResponse
from .mapping import EventWebhookMapper, OutboundWebhookEvent


class IntegrationContractError(ValueError):
    """Raised when connector/webhook behavior violates contract definitions."""


class ExternalApiConnectorService:
    def __init__(self, auth: IntegrationAuth) -> None:
        self._auth = auth

    def send(self, request: OutboundRequest) -> OutboundResponse:
        if request.provider not in ALLOWED_PROVIDERS:
            raise IntegrationContractError(f"Provider not allowed: {request.provider}")

        provider_contract = OUTBOUND_API_CONTRACTS[request.provider]
        endpoint = provider_contract["endpoints"].get(request.endpoint_key)
        if not endpoint:
            raise IntegrationContractError(f"Undefined endpoint for provider={request.provider}: {request.endpoint_key}")

        headers = self._auth.outbound_headers(request.provider, account_sid=request.account_sid)
        if "Authorization" not in headers:
            raise IntegrationAuthError(f"Missing authorization for provider={request.provider}")

        # Network I/O is intentionally abstracted; response below mirrors expected contract shape.
        return OutboundResponse(provider=request.provider, status_code=202, body={"request": asdict(request), "auth_headers": headers})


class WebhookReceiverService:
    def __init__(self, auth: IntegrationAuth) -> None:
        self._auth = auth
        self._processed_ids: set[str] = set()

    def receive(self, webhook: InboundWebhook) -> dict[str, Any]:
        if webhook.provider not in INBOUND_WEBHOOK_ENDPOINTS:
            raise IntegrationContractError(f"Unknown inbound provider: {webhook.provider}")

        if not self._auth.verify_webhook_signature(webhook.provider, webhook.headers):
            raise IntegrationAuthError(f"Invalid {webhook.provider} webhook signature")

        event_ids = self._extract_event_ids(webhook)
        accepted = 0
        duplicate = 0

        for event_id in event_ids:
            if event_id in self._processed_ids:
                duplicate += 1
                continue
            self._processed_ids.add(event_id)
            accepted += 1

        return {
            "provider": webhook.provider,
            "accepted_events": accepted,
            "duplicate_events": duplicate,
            "acknowledged": True,
        }

    @staticmethod
    def _extract_event_ids(webhook: InboundWebhook) -> list[str]:
        payload = webhook.payload
        if webhook.provider == "stripe":
            if not isinstance(payload, dict) or "id" not in payload:
                raise IntegrationContractError("Stripe webhook payload must include id")
            return [str(payload["id"])]

        if webhook.provider == "sendgrid":
            if not isinstance(payload, list):
                raise IntegrationContractError("SendGrid webhook payload must be an array")
            ids = [str(item.get("sg_event_id", "")) for item in payload if isinstance(item, dict)]
            if any(not event_id for event_id in ids):
                raise IntegrationContractError("SendGrid events must include sg_event_id")
            return ids

        if webhook.provider == "twilio":
            if not isinstance(payload, dict) or "MessageSid" not in payload or "MessageStatus" not in payload:
                raise IntegrationContractError("Twilio status payload must include MessageSid and MessageStatus")
            return [f"{payload['MessageSid']}::{payload['MessageStatus']}"]

        raise IntegrationContractError(f"Unsupported provider: {webhook.provider}")


class WebhookSenderService:
    def __init__(self, connector: ExternalApiConnectorService, mapper: EventWebhookMapper) -> None:
        self._connector = connector
        self._mapper = mapper

    def send_for_event(self, event_name: str, payload: dict[str, Any]) -> list[OutboundResponse]:
        mapped_events = self._mapper.map_event(event_name, payload)
        return [self._send_one(mapped) for mapped in mapped_events]

    def _send_one(self, mapped: OutboundWebhookEvent) -> OutboundResponse:
        if mapped.provider == "stripe":
            return self._connector.send(OutboundRequest(provider="stripe", endpoint_key="payment_intents", payload=mapped.payload))
        if mapped.provider == "sendgrid":
            return self._connector.send(OutboundRequest(provider="sendgrid", endpoint_key="mail_send", payload=mapped.payload))
        if mapped.provider == "twilio":
            return self._connector.send(
                OutboundRequest(provider="twilio", endpoint_key="messages", payload=mapped.payload, account_sid="integration-account")
            )
        raise IntegrationContractError(f"Unsupported mapped provider: {mapped.provider}")
