"""In-memory persistence and idempotency safeguards for WhatsApp execution."""

from __future__ import annotations

from collections import defaultdict

from .entities import Contact, Conversation, MessageEvent, MessageRecord


class MessagingRepository:
    def __init__(self) -> None:
        self.contacts: dict[tuple[str, str], Contact] = {}
        self.conversations: dict[str, Conversation] = {}
        self.conversation_keys: dict[tuple[str, str, str, str], str] = {}
        self.messages: dict[str, MessageRecord] = {}
        self.events: list[MessageEvent] = []
        self.timeline: dict[str, list[str]] = defaultdict(list)
        self.processed_inbound: set[str] = set()
        self.processed_status_events: set[str] = set()
        self.provider_index: dict[str, str] = {}

    def upsert_contact(self, contact: Contact) -> Contact:
        key = (contact.tenant_id, contact.normalized_phone)
        existing = self.contacts.get(key)
        if existing:
            merged = Contact(
                contact_id=existing.contact_id,
                tenant_id=existing.tenant_id,
                normalized_phone=existing.normalized_phone,
                profile_name=contact.profile_name or existing.profile_name,
                locale=contact.locale or existing.locale,
                opt_in_whatsapp=existing.opt_in_whatsapp and contact.opt_in_whatsapp,
                tags=tuple(sorted(set(existing.tags + contact.tags))),
            )
            self.contacts[key] = merged
            return merged
        self.contacts[key] = contact
        return contact

    def get_or_create_conversation(self, conversation: Conversation) -> Conversation:
        key = (
            conversation.tenant_id,
            conversation.channel,
            conversation.normalized_phone,
            conversation.business_context,
        )
        existing_id = self.conversation_keys.get(key)
        if existing_id:
            return self.conversations[existing_id]
        self.conversation_keys[key] = conversation.conversation_id
        self.conversations[conversation.conversation_id] = conversation
        return conversation

    def save_conversation(self, conversation: Conversation) -> None:
        self.conversations[conversation.conversation_id] = conversation

    def add_message(self, message: MessageRecord) -> MessageRecord:
        if message.message_id in self.messages:
            return self.messages[message.message_id]
        self.messages[message.message_id] = message
        self.provider_index[message.provider_message_id] = message.message_id
        self.timeline[message.conversation_id].append(message.message_id)
        return message

    def add_event(self, event: MessageEvent) -> None:
        self.events.append(event)

    def get_message_by_provider_id(self, provider_message_id: str) -> MessageRecord | None:
        message_id = self.provider_index.get(provider_message_id)
        return self.messages.get(message_id) if message_id else None

    def save_message(self, message: MessageRecord) -> None:
        self.messages[message.message_id] = message
