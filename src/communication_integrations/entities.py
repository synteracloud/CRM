"""Communication integration entities aligned to docs/domain-model.md and integration contracts."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


SUPPORTED_PROVIDERS: tuple[str, ...] = ("sendgrid", "twilio")
SUPPORTED_CHANNELS: tuple[str, ...] = ("email", "sms", "whatsapp", "message")
SUPPORTED_ENTITY_TYPES: tuple[str, ...] = ("lead", "contact", "ticket")

THREAD_FIELDS: tuple[str, ...] = (
    "message_thread_id",
    "tenant_id",
    "channel_type",
    "provider",
    "provider_thread_key",
    "linked_entity_type",
    "linked_entity_id",
    "subject",
    "participants",
    "status",
    "created_at",
    "updated_at",
)

MESSAGE_FIELDS: tuple[str, ...] = (
    "message_id",
    "tenant_id",
    "message_thread_id",
    "provider",
    "provider_message_id",
    "channel_type",
    "direction",
    "sender",
    "recipient",
    "body",
    "status",
    "linked_entity_type",
    "linked_entity_id",
    "sent_at",
    "delivered_at",
)


@dataclass(frozen=True)
class LinkedEntityRef:
    entity_type: str
    entity_id: str


@dataclass(frozen=True)
class CommunicationThread:
    message_thread_id: str
    tenant_id: str
    channel_type: str
    provider: str
    provider_thread_key: str
    linked_entity_type: str
    linked_entity_id: str
    subject: str
    participants: tuple[str, ...]
    status: str
    created_at: str
    updated_at: str

    def patch(self, **changes: Any) -> "CommunicationThread":
        return replace(self, **changes)


@dataclass(frozen=True)
class CommunicationMessage:
    message_id: str
    tenant_id: str
    message_thread_id: str
    provider: str
    provider_message_id: str
    channel_type: str
    direction: str
    sender: str
    recipient: str
    body: str
    status: str
    linked_entity_type: str
    linked_entity_id: str
    sent_at: str
    delivered_at: str | None = None


class CommunicationContractError(ValueError):
    """Raised when communication integration contracts are violated."""


class CommunicationNotFoundError(KeyError):
    """Raised when threads or messages cannot be found."""
