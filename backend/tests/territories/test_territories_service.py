"""Unit tests for Territory service: rule evaluation, conflict resolution, rep assignment.

Spec: backend/docs/domain/territory-management.md §3, §4, §5
"""
from __future__ import annotations

import pytest

from services.territories.entities import (
    evaluate_rule,
    evaluate_territory,
)
from services.territories.service import TerritoriesService


# ── Helpers ───────────────────────────────────────────────────────────────────

def _rule(rule_type, operator=None, value=None, field=None) -> dict:
    return {"rule_id": "r-001", "rule_type": rule_type, "operator": operator, "field": field, "value": value or {}}


def _territory(tid="t-001", priority=1, is_default=False, reps=None) -> dict:
    return {
        "territory_id":   tid,
        "name":           f"Territory {tid}",
        "is_active":      True,
        "routing_priority": priority,
        "is_default":     is_default,
        "assigned_reps":  reps or ["u-001"],
        "primary_manager":"u-mgr",
    }


# ── evaluate_rule: city ───────────────────────────────────────────────────────

class TestEvalRuleCity:
    def test_city_in_list_matches(self):
        rule = _rule("city", "in", {"cities": ["Lahore", "Karachi"]})
        assert evaluate_rule(rule, {"city": "Lahore"}) is True

    def test_city_case_insensitive(self):
        rule = _rule("city", "in", {"cities": ["lahore"]})
        assert evaluate_rule(rule, {"city": "LAHORE"}) is True

    def test_city_not_in_list(self):
        rule = _rule("city", "in", {"cities": ["Lahore"]})
        assert evaluate_rule(rule, {"city": "Peshawar"}) is False

    def test_city_not_in_operator(self):
        rule = _rule("city", "not_in", {"cities": ["Lahore"]})
        assert evaluate_rule(rule, {"city": "Karachi"}) is True


# ── evaluate_rule: postal_code ────────────────────────────────────────────────

class TestEvalRulePostal:
    def test_exact_match(self):
        rule = _rule("postal_code", "eq", {"codes": ["54000"]})
        assert evaluate_rule(rule, {"postal_code": "54000"}) is True

    def test_starts_with_match(self):
        rule = _rule("postal_code", "starts_with", {"codes": ["546"]})
        assert evaluate_rule(rule, {"postal_code": "54680"}) is True

    def test_starts_with_no_match(self):
        rule = _rule("postal_code", "starts_with", {"codes": ["75"]})
        assert evaluate_rule(rule, {"postal_code": "54680"}) is False


# ── evaluate_rule: region ─────────────────────────────────────────────────────

class TestEvalRuleRegion:
    def test_province_matches(self):
        rule = _rule("region", "in", {"provinces": ["Punjab", "Sindh"]})
        assert evaluate_rule(rule, {"province": "Punjab"}) is True

    def test_province_case_insensitive(self):
        rule = _rule("region", "in", {"provinces": ["punjab"]})
        assert evaluate_rule(rule, {"province": "PUNJAB"}) is True

    def test_province_no_match(self):
        rule = _rule("region", "in", {"provinces": ["Punjab"]})
        assert evaluate_rule(rule, {"province": "KPK"}) is False

    def test_region_fallback_field(self):
        rule = _rule("region", "in", {"provinces": ["Sindh"]})
        assert evaluate_rule(rule, {"region": "sindh"}) is True


# ── evaluate_rule: special cases ──────────────────────────────────────────────

class TestEvalRuleSpecial:
    def test_geo_polygon_always_false_in_v1(self):
        rule = _rule("geo_polygon", "geo_within", {"polygon": [[24.86, 67.01]]})
        assert evaluate_rule(rule, {"latitude": 24.86, "longitude": 67.01}) is False

    def test_rep_explicit_always_true(self):
        rule = _rule("rep_explicit", value={"rep_ids": ["u-001"]})
        assert evaluate_rule(rule, {}) is True

    def test_account_tier_matches(self):
        rule = _rule("account_tier", "in", {"tiers": ["enterprise", "mid_market"]})
        assert evaluate_rule(rule, {"tier": "enterprise"}) is True

    def test_custom_field_eq(self):
        rule = _rule("custom_field", "eq", {"key": "channel", "match_values": ["distributor"]})
        assert evaluate_rule(rule, {"custom_fields": {"channel": "distributor"}}) is True

    def test_custom_field_missing_key(self):
        rule = _rule("custom_field", "eq", {"key": "channel", "match_values": ["distributor"]})
        assert evaluate_rule(rule, {"custom_fields": {}}) is False


