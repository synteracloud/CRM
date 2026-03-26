"""Omnichannel inbox entities aligned to docs/domain-model.md."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


THREAD_FIELDS: tuple[str, ...] = (
    "message_thread_id",
    "tenant_id",
    "account_id",
    "contact_id",
    "channel_type",
    "subject",
    "status",
    "created_at",
    "updated_at",
)

MESSAGE_FIELDS: tuple[str, ...] = (
    "message_id",
    "tenant_id",
    "message_thread_id",
    "direction",
    "provider_message_id",
    "sender",
    "recipient",
    "status",
    "sent_at",
    "delivered_at",
    "opened_at",
    "clicked_at",
)


@dataclass(frozen=True)
class MessageThread:
    message_thread_id: str
    tenant_id: str
    account_id: str | None
    contact_id: str | None
    channel_type: str
    subject: str
    status: str
    created_at: str
    updated_at: str

    def patch(self, **changes: Any) -> "MessageThread":
        return replace(self, **changes)


@dataclass(frozen=True)
class Message:
    message_id: str
    tenant_id: str
    message_thread_id: str
    direction: str
    provider_message_id: str
    sender: str
    recipient: str
    status: str
    sent_at: str
    delivered_at: str | None = None
    opened_at: str | None = None
    clicked_at: str | None = None


@dataclass(frozen=True)
class RoutingDecision:
    tenant_id: str
    message_thread_id: str
    assigned_user_id: str | None
    assigned_team_id: str | None
    rule_code: str
    assigned_at: str


class ThreadStateError(ValueError):
    """Raised when thread/message lifecycle or linkage is invalid."""


class ThreadNotFoundError(KeyError):
    """Raised when a thread cannot be found for a given message_thread_id."""
