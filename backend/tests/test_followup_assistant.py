from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from services.followup import LeadSnapshot, SmartFollowupAssistant


class SmartFollowupAssistantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assistant = SmartFollowupAssistant()
        self.now = datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc)

    def test_stage_based_suggestion_contains_template_and_timing(self) -> None:
        lead = LeadSnapshot(
            lead_id="lead-1",
            tenant_id="tenant-1",
            owner_id="owner-1",
            status="open",
            priority="warm",
            stage="discovery",
            last_activity_at=self.now - timedelta(hours=1),
        )

        suggestion = self.assistant.suggest_followup(lead, now=self.now)

        self.assertEqual(suggestion.template_key, "discovery_probe")
        self.assertEqual(suggestion.next_followup_at, self.now + timedelta(hours=8))
        self.assertGreaterEqual(suggestion.confidence_percent, 90.0)

    def test_inactivity_detection_forces_fast_reengagement(self) -> None:
        lead = LeadSnapshot(
            lead_id="lead-2",
            tenant_id="tenant-1",
            owner_id="owner-1",
            status="open",
            priority="cold",
            stage="proposal",
            last_activity_at=self.now - timedelta(hours=72),
        )

        suggestion = self.assistant.suggest_followup(lead, now=self.now)

        self.assertEqual(suggestion.reason, "inactivity_threshold_exceeded")
        self.assertEqual(suggestion.next_followup_at, self.now + timedelta(minutes=15))
        self.assertEqual(suggestion.template_key, "inactivity_reengage")

    def test_auto_task_creation_ensures_pending_followups(self) -> None:
        leads = [
            LeadSnapshot(
                lead_id="lead-3",
                tenant_id="tenant-1",
                owner_id="owner-1",
                status="open",
                priority="hot",
                stage="new",
                last_activity_at=self.now - timedelta(hours=2),
            ),
            LeadSnapshot(
                lead_id="lead-4",
                tenant_id="tenant-1",
                owner_id="owner-2",
                status="working",
                priority="warm",
                stage="proposal",
                last_activity_at=self.now - timedelta(hours=3),
            ),
        ]

        created = self.assistant.auto_create_followup_tasks(leads, now=self.now)

        self.assertEqual(created, 2)
        for lead in leads:
            tasks = self.assistant.engine.tasks_for_lead(lead.lead_id)
            self.assertTrue(any(task.state.value == "pending" for task in tasks))

    def test_qc_alignment_report_hits_ten_on_ten_for_covered_dataset(self) -> None:
        leads = [
            LeadSnapshot(
                lead_id="lead-5",
                tenant_id="tenant-1",
                owner_id="owner-3",
                status="open",
                priority="warm",
                stage="discovery",
                last_activity_at=self.now - timedelta(hours=1),
            ),
            LeadSnapshot(
                lead_id="lead-6",
                tenant_id="tenant-1",
                owner_id="owner-4",
                status="nurture",
                priority="cold",
                stage="proposal",
                last_activity_at=self.now - timedelta(hours=2),
            ),
        ]

        report = self.assistant.qc_alignment_report(leads, now=self.now)

        self.assertEqual(report.no_idle_leads_percent, 100.0)
        self.assertEqual(report.suggestion_accuracy_percent, 100.0)
        self.assertEqual(report.overall_alignment_percent, 100.0)


if __name__ == "__main__":
    unittest.main()
