from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from services.workflow import ActionDefinition, ActionType, RuleCondition, TriggerType, WorkflowEngine, WorkflowEvent, WorkflowRule


class WorkflowAutomationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = WorkflowEngine()
        self.t0 = datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc)

        self.engine.register_rule(
            WorkflowRule(
                rule_id="lead_high_priority",
                trigger=TriggerType.LEAD_CREATED,
                conditions=(RuleCondition(field="priority", operator="eq", value="high"),),
                actions=(
                    ActionDefinition("msg-welcome", ActionType.SEND_MESSAGE, {"template": "welcome_high_priority"}),
                    ActionDefinition("task-followup", ActionType.CREATE_TASK, {"title": "Call lead in 15 minutes"}),
                ),
            )
        )
        self.engine.register_rule(
            WorkflowRule(
                rule_id="payment_reconcile",
                trigger=TriggerType.PAYMENT_RECEIVED,
                conditions=(RuleCondition(field="amount", operator="gte", value=100),),
                actions=(ActionDefinition("stage-paid", ActionType.UPDATE_STAGE, {"stage": "paid"}),),
            )
        )
        self.engine.register_rule(
            WorkflowRule(
                rule_id="inactive_reengage",
                trigger=TriggerType.INACTIVITY,
                conditions=(RuleCondition(field="days_inactive", operator="gte", value=7),),
                actions=(ActionDefinition("msg-reengage", ActionType.SEND_MESSAGE, {"template": "reengage_7d"}),),
            )
        )

    def test_all_supported_triggers_execute_actions(self) -> None:
        lead_results = self.engine.ingest_event(
            WorkflowEvent(
                event_id="evt-1",
                tenant_id="tenant-a",
                trigger=TriggerType.LEAD_CREATED,
                occurred_at=self.t0,
                payload={"priority": "high"},
            ),
            now=self.t0,
        )
        payment_results = self.engine.ingest_event(
            WorkflowEvent(
                event_id="evt-2",
                tenant_id="tenant-a",
                trigger=TriggerType.PAYMENT_RECEIVED,
                occurred_at=self.t0 + timedelta(minutes=1),
                payload={"amount": 300},
            ),
            now=self.t0 + timedelta(minutes=1),
        )
        inactivity_results = self.engine.ingest_event(
            WorkflowEvent(
                event_id="evt-3",
                tenant_id="tenant-a",
                trigger=TriggerType.INACTIVITY,
                occurred_at=self.t0 + timedelta(minutes=2),
                payload={"days_inactive": 10},
            ),
            now=self.t0 + timedelta(minutes=2),
        )

        self.assertEqual(len(lead_results), 1)
        self.assertEqual(len(payment_results), 1)
        self.assertEqual(len(inactivity_results), 1)
        action_types = [entry["action_type"] for entry in self.engine.action_log()]
        self.assertIn("send_message", action_types)
        self.assertIn("create_task", action_types)
        self.assertIn("update_stage", action_types)

    def test_rule_engine_conditions_and_missed_automation_detection(self) -> None:
        # Does not match threshold rule, should be detected as missed after grace period.
        self.engine.ingest_event(
            WorkflowEvent(
                event_id="evt-4",
                tenant_id="tenant-a",
                trigger=TriggerType.PAYMENT_RECEIVED,
                occurred_at=self.t0,
                payload={"amount": 50},
            ),
            now=self.t0,
        )

        missed = self.engine.detect_missed_automations(now=self.t0 + timedelta(hours=1))
        self.assertEqual(len(missed), 1)
        self.assertEqual(missed[0].event_id, "evt-4")

    def test_qc_alignment_reaches_ten_on_ten(self) -> None:
        self.engine.ingest_event(
            WorkflowEvent(
                event_id="evt-5",
                tenant_id="tenant-a",
                trigger=TriggerType.LEAD_CREATED,
                occurred_at=self.t0,
                payload={"priority": "high"},
            ),
            now=self.t0,
        )
        self.engine.ingest_event(
            WorkflowEvent(
                event_id="evt-6",
                tenant_id="tenant-a",
                trigger=TriggerType.PAYMENT_RECEIVED,
                occurred_at=self.t0 + timedelta(minutes=1),
                payload={"amount": 120},
            ),
            now=self.t0 + timedelta(minutes=1),
        )

        report = self.engine.qc_report(now=self.t0 + timedelta(hours=1))

        self.assertEqual(report.trigger_reliability_percent, 100.0)
        self.assertEqual(report.missed_automations, 0)
        self.assertEqual(report.alignment_percent, 100.0)
        self.assertEqual(report.score, "10/10")


if __name__ == "__main__":
    unittest.main()
