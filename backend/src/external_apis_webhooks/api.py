"""API-like surface describing external connector and webhook endpoints."""

from __future__ import annotations

from typing import Any

from .entities import INBOUND_WEBHOOK_ENDPOINTS, InboundWebhook
from .services import ExternalApiConnectorService, WebhookReceiverService, WebhookSenderService

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "send_stripe_api": {"method": "POST", "path": "/api/v1/integrations/stripe/requests"},
    "send_sendgrid_api": {"method": "POST", "path": "/api/v1/integrations/sendgrid/requests"},
    "send_twilio_api": {"method": "POST", "path": "/api/v1/integrations/twilio/requests"},
    "receive_stripe_webhook": INBOUND_WEBHOOK_ENDPOINTS["stripe"],
    "receive_sendgrid_webhook": INBOUND_WEBHOOK_ENDPOINTS["sendgrid"],
    "receive_twilio_webhook": INBOUND_WEBHOOK_ENDPOINTS["twilio"],
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": details or []},
        "meta": {"request_id": request_id},
    }


class ExternalIntegrationsApi:
    def __init__(
        self,
        connector_service: ExternalApiConnectorService,
        webhook_receiver: WebhookReceiverService,
        webhook_sender: WebhookSenderService,
    ) -> None:
        self._connector_service = connector_service
        self._webhook_receiver = webhook_receiver
        self._webhook_sender = webhook_sender

    def receive_webhook(self, webhook: InboundWebhook, request_id: str) -> dict[str, Any]:
        try:
            return success(self._webhook_receiver.receive(webhook), request_id)
        except ValueError as exc:
            return error("bad_request", str(exc), request_id)

    def send_webhooks_for_event(self, event_name: str, payload: dict[str, Any], request_id: str) -> dict[str, Any]:
        try:
            responses = self._webhook_sender.send_for_event(event_name, payload)
            return success(
                [
                    {
                        "provider": response.provider,
                        "status_code": response.status_code,
                        "body": response.body,
                    }
                    for response in responses
                ],
                request_id,
            )
        except ValueError as exc:
            return error("validation_error", str(exc), request_id)
