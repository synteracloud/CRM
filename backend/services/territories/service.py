"""TerritoriesService — evaluation pipeline, conflict resolution, rep assignment.

Domain spec: backend/docs/domain/territory-management.md §3, §4, §5
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from services.territories.entities import (
    AssignmentReason,
    evaluate_territory,
)


class TerritoriesService:
    """Stateless service for Territory domain business rules."""

    # ── Evaluation pipeline ───────────────────────────────────────────────────

    def evaluate_subject(
        self,
        subject: dict,
        territories: list[dict],
        rules_by_territory: dict[str, list[dict]],
    ) -> list[dict]:
        """
        Evaluate subject against all active territories.
        Returns a ranked list of matching territory dicts (highest priority first).
        Spec §3.1.
        """
        candidates = []
        for t in territories:
            if not t.get("is_active", True):
                continue
            rules = rules_by_territory.get(t["territory_id"], [])
            if evaluate_territory(t, rules, subject):
                candidates.append(t)
        return self.resolve_conflict(candidates, rules_by_territory)

    # ── Conflict resolution ───────────────────────────────────────────────────

    def resolve_conflict(
        self,
        candidates: list[dict],
        rules_by_territory: dict[str, list[dict]] | None = None,
    ) -> list[dict]:
        """
        Sort candidates by: routing_priority ASC → rule_count DESC → territory_id ASC.
        Spec §5.1.
        """
        if not candidates:
            return []

        def sort_key(t: dict) -> tuple:
            priority   = t.get("routing_priority", 99)
            rule_count = len((rules_by_territory or {}).get(t["territory_id"], []))
            tid        = t.get("territory_id", "")
            return (priority, -rule_count, tid)   # -rule_count: more rules = higher specificity

        return sorted(candidates, key=sort_key)

    def select_winner(
        self,
        candidates: list[dict],
        rules_by_territory: dict[str, list[dict]] | None = None,
    ) -> tuple[Optional[dict], str]:
        """
        Return (winning_territory, resolution_reason) from a ranked candidate list.
        Returns (None, 'no_match') if no candidates.
        """
        ranked = self.resolve_conflict(candidates, rules_by_territory)
        if not ranked:
            return None, "no_match"
        if len(ranked) == 1:
            return ranked[0], "single_match"

        t0, t1 = ranked[0], ranked[1]
        if t0.get("routing_priority", 99) < t1.get("routing_priority", 99):
            reason = "priority_order"
        elif len((rules_by_territory or {}).get(t0["territory_id"], [])) > \
             len((rules_by_territory or {}).get(t1["territory_id"], [])):
            reason = "rule_specificity"
        else:
            reason = "uuid_tiebreak"
        return ranked[0], reason

    # ── Rep assignment ────────────────────────────────────────────────────────

    def assign_rep_round_robin(
        self,
        territory: dict,
        cursor: int = 0,
    ) -> Optional[str]:
        """
        Select rep from territory.assigned_reps using round-robin.
        Returns rep_id or None if no reps configured.
        Spec §4.1 — round_robin is default for v1.
        """
        reps = territory.get("assigned_reps") or []
        if not reps:
            return territory.get("primary_manager")  # fallback — spec §4.3
        return reps[cursor % len(reps)]

    # ── Assignment record builder ─────────────────────────────────────────────

    def build_assignment(
        self,
        tenant_id: str,
        subject_type: str,
        subject_id: str,
        territory: dict,
        rep_id: Optional[str],
        reason: str,
        created_by: Optional[str] = None,
    ) -> dict:
        """Build a TerritoryAssignment record dict ready for persistence."""
        now = datetime.now(timezone.utc)
        return {
            "assignment_id":    None,  # generated at persist time
            "tenant_id":        tenant_id,
            "subject_type":     subject_type,
            "subject_id":       subject_id,
            "territory_id":     territory["territory_id"],
            "assigned_rep_id":  rep_id,
            "assignment_reason": reason,
            "superseded_by":    None,
            "is_active":        True,
            "effective_at":     now.isoformat(),
            "created_by":       created_by,
            "created_at":       now.isoformat(),
        }

    # ── Manual reassignment ───────────────────────────────────────────────────

    def validate_manual_override(
        self,
        current_assignment: dict,
        actor_role: str,
    ) -> None:
        """
        Validate that a manual reassignment is permitted.
        Managers can only reassign within their own territories.
        Admins can reassign anything.
        Raises ValueError on denial.
        Spec §5.3.
        """
        if actor_role not in ("manager", "admin", "tenant_admin", "tenant_owner"):
            raise ValueError("Manual territory reassignment requires manager or admin role.")

    def is_manually_assigned(self, assignment: dict) -> bool:
        """
        Return True if the current active assignment was a manual override.
        Manual overrides are sticky — not overridden by next auto-routing run.
        Spec §5.3.
        """
        return assignment.get("assignment_reason") == AssignmentReason.MANUAL_OVERRIDE
