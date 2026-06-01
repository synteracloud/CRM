"""Create all domain PostgreSQL schemas (org_tenant_db, identity_auth_db, etc.)

These schemas were pre-built locally via direct SQL; this migration
applies them to the Render production PostgreSQL database.

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-01
"""

from __future__ import annotations
from pathlib import Path
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None

DB_SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "db"

SCHEMAS = [
    "org_tenant_db",
    "identity_auth_db",
    "lead_management_db",
    "contact_account_db",
    "opportunity_db",
    "transaction_db",
    "activity_task_db",
    "feature_flag_db",
]

def upgrade() -> None:
    for schema in SCHEMAS:
        sql_path = DB_SCHEMA_ROOT / schema / "schema.sql"
        if sql_path.exists():
            sql = sql_path.read_text(encoding="utf-8")
            # Execute each statement separately, skipping search_path
            for stmt in sql.split(";"):
                stmt = stmt.strip()
                if not stmt:
                    continue
                if stmt.upper().startswith("SET SEARCH_PATH"):
                    continue
                if stmt.startswith("--"):
                    continue
                op.execute(stmt)

def downgrade() -> None:
    for schema in reversed(SCHEMAS):
        op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
