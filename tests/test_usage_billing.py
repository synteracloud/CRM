from __future__ import annotations

import unittest

from src.usage_billing import (
    BillableEventRule,
    MeterRateCard,
    TierPrice,
    TrackedEvent,
    UsageBillingService,
)


class UsageBillingServiceTests(unittest.TestCase):
    def test_usage_is_derived_from_real_tracked_events_only(self) -> None:
        service = UsageBillingService()
        rules = [
            BillableEventRule(meter_code="messages_sent", event_name="communication.message.sent.v1"),
            BillableEventRule(
                meter_code="workflow_steps",
                event_name="workflow.execution.completed.v1",
                quantity_field="steps_executed",
                default_quantity=1,
            ),
        ]
        events = [
            TrackedEvent(
                event_id="evt-1",
                tenant_id="tenant-1",
                event_name="communication.message.sent.v1",
                occurred_at="2026-03-01T00:00:00Z",
                payload={"subscription_id": "sub-1", "account_id": "acc-1"},
            ),
            TrackedEvent(
                event_id="evt-2",
                tenant_id="tenant-1",
                event_name="workflow.execution.completed.v1",
                occurred_at="2026-03-01T00:10:00Z",
                payload={"subscription_id": "sub-1", "account_id": "acc-1", "steps_executed": 3},
            ),
            # not in event-catalog billable allowlist -> ignored
            TrackedEvent(
                event_id="evt-3",
                tenant_id="tenant-1",
                event_name="lead.created.v1",
                occurred_at="2026-03-01T00:20:00Z",
                payload={"subscription_id": "sub-1", "account_id": "acc-1"},
            ),
        ]

        usage = service.collect_billable_events(events, rules)
        self.assertEqual(len(usage), 2)
        self.assertEqual(sum(record.quantity for record in usage), 4)
        self.assertEqual({record.source_event_name for record in usage}, {"communication.message.sent.v1", "workflow.execution.completed.v1"})

    def test_no_duplicate_usage_charging_for_duplicate_deliveries(self) -> None:
        service = UsageBillingService()
        rules = [BillableEventRule(meter_code="messages_sent", event_name="communication.message.sent.v1")]
        duplicate_event = TrackedEvent(
            event_id="evt-dup",
            tenant_id="tenant-1",
            event_name="communication.message.sent.v1",
            occurred_at="2026-03-02T00:00:00Z",
            payload={"subscription_id": "sub-1", "account_id": "acc-1"},
        )

        first_batch = service.collect_billable_events([duplicate_event], rules)
        second_batch = service.collect_billable_events([duplicate_event], rules)

        self.assertEqual(len(first_batch), 1)
        self.assertEqual(len(second_batch), 0)

    def test_aggregation_rating_and_invoice_generation_rules_are_explicit(self) -> None:
        service = UsageBillingService()
        rules = [
            BillableEventRule(meter_code="messages_sent", event_name="communication.message.sent.v1"),
            BillableEventRule(
                meter_code="workflow_steps",
                event_name="workflow.execution.completed.v1",
                quantity_field="steps_executed",
            ),
        ]
        events = [
            TrackedEvent(
                event_id="evt-10",
                tenant_id="tenant-1",
                event_name="communication.message.sent.v1",
                occurred_at="2026-03-03T00:00:00Z",
                payload={"subscription_id": "sub-1", "account_id": "acc-1"},
            ),
            TrackedEvent(
                event_id="evt-11",
                tenant_id="tenant-1",
                event_name="workflow.execution.completed.v1",
                occurred_at="2026-03-03T00:01:00Z",
                payload={"subscription_id": "sub-1", "account_id": "acc-1", "steps_executed": 9},
            ),
        ]

        usage = service.collect_billable_events(events, rules)
        aggregates = service.aggregate_usage(usage, period_start="2026-03-01T00:00:00Z", period_end="2026-04-01T00:00:00Z")
        self.assertEqual(len(aggregates), 2)

        rate_cards = [
            MeterRateCard(meter_code="messages_sent", unit="event", currency="USD", billing_model="flat", unit_price=0.02),
            MeterRateCard(
                meter_code="workflow_steps",
                unit="event",
                currency="USD",
                billing_model="tiered",
                tiers=(TierPrice(up_to=5, unit_price=0.05), TierPrice(up_to=None, unit_price=0.02)),
            ),
        ]
        rated = service.rate_usage(aggregates, rate_cards)
        invoice_inputs = service.generate_invoice_inputs(rated)
        rules_doc = service.processing_rules()

        self.assertEqual(len(invoice_inputs), 1)
        self.assertEqual(invoice_inputs[0].usage_subtotal, 0.35)
        self.assertEqual(
            rules_doc["aggregation_dimensions"],
            [
                "tenant_id",
                "subscription_id",
                "account_id",
                "meter_code",
                "unit",
                "period_start",
                "period_end",
            ],
        )


if __name__ == "__main__":
    unittest.main()
