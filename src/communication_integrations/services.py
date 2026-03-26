"""Services for email/SMS/WhatsApp communication integrations."""

from __future__ import annotations

from dataclasses import replace

from .entities import (
    CommunicationContractError,
    CommunicationMessage,
    CommunicationNotFoundError,
    CommunicationThread,
    LinkedEntityRef,
    SUPPORTED_CHANNELS,
    SUPPORTED_ENTITY_TYPES,
    SUPPORTED_PROVIDERS,
)


class CommunicationIntegrationService:
    """In-memory integration service enforcing contract-safe communication handling."""

    def __init__(self) -> None:
        self._threads: dict[str, CommunicationThread] = {}
        self._messages_by_thread: dict[str, list[CommunicationMessage]] = {}
        self._thread_by_dedupe_key: dict[str, str] = {}
        self._message_by_provider_id: dict[tuple[str, str, str], str] = {}
        self._valid_entities: dict[str, dict[str, set[str]]] = {}

    def register_valid_entities(
        self,
        *,
        tenant_id: str,
        lead_ids: set[str] | None = None,
        contact_ids: set[str] | None = None,
        ticket_ids: set[str] | None = None,
    ) -> None:
        self._valid_entities[tenant_id] = {
            "lead": set(lead_ids or set()),
            "contact": set(contact_ids or set()),
            "ticket": set(ticket_ids or set()),
        }

    def create_or_get_thread(self, thread: CommunicationThread) -> CommunicationThread:
        self._validate_provider_channel(provider=thread.provider, channel_type=thread.channel_type)
        self._validate_linked_entity(
            tenant_id=thread.tenant_id,
            linked_entity=LinkedEntityRef(thread.linked_entity_type, thread.linked_entity_id),
        )

        dedupe_key = self._build_thread_dedupe_key(thread)
        existing_thread_id = self._thread_by_dedupe_key.get(dedupe_key)
        if existing_thread_id:
            return self._threads[existing_thread_id]

        if thread.message_thread_id in self._threads:
            raise CommunicationContractError(f"Thread already exists: {thread.message_thread_id}")

        self._threads[thread.message_thread_id] = thread
        self._messages_by_thread.setdefault(thread.message_thread_id, [])
        self._thread_by_dedupe_key[dedupe_key] = thread.message_thread_id
        return thread

    def send_email(
        self,
        *,
        message: CommunicationMessage,
        linked_entity: LinkedEntityRef,
    ) -> CommunicationMessage:
        return self._send_message(message=message, linked_entity=linked_entity, expected_channel="email")

    def send_sms(
        self,
        *,
        message: CommunicationMessage,
        linked_entity: LinkedEntityRef,
    ) -> CommunicationMessage:
        return self._send_message(message=message, linked_entity=linked_entity, expected_channel="sms")

    def send_whatsapp(
        self,
        *,
        message: CommunicationMessage,
        linked_entity: LinkedEntityRef,
    ) -> CommunicationMessage:
        return self._send_message(message=message, linked_entity=linked_entity, expected_channel="whatsapp")

    def receive_message(
        self,
        *,
        message: CommunicationMessage,
        linked_entity: LinkedEntityRef,
    ) -> CommunicationMessage:
        if message.direction != "inbound":
            raise CommunicationContractError("Inbound receive_message requires direction='inbound'.")
        self._validate_provider_channel(provider=message.provider, channel_type=message.channel_type)
        return self._store_message(message=message, linked_entity=linked_entity)

    def list_threads(self) -> list[CommunicationThread]:
        return list(self._threads.values())

    def list_messages(self, message_thread_id: str) -> list[CommunicationMessage]:
        self.get_thread(message_thread_id)
        return list(self._messages_by_thread.get(message_thread_id, []))

    def get_thread(self, message_thread_id: str) -> CommunicationThread:
        thread = self._threads.get(message_thread_id)
        if not thread:
            raise CommunicationNotFoundError(f"Thread not found: {message_thread_id}")
        return thread

    def _send_message(
        self,
        *,
        message: CommunicationMessage,
        linked_entity: LinkedEntityRef,
        expected_channel: str,
    ) -> CommunicationMessage:
        if message.direction != "outbound":
            raise CommunicationContractError("Outbound send methods require direction='outbound'.")
        if message.channel_type != expected_channel:
            raise CommunicationContractError(
                f"Channel mismatch: expected={expected_channel}, actual={message.channel_type}"
            )
        self._validate_provider_channel(provider=message.provider, channel_type=message.channel_type)
        return self._store_message(message=message, linked_entity=linked_entity)

    def _store_message(self, *, message: CommunicationMessage, linked_entity: LinkedEntityRef) -> CommunicationMessage:
        self._validate_linked_entity(tenant_id=message.tenant_id, linked_entity=linked_entity)

        thread = self.get_thread(message.message_thread_id)
        if thread.tenant_id != message.tenant_id:
            raise CommunicationContractError("Message tenant_id must match thread tenant_id.")
        if thread.provider != message.provider:
            raise CommunicationContractError("Message provider must match thread provider.")
        if thread.channel_type != message.channel_type:
            raise CommunicationContractError("Message channel_type must match thread channel_type.")

        if (
            thread.linked_entity_type != linked_entity.entity_type
            or thread.linked_entity_id != linked_entity.entity_id
            or message.linked_entity_type != linked_entity.entity_type
            or message.linked_entity_id != linked_entity.entity_id
        ):
            raise CommunicationContractError("Message linkage must match thread linkage and provided linked_entity.")

        provider_dedupe_key = (message.tenant_id, message.provider, message.provider_message_id)
        if provider_dedupe_key in self._message_by_provider_id:
            existing_message_id = self._message_by_provider_id[provider_dedupe_key]
            for existing in self._messages_by_thread.get(message.message_thread_id, []):
                if existing.message_id == existing_message_id:
                    return existing
            raise CommunicationContractError("Duplicate provider message id points to a different thread.")

        thread_messages = self._messages_by_thread.setdefault(message.message_thread_id, [])
        if any(item.message_id == message.message_id for item in thread_messages):
            raise CommunicationContractError(f"Message already exists: {message.message_id}")

        thread_messages.append(message)
        self._message_by_provider_id[provider_dedupe_key] = message.message_id

        if thread.updated_at < message.sent_at:
            self._threads[thread.message_thread_id] = replace(thread, updated_at=message.sent_at)

        return message

    @staticmethod
    def _build_thread_dedupe_key(thread: CommunicationThread) -> str:
        participants_key = ",".join(sorted(p.strip().lower() for p in thread.participants))
        return (
            f"{thread.tenant_id}:{thread.provider}:{thread.channel_type}:{thread.provider_thread_key.lower()}:"
            f"{thread.linked_entity_type}:{thread.linked_entity_id}:{participants_key}"
        )

    def _validate_linked_entity(self, *, tenant_id: str, linked_entity: LinkedEntityRef) -> None:
        if linked_entity.entity_type not in SUPPORTED_ENTITY_TYPES:
            raise CommunicationContractError(f"Unsupported entity_type={linked_entity.entity_type}")
        tenant_entities = self._valid_entities.get(tenant_id)
        if not tenant_entities:
            raise CommunicationContractError(
                f"No registered entities for tenant={tenant_id}; cannot create communications without linkage source."
            )
        if linked_entity.entity_id not in tenant_entities[linked_entity.entity_type]:
            raise CommunicationContractError(
                f"Invalid linkage for {linked_entity.entity_type}={linked_entity.entity_id} in tenant={tenant_id}"
            )

    @staticmethod
    def _validate_provider_channel(*, provider: str, channel_type: str) -> None:
        if provider not in SUPPORTED_PROVIDERS:
            raise CommunicationContractError(f"Unsupported provider={provider}.")
        if channel_type not in SUPPORTED_CHANNELS:
            raise CommunicationContractError(f"Unsupported channel_type={channel_type}.")
        if channel_type == "email" and provider != "sendgrid":
            raise CommunicationContractError("Email channel must use sendgrid provider.")
        if channel_type in {"sms", "whatsapp", "message"} and provider != "twilio":
            raise CommunicationContractError("SMS/WhatsApp/message channels must use twilio provider.")
