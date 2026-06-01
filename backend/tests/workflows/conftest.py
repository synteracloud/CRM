"""Seed fixtures for workflow API tests."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tests.workflows._shared_db import shared_engine as _test_engine, SharedSession as TestSessionLocal

TEST_TENANT = "tenant-test-001"


@pytest.fixture(autouse=True)
def seed_workflows():
    """Create schema and seed workflow test data."""
    from services.db.base import Base
    from services.db.models.workflows import WorkflowDefinition, WorkflowExecution, WorkflowStep

    Base.metadata.create_all(bind=_test_engine)

    now = datetime.now(timezone.utc)
    db = TestSessionLocal()
    try:
        wf1 = WorkflowDefinition(
            workflow_id="wf-001",
            tenant_id=TEST_TENANT,
            workflow_key="lead_followup_enforcement",
            name="Lead Follow-up Enforcement",
            description="Enforces follow-up tasks for idle leads",
            status="active",
            trigger_events=["lead.idle.v1"],
            steps_dsl=[
                {"id": "s1", "type": "condition",    "name": "Check idle threshold", "condition": "lead.idle_days > threshold"},
                {"id": "s2", "type": "action",       "name": "Create follow-up task", "action": "create_followup_task"},
                {"id": "s3", "type": "notification", "name": "Notify owner",          "action": "send_whatsapp_alert"},
            ],
            max_retries=3,
            is_system=True,
            version=1,
            created_by="system",
            created_at=now,
            updated_at=now,
        )
        wf2 = WorkflowDefinition(
            workflow_id="wf-002",
            tenant_id=TEST_TENANT,
            workflow_key="collections_reminder",
            name="Collections Auto-Reminder",
            description="Sends reminders for overdue invoices",
            status="draft",
            trigger_events=["invoice.overdue.v1"],
            steps_dsl=[
                {"id": "s1", "type": "action", "name": "Load invoice", "action": "load_invoice"},
                {"id": "s2", "type": "notification", "name": "Send WhatsApp", "action": "send_whatsapp"},
            ],
            max_retries=3,
            is_system=False,
            version=1,
            created_by="system",
            created_at=now,
            updated_at=now,
        )
        db.merge(wf1)
        db.merge(wf2)

        executions = [
            WorkflowExecution(
                execution_id="exec-001",
                workflow_id="wf-001",
                tenant_id=TEST_TENANT,
                workflow_key="lead_followup_enforcement",
                workflow_name="Lead Follow-up Enforcement",
                trigger_event="lead.idle.v1",
                trigger_payload={"lead_id": "l-001"},
                status="succeeded",
                step_count=3,
                current_step=3,
                retry_count=0,
                started_at=now,
                ended_at=now,
                created_at=now,
            ),
            WorkflowExecution(
                execution_id="exec-002",
                workflow_id="wf-001",
                tenant_id=TEST_TENANT,
                workflow_key="lead_followup_enforcement",
                workflow_name="Lead Follow-up Enforcement",
                trigger_event="lead.idle.v1",
                trigger_payload={"lead_id": "l-002"},
                status="failed",
                step_count=3,
                current_step=1,
                failed_step="s2",
                error_message="Timeout",
                retry_count=0,
                started_at=now,
                ended_at=now,
                created_at=now,
            ),
            WorkflowExecution(
                execution_id="exec-003",
                workflow_id="wf-001",
                tenant_id=TEST_TENANT,
                workflow_key="lead_followup_enforcement",
                workflow_name="Lead Follow-up Enforcement",
                trigger_event="lead.idle.v1",
                trigger_payload={"lead_id": "l-003"},
                status="running",
                step_count=3,
                current_step=1,
                retry_count=0,
                started_at=now,
                created_at=now,
            ),
            WorkflowExecution(
                execution_id="exec-007",
                workflow_id="wf-001",
                tenant_id=TEST_TENANT,
                workflow_key="lead_followup_enforcement",
                workflow_name="Lead Follow-up Enforcement",
                trigger_event="lead.idle.v1",
                trigger_payload={"lead_id": "l-007"},
                status="succeeded",
                step_count=3,
                current_step=3,
                retry_count=0,
                started_at=now,
                ended_at=now,
                created_at=now,
            ),
            WorkflowExecution(
                execution_id="exec-008",
                workflow_id="wf-001",
                tenant_id=TEST_TENANT,
                workflow_key="lead_followup_enforcement",
                workflow_name="Lead Follow-up Enforcement",
                trigger_event="lead.idle.v1",
                trigger_payload={"lead_id": "l-008"},
                status="running",
                step_count=3,
                current_step=1,
                retry_count=0,
                started_at=now,
                created_at=now,
            ),
        ]
        for e in executions:
            db.merge(e)

        # Steps for exec-007 (3 steps)
        for i in range(3):
            s = WorkflowStep(
                step_record_id=f"step-007-{i}",
                execution_id="exec-007",
                workflow_id="wf-001",
                tenant_id=TEST_TENANT,
                step_index=i,
                step_name=f"Step {i+1}",
                step_type="action",
                status="succeeded",
                input_data={},
                output_data={"result": "ok"},
                duration_ms=100,
                created_at=now,
            )
            db.merge(s)

        db.commit()
    finally:
        db.close()
