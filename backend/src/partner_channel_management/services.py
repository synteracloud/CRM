"""Services implementing partner model, attribution rules, and channel flows."""

from __future__ import annotations

from collections import defaultdict

from .entities import (
    DealRegistration,
    OpportunityRecord,
    Partner,
    PartnerAttribution,
    PartnerChannelError,
    PartnerChannelNotFoundError,
    PartnerRelationship,
)


class PartnerChannelService:
    def __init__(self) -> None:
        self._partners: dict[str, Partner] = {}
        self._partner_code_index: dict[tuple[str, str], str] = {}
        self._relationships: dict[str, PartnerRelationship] = {}
        self._opportunities: dict[str, OpportunityRecord] = {}
        self._deal_registrations: dict[str, DealRegistration] = {}
        self._attributions: dict[str, PartnerAttribution] = {}

    def create_partner(self, partner: Partner) -> Partner:
        if partner.partner_id in self._partners:
            raise PartnerChannelError(f"Partner already exists: {partner.partner_id}")
        key = (partner.tenant_id, partner.partner_code.lower())
        if key in self._partner_code_index:
            raise PartnerChannelError(
                f"Partner code already exists in tenant={partner.tenant_id}: {partner.partner_code}"
            )
        self._partners[partner.partner_id] = partner
        self._partner_code_index[key] = partner.partner_id
        return partner

    def register_opportunity(self, opportunity: OpportunityRecord) -> OpportunityRecord:
        if opportunity.opportunity_id in self._opportunities:
            raise PartnerChannelError(f"Opportunity already exists: {opportunity.opportunity_id}")
        self._opportunities[opportunity.opportunity_id] = opportunity
        return opportunity

    def activate_relationship(self, relationship: PartnerRelationship) -> PartnerRelationship:
        if relationship.partner_id not in self._partners:
            raise PartnerChannelNotFoundError(f"Partner not found: {relationship.partner_id}")
        if relationship.partner_relationship_id in self._relationships:
            raise PartnerChannelError(f"Relationship exists: {relationship.partner_relationship_id}")
        if relationship.status != "active":
            raise PartnerChannelError("Relationship must be created as active.")
        self._relationships[relationship.partner_relationship_id] = relationship
        return relationship

    def register_deal(self, registration: DealRegistration) -> DealRegistration:
        if registration.partner_id not in self._partners:
            raise PartnerChannelNotFoundError(f"Partner not found: {registration.partner_id}")
        opportunity = self._require_opportunity(registration.opportunity_id)
        if opportunity.account_id != registration.account_id:
            raise PartnerChannelError("Deal registration account must match opportunity account.")
        for existing in self._deal_registrations.values():
            if (
                existing.tenant_id == registration.tenant_id
                and existing.account_id == registration.account_id
                and existing.partner_id == registration.partner_id
                and self._windows_overlap(
                    existing.registered_at,
                    existing.window_end_at,
                    registration.registered_at,
                    registration.window_end_at,
                )
            ):
                raise PartnerChannelError(
                    "Registration conflict: overlapping deal window for tenant/account/partner."
                )
        self._deal_registrations[registration.deal_registration_id] = registration
        return registration

    def add_candidate_attribution(self, attribution: PartnerAttribution) -> PartnerAttribution:
        if attribution.partner_id not in self._partners:
            raise PartnerChannelNotFoundError(f"Partner not found: {attribution.partner_id}")
        opportunity = self._require_opportunity(attribution.opportunity_id)
        if opportunity.account_id != attribution.account_id:
            raise PartnerChannelError("Attribution account must match opportunity account.")
        if attribution.attribution_status != "candidate":
            raise PartnerChannelError("Attribution must start in candidate state.")
        if not 0.0 <= attribution.attribution_weight <= 1.0:
            raise PartnerChannelError("attribution_weight must be between 0 and 1.")
        self._attributions[attribution.partner_attribution_id] = attribution
        return attribution

    def lock_attribution(self, tenant_id: str, opportunity_id: str, locked_at: str) -> list[PartnerAttribution]:
        opportunity = self._require_opportunity(opportunity_id)
        if opportunity.tenant_id != tenant_id:
            raise PartnerChannelError("Tenant mismatch for lock request.")

        candidates = [
            row
            for row in self._attributions.values()
            if row.tenant_id == tenant_id
            and row.opportunity_id == opportunity_id
            and row.attribution_status == "candidate"
        ]
        if not candidates:
            raise PartnerChannelError("No candidate attributions to lock.")

        by_model: dict[str, list[PartnerAttribution]] = defaultdict(list)
        for row in candidates:
            by_model[row.attribution_model].append(row)

        if len(by_model) != 1:
            raise PartnerChannelError("All candidate attributions must use the same attribution_model.")

        model = next(iter(by_model))
        chosen = self._resolve_model(model=model, candidates=by_model[model])

        locked: list[PartnerAttribution] = []
        chosen_ids = {row.partner_attribution_id for row in chosen}
        for row in candidates:
            if row.partner_attribution_id in chosen_ids:
                patched = row.patch(attribution_status="locked", locked_at=locked_at)
            else:
                patched = row.patch(attribution_status="released")
            self._attributions[row.partner_attribution_id] = patched
            if patched.attribution_status == "locked":
                locked.append(patched)

        if opportunity.owner_user_id != self._opportunities[opportunity_id].owner_user_id:
            raise PartnerChannelError("Ownership conflict detected: direct owner must remain unchanged.")
        return locked

    def list_opportunity_attributions(self, opportunity_id: str) -> list[PartnerAttribution]:
        return [row for row in self._attributions.values() if row.opportunity_id == opportunity_id]

    def get_opportunity(self, opportunity_id: str) -> OpportunityRecord:
        return self._require_opportunity(opportunity_id)

    def _resolve_model(self, model: str, candidates: list[PartnerAttribution]) -> list[PartnerAttribution]:
        ordered = sorted(candidates, key=lambda row: row.partner_attribution_id)
        if model == "first_touch":
            return ordered[:1]
        if model == "last_touch":
            return ordered[-1:]
        if model == "split":
            total_weight = round(sum(row.attribution_weight for row in candidates), 6)
            if total_weight != 1.0:
                raise PartnerChannelError(
                    f"Split attribution requires total active weight of 1.0, got {total_weight}"
                )
            return ordered
        raise PartnerChannelError(f"Unsupported attribution_model={model}")

    def _require_opportunity(self, opportunity_id: str) -> OpportunityRecord:
        opportunity = self._opportunities.get(opportunity_id)
        if not opportunity:
            raise PartnerChannelNotFoundError(f"Opportunity not found: {opportunity_id}")
        return opportunity

    @staticmethod
    def _windows_overlap(start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
        return max(start_a, start_b) <= min(end_a, end_b)
