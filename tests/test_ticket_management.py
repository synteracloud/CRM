from __future__ import annotations

import unittest

from src.ticket_management import Ticket, TicketApi, TicketService


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

    def test_api_envelopes_and_endpoints(self) -> None:
        service = TicketService()
        api = TicketApi(service)
        created = api.create_ticket(self._ticket(), request_id="req-1")
        self.assertEqual(created["meta"]["request_id"], "req-1")
        self.assertIn("data", created)

        transitioned = api.start_progress("t-1", request_id="req-2")
        self.assertEqual(transitioned["data"]["status"], "in_progress")

        not_found = api.get_ticket("missing", request_id="req-3")
        self.assertEqual(not_found["error"]["code"], "not_found")


if __name__ == "__main__":
    unittest.main()
