"""Add SNOOZED/FAILED followup states, closure_reason to leads, FK, idempotency_records table.

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-25

Gap register IDs fixed: D-002, D-010, A-005
  D-002: followup_tasks.state CHECK extended with 'snoozed' and 'failed'
  D-010: leads.closure_reason column; FK followup_tasks → leads
  A-005: idempotency_records table for DB-backed gateway idempotency ledger

Spec:
  domain/followup-enforcement-model.md §2.A  — state machine
  domain/domain-model.md                     — Lead.closure_reason field
  infrastructure/global-idempotency.md §2.1  — idempotency_records schema
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. followup_tasks — drop old state CHECK, add snoozed + failed ──────────
    op.drop_constraint("followup_tasks_state_chk", "followup_tasks", type_="check")
    op.create_check_constraint(
        "followup_tasks_state_chk",
        "followup_tasks",
        "state IN ('pending', 'overdue', 'completed', 'snoozed', 'failed')",
    )

    # ── 2. leads — add closure_reason column ─────────────────────────────────────
    op.add_column(
        "leads",
        sa.Column("closure_reason", sa.Text(), nullable=True),
    )

    # ── 3. followup_tasks — add FK to leads ──────────────────────────────────────
    # Deferrable so existing rows without a matching lead don't break backfill.
    op.create_foreign_key(
        "fk_followup_tasks_lead_id",
        "followup_tasks",
        "leads",
        ["lead_id"],
        ["lead_id"],
        deferrable=True,
        initially="DEFERRED",
    )

    # ── 4. idempotency_records — DB-backed idempotency ledger (gap A-005) ────────
    op.create_table(
        "idempotency_records",
        sa.Column("record_id", sa.String(), primary_key=True),
        # 4-tuple key: tenant_id:METHOD:canonical_route:idempotency_key_header
        sa.Column("idempotency_key", sa.String(512), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("http_method", sa.String(10), nullable=False),
        sa.Column("canonical_route", sa.String(512), nullable=False),
        sa.Column("request_fingerprint", sa.String(64), nullable=False),
        sa.Column("response_status", sa.Integer(), nullable=True),
        sa.Column("response_body", sa.Text(), nullable=True),
        sa.Column("state", sa.String(20), nullable=False, server_default="in_flight"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.CheckConstraint(
            "state IN ('in_flight', 'complete', 'conflict')",
            name="idempotency_records_state_chk",
        ),
    )
    op.create_index("idx_idem_key", "idempotency_records", ["idempotency_key"])
    op.create_index("idx_idem_tenant", "idempotency_records", ["tenant_id"])
    op.create_index("idx_idem_expires", "idempotency_records", ["expires_at"])


def downgrade() -> None:
    op.drop_table("idempotency_records")
    op.drop_constraint("fk_followup_tasks_lead_id", "followup_tasks", type_="foreignkey")
    op.drop_column("leads", "closure_reason")
    op.drop_constraint("followup_tasks_state_chk", "followup_tasks", type_="check")
    op.create_check_constraint(
        "followup_tasks_state_chk",
        "followup_tasks",
        "state IN ('pending', 'overdue', 'completed')",
    )
