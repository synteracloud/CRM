"""Unit tests for Partners service: commission calculation, state machines, attribution.

Spec: backend/docs/domain/partners.md §1, §3, §4
Invariant: status=paid commission is immutable.
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from services.partners.entities import (
    COMMISSION_RATES,
    DEAL_REG_EXPIRY_DAYS,
    PartnerDomainError,
    calculate_commission,
    compute_expiry_date,
    validate_commission_transition,
    validate_partner_status_transition,
)
from services.partners.service import PartnersService


# ── calculate_commission ──────────────────────────────────────────────────────

class TestCalculateCommission:
    def test_platinum_15_percent(self):
        amount, rate = calculate_commission(1_000_000, "platinum")
        assert amount == 150_000.0
        assert rate   == 0.15

    def test_gold_10_percent(self):
        amount, rate = calculate_commission(500_000, "gold")
        assert amount == 50_000.0
        assert rate   == 0.10

    def test_silver_5_percent(self):
        amount, rate = calculate_commission(200_000, "silver")
        assert amount == 10_000.0
        assert rate   == 0.05

    def test_zero_amount(self):
        amount, rate = calculate_commission(0, "platinum")
        assert amount == 0.0

    def test_fractional_amount_rounded(self):
        amount, _ = calculate_commission(333_333, "gold")
        assert amount == round(333_333 * 0.10, 2)


# ── compute_expiry_date ───────────────────────────────────────────────────────

class TestComputeExpiryDate:
    def test_platinum_30_days(self):
        result = compute_expiry_date("2026-05-01T00:00:00Z", "platinum")
        assert result == "2026-05-31"

    def test_gold_45_days(self):
        result = compute_expiry_date("2026-05-01T00:00:00Z", "gold")
        assert result == "2026-06-15"

    def test_silver_no_expiry(self):
        result = compute_expiry_date("2026-05-01T00:00:00Z", "silver")
        assert result is None


# ── validate_commission_transition ────────────────────────────────────────────

class TestCommissionTransition:
    def test_pending_to_approved(self):
        validate_commission_transition("pending", "approved")  # no exception

    def test_approved_to_paid(self):
        validate_commission_transition("approved", "paid")

    def test_pending_to_disputed(self):
        validate_commission_transition("pending", "disputed")

    def test_paid_is_immutable(self):
        with pytest.raises(PartnerDomainError, match="immutable"):
            validate_commission_transition("paid", "disputed")

    def test_paid_to_anything_blocked(self):
        with pytest.raises(PartnerDomainError):
            validate_commission_transition("paid", "cancelled")

    def test_cancelled_is_terminal(self):
        with pytest.raises(PartnerDomainError):
            validate_commission_transition("cancelled", "pending")

    def test_approved_to_pending_blocked(self):
        with pytest.raises(PartnerDomainError):
            validate_commission_transition("approved", "pending")


# ── validate_partner_status_transition ───────────────────────────────────────

class TestPartnerStatusTransition:
    def test_active_to_inactive(self):
        validate_partner_status_transition("active", "inactive")

    def test_active_to_suspended(self):
        validate_partner_status_transition("active", "suspended")

    def test_inactive_to_active(self):
        validate_partner_status_transition("inactive", "active")

    def test_suspended_to_active(self):
        validate_partner_status_transition("suspended", "active")

    def test_inactive_to_suspended_blocked(self):
        with pytest.raises(PartnerDomainError):
            validate_partner_status_transition("inactive", "suspended")

    def test_active_to_active_blocked(self):
        with pytest.raises(PartnerDomainError):
            validate_partner_status_transition("active", "active")


# ── PartnersService.compute_commission_on_win ─────────────────────────────────

class TestComputeCommissionOnWin:
    svc = PartnersService()

    def test_builds_pending_commission(self):
        result = self.svc.compute_commission_on_win(
            opportunity_amount=1_000_000,
            partner_tier="gold",
            opportunity_id="opp-001",
            opportunity_name="Big Deal",
            partner_id="p-001",
            tenant_id="t-001",
        )
        assert result["status"] == "pending"
        assert result["amount"] == 100_000.0
        assert result["rate"]   == 0.10
        assert result["partner_id"]     == "p-001"
        assert result["opportunity_id"] == "opp-001"

    def test_silver_rate_applied(self):
        result = self.svc.compute_commission_on_win(
            opportunity_amount=200_000,
            partner_tier="silver",
            opportunity_id="opp-002",
            opportunity_name="Small Deal",
            partner_id="p-002",
            tenant_id="t-001",
        )
        assert result["amount"] == 10_000.0


# ── PartnersService.apply_commission_transition ───────────────────────────────

class TestApplyCommissionTransition:
    svc = PartnersService()

    def _commission(self, status="pending") -> dict:
        return {"commission_id": "com-001", "status": status, "amount": 50000}

    def test_approve_sets_approved_at(self):
        result = self.svc.apply_commission_transition(
            self._commission("pending"), "approved", actor_id="u-001"
        )
        assert result["status"]      == "approved"
        assert result["approved_by"] == "u-001"
        assert result["approved_at"] is not None

    def test_pay_requires_reference(self):
        with pytest.raises(PartnerDomainError, match="reference"):
            self.svc.apply_commission_transition(
                self._commission("approved"), "paid"
            )

    def test_pay_sets_paid_at_and_reference(self):
        result = self.svc.apply_commission_transition(
            self._commission("approved"), "paid", payment_reference="TRF-001"
        )
        assert result["status"]            == "paid"
        assert result["payment_reference"] == "TRF-001"
        assert result["paid_at"] is not None

    def test_paid_commission_immutable(self):
        with pytest.raises(PartnerDomainError, match="immutable"):
            self.svc.apply_commission_transition(self._commission("paid"), "disputed")


# ── PartnersService.validate_attribution ─────────────────────────────────────

class TestValidateAttribution:
    svc = PartnersService()

    def test_active_partner_ok(self):
        self.svc.validate_attribution({"status": "active"})

    def test_inactive_partner_blocked(self):
        with pytest.raises(PartnerDomainError, match="inactive"):
            self.svc.validate_attribution({"status": "inactive"})

    def test_suspended_partner_blocked(self):
        with pytest.raises(PartnerDomainError, match="suspended"):
            self.svc.validate_attribution({"status": "suspended"})


# ── PartnersService.build_deal_registration ───────────────────────────────────

class TestBuildDealRegistration:
    svc = PartnersService()

    def _partner(self, tier="platinum") -> dict:
        return {"partner_id": "p-001", "partner_tier": tier, "status": "active"}

    def test_platinum_has_30_day_expiry(self):
        reg = self.svc.build_deal_registration(
            self._partner("platinum"), "ABC Corp", 500_000, "t-001",
            submitted_at_iso="2026-06-01T00:00:00Z"
        )
        assert reg["expiry_date"] == "2026-07-01"

    def test_gold_has_45_day_expiry(self):
        reg = self.svc.build_deal_registration(
            self._partner("gold"), "XYZ Ltd", 200_000, "t-001",
            submitted_at_iso="2026-06-01T00:00:00Z"
        )
        assert reg["expiry_date"] == "2026-07-16"

    def test_silver_no_expiry(self):
        reg = self.svc.build_deal_registration(
            self._partner("silver"), "Mini Corp", 50_000, "t-001",
            submitted_at_iso="2026-06-01T00:00:00Z"
        )
        assert reg["expiry_date"] is None

    def test_initial_status_is_submitted(self):
        reg = self.svc.build_deal_registration(
            self._partner(), "Test Corp", 100_000, "t-001"
        )
        assert reg["status"] == "submitted"
