"""Entities for conversational CRM operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ChatMessage:
    message_id: str
    tenant_id: str
    conversation_id: str
    contact_id: str
    direction: str
    text: str
    occurred_at: str


@dataclass(frozen=True)
class ConversationContext:
    tenant_id: str
    conversation_id: str
    contact_id: str
    lead_id: str


@dataclass(frozen=True)
class CommandIntent:
    name: str
    confidence: float
    entities: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CommandParseResult:
    intents: tuple[CommandIntent, ...]
    unmatched_text: str = ""


@dataclass(frozen=True)
class ConversationActivityEvent:
    event_id: str
    tenant_id: str
    conversation_id: str
    lead_id: str
    message_id: str
    activity_type: str
    payload: dict[str, Any]
    occurred_at: str


@dataclass(frozen=True)
class ChatActionResult:
    action: str
    lead_id: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)
