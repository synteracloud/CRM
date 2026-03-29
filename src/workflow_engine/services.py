"""Workflow execution engine with trigger handling and action execution primitives."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from src.event_bus import EVENT_NAMES, Event

from .entities import (
    ActionDefinition,
    ConditionDefinition,
    ConditionRule,
    FailureDisposition,
    RetryPolicy,
    SequencingDefinition,
    WorkflowBuilderGraph,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowGraphEdge,
    WorkflowGraphNode,
    WorkflowGraphValidationError,
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
            if action.operation.startswith("fail:"):
                error_code = action.operation.split(":", 1)[1].strip() or "service_unavailable"
                return {"service": action.service, "operation": action.operation, "input": rendered_input, "ok": False, "error_code": error_code}
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

    def create_workflow_from_graph(self, graph: WorkflowBuilderGraph, overwrite: bool = False) -> WorkflowDefinition:
        if not overwrite and graph.workflow_key in self._definitions:
            raise WorkflowValidationError(f"Workflow already exists: {graph.workflow_key}")
        definition = self._graph_to_definition(graph)
        return self.register_workflow(definition)

    def update_workflow_from_graph(self, workflow_key: str, graph: WorkflowBuilderGraph) -> WorkflowDefinition:
        if workflow_key not in self._definitions:
            raise WorkflowNotFoundError(f"Workflow not found: {workflow_key}")
        if workflow_key != graph.workflow_key:
            raise WorkflowValidationError("workflow_key mismatch between path and graph payload")
        return self.create_workflow_from_graph(graph, overwrite=True)

    def export_workflow_graph(self, workflow_key: str) -> WorkflowBuilderGraph:
        definition = self.get_workflow(workflow_key)
        nodes = tuple(
            WorkflowGraphNode(
                id=step.id,
                action_type=definition.actions[step.action].type,
                service=definition.actions[step.action].service,
                operation=definition.actions[step.action].operation,
                input=definition.actions[step.action].input,
                emits=definition.actions[step.action].emits,
                when=step.when,
                timeout=step.timeout,
                retries=step.retries,
            )
            for step in definition.sequencing.steps
        )
        edges: list[WorkflowGraphEdge] = []
        for index, step in enumerate(definition.sequencing.steps):
            if definition.sequencing.strategy == "branching":
                if step.next and step.next != "end":
                    edges.append(WorkflowGraphEdge(source=step.id, target=step.next))
            elif index + 1 < len(definition.sequencing.steps):
                edges.append(WorkflowGraphEdge(source=step.id, target=definition.sequencing.steps[index + 1].id))

        return WorkflowBuilderGraph(
            workflow_key=definition.workflow_key,
            version=definition.version,
            metadata=definition.metadata,
            triggers=definition.triggers,
            conditions=definition.conditions,
            nodes=nodes,
            edges=tuple(edges),
            start_node_id=definition.sequencing.steps[0].id,
        )

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

    def self_qc_trigger_action_integrity(self) -> dict[str, Any]:
        checks = {
            "all_triggers_map_to_event_catalog": True,
            "no_undefined_actions": True,
            "all_action_types_supported": True,
            "all_workflows_have_steps": True,
            "all_step_references_resolve": True,
            "sequencing_valid": True,
            "all_workflows_versioned": True,
            "conditions_structurally_valid": True,
            "trigger_modes_valid": True,
            "tenant_context_supported": True,
            "retry_rules_deterministic": True,
            "no_infinite_retries": True,
            "compensation_defined_for_critical_flows": True,
        }
        issues: list[str] = []

        for workflow in self._definitions.values():
            if not workflow.triggers.events or any(event not in EVENT_NAMES for event in workflow.triggers.events):
                checks["all_triggers_map_to_event_catalog"] = False
                issues.append(f"unknown trigger event(s) in {workflow.workflow_key}")

            if workflow.triggers.mode not in {"any", "all"}:
                checks["trigger_modes_valid"] = False
                issues.append(f"invalid trigger mode in {workflow.workflow_key}")

            if not workflow.version:
                checks["all_workflows_versioned"] = False
                issues.append(f"missing version in {workflow.workflow_key}")

            if not workflow.sequencing.steps:
                checks["all_workflows_have_steps"] = False
                issues.append(f"no steps in {workflow.workflow_key}")
                continue

            if workflow.sequencing.strategy not in {"linear", "branching"}:
                checks["sequencing_valid"] = False
                issues.append(f"invalid sequencing strategy in {workflow.workflow_key}")

            action_ids = set(workflow.actions)
            step_ids = {step.id for step in workflow.sequencing.steps}

            for step in workflow.sequencing.steps:
                if step.action not in action_ids:
                    checks["no_undefined_actions"] = False
                    checks["all_step_references_resolve"] = False
                    issues.append(f"undefined action {step.action} in {workflow.workflow_key}")
                    continue

                action = workflow.actions[step.action]
                if action.type not in ALLOWED_ACTION_TYPES:
                    checks["all_action_types_supported"] = False
                    issues.append(f"unsupported action type {action.type} in {workflow.workflow_key}")

                if workflow.sequencing.strategy == "branching" and step.next and step.next != "end" and step.next not in step_ids:
                    checks["sequencing_valid"] = False
                    issues.append(f"invalid next step '{step.next}' in {workflow.workflow_key}")
                attempts_cap = max(step.retries + 1, workflow.retry_policy.max_attempts)
                if attempts_cap <= 0:
                    checks["no_infinite_retries"] = False
                    issues.append(f"invalid retries policy for step={step.id} in {workflow.workflow_key}")

            for rule in workflow.conditions.rules:
                if not rule.field:
                    checks["conditions_structurally_valid"] = False
                    issues.append(f"invalid condition rule in {workflow.workflow_key}")
            if workflow.retry_policy.backoff_seconds <= 0 or workflow.retry_policy.max_backoff_seconds <= 0:
                checks["retry_rules_deterministic"] = False
                issues.append(f"invalid backoff configuration in {workflow.workflow_key}")
            if workflow.retry_policy.max_attempts <= 0:
                checks["no_infinite_retries"] = False
                issues.append(f"invalid max_attempts in {workflow.workflow_key}")
            if workflow.sequencing.on_error == "compensate":
                critical_steps = [
                    step for step in workflow.sequencing.steps if definition_action_is_critical(workflow.actions[step.action])
                ]
                missing = [step.id for step in critical_steps if step.action not in workflow.compensations]
                if missing:
                    checks["compensation_defined_for_critical_flows"] = False
                    issues.append(f"missing compensations in {workflow.workflow_key} for steps={missing}")

        score = sum(1 for passed in checks.values() if passed)
        return {"score": score, "checks": checks, "issues": sorted(set(issues))}

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
            if not self._execute_step_with_retry(definition, step, action, execution):
                return

        execution.status = "completed"
        execution.completed_at = _now_iso()

    def _execute_step_with_retry(
        self, definition: WorkflowDefinition, step: WorkflowStep, action: ActionDefinition, execution: WorkflowExecution
    ) -> bool:
        max_attempts = min(max(step.retries + 1, definition.retry_policy.max_attempts), 25)
        for attempt in range(1, max_attempts + 1):
            result = self._action_engine.execute(action, execution.context, execution.state)
            if result.get("ok", True):
                execution.state[step.action] = result
                execution.step_log.append(
                    {"step_id": step.id, "action": step.action, "result": result, "attempt": attempt, "at": _now_iso()}
                )
                execution.current_step_id = self._resolve_next_step(definition, step)
                return True

            error_code = str(result.get("error_code", "service_unavailable"))
            disposition = _classify_failure(error_code, definition.retry_policy)
            execution.step_log.append(
                {
                    "step_id": step.id,
                    "action": step.action,
                    "attempt": attempt,
                    "error_code": error_code,
                    "disposition": disposition,
                    "at": _now_iso(),
                }
            )
            if disposition == "retryable" and attempt < max_attempts:
                backoff = _compute_backoff_seconds(attempt, definition.retry_policy)
                execution.step_log.append(
                    {
                        "step_id": step.id,
                        "action": "retry.scheduled",
                        "attempt": attempt + 1,
                        "backoff_seconds": backoff,
                        "at": _now_iso(),
                    }
                )
                continue
            self._handle_terminal_failure(definition, step, error_code, execution)
            return False
        self._handle_terminal_failure(definition, step, "retries_exhausted", execution)
        return False

    def _handle_terminal_failure(
        self, definition: WorkflowDefinition, step: WorkflowStep, error_code: str, execution: WorkflowExecution
    ) -> None:
        execution.status = "failed"
        execution.error_message = f"Step failed: {step.id} error_code={error_code}"
        execution.step_log.append({"step_id": step.id, "action": "step.failed", "error_code": error_code, "at": _now_iso()})
        if definition.sequencing.on_error == "compensate":
            self._run_compensations(definition, execution)
        execution.completed_at = _now_iso()

    def _run_compensations(self, definition: WorkflowDefinition, execution: WorkflowExecution) -> None:
        completed_actions = [
            entry["action"]
            for entry in execution.step_log
            if entry.get("result") and isinstance(entry.get("action"), str) and entry["action"] in definition.actions
        ]
        for action_ref in reversed(completed_actions):
            compensation = definition.compensations.get(action_ref)
            if not compensation:
                continue
            result = self._action_engine.execute(compensation, execution.context, execution.state)
            if result.get("ok", True):
                execution.step_log.append(
                    {"action": "compensation.executed", "for_action": action_ref, "result": result, "at": _now_iso()}
                )
            else:
                execution.step_log.append(
                    {"action": "compensation.failed", "for_action": action_ref, "result": result, "at": _now_iso()}
                )
                execution.error_message = (
                    f"{execution.error_message}; compensation_failed_for={action_ref}:{result.get('error_code')}"
                )

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
        if definition.retry_policy.max_attempts <= 0:
            raise WorkflowValidationError("retry_policy.max_attempts must be positive")
        if definition.retry_policy.backoff_seconds <= 0 or definition.retry_policy.max_backoff_seconds <= 0:
            raise WorkflowValidationError("retry_policy backoff values must be positive")
        if definition.retry_policy.backoff_seconds > definition.retry_policy.max_backoff_seconds:
            raise WorkflowValidationError("retry_policy.backoff_seconds cannot exceed max_backoff_seconds")
        unknown_compensation_refs = sorted(set(definition.compensations) - set(definition.actions))
        if unknown_compensation_refs:
            raise WorkflowValidationError(f"Compensation references unknown actions: {unknown_compensation_refs}")

    def _next_execution_id(self, workflow_key: str) -> str:
        self._execution_counter += 1
        return f"wfexec::{workflow_key}::{self._execution_counter}"

    def _graph_to_definition(self, graph: WorkflowBuilderGraph) -> WorkflowDefinition:
        self._validate_graph(graph)
        node_map = {node.id: node for node in graph.nodes}
        outgoing: dict[str, list[str]] = {}
        incoming: dict[str, int] = {node.id: 0 for node in graph.nodes}
        for edge in graph.edges:
            outgoing.setdefault(edge.source, []).append(edge.target)
            incoming[edge.target] += 1

        strategy = "branching" if any(len(targets) > 1 for targets in outgoing.values()) else "linear"
        ordered_ids = _topological_order(graph.start_node_id, outgoing, incoming)
        steps: list[WorkflowStep] = []
        actions: dict[str, ActionDefinition] = {}
        for index, node_id in enumerate(ordered_ids):
            node = node_map[node_id]
            action_ref = f"action_{node.id}"
            next_pointer: str | None = None
            if strategy == "branching":
                targets = outgoing.get(node.id, [])
                next_pointer = targets[0] if targets else "end"
            step = WorkflowStep(
                id=node.id,
                action=action_ref,
                when=node.when,
                timeout=node.timeout,
                retries=node.retries,
                next=next_pointer,
            )
            if strategy == "linear" and index + 1 < len(ordered_ids):
                step = WorkflowStep(
                    id=node.id,
                    action=action_ref,
                    when=node.when,
                    timeout=node.timeout,
                    retries=node.retries,
                )
            steps.append(step)
            actions[action_ref] = ActionDefinition(
                type=node.action_type,
                service=node.service,
                operation=node.operation,
                input=node.input,
                emits=node.emits,
            )

        return WorkflowDefinition(
            workflow_key=graph.workflow_key,
            version=graph.version,
            metadata=graph.metadata,
            triggers=graph.triggers,
            conditions=graph.conditions,
            sequencing=asdict_to_sequence(strategy, tuple(steps)),
            actions=actions,
        )

    @staticmethod
    def _validate_graph(graph: WorkflowBuilderGraph) -> None:
        if not graph.nodes:
            raise WorkflowGraphValidationError("Graph must include at least one node")
        node_ids = [node.id for node in graph.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise WorkflowGraphValidationError("Graph nodes must have unique ids")
        if graph.start_node_id not in set(node_ids):
            raise WorkflowGraphValidationError("start_node_id must reference an existing node")

        node_set = set(node_ids)
        incoming: dict[str, int] = {node_id: 0 for node_id in node_ids}
        outgoing: dict[str, int] = {node_id: 0 for node_id in node_ids}
        edge_pairs: set[tuple[str, str]] = set()
        for edge in graph.edges:
            if edge.source not in node_set or edge.target not in node_set:
                raise WorkflowGraphValidationError("Graph edges must reference valid node ids")
            if edge.source == edge.target:
                raise WorkflowGraphValidationError("Self-loop edges are not allowed")
            pair = (edge.source, edge.target)
            if pair in edge_pairs:
                raise WorkflowGraphValidationError("Duplicate graph edge found")
            edge_pairs.add(pair)
            outgoing[edge.source] += 1
            incoming[edge.target] += 1

        end_nodes = [node_id for node_id, degree in outgoing.items() if degree == 0]
        if not end_nodes:
            raise WorkflowGraphValidationError("Graph must have at least one terminal step")
        if incoming[graph.start_node_id] > 0:
            raise WorkflowGraphValidationError("start_node_id cannot have inbound edges")
        unreachable = _collect_unreachable(graph.start_node_id, graph.edges, node_set)
        if unreachable:
            raise WorkflowGraphValidationError(f"Graph contains unreachable steps: {sorted(unreachable)}")



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


def asdict_to_sequence(strategy: str, steps: tuple[WorkflowStep, ...]) -> SequencingDefinition:
    return SequencingDefinition(strategy=strategy, on_error="fail_fast", steps=steps)


def definition_action_is_critical(action: ActionDefinition) -> bool:
    return action.type in {"call_service", "mutate_state", "emit_event"}


def _classify_failure(error_code: str, policy: RetryPolicy) -> FailureDisposition:
    if error_code in policy.terminal_error_codes:
        return "terminal"
    if error_code in policy.retryable_error_codes:
        return "retryable"
    return "terminal"


def _compute_backoff_seconds(attempt: int, policy: RetryPolicy) -> int:
    exponent = max(attempt - 1, 0)
    return min(policy.backoff_seconds * (2**exponent), policy.max_backoff_seconds)


def _collect_unreachable(start_node_id: str, edges: tuple[WorkflowGraphEdge, ...], node_set: set[str]) -> set[str]:
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_set}
    for edge in edges:
        adjacency[edge.source].append(edge.target)
    visited: set[str] = set()
    stack = [start_node_id]
    while stack:
        node_id = stack.pop()
        if node_id in visited:
            continue
        visited.add(node_id)
        stack.extend(adjacency[node_id])
    return node_set - visited


def _topological_order(start_node_id: str, outgoing: dict[str, list[str]], incoming: dict[str, int]) -> list[str]:
    in_degree = incoming.copy()
    order: list[str] = []
    queue = [start_node_id]
    while queue:
        node_id = queue.pop(0)
        if node_id in order:
            continue
        order.append(node_id)
        for target in outgoing.get(node_id, []):
            in_degree[target] -= 1
            if in_degree[target] == 0:
                queue.append(target)
    if len(order) != len(in_degree):
        raise WorkflowGraphValidationError("Graph must be acyclic and connected from start node")
    return order
