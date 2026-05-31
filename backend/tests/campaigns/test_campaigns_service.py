"""Unit tests for CampaignsService: state machine, guards, attribution, rates.

Spec: backend/docs/domain/marketing-campaigns.md §3, §5, §6
P-017: Urdu approval gate tested explicitly.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from services.campaigns.entities import (
    ALLOWED_TRANSITIONS,
    CampaignTransitionError,
    validate_activation_guards,
    validate_transition,
)
from services.campaigns.service import CampaignsService


def _utc(*args) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)


def _campaign(status="draft", segment_id="seg-001", template_id="tpl-001", urdu_approved=None) -> dict:
    return {
        "campaign_id":          "cmp-001",
        "status":               status,
        "type":                 "whatsapp_broadcast",
        "segment_id":           segment_id,
        "template_id":          template_id,
        "urdu_approved_by":     urdu_approved,
        "attribution_window_days": 30,
        "sent_count":           100,
        "delivered_count":      90,
        "opened_count":         60,
        "replied_count":        20,
        "opted_out_count":      5,
    }


def _template(is_urdu=False, meta_status="approved") -> dict:
    return {
        "template_id":          "tpl-001",
        "channel":              "whatsapp_broadcast",
        "is_urdu":              is_urdu,
        "meta_template_status": meta_status,
    }


# ── validate_transition ───────────────────────────────────────────────────────

class TestValidateTransition:
    def test_draft_to_active_allowed(self):
        validate_transition("draft", "active")

    def test_draft_to_scheduled_allowed(self):
        validate_transition("draft", "scheduled")

    def test_active_to_paused_allowed(self):
        validate_transition("active", "paused")

    def test_paused_to_active_allowed(self):
        validate_transition("paused", "active")

    def test_completed_is_terminal(self):
        with pytest.raises(CampaignTransitionError, match="not permitted"):
            validate_transition("completed", "active")

    def test_cancelled_is_terminal(self):
        with pytest.raises(CampaignTransitionError):
            validate_transition("cancelled", "draft")

    def test_draft_to_completed_blocked(self):
        with pytest.raises(CampaignTransitionError):
            validate_transition("draft", "completed")

    def test_all_allowed_pass(self):
        for from_s, targets in ALLOWED_TRANSITIONS.items():
            for to_s in targets:
                validate_transition(from_s, to_s)


# ── validate_activation_guards ────────────────────────────────────────────────

class TestActivationGuards:
    def test_no_segment_blocked(self):
        c = _campaign(segment_id=None)
        with pytest.raises(CampaignTransitionError, match="segment_id"):
            validate_activation_guards(c, segment_size=10)

    def test_no_template_blocked(self):
        c = _campaign(template_id=None)
        with pytest.raises(CampaignTransitionError, match="template_id"):
            validate_activation_guards(c, segment_size=10)

    def test_zero_segment_size_blocked(self):
        c = _campaign()
        with pytest.raises(CampaignTransitionError, match="0 eligible"):
            validate_activation_guards(c, segment_size=0)

    def test_urdu_without_approval_blocked_p017(self):
        c = _campaign(urdu_approved=None)
        t = _template(is_urdu=True)
        with pytest.raises(CampaignTransitionError, match="P-017"):
            validate_activation_guards(c, template=t, segment_size=100)

    def test_urdu_with_approval_passes(self):
        c = _campaign(urdu_approved="u-001")
        t = _template(is_urdu=True)
        validate_activation_guards(c, template=t, segment_size=100)  # no exception

    def test_whatsapp_rejected_template_blocked(self):
        c = _campaign()
        t = _template(meta_status="rejected")
        with pytest.raises(CampaignTransitionError, match="meta_template_status"):
            validate_activation_guards(c, template=t, segment_size=100)

    def test_whatsapp_approved_template_passes(self):
        c = _campaign()
        t = _template(meta_status="approved")
        validate_activation_guards(c, template=t, segment_size=100)  # no exception


# ── CampaignsService.apply_transition ─────────────────────────────────────────

class TestApplyTransition:
    svc = CampaignsService()

    def test_activate_sets_activated_at(self):
        c = _campaign("draft")
        t = _template()
        result = self.svc.apply_transition(c, "active", template=t, segment_size=50)
        assert result["status"] == "active"
        assert result["activated_at"] is not None

    def test_schedule_requires_scheduled_at(self):
        c = _campaign("draft")
        with pytest.raises(CampaignTransitionError, match="scheduled_at"):
            self.svc.apply_transition(c, "scheduled", template=_template(), segment_size=50)

    def test_schedule_with_date_passes(self):
        c = _campaign("draft")
        future = datetime.now(timezone.utc) + timedelta(days=1)
        result = self.svc.apply_transition(c, "scheduled", template=_template(), segment_size=50, scheduled_at=future)
        assert result["scheduled_at"] == future

    def test_pause_sets_paused_at(self):
        c = _campaign("active")
        result = self.svc.apply_transition(c, "paused")
        assert result["paused_at"] is not None

    def test_cancel_sets_cancelled_at(self):
        c = _campaign("active")
        result = self.svc.apply_transition(c, "cancelled")
        assert result["cancelled_at"] is not None

    def test_reschedule_clears_scheduled_at(self):
        c = _campaign("scheduled")
        result = self.svc.apply_transition(c, "draft")
        assert result["scheduled_at"] is None


# ── CampaignsService: opt-in gate ─────────────────────────────────────────────

class TestShouldSkipContact:
    svc = CampaignsService()

    def test_opted_in_whatsapp_not_skipped(self):
        contact = {"whatsapp_opted_in": True, "phone_e164": "+923001234567"}
        assert self.svc.should_skip_contact(contact, "whatsapp_broadcast") is None

    def test_not_opted_in_skipped(self):
        contact = {"whatsapp_opted_in": False, "phone_e164": "+923001234567"}
        assert self.svc.should_skip_contact(contact, "whatsapp_broadcast") == "not_opted_in"

    def test_no_phone_skipped(self):
        contact = {"whatsapp_opted_in": True}
        assert self.svc.should_skip_contact(contact, "whatsapp_broadcast") == "no_channel"

    def test_email_no_email_skipped(self):
        contact = {}
        assert self.svc.should_skip_contact(contact, "email") == "no_channel"

    def test_email_with_email_not_skipped(self):
        contact = {"email": "test@example.com"}
        assert self.svc.should_skip_contact(contact, "email") is None


# ── CampaignsService: merge tags ──────────────────────────────────────────────

class TestMergeTags:
    svc = CampaignsService()

    def test_resolves_name_tag(self):
        result = self.svc.resolve_merge_tags("Hello {{contact.name}}!", {"display_name": "Tariq"})
        assert result == "Hello Tariq!"

    def test_resolves_company_tag(self):
        result = self.svc.resolve_merge_tags("From {{contact.company}}", {"account_name": "Acme Ltd"})
        assert result == "From Acme Ltd"

    def test_missing_field_uses_default(self):
        result = self.svc.resolve_merge_tags("Hello {{contact.name}}", {})
        assert result == "Hello Valued Customer"


# ── CampaignsService: attribution ────────────────────────────────────────────

class TestAttribution:
    svc = CampaignsService()

    def test_within_window_true(self):
        send_at  = _utc(2026, 5, 1, 9, 0, 0)
        event_at = _utc(2026, 5, 20, 9, 0, 0)
        assert self.svc.is_within_attribution_window(send_at, event_at, 30) is True

    def test_outside_window_false(self):
        send_at  = _utc(2026, 5, 1, 9, 0, 0)
        event_at = _utc(2026, 6, 5, 9, 0, 0)
        assert self.svc.is_within_attribution_window(send_at, event_at, 30) is False

    def test_lead_created_conversion_type(self):
        assert self.svc.determine_conversion_type("lead") == "lead_created"

    def test_opportunity_won_conversion_type(self):
        assert self.svc.determine_conversion_type("opportunity", is_won=True) == "opportunity_won"

    def test_opportunity_created_conversion_type(self):
        assert self.svc.determine_conversion_type("opportunity", is_won=False) == "opportunity_created"


# ── CampaignsService: compute_rates ──────────────────────────────────────────

class TestComputeRates:
    svc = CampaignsService()

    def test_rates_computed_correctly(self):
        c = _campaign()
        rates = self.svc.compute_rates(c)
        assert rates["delivery_rate"] == 90.0
        assert rates["open_rate"]     == 60.0
        assert rates["reply_rate"]    == 20.0

    def test_zero_sent_returns_zeros(self):
        c = {**_campaign(), "sent_count": 0}
        rates = self.svc.compute_rates(c)
        assert rates["delivery_rate"] == 0
        assert rates["open_rate"]     == 0
