from __future__ import annotations

import unittest

from src.event_bus import Event
from src.workflow_engine import (
    API_ENDPOINTS,
    ActionExecutionEngine,
    TriggerHandlingSystem,
    TriggerDefinition,
    WorkflowApi,
    ActionDefinition,
    SequencingDefinition,
    TriggerDefinition,
    ConditionDefinition,
    WorkflowBuilderGraph,
    WorkflowGraphEdge,
    WorkflowGraphNode,
    WorkflowGraphValidationError,
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

    def test_self_qc_reports_10_of_10_for_valid_registered_workflows(self) -> None:
        engine = WorkflowEngine()
        for workflow in build_canonical_workflows():
            engine.register_workflow(workflow)

        report = engine.self_qc_trigger_action_integrity()
        self.assertEqual(report["score"], 10)
        self.assertEqual(report["issues"], [])
        self.assertTrue(report["checks"]["all_triggers_map_to_event_catalog"])
        self.assertTrue(report["checks"]["no_undefined_actions"])

    def test_failure_recovery_resume_recovers_failed_execution(self) -> None:
        engine = WorkflowEngine()
        workflow = WorkflowDefinition(
            workflow_key="failure_recovery_resume",
            version="v1",
            metadata={"name": "Failure recovery resume"},
            triggers=TriggerDefinition(mode="any", events=("lead.created.v1",), manual=False),
            conditions=ConditionDefinition(match="all", rules=()),
            sequencing=SequencingDefinition(
                strategy="linear",
                on_error="fail_fast",
                steps=(
                    WorkflowStep("s1", "first"),
                    WorkflowStep("s2", "fails_once"),
                    WorkflowStep("s3", "last"),
                ),
            ),
            actions={
                "first": ActionDefinition("call_service", "Service A", "first"),
                "fails_once": ActionDefinition("call_service", "Service B", "fails_once", {"__raise_error__": True}),
                "last": ActionDefinition("call_service", "Service C", "last"),
            },
        )
        engine.register_workflow(workflow)
        event = Event(
            event_name="lead.created.v1",
            event_id="evt-recovery-1",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-recovery",
            payload={"id": "lead-recovery"},
        )

        execution = engine.start_workflow("failure_recovery_resume", event=event)
        self.assertEqual(execution.status, "failed")
        self.assertEqual(execution.recovery_state["failed_step_id"], "s2")
        self.assertIn("RuntimeError", execution.error_message or "")

        # clear the injected failure and resume from the failed step
        workflow.actions["fails_once"].input["__raise_error__"] = False
        recovered = engine.recover_execution(execution.execution_id, strategy="resume", reason="operator_resume", actor="ops")
        self.assertEqual(recovered.status, "completed")
        self.assertEqual(recovered.recovery_state["mode"], "resume")
        self.assertEqual(recovered.recovery_state["attempt_count"], 1)
        audit = engine.recovery_audit_trail(execution.execution_id)
        self.assertTrue(any(item["action"] == "execution.failed" for item in audit))
        self.assertTrue(any(item["action"] == "recovery.completed" for item in audit))

    def test_replay_full_resets_state_and_audit_visible(self) -> None:
        engine = WorkflowEngine()
        workflow = WorkflowDefinition(
            workflow_key="failure_replay_full",
            version="v1",
            metadata={"name": "Failure replay full"},
            triggers=TriggerDefinition(mode="any", events=("lead.created.v1",), manual=False),
            conditions=ConditionDefinition(match="all", rules=()),
            sequencing=SequencingDefinition(
                strategy="linear",
                on_error="fail_fast",
                steps=(WorkflowStep("s1", "first"), WorkflowStep("s2", "last")),
            ),
            actions={
                "first": ActionDefinition("call_service", "Service A", "first"),
                "last": ActionDefinition("call_service", "Service B", "last"),
            },
        )
        engine.register_workflow(workflow)
        event = Event(
            event_name="lead.created.v1",
            event_id="evt-recovery-2",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-recovery",
            payload={"id": "lead-recovery-2"},
        )
        execution = engine.start_workflow("failure_replay_full", event=event)
        self.assertEqual(execution.status, "completed")
        self.assertIn("first", execution.state)

        replayed = engine.recover_execution(execution.execution_id, strategy="replay_full", reason="force_replay", actor="ops")
        self.assertEqual(replayed.status, "completed")
        self.assertIn("first", replayed.state)
        dashboard = engine.recovery_dashboard()
        self.assertGreaterEqual(dashboard["recovery_attempts"], 2)

    def test_stuck_workflow_recovery_and_visibility_hooks(self) -> None:
        engine = WorkflowEngine()
        branch = WorkflowDefinition(
            workflow_key="stuck_waiting_workflow",
            version="v1",
            metadata={"name": "Stuck waiting workflow"},
            triggers=TriggerDefinition(mode="any", events=("lead.created.v1",), manual=False),
            conditions=ConditionDefinition(match="all", rules=()),
            sequencing=SequencingDefinition(
                strategy="linear",
                on_error="fail_fast",
                steps=(WorkflowStep("s1", "first"), WorkflowStep("wait", "wait"), WorkflowStep("s2", "last")),
            ),
            actions={
                "first": ActionDefinition("call_service", "Service A", "first"),
                "wait": ActionDefinition("wait", "Workflow Automation Service", "pause", {"duration_seconds": 3600}),
                "last": ActionDefinition("call_service", "Service B", "last"),
            },
        )
        engine.register_workflow(branch)
        event = Event(
            event_name="lead.created.v1",
            event_id="evt-stuck-1",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-stuck",
            payload={"id": "stuck-entity"},
        )
        execution = engine.start_workflow("stuck_waiting_workflow", event=event)
        self.assertEqual(execution.status, "waiting")
        execution.updated_at = "2026-03-01T00:00:00Z"
        execution.waiting_until = "2026-03-01T00:10:00Z"

        recovered = engine.recover_stuck_workflows(stale_before_iso="2026-03-15T00:00:00Z", now_iso="2026-03-29T00:00:00Z")
        self.assertEqual(len(recovered), 1)
        self.assertIn(recovered[0].status, {"waiting", "completed"})
        dashboard = engine.recovery_dashboard()
        self.assertGreaterEqual(dashboard["recovery_attempts"], 2)
        self.assertIn("recoverable_failures", dashboard)


class TriggerAndActionEngineTests(unittest.TestCase):
    def test_trigger_system_respects_any_and_all_modes(self) -> None:
        workflows = build_canonical_workflows()
        trigger_system = TriggerHandlingSystem()
        for workflow in workflows:
            trigger_system.register(workflow)

        all_mode = WorkflowDefinition(
            workflow_key="all_mode_workflow",
            version="v1",
            metadata={"name": "All mode"},
            triggers=TriggerDefinition(mode="all", events=("lead.created.v1", "lead.converted.v1")),
            conditions=workflows[0].conditions,
            sequencing=SequencingDefinition(
                strategy="linear",
                on_error="fail_fast",
                steps=(WorkflowStep("s1", "a1"),),
            ),
            actions={"a1": ActionDefinition("call_service", "Service", "op")},
        )
        trigger_system.register(all_mode)

        first = Event(
            event_name="lead.created.v1",
            event_id="evt-a",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-a",
            payload={},
        )
        second = Event(
            event_name="lead.converted.v1",
            event_id="evt-b",
            occurred_at="2026-03-26T00:00:01Z",
            tenant_id="tenant-a",
            payload={},
        )
        self.assertFalse(trigger_system.trigger_matches(all_mode, first))
        self.assertTrue(trigger_system.trigger_matches(all_mode, second))

    def test_action_engine_executes_supported_action_types(self) -> None:
        engine = ActionExecutionEngine()
        context = {"tenant_id": "tenant-1", "entity": {"id": "lead-1"}}
        state = {"prior": {"output": "ok"}}

        notify = ActionDefinition("notify", "Notification Orchestrator", "send", {"lead_id": "${context.entity.id}"})
        result = engine.execute(notify, context, state)
        self.assertEqual(result["channel"], "notification")
        self.assertEqual(result["input"]["lead_id"], "lead-1")


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


class WorkflowBuilderTests(unittest.TestCase):
    def test_graph_definition_maps_to_dsl_and_executes(self) -> None:
        engine = WorkflowEngine()
        graph = WorkflowBuilderGraph(
            workflow_key="builder_graph_example",
            version="v1",
            metadata={"name": "Builder graph example", "domain": "sales"},
            triggers=TriggerDefinition(mode="any", events=("lead.created.v1",), manual=False),
            conditions=ConditionDefinition(match="all", rules=()),
            nodes=(
                WorkflowGraphNode(
                    id="validate_lead",
                    action_type="call_service",
                    service="Data Quality Service",
                    operation="validate",
                    input={"lead_id": "${context.entity.id}"},
                ),
                WorkflowGraphNode(
                    id="notify_owner",
                    action_type="notify",
                    service="Notification Orchestrator",
                    operation="notify_assigned_owner",
                ),
            ),
            edges=(WorkflowGraphEdge(source="validate_lead", target="notify_owner"),),
            start_node_id="validate_lead",
        )
        definition = engine.create_workflow_from_graph(graph)
        self.assertEqual(definition.workflow_key, "builder_graph_example")
        self.assertEqual(definition.sequencing.steps[0].id, "validate_lead")
        self.assertEqual(definition.sequencing.steps[1].id, "notify_owner")

        event = Event(
            event_name="lead.created.v1",
            event_id="evt-builder-1",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-builder",
            payload={"id": "lead-10"},
        )
        run = engine.start_workflow("builder_graph_example", event=event)
        self.assertEqual(run.status, "completed")
        self.assertEqual(len(run.step_log), 2)

    def test_graph_validation_rejects_unreachable_step(self) -> None:
        engine = WorkflowEngine()
        graph = WorkflowBuilderGraph(
            workflow_key="builder_graph_invalid",
            version="v1",
            metadata={"name": "Builder graph invalid"},
            triggers=TriggerDefinition(mode="any", events=("lead.created.v1",), manual=False),
            conditions=ConditionDefinition(),
            nodes=(
                WorkflowGraphNode("step_a", "call_service", "A", "op_a"),
                WorkflowGraphNode("step_b", "call_service", "B", "op_b"),
            ),
            edges=(),
            start_node_id="step_a",
        )
        with self.assertRaises(WorkflowGraphValidationError):
            engine.create_workflow_from_graph(graph)

    def test_builder_api_create_and_edit_workflow(self) -> None:
        engine = WorkflowEngine()
        api = WorkflowApi(engine)
        create_payload = {
            "workflow_key": "api_builder_workflow",
            "version": "v1",
            "metadata": {"name": "API Builder Workflow"},
            "triggers": {"mode": "any", "events": ["lead.created.v1"], "manual": False},
            "conditions": {"match": "all", "rules": []},
            "nodes": [
                {
                    "id": "first",
                    "action_type": "call_service",
                    "service": "Workflow Automation Service",
                    "operation": "do_first",
                }
            ],
            "edges": [],
            "start_node_id": "first",
        }
        created = api.create_workflow(create_payload, request_id="req-builder-1")
        self.assertIn("data", created)

        edit_payload = {
            **create_payload,
            "nodes": [
                {
                    "id": "first",
                    "action_type": "call_service",
                    "service": "Workflow Automation Service",
                    "operation": "do_first",
                },
                {
                    "id": "second",
                    "action_type": "notify",
                    "service": "Notification Orchestrator",
                    "operation": "send_done",
                },
            ],
            "edges": [{"source": "first", "target": "second"}],
        }
        edited = api.edit_workflow("api_builder_workflow", edit_payload, request_id="req-builder-2")
        self.assertIn("data", edited)
        self.assertEqual(len(edited["data"]["sequencing"]["steps"]), 2)


if __name__ == "__main__":
    unittest.main()
