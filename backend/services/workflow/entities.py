"""Workflow automation entities for trigger/action execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class TriggerType(str, Enum):
    LEAD_CREATED = "lead_created"
    PAYMENT_RECEIVED = "payment_received"
    INACTIVITY = "inactivity"


class ActionType(str, Enum):
    SEND_MESSAGE = "send_message"
    CREATE_TASK = "create_task"
    UPDATE_STAGE = "update_stage"


@dataclass(frozen=True)
class WorkflowEvent:
    event_id: str
    tenant_id: str
    trigger: TriggerType
    occurred_at: datetime
    payload: dict[str, object]


@dataclass(frozen=True)
class RuleCondition:
    field: str
    operator: str
    value: object


@dataclass(frozen=True)
class ActionDefinition:
    action_id: str
    action_type: ActionType
    params: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowRule:
    rule_id: str
    trigger: TriggerType
    conditions: tuple[RuleCondition, ...]
    actions: tuple[ActionDefinition, ...]


@dataclass(frozen=True)
class AutomationResult:
    event_id: str
    rule_id: str
    executed_action_ids: tuple[str, ...]
    executed_at: datetime


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
