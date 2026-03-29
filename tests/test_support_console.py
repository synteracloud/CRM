from __future__ import annotations

import unittest

from src.support_console import ConversationMessage, CustomerContext, QueueItem, SupportConsoleService


class SupportConsoleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = SupportConsoleService()
        self.service.upsert_queue_item(
            QueueItem(
                ticket_id="tick-1",
                subject="Cannot login",
                status="open",
                priority="high",
                owner_user_id="agent-1",
                queue_name="tier1",
                response_due_at="2026-03-29T01:00:00Z",
                resolution_due_at="2026-03-29T04:00:00Z",
                sla_state="at_risk",
            )
        )
        self.service.upsert_queue_item(
            QueueItem(
                ticket_id="tick-2",
                subject="Billing mismatch",
                status="open",
                priority="medium",
                owner_user_id="agent-2",
                queue_name="billing",
                response_due_at="2026-03-29T00:30:00Z",
                resolution_due_at="2026-03-29T03:00:00Z",
                sla_state="breached",
            )
        )

    def test_workspace_is_ticket_first_with_required_views(self) -> None:
        workspace = self.service.build_workspace(workspace_id="ws-1", selected_ticket_id="tick-1")

        self.assertEqual(workspace.primary_view, "queue")
        self.assertIn("queue_view", workspace.views)
        self.assertIn("conversation_thread_panel", workspace.views)
        self.assertIn("customer_context_sidebar", workspace.views)
        self.assertIn("escalation_controls", workspace.views)
        self.assertTrue(workspace.active_sla_timer)

    def test_queue_default_sort_prioritizes_soonest_sla(self) -> None:
        workspace = self.service.build_workspace(workspace_id="ws-2", selected_ticket_id=None)
        self.assertEqual(workspace.queue_items[0].ticket_id, "tick-2")
        self.assertIn("response_due=", workspace.active_sla_timer)

    def test_conversation_and_context_panels_attach_to_selected_ticket(self) -> None:
        self.service.add_conversation_message(
            "tick-1",
            ConversationMessage(
                message_id="m-1",
                sender_type="customer",
                body="Any update on my login issue?",
                created_at="2026-03-29T00:10:00Z",
            ),
        )
        self.service.set_customer_context(
            "tick-1",
            CustomerContext(
                account_id="acc-1",
                account_name="Acme Inc",
                contact_id="con-1",
                contact_name="Sam Doe",
                contact_email="sam@acme.example",
                open_ticket_count=3,
                csat_score=4.2,
                plan_tier="enterprise",
            ),
        )

        workspace = self.service.build_workspace(workspace_id="ws-3", selected_ticket_id="tick-1")
        self.assertEqual(len(workspace.conversation_thread), 1)
        self.assertEqual(workspace.customer_context.account_id, "acc-1")

    def test_escalation_controls_and_actions_are_deterministic(self) -> None:
        controls = self.service.build_workspace(workspace_id="ws-4", selected_ticket_id="tick-2").escalation_controls
        self.assertEqual(controls.recommended_action, "page_on_call")

        updated = self.service.perform_escalation_action("tick-2", "page_on_call")
        self.assertEqual(updated.owner_user_id, "on-call-support")


if __name__ == "__main__":
    unittest.main()
