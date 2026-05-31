"""Unit tests for InboxService: assignment pipeline, claim/handoff guards, presence.

Spec: backend/docs/domain/shared-inbox.md §3, §4
"""
from __future__ import annotations

import pytest

from services.inbox.entities import (
    INTENT_QUEUE_MAP,
    is_eligible_for_auto_assign,
    is_eligible_to_claim,
)
from services.inbox.service import InboxAssignmentError, InboxService


# ── Helpers ───────────────────────────────────────────────────────────────────

def _presence(status="online", count=0, max_c=10) -> dict:
    return {"agent_id": "u-001", "status": status, "open_conversation_count": count, "max_concurrent": max_c}


def _queue(strategy="round_robin", auto=True) -> dict:
    return {"queue_id": "q-001", "name": "General", "routing_strategy": strategy, "auto_assign": auto, "is_active": True}


def _conv(assigned=None) -> dict:
    return {"conversation_id": "c-001", "tenant_id": "t-001", "assigned_agent_id": assigned, "state": "open"}


# ── is_eligible_for_auto_assign ───────────────────────────────────────────────

class TestAutoAssignEligibility:
    def test_online_under_capacity_eligible(self):
        assert is_eligible_for_auto_assign(_presence("online", 3, 10)) is True

    def test_away_not_eligible(self):
        assert is_eligible_for_auto_assign(_presence("away")) is False

    def test_busy_not_eligible(self):
        assert is_eligible_for_auto_assign(_presence("busy")) is False

    def test_at_capacity_not_eligible(self):
        assert is_eligible_for_auto_assign(_presence("online", 10, 10)) is False

    def test_over_capacity_not_eligible(self):
        assert is_eligible_for_auto_assign(_presence("online", 11, 10)) is False


# ── is_eligible_to_claim ──────────────────────────────────────────────────────

class TestClaimEligibility:
    def test_online_can_claim(self):
        assert is_eligible_to_claim(_presence("online")) is True

    def test_away_can_claim(self):
        assert is_eligible_to_claim(_presence("away")) is True

    def test_busy_cannot_claim(self):
        assert is_eligible_to_claim(_presence("busy")) is False

    def test_offline_cannot_claim(self):
        assert is_eligible_to_claim(_presence("offline")) is False

    def test_away_at_capacity_cannot_claim(self):
        assert is_eligible_to_claim(_presence("away", 10, 10)) is False


# ── InboxService.resolve_queue ────────────────────────────────────────────────

class TestResolveQueue:
    svc = InboxService()
    queues = [
        {"queue_id": "q-001", "name": "Sales",   "is_active": True},
        {"queue_id": "q-002", "name": "Billing",  "is_active": True},
        {"queue_id": "q-003", "name": "Support",  "is_active": True},
        {"queue_id": "q-004", "name": "General",  "is_active": True},
    ]

    def test_lead_inquiry_routes_to_sales(self):
        q = self.svc.resolve_queue("lead_inquiry", self.queues)
        assert q["name"] == "Sales"

    def test_payment_query_routes_to_billing(self):
        q = self.svc.resolve_queue("payment_query", self.queues)
        assert q["name"] == "Billing"

    def test_support_request_routes_to_support(self):
        q = self.svc.resolve_queue("support_request", self.queues)
        assert q["name"] == "Support"

    def test_unknown_intent_falls_back_to_first_active(self):
        q = self.svc.resolve_queue("nonsense", self.queues)
        assert q is not None  # falls back to first active

    def test_no_matching_and_no_active_returns_none(self):
        q = self.svc.resolve_queue("lead_inquiry", [])
        assert q is None


# ── InboxService.auto_assign ──────────────────────────────────────────────────

class TestAutoAssign:
    svc = InboxService()

    def test_round_robin_selects_eligible(self):
        presence = [_presence("online", 2, 10), _presence("online", 3, 10)]
        presence[0]["agent_id"] = "u-001"
        presence[1]["agent_id"] = "u-002"
        agent_id = self.svc.auto_assign(_queue("round_robin"), presence, 0)
        assert agent_id in ("u-001", "u-002")

    def test_least_loaded_selects_lowest_count(self):
        p1 = {**_presence("online", 8, 10), "agent_id": "u-high"}
        p2 = {**_presence("online", 1, 10), "agent_id": "u-low"}
        agent_id = self.svc.auto_assign(_queue("least_loaded"), [p1, p2])
        assert agent_id == "u-low"

    def test_no_eligible_returns_none(self):
        presence = [_presence("offline"), _presence("busy", 10, 10)]
        assert self.svc.auto_assign(_queue(), presence) is None

    def test_auto_assign_false_returns_none(self):
        presence = [_presence("online")]
        assert self.svc.auto_assign(_queue(auto=False), presence) is None


# ── InboxService.validate_claim ───────────────────────────────────────────────

class TestValidateClaim:
    svc = InboxService()

    def test_unassigned_online_agent_can_claim(self):
        self.svc.validate_claim(_conv(assigned=None), "u-001", _presence("online"))  # no exception

    def test_already_assigned_raises(self):
        with pytest.raises(InboxAssignmentError, match="already assigned"):
            self.svc.validate_claim(_conv(assigned="u-999"), "u-001", _presence("online"))

    def test_offline_agent_cannot_claim(self):
        with pytest.raises(InboxAssignmentError, match="not eligible"):
            self.svc.validate_claim(_conv(assigned=None), "u-001", _presence("offline"))

    def test_busy_agent_cannot_claim(self):
        with pytest.raises(InboxAssignmentError, match="not eligible"):
            self.svc.validate_claim(_conv(assigned=None), "u-001", _presence("busy"))

    def test_at_capacity_cannot_claim(self):
        with pytest.raises(InboxAssignmentError, match="not eligible"):
            self.svc.validate_claim(_conv(assigned=None), "u-001", _presence("online", 10, 10))


# ── InboxService.validate_handoff ─────────────────────────────────────────────

class TestValidateHandoff:
    svc = InboxService()

    def test_assigned_agent_can_hand_off(self):
        conv = _conv(assigned="u-001")
        self.svc.validate_handoff(conv, "u-001", "agent")  # no exception

    def test_supervisor_can_hand_off_any(self):
        conv = _conv(assigned="u-999")
        self.svc.validate_handoff(conv, "u-001", "manager")  # no exception

    def test_non_assigned_agent_cannot_hand_off(self):
        conv = _conv(assigned="u-999")
        with pytest.raises(InboxAssignmentError, match="assigned agent or a supervisor"):
            self.svc.validate_handoff(conv, "u-001", "agent")

    def test_admin_can_hand_off_any(self):
        conv = _conv(assigned="u-999")
        self.svc.validate_handoff(conv, "u-001", "admin")  # no exception


# ── InboxService.compute_presence_after_conversation_change ───────────────────

class TestPresenceCompute:
    svc = InboxService()

    def test_increment_below_max_no_busy(self):
        result = self.svc.compute_presence_after_conversation_change(3, 10, +1)
        assert result["open_conversation_count"] == 4
        assert result["suggested_status"] is None

    def test_increment_to_max_suggests_busy(self):
        result = self.svc.compute_presence_after_conversation_change(9, 10, +1)
        assert result["open_conversation_count"] == 10
        assert result["suggested_status"] == "busy"

    def test_decrement_does_not_go_negative(self):
        result = self.svc.compute_presence_after_conversation_change(0, 10, -1)
        assert result["open_conversation_count"] == 0
