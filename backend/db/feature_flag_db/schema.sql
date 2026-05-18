-- FEATURE_FLAG_DB
-- Feature flags, targeting rules, evaluation log.
-- Source: docs/feature-flags-config.md
-- Rule: flags are safe-by-default (OFF). Evaluation is deterministic and logged.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS feature_flag_db;
SET search_path TO feature_flag_db, public;

CREATE OR REPLACE FUNCTION feature_flag_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

-- ── Feature flags ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS feature_flags (
  flag_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key            TEXT NOT NULL UNIQUE,       -- e.g. "whatsapp_360dialog", "compliance_pk"
  name           TEXT NOT NULL,
  description    TEXT,
  default_value  BOOLEAN NOT NULL DEFAULT FALSE,  -- safe-by-default = OFF
  status         TEXT NOT NULL DEFAULT 'active',
  created_by     UUID NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT ff_status_chk CHECK (status IN ('active','archived'))
);
CREATE TRIGGER trg_feature_flags_updated_at BEFORE UPDATE ON feature_flags
  FOR EACH ROW EXECUTE FUNCTION feature_flag_db.set_updated_at();

-- ── Targeting rules (ordered by priority) ─────────────────────────────────────
-- rule_type: tenant | role | percentage | always_on | always_off
CREATE TABLE IF NOT EXISTS flag_rules (
  rule_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  flag_id          UUID NOT NULL REFERENCES feature_flags(flag_id) ON DELETE CASCADE,
  rule_type        TEXT NOT NULL,
  condition_json   JSONB NOT NULL DEFAULT '{}',  -- e.g. {"tenant_id": "abc"} or {"role": "tenant_owner"}
  value            BOOLEAN NOT NULL DEFAULT TRUE,
  priority         INTEGER NOT NULL DEFAULT 0,   -- lower = evaluated first
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT ff_rule_type_chk CHECK (rule_type IN ('tenant','role','percentage','always_on','always_off'))
);
CREATE INDEX IF NOT EXISTS idx_flag_rules_flag_priority ON flag_rules(flag_id, priority);

-- ── Evaluation log (sampled — not every evaluation, only edge cases) ───────────
CREATE TABLE IF NOT EXISTS flag_evaluations (
  eval_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  flag_id          UUID NOT NULL REFERENCES feature_flags(flag_id) ON DELETE CASCADE,
  tenant_id        UUID,
  user_id          UUID,
  evaluated_value  BOOLEAN NOT NULL,
  rule_matched     TEXT,
  evaluated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_flag_evals_flag_time ON flag_evaluations(flag_id, evaluated_at DESC);