# ── evaluate_territory ────────────────────────────────────────────────────────

class TestEvalTerritory:
    def test_empty_rules_always_match(self):
        assert evaluate_territory(_territory(), [], {"city": "anywhere"}) is True

    def test_all_rules_must_match(self):
        rules = [
            _rule("region", "in", {"provinces": ["Punjab"]}),
            _rule("city",   "in", {"cities": ["Lahore"]}),
        ]
        assert evaluate_territory(_territory(), rules, {"province": "Punjab", "city": "Lahore"}) is True

    def test_one_rule_fails_territory_fails(self):
        rules = [
            _rule("region", "in", {"provinces": ["Punjab"]}),
            _rule("city",   "in", {"cities": ["Lahore"]}),
        ]
        assert evaluate_territory(_territory(), rules, {"province": "Punjab", "city": "Multan"}) is False


# ── TerritoriesService.resolve_conflict ───────────────────────────────────────

class TestResolveConflict:
    svc = TerritoriesService()

    def test_single_candidate_returned(self):
        c = [_territory("t-001", 1)]
        assert self.svc.resolve_conflict(c) == c

    def test_priority_order_ascending(self):
        c = [_territory("t-002", 5), _territory("t-001", 1)]
        ranked = self.svc.resolve_conflict(c)
        assert ranked[0]["territory_id"] == "t-001"

    def test_tie_prefers_more_rules(self):
        t1 = _territory("t-001", 1)
        t2 = _territory("t-002", 1)
        rules = {"t-001": [{"rule_id": "r1"}], "t-002": [{"rule_id": "r2"}, {"rule_id": "r3"}]}
        ranked = self.svc.resolve_conflict([t1, t2], rules)
        assert ranked[0]["territory_id"] == "t-002"  # more specific

    def test_tie_uuid_tiebreak(self):
        t1 = _territory("aaaa", 1)
        t2 = _territory("bbbb", 1)
        ranked = self.svc.resolve_conflict([t2, t1], {})
        assert ranked[0]["territory_id"] == "aaaa"


# ── TerritoriesService.select_winner ─────────────────────────────────────────

class TestSelectWinner:
    svc = TerritoriesService()

    def test_no_candidates_returns_none(self):
        winner, reason = self.svc.select_winner([])
        assert winner is None
        assert reason == "no_match"

    def test_single_winner(self):
        winner, reason = self.svc.select_winner([_territory()])
        assert winner is not None
        assert reason == "single_match"

    def test_conflict_resolved_reason(self):
        c = [_territory("t-002", 5), _territory("t-001", 1)]
        winner, reason = self.svc.select_winner(c)
        assert winner["territory_id"] == "t-001"
        assert reason in ("priority_order", "rule_specificity", "uuid_tiebreak")


# ── TerritoriesService.assign_rep_round_robin ─────────────────────────────────

class TestAssignRep:
    svc = TerritoriesService()

    def test_single_rep_always_assigned(self):
        t = _territory(reps=["u-001"])
        assert self.svc.assign_rep_round_robin(t, 0) == "u-001"
        assert self.svc.assign_rep_round_robin(t, 1) == "u-001"

    def test_round_robin_cycles(self):
        t = _territory(reps=["u-001", "u-002", "u-003"])
        assert self.svc.assign_rep_round_robin(t, 0) == "u-001"
        assert self.svc.assign_rep_round_robin(t, 1) == "u-002"
        assert self.svc.assign_rep_round_robin(t, 2) == "u-003"
        assert self.svc.assign_rep_round_robin(t, 3) == "u-001"  # wraps

    def test_no_reps_falls_back_to_manager(self):
        t = _territory(reps=[])
        t["primary_manager"] = "u-mgr"
        assert self.svc.assign_rep_round_robin(t, 0) == "u-mgr"


# ── TerritoriesService.validate_manual_override ───────────────────────────────

class TestManualOverride:
    svc = TerritoriesService()

    def test_manager_allowed(self):
        self.svc.validate_manual_override({}, "manager")  # no exception

    def test_admin_allowed(self):
        self.svc.validate_manual_override({}, "admin")

    def test_agent_denied(self):
        with pytest.raises(ValueError, match="manager or admin"):
            self.svc.validate_manual_override({}, "agent")

    def test_is_manually_assigned(self):
        assert self.svc.is_manually_assigned({"assignment_reason": "manual_override"}) is True
        assert self.svc.is_manually_assigned({"assignment_reason": "auto_rule_match"}) is False
