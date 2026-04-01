"""Workflow DSL entities and validation primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


TriggerMode = Literal["any", "all"]
ConditionMatch = Literal["all", "any"]
SequencingStrategy = Literal["linear", "branching"]
OnError = Literal["fail_fast", "continue", "compensate"]
ActionType = Literal["emit_event", "call_service", "notify", "mutate_state", "wait"]
InstanceStatus = Literal[
    "pending",
    "in_progress",
    "running",
    "waiting",
    "recovering",
    "completed",
    "failed",
    "failed_retryable",
    "dead_lettered",
    "stopped",
]
ConditionOp = Literal["exists", "eq", "neq", "in", "not_in", "gt", "gte", "lt", "lte"]
FailureDisposition = Literal["retryable", "terminal"]


class WorkflowValidationError(ValueError):
    """Raised when a workflow definition cannot be validated."""


class WorkflowNotFoundError(LookupError):
    """Raised when a workflow key is unknown."""


class WorkflowGraphValidationError(WorkflowValidationError):
    """Raised when a graph-based builder payload is invalid."""


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
class RetryPolicy:
    max_attempts: int = 3
    backoff_seconds: int = 2
    max_backoff_seconds: int = 60
    retryable_error_codes: tuple[str, ...] = (
        "timeout",
        "rate_limited",
        "service_unavailable",
        "deadlock",
        "conflict_retryable",
    )
    terminal_error_codes: tuple[str, ...] = (
        "validation_error",
        "not_found",
        "authorization_error",
        "bad_request",
        "compensation_failed",
    )
    dead_letter_after_attempts: int = 10


@dataclass(frozen=True)
class WorkflowDefinition:
    workflow_key: str
    version: str
    metadata: dict[str, Any]
    triggers: TriggerDefinition
    conditions: ConditionDefinition
    sequencing: SequencingDefinition
    actions: dict[str, ActionDefinition]
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    compensations: dict[str, ActionDefinition] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    execution_id: str
    workflow_key: str
    tenant_id: str
    status: InstanceStatus
    context: dict[str, Any]
    current_step_id: str | None
    started_at: str
    updated_at: str
    completed_at: str | None = None
    waiting_until: str | None = None
    state: dict[str, Any] = field(default_factory=dict)
    step_log: list[dict[str, Any]] = field(default_factory=list)
    error_message: str | None = None
    last_successful_step_id: str | None = None
    recovery_state: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowGraphNode:
    id: str
    action_type: ActionType
    service: str
    operation: str
    input: dict[str, Any] = field(default_factory=dict)
    emits: tuple[str, ...] = ()
    when: str | None = None
    timeout: str | None = None
    retries: int = 0


@dataclass(frozen=True)
class WorkflowGraphEdge:
    source: str
    target: str
    label: str | None = None


@dataclass(frozen=True)
class WorkflowBuilderGraph:
    workflow_key: str
    version: str
    metadata: dict[str, Any]
    triggers: TriggerDefinition
    conditions: ConditionDefinition
    nodes: tuple[WorkflowGraphNode, ...]
    edges: tuple[WorkflowGraphEdge, ...]
    start_node_id: str
