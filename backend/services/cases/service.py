"""CasesService — state machine enforcement, SLA computation, business logic.

Domain spec: backend/docs/domain/cases-domain.md §3, §4, §6
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from services.cases.entities import (
    ALLOWED_TRANSITIONS,
    SLA_DEFAULTS,
    SLATier,
    CaseTransitionError,
    compute_sla_deadline,
    validate_transition,
)


class CasesService:
    """Stateless domain service for Case business rules."""

    # ── SLA ───────────────────────────────────────────────────────────────────

    def compute_sla_deadlines(self, created_at: datetime, sla_tier: str) -> dict:
        """Return sla_first_response_due_at and sla_resolution_due_at for the tier."""
        tier     = SLATier(sla_tier)
        defaults = SLA_DEFAULTS[tier]
        return {
            "sla_first_response_due_at": compute_sla_deadline(created_at, defaults["first_response_hours"]),
            "sla_resolution_due_at":     compute_sla_deadline(created_at, defaults["resolution_hours"]),
        }

    # ── State machine ─────────────────────────────────────────────────────────

    def apply_transition(
        self,
        current_status: str,
        target_status: str,
        *,
        has_resolution_comment: bool = False,
        resolution_confirmed_at: Optional[datetime] = None,
        actor_role: str = "agent",
    ) -> dict:
        """
        Validate transition and return a dict of field updates to apply.
        Raises CaseTransitionError on an invalid or guard-blocked transition.
        """
        validate_transition(current_status, target_status)

        now: datetime = datetime.now(timezone.utc)
        updates: dict = {"status": target_status, "updated_at": now}

        if target_status == "RESOLVED":
            # Guard: resolution comment required — spec §3.2
            if not has_resolution_comment:
                raise CaseTransitionError(
                    "Cannot resolve: at least one comment of type 'resolution' is required."
                )
            updates["resolved_at"] = now

        if target_status == "CLOSED":
            if current_status == "RESOLVED":
                if not resolution_confirmed_at:
                    updates["resolution_confirmed_at"] = now
            elif current_status not in ("WAITING_ON_CUSTOMER",):
                # Force-close without resolution — admin/manager only — spec §3.2
                if actor_role not in ("admin", "manager", "tenant_admin", "tenant_owner"):
                    raise CaseTransitionError(
                        "Force-close without resolution requires admin or manager role."
                    )
            updates["closed_at"] = now

        if target_status == "OPEN" and current_status == "CLOSED":
            # Reopen — clear closed/resolved timestamps; route layer increments reopen_count
            updates["resolved_at"]            = None
            updates["closed_at"]              = None
            updates["resolution_confirmed_at"] = None

        if target_status == "ESCALATED":
            updates["escalation_level"] = 1   # floor; route layer may override

        return updates

    # ── Escalation ladder ─────────────────────────────────────────────────────

    def evaluate_sla_escalation(
        self,
        case: dict,
        now: Optional[datetime] = None,
    ) -> Optional[dict]:
        """
        Evaluate SLA breach for a running case.
        Returns a dict with escalation_level and event_type if a new breach is found,
        or None if no new breach.

        Spec §4.2 + §6.1:
          Level 1 — first_response_due_at breached and first_responded_at is None
          Level 2 — resolution_due_at breached (any breach)
          Level 3 — resolution 50% past due
          Level 4 — resolution 100% past due
        """
        if now is None:
            now = datetime.now(timezone.utc)

        status = case.get("status", "OPEN")
        if status in ("RESOLVED", "CLOSED"):
            return None

        current_level: int = case.get("escalation_level", 0)
        new_level = current_level
        event_type: Optional[str] = None

        # Level 1 — first response breach
        first_due = case.get("sla_first_response_due_at")
        first_responded = case.get("first_responded_at")
        if first_due and not first_responded and now > first_due:
            if new_level < 1:
                new_level = 1
                event_type = "case.sla.first_response_breached.v1"

        # Level 2+ — resolution breach
        res_due = case.get("sla_resolution_due_at")
        if res_due and now > res_due:
            # How far past due as a fraction of the original window
            created_at = case.get("created_at")
            if created_at and isinstance(created_at, datetime):
                total_window = (res_due - created_at).total_seconds()
                overrun = (now - res_due).total_seconds()
                if total_window > 0:
                    pct_overrun = overrun / total_window
                    if pct_overrun >= 1.0 and new_level < 4:
                        new_level = 4
                        event_type = "case.sla.resolution_breached.v1"
                    elif pct_overrun >= 0.5 and new_level < 3:
                        new_level = 3
                        event_type = "case.sla.resolution_breached.v1"
                    elif new_level < 2:
                        new_level = 2
                        event_type = "case.sla.resolution_breached.v1"
                else:
                    if new_level < 2:
                        new_level = 2
                        event_type = "case.sla.resolution_breached.v1"

        if new_level > current_level:
            return {"escalation_level": new_level, "event_type": event_type}
        return None
