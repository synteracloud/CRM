"""Unit tests for WorkflowService: definition validation, execution lifecycle, retry logic.

Spec: backend/docs/infrastructure/workflow-catalog.md §12
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from services.workflows.entities import (
    CATALOG_WORKFLOWS,
    WorkflowDomainError,
    validate_steps_dsl,
    validate_workflow_transition,
)
from services.workflows.service import WorkflowService


def _utc(*args) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)


def _execution(status="failed", retry_count=0, max_retries=3) -> dict:
    return {
        "execution_id":  "exec-001",
        "workflow_id":   "wf-001",
        "workflow_key":  "lead_followup_enforcement",
        "workflow_name": "Lead Follow-up Enforcement",
        "trigger_event": "lead.idle.v1",
        "trigger_payload": {},
        "status":        status,
        "step_count":    3,
        "retry_count":   retry_count,
        "max_retries":   max_retries,
        "started_at":    datetime.now(timezone.utc).isoformat(),
    }


def _workflow(steps=None, trigger_events=None) -> dict:
    return {
        "workflow_id":   "wf-001",
        "name":          "Test Workflow",
        "trigger_events": trigger_events or ["lead.idle.v1"],
        "steps_dsl":     steps or [
            {"id": "s1", "type": "condition", "name": "Check", "condition": "x > 0"},
            {"id": "s2", "type": "action",    "name": "Do it", "action": "some_action"},
        ],
    }


# ── validate_workflow_transition ──────────────────────────────────────────────

class TestWorkflowTransition:
    def test_draft_to_active(self):
        validate_workflow_transition("draft", "active")

    def test_active_to_paused(self):
        validate_workflow_transition("active", "paused")

    def test_paused_to_active(self):
        validate_workflow_transition("paused", "active")

    def test_archived_is_terminal(self):
        with pytest.raises(WorkflowDomainError):
            validate_workflow_transition("archived", "active")

    def test_draft_to_paused_blocked(self):
        with pytest.raises(WorkflowDomainError):
            validate_workflow_transition("draft", "paused")


# ── validate_steps_dsl ────────────────────────────────────────────────────────

class TestValidateStepsDsl:
    def test_empty_steps_error(self):
        errors = validate_steps_dsl([])
        assert any("at least one step" in e for e in errors)

    def test_valid_steps_no_errors(self):
        steps = [
            {"id": "s1", "type": "condition", "name": "Check", "condition": "x > 0"},
            {"id": "s2", "type": "action",    "name": "Do",    "action": "do_something"},
        ]
        errors = validate_steps_dsl(steps)
        assert errors == []

    def test_duplicate_step_id_error(self):
        steps = [
            {"id": "s1", "type": "action", "name": "Step 1", "action": "a"},
            {"id": "s1", "type": "action", "name": "Step 2", "action": "b"},
        ]
        errors = validate_steps_dsl(steps)
        assert any("Duplicate" in e for e in errors)

    def test_invalid_step_type_error(self):
        steps = [{"id": "s1", "type": "invalid_type", "name": "Bad"}]
        errors = validate_steps_dsl(steps)
        assert any("invalid type" in e for e in errors)

    def test_action_without_action_key_error(self):
        steps = [{"id": "s1", "type": "action", "name": "No action key"}]
        errors = validate_steps_dsl(steps)
        assert any("action" in e.lower() for e in errors)

    def test_condition_without_condition_key_error(self):
        steps = [{"id": "s1", "type": "condition", "name": "No condition key"}]
        errors = validate_steps_dsl(steps)
        assert any("condition" in e.lower() for e in errors)


# ── WorkflowService.validate_definition ──────────────────────────────────────

class TestValidateDefinition:
    svc = WorkflowService()

    def test_valid_workflow_no_errors(self):
        errors = self.svc.validate_definition(_workflow())
        assert errors == []

    def test_missing_name_error(self):
        wf = {**_workflow(), "name": ""}
        errors = self.svc.validate_definition(wf)
        assert any("name" in e.lower() for e in errors)

    def test_missing_trigger_events_error(self):
        wf = {**_workflow(), "trigger_events": []}
        errors = self.svc.validate_definition(wf)
        assert any("trigger" in e.lower() for e in errors)


# ── WorkflowService.can_retry ─────────────────────────────────────────────────

class TestCanRetry:
    svc = WorkflowService()

    def test_failed_under_limit_can_retry(self):
        assert self.svc.can_retry(_execution("failed", 0, 3)) is True

    def test_retrying_under_limit_can_retry(self):
        assert self.svc.can_retry(_execution("retrying", 1, 3)) is True

    def test_at_max_retries_cannot_retry(self):
        assert self.svc.can_retry(_execution("failed", 3, 3)) is False

    def test_succeeded_cannot_retry(self):
        assert self.svc.can_retry(_execution("succeeded")) is False

    def test_cancelled_cannot_retry(self):
        assert self.svc.can_retry(_execution("cancelled")) is False


# ── WorkflowService.build_retry_execution ─────────────────────────────────────

class TestBuildRetryExecution:
    svc = WorkflowService()

    def test_retry_increments_count(self):
        orig = _execution("failed", 0)
        retry = self.svc.build_retry_execution(orig, "t-001")
        assert retry["retry_count"] == 1
        assert retry["parent_execution_id"] == "exec-001"
        assert retry["status"] == "running"
        assert retry["failed_step"] is None

    def test_retry_at_max_raises(self):
        orig = _execution("failed", 3, 3)
        with pytest.raises(WorkflowDomainError, match="cannot be retried"):
            self.svc.build_retry_execution(orig, "t-001")

    def test_retry_preserves_workflow_metadata(self):
        orig = _execution("failed", 0)
        retry = self.svc.build_retry_execution(orig, "t-001")
        assert retry["workflow_key"]  == orig["workflow_key"]
        assert retry["trigger_event"] == orig["trigger_event"]


# ── WorkflowService.finalize_execution ───────────────────────────────────────

class TestFinalizeExecution:
    svc = WorkflowService()

    def test_success_sets_succeeded(self):
        exec_ = _execution("running")
        result = self.svc.finalize_execution(exec_, success=True)
        assert result["status"] == "succeeded"
        assert result["ended_at"] is not None

    def test_failure_sets_failed_with_step_and_message(self):
        exec_ = _execution("running")
        result = self.svc.finalize_execution(exec_, success=False, failed_step="send_whatsapp", error_message="timeout")
        assert result["status"]        == "failed"
        assert result["failed_step"]   == "send_whatsapp"
        assert result["error_message"] == "timeout"

    def test_duration_computed(self):
        now = datetime.now(timezone.utc)
        exec_ = {**_execution("running"), "started_at": (now - timedelta(seconds=5)).isoformat()}
        result = self.svc.finalize_execution(exec_, success=True)
        assert result["duration_ms"] is not None
        assert result["duration_ms"] >= 4000


# ── WorkflowService.simulate_execution ───────────────────────────────────────

class TestSimulateExecution:
    svc = WorkflowService()

    def test_returns_step_for_each_dsl_entry(self):
        wf = _workflow()
        results = self.svc.simulate_execution(wf, {})
        assert len(results) == len(wf["steps_dsl"])

    def test_all_steps_succeed_in_simulation(self):
        wf = _workflow()
        results = self.svc.simulate_execution(wf, {})
        assert all(r["status"] == "succeeded" for r in results)

    def test_condition_step_outputs_branch(self):
        wf = _workflow()
        results = self.svc.simulate_execution(wf, {})
        cond_steps = [r for r in results if r["step_type"] == "condition"]
        for s in cond_steps:
            assert "result" in s["output_data"]


# ── WorkflowService.compute_execution_stats ──────────────────────────────────

class TestComputeStats:
    svc = WorkflowService()

    def test_success_rate_computed(self):
        executions = [
            {"status": "succeeded", "duration_ms": 1000},
            {"status": "succeeded", "duration_ms": 2000},
            {"status": "failed",    "duration_ms": 500},
            {"status": "failed",    "duration_ms": 400},
        ]
        stats = self.svc.compute_execution_stats(executions)
        assert stats["total"]        == 4
        assert stats["succeeded"]    == 2
        assert stats["failed"]       == 2
        assert stats["success_rate"] == 50.0
        assert stats["avg_duration_ms"] == 975

    def test_empty_executions(self):
        stats = self.svc.compute_execution_stats([])
        assert stats["total"]        == 0
        assert stats["success_rate"] == 0


# ── CATALOG_WORKFLOWS ─────────────────────────────────────────────────────────

class TestCatalogWorkflows:
    def test_catalog_has_five_entries(self):
        assert len(CATALOG_WORKFLOWS) == 5

    def test_all_have_workflow_key(self):
        for wf in CATALOG_WORKFLOWS:
            assert wf.get("workflow_key")

    def test_all_have_trigger_events(self):
        for wf in CATALOG_WORKFLOWS:
            assert wf.get("trigger_events")

    def test_all_have_steps(self):
        for wf in CATALOG_WORKFLOWS:
            assert len(wf.get("steps_dsl", [])) > 0
