"""AI scores schema: lead_scores, churn_predictions, clv_estimates, copilot_suggestions.

Revision ID: 0010
Revises: 0009
Create Date: 2026-05-30
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lead_scores",
        sa.Column("score_id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(50), nullable=False),
        sa.Column("lead_id", sa.String(36), nullable=False),
        sa.Column("model_id", sa.String(50), nullable=False, server_default="lead_score_v1"),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("score_band", sa.String(20), nullable=False),
        sa.Column("trend", sa.String(10), nullable=False),
        sa.Column("trend_delta", sa.Integer, nullable=True),
        sa.Column("top_drivers", sa.JSON, nullable=True),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=False, server_default="0.85"),
        sa.Column("is_stale", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="ck_lead_score_range"),
        sa.CheckConstraint(
            "score_band IN ('hot','warm','cold','disqualified')", name="ck_lead_score_band"
        ),
        sa.CheckConstraint(
            "trend IN ('rising','stable','falling')", name="ck_lead_score_trend"
        ),
    )
    op.create_index("ix_lead_scores_tenant_lead", "lead_scores", ["tenant_id", "lead_id"])
    op.create_index("ix_lead_scores_tenant_id", "lead_scores", ["tenant_id"])

    op.create_table(
        "churn_predictions",
        sa.Column("prediction_id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(50), nullable=False),
        sa.Column("account_id", sa.String(36), nullable=False),
        sa.Column(
            "model_id", sa.String(50), nullable=False, server_default="churn_predict_v1"
        ),
        sa.Column("churn_probability", sa.Numeric(4, 3), nullable=False),
        sa.Column("risk_band", sa.String(10), nullable=False),
        sa.Column("top_drivers", sa.JSON, nullable=True),
        sa.Column("recommended_action", sa.String(255), nullable=True),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=False, server_default="0.80"),
        sa.Column("evidence_anchor", sa.String(500), nullable=False),
        sa.Column("is_stale", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "risk_band IN ('high','medium','low')", name="ck_churn_risk_band"
        ),
    )
    op.create_index(
        "ix_churn_predictions_tenant_account",
        "churn_predictions",
        ["tenant_id", "account_id"],
    )
    op.create_index(
        "ix_churn_predictions_tenant_id", "churn_predictions", ["tenant_id"]
    )

    op.create_table(
        "clv_estimates",
        sa.Column("estimate_id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(50), nullable=False),
        sa.Column("account_id", sa.String(36), nullable=False),
        sa.Column(
            "model_id", sa.String(50), nullable=False, server_default="clv_estimate_v1"
        ),
        sa.Column("estimated_clv", sa.Numeric(18, 2), nullable=False),
        sa.Column("clv_horizon_months", sa.Integer, nullable=False, server_default="24"),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=False, server_default="0.75"),
        sa.Column("evidence_anchor", sa.String(500), nullable=False),
        sa.Column("is_stale", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_clv_estimates_tenant_account", "clv_estimates", ["tenant_id", "account_id"]
    )
    op.create_index("ix_clv_estimates_tenant_id", "clv_estimates", ["tenant_id"])

    op.create_table(
        "copilot_suggestions",
        sa.Column("suggestion_id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(50), nullable=False),
        sa.Column("target_user_id", sa.String(36), nullable=False),
        sa.Column("suggestion_type", sa.String(30), nullable=False),
        sa.Column("priority", sa.String(10), nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("body", sa.String(500), nullable=False),
        sa.Column("action_label", sa.String(50), nullable=False),
        sa.Column("action_href", sa.String(255), nullable=False),
        sa.Column("evidence_anchor", sa.String(500), nullable=False),
        sa.Column("entity_type", sa.String(30), nullable=True),
        sa.Column("entity_id", sa.String(36), nullable=True),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=False, server_default="0.80"),
        sa.Column("is_dismissed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("dismissed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_actioned", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("actioned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "suggestion_type IN ('next_action','risk_flag','deal_nudge',"
            "'follow_up_overdue','sla_breach_alert','stale_deal')",
            name="ck_suggestion_type",
        ),
        sa.CheckConstraint(
            "priority IN ('urgent','high','medium','low')", name="ck_suggestion_priority"
        ),
    )
    op.create_index(
        "ix_copilot_suggestions_tenant_user",
        "copilot_suggestions",
        ["tenant_id", "target_user_id"],
    )
    op.create_index(
        "ix_copilot_suggestions_tenant_id", "copilot_suggestions", ["tenant_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_copilot_suggestions_tenant_id", table_name="copilot_suggestions")
    op.drop_index("ix_copilot_suggestions_tenant_user", table_name="copilot_suggestions")
    op.drop_table("copilot_suggestions")

    op.drop_index("ix_clv_estimates_tenant_id", table_name="clv_estimates")
    op.drop_index("ix_clv_estimates_tenant_account", table_name="clv_estimates")
    op.drop_table("clv_estimates")

    op.drop_index("ix_churn_predictions_tenant_id", table_name="churn_predictions")
    op.drop_index("ix_churn_predictions_tenant_account", table_name="churn_predictions")
    op.drop_table("churn_predictions")

    op.drop_index("ix_lead_scores_tenant_id", table_name="lead_scores")
    op.drop_index("ix_lead_scores_tenant_lead", table_name="lead_scores")
    op.drop_table("lead_scores")
