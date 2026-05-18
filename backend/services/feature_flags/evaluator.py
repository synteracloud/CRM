"""Feature flag evaluation engine.

Docs: db/feature_flag_db/schema.sql
      docs/feature-flags-config.md (if exists)

Design:
  - Safe-by-default: a flag with no matching rule returns its default_value (FALSE).
  - Rules are evaluated in ascending priority order (lower number = first).
  - First matching rule wins; remaining rules are skipped.
  - Rule types (from schema flag_rules.rule_type):
      always_off   → return False unconditionally
      always_on    → return True unconditionally
      tenant       → match condition_json["tenant_id"] against context.tenant_id
      role         → match condition_json["role"] against context.role
      percentage   → deterministic hash-based rollout, condition_json["percentage"] ∈ [0, 100]

  Evaluation is deterministic: same flag_key + tenant_id always produces same result
  for percentage rules (hash is stable across processes).

Usage::
    evaluator = FeatureFlagEvaluator()
    evaluator.register(
        FeatureFlag(key="whatsapp_360dialog", name="360dialog", default_value=False),
        rules=[FlagRule(rule_type="tenant", condition_json={"tenant_id": "abc"}, value=True, priority=10)],
    )
    on = evaluator.evaluate("whatsapp_360dialog", EvaluationContext(tenant_id="abc", role="agent"))
    # → True

    # DB-backed: inject a DbFlagStore (built in P-025) for production persistence.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


# ── Domain types ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FeatureFlag:
    """Mirrors feature_flag_db.feature_flags table row."""
    key:           str
    name:          str
    default_value: bool = False
    status:        str  = "active"   # active | archived


@dataclass(frozen=True)
class FlagRule:
    """Mirrors feature_flag_db.flag_rules table row."""
    rule_type:      str           # tenant | role | percentage | always_on | always_off
    condition_json: dict[str, Any]
    value:          bool = True
    priority:       int  = 0      # lower = evaluated first


@dataclass(frozen=True)
class EvaluationContext:
    """Caller-supplied context used to evaluate targeting rules."""
    tenant_id: str | None = None
    user_id:   str | None = None
    role:      str | None = None
    extra:     dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationResult:
    flag_key:      str
    value:         bool
    rule_matched:  str | None  # rule_type that produced the result, or None (default)
    default_used:  bool


# ── Evaluator ─────────────────────────────────────────────────────────────────

class FeatureFlagEvaluator:
    """In-memory feature flag evaluator.

    Swap for a DB-backed store (inject a store that reads from
    feature_flag_db.feature_flags and feature_flag_db.flag_rules) in P-025.
    """

    def __init__(self) -> None:
        self._flags: dict[str, FeatureFlag] = {}
        self._rules: dict[str, list[FlagRule]] = {}   # key → sorted rules

    def register(self, flag: FeatureFlag, rules: list[FlagRule] | None = None) -> None:
        """Register a flag and its targeting rules."""
        self._flags[flag.key] = flag
        self._rules[flag.key] = sorted(rules or [], key=lambda r: r.priority)

    def evaluate(self, flag_key: str, context: EvaluationContext) -> EvaluationResult:
        """Evaluate flag_key against context.

        Returns EvaluationResult with value (bool) and which rule matched.
        If the flag is unknown or archived, returns False (safe default).
        """
        flag = self._flags.get(flag_key)
        if flag is None or flag.status == "archived":
            return EvaluationResult(
                flag_key=flag_key,
                value=False,
                rule_matched=None,
                default_used=True,
            )

        for rule in self._rules.get(flag_key, []):
            matched, value = self._apply_rule(rule, context, flag_key)
            if matched:
                return EvaluationResult(
                    flag_key=flag_key,
                    value=value,
                    rule_matched=rule.rule_type,
                    default_used=False,
                )

        return EvaluationResult(
            flag_key=flag_key,
            value=flag.default_value,
            rule_matched=None,
            default_used=True,
        )

    def is_enabled(self, flag_key: str, context: EvaluationContext) -> bool:
        """Convenience: return bool result of evaluate()."""
        return self.evaluate(flag_key, context).value

    # ── Rule matchers ─────────────────────────────────────────────────────────

    def _apply_rule(
        self,
        rule: FlagRule,
        context: EvaluationContext,
        flag_key: str,
    ) -> tuple[bool, bool]:
        """Return (matched: bool, value: bool).  If not matched, value is ignored."""

        match rule.rule_type:
            case "always_off":
                return True, False

            case "always_on":
                return True, True

            case "tenant":
                target = rule.condition_json.get("tenant_id")
                if target and context.tenant_id == target:
                    return True, rule.value
                return False, False

            case "role":
                target = rule.condition_json.get("role")
                if target and context.role == target:
                    return True, rule.value
                return False, False

            case "percentage":
                pct = float(rule.condition_json.get("percentage", 0))
                if pct <= 0:
                    return False, False
                if pct >= 100:
                    return True, rule.value
                # Deterministic hash: sha256(flag_key + tenant_id) mod 100
                seed = f"{flag_key}:{context.tenant_id or ''}".encode("utf-8")
                bucket = int(hashlib.sha256(seed).hexdigest(), 16) % 100
                return bucket < pct, rule.value

            case _:
                # Unknown rule type — skip (safe-by-default)
                return False, False


# ── Module-level singleton ────────────────────────────────────────────────────
# Used by services that import evaluate() directly without DI.
# P-019/P-025 will replace this with a DB-backed evaluator injected at startup.

_default_evaluator = FeatureFlagEvaluator()


def register(flag: FeatureFlag, rules: list[FlagRule] | None = None) -> None:
    """Register a flag on the default module-level evaluator."""
    _default_evaluator.register(flag, rules)


def evaluate(flag_key: str, context: EvaluationContext) -> EvaluationResult:
    """Evaluate using the default module-level evaluator."""
    return _default_evaluator.evaluate(flag_key, context)


def is_enabled(flag_key: str, context: EvaluationContext) -> bool:
    """Shorthand: True if flag is enabled for context."""
    return _default_evaluator.is_enabled(flag_key, context)
