from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from services.followup import FollowupEnforcementEngine, FollowupPolicyError, FollowupState, LeadSnapshot


class FollowupEnforcementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = FollowupEnforcementEngine()
        self.t0 = datetime(2026, 3, 30, 8, 0, tzinfo=timezone.utc)
        self.lead = LeadSnapshot(
            lead_id="lead-1",
            tenant_id="tenant-1",
            owner_id="user-1",
            status="open",
            priority="hot",
            stage="discovery",
            last_activity_at=self.t0,
        )

    def test_scheduler_creates_initial_followup_and_queue_job(self) -> None:
        task = self.engine.register_lead(self.lead, now=self.t0)

        self.assertEqual(task.state, FollowupState.PENDING)
        self.assertEqual(self.engine.job_queue().size(), 1)

    def test_rule_engine_repairs_missing_pending_task(self) -> None:
        task = self.engine.register_lead(self.lead, now=self.t0)
        completed = task.patch(state=FollowupState.COMPLETED, completed_at=self.t0 + timedelta(minutes=10))
        self.engine._replace_task(completed)  # test setup for invalid state

        self.engine.hourly_sweep(now=self.t0 + timedelta(hours=1))
        states = [task.state for task in self.engine.tasks_for_lead(self.lead.lead_id)]

        self.assertIn(FollowupState.PENDING, states)
        self.assertTrue(any(v["code"] == "MISSING_PENDING_TASK" for v in self.engine.violations()))

    def test_overdue_detection_and_escalation_pipeline(self) -> None:
        self.engine.register_lead(self.lead, now=self.t0)

        events = self.engine.process_due_transitions(now=self.t0 + timedelta(hours=53))
        levels = [event.level.value for event in events]

        self.assertIn("reminder", levels)
        self.assertIn("warning", levels)
        self.assertIn("escalated", levels)
        self.assertIn("reassigned", levels)

    def test_enforcement_blocks_close_with_unresolved_tasks(self) -> None:
        self.engine.register_lead(self.lead, now=self.t0)

        with self.assertRaises(FollowupPolicyError):
            self.engine.request_close_lead(self.lead.lead_id, closure_reason="lost", now=self.t0 + timedelta(hours=1))

    def test_state_model_and_metrics(self) -> None:
        self.engine.register_lead(self.lead, now=self.t0)
        self.engine.log_activity(self.lead.lead_id, activity_id="act-1", now=self.t0 + timedelta(hours=2))

        tasks = self.engine.tasks_for_lead(self.lead.lead_id)
        self.assertIn(FollowupState.COMPLETED, [task.state for task in tasks])
        self.assertIn(FollowupState.PENDING, [task.state for task in tasks])

        metrics = self.engine.metrics()
        self.assertGreaterEqual(metrics.compliance_percent, 50.0)
        self.assertEqual(metrics.overdue_percent, 0.0)


if __name__ == "__main__":
    unittest.main()
