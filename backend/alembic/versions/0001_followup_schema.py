"""Create followup_tasks, followup_escalations, leads, activities tables.

Revision ID: 0001
Revises:
Create Date: 2026-05-18

Source specs:
  backend/db/activity_task_db/followup_enforcement_schema.sql
  backend/db/lead_management_db/schema.sql
  backend/db/activity_task_db/schema.sql
  backend/docs/domain-model.md
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "followup_tasks",
        sa.Column("task_id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("lead_id", sa.String(), nullable=False),
        sa.Column("owner_id", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False, server_default="pending"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_activity_id", sa.String(), nullable=True),
        sa.Column("rule_type", sa.String(), nullable=False),
        sa.Column("escalation_level", sa.String(), nullable=False, server_default="none"),
        sa.Column("generated_by", sa.String(), nullable=False, server_default="Scheduler"),
        sa.Column("is_canonical", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("manager_cancel_reason", sa.Text(), nullable=True),
        sa.Column("canceled_by_manager_id", sa.String(), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "state IN ('pending', 'overdue', 'completed')", name="followup_tasks_state_chk"
        ),
        sa.CheckConstraint(
            "rule_type IN ('TimeBased', 'ActivityBased', 'InactivityBased')",
            name="followup_tasks_rule_type_chk",
        ),
        sa.CheckConstraint(
            "escalation_level IN ('none', 'reminder', 'warning', 'escalated', 'reassigned')",
            name="followup_tasks_escalation_chk",
        ),
        sa.CheckConstraint(
            "generated_by IN ('Scheduler', 'EscalationEngine', 'SystemRepair')",
            name="followup_tasks_generated_by_chk",
        ),
    )
    op.create_index("idx_followup_tasks_tenant", "followup_tasks", ["tenant_id"])
    op.create_index(
        "idx_followup_tasks_lead_state_due",
        "followup_tasks",
        ["lead_id", "state", "due_at"],
    )

    op.create_table(
        "followup_escalations",
        sa.Column("escalation_id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("lead_id", sa.String(), nullable=False),
        sa.Column("task_id", sa.String(), nullable=False),
        sa.Column("escalation_level", sa.String(), nullable=False),
        sa.Column("owner_id", sa.String(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "escalation_level IN ('reminder', 'warning', 'escalated', 'reassigned')",
            name="followup_escalations_level_chk",
        ),
    )
    op.create_index(
        "idx_followup_escalations_tenant", "followup_escalations", ["tenant_id"]
    )
    op.create_index(
        "idx_followup_escalations_lead", "followup_escalations", ["lead_id"]
    )

    op.create_table(
        "leads",
        sa.Column("lead_id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("contact_id", sa.String(), nullable=False),
        sa.Column("owner_id", sa.String(), nullable=False),
        sa.Column("stage", sa.String(), nullable=False, server_default="new"),
        sa.Column("status", sa.String(), nullable=False, server_default="open"),
        sa.Column("priority", sa.String(), nullable=False, server_default="warm"),
        sa.Column("source", sa.String(), nullable=False, server_default="manual"),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version_no", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "stage IN ('new','qualifying','nurturing','proposal','negotiation','won','lost','disqualified')",
            name="leads_stage_chk",
        ),
        sa.CheckConstraint(
            "status IN ('open','working','idle','closed')", name="leads_status_chk"
        ),
        sa.CheckConstraint(
            "priority IN ('hot','warm','cold')", name="leads_priority_chk"
        ),
        sa.CheckConstraint(
            "source IN ('whatsapp','web','import','manual','referral','campaign')",
            name="leads_source_chk",
        ),
    )
    op.create_index("idx_leads_tenant", "leads", ["tenant_id"])

    op.create_table(
        "activities",
        sa.Column("activity_id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("actor_user_id", sa.String(), nullable=True),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("source_service", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "entity_type IN ('lead','contact','account','opportunity','case','message_thread')",
            name="activities_entity_type_chk",
        ),
    )
    op.create_index("idx_activities_tenant", "activities", ["tenant_id"])
    op.create_index(
        "idx_activities_entity", "activities", ["tenant_id", "entity_type", "entity_id"]
    )


def downgrade() -> None:
    op.drop_table("activities")
    op.drop_table("leads")
    op.drop_table("followup_escalations")
    op.drop_table("followup_tasks")
