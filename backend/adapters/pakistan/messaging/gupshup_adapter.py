"""Pakistan WhatsApp adapter via Gupshup Enterprise API.

Webhook contract: POST /webhooks/whatsapp/gupshup
Auth header: apikey
Dedup key: payload.id

Docs: docs/integration-contracts.md WhatsApp Provider Contracts (Gupshup)
      docs/pakistan-adapter-architecture.md §3.A
"""

from __future__ import annotations

from uuid import uuid4

from adapters.interfaces.messaging_adapter import (
    InboundMessage,
    MessageDeliveryStatus,
    MessageSendInput,
    MessageSendResult,
    MessageStatusInput,
    MessageStatusResult,
    MessageWebhookEvent,
    RawWebhookInput,
    TemplateSendInput,
)
from adapters.interfaces.types import AdapterContext, AdapterError, AdapterErrorCode, utcnow_iso

_STATUS_MAP: dict[str, MessageDeliveryStatus] = {
    "sent": MessageDeliveryStatus.SENT,
    "delivered": MessageDeliveryStatus.DELIVERED,
    "read": MessageDeliveryStatus.READ,
    "failed": MessageDeliveryStatus.FAILED,
    "enqueued": MessageDeliveryStatus.SENT,
}

_TYPE_MAP: dict[str, str] = {
    "text": "text",
    "image": "media",
    "document": "media",
    "audio": "media",
    "video": "media",
}


class GupshupAdapter:
    """Implements MessagingAdapter via Gupshup WhatsApp Enterprise API."""

    provider = "gupshup"

    def __init__(self, api_key: str, app_name: str, source_number: str) -> None:
        self._api_key = api_key
        self._app_name = app_name
        self._source = source_number  # E.164 sender number

    # ------------------------------------------------------------------ send

    def send_message(self, input: MessageSendInput, ctx: AdapterContext) -> MessageSendResult:
        if not input.to.startswith("+"):
            raise AdapterError(
                code=AdapterErrorCode.INVALID_RECIPIENT,
                message="Recipient must be E.164 formatted.",
                retryable=False,
                provider=self.provider,
                correlation_id=ctx.trace_id,
            )
        # Stub: real impl posts to https://api.gupshup.io/sm/api/v1/msg
        return MessageSendResult(
            message_id=input.message_id,
            provider_message_id=f"gs.{uuid4().hex}",
            status=MessageDeliveryStatus.SENT,
            accepted_at=utcnow_iso(),
            raw={"provider": self.provider, "app": self._app_name, "trace_id": ctx.trace_id},
        )

    def send_template(self, input: TemplateSendInput, ctx: AdapterContext) -> MessageSendResult:
        if not input.template_id:
            raise AdapterError(
                code=AdapterErrorCode.TEMPLATE_REJECTED,
                message="template_id is required.",
                retryable=False,
                provider=self.provider,
                correlation_id=ctx.trace_id,
            )
        # Stub: real impl posts to https://api.gupshup.io/sm/api/v1/template/msg
        return MessageSendResult(
            message_id=input.message_id,
            provider_message_id=f"gs.{uuid4().hex}",
            status=MessageDeliveryStatus.SENT,
            accepted_at=utcnow_iso(),
            raw={"template": input.template_id, "provider": self.provider},
        )

    def get_message_status(self, input: MessageStatusInput, ctx: AdapterContext) -> MessageStatusResult:
        # Stub: Gupshup does not expose a status poll endpoint; status comes via webhook only.
        return MessageStatusResult(
            provider_message_id=input.provider_message_id,
            status=MessageDeliveryStatus.SENT,
            last_updated_at=utcnow_iso(),
            raw={"note": "Gupshup status is webhook-only"},
        )

    # ------------------------------------------------------------------ webhook

    def parse_webhook(self, input: RawWebhookInput, ctx: AdapterContext) -> list[MessageWebhookEvent]:
        payload = input.body.get("payload", {})
        msg_type = str(input.body.get("type", "")).lower()

        if msg_type not in ("message-event", "message_event"):
            return []

        status_str = str(payload.get("type", "failed")).lower()
        return [
            MessageWebhookEvent(
                event_id=str(payload.get("id") or uuid4()),
                provider_message_id=str(payload.get("gsId") or payload.get("id") or ""),
                status=_STATUS_MAP.get(status_str, MessageDeliveryStatus.FAILED),
                occurred_at=str(input.body.get("timestamp") or utcnow_iso()),
                reason=payload.get("error"),
                raw=input.body,
            )
        ]

    def parse_inbound(self, input: RawWebhookInput, ctx: AdapterContext) -> list[InboundMessage]:
        msg_type = str(input.body.get("type", "")).lower()
        if msg_type != "message":
            return []

        payload = input.body.get("payload", {})
        sender = input.body.get("sender", {})

        text = ""
        if payload.get("type") == "text":
            text = str(payload.get("payload", {}).get("text", ""))

        phone = str(sender.get("phone", ""))
        if phone and not phone.startswith("+"):
            phone = f"+{phone}"

        return [
            InboundMessage(
                event_id=str(payload.get("id") or uuid4()),
                provider_message_id=str(payload.get("id") or uuid4()),
                from_number=phone,
                to_number=self._source,
                text=text,
                occurred_at=str(input.body.get("timestamp") or utcnow_iso()),
                profile_name=sender.get("name"),
                raw=input.body,
            )
        ]
