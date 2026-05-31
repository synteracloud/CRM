"""Workflow domain entities: status enums, step types, DSL validation.

Domain spec: backend/docs/infrastructure/workflow-catalog.md
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Optional


class WorkflowStatus(str, Enum):
    DRAFT    = "draft"
    ACTIVE   = "active"
    PAUSED   = "paused"
    ARCHIVED = "archived"


class ExecutionStatus(str, Enum):
    RUNNING   = "running"
    SUCCEEDED = "succeeded"
    FAILED    = "failed"
    RETRYING  = "retrying"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCEEDED = "succeeded"
    FAILED    = "failed"
    SKIPPED   = "skipped"


class StepType(str, Enum):
    CONDITION    = "condition"
    ACTION       = "action"
    NOTIFICATION = "notification"
    DELAY        = "delay"
    FORK         = "fork"
    JOIN         = "join"


# Allowed workflow status transitions
WORKFLOW_TRANSITIONS: dict[str, list[str]] = {
    "draft":    ["active", "archived"],
    "active":   ["paused", "archived"],
    "paused":   ["active", "archived"],
    "archived": [],   # terminal
}

# Execution terminal states
TERMINAL_EXECUTION_STATUSES = {ExecutionStatus.SUCCEEDED, ExecutionStatus.CANCELLED}

# Retryable execution states
RETRYABLE_EXECUTION_STATUSES = {ExecutionStatus.FAILED, ExecutionStatus.RETRYING}


class WorkflowDomainError(ValueError):
    """Raised when a workflow domain rule is violated."""


def validate_workflow_transition(from_status: str, to_status: str) -> None:
    allowed = WORKFLOW_TRANSITIONS.get(from_status, [])
    if to_status not in allowed:
        raise WorkflowDomainError(
            f"Workflow status transition {from_status!r} → {to_status!r} is not permitted. "
            f"Allowed: {allowed}"
        )


def validate_steps_dsl(steps: list[dict]) -> list[str]:
    """
    Validate a steps DSL list.
    Returns a list of validation error strings (empty = valid).
    """
    errors: list[str] = []
    if not steps:
        errors.append("Workflow must have at least one step.")
        return errors

    seen_ids: set[str] = set()
    valid_types = {t.value for t in StepType}

    for i, step in enumerate(steps):
        step_id   = step.get("id") or step.get("step_id") or f"step-{i}"
        step_name = step.get("name", f"Step {i}")
        step_type = step.get("type", "action")

        if step_id in seen_ids:
            errors.append(f"Duplicate step id {step_id!r} at index {i}.")
        seen_ids.add(step_id)

        if step_type not in valid_types:
            errors.append(
                f"Step {step_name!r} (index {i}): invalid type {step_type!r}. "
                f"Must be one of {sorted(valid_types)}."
            )

        if step_type == StepType.ACTION and not step.get("action"):
            errors.append(f"Step {step_name!r} (index {i}): 'action' steps must have an 'action' key.")

        if step_type == StepType.CONDITION and not step.get("condition"):
            errors.append(f"Step {step_name!r} (index {i}): 'condition' steps must have a 'condition' key.")

    return errors


# Canonical workflow definitions seeded from workflow-catalog.md
# Used to bootstrap WorkflowDefinition records on tenant provisioning.
CATALOG_WORKFLOWS: list[dict] = [
    {
        "workflow_key":   "lead_followup_enforcement",
        "name":           "Lead Follow-up Enforcement",
        "trigger_events": ["lead.idle.v1"],
        "steps_dsl": [
            {"id": "s1", "type": "condition",    "name": "Check idle threshold", "condition": "lead.idle_days > threshold"},
            {"id": "s2", "type": "action",       "name": "Create follow-up task", "action": "create_followup_task"},
            {"id": "s3", "type": "notification", "name": "Notify owner",          "action": "send_whatsapp_alert"},
        ],
        "is_system": True,
    },
    {
        "workflow_key":   "collections_reminder",
        "name":           "Collections Auto-Reminder",
        "trigger_events": ["invoice.overdue.v1"],
        "steps_dsl": [
            {"id": "s1", "type": "action",       "name": "Load invoice",       "action": "load_invoice"},
            {"id": "s2", "type": "notification", "name": "Send WhatsApp",      "action": "send_whatsapp"},
        ],
        "is_system": True,
    },
    {
        "workflow_key":   "sla_breach_notify",
        "name":           "SLA Breach Notification",
        "trigger_events": ["case.sla.breached.v1", "case.sla.first_response_breached.v1"],
        "steps_dsl": [
            {"id": "s1", "type": "action",       "name": "Load case",              "action": "load_case"},
            {"id": "s2", "type": "action",       "name": "Escalate case",          "action": "escalate_case"},
            {"id": "s3", "type": "notification", "name": "Notify supervisor",       "action": "notify_supervisor"},
            {"id": "s4", "type": "action",       "name": "Log escalation event",   "action": "log_event"},
        ],
        "is_system": True,
    },
    {
        "workflow_key":   "lead_assignment",
        "name":           "Lead Territory Assignment",
        "trigger_events": ["lead.created.v1"],
        "steps_dsl": [
            {"id": "s1", "type": "action", "name": "Evaluate territory", "action": "evaluate_territory"},
            {"id": "s2", "type": "action", "name": "Assign owner",       "action": "assign_owner"},
        ],
        "is_system": True,
    },
    {
        "workflow_key":   "opportunity_stage_notify",
        "name":           "Stage Change Notification",
        "trigger_events": ["opportunity.stage.changed.v1"],
        "steps_dsl": [
            {"id": "s1", "type": "condition",    "name": "Check notify config", "condition": "stage in notify_stages"},
            {"id": "s2", "type": "notification", "name": "Notify team",          "action": "send_stage_alert"},
            {"id": "s3", "type": "action",       "name": "Update forecast",      "action": "refresh_forecast"},
        ],
        "is_system": True,
    },
]
