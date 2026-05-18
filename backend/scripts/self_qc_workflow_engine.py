"""Self-QC checks for B4-P03 workflow engine."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.event_bus import Event
from src.workflow_engine import ALLOWED_ACTION_TYPES, WorkflowEngine, build_canonical_workflows


def assert_dsl_supported() -> None:
    engine = WorkflowEngine()
    for workflow in build_canonical_workflows():
        engine.register_workflow(workflow)


def assert_all_workflows_executable() -> None:
    engine = WorkflowEngine()
    workflows = build_canonical_workflows()
    for workflow in workflows:
        engine.register_workflow(workflow)

    for index, workflow in enumerate(workflows, start=1):
        event = Event(
            event_name=workflow.triggers.events[0],
            event_id=f"evt-selfqc-{index}",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-self-qc",
            payload={"id": f"entity-{index}"},
        )
        execution = engine.start_workflow(workflow.workflow_key, event=event)
        if execution.status not in {"completed", "waiting"}:
            raise AssertionError(f"Workflow did not execute successfully: {workflow.workflow_key}")


def assert_no_undefined_steps() -> None:
    workflows = build_canonical_workflows()
    for workflow in workflows:
        for step in workflow.sequencing.steps:
            if step.action not in workflow.actions:
                raise AssertionError(f"Undefined step action in {workflow.workflow_key}: {step.action}")
            action = workflow.actions[step.action]
            if action.type not in ALLOWED_ACTION_TYPES:
                raise AssertionError(f"Unsupported action type in {workflow.workflow_key}: {action.type}")


def main() -> None:
    assert_dsl_supported()
    assert_all_workflows_executable()
    assert_no_undefined_steps()
    print("Self-QC score: 10/10")


if __name__ == "__main__":
    main()
