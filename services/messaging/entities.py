"""Conversation and message entities for WhatsApp-first execution runtime."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any


class ConversationState(str, Enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    WAITING_ON_CONTACT = "WAITING_ON_CONTACT"
    WAITING_ON_INTERNAL = "WAITING_ON_INTERNAL"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"


class MessageDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


@dataclass(frozen=True)
class Contact:
    contact_id: str
    tenant_id: str
    normalized_phone: str
    profile_name: str | None = None
    locale: str | None = None
    opt_in_whatsapp: bool = True
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Conversation:
    conversation_id: str
    tenant_id: str
    channel: str
    normalized_phone: str
    contact_id: str
    state: ConversationState
    business_context: str = "general"
    last_inbound_at: str | None = None
    last_outbound_at: str | None = None

    def patch(self, **changes: Any) -> "Conversation":
        return replace(self, **changes)


@dataclass(frozen=True)
class MessageRecord:
    message_id: str
    tenant_id: str
    conversation_id: str
    contact_id: str
    direction: MessageDirection
    provider: str
    provider_message_id: str
    text: str
    intent: str
    status: str
    payload_hash: str
    timestamp: str
    error_code: str | None = None
    retry_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MessageEvent:
    event_id: str
    tenant_id: str
    message_id: str
    conversation_id: str
    contact_id: str
    event_type: str
    status: str
    occurred_at: str
    provider: str
    provider_message_id: str
    payload_hash: str
    error_code: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
