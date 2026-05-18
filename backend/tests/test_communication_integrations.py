from __future__ import annotations

import unittest

from src.communication_integrations import (
    API_ENDPOINTS,
    CommunicationContractError,
    CommunicationIntegrationService,
    CommunicationMessage,
    CommunicationThread,
    LinkedEntityRef,
)


class CommunicationIntegrationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = CommunicationIntegrationService()
        self.service.register_valid_entities(
            tenant_id="tenant-1",
            lead_ids={"lead-1"},
            contact_ids={"contact-1"},
            ticket_ids={"ticket-1"},
        )

    def test_thread_dedupes_and_prevents_duplicate_thread_records(self) -> None:
        thread1 = CommunicationThread(
            message_thread_id="thr-1",
            tenant_id="tenant-1",
            channel_type="email",
            provider="sendgrid",
            provider_thread_key="ticket-xyz",
            linked_entity_type="ticket",
            linked_entity_id="ticket-1",
            subject="Support needed",
            participants=("customer@example.com", "support@example.com"),
            status="open",
            created_at="2026-03-26T00:00:00Z",
            updated_at="2026-03-26T00:00:00Z",
        )
        thread2 = CommunicationThread(
            message_thread_id="thr-2",
            tenant_id="tenant-1",
            channel_type="email",
            provider="sendgrid",
            provider_thread_key="ticket-xyz",
            linked_entity_type="ticket",
            linked_entity_id="ticket-1",
            subject="Support needed",
            participants=("support@example.com", "customer@example.com"),
            status="open",
            created_at="2026-03-26T00:01:00Z",
            updated_at="2026-03-26T00:01:00Z",
        )

        stored_1 = self.service.create_or_get_thread(thread1)
        stored_2 = self.service.create_or_get_thread(thread2)

        self.assertEqual(stored_1.message_thread_id, "thr-1")
        self.assertEqual(stored_2.message_thread_id, "thr-1")
        self.assertEqual(len(self.service.list_threads()), 1)

    def test_send_and_receive_across_email_sms_whatsapp_with_valid_linkage(self) -> None:
        email_thread = CommunicationThread(
            message_thread_id="thr-email",
            tenant_id="tenant-1",
            channel_type="email",
            provider="sendgrid",
            provider_thread_key="sg-thread-1",
            linked_entity_type="contact",
            linked_entity_id="contact-1",
            subject="Welcome",
            participants=("noreply@crm.test", "customer@example.com"),
            status="open",
            created_at="2026-03-26T01:00:00Z",
            updated_at="2026-03-26T01:00:00Z",
        )
        sms_thread = CommunicationThread(
            message_thread_id="thr-sms",
            tenant_id="tenant-1",
            channel_type="sms",
            provider="twilio",
            provider_thread_key="sms-session-1",
            linked_entity_type="lead",
            linked_entity_id="lead-1",
            subject="Lead nurture",
            participants=("+15550000001", "+15550000002"),
            status="open",
            created_at="2026-03-26T01:10:00Z",
            updated_at="2026-03-26T01:10:00Z",
        )
        wa_thread = CommunicationThread(
            message_thread_id="thr-wa",
            tenant_id="tenant-1",
            channel_type="whatsapp",
            provider="twilio",
            provider_thread_key="wa-thread-1",
            linked_entity_type="ticket",
            linked_entity_id="ticket-1",
            subject="Ticket update",
            participants=("whatsapp:+15550000001", "whatsapp:+15550000003"),
            status="open",
            created_at="2026-03-26T01:20:00Z",
            updated_at="2026-03-26T01:20:00Z",
        )
        self.service.create_or_get_thread(email_thread)
        self.service.create_or_get_thread(sms_thread)
        self.service.create_or_get_thread(wa_thread)

        outbound_email = CommunicationMessage(
            message_id="msg-1",
            tenant_id="tenant-1",
            message_thread_id="thr-email",
            provider="sendgrid",
            provider_message_id="sg-msg-1",
            channel_type="email",
            direction="outbound",
            sender="noreply@crm.test",
            recipient="customer@example.com",
            body="Hello from CRM",
            status="queued",
            linked_entity_type="contact",
            linked_entity_id="contact-1",
            sent_at="2026-03-26T01:01:00Z",
        )
        outbound_sms = CommunicationMessage(
            message_id="msg-2",
            tenant_id="tenant-1",
            message_thread_id="thr-sms",
            provider="twilio",
            provider_message_id="tw-msg-1",
            channel_type="sms",
            direction="outbound",
            sender="+15550000001",
            recipient="+15550000002",
            body="Hi lead",
            status="queued",
            linked_entity_type="lead",
            linked_entity_id="lead-1",
            sent_at="2026-03-26T01:11:00Z",
        )
        inbound_wa = CommunicationMessage(
            message_id="msg-3",
            tenant_id="tenant-1",
            message_thread_id="thr-wa",
            provider="twilio",
            provider_message_id="tw-msg-2",
            channel_type="whatsapp",
            direction="inbound",
            sender="whatsapp:+15550000003",
            recipient="whatsapp:+15550000001",
            body="Any update?",
            status="received",
            linked_entity_type="ticket",
            linked_entity_id="ticket-1",
            sent_at="2026-03-26T01:21:00Z",
        )

        self.service.send_email(message=outbound_email, linked_entity=LinkedEntityRef("contact", "contact-1"))
        self.service.send_sms(message=outbound_sms, linked_entity=LinkedEntityRef("lead", "lead-1"))
        self.service.receive_message(message=inbound_wa, linked_entity=LinkedEntityRef("ticket", "ticket-1"))

        self.assertEqual(len(self.service.list_messages("thr-email")), 1)
        self.assertEqual(len(self.service.list_messages("thr-sms")), 1)
        self.assertEqual(len(self.service.list_messages("thr-wa")), 1)


    def test_communication_api_paths_use_noun_based_resources(self) -> None:
        self.assertEqual(API_ENDPOINTS["send_email"]["path"], "/api/v1/communications/email-messages")
        self.assertEqual(API_ENDPOINTS["send_sms"]["path"], "/api/v1/communications/sms-messages")
        self.assertEqual(API_ENDPOINTS["send_whatsapp"]["path"], "/api/v1/communications/whatsapp-messages")
        self.assertEqual(API_ENDPOINTS["receive_message"]["path"], "/api/v1/communications/inbound-messages")

    def test_orphan_or_invalid_linkage_is_rejected(self) -> None:
        thread = CommunicationThread(
            message_thread_id="thr-invalid",
            tenant_id="tenant-1",
            channel_type="email",
            provider="sendgrid",
            provider_thread_key="invalid-1",
            linked_entity_type="contact",
            linked_entity_id="contact-does-not-exist",
            subject="Invalid",
            participants=("a@example.com", "b@example.com"),
            status="open",
            created_at="2026-03-26T02:00:00Z",
            updated_at="2026-03-26T02:00:00Z",
        )

        with self.assertRaises(CommunicationContractError):
            self.service.create_or_get_thread(thread)

    def test_duplicate_provider_message_id_is_idempotent(self) -> None:
        thread = CommunicationThread(
            message_thread_id="thr-idempotent",
            tenant_id="tenant-1",
            channel_type="sms",
            provider="twilio",
            provider_thread_key="idempotent-1",
            linked_entity_type="lead",
            linked_entity_id="lead-1",
            subject="Lead touch",
            participants=("+15550000010", "+15550000011"),
            status="open",
            created_at="2026-03-26T03:00:00Z",
            updated_at="2026-03-26T03:00:00Z",
        )
        self.service.create_or_get_thread(thread)

        message_1 = CommunicationMessage(
            message_id="msg-a",
            tenant_id="tenant-1",
            message_thread_id="thr-idempotent",
            provider="twilio",
            provider_message_id="tw-idempotent-1",
            channel_type="sms",
            direction="outbound",
            sender="+15550000010",
            recipient="+15550000011",
            body="Hello",
            status="queued",
            linked_entity_type="lead",
            linked_entity_id="lead-1",
            sent_at="2026-03-26T03:01:00Z",
        )
        message_2 = CommunicationMessage(
            message_id="msg-b",
            tenant_id="tenant-1",
            message_thread_id="thr-idempotent",
            provider="twilio",
            provider_message_id="tw-idempotent-1",
            channel_type="sms",
            direction="outbound",
            sender="+15550000010",
            recipient="+15550000011",
            body="Hello duplicate",
            status="queued",
            linked_entity_type="lead",
            linked_entity_id="lead-1",
            sent_at="2026-03-26T03:01:30Z",
        )

        stored_1 = self.service.send_sms(message=message_1, linked_entity=LinkedEntityRef("lead", "lead-1"))
        stored_2 = self.service.send_sms(message=message_2, linked_entity=LinkedEntityRef("lead", "lead-1"))

        self.assertEqual(stored_1.message_id, "msg-a")
        self.assertEqual(stored_2.message_id, "msg-a")
        self.assertEqual(len(self.service.list_messages("thr-idempotent")), 1)


if __name__ == "__main__":
    unittest.main()
