from __future__ import annotations

import unittest

from src.predictive_forecasting import ForecastEngineApi, ForecastEngineService, OpportunityForecastRow


class ForecastEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ForecastEngineService()
        self.api = ForecastEngineApi(self.service)

    def test_builds_revenue_and_pipeline_forecast_from_valid_rows_only(self) -> None:
        response = self.api.build_forecast(
            tenant_id="tenant-1",
            as_of="2026-03-26",
            opportunities=[
                OpportunityForecastRow(
                    opportunity_id="opp-open-1",
                    tenant_id="tenant-1",
                    stage="proposal",
                    amount=10000,
                    close_date="2026-04-30",
                    forecast_category="commit",
                    is_closed=False,
                    is_won=False,
                ),
                OpportunityForecastRow(
                    opportunity_id="opp-open-2",
                    tenant_id="tenant-1",
                    stage="qualification",
                    amount=6000,
                    close_date="2026-04-15",
                    forecast_category="pipeline",
                    is_closed=False,
                    is_won=False,
                ),
                OpportunityForecastRow(
                    opportunity_id="opp-closed-won-1",
                    tenant_id="tenant-1",
                    stage="proposal",
                    amount=8000,
                    close_date="2026-03-01",
                    forecast_category="closed",
                    is_closed=True,
                    is_won=True,
                ),
                OpportunityForecastRow(
                    opportunity_id="opp-closed-lost-1",
                    tenant_id="tenant-1",
                    stage="proposal",
                    amount=4000,
                    close_date="2026-03-10",
                    forecast_category="closed",
                    is_closed=True,
                    is_won=False,
                ),
            ],
            request_id="req-1",
        )

        self.assertIn("data", response)
        totals = response["data"]["totals"]
        self.assertEqual(totals["total_pipeline_amount"], 16000)
        self.assertEqual(totals["weighted_pipeline_amount"], 9000.0)
        self.assertEqual(totals["won_revenue_amount"], 8000)
        self.assertGreater(totals["predicted_revenue_amount"], 0)

        predictions = response["data"]["predictions"]
        self.assertEqual(len(predictions), 2)
        self.assertTrue(all(item["probability"] is not None for item in predictions))

    def test_rejects_invalid_domain_model_rows(self) -> None:
        response = self.api.build_forecast(
            tenant_id="tenant-1",
            as_of="2026-03-26",
            opportunities=[
                OpportunityForecastRow(
                    opportunity_id="opp-invalid",
                    tenant_id="tenant-1",
                    stage="prospecting",
                    amount=2000,
                    close_date="2026-03-31",
                    forecast_category="pipeline",
                    is_closed=False,
                    is_won=True,
                )
            ],
            request_id="req-2",
        )

        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], "validation_error")

    def test_no_fabricated_predictions_when_no_open_rows(self) -> None:
        response = self.api.build_forecast(
            tenant_id="tenant-1",
            as_of="2026-03-26",
            opportunities=[
                OpportunityForecastRow(
                    opportunity_id="opp-closed-1",
                    tenant_id="tenant-1",
                    stage="closed_won",
                    amount=5000,
                    close_date="2026-03-20",
                    forecast_category="closed",
                    is_closed=True,
                    is_won=True,
                )
            ],
            request_id="req-3",
        )

        self.assertIn("data", response)
        self.assertEqual(response["data"]["predictions"], ())
        self.assertEqual(response["data"]["totals"]["predicted_revenue_amount"], 0)


if __name__ == "__main__":
    unittest.main()
