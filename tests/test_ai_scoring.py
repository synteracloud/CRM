from __future__ import annotations

import unittest

from src.ai_scoring import LeadScoringInput, OpportunityScoringInput, ScoringApi, ScoringService


class ScoringServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ScoringService()
        self.api = ScoringApi(self.service)

    def test_lead_score_uses_real_fields_and_returns_factors(self) -> None:
        scoring_input = LeadScoringInput(
            lead_id="lead-1",
            tenant_id="tenant-1",
            source="web_form",
            status="new",
            email="lead@example.com",
            phone="+12065550100",
            company_name="Acme",
            activity_event_count_30d=6,
        )

        response = self.api.score_lead(scoring_input, request_id="req-1")

        self.assertIn("data", response)
        self.assertEqual(response["data"]["entity_type"], "lead")
        self.assertGreater(response["data"]["score"], 0)
        self.assertEqual(len(response["data"]["factors"]), 4)

    def test_opportunity_score_uses_pipeline_fields_and_returns_factors(self) -> None:
        scoring_input = OpportunityScoringInput(
            opportunity_id="opp-1",
            tenant_id="tenant-1",
            stage="proposal",
            amount=50000,
            close_days_out=25,
            quote_count=1,
            activity_event_count_30d=9,
            has_primary_contact=True,
        )

        result = self.service.score_opportunity(scoring_input)

        self.assertEqual(result.entity_type, "opportunity")
        self.assertEqual(len(result.factors), 4)
        self.assertGreaterEqual(result.score, 0)
        self.assertLessEqual(result.score, 100)

    def test_validation_error_when_no_lead_contact_data(self) -> None:
        scoring_input = LeadScoringInput(
            lead_id="lead-2",
            tenant_id="tenant-1",
            source="web_form",
            status="open",
            email="",
            phone="",
            company_name="Acme",
            activity_event_count_30d=2,
        )

        response = self.api.score_lead(scoring_input, request_id="req-2")

        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], "validation_error")


if __name__ == "__main__":
    unittest.main()
