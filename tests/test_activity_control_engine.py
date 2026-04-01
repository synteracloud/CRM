from __future__ import annotations

import unittest

from services.activity import ActivityControlEngine, ActorContext, EntityRecord, OwnershipError, PolicyDeniedError


class ActivityControlEngineTests(unittest.TestCase):
    def _owner(self) -> ActorContext:
        return ActorContext(actor_id="usr-owner", actor_name="Owner", actor_role="sales_rep", team_id="team-a")

    def _manager(self) -> ActorContext:
        return ActorContext(actor_id="usr-mgr", actor_name="Manager", actor_role="sales_manager", team_id="team-a")

    def _intruder(self) -> ActorContext:
        return ActorContext(actor_id="usr-other", actor_name="Intruder", actor_role="sales_rep", team_id="team-z")

    def _entity(self) -> EntityRecord:
        return EntityRecord(
            tenant_id="ten-1",
            entity_type="lead",
            entity_id="lead-1",
            owner_id="usr-owner",
            owner_team_id="team-a",
            last_activity_at="2026-04-01T00:00:00Z",
        )

    def test_mutations_are_logged_with_immutable_audit_chain(self) -> None:
        engine = ActivityControlEngine()
        engine.register_entity(self._entity(), self._owner(), request_id="req-create", trace_id="trc-create")

        updated = engine.mutate_entity(
            "lead",
            "lead-1",
            self._owner(),
            {"state": "qualified"},
            request_id="req-update",
            trace_id="trc-update",
        )

        self.assertEqual(updated.state, "qualified")
        self.assertEqual(len(engine.activity_feed("ten-1")), 2)
        audit = engine.audit_log()
        self.assertEqual(len(audit), 2)
        self.assertEqual(audit[1].chain_seq, 2)
        self.assertTrue(audit[1].prev_hash.startswith("sha256:"))

    def test_ownership_enforcement_denies_non_owner_and_emits_misuse_alert(self) -> None:
        engine = ActivityControlEngine(misuse_denied_threshold=2)
        engine.register_entity(self._entity(), self._owner(), request_id="req-create", trace_id="trc-create")

        with self.assertRaises(PolicyDeniedError):
            engine.mutate_entity("lead", "lead-1", self._intruder(), {"owner_team_id": "team-a"}, "req-1", "trc-1")
        with self.assertRaises(PolicyDeniedError):
            engine.mutate_entity("lead", "lead-1", self._intruder(), {"owner_team_id": "team-a"}, "req-2", "trc-2")

        misuse_alerts = [a for a in engine.alerts() if a.alert_type == "misuse"]
        self.assertGreaterEqual(len(misuse_alerts), 1)

    def test_transfer_requires_reason_and_records_history(self) -> None:
        engine = ActivityControlEngine()
        engine.register_entity(self._entity(), self._owner(), request_id="req-create", trace_id="trc-create")

        with self.assertRaises(OwnershipError):
            engine.transfer_ownership(
                "lead",
                "lead-1",
                self._manager(),
                to_owner_id="usr-new",
                to_team_id="team-a",
                reason_code="",
                reason_note="",
                request_id="req-transfer",
                trace_id="trc-transfer",
            )

        transfer = engine.transfer_ownership(
            "lead",
            "lead-1",
            self._manager(),
            to_owner_id="usr-new",
            to_team_id="team-a",
            reason_code="capacity_rebalance",
            reason_note="Rebalancing queue",
            request_id="req-transfer-2",
            trace_id="trc-transfer-2",
        )
        self.assertEqual(transfer.status, "approved")
        self.assertEqual(len(engine.ownership_history("lead", "lead-1")), 1)

    def test_visibility_queries_and_review_agent_alignment(self) -> None:
        engine = ActivityControlEngine(inactivity_hours=1)
        engine.register_entity(self._entity(), self._owner(), request_id="req-create", trace_id="trc-create")
        engine.mutate_entity("lead", "lead-1", self._owner(), {"owner_team_id": "team-a"}, "req-upd", "trc-upd")

        owner_ledger = engine.user_activity_ledger("ten-1", "usr-owner")
        self.assertEqual(len(owner_ledger), 2)

        alerts = engine.detect_and_emit_alerts(now="2030-04-01T03:00:00Z")
        self.assertTrue(any(a.alert_type == "inactivity" for a in alerts))

        report = engine.review_agent_report()
        self.assertTrue(report["traceability_complete"])
        self.assertEqual(report["alignment_percent"], 100.0)
        self.assertEqual(report["score"], "10/10")


if __name__ == "__main__":
    unittest.main()
