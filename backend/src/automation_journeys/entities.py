"""Domain entities for automation journeys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


StepAction = Literal["email", "update", "assign", "delay"]
InstanceStatus = Literal["running", "waiting", "completed", "failed", "stopped"]


class JourneyValidationError(ValueError):
    """Raised when a journey definition is invalid."""


class JourneyNotFoundError(LookupError):
    """Raised when a journey cannot be found."""


@dataclass(frozen=True)
class JourneyStep:
    step_id: str
    action: StepAction
    config: dict[str, Any] = field(default_factory=dict)
    delay_seconds: int = 0


@dataclass(frozen=True)
class JourneyDefinition:
    journey_id: str
    tenant_id: str
    name: str
    trigger_event: str
    steps: tuple[JourneyStep, ...]
    is_active: bool = True


@dataclass
class JourneyInstance:
    instance_id: str
    tenant_id: str
    journey_id: str
    trigger_event: str
    trigger_event_id: str
    status: InstanceStatus
    current_step_index: int
    started_at: str
    waiting_until: str | None = None
    completed_at: str | None = None
    error_message: str | None = None
    execution_log: list[dict[str, Any]] = field(default_factory=list)
