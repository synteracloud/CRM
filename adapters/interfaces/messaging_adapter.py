"""Canonical MessagingAdapter contracts consumed by country-agnostic services."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from .types import AdapterContext


class MessageDeliveryStatus(str, Enum):
    RECEIVED = "received"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


@dataclass(frozen=True)
class MessageSendInput:
    message_id: str
    to: str
    channel: str
    body: str
    media_urls: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateSendInput:
    message_id: str
    to: str
    template_id: str
    params: dict[str, Any]
    locale: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MessageStatusInput:
    provider_message_id: str


@dataclass(frozen=True)
class MessageSendResult:
    message_id: str
    provider_message_id: str
    status: MessageDeliveryStatus
    accepted_at: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MessageStatusResult:
    provider_message_id: str
    status: MessageDeliveryStatus
    last_updated_at: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MessageWebhookEvent:
    event_id: str
    provider_message_id: str
    status: MessageDeliveryStatus
    occurred_at: str
    reason: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class InboundMessage:
    event_id: str
    provider_message_id: str
    from_number: str
    to_number: str
    text: str
    occurred_at: str
    profile_name: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RawWebhookInput:
    headers: dict[str, str]
    body: dict[str, Any]


class MessagingAdapter(Protocol):
    def send_message(self, input: MessageSendInput, ctx: AdapterContext) -> MessageSendResult: ...

    def send_template(self, input: TemplateSendInput, ctx: AdapterContext) -> MessageSendResult: ...

    def get_message_status(self, input: MessageStatusInput, ctx: AdapterContext) -> MessageStatusResult: ...

    def parse_webhook(self, input: RawWebhookInput, ctx: AdapterContext) -> list[MessageWebhookEvent]: ...

    def parse_inbound(self, input: RawWebhookInput, ctx: AdapterContext) -> list[InboundMessage]: ...
