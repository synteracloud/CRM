from __future__ import annotations

import unittest

from src.event_bus import Event
from src.workflow_engine import (
    API_ENDPOINTS,
    WorkflowApi,
    ActionDefinition,
    SequencingDefinition,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowStep,
    WorkflowValidationError,
    build_canonical_workflows,
)


class WorkflowEngineTests(unittest.TestCase):
    def test_event_trigger_starts_and_completes_workflow(self) -> None:
        engine = WorkflowEngine()
        for workflow in build_canonical_workflows():
            engine.register_workflow(workflow)

        event = Event(
            event_name="lead.converted.v1",
            event_id="evt-1",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-1",
            payload={"lead_id": "lead-1"},
        )
        started = engine.handle_event(event)

        lead_runs = [item for item in started if item.workflow_key == "lead_intake_assignment_conversion"]
        self.assertEqual(len(lead_runs), 1)
        self.assertEqual(lead_runs[0].status, "completed")
        self.assertTrue(any(log.get("step_id") == "run_conversion" for log in lead_runs[0].step_log))

    def test_wait_step_transitions_waiting_then_resumes(self) -> None:
        engine = WorkflowEngine()
        branch = WorkflowDefinition(
            workflow_key="wait_test_workflow",
            version="v1",
            metadata={"name": "Wait Test"},
            triggers=build_canonical_workflows()[0].triggers,
            conditions=build_canonical_workflows()[0].conditions,
            sequencing=build_canonical_workflows()[0].sequencing,
            actions=build_canonical_workflows()[0].actions,
        )
        # clone with a simple wait-driven path
        branch = WorkflowDefinition(
            workflow_key="wait_test_workflow",
            version="v1",
            metadata={"name": "Wait Test"},
            triggers=branch.triggers,
            conditions=branch.conditions,
            sequencing=SequencingDefinition(
                strategy="linear",
                on_error="fail_fast",
                steps=(
                    WorkflowStep("first", "first"),
                    WorkflowStep("wait", "wait"),
                    WorkflowStep("last", "last"),
                ),
            ),
            actions={
                "first": ActionDefinition("call_service", "X", "first"),
                "wait": ActionDefinition("wait", "Workflow Automation Service", "pause", {"duration_seconds": 1}),
                "last": ActionDefinition("call_service", "X", "last"),
            },
        )
        engine.register_workflow(branch)

        event = Event(
            event_name=branch.triggers.events[0],
            event_id="evt-2",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-2",
            payload={},
        )
        execution = engine.start_workflow("wait_test_workflow", event=event)
        self.assertEqual(execution.status, "waiting")

        resumed = engine.resume_due_waits("2030-01-01T00:00:00Z")
        self.assertEqual(len(resumed), 1)
        self.assertEqual(resumed[0].status, "completed")

    def test_validation_rejects_undefined_step_actions(self) -> None:
        engine = WorkflowEngine()
        workflow = build_canonical_workflows()[0]
        broken = WorkflowDefinition(
            workflow_key="broken_workflow",
            version=workflow.version,
            metadata=workflow.metadata,
            triggers=workflow.triggers,
            conditions=workflow.conditions,
            sequencing=SequencingDefinition(
                strategy="linear",
                on_error="fail_fast",
                steps=(WorkflowStep("bad", "missing_action"),),
            ),
            actions={},
        )
        with self.assertRaises(WorkflowValidationError):
            engine.register_workflow(broken)


class WorkflowApiTests(unittest.TestCase):
    def test_start_and_stop_api(self) -> None:
        engine = WorkflowEngine()
        workflow = build_canonical_workflows()[0]
        engine.register_workflow(workflow)
        api = WorkflowApi(engine)

        event = Event(
            event_name=workflow.triggers.events[0],
            event_id="evt-3",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-3",
            payload={},
        )
        response = api.start_workflow(workflow.workflow_key, event=event, context=None, request_id="req-1")
        self.assertIn("data", response)
        execution_id = response["data"]["execution_id"]

        stopped = api.stop_workflow(execution_id, request_id="req-2")
        self.assertIn("data", stopped)
        self.assertEqual(API_ENDPOINTS["start_workflow"]["method"], "POST")


class WorkflowCatalogCoverageTests(unittest.TestCase):
    def test_all_canonical_workflows_execute_from_trigger_events(self) -> None:
        engine = WorkflowEngine()
        workflows = build_canonical_workflows()
        for workflow in workflows:
            engine.register_workflow(workflow)

        for index, workflow in enumerate(workflows, start=1):
            event = Event(
                event_name=workflow.triggers.events[0],
                event_id=f"evt-catalog-{index}",
                occurred_at="2026-03-26T00:00:00Z",
                tenant_id="tenant-catalog",
                payload={"id": f"entity-{index}"},
            )
            execution = engine.start_workflow(workflow.workflow_key, event=event)
            self.assertIn(execution.status, {"completed", "waiting"})


if __name__ == "__main__":
    unittest.main()
