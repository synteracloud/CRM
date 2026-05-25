"""Add collections (invoices, payments, reconciliation_cases) and conversations tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-25

Gap register IDs fixed: A-003, A-004
  A-003: invoices, payments, reconciliation_cases tables for CollectionsService
  A-004: conversations, conversation_messages tables for ConversationalCRMService

Spec:
  domain/collections-engine-model.md §2      — Invoice, Payment, ReconciliationCase schemas
  adapters/whatsapp-execution-model.md §5    — Conversation entity
  domain/activity-control-model.md §1.2      — ConversationActivityEvent feed
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. invoices ───────────────────────────────────────────────────────────────
    op.create_table(
        "invoices",
        sa.Column("invoice_id", sa.String(), primary_key=True),
        sa.Column("invoice_number", sa.String(64), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("issue_date", sa.String(10), nullable=False),   # ISO date string
        sa.Column("due_date", sa.String(10), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="PKR"),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("amount_paid", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("amount_outstanding", sa.Numeric(14, 2), nullable=False),
        sa.Column("state", sa.String(20), nullable=False, server_default="unpaid"),
        sa.Column("overdue_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reminder_policy_id", sa.String(), nullable=False, server_default="default"),
        sa.Column("escalation_level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
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
            "state IN ('unpaid', 'partial', 'paid', 'overdue')",
            name="invoices_state_chk",
        ),
    )
    op.create_index("idx_invoices_tenant", "invoices", ["tenant_id"])
    op.create_index("idx_invoices_customer", "invoices", ["tenant_id", "customer_id"])
    op.create_index("idx_invoices_state", "invoices", ["tenant_id", "state"])

    # ── 2. payments ───────────────────────────────────────────────────────────────
    op.create_table(
        "payments",
        sa.Column("payment_id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("provider_txn_id", sa.String(256), nullable=False),
        sa.Column("invoice_ref", sa.String(), nullable=True),
        sa.Column("customer_ref", sa.String(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="PKR"),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("received_at", sa.String(32), nullable=False),
        sa.Column("settled_at", sa.String(32), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False, server_default="{}"),
        # Manual/cash proof fields
        sa.Column("entered_by", sa.String(), nullable=True),
        sa.Column("proof_url", sa.Text(), nullable=True),
        sa.Column("proof_note", sa.Text(), nullable=True),
        sa.Column("verification_status", sa.String(24), nullable=False, server_default="not_required"),
        sa.Column("verified_by", sa.String(), nullable=True),
        sa.Column("verified_at", sa.String(32), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('initiated', 'succeeded', 'failed', 'reversed', 'chargeback')",
            name="payments_status_chk",
        ),
        sa.CheckConstraint(
            "verification_status IN ('not_required', 'pending_verification', 'verified', 'rejected')",
            name="payments_verification_chk",
        ),
        sa.CheckConstraint(
            "provider IN ('jazzcash', 'easypaisa', 'bank_transfer', 'cash', 'manual')",
            name="payments_provider_chk",
        ),
    )
    op.create_index("idx_payments_tenant", "payments", ["tenant_id"])
    op.create_index("idx_payments_invoice", "payments", ["tenant_id", "invoice_ref"])
    op.create_index("idx_payments_provider_txn", "payments", ["provider", "provider_txn_id"], unique=True)

    # ── 3. reconciliation_cases ───────────────────────────────────────────────────
    op.create_table(
        "reconciliation_cases",
        sa.Column("case_id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("payment_id", sa.String(), nullable=False),
        sa.Column("invoice_id", sa.String(), nullable=True),
        sa.Column("match_status", sa.String(20), nullable=False),
        sa.Column("mismatch_reason", sa.String(32), nullable=True),
        sa.Column("resolver_user_id", sa.String(), nullable=True),
        sa.Column("resolution_action", sa.Text(), nullable=True),
        sa.Column("resolved_at", sa.String(32), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "match_status IN ('auto_matched', 'needs_review', 'resolved')",
            name="recon_cases_status_chk",
        ),
    )
    op.create_index("idx_recon_tenant", "reconciliation_cases", ["tenant_id"])
    op.create_index("idx_recon_payment", "reconciliation_cases", ["payment_id"])

    # ── 4. conversations ──────────────────────────────────────────────────────────
    op.create_table(
        "conversations",
        sa.Column("conversation_id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("contact_id", sa.String(), nullable=False),
        sa.Column("lead_id", sa.String(), nullable=True),
        sa.Column("channel", sa.String(32), nullable=False, server_default="whatsapp"),
        sa.Column("state", sa.String(32), nullable=False, server_default="open"),
        sa.Column("assigned_to", sa.String(), nullable=True),
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
            "state IN ('open', 'waiting_on_contact', 'resolved', 'closed', 'reopened')",
            name="conversations_state_chk",
        ),
    )
    op.create_index("idx_conv_tenant", "conversations", ["tenant_id"])
    op.create_index("idx_conv_contact", "conversations", ["tenant_id", "contact_id"])

    # ── 5. conversation_messages ──────────────────────────────────────────────────
    op.create_table(
        "conversation_messages",
        sa.Column("message_id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("conversation_id", sa.String(), nullable=False),
        sa.Column("contact_id", sa.String(), nullable=False),
        sa.Column("direction", sa.String(8), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.String(32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "direction IN ('inbound', 'outbound')",
            name="conv_messages_direction_chk",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.conversation_id"],
            name="fk_conv_messages_conversation",
        ),
    )
    op.create_index("idx_conv_messages_conv", "conversation_messages", ["conversation_id"])
    op.create_index("idx_conv_messages_tenant", "conversation_messages", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("conversation_messages")
    op.drop_table("conversations")
    op.drop_table("reconciliation_cases")
    op.drop_table("payments")
    op.drop_table("invoices")
