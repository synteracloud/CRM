from __future__ import annotations

import unittest

from src.ticket_management import EscalationRule, SlaEscalationService, Ticket, TicketApi, TicketService


class TicketManagementTests(unittest.TestCase):
    def _ticket(self, ticket_id: str = "t-1") -> Ticket:
        return Ticket(
            ticket_id=ticket_id,
            tenant_id="tenant-1",
            account_id="acc-1",
            contact_id="con-1",
            owner_user_id="user-1",
            subject="Login issue",
            description="User cannot login",
            priority="high",
            status="open",
            created_at="2026-03-26T00:00:00Z",
            response_due_at="2026-03-26T01:00:00Z",
            resolution_due_at="2026-03-26T04:00:00Z",
        )

    def _rules(self) -> list[EscalationRule]:
        return [
            EscalationRule(
                rule_id="r1",
                tenant_id="tenant-1",
                level=1,
                name="Priority fast lane",
                route_to="support-team-l2",
                trigger="time_since_created",
                threshold_minutes=30,
                condition_field="priority",
                condition_op="eq",
                condition_value="high",
            ),
            EscalationRule(
                rule_id="r2",
                tenant_id="tenant-1",
                level=2,
                name="Response due breached",
                route_to="support-manager",
                trigger="response_due",
                threshold_minutes=0,
            ),
            EscalationRule(
                rule_id="r3",
                tenant_id="tenant-1",
                level=3,
                name="Resolution breached",
                route_to="incident-commander",
                trigger="resolution_due",
                threshold_minutes=0,
            ),
        ]

    def test_status_lifecycle_complete(self) -> None:
        service = TicketService()
        service.create_ticket(self._ticket())
        service.start_progress("t-1")
        service.resolve_ticket("t-1", resolved_at="2026-03-26T03:00:00Z")
        closed = service.close_ticket("t-1", closed_at="2026-03-26T03:30:00Z")
        self.assertEqual(closed.status, "closed")

    def test_sla_response_and_resolution_enforced(self) -> None:
        service = TicketService()
        service.create_ticket(self._ticket())
        service.start_progress("t-1")

        with self.assertRaisesRegex(ValueError, "Response SLA breached"):
            service.record_first_response("t-1", responded_at="2026-03-26T02:00:00Z")

        service.record_first_response("t-1", responded_at="2026-03-26T00:30:00Z")

        with self.assertRaisesRegex(ValueError, "Resolution SLA breached"):
            service.resolve_ticket("t-1", resolved_at="2026-03-26T05:00:00Z")

    def test_escalations_are_deterministic_and_routed(self) -> None:
        ticket_service = TicketService()
        ticket_service.create_ticket(self._ticket())
        escalation_service = SlaEscalationService(ticket_service)
        escalation_service.register_rules("tenant-1", self._rules())

        first = escalation_service.evaluate_escalations("t-1", now="2026-03-26T01:30:00Z")
        second = escalation_service.evaluate_escalations("t-1", now="2026-03-26T01:30:00Z")

        self.assertEqual([a.rule_id for a in first], ["r1", "r2"])
        self.assertEqual([a.route_to for a in first], ["support-team-l2", "support-manager"])
        self.assertEqual([(a.rule_id, a.route_to) for a in first], [(a.rule_id, a.route_to) for a in second])

    def test_breach_prediction_and_audit_paths_complete(self) -> None:
        ticket_service = TicketService()
        ticket_service.create_ticket(self._ticket())
        escalation_service = SlaEscalationService(ticket_service)
        escalation_service.register_rules("tenant-1", self._rules())

        prediction = escalation_service.predict_breach("t-1", now="2026-03-26T00:45:00Z", horizon_minutes=30)
        self.assertTrue(prediction["response_breach_likely"])
        self.assertFalse(prediction["resolution_breach_likely"])

        actions = escalation_service.evaluate_escalations("t-1", now="2026-03-26T04:30:00Z")
        self.assertEqual([a.rule_id for a in actions], ["r1", "r2", "r3"])

        audit = escalation_service.list_audit("t-1")
        event_types = [entry.event_type for entry in audit]
        self.assertIn("escalation.breach_prediction", event_types)
        self.assertIn("escalation.triggered", event_types)

    def test_api_envelopes_endpoints_and_escalation_contracts(self) -> None:
        ticket_service = TicketService()
        escalation_service = SlaEscalationService(ticket_service)
        api = TicketApi(ticket_service, escalation_service)

        created = api.create_ticket(self._ticket(), request_id="req-1")
        self.assertEqual(created["meta"]["request_id"], "req-1")

        rules_resp = api.register_escalation_rules("tenant-1", self._rules(), request_id="req-rules")
        self.assertEqual(len(rules_resp["data"]), 3)

        escalated = api.evaluate_escalation("t-1", now="2026-03-26T01:30:00Z", request_id="req-esc")
        self.assertEqual(escalated["data"][0]["route_to"], "support-team-l2")

        audit = api.list_escalation_audit("t-1", request_id="req-audit")
        self.assertGreaterEqual(len(audit["data"]), 1)


if __name__ == "__main__":
    unittest.main()
