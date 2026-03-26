"""Rule engine entities for deterministic condition evaluation and action triggering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

ConditionMatchMode = Literal["all", "any"]
RuleOperator = Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "contains", "exists"]
ActionType = Literal["emit_event", "call_service", "notify", "mutate_state", "wait"]


@dataclass(frozen=True)
class ConditionRule:
    field: str
    op: RuleOperator
    value: Any


@dataclass(frozen=True)
class ActionDefinition:
    action_id: str
    type: ActionType
    target: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class RuleDefinition:
    rule_id: str
    tenant_id: str
    workflow_key: str
    trigger_event: str
    priority: int
    match: ConditionMatchMode
    conditions: tuple[ConditionRule, ...]
    actions: tuple[ActionDefinition, ...]
    is_active: bool = True


@dataclass(frozen=True)
class RuleEvaluation:
    rule_id: str
    matched: bool
    actions: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class RuleEvaluationResult:
    trigger_event: str
    matched_rule_ids: tuple[str, ...]
    evaluations: tuple[RuleEvaluation, ...]


class RuleValidationError(ValueError):
    """Raised when rule definitions are invalid or ambiguous."""


class RuleNotFoundError(KeyError):
    """Raised when a rule does not exist."""
