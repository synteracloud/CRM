"""PartnersService — commission logic, attribution rules, state transitions.

Domain spec: backend/docs/domain/partners.md §3, §4
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from services.partners.entities import (
    CommissionStatus,
    PartnerDomainError,
    calculate_commission,
    compute_expiry_date,
    validate_commission_transition,
    validate_partner_status_transition,
)


class PartnersService:
    """Stateless domain service for Partner business rules."""

    # ── Commission ────────────────────────────────────────────────────────────

    def compute_commission_on_win(
        self,
        opportunity_amount: float,
        partner_tier: str,
        opportunity_id: str,
        opportunity_name: str,
        partner_id: str,
        tenant_id: str,
    ) -> dict:
        """
        Build a PartnerCommission record dict when an opportunity is won.
        Spec §4.1: triggered by Opportunity.is_won = true with attributed_partner_id set.
        """
        amount, rate = calculate_commission(opportunity_amount, partner_tier)
        now = datetime.now(timezone.utc)
        return {
            "commission_id":    None,   # generated at persist time
            "partner_id":       partner_id,
            "tenant_id":        tenant_id,
            "opportunity_id":   opportunity_id,
            "opportunity_name": opportunity_name,
            "amount":           amount,
            "rate":             rate,
            "status":           CommissionStatus.PENDING,
            "calculated_at":    now.isoformat(),
            "approved_at":      None,
            "approved_by":      None,
            "paid_at":          None,
            "payment_reference": None,
            "dispute_reason":   None,
            "created_at":       now.isoformat(),
            "updated_at":       now.isoformat(),
        }

    def apply_commission_transition(
        self,
        commission: dict,
        target_status: str,
        *,
        actor_id: Optional[str] = None,
        payment_reference: Optional[str] = None,
    ) -> dict:
        """
        Validate and apply a commission status transition.
        Raises PartnerDomainError on immutability or invalid transition.
        """
        validate_commission_transition(commission["status"], target_status)

        now = datetime.now(timezone.utc)
        updates: dict = {"status": target_status, "updated_at": now}

        if target_status == CommissionStatus.APPROVED:
            updates["approved_at"] = now
            updates["approved_by"] = actor_id

        if target_status == CommissionStatus.PAID:
            if not payment_reference:
                raise PartnerDomainError(
                    "Payment reference is required when recording commission payment."
                )
            updates["paid_at"]           = now
            updates["payment_reference"] = payment_reference

        return updates

    # ── Attribution ───────────────────────────────────────────────────────────

    def validate_attribution(self, partner: dict) -> None:
        """
        Validate that a partner can receive attribution.
        Raises PartnerDomainError if partner is inactive or suspended.
        Spec §1.3 rule 4.
        """
        if partner.get("status") != "active":
            raise PartnerDomainError(
                f"Cannot attribute opportunity to {partner.get('status')!r} partner. "
                "Partner must be active."
            )

    # ── Deal registration ─────────────────────────────────────────────────────

    def build_deal_registration(
        self,
        partner: dict,
        prospect_name: str,
        estimated_value: float,
        tenant_id: str,
        submitted_at_iso: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Build a DealRegistration record dict. Computes expiry date from tier."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        submitted_at = submitted_at_iso or now.isoformat()
        expiry_date  = compute_expiry_date(submitted_at, partner["partner_tier"])

        return {
            "registration_id":    None,
            "partner_id":         partner["partner_id"],
            "tenant_id":          tenant_id,
            "opportunity_id":     None,
            "prospect_name":      prospect_name,
            "prospect_phone":     kwargs.get("prospect_phone"),
            "prospect_email":     kwargs.get("prospect_email"),
            "estimated_value":    estimated_value,
            "expected_close_date":kwargs.get("expected_close_date"),
            "status":             "submitted",
            "submitted_at":       submitted_at,
            "reviewed_at":        None,
            "reviewed_by":        None,
            "rejection_reason":   None,
            "expiry_date":        expiry_date,
            "notes":              kwargs.get("notes"),
            "created_at":         submitted_at,
            "updated_at":         submitted_at,
        }

    # ── Partner status ────────────────────────────────────────────────────────

    def apply_status_transition(
        self,
        current_status: str,
        target_status: str,
    ) -> dict:
        """Validate and return field updates for a partner status change."""
        validate_partner_status_transition(current_status, target_status)
        return {"status": target_status, "updated_at": datetime.now(timezone.utc)}
