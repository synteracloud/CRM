from __future__ import annotations

import unittest

from src.ai_copilot import CopilotApi, CopilotContext, CopilotService


class CopilotServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = CopilotService()
        self.api = CopilotApi(self.service)

    def test_context_aware_suggestion_for_opportunity_workflow(self) -> None:
        context = CopilotContext(
            tenant_id="tenant-1",
            user_id="user-1",
            workflow_name="Opportunity pipeline & close outcomes",
            primary_entity_type="Opportunity",
            primary_entity_id="opp-100",
            observed_data={
                "opportunity_stage": "proposal",
                "activity_event_count_30d": 8,
                "quote_count": 2,
                "close_days_out": 25,
                "amount": 125000,
            },
        )

        response = self.api.get_suggestions(context, request_id="req-copilot-1")

        self.assertIn("data", response)
        self.assertEqual(response["data"]["workflow_name"], "Opportunity pipeline & close outcomes")
        self.assertEqual(len(response["data"]["suggestions"]), 1)
        suggestion = response["data"]["suggestions"][0]
        self.assertEqual(suggestion["action_type"], "recommend_stage_progression")
        self.assertIn("quote_count", suggestion["evidence"])

    def test_no_hallucinated_action_when_required_data_missing(self) -> None:
        context = CopilotContext(
            tenant_id="tenant-1",
            user_id="user-1",
            workflow_name="Lead intake, assignment, conversion",
            primary_entity_type="Lead",
            primary_entity_id="lead-12",
            observed_data={
                "lead_status": "new",
                "lead_score": 92,
                # missing assigned_user_id / activity_event_count_7d / has_contact
                "has_account": False,
            },
        )

        result = self.service.suggest(context)

        self.assertEqual(result.primary_entity_id, "lead-12")
        self.assertEqual(len(result.suggestions), 0)

    def test_validation_error_when_observed_data_is_empty(self) -> None:
        context = CopilotContext(
            tenant_id="tenant-1",
            user_id="user-1",
            workflow_name="Case management & SLA",
            primary_entity_type="Case",
            primary_entity_id="case-9",
            observed_data={},
        )

        response = self.api.get_suggestions(context, request_id="req-copilot-2")

        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], "validation_error")


if __name__ == "__main__":
    unittest.main()
