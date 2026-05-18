"""Pakistan WhatsApp adapter via 360dialog Cloud API.

Webhook contract: POST /webhooks/whatsapp/360dialog
Auth header: D360-API-KEY
Dedup key: messages[].id

Docs: docs/integration-contracts.md WhatsApp Provider Contracts (360dialog)
      docs/pakistan-adapter-architecture.md §3.A
"""

from __future__ import annotations

import hashlib
import hmac
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
    "deleted": MessageDeliveryStatus.FAILED,
}


class Dialog360Adapter:
    """Implements MessagingAdapter via 360dialog WhatsApp Business API."""

    provider = "360dialog"

    def __init__(self, api_key: str, webhook_secret: str | None = None) -> None:
        self._api_key = api_key
        self._webhook_secret = (webhook_secret or "").encode("utf-8")

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
        # Stub: real impl posts to https://waba.360dialog.io/v1/messages
        return MessageSendResult(
            message_id=input.message_id,
            provider_message_id=f"360d.{uuid4().hex}",
            status=MessageDeliveryStatus.SENT,
            accepted_at=utcnow_iso(),
            raw={"provider": self.provider, "trace_id": ctx.trace_id},
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
        # Stub: real impl posts to https://waba.360dialog.io/v1/messages with type=template
        return MessageSendResult(
            message_id=input.message_id,
            provider_message_id=f"360d.{uuid4().hex}",
            status=MessageDeliveryStatus.SENT,
            accepted_at=utcnow_iso(),
            raw={"template": input.template_id, "trace_id": ctx.trace_id},
        )

    def get_message_status(self, input: MessageStatusInput, ctx: AdapterContext) -> MessageStatusResult:
        # Stub: real impl calls GET https://waba.360dialog.io/v1/messages/{id}
        return MessageStatusResult(
            provider_message_id=input.provider_message_id,
            status=MessageDeliveryStatus.DELIVERED,
            last_updated_at=utcnow_iso(),
            raw={"provider": self.provider},
        )

    # ------------------------------------------------------------------ webhook

    def parse_webhook(self, input: RawWebhookInput, ctx: AdapterContext) -> list[MessageWebhookEvent]:
        self._verify_signature(input, ctx)
        events: list[MessageWebhookEvent] = []
        for msg in input.body.get("statuses", []):
            status_str = str(msg.get("status", "failed")).lower()
            events.append(
                MessageWebhookEvent(
                    event_id=str(msg.get("id") or uuid4()),
                    provider_message_id=str(msg.get("id") or ""),
                    status=_STATUS_MAP.get(status_str, MessageDeliveryStatus.FAILED),
                    occurred_at=str(msg.get("timestamp") or utcnow_iso()),
                    reason=msg.get("errors", [{}])[0].get("title") if msg.get("errors") else None,
                    raw=msg,
                )
            )
        return events

    def parse_inbound(self, input: RawWebhookInput, ctx: AdapterContext) -> list[InboundMessage]:
        self._verify_signature(input, ctx)
        inbound: list[InboundMessage] = []
        for msg in input.body.get("messages", []):
            inbound.append(
                InboundMessage(
                    event_id=str(msg.get("id") or uuid4()),
                    provider_message_id=str(msg.get("id") or uuid4()),
                    from_number=str(msg.get("from", "")),
                    to_number=str(input.body.get("to", "")),
                    text=str(msg.get("text", {}).get("body", "") if msg.get("type") == "text" else ""),
                    occurred_at=str(msg.get("timestamp") or utcnow_iso()),
                    profile_name=input.body.get("contacts", [{}])[0].get("profile", {}).get("name"),
                    raw=msg,
                )
            )
        return inbound

    # ------------------------------------------------------------------ private

    def _verify_signature(self, input: RawWebhookInput, ctx: AdapterContext) -> None:
        if not self._webhook_secret:
            return  # signature verification disabled (dev/test)
        provided = input.headers.get("d360-signature", "")
        expected = hmac.new(
            self._webhook_secret,
            str(input.body).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(provided, expected):
            raise AdapterError(
                code=AdapterErrorCode.AUTH_ERROR,
                message="Invalid 360dialog webhook signature.",
                retryable=False,
                provider=self.provider,
                provider_code="BAD_SIGNATURE",
                correlation_id=ctx.trace_id,
            )
