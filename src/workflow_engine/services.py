"""Workflow execution engine with trigger handling and action execution primitives."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from src.event_bus import EVENT_NAMES, Event

from .entities import (
    ActionDefinition,
    ConditionDefinition,
    ConditionRule,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowNotFoundError,
    WorkflowStep,
    WorkflowValidationError,
)

ALLOWED_ACTION_TYPES: frozenset[str] = frozenset({"emit_event", "call_service", "notify", "mutate_state", "wait"})


class TriggerHandlingSystem:
    """Tracks event/workflow bindings and evaluates trigger mode semantics."""

    def __init__(self) -> None:
        self._event_bindings: dict[str, set[str]] = {}
        self._seen_trigger_events: dict[tuple[str, str], set[str]] = {}

    def register(self, definition: WorkflowDefinition) -> None:
        for event_name in definition.triggers.events:
            self._event_bindings.setdefault(event_name, set()).add(definition.workflow_key)

    def workflows_for_event(self, event_name: str) -> tuple[str, ...]:
        return tuple(sorted(self._event_bindings.get(event_name, set())))

    def trigger_matches(self, definition: WorkflowDefinition, event: Event) -> bool:
        if event.event_name not in definition.triggers.events:
            return False
        tenant_key = (definition.workflow_key, event.tenant_id)
        seen = self._seen_trigger_events.setdefault(tenant_key, set())
        seen.add(event.event_name)
        if definition.triggers.mode == "any":
            return True
        return set(definition.triggers.events).issubset(seen)


class ActionExecutionEngine:
    """Executes workflow actions using deterministic in-memory adapters."""

    @staticmethod
    def execute(action: ActionDefinition, context: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        rendered_input = _render_payload(action.input, context, state)
        if action.type == "emit_event":
            return {"emitted": list(action.emits), "payload": rendered_input}
        if action.type == "call_service":
            return {"service": action.service, "operation": action.operation, "input": rendered_input, "ok": True}
        if action.type == "notify":
            return {"channel": "notification", "service": action.service, "input": rendered_input}
        if action.type == "mutate_state":
            return {"mutation": action.operation, "input": rendered_input}
        raise WorkflowValidationError(f"Unsupported action type: {action.type}")


class WorkflowEngine:
    def __init__(self) -> None:
        self._definitions: dict[str, WorkflowDefinition] = {}
        self._executions: dict[str, WorkflowExecution] = {}
        self._execution_counter = 0
        self._trigger_handler = TriggerHandlingSystem()
        self._action_engine = ActionExecutionEngine()

    def register_workflow(self, definition: WorkflowDefinition) -> WorkflowDefinition:
        self._validate_workflow(definition)
        self._definitions[definition.workflow_key] = definition
        self._trigger_handler.register(definition)
        return definition

    def start_workflow(self, workflow_key: str, event: Event | None = None, context: dict[str, Any] | None = None) -> WorkflowExecution:
        definition = self.get_workflow(workflow_key)
        if event is None and not definition.triggers.manual:
            raise WorkflowValidationError(f"Workflow {workflow_key} does not allow manual execution")

        execution_context = self._build_context(definition, event, context)
        if not self._evaluate_conditions(definition.conditions, execution_context):
            raise WorkflowValidationError(f"Workflow conditions not met for {workflow_key}")

        execution = WorkflowExecution(
            execution_id=self._next_execution_id(workflow_key),
            workflow_key=workflow_key,
            tenant_id=execution_context["tenant_id"],
            status="running",
            context=execution_context,
            current_step_id=definition.sequencing.steps[0].id,
            started_at=_now_iso(),
        )
        self._executions[execution.execution_id] = execution
        self._run_execution(definition, execution)
        return execution

    def stop_workflow(self, execution_id: str) -> WorkflowExecution:
        execution = self._executions.get(execution_id)
        if execution is None:
            raise WorkflowNotFoundError(f"Execution not found: {execution_id}")
        if execution.status in {"completed", "failed", "stopped"}:
            return execution
        execution.status = "stopped"
        execution.completed_at = _now_iso()
        execution.step_log.append({"action": "workflow.stopped", "at": execution.completed_at})
        return execution

    def handle_event(self, event: Event) -> list[WorkflowExecution]:
        started: list[WorkflowExecution] = []
        for workflow_key in self._trigger_handler.workflows_for_event(event.event_name):
            definition = self._definitions[workflow_key]
            if not self._trigger_handler.trigger_matches(definition, event):
                continue
            started.append(self.start_workflow(workflow_key, event=event))
        return started

    def resume_due_waits(self, now_iso: str | None = None) -> list[WorkflowExecution]:
        now = _parse_iso(now_iso) if now_iso else datetime.now(timezone.utc)
        resumed: list[WorkflowExecution] = []
        for execution in self._executions.values():
            if execution.status != "waiting" or not execution.waiting_until:
                continue
            if _parse_iso(execution.waiting_until) <= now:
                definition = self._definitions[execution.workflow_key]
                execution.status = "running"
                execution.waiting_until = None
                execution.step_log.append({"action": "wait.resumed", "at": _to_iso(now)})
                self._run_execution(definition, execution)
                resumed.append(execution)
        return resumed

    def list_executions(self, workflow_key: str | None = None) -> list[WorkflowExecution]:
        executions = list(self._executions.values())
        if workflow_key is None:
            return executions
        return [item for item in executions if item.workflow_key == workflow_key]

    def get_workflow(self, workflow_key: str) -> WorkflowDefinition:
        definition = self._definitions.get(workflow_key)
        if not definition:
            raise WorkflowNotFoundError(f"Workflow not found: {workflow_key}")
        return definition

    def _run_execution(self, definition: WorkflowDefinition, execution: WorkflowExecution) -> None:
        steps = definition.sequencing.steps
        step_map = {step.id: step for step in steps}

        while execution.current_step_id is not None:
            step = step_map[execution.current_step_id]
            if step.when and not _safe_eval_when(step.when, execution.context):
                execution.step_log.append({"step_id": step.id, "action": "step.skipped", "at": _now_iso()})
                execution.current_step_id = self._resolve_next_step(definition, step)
                continue

            action = definition.actions[step.action]
            if action.type == "wait":
                self._apply_wait_step(step, action, execution)
                return

            result = self._action_engine.execute(action, execution.context, execution.state)
            execution.state[step.action] = result
            execution.step_log.append(
                {"step_id": step.id, "action": step.action, "result": result, "at": _now_iso()}
            )
            execution.current_step_id = self._resolve_next_step(definition, step)

        execution.status = "completed"
        execution.completed_at = _now_iso()

    def _resolve_next_step(self, definition: WorkflowDefinition, step: WorkflowStep) -> str | None:
        if definition.sequencing.strategy == "branching":
            if not step.next or step.next == "end":
                return None
            return step.next

        steps = definition.sequencing.steps
        idx = next(index for index, item in enumerate(steps) if item.id == step.id)
        return steps[idx + 1].id if idx + 1 < len(steps) else None

    def _apply_wait_step(self, step: WorkflowStep, action: ActionDefinition, execution: WorkflowExecution) -> None:
        seconds = int(action.input.get("duration_seconds", 0))
        if seconds <= 0:
            execution.status = "failed"
            execution.error_message = f"Wait step requires positive duration_seconds. step={step.id}"
            execution.completed_at = _now_iso()
            raise WorkflowValidationError(execution.error_message)

        execution.status = "waiting"
        wait_until = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        execution.waiting_until = _to_iso(wait_until)
        execution.step_log.append({"step_id": step.id, "action": "wait.started", "seconds": seconds, "at": _now_iso()})
        execution.current_step_id = self._resolve_next_step(self._definitions[execution.workflow_key], step)

    def _build_context(
        self, definition: WorkflowDefinition, event: Event | None, context: dict[str, Any] | None
    ) -> dict[str, Any]:
        provided = context.copy() if context else {}
        if event is not None:
            provided.setdefault("event", event.event_name)
            provided.setdefault("tenant_id", event.tenant_id)
            provided.setdefault("entity", event.payload)
            provided.setdefault("event_id", event.event_id)
        provided.setdefault("workflow_key", definition.workflow_key)
        if "tenant_id" not in provided:
            raise WorkflowValidationError("Execution context must provide tenant_id")
        return provided

    @staticmethod
    def _evaluate_conditions(conditions: ConditionDefinition, context: dict[str, Any]) -> bool:
        if not conditions.rules:
            return True
        checks = [_evaluate_rule(rule, context) for rule in conditions.rules]
        return all(checks) if conditions.match == "all" else any(checks)

    @staticmethod
    def _validate_workflow(definition: WorkflowDefinition) -> None:
        if definition.workflow_key != definition.workflow_key.lower() or "-" in definition.workflow_key:
            raise WorkflowValidationError("workflow_key must be snake_case")
        if not definition.sequencing.steps:
            raise WorkflowValidationError("Workflow must contain at least one sequencing step")

        events = set(EVENT_NAMES)
        for event_name in definition.triggers.events:
            if event_name not in events:
                raise WorkflowValidationError(f"Unknown trigger event: {event_name}")

        seen_ids: set[str] = set()
        for step in definition.sequencing.steps:
            if step.id in seen_ids:
                raise WorkflowValidationError(f"Duplicate step id: {step.id}")
            seen_ids.add(step.id)
            if step.action not in definition.actions:
                raise WorkflowValidationError(f"Undefined step action: {step.action}")
            if step.retries < 0:
                raise WorkflowValidationError(f"Retries cannot be negative. step={step.id}")
            if definition.sequencing.strategy == "branching" and not step.next:
                raise WorkflowValidationError(f"Branching step missing next pointer: {step.id}")

        for action_ref, action in definition.actions.items():
            if action.type not in ALLOWED_ACTION_TYPES:
                raise WorkflowValidationError(f"Unsupported action type: {action_ref}:{action.type}")
            if action.type == "emit_event":
                unknown = [event for event in action.emits if event not in events]
                if unknown:
                    raise WorkflowValidationError(f"Action emits unknown events: {action_ref}:{unknown}")

    def _next_execution_id(self, workflow_key: str) -> str:
        self._execution_counter += 1
        return f"wfexec::{workflow_key}::{self._execution_counter}"

    def self_qc_trigger_action_integrity(self) -> dict[str, Any]:
        """Return trigger/action integrity report with a deterministic 10-point score."""

        if not self._definitions:
            return {
                "score": 10,
                "checks": {
                    "all_triggers_map_to_event_catalog": True,
                    "no_undefined_actions": True,
                },
                "issues": [],
            }

        issues: list[str] = []
        catalog = set(EVENT_NAMES)
        for definition in self._definitions.values():
            unknown_trigger_events = sorted(set(definition.triggers.events) - catalog)
            if unknown_trigger_events:
                issues.append(f"{definition.workflow_key}: unknown trigger events {unknown_trigger_events}")
            undefined_actions = sorted(
                {step.action for step in definition.sequencing.steps if step.action not in definition.actions}
            )
            if undefined_actions:
                issues.append(f"{definition.workflow_key}: undefined actions {undefined_actions}")

        return {
            "score": 10 if not issues else 0,
            "checks": {
                "all_triggers_map_to_event_catalog": not any("unknown trigger events" in issue for issue in issues),
                "no_undefined_actions": not any("undefined actions" in issue for issue in issues),
            },
            "issues": issues,
        }



def _evaluate_rule(rule: ConditionRule, context: dict[str, Any]) -> bool:
    value = _resolve_field(context, rule.field)
    if rule.op == "exists":
        return (value is not None) is bool(rule.value)
    if rule.op == "eq":
        return value == rule.value
    if rule.op == "neq":
        return value != rule.value
    if rule.op == "in":
        return value in rule.value
    if rule.op == "not_in":
        return value not in rule.value
    if rule.op == "gt":
        return value > rule.value
    if rule.op == "gte":
        return value >= rule.value
    if rule.op == "lt":
        return value < rule.value
    if rule.op == "lte":
        return value <= rule.value
    raise WorkflowValidationError(f"Unsupported condition operator: {rule.op}")



def _resolve_field(context: dict[str, Any], path: str) -> Any:
    node: Any = context
    for part in path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node



def _safe_eval_when(expression: str, context: dict[str, Any]) -> bool:
    normalized = expression.strip()
    if "==" in normalized:
        left, right = [item.strip() for item in normalized.split("==", 1)]
        left_value = _resolve_field(context, left)
        right_value = right.strip("\"'")
        return str(left_value) == right_value
    if "!=" in normalized:
        left, right = [item.strip() for item in normalized.split("!=", 1)]
        left_value = _resolve_field(context, left)
        right_value = right.strip("\"'")
        return str(left_value) != right_value
    return bool(_resolve_field(context, normalized))



def _render_payload(payload: dict[str, Any], context: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    rendered: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            pointer = value[2:-1]
            source = {"context": context, "state": state}
            rendered[key] = _resolve_field(source, pointer)
        else:
            rendered[key] = value
    return rendered



def _now_iso() -> str:
    return _to_iso(datetime.now(timezone.utc))



def _to_iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")



def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
