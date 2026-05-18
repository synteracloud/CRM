from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from services.activation import ActivationOrchestrator, ActivationState


class ActivationEngineTests(unittest.TestCase):
    def test_bootstrap_creates_defaults_and_sample_data(self) -> None:
        orchestrator = ActivationOrchestrator()
        started_at = datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc)

        snapshot = orchestrator.start("tenant-a", now=started_at)

        self.assertEqual(snapshot.pipeline.name, "Sales Pipeline")
        self.assertEqual(snapshot.pipeline.stages, ("New", "Qualified", "Proposal", "Negotiation", "Won"))
        self.assertEqual(snapshot.session.inbox_channel, "WhatsApp Primary")
        self.assertEqual(len(snapshot.contacts), 5)
        self.assertEqual(len(snapshot.deals), 4)
        self.assertTrue(all(prompt.optional for prompt in snapshot.prompts))
        self.assertEqual(snapshot.session.state, ActivationState.SAMPLE_DATA_READY)

    def test_onboarding_flow_reaches_aha_and_tracks_first_conversion(self) -> None:
        orchestrator = ActivationOrchestrator()
        started_at = datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc)
        snapshot = orchestrator.start("tenant-a", now=started_at)

        orchestrator.simulate_whatsapp_inbound("tenant-a", contact_id=snapshot.contacts[0].contact_id, now=started_at + timedelta(minutes=2))
        orchestrator.move_deal_stage("tenant-a", deal_id=snapshot.deals[0].deal_id, to_stage="Qualified", now=started_at + timedelta(minutes=6))

        metrics = orchestrator.metrics("tenant-a")
        qc = orchestrator.review_agent_qc("tenant-a")
        event_names = [event["name"] for event in orchestrator.events()]

        self.assertEqual(metrics.time_to_aha_seconds, 360.0)
        self.assertTrue(qc["value_under_10_minutes"])
        self.assertEqual(qc["score"], "10/10")
        self.assertIn("first_conversion_tracked", event_names)


if __name__ == "__main__":
    unittest.main()
