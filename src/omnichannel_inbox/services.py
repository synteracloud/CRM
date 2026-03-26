"""Routing and inbox service for unified omnichannel message handling."""

from __future__ import annotations

from collections.abc import Mapping

from .entities import Message, MessageThread, RoutingDecision, ThreadNotFoundError, ThreadStateError


class OmnichannelInboxService:
    """In-memory inbox service with deduped threads and deterministic routing."""

    def __init__(self) -> None:
        self._threads: dict[str, MessageThread] = {}
        self._messages_by_thread: dict[str, list[Message]] = {}
        self._thread_keys: dict[str, str] = {}
        self._routing: dict[str, RoutingDecision] = {}

    def list_threads(self) -> list[MessageThread]:
        return list(self._threads.values())

    def get_thread(self, message_thread_id: str) -> MessageThread:
        thread = self._threads.get(message_thread_id)
        if not thread:
            raise ThreadNotFoundError(f"Thread not found: {message_thread_id}")
        return thread

    def list_messages(self, message_thread_id: str) -> list[Message]:
        self.get_thread(message_thread_id)
        return list(self._messages_by_thread.get(message_thread_id, []))

    def upsert_thread(
        self,
        thread: MessageThread,
        *,
        dedupe_key: str | None = None,
    ) -> MessageThread:
        key = self._build_dedupe_key(thread, dedupe_key)
        existing_thread_id = self._thread_keys.get(key)
        if existing_thread_id:
            return self._threads[existing_thread_id]
        if thread.message_thread_id in self._threads:
            raise ThreadStateError(f"Thread already exists: {thread.message_thread_id}")

        self._threads[thread.message_thread_id] = thread
        self._messages_by_thread.setdefault(thread.message_thread_id, [])
        self._thread_keys[key] = thread.message_thread_id
        return thread

    def ingest_message(
        self,
        message: Message,
        *,
        customer_account_id: str | None = None,
        customer_contact_id: str | None = None,
    ) -> Message:
        thread = self.get_thread(message.message_thread_id)
        if thread.tenant_id != message.tenant_id:
            raise ThreadStateError("Message tenant_id must match thread tenant_id.")
        if customer_account_id and thread.account_id and customer_account_id != thread.account_id:
            raise ThreadStateError("Message is linked to a different account than its thread.")
        if customer_contact_id and thread.contact_id and customer_contact_id != thread.contact_id:
            raise ThreadStateError("Message is linked to a different contact than its thread.")

        messages = self._messages_by_thread.setdefault(message.message_thread_id, [])
        if any(item.message_id == message.message_id for item in messages):
            raise ThreadStateError(f"Message already exists: {message.message_id}")

        messages.append(message)
        return message

    def route_thread(
        self,
        message_thread_id: str,
        *,
        assigned_at: str,
        contact_owner_map: Mapping[str, str] | None = None,
        channel_team_map: Mapping[str, str] | None = None,
        keyword_team_map: Mapping[str, str] | None = None,
        force_reassign: bool = False,
    ) -> RoutingDecision:
        if not force_reassign and message_thread_id in self._routing:
            return self._routing[message_thread_id]

        thread = self.get_thread(message_thread_id)
        subject_text = thread.subject.lower()

        contact_owner_map = contact_owner_map or {}
        channel_team_map = channel_team_map or {
            "email": "team-email-support",
            "chat": "team-live-chat",
            "message": "team-sms-support",
        }
        keyword_team_map = keyword_team_map or {
            "billing": "team-billing",
            "invoice": "team-billing",
            "refund": "team-billing",
            "bug": "team-technical-support",
            "outage": "team-technical-support",
        }

        assigned_user_id: str | None = None
        assigned_team_id: str | None = None
        rule_code = "channel_default"

        if thread.contact_id and thread.contact_id in contact_owner_map:
            assigned_user_id = contact_owner_map[thread.contact_id]
            rule_code = "contact_owner"
        else:
            for keyword, team_id in keyword_team_map.items():
                if keyword in subject_text:
                    assigned_team_id = team_id
                    rule_code = "subject_keyword"
                    break

            if not assigned_team_id:
                assigned_team_id = channel_team_map.get(thread.channel_type, "team-general")

        decision = RoutingDecision(
            tenant_id=thread.tenant_id,
            message_thread_id=message_thread_id,
            assigned_user_id=assigned_user_id,
            assigned_team_id=assigned_team_id,
            rule_code=rule_code,
            assigned_at=assigned_at,
        )
        self._routing[message_thread_id] = decision
        return decision

    def get_routing(self, message_thread_id: str) -> RoutingDecision:
        if message_thread_id not in self._routing:
            raise ThreadNotFoundError(f"No routing decision found for thread: {message_thread_id}")
        return self._routing[message_thread_id]

    @staticmethod
    def _build_dedupe_key(thread: MessageThread, override: str | None) -> str:
        if override:
            return f"{thread.tenant_id}:{override.strip().lower()}"

        normalized_subject = " ".join(thread.subject.lower().split())
        return (
            f"{thread.tenant_id}:{thread.channel_type}:{thread.account_id or '-'}:"
            f"{thread.contact_id or '-'}:{normalized_subject}"
        )
