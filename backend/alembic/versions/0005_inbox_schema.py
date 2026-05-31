"""Add shared inbox schema and extend conversations table.

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-29

Sprint: 5B-2 — Shared Inbox / Routing
Spec:   backend/docs/domain/shared-inbox.md

Changes:
  conversations  — ADD COLUMNS: assigned_agent_id, queue_id, assignment_reason,
                                handoff_count, last_handoff_at, assigned_at
  inbox_queues   — CREATE: queue config per tenant
  agent_presence — CREATE: per-agent availability status
  conversation_handoffs — CREATE: immutable handoff audit records
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

VALID_PRESENCE_STATUS   = "('online','away','busy','offline')"
VALID_ASSIGNMENT_REASON = "('auto_routed','claimed','supervisor_assigned','handoff')"
VALID_HANDOFF_REASON    = "('agent_unavailable','capacity_exceeded','skill_match','manual','escalation')"
VALID_ROUTING_STRATEGY  = "('round_robin','least_loaded','claim_first','skill_based')"


def upgrade() -> None:
    # ── 1. Extend conversations ───────────────────────────────────────────────
    op.add_column("conversations", sa.Column("assigned_agent_id", sa.String(),              nullable=True))
    op.add_column("conversations", sa.Column("assigned_at",       sa.DateTime(timezone=True), nullable=True))
    op.add_column("conversations", sa.Column("queue_id",          sa.String(),              nullable=True))
    op.add_column("conversations", sa.Column("assignment_reason", sa.String(32),            nullable=True))
    op.add_column("conversations", sa.Column("last_handoff_at",   sa.DateTime(timezone=True), nullable=True))
    op.add_column("conversations", sa.Column("handoff_count",     sa.Integer(),             nullable=False, server_default="0"))

    op.create_index("idx_conv_assigned_agent", "conversations", ["tenant_id", "assigned_agent_id"])
    op.create_index("idx_conv_queue",          "conversations", ["tenant_id", "queue_id"])

    # ── 2. inbox_queues ───────────────────────────────────────────────────────
    op.create_table(
        "inbox_queues",
        sa.Column("queue_id",          sa.String(),    primary_key=True),
        sa.Column("tenant_id",         sa.String(),    nullable=False),
        sa.Column("name",              sa.String(128), nullable=False),
        sa.Column("routing_strategy",  sa.String(32),  nullable=False, server_default="round_robin"),
        sa.Column("skill_tags",        sa.String(),    nullable=True),
        sa.Column("team_id",           sa.String(),    nullable=True),
        sa.Column("auto_assign",       sa.Boolean(),   nullable=False, server_default="true"),
        sa.Column("is_active",         sa.Boolean(),   nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"routing_strategy IN {VALID_ROUTING_STRATEGY}", name="inbox_queues_strategy_chk"),
    )
    op.create_index("idx_inbox_queues_tenant", "inbox_queues", ["tenant_id"])

    # ── 3. agent_presence ─────────────────────────────────────────────────────
    op.create_table(
        "agent_presence",
        sa.Column("agent_id",                 sa.String(),   primary_key=True),
        sa.Column("tenant_id",                sa.String(),   nullable=False),
        sa.Column("status",                   sa.String(16), nullable=False, server_default="offline"),
        sa.Column("open_conversation_count",  sa.Integer(),  nullable=False, server_default="0"),
        sa.Column("max_concurrent",           sa.Integer(),  nullable=False, server_default="10"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at",   sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"status IN {VALID_PRESENCE_STATUS}", name="agent_presence_status_chk"),
    )
    op.create_index("idx_agent_presence_tenant", "agent_presence", ["tenant_id"])

    # ── 4. conversation_handoffs ──────────────────────────────────────────────
    op.create_table(
        "conversation_handoffs",
        sa.Column("handoff_id",       sa.String(),  primary_key=True),
        sa.Column("conversation_id",  sa.String(),  nullable=False),
        sa.Column("tenant_id",        sa.String(),  nullable=False),
        sa.Column("from_agent_id",    sa.String(),  nullable=True),
        sa.Column("to_agent_id",      sa.String(),  nullable=True),
        sa.Column("handoff_reason",   sa.String(32), nullable=False, server_default="manual"),
        sa.Column("note",             sa.Text(),    nullable=True),
        sa.Column("initiated_by",     sa.String(),  nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"handoff_reason IN {VALID_HANDOFF_REASON}", name="conv_handoffs_reason_chk"),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["conversations.conversation_id"],
            name="fk_handoffs_conversation",
        ),
    )
    op.create_index("idx_handoffs_conv",   "conversation_handoffs", ["conversation_id"])
    op.create_index("idx_handoffs_tenant", "conversation_handoffs", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("conversation_handoffs")
    op.drop_table("agent_presence")
    op.drop_table("inbox_queues")
    op.drop_index("idx_conv_queue",          table_name="conversations")
    op.drop_index("idx_conv_assigned_agent", table_name="conversations")
    op.drop_column("conversations", "handoff_count")
    op.drop_column("conversations", "last_handoff_at")
    op.drop_column("conversations", "assignment_reason")
    op.drop_column("conversations", "queue_id")
    op.drop_column("conversations", "assigned_at")
    op.drop_column("conversations", "assigned_agent_id")
