from __future__ import annotations

import unittest

from src.revenue_recognition import BillingEvent, RecognitionRule, RevenueRecognitionApi, RevenueRecognitionService


class RevenueRecognitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = RevenueRecognitionService()
        self.api = RevenueRecognitionApi(self.service)

    def test_builds_deterministic_schedules_for_one_time_and_recurring_rules(self) -> None:
        rules = [
            RecognitionRule(
                rule_id="rule-recurring",
                tenant_id="tenant-1",
                contract_id="contract-1",
                revenue_type="recurring",
                amount=90.0,
                currency="USD",
                service_period_start="2026-03-01",
                service_period_end="2026-03-03",
            ),
            RecognitionRule(
                rule_id="rule-onetime",
                tenant_id="tenant-1",
                contract_id="contract-1",
                revenue_type="one_time",
                amount=30.0,
                currency="USD",
                service_period_start="2026-03-02",
                service_period_end="2026-03-02",
                recognized_at="2026-03-02",
            ),
        ]
        events = [
            BillingEvent(
                event_id="evt-invoice-1",
                tenant_id="tenant-1",
                contract_id="contract-1",
                event_type="invoice_posted",
                amount=120.0,
                currency="USD",
                occurred_at="2026-03-01",
            )
        ]

        first = self.service.build_schedules(tenant_id="tenant-1", rules=rules, billing_events=events)
        second = self.service.build_schedules(tenant_id="tenant-1", rules=list(reversed(rules)), billing_events=events)

        self.assertEqual(first, second)
        schedule = first[0]
        self.assertEqual(schedule.total_scheduled_amount, 120.0)
        self.assertEqual(tuple((line.recognition_date, line.amount) for line in schedule.lines), (
            ("2026-03-01", 30.0),
            ("2026-03-02", 30.0),
            ("2026-03-02", 30.0),
            ("2026-03-03", 30.0),
        ))

    def test_earned_and_deferred_tie_to_billing_events_without_mismatch(self) -> None:
        rules = [
            RecognitionRule(
                rule_id="rule-recurring",
                tenant_id="tenant-1",
                contract_id="contract-1",
                revenue_type="recurring",
                amount=100.0,
                currency="USD",
                service_period_start="2026-03-01",
                service_period_end="2026-03-10",
            )
        ]
        events = [
            BillingEvent("evt-invoice", "tenant-1", "contract-1", "invoice_posted", 100.0, "USD", "2026-03-01"),
            BillingEvent("evt-pay-1", "tenant-1", "contract-1", "payment_settled", 70.0, "USD", "2026-03-05"),
            BillingEvent("evt-refund-1", "tenant-1", "contract-1", "payment_refunded", 10.0, "USD", "2026-03-08"),
        ]
        schedules = self.service.build_schedules(tenant_id="tenant-1", rules=rules, billing_events=events)

        positions = self.service.build_positions(
            tenant_id="tenant-1",
            as_of="2026-03-08",
            schedules=list(schedules),
            billing_events=events,
        )

        position = positions[0]
        self.assertEqual(position.billed_amount, 100.0)
        self.assertEqual(position.collected_amount, 60.0)
        self.assertEqual(position.scheduled_through_as_of, 80.0)
        self.assertEqual(position.earned_amount, 60.0)
        self.assertEqual(position.deferred_amount, 0.0)

    def test_build_reporting_inputs_returns_traceable_daily_series(self) -> None:
        rules = [
            RecognitionRule(
                rule_id="rule-1",
                tenant_id="tenant-1",
                contract_id="contract-9",
                revenue_type="one_time",
                amount=50.0,
                currency="USD",
                service_period_start="2026-03-02",
                service_period_end="2026-03-02",
                recognized_at="2026-03-02",
            )
        ]
        events = [
            BillingEvent("evt-invoice-9", "tenant-1", "contract-9", "invoice_posted", 50.0, "USD", "2026-03-01"),
            BillingEvent("evt-pay-9", "tenant-1", "contract-9", "payment_settled", 50.0, "USD", "2026-03-02"),
        ]
        schedules = self.service.build_schedules(tenant_id="tenant-1", rules=rules, billing_events=events)
        response = self.api.build_reporting_inputs(
            tenant_id="tenant-1",
            as_of="2026-03-03",
            schedules=list(schedules),
            billing_events=events,
            request_id="req-rr-1",
        )

        self.assertIn("data", response)
        report = response["data"][0]
        self.assertEqual(report["daily_earned"], (("2026-03-02", 50.0),))
        self.assertEqual(report["daily_billed"], (("2026-03-01", 50.0),))
        self.assertEqual(report["daily_collected"], (("2026-03-02", 50.0),))
        self.assertEqual(report["cumulative_earned"], 50.0)
        self.assertEqual(report["deferred_ending_balance"], 0.0)


if __name__ == "__main__":
    unittest.main()
