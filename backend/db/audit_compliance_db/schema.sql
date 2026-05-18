-- AUDIT_COMPLIANCE_DB
-- Immutable audit log with hash-chain verification, compliance event records.
-- Source: docs/observability-audit.md, docs/activity-control-model.md
-- Rule: audit_log is append-only — no UPDATE, no DELETE permitted.
-- Chain: hash = sha256(prev_hash || actor_id || action_type || entity_id || occurred_at || payload)

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS audit_compliance_db;
SET search_path TO audit_compliance_db, public;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Audit log (immutable, hash-chained) ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
  log_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  actor_user_id  UUID,                       -- NULL for system-generated entries
  action_type    TEXT NOT NULL,              -- e.g. "lead.stage.changed"
  entity_type    TEXT NOT NULL,
  entity_id      UUID NOT NULL,
  before_state   JSONB,
  after_state    JSONB,
  ip_address     TEXT,
  user_agent     TEXT,
  trace_id       TEXT NOT NULL,
  source_service TEXT NOT NULL,
  hash           TEXT NOT NULL,              -- sha256 of this row's canonical fields
  prev_hash      TEXT NOT NULL DEFAULT '0', -- sha256 of previous entry (genesis = '0')
  occurred_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
  -- No updated_at — this table is append-only by design.
);
CREATE INDEX IF NOT EXISTS idx_audit_tenant_entity    ON audit_log(tenant_id, entity_type, entity_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_tenant_actor     ON audit_log(tenant_id, actor_user_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_tenant_occurred  ON audit_log(tenant_id, occurred_at DESC);

-- Prevent any UPDATE or DELETE on audit_log rows.
CREATE OR REPLACE RULE audit_log_no_update AS ON UPDATE TO audit_log DO INSTEAD NOTHING;
CREATE OR REPLACE RULE audit_log_no_delete AS ON DELETE TO audit_log DO INSTEAD NOTHING;

-- ── Compliance events (country-specific regulatory obligations) ────────────────
CREATE TABLE IF NOT EXISTS compliance_events (
  event_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  country        TEXT NOT NULL,              -- ISO-3166 alpha-2
  action_type    TEXT NOT NULL,
  entity_id      UUID NOT NULL,
  payload        JSONB NOT NULL DEFAULT '{}',
  check_result   TEXT NOT NULL,              -- 'allowed' | 'blocked'
  obligations    TEXT[] NOT NULL DEFAULT '{}',
  report_ref     TEXT,                       -- provider-returned report reference
  occurred_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_compliance_tenant_country ON compliance_events(tenant_id, country, occurred_at DESC);
