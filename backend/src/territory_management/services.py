"""Territory model, assignment logic, and security-aware ownership resolution."""

from __future__ import annotations

from dataclasses import asdict

from .entities import (
    AmbiguousOwnershipError,
    PrincipalContext,
    SecurityBoundaryError,
    Territory,
    TerritoryAssignment,
    TerritoryError,
    TerritoryNotFoundError,
    TerritoryRule,
)


class TerritoryManagementService:
    """In-memory service implementing deterministic territory assignment rules."""

    def __init__(self) -> None:
        self._territories: dict[str, Territory] = {}
        self._rules: dict[str, TerritoryRule] = {}
        self._assignments: dict[tuple[str, str, str], TerritoryAssignment] = {}

    def create_territory(self, territory: Territory) -> Territory:
        if territory.territory_id in self._territories:
            raise TerritoryError(f"Territory already exists: {territory.territory_id}")
        if territory.parent_territory_id:
            parent = self._territories.get(territory.parent_territory_id)
            if not parent:
                raise TerritoryNotFoundError(f"Parent territory not found: {territory.parent_territory_id}")
            if parent.tenant_id != territory.tenant_id:
                raise SecurityBoundaryError("Cross-tenant hierarchy is not allowed.")
            if territory.level != parent.level + 1:
                raise TerritoryError("Territory hierarchy levels must increment by one per parent-child relation.")
        self._territories[territory.territory_id] = territory
        return territory

    def list_territories(self, tenant_id: str) -> list[Territory]:
        return [t for t in self._territories.values() if t.tenant_id == tenant_id]

    def register_rule(self, rule: TerritoryRule) -> TerritoryRule:
        territory = self._territories.get(rule.territory_id)
        if not territory:
            raise TerritoryNotFoundError(f"Territory not found: {rule.territory_id}")
        if territory.tenant_id != rule.tenant_id:
            raise SecurityBoundaryError("Rule tenant must match territory tenant.")
        if rule.rule_id in self._rules:
            raise TerritoryError(f"Rule already exists: {rule.rule_id}")

        for existing in self._rules.values():
            same_scope = (
                existing.tenant_id == rule.tenant_id
                and existing.subject_type == rule.subject_type
                and existing.priority == rule.priority
                and existing.criteria == rule.criteria
            )
            if same_scope:
                raise AmbiguousOwnershipError(
                    "Overlapping territory rules with equal precedence are not allowed."
                )

        self._rules[rule.rule_id] = rule
        return rule

    def assign_subject(
        self,
        *,
        principal: PrincipalContext,
        subject_type: str,
        subject_id: str,
        subject_facts: dict[str, str],
        assigned_at: str,
    ) -> TerritoryAssignment:
        if "records.update" not in principal.permissions:
            raise SecurityBoundaryError("Principal lacks records.update permission.")
        if subject_facts.get("tenant_id") != principal.tenant_id:
            raise SecurityBoundaryError("Principal cannot assign records outside tenant boundary.")

        winner = self._select_best_rule(
            tenant_id=principal.tenant_id,
            subject_type=subject_type,
            subject_facts=subject_facts,
        )
        assignment = TerritoryAssignment(
            assignment_id=f"asgn-{subject_type}-{subject_id}",
            tenant_id=principal.tenant_id,
            subject_type=subject_type,
            subject_id=subject_id,
            territory_id=winner.territory_id,
            owner_type=winner.owner_type,
            owner_id=winner.owner_id,
            assignment_rule=winner.rule_id,
            assigned_at=assigned_at,
        )
        self._assignments[(principal.tenant_id, subject_type, subject_id)] = assignment
        return assignment

    def get_assignment(self, *, principal: PrincipalContext, subject_type: str, subject_id: str) -> TerritoryAssignment:
        assignment = self._assignments.get((principal.tenant_id, subject_type, subject_id))
        if not assignment:
            raise TerritoryNotFoundError(f"Assignment not found: {subject_type}/{subject_id}")
        self._check_read_scope(principal, assignment)
        return assignment

    def get_coverage(self, *, principal: PrincipalContext, territory_id: str) -> dict[str, object]:
        territory = self._territories.get(territory_id)
        if not territory:
            raise TerritoryNotFoundError(f"Territory not found: {territory_id}")
        if territory.tenant_id != principal.tenant_id:
            raise SecurityBoundaryError("Principal cannot access cross-tenant territory coverage.")

        if "records.read" not in principal.permissions:
            raise SecurityBoundaryError("Principal lacks records.read permission.")

        lineage = []
        cursor: Territory | None = territory
        while cursor:
            lineage.append(cursor.territory_id)
            cursor = self._territories.get(cursor.parent_territory_id) if cursor.parent_territory_id else None

        active_assignments = [
            asdict(a)
            for a in self._assignments.values()
            if a.tenant_id == principal.tenant_id and a.territory_id in lineage
        ]
        return {
            "territory_id": territory_id,
            "lineage": tuple(lineage),
            "covered_subject_count": len(active_assignments),
            "assignments": active_assignments,
        }

    def _select_best_rule(self, *, tenant_id: str, subject_type: str, subject_facts: dict[str, str]) -> TerritoryRule:
        matched = [
            rule
            for rule in self._rules.values()
            if rule.tenant_id == tenant_id
            and rule.subject_type == subject_type
            and all(subject_facts.get(k) == v for k, v in rule.criteria.items())
        ]
        if not matched:
            raise TerritoryNotFoundError(f"No matching territory rule for {subject_type}.")

        ranked = sorted(
            matched,
            key=lambda r: (
                -r.priority,
                -len(r.criteria),
                r.rule_id,
            ),
        )
        return ranked[0]

    def _check_read_scope(self, principal: PrincipalContext, assignment: TerritoryAssignment) -> None:
        if assignment.tenant_id != principal.tenant_id:
            raise SecurityBoundaryError("Cross-tenant access denied.")
        if "records.read" not in principal.permissions:
            raise SecurityBoundaryError("Principal lacks records.read permission.")

        if principal.role in {"Tenant Owner", "Tenant Admin", "Auditor", "Analyst"}:
            return
        if principal.role == "Manager" and assignment.owner_type == "team" and assignment.owner_id in principal.team_ids:
            return
        if principal.role == "Agent" and assignment.owner_type == "user" and assignment.owner_id == principal.user_id:
            return

        raise SecurityBoundaryError("Principal scope does not permit this record assignment.")
