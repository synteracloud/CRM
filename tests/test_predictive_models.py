from __future__ import annotations

import unittest

from src.predictive_models import OpportunityHistory, PredictiveModelApi, PredictiveModelService, SubscriptionValueHistory


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

    def test_predict_churn_uses_billing_and_subscription_signals(self) -> None:
        self.service.ingest_subscription_history(
            [
                SubscriptionValueHistory(
                    subscription_id="sub-1",
                    tenant_id="tenant-1",
                    status="active",
                    start_date="2025-01-01",
                    end_date=None,
                    renewal_date="2026-01-01",
                    invoice_amount_due_12m=5000,
                    invoice_amount_paid_12m=5000,
                    invoice_overdue_count_12m=0,
                    payment_failed_count_90d=0,
                    payment_success_count_90d=4,
                ),
                SubscriptionValueHistory(
                    subscription_id="sub-2",
                    tenant_id="tenant-1",
                    status="canceled",
                    start_date="2025-02-01",
                    end_date="2025-08-31",
                    renewal_date=None,
                    invoice_amount_due_12m=6000,
                    invoice_amount_paid_12m=3000,
                    invoice_overdue_count_12m=5,
                    payment_failed_count_90d=3,
                    payment_success_count_90d=1,
                ),
            ]
        )

        response = self.api.predict_churn(
            tenant_id="tenant-1",
            subscription_id="sub-open-1",
            status="past_due",
            start_date="2025-06-01",
            end_date=None,
            renewal_date="2026-06-01",
            invoice_amount_due_12m=7200,
            invoice_amount_paid_12m=4200,
            invoice_overdue_count_12m=4,
            payment_failed_count_90d=3,
            payment_success_count_90d=1,
            request_id="req-2",
        )

        self.assertIn("data", response)
        self.assertGreaterEqual(response["data"]["churn_probability"], 0.7)
        self.assertEqual(response["data"]["risk_level"], "high")

    def test_predict_clv_uses_subscription_and_churn_logic(self) -> None:
        self.service.ingest_subscription_history(
            [
                SubscriptionValueHistory(
                    subscription_id="sub-1",
                    tenant_id="tenant-1",
                    status="active",
                    start_date="2024-01-01",
                    end_date=None,
                    renewal_date="2026-01-01",
                    invoice_amount_due_12m=12000,
                    invoice_amount_paid_12m=11800,
                    invoice_overdue_count_12m=0,
                    payment_failed_count_90d=0,
                    payment_success_count_90d=5,
                )
            ]
        )

        response = self.api.predict_customer_lifetime_value(
            tenant_id="tenant-1",
            subscription_id="sub-1",
            status="active",
            start_date="2024-01-01",
            end_date=None,
            renewal_date="2026-01-01",
            invoice_amount_due_12m=12000,
            invoice_amount_paid_12m=11800,
            invoice_overdue_count_12m=0,
            payment_failed_count_90d=0,
            payment_success_count_90d=5,
            request_id="req-4",
        )

        self.assertIn("data", response)
        self.assertGreater(response["data"]["estimated_clv"], 11800)
        self.assertIn("expected_retention_years", " ".join(response["data"]["drivers"]))

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
