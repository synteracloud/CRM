"""WorkflowService — execution lifecycle, retry logic, DSL step processing.

Domain spec: backend/docs/infrastructure/workflow-catalog.md §12
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from services.workflows.entities import (
    ExecutionStatus,
    RETRYABLE_EXECUTION_STATUSES,
    TERMINAL_EXECUTION_STATUSES,
    WorkflowDomainError,
    validate_steps_dsl,
    validate_workflow_transition,
)


class WorkflowService:
    """Stateless service for Workflow Execution Engine business rules."""

    # ── Definition lifecycle ──────────────────────────────────────────────────

    def validate_definition(self, workflow: dict) -> list[str]:
        """
        Validate a workflow definition before saving/publishing.
        Returns list of error strings (empty = valid).
        """
        errors: list[str] = []
        if not workflow.get("name"):
            errors.append("Workflow name is required.")
        if not workflow.get("trigger_events"):
            errors.append("At least one trigger event is required.")
        step_errors = validate_steps_dsl(workflow.get("steps_dsl") or [])
        errors.extend(step_errors)
        return errors

    def apply_status_transition(self, current: str, target: str) -> dict:
        """Validate and return field updates for a workflow status change."""
        validate_workflow_transition(current, target)
        return {"status": target, "updated_at": datetime.now(timezone.utc)}

    # ── Execution lifecycle ───────────────────────────────────────────────────

    def can_retry(self, execution: dict, max_retries: int = 3) -> bool:
        """Return True if the execution can be retried."""
        if execution.get("status") not in (e.value for e in RETRYABLE_EXECUTION_STATUSES):
            return False
        return execution.get("retry_count", 0) < max_retries

    def build_retry_execution(
        self,
        original: dict,
        tenant_id: str,
    ) -> dict:
        """
        Build a new execution record as a retry of `original`.
        Raises WorkflowDomainError if the execution is not retryable.
        """
        if not self.can_retry(original, original.get("max_retries", 3)):
            raise WorkflowDomainError(
                f"Execution {original.get('execution_id')!r} cannot be retried: "
                f"status={original.get('status')!r}, "
                f"retry_count={original.get('retry_count', 0)}/{original.get('max_retries', 3)}."
            )
        now = datetime.now(timezone.utc)
        return {
            "execution_id":        None,  # assigned at persist time
            "workflow_id":         original["workflow_id"],
            "tenant_id":           tenant_id,
            "workflow_key":        original["workflow_key"],
            "workflow_name":       original["workflow_name"],
            "trigger_event":       original["trigger_event"],
            "trigger_payload":     original.get("trigger_payload", {}),
            "status":              ExecutionStatus.RUNNING,
            "step_count":          original.get("step_count", 0),
            "current_step":        0,
            "failed_step":         None,
            "error_message":       None,
            "retry_count":         (original.get("retry_count") or 0) + 1,
            "parent_execution_id": original["execution_id"],
            "started_at":          now.isoformat(),
            "ended_at":            None,
            "duration_ms":         None,
            "created_at":          now.isoformat(),
        }

    def finalize_execution(
        self,
        execution: dict,
        success: bool,
        failed_step: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> dict:
        """Return field updates to finalize an execution run."""
        now = datetime.now(timezone.utc)
        started = execution.get("started_at")
        duration_ms: Optional[int] = None
        if started:
            try:
                start_dt = datetime.fromisoformat(str(started).replace("Z", "+00:00"))
                duration_ms = int((now - start_dt).total_seconds() * 1000)
            except (ValueError, TypeError):
                pass

        return {
            "status":       ExecutionStatus.SUCCEEDED if success else ExecutionStatus.FAILED,
            "ended_at":     now,
            "duration_ms":  duration_ms,
            "failed_step":  failed_step,
            "error_message":error_message,
        }

    # ── DSL step simulation ───────────────────────────────────────────────────

    def simulate_execution(
        self,
        workflow: dict,
        trigger_payload: dict,
    ) -> list[dict]:
        """
        Simulate step-by-step execution of a workflow DSL against a trigger payload.
        Returns a list of step execution records (all marked succeeded in simulation).
        This is used for the workflow builder's validate/simulate feature.
        """
        steps_dsl = workflow.get("steps_dsl") or []
        results: list[dict] = []
        now = datetime.now(timezone.utc)

        for i, step in enumerate(steps_dsl):
            step_name = step.get("name", f"Step {i+1}")
            step_type = step.get("type", "action")
            # Simulation: all steps succeed except conditions that evaluate False
            sim_output: dict = {}
            if step_type == "condition":
                sim_output = {"result": True, "branch": "true"}
            elif step_type == "action":
                sim_output = {"result": "ok", "action": step.get("action")}
            elif step_type == "notification":
                sim_output = {"sent": True, "channel": "whatsapp"}

            results.append({
                "step_index":   i,
                "step_name":    step_name,
                "step_type":    step_type,
                "status":       "succeeded",
                "input_data":   trigger_payload if i == 0 else {},
                "output_data":  sim_output,
                "duration_ms":  100 + i * 50,
                "simulated":    True,
            })

        return results

    # ── Stats ─────────────────────────────────────────────────────────────────

    def compute_execution_stats(self, executions: list[dict]) -> dict:
        """Compute aggregate KPI stats over a list of execution records."""
        total     = len(executions)
        succeeded = sum(1 for e in executions if e.get("status") == "succeeded")
        failed    = sum(1 for e in executions if e.get("status") == "failed")
        retrying  = sum(1 for e in executions if e.get("status") == "retrying")
        running   = sum(1 for e in executions if e.get("status") == "running")

        durations = [e["duration_ms"] for e in executions if e.get("duration_ms")]
        avg_ms    = round(sum(durations) / len(durations)) if durations else 0

        return {
            "total":          total,
            "succeeded":      succeeded,
            "failed":         failed,
            "retrying":       retrying,
            "running":        running,
            "success_rate":   round(succeeded / total * 100, 1) if total else 0,
            "avg_duration_ms":avg_ms,
        }
