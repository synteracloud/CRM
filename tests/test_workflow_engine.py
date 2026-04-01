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
    RetryPolicy,
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
        self.assertEqual(report["score"], 13)
        self.assertEqual(report["issues"], [])
        self.assertTrue(report["checks"]["all_triggers_map_to_event_catalog"])
        self.assertTrue(report["checks"]["no_undefined_actions"])

    def test_retry_engine_retries_then_fails_without_infinite_loop(self) -> None:
        engine = WorkflowEngine()
        workflow = WorkflowDefinition(
            workflow_key="retry_engine_test",
            version="v1",
            metadata={"name": "Retry test"},
            triggers=TriggerDefinition(mode="any", events=("lead.created.v1",)),
            conditions=ConditionDefinition(),
            sequencing=SequencingDefinition(
                strategy="linear",
                on_error="fail_fast",
                steps=(WorkflowStep("step_1", "always_fails", retries=2),),
            ),
            actions={"always_fails": ActionDefinition("call_service", "Service", "fail:timeout")},
            retry_policy=RetryPolicy(max_attempts=3, backoff_seconds=1, max_backoff_seconds=8),
        )
        engine.register_workflow(workflow)
        event = Event(
            event_name="lead.created.v1",
            event_id="evt-retry-1",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-retry",
            payload={},
        )
        execution = engine.start_workflow("retry_engine_test", event=event)
        self.assertEqual(execution.status, "failed_retryable")
        attempts = [log for log in execution.step_log if log.get("step_id") == "step_1" and log.get("action") == "always_fails"]
        self.assertEqual(len(attempts), 3)
        self.assertTrue(any(log.get("action") == "retry.scheduled" for log in execution.step_log))
        self.assertEqual(execution.status, "failed_retryable")

    def test_retry_schedule_is_deterministic_for_same_execution_and_attempt(self) -> None:
        engine = WorkflowEngine()
        workflow = WorkflowDefinition(
            workflow_key="retry_deterministic_test",
            version="v1",
            metadata={"name": "Retry deterministic test"},
            triggers=TriggerDefinition(mode="any", events=("lead.created.v1",)),
            conditions=ConditionDefinition(),
            sequencing=SequencingDefinition(
                strategy="linear",
                on_error="fail_fast",
                steps=(WorkflowStep("step_1", "always_fails", retries=1),),
            ),
            actions={"always_fails": ActionDefinition("call_service", "Service", "fail:timeout")},
            retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=2, max_backoff_seconds=8),
        )
        engine.register_workflow(workflow)
        event = Event(
            event_name="lead.created.v1",
            event_id="evt-retry-deterministic",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-retry",
            payload={},
        )
        execution = engine.start_workflow("retry_deterministic_test", event=event)
        scheduled = [log for log in execution.step_log if log.get("action") == "retry.scheduled"]
        self.assertEqual(len(scheduled), 1)
        expected_retry_after = scheduled[0]["backoff_seconds"] + scheduled[0]["jitter_seconds"]
        self.assertEqual(scheduled[0]["retry_after_seconds"], expected_retry_after)

    def test_retryable_failure_dead_letters_at_policy_threshold(self) -> None:
        engine = WorkflowEngine()
        workflow = WorkflowDefinition(
            workflow_key="retry_dead_letter_test",
            version="v1",
            metadata={"name": "Retry dead letter test"},
            triggers=TriggerDefinition(mode="any", events=("lead.created.v1",)),
            conditions=ConditionDefinition(),
            sequencing=SequencingDefinition(
                strategy="linear",
                on_error="fail_fast",
                steps=(WorkflowStep("step_1", "always_fails", retries=2),),
            ),
            actions={"always_fails": ActionDefinition("call_service", "Service", "fail:timeout")},
            retry_policy=RetryPolicy(max_attempts=3, backoff_seconds=1, max_backoff_seconds=8, dead_letter_after_attempts=3),
        )
        engine.register_workflow(workflow)
        event = Event(
            event_name="lead.created.v1",
            event_id="evt-retry-dead-letter",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-retry",
            payload={},
        )
        execution = engine.start_workflow("retry_dead_letter_test", event=event)
        self.assertEqual(execution.status, "dead_lettered")
        self.assertTrue(any(log.get("action") == "step.failed" and log.get("disposition") == "retryable" for log in execution.step_log))

    def test_compensation_runs_in_reverse_for_multi_step_flow(self) -> None:
        engine = WorkflowEngine()
        workflow = WorkflowDefinition(
            workflow_key="compensation_test",
            version="v1",
            metadata={"name": "Compensation test"},
            triggers=TriggerDefinition(mode="any", events=("lead.created.v1",)),
            conditions=ConditionDefinition(),
            sequencing=SequencingDefinition(
                strategy="linear",
                on_error="compensate",
                steps=(
                    WorkflowStep("reserve_inventory", "reserve"),
                    WorkflowStep("create_order", "create"),
                    WorkflowStep("collect_payment", "payment"),
                ),
            ),
            actions={
                "reserve": ActionDefinition("call_service", "Inventory", "reserve"),
                "create": ActionDefinition("call_service", "Orders", "create"),
                "payment": ActionDefinition("call_service", "Payments", "fail:validation_error"),
            },
            compensations={
                "reserve": ActionDefinition("call_service", "Inventory", "release"),
                "create": ActionDefinition("call_service", "Orders", "cancel"),
            },
        )
        engine.register_workflow(workflow)
        event = Event(
            event_name="lead.created.v1",
            event_id="evt-comp-1",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-comp",
            payload={},
        )
        execution = engine.start_workflow("compensation_test", event=event)
        self.assertEqual(execution.status, "failed")
        compensations = [log for log in execution.step_log if log.get("action") == "compensation.executed"]
        self.assertEqual(len(compensations), 2)
        self.assertEqual(compensations[0]["for_action"], "create")
        self.assertEqual(compensations[1]["for_action"], "reserve")

    def test_recover_stuck_workflow_recovers_failed_retryable(self) -> None:
        engine = WorkflowEngine()
        workflow = WorkflowDefinition(
            workflow_key="recover_stuck_retryable_test",
            version="v1",
            metadata={"name": "Recover stuck workflow"},
            triggers=TriggerDefinition(mode="any", events=("lead.created.v1",), manual=True),
            conditions=ConditionDefinition(),
            sequencing=SequencingDefinition(
                strategy="linear",
                on_error="fail_fast",
                steps=(WorkflowStep("step_1", "always_fails", retries=1),),
            ),
            actions={"always_fails": ActionDefinition("call_service", "Service", "fail:timeout")},
            retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=1, max_backoff_seconds=8, dead_letter_after_attempts=10),
        )
        engine.register_workflow(workflow)
        execution = engine.start_workflow("recover_stuck_retryable_test", context={"tenant_id": "tenant-1"})
        self.assertEqual(execution.status, "failed_retryable")
        execution.updated_at = "2026-03-01T00:00:00Z"
        recovered = engine.recover_stuck_workflows("2026-03-15T00:00:00Z")
        self.assertEqual(len(recovered), 1)


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
