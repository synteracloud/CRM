"""Execution-first workflow engine with trigger reliability and QC."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

from .entities import (
    ActionDefinition,
    ActionType,
    AutomationResult,
    RuleCondition,
    TriggerType,
    WorkflowEvent,
    WorkflowRule,
    utc_now,
)


class WorkflowValidationError(ValueError):
    """Raised when workflow events/rules are invalid."""


@dataclass(frozen=True)
class ReliabilityReport:
    trigger_reliability_percent: float
    missed_automations: int
    processed_events: int
    alignment_percent: float
    score: str


class WorkflowEngine:
    """In-memory workflow engine supporting triggers, actions, and conditions."""

    _OPERATORS = {
        "eq": lambda left, right: left == right,
        "neq": lambda left, right: left != right,
        "gt": lambda left, right: left > right,
        "gte": lambda left, right: left >= right,
        "lt": lambda left, right: left < right,
        "lte": lambda left, right: left <= right,
        "contains": lambda left, right: isinstance(left, (str, list, tuple, set)) and right in left,
    }

    def __init__(self) -> None:
        self._rules: dict[str, WorkflowRule] = {}
        self._processed_event_ids: set[str] = set()
        self._events: list[WorkflowEvent] = []
        self._results: list[AutomationResult] = []
        self._action_log: list[dict[str, object]] = []
        self._trigger_stats: dict[TriggerType, dict[str, int]] = defaultdict(lambda: {"received": 0, "executed": 0})

    def register_rule(self, rule: WorkflowRule) -> WorkflowRule:
        self._validate_rule(rule)
        self._rules[rule.rule_id] = rule
        return rule

    def ingest_event(self, event: WorkflowEvent, now: datetime | None = None) -> list[AutomationResult]:
        now = now or utc_now()
        self._validate_event(event)

        if event.event_id in self._processed_event_ids:
            return []

        self._processed_event_ids.add(event.event_id)
        self._events.append(event)
        self._trigger_stats[event.trigger]["received"] += 1

        matched_rules = [rule for rule in self._rules.values() if rule.trigger == event.trigger and self._rule_matches(rule, event)]
        outcomes: list[AutomationResult] = []

        for rule in matched_rules:
            executed_ids: list[str] = []
            for action in rule.actions:
                self._execute_action(action, event, now)
                executed_ids.append(action.action_id)

            self._trigger_stats[event.trigger]["executed"] += 1
            result = AutomationResult(
                event_id=event.event_id,
                rule_id=rule.rule_id,
                executed_action_ids=tuple(executed_ids),
                executed_at=now,
            )
            self._results.append(result)
            outcomes.append(result)

        return outcomes

    def detect_missed_automations(self, grace_period: timedelta = timedelta(minutes=30), now: datetime | None = None) -> list[WorkflowEvent]:
        now = now or utc_now()
        actionable_triggers = {rule.trigger for rule in self._rules.values()}
        covered_event_ids = {result.event_id for result in self._results}
        return [
            event
            for event in self._events
            if event.trigger in actionable_triggers
            and event.event_id not in covered_event_ids
            and event.occurred_at <= now - grace_period
        ]

    def qc_report(self, now: datetime | None = None) -> ReliabilityReport:
        now = now or utc_now()
        received = sum(stats["received"] for stats in self._trigger_stats.values())
        executed = sum(stats["executed"] for stats in self._trigger_stats.values())
        missed = len(self.detect_missed_automations(now=now))

        trigger_reliability = 100.0 if received == 0 else round((executed / received) * 100, 2)
        missed_penalty = 0.0 if received == 0 else round((missed / received) * 100, 2)
        alignment = max(0.0, round(100.0 - missed_penalty, 2))
        perfect = trigger_reliability == 100.0 and missed == 0 and alignment == 100.0
        return ReliabilityReport(
            trigger_reliability_percent=trigger_reliability,
            missed_automations=missed,
            processed_events=received,
            alignment_percent=alignment,
            score="10/10" if perfect else "9/10",
        )

    def action_log(self) -> list[dict[str, object]]:
        return list(self._action_log)

    def results(self) -> list[AutomationResult]:
        return list(self._results)

    def _execute_action(self, action: ActionDefinition, event: WorkflowEvent, now: datetime) -> None:
        if action.action_type not in {ActionType.SEND_MESSAGE, ActionType.CREATE_TASK, ActionType.UPDATE_STAGE}:
            raise WorkflowValidationError(f"Unsupported action type: {action.action_type}")

        self._action_log.append(
            {
                "action_id": action.action_id,
                "action_type": action.action_type.value,
                "tenant_id": event.tenant_id,
                "event_id": event.event_id,
                "trigger": event.trigger.value,
                "params": dict(action.params),
                "at": now,
            }
        )

    def _rule_matches(self, rule: WorkflowRule, event: WorkflowEvent) -> bool:
        return all(self._evaluate_condition(condition, event.payload) for condition in rule.conditions)

    def _evaluate_condition(self, condition: RuleCondition, payload: dict[str, object]) -> bool:
        op = self._OPERATORS.get(condition.operator)
        if op is None:
            raise WorkflowValidationError(f"Unsupported operator: {condition.operator}")
        left = payload.get(condition.field)
        return op(left, condition.value)

    @staticmethod
    def _validate_event(event: WorkflowEvent) -> None:
        if not event.event_id.strip():
            raise WorkflowValidationError("event_id is required")
        if not event.tenant_id.strip():
            raise WorkflowValidationError("tenant_id is required")

    @staticmethod
    def _validate_rule(rule: WorkflowRule) -> None:
        if not rule.rule_id.strip():
            raise WorkflowValidationError("rule_id is required")
        if not rule.actions:
            raise WorkflowValidationError("rule must contain at least one action")
