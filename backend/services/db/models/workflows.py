"""SQLAlchemy ORM models for Workflow Execution Engine.

Domain spec: backend/docs/infrastructure/workflow-catalog.md
             backend/docs/domain/workflow-dsl.md (if exists)
Migration:   backend/alembic/versions/0009_workflows_schema.py

Entities:
  WorkflowDefinition — canonical workflow schema (trigger events, DSL steps)
  WorkflowExecution  — a single run of a definition
  WorkflowStep       — per-step execution log within a run (immutable append-only)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from services.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    workflow_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # Human-readable key used across the system (e.g. "lead_followup_enforcement")
    workflow_key: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    # WorkflowStatus: draft | active | paused | archived
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")
    # Trigger events that start this workflow (JSON array of event names)
    trigger_events: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    # DSL steps definition (JSON array of step objects)
    steps_dsl: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    # Retry policy config
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    retry_backoff_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=300)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # system-managed, not editable
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_by: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    execution_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    workflow_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    workflow_key: Mapped[str] = mapped_column(String(128), nullable=False)
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger_event: Mapped[str] = mapped_column(String(128), nullable=False)
    trigger_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    # ExecutionStatus: running | succeeded | failed | retrying | cancelled
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="running")
    step_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_step: Mapped[str | None] = mapped_column(String(128), nullable=True, default=None)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Parent execution if this is a retry
    parent_execution_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    step_record_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    execution_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    workflow_id: Mapped[str] = mapped_column(String, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String(128), nullable=False)
    step_type: Mapped[str] = mapped_column(String(32), nullable=False, default="action")
    # StepStatus: pending | running | succeeded | failed | skipped
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    input_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    output_data: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
