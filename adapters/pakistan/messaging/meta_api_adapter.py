"""Pakistan WhatsApp adapter via Meta Cloud API semantics."""

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


class MetaWhatsAppAdapter:
    provider = "meta"

    def send_message(self, input: MessageSendInput, ctx: AdapterContext) -> MessageSendResult:
        if not input.to.startswith("+"):
            raise AdapterError(
                code=AdapterErrorCode.INVALID_RECIPIENT,
                message="Recipient number must be E.164 formatted.",
                retryable=False,
                provider=self.provider,
            )
        return MessageSendResult(
            message_id=input.message_id,
            provider_message_id=f"wamid.{uuid4()}",
            status=MessageDeliveryStatus.SENT,
            accepted_at=utcnow_iso(),
            raw={"trace_id": ctx.trace_id},
        )

    def send_template(self, input: TemplateSendInput, ctx: AdapterContext) -> MessageSendResult:
        if not input.template_id:
            raise AdapterError(
                code=AdapterErrorCode.TEMPLATE_REJECTED,
                message="Template id is required.",
                retryable=False,
                provider=self.provider,
            )
        return MessageSendResult(
            message_id=input.message_id,
            provider_message_id=f"wamid.{uuid4()}",
            status=MessageDeliveryStatus.SENT,
            accepted_at=utcnow_iso(),
            raw={"template": input.template_id, "trace_id": ctx.trace_id},
        )

    def get_message_status(self, input: MessageStatusInput, ctx: AdapterContext) -> MessageStatusResult:
        return MessageStatusResult(
            provider_message_id=input.provider_message_id,
            status=MessageDeliveryStatus.DELIVERED,
            last_updated_at=utcnow_iso(),
            raw={"trace_id": ctx.trace_id},
        )

    def parse_webhook(self, input: RawWebhookInput, ctx: AdapterContext) -> list[MessageWebhookEvent]:
        statuses = input.body.get("statuses", [])
        events: list[MessageWebhookEvent] = []
        for row in statuses:
            status_value = str(row.get("status", "failed")).lower()
            mapped = {
                "sent": MessageDeliveryStatus.SENT,
                "delivered": MessageDeliveryStatus.DELIVERED,
                "read": MessageDeliveryStatus.READ,
                "failed": MessageDeliveryStatus.FAILED,
            }.get(status_value, MessageDeliveryStatus.FAILED)
            events.append(
                MessageWebhookEvent(
                    event_id=str(row.get("id") or uuid4()),
                    provider_message_id=str(row.get("message_id", "")),
                    status=mapped,
                    occurred_at=str(row.get("timestamp") or utcnow_iso()),
                    reason=row.get("errors", [{}])[0].get("code") if row.get("errors") else None,
                    raw=row,
                )
            )
        return events

    def parse_inbound(self, input: RawWebhookInput, ctx: AdapterContext) -> list[InboundMessage]:
        messages = input.body.get("messages", [])
        inbound: list[InboundMessage] = []
        for row in messages:
            inbound.append(
                InboundMessage(
                    event_id=str(row.get("id") or uuid4()),
                    provider_message_id=str(row.get("id") or uuid4()),
                    from_number=str(row.get("from", "")),
                    to_number=str(input.body.get("metadata", {}).get("display_phone_number", "")),
                    text=str(row.get("text", {}).get("body", "")),
                    occurred_at=str(row.get("timestamp") or utcnow_iso()),
                    profile_name=input.body.get("contacts", [{}])[0].get("profile", {}).get("name"),
                    raw=row,
                )
            )
        return inbound
