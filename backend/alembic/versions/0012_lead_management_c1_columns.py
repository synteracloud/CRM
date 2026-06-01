"""Add C1 columns to lead_management_db.leads and leads repository fixes.

Revision ID: 0012
Revises: 0011
Create Date: 2026-06-02
"""

from __future__ import annotations
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    raw = conn.connection.dbapi_connection
    cur = raw.cursor()
    try:
        # Add columns that leads.repository.js expects but schema.sql didn't have
        cur.execute("""
            ALTER TABLE lead_management_db.leads
                ADD COLUMN IF NOT EXISTS deleted_at         TIMESTAMPTZ,
                ADD COLUMN IF NOT EXISTS title              TEXT,
                ADD COLUMN IF NOT EXISTS contact_name       TEXT,
                ADD COLUMN IF NOT EXISTS contact_phone_e164 TEXT,
                ADD COLUMN IF NOT EXISTS contact_email      TEXT,
                ADD COLUMN IF NOT EXISTS estimated_value    NUMERIC,
                ADD COLUMN IF NOT EXISTS currency           TEXT NOT NULL DEFAULT 'PKR',
                ADD COLUMN IF NOT EXISTS notes              TEXT,
                ADD COLUMN IF NOT EXISTS metadata           JSONB;
        """)
        # Relax the NOT NULL on contact_id (repository doesn't always provide it)
        cur.execute("""
            ALTER TABLE lead_management_db.leads
                ALTER COLUMN contact_id DROP NOT NULL;
        """)
        raw.commit()
    except Exception:
        raw.rollback()
        raise
    finally:
        cur.close()


def downgrade() -> None:
    conn = op.get_bind()
    raw = conn.connection.dbapi_connection
    cur = raw.cursor()
    try:
        for col in ['deleted_at', 'title', 'contact_name', 'contact_phone_e164',
                    'contact_email', 'estimated_value', 'currency', 'notes', 'metadata']:
            cur.execute(f"ALTER TABLE lead_management_db.leads DROP COLUMN IF EXISTS {col}")
        raw.commit()
    finally:
        cur.close()
