"""WhatsApp core engine orchestrating inbound/outbound and delivery life-cycle."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from uuid import uuid4

from adapters.interfaces.messaging_adapter import (
    InboundMessage,
    MessageDeliveryStatus,
    MessageSendInput,
    MessageWebhookEvent,
    MessagingAdapter,
    RawWebhookInput,
)
from adapters.interfaces.types import AdapterContext, AdapterError

from .entities import Contact, Conversation, ConversationState, MessageDirection, MessageEvent, MessageRecord
from .repository import MessagingRepository
from services.leads.service import WhatsAppLeadCaptureService


class WhatsAppCoreEngine:
    """Country-agnostic execution layer for message processing and timeline mapping."""

    def __init__(
        self,
        repository: MessagingRepository,
        adapter: MessagingAdapter,
        provider: str,
        lead_capture_service: WhatsAppLeadCaptureService | None = None,
    ) -> None:
        self._repository = repository
        self._adapter = adapter
        self._provider = provider
        self._lead_capture_service = lead_capture_service

    def handle_inbound_webhook(self, webhook: RawWebhookInput, ctx: AdapterContext) -> list[MessageRecord]:
        inbound = self._adapter.parse_inbound(webhook, ctx)
        persisted: list[MessageRecord] = []
        for item in inbound:
            if item.event_id in self._repository.processed_inbound:
                continue
            self._repository.processed_inbound.add(item.event_id)
            persisted.append(self._persist_inbound(item, ctx))
        return persisted

    def send_outbound_message(
        self,
        *,
        to: str,
        body: str,
        intent: str,
        ctx: AdapterContext,
        business_context: str = "general",
        max_retries: int = 3,
    ) -> MessageRecord:
        contact, conversation = self._resolve_contact_conversation(
            phone=to,
            profile_name=None,
            ctx=ctx,
            business_context=business_context,
        )
        message_id = str(uuid4())
        send_input = MessageSendInput(
            message_id=message_id,
            to=to,
            channel="whatsapp",
            body=body,
            metadata={"intent": intent, "conversation_id": conversation.conversation_id},
        )

        retry_count = 0
        while True:
            try:
                result = self._adapter.send_message(send_input, ctx)
                message = MessageRecord(
                    message_id=message_id,
                    tenant_id=ctx.tenant_id,
                    conversation_id=conversation.conversation_id,
                    contact_id=contact.contact_id,
                    direction=MessageDirection.OUTBOUND,
                    provider=self._provider,
                    provider_message_id=result.provider_message_id,
                    text=body,
                    intent=intent,
                    status=result.status.value,
                    payload_hash=self._hash_payload(body, to),
                    timestamp=result.accepted_at,
                    retry_count=retry_count,
                )
                stored = self._repository.add_message(message)
                self._repository.save_conversation(conversation.patch(last_outbound_at=result.accepted_at, state=ConversationState.WAITING_ON_CONTACT))
                self._repository.add_event(
                    self._make_event(
                        event_type="message_sent",
                        message=stored,
                        status=result.status.value,
                        occurred_at=result.accepted_at,
                    )
                )
                return stored
            except AdapterError as err:
                retry_count += 1
                if not err.retryable or retry_count > max_retries:
                    failed = MessageRecord(
                        message_id=message_id,
                        tenant_id=ctx.tenant_id,
                        conversation_id=conversation.conversation_id,
                        contact_id=contact.contact_id,
                        direction=MessageDirection.OUTBOUND,
                        provider=self._provider,
                        provider_message_id=f"failed:{message_id}",
                        text=body,
                        intent=intent,
                        status=MessageDeliveryStatus.FAILED.value,
                        payload_hash=self._hash_payload(body, to),
                        timestamp=ctx.metadata.get("occurred_at", ""),
                        error_code=err.code.value,
                        retry_count=retry_count,
                    )
                    stored = self._repository.add_message(failed)
                    self._repository.add_event(
                        self._make_event(
                            event_type="message_retry_exhausted",
                            message=stored,
                            status=MessageDeliveryStatus.FAILED.value,
                            occurred_at=ctx.metadata.get("occurred_at", ""),
                            error_code=err.code.value,
                        )
                    )
                    return stored

                self._repository.add_event(
                    MessageEvent(
                        event_id=str(uuid4()),
                        tenant_id=ctx.tenant_id,
                        message_id=message_id,
                        conversation_id=conversation.conversation_id,
                        contact_id=contact.contact_id,
                        event_type="message_retry_scheduled",
                        status="retrying",
                        occurred_at=ctx.metadata.get("occurred_at", ""),
                        provider=self._provider,
                        provider_message_id="",
                        payload_hash=self._hash_payload(body, to),
                        error_code=err.code.value,
                        details={"retry_count": retry_count},
                    )
                )

    def handle_status_webhook(self, webhook: RawWebhookInput, ctx: AdapterContext) -> list[MessageRecord]:
        events = self._adapter.parse_webhook(webhook, ctx)
        updated: list[MessageRecord] = []
        for event in events:
            if event.event_id in self._repository.processed_status_events:
                continue
            self._repository.processed_status_events.add(event.event_id)
            message = self._repository.get_message_by_provider_id(event.provider_message_id)
            if not message:
                continue
            patched = replace(message, status=event.status.value, error_code=event.reason)
            self._repository.save_message(patched)
            self._repository.add_event(
                self._make_event(
                    event_type=f"message_{event.status.value}",
                    message=patched,
                    status=event.status.value,
                    occurred_at=event.occurred_at,
                    error_code=event.reason,
                )
            )
            updated.append(patched)
        return updated

    def _persist_inbound(self, item: InboundMessage, ctx: AdapterContext) -> MessageRecord:
        contact, conversation = self._resolve_contact_conversation(
            phone=item.from_number,
            profile_name=item.profile_name,
            ctx=ctx,
            business_context="general",
        )
        message = MessageRecord(
            message_id=str(uuid4()),
            tenant_id=ctx.tenant_id,
            conversation_id=conversation.conversation_id,
            contact_id=contact.contact_id,
            direction=MessageDirection.INBOUND,
            provider=self._provider,
            provider_message_id=item.provider_message_id,
            text=item.text,
            intent=self._classify_inbound_intent(item.text),
            status=MessageDeliveryStatus.RECEIVED.value,
            payload_hash=self._hash_payload(item.text, item.from_number),
            timestamp=item.occurred_at,
            metadata={"event_id": item.event_id, "raw": item.raw},
        )
        stored = self._repository.add_message(message)
        self._repository.save_conversation(conversation.patch(last_inbound_at=item.occurred_at, state=ConversationState.ACTIVE))
        self._repository.add_event(
            self._make_event(
                event_type="message_received",
                message=stored,
                status=MessageDeliveryStatus.RECEIVED.value,
                occurred_at=item.occurred_at,
            )
        )
        if self._lead_capture_service:
            self._lead_capture_service.capture_inbound_message(
                tenant_id=ctx.tenant_id,
                contact_id=contact.contact_id,
                normalized_phone=contact.normalized_phone,
                conversation_id=conversation.conversation_id,
                message=stored,
                classified_intent=stored.intent,
            )
        return stored

    def _resolve_contact_conversation(
        self,
        *,
        phone: str,
        profile_name: str | None,
        ctx: AdapterContext,
        business_context: str,
    ) -> tuple[Contact, Conversation]:
        normalized_phone = self._normalize_phone(phone)
        contact = self._repository.upsert_contact(
            Contact(
                contact_id=str(uuid4()),
                tenant_id=ctx.tenant_id,
                normalized_phone=normalized_phone,
                profile_name=profile_name,
            )
        )
        conversation = self._repository.get_or_create_conversation(
            Conversation(
                conversation_id=str(uuid4()),
                tenant_id=ctx.tenant_id,
                channel="whatsapp",
                normalized_phone=normalized_phone,
                contact_id=contact.contact_id,
                state=ConversationState.NEW,
                business_context=business_context,
            )
        )
        return contact, conversation

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        digits = "".join(ch for ch in phone if ch.isdigit())
        if phone.startswith("+"):
            return f"+{digits}"
        return f"+{digits}"

    @staticmethod
    def _hash_payload(text: str, phone: str) -> str:
        return hashlib.sha256(f"{phone}:{text}".encode("utf-8")).hexdigest()

    @staticmethod
    def _classify_inbound_intent(text: str) -> str:
        normalized = text.lower()
        if any(token in normalized for token in ("buy", "invoice paid", "payment done", "confirmed")):
            return "PURCHASE_CONFIRMED"
        if any(token in normalized for token in ("price", "discount", "offer", "negotiate", "counter")):
            return "NEGOTIATION"
        if any(token in normalized for token in ("not interested", "stop", "cancel")):
            return "LOST_SIGNAL"
        if any(token in normalized for token in ("budget", "team size", "company", "need", "requirements")):
            return "QUALIFICATION"
        return "INBOUND_USER_MESSAGE"

    def _make_event(
        self,
        *,
        event_type: str,
        message: MessageRecord,
        status: str,
        occurred_at: str,
        error_code: str | None = None,
    ) -> MessageEvent:
        return MessageEvent(
            event_id=str(uuid4()),
            tenant_id=message.tenant_id,
            message_id=message.message_id,
            conversation_id=message.conversation_id,
            contact_id=message.contact_id,
            event_type=event_type,
            status=status,
            occurred_at=occurred_at,
            provider=message.provider,
            provider_message_id=message.provider_message_id,
            payload_hash=message.payload_hash,
            error_code=error_code,
        )
