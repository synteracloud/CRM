from __future__ import annotations

import unittest

from services.conversation import ChatMessage, ConversationContext, ConversationalCRMService
from src.lead_management.entities import Lead


class ConversationalCRMServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ConversationalCRMService()
        lead = Lead(
            lead_id="lead-1",
            tenant_id="tenant-1",
            owner_user_id="owner-1",
            source="whatsapp",
            status="new",
            score=10,
            email="old@example.com",
            phone="+12025550100",
            company_name="Acme",
            created_at="2026-04-01T10:00:00Z",
        )
        self.service.ensure_lead(lead)
        self.service.bind_conversation(
            ConversationContext(
                tenant_id="tenant-1",
                conversation_id="conv-1",
                contact_id="contact-1",
                lead_id="lead-1",
            )
        )

    def test_actions_can_be_executed_via_chat(self) -> None:
        message = ChatMessage(
            message_id="msg-1",
            tenant_id="tenant-1",
            conversation_id="conv-1",
            contact_id="contact-1",
            direction="inbound",
            text="set email to new@example.com and follow up tomorrow",
            occurred_at="2026-04-01T10:05:00Z",
        )

        results = self.service.handle_message(message)

        self.assertEqual({item.action for item in results}, {"update_lead", "schedule_follow_up"})
        self.assertEqual(self.service._lead_service.get_lead("lead-1").email, "new@example.com")

    def test_stage_moves_via_chat_trigger(self) -> None:
        message = ChatMessage(
            message_id="msg-2",
            tenant_id="tenant-1",
            conversation_id="conv-1",
            contact_id="contact-1",
            direction="inbound",
            text="move stage to qualified",
            occurred_at="2026-04-01T10:06:00Z",
        )

        results = self.service.handle_message(message)

        self.assertEqual(results[0].action, "move_stage")
        self.assertEqual(self.service._lead_service.get_lead("lead-1").status, "qualified")

    def test_every_message_is_linked_to_activity_and_missing_flows_are_detected(self) -> None:
        message = ChatMessage(
            message_id="msg-3",
            tenant_id="tenant-1",
            conversation_id="conv-1",
            contact_id="contact-1",
            direction="inbound",
            text="can you summarize prior notes",
            occurred_at="2026-04-01T10:07:00Z",
        )

        results = self.service.handle_message(message)
        events = self.service.list_activity(tenant_id="tenant-1", conversation_id="conv-1")

        self.assertEqual(results[0].status, "missing_flow")
        self.assertGreaterEqual(len(events), 2)
        self.assertEqual(events[-1].activity_type, "missing_flow_detected")

    def test_qc_report_is_aligned_to_target_state(self) -> None:
        self.service.handle_message(
            ChatMessage(
                message_id="msg-4",
                tenant_id="tenant-1",
                conversation_id="conv-1",
                contact_id="contact-1",
                direction="inbound",
                text="send invoice",
                occurred_at="2026-04-01T10:08:00Z",
            )
        )

        qc = self.service.review_qc()

        self.assertTrue(qc["chat_first_operations"])
        self.assertTrue(qc["activity_linking"])
        self.assertEqual(qc["score"], "10/10")


if __name__ == "__main__":
    unittest.main()
