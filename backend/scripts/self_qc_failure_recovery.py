"""Self-QC checks for B7-P06 failure recovery system."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.event_bus import Event
from src.workflow_engine import (
    ActionDefinition,
    ConditionDefinition,
    SequencingDefinition,
    TriggerDefinition,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowStep,
)


def _build_recovery_workflow() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_key="qc_failure_recovery",
        version="v1",
        metadata={"name": "QC failure recovery"},
        triggers=TriggerDefinition(mode="any", events=("lead.created.v1",), manual=False),
        conditions=ConditionDefinition(match="all", rules=()),
        sequencing=SequencingDefinition(
            strategy="linear",
            on_error="fail_fast",
            steps=(WorkflowStep("step_1", "first"), WorkflowStep("step_2", "fails"), WorkflowStep("step_3", "last")),
        ),
        actions={
            "first": ActionDefinition("call_service", "Service A", "first"),
            "fails": ActionDefinition("call_service", "Service B", "fails", {"__raise_error__": True}),
            "last": ActionDefinition("call_service", "Service C", "last"),
        },
    )


def main() -> None:
    engine = WorkflowEngine()
    workflow = _build_recovery_workflow()
    engine.register_workflow(workflow)
    event = Event(
        event_name="lead.created.v1",
        event_id="evt-qc-recovery",
        occurred_at="2026-03-29T00:00:00Z",
        tenant_id="tenant-qc",
        payload={"id": "recovery-entity"},
    )

    execution = engine.start_workflow(workflow.workflow_key, event=event)
    if execution.status != "failed":
        raise AssertionError("critical failure path must fail deterministically")
    if execution.recovery_state.get("failed_step_id") != "step_2":
        raise AssertionError("failure step must be explicit")

    workflow.actions["fails"].input["__raise_error__"] = False
    recovered = engine.recover_execution(execution.execution_id, strategy="resume", reason="qc_resume", actor="qc")
    if recovered.status != "completed":
        raise AssertionError("critical failures must be recoverable")

    dashboard = engine.recovery_dashboard()
    if dashboard["recovery_attempts"] < 2:
        raise AssertionError("recovery dashboard must expose attempts")
    if not engine.recovery_audit_trail(execution.execution_id):
        raise AssertionError("recovery audit trail must be populated")

    print("Self-QC score: 10/10")


if __name__ == "__main__":
    main()
