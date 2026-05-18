from __future__ import annotations

import unittest

from services.sync import SyncService


class SyncServiceTests(unittest.TestCase):
    def test_offline_queue_and_reconnect_sync(self) -> None:
        sync = SyncService(max_retries=3)
        sync.set_connectivity(False)

        sync.enqueue_action("lead", "lead-1", "update", {"stage": "qualified"})
        self.assertEqual(len(sync.queue_snapshot()), 1)
        self.assertIsNone(sync.get_entity("lead", "lead-1"))

        sync.set_connectivity(True)
        entity = sync.get_entity("lead", "lead-1")

        self.assertIsNotNone(entity)
        assert entity is not None
        self.assertEqual(entity.data["stage"], "qualified")
        self.assertEqual(len(sync.queue_snapshot()), 0)

    def test_retry_and_dead_letter_for_network_errors(self) -> None:
        sync = SyncService(max_retries=2)
        sync.set_connectivity(False)
        sync.enqueue_action("contact", "c-1", "update", {"simulate_network_error": True})

        sync.set_connectivity(True)
        self.assertEqual(len(sync.queue_snapshot()), 1)

        sync.sync_pending()
        self.assertEqual(len(sync.queue_snapshot()), 0)

        dead_letter_count = len([h for h in sync.history() if h.status == "dead_letter"])
        self.assertEqual(dead_letter_count, 1)

        report = sync.reliability_report()
        self.assertTrue(report.data_loss_risk)

    def test_conflict_last_write_wins(self) -> None:
        sync = SyncService(conflict_policy="last_write_wins")
        sync.enqueue_action("deal", "d-1", "create", {"amount": 100}, base_version=0)

        current = sync.get_entity("deal", "d-1")
        assert current is not None
        stale_version = current.version - 1

        sync.enqueue_action("deal", "d-1", "update", {"amount": 125}, base_version=stale_version)
        updated = sync.get_entity("deal", "d-1")

        assert updated is not None
        self.assertEqual(updated.data["amount"], 125)
        self.assertGreaterEqual(sync.reliability_report().conflict_count, 1)

    def test_qc_alignment_targets_10_on_healthy_sync(self) -> None:
        sync = SyncService()
        sync.enqueue_action("account", "a-1", "create", {"name": "Acme"})
        sync.enqueue_action("account", "a-1", "update", {"tier": "enterprise"}, base_version=1)

        report = sync.reliability_report()
        self.assertFalse(report.data_loss_risk)
        self.assertEqual(report.alignment_percent, 100.0)
        self.assertEqual(report.score, "10/10")


if __name__ == "__main__":
    unittest.main()
