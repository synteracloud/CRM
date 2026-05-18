from __future__ import annotations

import unittest

from src.automation_journeys import (
    JourneyDefinition,
    JourneyService,
    JourneyStep,
    JourneyValidationError,
    assert_triggers_in_catalog,
)
from src.event_bus import Event


class JourneyServiceTests(unittest.TestCase):
    def test_handle_event_executes_until_delay_then_resume(self) -> None:
        service = JourneyService()
        service.create_journey(
            JourneyDefinition(
                journey_id="journey-1",
                tenant_id="tenant-1",
                name="Stage Follow-up",
                trigger_event="opportunity.stage.changed.v1",
                steps=(
                    JourneyStep("assign", "assign", {"assignee": "user:42"}),
                    JourneyStep("wait", "delay", delay_seconds=1),
                    JourneyStep("email", "email", {"template": "stage-follow-up"}),
                ),
            )
        )

        event = Event(
            event_name="opportunity.stage.changed.v1",
            event_id="evt-1",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-1",
            payload={"opportunity_id": "opp-1"},
        )

        started = service.handle_event(event)
        self.assertEqual(len(started), 1)
        self.assertEqual(started[0].status, "waiting")

        resumed = service.resume_due_delays("2030-01-01T00:00:00Z")
        self.assertEqual(len(resumed), 1)
        self.assertEqual(resumed[0].status, "completed")
        self.assertEqual([item["action"] for item in resumed[0].execution_log if "action" in item][:3], ["assign", "delay.started", "delay.resumed"])

    def test_validation_rejects_unknown_trigger_and_undefined_action(self) -> None:
        service = JourneyService()

        with self.assertRaises(JourneyValidationError):
            service.create_journey(
                JourneyDefinition(
                    journey_id="bad-trigger",
                    tenant_id="tenant-1",
                    name="Bad Trigger",
                    trigger_event="not.in.catalog.v1",
                    steps=(JourneyStep("step-1", "email", {"template": "x"}),),
                )
            )

        with self.assertRaises(JourneyValidationError):
            service.create_journey(
                JourneyDefinition(
                    journey_id="bad-action",
                    tenant_id="tenant-1",
                    name="Bad Action",
                    trigger_event="lead.converted.v1",
                    steps=(JourneyStep("step-1", "delay", delay_seconds=0),),
                )
            )

    def test_stop_journey_prevents_future_starts(self) -> None:
        service = JourneyService()
        service.create_journey(
            JourneyDefinition(
                journey_id="journey-stop",
                tenant_id="tenant-1",
                name="Stop Example",
                trigger_event="lead.converted.v1",
                steps=(JourneyStep("notify", "email", {"template": "notify"}),),
            )
        )

        service.stop_journey("journey-stop")
        event = Event(
            event_name="lead.converted.v1",
            event_id="evt-stop",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-1",
            payload={"lead_id": "lead-1"},
        )
        started = service.handle_event(event)
        self.assertEqual(started, [])


class JourneyBindingsTests(unittest.TestCase):
    def test_all_workflow_automation_triggers_are_catalog_backed(self) -> None:
        assert_triggers_in_catalog()


if __name__ == "__main__":
    unittest.main()
