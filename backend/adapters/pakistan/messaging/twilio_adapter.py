"""Optional Twilio adapter stub for Pakistan WhatsApp transport."""

from __future__ import annotations

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
from adapters.interfaces.types import AdapterContext, AdapterError, AdapterErrorCode


class TwilioWhatsAppAdapterStub:
    provider = "twilio"

    def send_message(self, input: MessageSendInput, ctx: AdapterContext) -> MessageSendResult:
        raise AdapterError(
            code=AdapterErrorCode.PROVIDER_UNAVAILABLE,
            message="Twilio WhatsApp adapter is a stub and not enabled.",
            retryable=True,
            provider=self.provider,
        )

    def send_template(self, input: TemplateSendInput, ctx: AdapterContext) -> MessageSendResult:
        raise AdapterError(
            code=AdapterErrorCode.PROVIDER_UNAVAILABLE,
            message="Twilio template send is not implemented.",
            retryable=True,
            provider=self.provider,
        )

    def get_message_status(self, input: MessageStatusInput, ctx: AdapterContext) -> MessageStatusResult:
        raise AdapterError(
            code=AdapterErrorCode.PROVIDER_UNAVAILABLE,
            message="Twilio status retrieval is not implemented.",
            retryable=True,
            provider=self.provider,
        )

    def parse_webhook(self, input: RawWebhookInput, ctx: AdapterContext) -> list[MessageWebhookEvent]:
        return []

    def parse_inbound(self, input: RawWebhookInput, ctx: AdapterContext) -> list[InboundMessage]:
        return []
