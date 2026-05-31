"""Add workflow execution engine schema.

Revision ID: 0009
Revises: 0008
Create Date: 2026-05-29

Sprint: 5B-6 — Workflow Execution Engine
Spec:   backend/docs/infrastructure/workflow-catalog.md

Tables created:
  workflow_definitions — Canonical workflow schemas (DSL + trigger events)
  workflow_executions  — Execution run records (one per trigger)
  workflow_steps       — Per-step execution logs (immutable, append-only)

System workflows from workflow-catalog.md are seeded via application bootstrap,
not via migration (tenant-scoped records).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None

VALID_WF_STATUS   = "('draft','active','paused','archived')"
VALID_EXEC_STATUS = "('running','succeeded','failed','retrying','cancelled')"
VALID_STEP_STATUS = "('pending','running','succeeded','failed','skipped')"
VALID_STEP_TYPE   = "('condition','action','notification','delay','fork','join')"


def upgrade() -> None:
    # ── 1. workflow_definitions ────────────────────────────────────────────────
    op.create_table(
        "workflow_definitions",
        sa.Column("workflow_id",            sa.String(),    primary_key=True),
        sa.Column("tenant_id",              sa.String(),    nullable=False),
        sa.Column("workflow_key",           sa.String(128), nullable=False),
        sa.Column("name",                   sa.String(255), nullable=False),
        sa.Column("description",            sa.Text(),      nullable=True),
        sa.Column("status",                 sa.String(16),  nullable=False, server_default="draft"),
        sa.Column("trigger_events",         sa.JSON(),      nullable=False, server_default="[]"),
        sa.Column("steps_dsl",              sa.JSON(),      nullable=False, server_default="[]"),
        sa.Column("max_retries",            sa.Integer(),   nullable=False, server_default="3"),
        sa.Column("retry_backoff_seconds",  sa.Integer(),   nullable=False, server_default="60"),
        sa.Column("timeout_seconds",        sa.Integer(),   nullable=False, server_default="300"),
        sa.Column("is_system",              sa.Boolean(),   nullable=False, server_default="false"),
        sa.Column("version",                sa.Integer(),   nullable=False, server_default="1"),
        sa.Column("created_by",             sa.String(),    nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"status IN {VALID_WF_STATUS}", name="workflow_def_status_chk"),
        sa.UniqueConstraint("tenant_id", "workflow_key", name="uq_workflow_def_key"),
    )
    op.create_index("idx_workflow_def_tenant",  "workflow_definitions", ["tenant_id"])
    op.create_index("idx_workflow_def_status",  "workflow_definitions", ["tenant_id", "status"])
    op.create_index("idx_workflow_def_key",     "workflow_definitions", ["tenant_id", "workflow_key"])

    # ── 2. workflow_executions ────────────────────────────────────────────────
    op.create_table(
        "workflow_executions",
        sa.Column("execution_id",        sa.String(),    primary_key=True),
        sa.Column("workflow_id",         sa.String(),    nullable=False),
        sa.Column("tenant_id",           sa.String(),    nullable=False),
        sa.Column("workflow_key",        sa.String(128), nullable=False),
        sa.Column("workflow_name",       sa.String(255), nullable=False),
        sa.Column("trigger_event",       sa.String(128), nullable=False),
        sa.Column("trigger_payload",     sa.JSON(),      nullable=False, server_default="{}"),
        sa.Column("status",              sa.String(16),  nullable=False, server_default="running"),
        sa.Column("step_count",          sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("current_step",        sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("failed_step",         sa.String(128), nullable=True),
        sa.Column("error_message",       sa.Text(),      nullable=True),
        sa.Column("retry_count",         sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("parent_execution_id", sa.String(),    nullable=True),
        sa.Column("started_at",  sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("ended_at",    sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(),               nullable=True),
        sa.Column("created_at",  sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"status IN {VALID_EXEC_STATUS}", name="workflow_exec_status_chk"),
        sa.ForeignKeyConstraint(
            ["workflow_id"], ["workflow_definitions.workflow_id"],
            name="fk_workflow_exec_def",
        ),
    )
    op.create_index("idx_workflow_exec_tenant",  "workflow_executions", ["tenant_id"])
    op.create_index("idx_workflow_exec_workflow", "workflow_executions", ["workflow_id"])
    op.create_index("idx_workflow_exec_status",  "workflow_executions", ["tenant_id", "status"])
    op.create_index("idx_workflow_exec_trigger", "workflow_executions", ["tenant_id", "trigger_event"])

    # ── 3. workflow_steps ──────────────────────────────────────────────────────
    op.create_table(
        "workflow_steps",
        sa.Column("step_record_id", sa.String(),    primary_key=True),
        sa.Column("execution_id",   sa.String(),    nullable=False),
        sa.Column("workflow_id",    sa.String(),    nullable=False),
        sa.Column("tenant_id",      sa.String(),    nullable=False),
        sa.Column("step_index",     sa.Integer(),   nullable=False),
        sa.Column("step_name",      sa.String(128), nullable=False),
        sa.Column("step_type",      sa.String(32),  nullable=False, server_default="action"),
        sa.Column("status",         sa.String(16),  nullable=False, server_default="pending"),
        sa.Column("input_data",     sa.JSON(),      nullable=False, server_default="{}"),
        sa.Column("output_data",    sa.JSON(),      nullable=True),
        sa.Column("error_message",  sa.Text(),      nullable=True),
        sa.Column("duration_ms",    sa.Integer(),   nullable=True),
        sa.Column("started_at",  sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at",    sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at",  sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"status    IN {VALID_STEP_STATUS}", name="workflow_step_status_chk"),
        sa.CheckConstraint(f"step_type IN {VALID_STEP_TYPE}",   name="workflow_step_type_chk"),
        sa.ForeignKeyConstraint(
            ["execution_id"], ["workflow_executions.execution_id"],
            name="fk_workflow_steps_exec",
        ),
    )
    op.create_index("idx_workflow_steps_exec",   "workflow_steps", ["execution_id"])
    op.create_index("idx_workflow_steps_tenant", "workflow_steps", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("workflow_steps")
    op.drop_table("workflow_executions")
    op.drop_table("workflow_definitions")
