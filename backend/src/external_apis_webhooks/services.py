"""Service layer for outbound connector calls and inbound webhook processing."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any
from uuid import uuid4

from src.event_bus.catalog_events import EVENT_NAME_SET

from .auth import IntegrationAuth, IntegrationAuthError
from .entities import (
    ALLOWED_PROVIDERS,
    INBOUND_WEBHOOK_ENDPOINTS,
    OUTBOUND_API_CONTRACTS,
    InboundWebhook,
    OutboundRequest,
    OutboundResponse,
    WebhookDelivery,
    WebhookSubscription,
)
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


class WebhookSubscriptionService:
    """Manages outbound webhook subscribers for internal CRM events."""

    def __init__(self) -> None:
        self._subscriptions: dict[str, WebhookSubscription] = {}

    def subscribe(self, target_url: str, event_names: list[str], max_attempts: int = 10) -> WebhookSubscription:
        if not target_url.startswith("https://"):
            raise IntegrationContractError("Webhook subscription target_url must use https")

        unknown = sorted(set(event_names) - EVENT_NAME_SET)
        if unknown:
            raise IntegrationContractError(f"Unknown event(s) in subscription: {', '.join(unknown)}")

        subscription = WebhookSubscription(
            subscription_id=f"whsub_{uuid4().hex[:12]}",
            target_url=target_url,
            event_names=tuple(dict.fromkeys(event_names)),
            max_attempts=max_attempts,
        )
        self._subscriptions[subscription.subscription_id] = subscription
        return subscription

    def list_subscriptions(self) -> list[WebhookSubscription]:
        return list(self._subscriptions.values())

    def subscriptions_for_event(self, event_name: str) -> list[WebhookSubscription]:
        if event_name not in EVENT_NAME_SET:
            raise IntegrationContractError(f"Unknown event for delivery: {event_name}")

        return [
            sub for sub in self._subscriptions.values() if sub.is_active and event_name in sub.event_names
        ]


class WebhookDeliveryService:
    """Delivers internal events to external webhook subscriptions with retry/failure handling."""

    def __init__(self, subscription_service: WebhookSubscriptionService) -> None:
        self._subscription_service = subscription_service
        self._deliveries: dict[str, WebhookDelivery] = {}

    def deliver_event(self, event_name: str, payload: dict[str, Any]) -> list[WebhookDelivery]:
        deliveries: list[WebhookDelivery] = []
        for subscription in self._subscription_service.subscriptions_for_event(event_name):
            delivery = WebhookDelivery(
                delivery_id=f"whdel_{uuid4().hex[:12]}",
                subscription_id=subscription.subscription_id,
                event_name=event_name,
                target_url=subscription.target_url,
                payload=payload,
                max_attempts=subscription.max_attempts,
            )
            self._deliveries[delivery.delivery_id] = delivery
            deliveries.append(self._attempt_delivery(delivery.delivery_id))
        return deliveries

    def retry_delivery(self, delivery_id: str) -> WebhookDelivery:
        delivery = self._deliveries.get(delivery_id)
        if not delivery:
            raise IntegrationContractError(f"Unknown delivery id: {delivery_id}")
        if delivery.status in {"delivered", "dead_lettered"}:
            return delivery
        return self._attempt_delivery(delivery_id)

    def get_delivery(self, delivery_id: str) -> WebhookDelivery:
        delivery = self._deliveries.get(delivery_id)
        if not delivery:
            raise IntegrationContractError(f"Unknown delivery id: {delivery_id}")
        return delivery

    def _attempt_delivery(self, delivery_id: str) -> WebhookDelivery:
        delivery = self._deliveries[delivery_id]
        attempt = delivery.attempt_count + 1
        should_fail = self._should_fail_delivery(delivery.payload, attempt)

        if should_fail and attempt >= delivery.max_attempts:
            updated = WebhookDelivery(
                **{**asdict(delivery), "attempt_count": attempt, "status": "dead_lettered", "last_error": "delivery failed after max retries"}
            )
        elif should_fail:
            updated = WebhookDelivery(
                **{**asdict(delivery), "attempt_count": attempt, "status": "failed", "last_error": f"attempt {attempt} failed"}
            )
        else:
            updated = WebhookDelivery(
                **{**asdict(delivery), "attempt_count": attempt, "status": "delivered", "last_error": None}
            )

        self._deliveries[delivery_id] = updated
        return updated

    @staticmethod
    def _should_fail_delivery(payload: dict[str, Any], attempt: int) -> bool:
        force_fail = payload.get("force_fail")
        force_fail_attempts = payload.get("force_fail_attempts")

        if force_fail is True:
            return True
        if isinstance(force_fail_attempts, int) and attempt <= force_fail_attempts:
            return True
        return False


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
