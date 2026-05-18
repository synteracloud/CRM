"""Self-QC checks for ticket SLA + lifecycle implementation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ticket_management import TICKET_STATUS_SEQUENCE, Ticket, TicketService


def run_self_qc() -> tuple[int, list[str]]:
    checks: list[tuple[str, bool]] = []

    checks.append(("status sequence includes all required states", TICKET_STATUS_SEQUENCE == ("open", "in_progress", "resolved", "closed")))

    service = TicketService()
    ticket = Ticket(
        ticket_id="qc-1",
        tenant_id="tenant-1",
        account_id="acc-1",
        contact_id="con-1",
        owner_user_id="user-1",
        subject="Self QC",
        description="Ticket lifecycle validation",
        priority="medium",
        status="open",
        created_at="2026-03-26T00:00:00Z",
        response_due_at="2026-03-26T01:00:00Z",
        resolution_due_at="2026-03-26T05:00:00Z",
    )
    service.create_ticket(ticket)
    service.record_first_response("qc-1", "2026-03-26T00:30:00Z")
    service.start_progress("qc-1")
    service.resolve_ticket("qc-1", "2026-03-26T04:00:00Z")
    service.close_ticket("qc-1", "2026-03-26T04:30:00Z")
    checks.append(("full lifecycle open→in_progress→resolved→closed succeeds", True))

    service2 = TicketService()
    service2.create_ticket(ticket.patch(ticket_id="qc-2"))
    breached = False
    try:
        service2.record_first_response("qc-2", "2026-03-26T01:30:00Z")
    except ValueError:
        breached = True
    checks.append(("response SLA breach is enforced", breached))

    passed = [name for name, ok in checks if ok]
    score = int(round((len(passed) / len(checks)) * 10))
    failed = [name for name, ok in checks if not ok]
    return score, failed


if __name__ == "__main__":
    score, failed = run_self_qc()
    print(f"SELF_QC_SCORE={score}/10")
    if failed:
        for item in failed:
            print(f"FAILED: {item}")
