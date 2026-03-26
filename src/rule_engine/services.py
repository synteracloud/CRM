"""Deterministic rule evaluation engine."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .entities import (
    ActionDefinition,
    ConditionClause,
    ConditionGroup,
    ConditionRule,
    RuleDefinition,
    RuleEvaluation,
    RuleEvaluationResult,
    RuleNotFoundError,
    RuleValidationError,
)

ALLOWED_OPERATORS: frozenset[str] = frozenset({"eq", "ne", "gt", "gte", "lt", "lte", "in", "contains", "exists"})
ALLOWED_MATCH_MODES: frozenset[str] = frozenset({"all", "any"})
ALLOWED_LOGICAL_OPERATORS: frozenset[str] = frozenset({"and", "or"})


class RuleConditionBuilder:
    """Composable builder for deterministic rule condition trees."""

    @staticmethod
    def condition(field: str, op: str, value: Any) -> ConditionRule:
        return ConditionRule(field=field, op=op, value=value)

    @staticmethod
    def all(*clauses: ConditionClause) -> ConditionGroup:
        return ConditionGroup(operator="and", clauses=tuple(clauses))

    @staticmethod
    def any(*clauses: ConditionClause) -> ConditionGroup:
        return ConditionGroup(operator="or", clauses=tuple(clauses))


class RuleEngineService:
    def __init__(self) -> None:
        self._rules: dict[str, RuleDefinition] = {}
        self._by_trigger: dict[str, list[str]] = {}

    def list_rules(self, trigger_event: str | None = None) -> list[RuleDefinition]:
        if trigger_event is None:
            return [self._rules[key] for key in sorted(self._rules)]
        ordered = self._by_trigger.get(trigger_event, [])
        return [self._rules[rule_id] for rule_id in ordered]

    def get_rule(self, rule_id: str) -> RuleDefinition:
        rule = self._rules.get(rule_id)
        if not rule:
            raise RuleNotFoundError(f"Rule not found: {rule_id}")
        return rule

    def register_rule(self, definition: RuleDefinition) -> RuleDefinition:
        self._validate_definition(definition)
        self._ensure_not_ambiguous(definition)

        self._rules[definition.rule_id] = definition
        self._reindex_trigger(definition.trigger_event)
        return definition

    def deactivate_rule(self, rule_id: str) -> RuleDefinition:
        current = self.get_rule(rule_id)
        updated = replace(current, is_active=False)
        self._rules[rule_id] = updated
        self._reindex_trigger(updated.trigger_event)
        return updated

    def evaluate(self, trigger_event: str, tenant_id: str, context: dict[str, Any]) -> RuleEvaluationResult:
        evaluations: list[RuleEvaluation] = []
        matched_rule_ids: list[str] = []

        for rule in self.list_rules(trigger_event):
            if not rule.is_active or rule.tenant_id != tenant_id:
                continue

            matched = self._evaluate_conditions(rule, context)
            actions: tuple[dict[str, Any], ...] = ()
            if matched:
                actions = tuple(self._trigger_action(action, context) for action in rule.actions)
                matched_rule_ids.append(rule.rule_id)
            evaluations.append(RuleEvaluation(rule_id=rule.rule_id, matched=matched, actions=actions))

        return RuleEvaluationResult(
            trigger_event=trigger_event,
            matched_rule_ids=tuple(matched_rule_ids),
            evaluations=tuple(evaluations),
        )

    def _validate_definition(self, definition: RuleDefinition) -> None:
        if definition.match not in ALLOWED_MATCH_MODES:
            raise RuleValidationError(f"Unsupported condition match mode: {definition.match}")
        if not definition.conditions and definition.condition_root is None:
            raise RuleValidationError("Rule must define at least one condition")
        if not definition.actions:
            raise RuleValidationError("Rule must define at least one action")

        if definition.condition_root is not None:
            self._validate_condition_clause(definition.condition_root)
        else:
            for condition in definition.conditions:
                self._validate_condition(condition)
        for action in definition.actions:
            self._validate_action(action)

    def _ensure_not_ambiguous(self, definition: RuleDefinition) -> None:
        for existing in self.list_rules(definition.trigger_event):
            if existing.rule_id == definition.rule_id:
                continue
            if existing.tenant_id != definition.tenant_id:
                continue
            if existing.priority == definition.priority:
                raise RuleValidationError(
                    f"Ambiguous priority for trigger={definition.trigger_event}, tenant={definition.tenant_id}, "
                    f"priority={definition.priority}. Conflicts with rule={existing.rule_id}"
                )
            if self._conditions_signature(existing) == self._conditions_signature(definition):
                raise RuleValidationError(
                    f"Ambiguous duplicate condition set for trigger={definition.trigger_event}, tenant={definition.tenant_id}. "
                    f"Conflicts with rule={existing.rule_id}"
                )

    def _reindex_trigger(self, trigger_event: str) -> None:
        active_and_inactive = [
            rule for rule in self._rules.values() if rule.trigger_event == trigger_event
        ]
        active_and_inactive.sort(key=lambda rule: (rule.priority, rule.rule_id))
        self._by_trigger[trigger_event] = [rule.rule_id for rule in active_and_inactive]

    @staticmethod
    def _conditions_signature(rule: RuleDefinition) -> tuple[tuple[str, str, str], ...]:
        if rule.condition_root is not None:
            return (("tree", "root", RuleEngineService._clause_signature(rule.condition_root)),)

        payload = []
        for condition in rule.conditions:
            payload.append((condition.field, condition.op, repr(condition.value)))
        return tuple(sorted(payload))

    @staticmethod
    def _clause_signature(clause: ConditionClause) -> str:
        if isinstance(clause, ConditionRule):
            return f"rule({clause.field}|{clause.op}|{repr(clause.value)})"
        children = ",".join(RuleEngineService._clause_signature(child) for child in clause.clauses)
        return f"group({clause.operator}|{children})"

    @staticmethod
    def _validate_condition(condition: ConditionRule) -> None:
        if condition.op not in ALLOWED_OPERATORS:
            raise RuleValidationError(f"Unsupported condition operator: {condition.op}")
        if not condition.field:
            raise RuleValidationError("Condition field path must be non-empty")

    def _validate_condition_clause(self, clause: ConditionClause) -> None:
        if isinstance(clause, ConditionRule):
            self._validate_condition(clause)
            return

        if clause.operator not in ALLOWED_LOGICAL_OPERATORS:
            raise RuleValidationError(f"Unsupported logical operator: {clause.operator}")
        if not clause.clauses:
            raise RuleValidationError("Condition groups must contain at least one clause")
        for nested in clause.clauses:
            self._validate_condition_clause(nested)

    @staticmethod
    def _validate_action(action: ActionDefinition) -> None:
        if not action.action_id:
            raise RuleValidationError("Action action_id must be non-empty")
        if not action.target:
            raise RuleValidationError("Action target must be non-empty")

    def _evaluate_conditions(self, definition: RuleDefinition, context: dict[str, Any]) -> bool:
        if definition.condition_root is not None:
            return self._evaluate_clause(definition.condition_root, context)
        outcomes = [self._evaluate_condition(rule, context) for rule in definition.conditions]
        if definition.match == "all":
            return all(outcomes)
        return any(outcomes)

    def _evaluate_clause(self, clause: ConditionClause, context: dict[str, Any]) -> bool:
        if isinstance(clause, ConditionRule):
            return self._evaluate_condition(clause, context)

        if clause.operator == "and":
            for nested in clause.clauses:
                if not self._evaluate_clause(nested, context):
                    return False
            return True

        for nested in clause.clauses:
            if self._evaluate_clause(nested, context):
                return True
        return False

    def _evaluate_condition(self, rule: ConditionRule, context: dict[str, Any]) -> bool:
        actual = _resolve_field_path(context, rule.field)

        if rule.op == "exists":
            return (actual is not None) is bool(rule.value)
        if rule.op == "eq":
            return actual == rule.value
        if rule.op == "ne":
            return actual != rule.value
        if rule.op == "gt":
            return actual is not None and actual > rule.value
        if rule.op == "gte":
            return actual is not None and actual >= rule.value
        if rule.op == "lt":
            return actual is not None and actual < rule.value
        if rule.op == "lte":
            return actual is not None and actual <= rule.value
        if rule.op == "contains":
            return actual is not None and str(rule.value) in str(actual)
        if rule.op == "in":
            if not isinstance(rule.value, (tuple, list, set, frozenset)):
                return False
            return actual in set(rule.value)
        return False

    @staticmethod
    def _trigger_action(action: ActionDefinition, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "action_id": action.action_id,
            "type": action.type,
            "target": action.target,
            "payload": _resolve_template_payload(action.payload, context),
            "status": "triggered",
        }


def _resolve_field_path(payload: dict[str, Any], field_path: str) -> Any:
    cursor: Any = payload
    for part in field_path.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            return None
        cursor = cursor[part]
    return cursor


def _resolve_template_payload(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            field_path = value[2:-1]
            resolved[key] = _resolve_field_path(context, field_path)
            continue
        resolved[key] = value
    return resolved
