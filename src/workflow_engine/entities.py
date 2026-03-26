"""Workflow DSL entities and validation primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


TriggerMode = Literal["any", "all"]
ConditionMatch = Literal["all", "any"]
SequencingStrategy = Literal["linear", "branching"]
OnError = Literal["fail_fast", "continue", "compensate"]
ActionType = Literal["emit_event", "call_service", "notify", "mutate_state", "wait"]
InstanceStatus = Literal["running", "waiting", "completed", "failed", "stopped"]
ConditionOp = Literal["exists", "eq", "neq", "in", "not_in", "gt", "gte", "lt", "lte"]


class WorkflowValidationError(ValueError):
    """Raised when a workflow definition cannot be validated."""


class WorkflowNotFoundError(LookupError):
    """Raised when a workflow key is unknown."""


@dataclass(frozen=True)
class TriggerDefinition:
    mode: TriggerMode
    events: tuple[str, ...]
    schedule: str | None = None
    manual: bool = False


@dataclass(frozen=True)
class ConditionRule:
    field: str
    op: ConditionOp
    value: Any = None


@dataclass(frozen=True)
class ConditionDefinition:
    match: ConditionMatch = "all"
    rules: tuple[ConditionRule, ...] = ()


@dataclass(frozen=True)
class WorkflowStep:
    id: str
    action: str
    when: str | None = None
    timeout: str | None = None
    retries: int = 0
    next: str | None = None


@dataclass(frozen=True)
class SequencingDefinition:
    strategy: SequencingStrategy
    on_error: OnError
    steps: tuple[WorkflowStep, ...]


@dataclass(frozen=True)
class ActionDefinition:
    type: ActionType
    service: str
    operation: str
    input: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] | None = None
    emits: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkflowDefinition:
    workflow_key: str
    version: str
    metadata: dict[str, Any]
    triggers: TriggerDefinition
    conditions: ConditionDefinition
    sequencing: SequencingDefinition
    actions: dict[str, ActionDefinition]


@dataclass
class WorkflowExecution:
    execution_id: str
    workflow_key: str
    tenant_id: str
    status: InstanceStatus
    context: dict[str, Any]
    current_step_id: str | None
    started_at: str
    completed_at: str | None = None
    waiting_until: str | None = None
    state: dict[str, Any] = field(default_factory=dict)
    step_log: list[dict[str, Any]] = field(default_factory=list)
    error_message: str | None = None
