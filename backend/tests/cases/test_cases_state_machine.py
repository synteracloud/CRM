"""Unit tests for Case state machine and SLA computation.

Spec: backend/docs/domain/cases-domain.md §3, §4
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from services.cases.entities import (
    ALLOWED_TRANSITIONS,
    CaseTransitionError,
    SLATier,
    compute_sla_deadline,
    validate_transition,
)
from services.cases.service import CasesService


# ── Helpers ───────────────────────────────────────────────────────────────────

def _utc(*args) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)


# ── validate_transition ───────────────────────────────────────────────────────

class TestValidateTransition:
    def test_open_to_assigned_allowed(self):
        validate_transition("OPEN", "ASSIGNED")  # no exception

    def test_open_to_in_progress_blocked(self):
        with pytest.raises(CaseTransitionError, match="not permitted"):
            validate_transition("OPEN", "IN_PROGRESS")

    def test_assigned_to_escalated_allowed(self):
        validate_transition("ASSIGNED", "ESCALATED")

    def test_resolved_to_closed_allowed(self):
        validate_transition("RESOLVED", "CLOSED")

    def test_closed_to_open_allowed(self):
        validate_transition("CLOSED", "OPEN")

    def test_closed_to_in_progress_blocked(self):
        with pytest.raises(CaseTransitionError):
            validate_transition("CLOSED", "IN_PROGRESS")

    def test_all_allowed_transitions_pass(self):
        for from_s, targets in ALLOWED_TRANSITIONS.items():
            for to_s in targets:
                validate_transition(from_s, to_s)  # no exception

    def test_invalid_status_raises(self):
        with pytest.raises(CaseTransitionError):
            validate_transition("NONEXISTENT", "OPEN")


# ── CasesService.apply_transition ─────────────────────────────────────────────

class TestApplyTransition:
    svc = CasesService()

    def test_resolve_without_comment_raises(self):
        with pytest.raises(CaseTransitionError, match="resolution"):
            self.svc.apply_transition("IN_PROGRESS", "RESOLVED", has_resolution_comment=False)

    def test_resolve_with_comment_succeeds(self):
        result = self.svc.apply_transition("IN_PROGRESS", "RESOLVED", has_resolution_comment=True)
        assert result["status"] == "RESOLVED"
        assert result["resolved_at"] is not None

    def test_force_close_requires_admin(self):
        with pytest.raises(CaseTransitionError, match="admin or manager"):
            self.svc.apply_transition("ASSIGNED", "CLOSED", actor_role="agent")

    def test_force_close_admin_allowed(self):
        result = self.svc.apply_transition("ASSIGNED", "CLOSED", actor_role="admin")
        assert result["status"] == "CLOSED"

    def test_reopen_clears_timestamps(self):
        result = self.svc.apply_transition("CLOSED", "OPEN")
        assert result["resolved_at"] is None
        assert result["closed_at"] is None
        assert result["resolution_confirmed_at"] is None

    def test_escalated_sets_escalation_level(self):
        result = self.svc.apply_transition("IN_PROGRESS", "ESCALATED")
        assert result["escalation_level"] == 1

    def test_close_from_resolved_sets_confirmation(self):
        result = self.svc.apply_transition("RESOLVED", "CLOSED", resolution_confirmed_at=None)
        assert result["resolution_confirmed_at"] is not None
        assert result["closed_at"] is not None


# ── compute_sla_deadline ──────────────────────────────────────────────────────

class TestComputeSlaDeadline:
    def test_1_hour_within_business_day(self):
        # Wednesday 09:00 PKT = Tuesday 04:00 UTC
        start = _utc(2026, 5, 27, 4, 0, 0)   # 09:00 PKT Wed
        deadline = compute_sla_deadline(start, 1)
        # Expect 10:00 PKT Wed = 05:00 UTC
        assert deadline == _utc(2026, 5, 27, 5, 0, 0)

    def test_deadline_skips_after_hours(self):
        # Wednesday 18:00 PKT (1h before close) + 2h = crosses into Thursday 10:00 PKT
        start = _utc(2026, 5, 27, 13, 0, 0)  # 18:00 PKT Wed
        deadline = compute_sla_deadline(start, 2)
        # 1h fills Wed (18:00→19:00), 1h continues Thu (09:00→10:00)
        assert deadline == _utc(2026, 5, 28, 5, 0, 0)  # 10:00 PKT Thu = 05:00 UTC

    def test_deadline_skips_sunday(self):
        # Saturday 18:30 PKT + 1h should land Monday 09:30 PKT
        start = _utc(2026, 5, 30, 13, 30, 0)  # 18:30 PKT Sat
        deadline = compute_sla_deadline(start, 1)
        # 30min fills Sat (18:30→19:00), remaining 30min on Mon (09:00→09:30)
        assert deadline == _utc(2026, 6, 1, 4, 30, 0)   # 09:30 PKT Mon = 04:30 UTC

    def test_24h_tier_low_spans_multiple_days(self):
        # Start Monday 09:00 PKT, 24 business hours = 3 business days (8h each) + end of day 3
        start = _utc(2026, 5, 25, 4, 0, 0)  # 09:00 PKT Mon
        deadline = compute_sla_deadline(start, 24)
        # 10h/day × 3 days = 30h; 24h = Mon full + Tue full + Wed 04:00 = 09:00 + 4h → 13:00 PKT Wed
        assert deadline.weekday() in (0, 1, 2, 3, 4, 5)  # not Sunday
        assert deadline > start + timedelta(hours=24)

    def test_returns_utc_aware(self):
        start = _utc(2026, 5, 27, 4, 0, 0)
        deadline = compute_sla_deadline(start, 1)
        assert deadline.tzinfo is not None


# ── CasesService.compute_sla_deadlines ────────────────────────────────────────

class TestComputeSlaDeadlines:
    svc = CasesService()

    def test_tier_1_first_response_1h(self):
        start = _utc(2026, 5, 27, 4, 0, 0)  # 09:00 PKT
        result = self.svc.compute_sla_deadlines(start, "tier_1_critical")
        assert result["sla_first_response_due_at"] == _utc(2026, 5, 27, 5, 0, 0)

    def test_tier_3_first_response_8h(self):
        start = _utc(2026, 5, 27, 4, 0, 0)  # 09:00 PKT Mon
        result = self.svc.compute_sla_deadlines(start, "tier_3_standard")
        # 8 business hours from 09:00 = 17:00 PKT same day (9h window per day)
        due = result["sla_first_response_due_at"]
        assert due > start
        assert due < start + timedelta(days=2)

    def test_invalid_tier_raises(self):
        with pytest.raises(ValueError):
            self.svc.compute_sla_deadlines(_utc(2026, 5, 27, 4, 0, 0), "tier_99_bogus")


# ── CasesService.evaluate_sla_escalation ──────────────────────────────────────

class TestEvaluateSlaEscalation:
    svc = CasesService()

    def _case(self, status="IN_PROGRESS", level=0, first_due=None, res_due=None, responded=None, created=None):
        now = datetime.now(timezone.utc)
        return {
            "status":                   status,
            "escalation_level":         level,
            "sla_first_response_due_at": first_due,
            "sla_resolution_due_at":     res_due,
            "first_responded_at":        responded,
            "created_at":                created or (now - timedelta(hours=10)),
        }

    def test_no_breach_returns_none(self):
        now = datetime.now(timezone.utc)
        case = self._case(first_due=now + timedelta(hours=2), res_due=now + timedelta(hours=10))
        assert self.svc.evaluate_sla_escalation(case, now=now) is None

    def test_first_response_breach_returns_level_1(self):
        now = datetime.now(timezone.utc)
        case = self._case(first_due=now - timedelta(minutes=30), responded=None)
        result = self.svc.evaluate_sla_escalation(case, now=now)
        assert result is not None
        assert result["escalation_level"] == 1

    def test_already_responded_no_breach(self):
        now = datetime.now(timezone.utc)
        case = self._case(first_due=now - timedelta(hours=1), responded=now - timedelta(minutes=30))
        result = self.svc.evaluate_sla_escalation(case, now=now)
        assert result is None

    def test_resolved_case_skipped(self):
        now = datetime.now(timezone.utc)
        case = self._case(status="RESOLVED", first_due=now - timedelta(hours=2))
        assert self.svc.evaluate_sla_escalation(case, now=now) is None
