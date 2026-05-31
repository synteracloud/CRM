"""Territory domain entities: enums, rule types, evaluation helpers.

Domain spec: backend/docs/domain/territory-management.md §2, §3
"""
from __future__ import annotations

from enum import Enum
from typing import Any


class TerritoryCriteriaType(str, Enum):
    GEOGRAPHIC      = "geographic"
    POSTAL          = "postal"
    ACCOUNT_SEGMENT = "account_segment"
    REP_ASSIGNED    = "rep_assigned"
    HYBRID          = "hybrid"


class TerritoryRuleType(str, Enum):
    CITY             = "city"
    POSTAL_CODE      = "postal_code"
    REGION           = "region"
    GEO_POLYGON      = "geo_polygon"
    ACCOUNT_INDUSTRY = "account_industry"
    ACCOUNT_SIZE     = "account_size"
    ACCOUNT_TIER     = "account_tier"
    REP_EXPLICIT     = "rep_explicit"
    CUSTOM_FIELD     = "custom_field"


class RuleOperator(str, Enum):
    EQ          = "eq"
    IN          = "in"
    NOT_IN      = "not_in"
    STARTS_WITH = "starts_with"
    CONTAINS    = "contains"
    GEO_WITHIN  = "geo_within"


class SubjectType(str, Enum):
    LEAD    = "lead"
    ACCOUNT = "account"
    CONTACT = "contact"


class AssignmentReason(str, Enum):
    AUTO_RULE_MATCH      = "auto_rule_match"
    MANUAL_OVERRIDE      = "manual_override"
    CONFLICT_RESOLUTION  = "conflict_resolution"
    DEFAULT_FALLBACK     = "default_fallback"


# ── Rule evaluation ───────────────────────────────────────────────────────────

class RuleEvaluationError(ValueError):
    """Raised when a rule cannot be evaluated (e.g. missing required fields)."""


def evaluate_rule(rule: dict, subject: dict) -> bool:
    """
    Evaluate a single TerritoryRule against a subject (lead or account dict).
    Returns True if the rule matches, False otherwise.
    Spec §3.2.

    Geo polygon (geo_within) returns False when lat_lng is None — spec §3.2.
    """
    rule_type = rule.get("rule_type")
    operator  = rule.get("operator")
    value     = rule.get("value", {})

    if rule_type == TerritoryRuleType.GEO_POLYGON:
        # v1: no-match when lat_lng absent — spec §3.2
        return False

    if rule_type == TerritoryRuleType.REP_EXPLICIT:
        # Explicit rep assignment — always matches (the rep assignment happens later)
        return True

    if rule_type == TerritoryRuleType.CITY:
        cities    = [c.lower() for c in value.get("cities", [])]
        subj_city = (subject.get("city") or "").lower()
        if operator == RuleOperator.EQ:
            return subj_city in cities
        if operator == RuleOperator.IN:
            return subj_city in cities
        if operator == RuleOperator.NOT_IN:
            return subj_city not in cities
        return False

    if rule_type == TerritoryRuleType.POSTAL_CODE:
        codes      = [str(c) for c in value.get("codes", [])]
        subj_code  = str(subject.get("postal_code") or "")
        if operator == RuleOperator.EQ:
            return subj_code in codes
        if operator == RuleOperator.IN:
            return subj_code in codes
        if operator == RuleOperator.STARTS_WITH:
            return any(subj_code.startswith(c) for c in codes)
        return False

    if rule_type == TerritoryRuleType.REGION:
        provinces   = [p.lower() for p in value.get("provinces", [])]
        subj_prov   = (subject.get("province") or subject.get("region") or "").lower()
        if operator in (RuleOperator.EQ, RuleOperator.IN):
            return subj_prov in provinces
        return False

    if rule_type in (TerritoryRuleType.ACCOUNT_INDUSTRY, TerritoryRuleType.ACCOUNT_TIER):
        key      = "industry" if rule_type == TerritoryRuleType.ACCOUNT_INDUSTRY else "tier"
        allowed  = [v.lower() for v in value.get("industries" if key == "industry" else "tiers", [])]
        subj_val = (subject.get(key) or "").lower()
        if operator in (RuleOperator.EQ, RuleOperator.IN):
            return subj_val in allowed
        return False

    if rule_type == TerritoryRuleType.ACCOUNT_SIZE:
        sizes     = value.get("sizes", [])
        subj_size = subject.get("account_size") or subject.get("employee_count") or ""
        return str(subj_size) in sizes

    if rule_type == TerritoryRuleType.CUSTOM_FIELD:
        cf_key   = value.get("key", "")
        match_vs = [str(v).lower() for v in value.get("match_values", [])]
        cf_dict  = subject.get("custom_fields") or {}
        subj_cf  = str(cf_dict.get(cf_key, "")).lower()
        if operator == RuleOperator.EQ:
            return subj_cf in match_vs
        if operator == RuleOperator.IN:
            return subj_cf in match_vs
        if operator == RuleOperator.CONTAINS:
            return any(m in subj_cf for m in match_vs)
        return False

    return False


def evaluate_territory(territory: dict, rules: list[dict], subject: dict) -> bool:
    """
    Evaluate all rules for a territory against a subject.
    ALL rules must match (AND logic). Empty rules list = always matches.
    Spec §3.1.
    """
    if not rules:
        return True
    return all(evaluate_rule(r, subject) for r in rules)
