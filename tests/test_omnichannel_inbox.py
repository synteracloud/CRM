from __future__ import annotations

import unittest

from src.omnichannel_inbox import Message, MessageThread, OmnichannelInboxService, ThreadStateError


class OmnichannelInboxServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = OmnichannelInboxService()

    def test_no_duplicate_threads_for_same_customer_channel_and_subject(self) -> None:
        thread1 = MessageThread(
            message_thread_id="thr-1",
            tenant_id="tenant-1",
            account_id="acc-1",
            contact_id="con-1",
            channel_type="email",
            subject="Billing issue",
            status="open",
            created_at="2026-03-26T00:00:00Z",
            updated_at="2026-03-26T00:00:00Z",
        )
        thread2 = MessageThread(
            message_thread_id="thr-2",
            tenant_id="tenant-1",
            account_id="acc-1",
            contact_id="con-1",
            channel_type="email",
            subject="  Billing   issue ",
            status="open",
            created_at="2026-03-26T00:01:00Z",
            updated_at="2026-03-26T00:01:00Z",
        )

        stored1 = self.service.upsert_thread(thread1)
        stored2 = self.service.upsert_thread(thread2)

        self.assertEqual(stored1.message_thread_id, "thr-1")
        self.assertEqual(stored2.message_thread_id, "thr-1")
        self.assertEqual(len(self.service.list_threads()), 1)

    def test_message_must_be_tied_to_same_customer_entity_as_thread(self) -> None:
        thread = MessageThread(
            message_thread_id="thr-3",
            tenant_id="tenant-1",
            account_id="acc-1",
            contact_id="con-1",
            channel_type="chat",
            subject="Product question",
            status="open",
            created_at="2026-03-26T02:00:00Z",
            updated_at="2026-03-26T02:00:00Z",
        )
        self.service.upsert_thread(thread)

        message = Message(
            message_id="msg-1",
            tenant_id="tenant-1",
            message_thread_id="thr-3",
            direction="inbound",
            provider_message_id="provider-1",
            sender="customer@example.com",
            recipient="support@example.com",
            status="received",
            sent_at="2026-03-26T02:01:00Z",
        )

        self.service.ingest_message(message, customer_account_id="acc-1", customer_contact_id="con-1")
        with self.assertRaises(ThreadStateError):
            self.service.ingest_message(
                Message(
                    message_id="msg-2",
                    tenant_id="tenant-1",
                    message_thread_id="thr-3",
                    direction="inbound",
                    provider_message_id="provider-2",
                    sender="customer@example.com",
                    recipient="support@example.com",
                    status="received",
                    sent_at="2026-03-26T02:02:00Z",
                ),
                customer_contact_id="con-x",
            )

    def test_routing_is_consistent_once_assigned(self) -> None:
        thread = MessageThread(
            message_thread_id="thr-4",
            tenant_id="tenant-1",
            account_id="acc-2",
            contact_id="con-42",
            channel_type="message",
            subject="Need invoice and refund help",
            status="open",
            created_at="2026-03-26T03:00:00Z",
            updated_at="2026-03-26T03:00:00Z",
        )
        self.service.upsert_thread(thread)

        first = self.service.route_thread(
            "thr-4",
            assigned_at="2026-03-26T03:01:00Z",
            contact_owner_map={"con-42": "agent-7"},
        )
        second = self.service.route_thread(
            "thr-4",
            assigned_at="2026-03-26T03:02:00Z",
            contact_owner_map={"con-42": "agent-9"},
        )

        self.assertEqual(first.assigned_user_id, "agent-7")
        self.assertEqual(second.assigned_user_id, "agent-7")
        self.assertEqual(first.rule_code, "contact_owner")


if __name__ == "__main__":
    unittest.main()
