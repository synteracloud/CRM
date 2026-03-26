from __future__ import annotations

import unittest

from src.predictive_models import OpportunityHistory, PredictiveModelApi, PredictiveModelService, SubscriptionHistory


class PredictiveModelServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = PredictiveModelService()
        self.api = PredictiveModelApi(self.service)

    def test_predict_win_probability_uses_historical_opportunity_data(self) -> None:
        self.service.ingest_opportunity_history(
            [
                OpportunityHistory(
                    opportunity_id="opp-1",
                    tenant_id="tenant-1",
                    stage="closed_won",
                    amount=25000,
                    forecast_category="closed",
                    is_closed=True,
                    is_won=True,
                    created_at="2025-01-01",
                    close_date="2025-02-01",
                ),
                OpportunityHistory(
                    opportunity_id="opp-2",
                    tenant_id="tenant-1",
                    stage="closed_lost",
                    amount=40000,
                    forecast_category="closed",
                    is_closed=True,
                    is_won=False,
                    created_at="2025-01-15",
                    close_date="2025-03-10",
                ),
            ]
        )

        response = self.api.predict_win_probability(
            tenant_id="tenant-1",
            opportunity_id="opp-open-1",
            stage="negotiation",
            amount=30000,
            forecast_category="commit",
            created_at="2026-01-01",
            close_date="2026-03-01",
            request_id="req-1",
        )

        self.assertIn("data", response)
        self.assertGreater(response["data"]["probability"], 0.5)
        self.assertIn("tenant_historical_win_rate", response["data"]["drivers"][0])

    def test_predict_churn_uses_historical_subscription_data(self) -> None:
        self.service.ingest_subscription_history(
            [
                SubscriptionHistory(
                    subscription_id="sub-1",
                    tenant_id="tenant-1",
                    status="active",
                    mrr=5000,
                    started_at="2025-01-01",
                    current_period_end="2025-12-31",
                    last_payment_at="2025-12-15",
                    late_payment_count=0,
                    support_case_count_90d=1,
                ),
                SubscriptionHistory(
                    subscription_id="sub-2",
                    tenant_id="tenant-1",
                    status="canceled",
                    mrr=2200,
                    started_at="2025-02-01",
                    current_period_end="2025-08-31",
                    last_payment_at="2025-06-15",
                    late_payment_count=3,
                    support_case_count_90d=6,
                ),
            ]
        )

        response = self.api.predict_churn(
            tenant_id="tenant-1",
            subscription_id="sub-open-1",
            status="past_due",
            mrr=1800,
            started_at="2025-06-01",
            current_period_end="2026-06-01",
            last_payment_at="2026-03-01",
            late_payment_count=4,
            support_case_count_90d=7,
            request_id="req-2",
        )

        self.assertIn("data", response)
        self.assertGreaterEqual(response["data"]["churn_probability"], 0.7)
        self.assertEqual(response["data"]["risk_level"], "high")

    def test_rejects_invalid_historical_data(self) -> None:
        response = self.api.ingest_opportunity_history(
            [
                OpportunityHistory(
                    opportunity_id="opp-bad",
                    tenant_id="tenant-1",
                    stage="unknown",
                    amount=100,
                    forecast_category="pipeline",
                    is_closed=False,
                    is_won=False,
                    created_at="2026-01-10",
                    close_date="2026-01-11",
                )
            ],
            request_id="req-3",
        )

        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], "validation_error")


if __name__ == "__main__":
    unittest.main()
