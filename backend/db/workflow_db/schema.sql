-- WORKFLOW_DB
-- Workflow definitions (DSL), executions, step results.
-- Source: docs/workflow-dsl.md, docs/workflow-catalog.md, docs/domain-model.md

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS workflow_db;
SET search_path TO workflow_db, public;

CREATE OR REPLACE FUNCTION workflow_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Workflow definitions (versioned DSL) ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS workflow_definitions (
  definition_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  name           TEXT NOT NULL,
  trigger_type   TEXT NOT NULL,              -- event | schedule | manual | webhook
  trigger_config JSONB NOT NULL DEFAULT '{}',
  dsl_json       JSONB NOT NULL,             -- full workflow DSL spec
  version        INTEGER NOT NULL DEFAULT 1,
  status         TEXT NOT NULL DEFAULT 'draft',
  created_by     UUID NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, name, version),
  CONSTRAINT wf_def_status_chk CHECK (status IN ('draft','active','paused','archived'))
);
CREATE TRIGGER trg_wf_definitions_updated_at BEFORE UPDATE ON workflow_definitions
  FOR EACH ROW EXECUTE FUNCTION workflow_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_wf_def_tenant_status ON workflow_definitions(tenant_id, status);

-- ── Workflow executions ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS workflow_executions (
  execution_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id         UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  definition_id     UUID NOT NULL REFERENCES workflow_definitions(definition_id) ON DELETE RESTRICT,
  trigger_event_id  TEXT,                    -- idempotency key for trigger dedup
  entity_type       TEXT,
  entity_id         UUID,
  status            TEXT NOT NULL DEFAULT 'running',
  error_message     TEXT,
  started_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at      TIMESTAMPTZ,
  CONSTRAINT wf_exec_status_chk CHECK (status IN ('running','completed','failed','cancelled','timed_out'))
);
CREATE INDEX IF NOT EXISTS idx_wf_exec_tenant_status ON workflow_executions(tenant_id, status, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_wf_exec_entity        ON workflow_executions(tenant_id, entity_type, entity_id);

-- ── Workflow step results ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS workflow_steps (
  step_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  execution_id  UUID NOT NULL REFERENCES workflow_executions(execution_id) ON DELETE CASCADE,
  tenant_id     UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  step_name     TEXT NOT NULL,
  step_type     TEXT NOT NULL,               -- action | condition | wait | parallel
  status        TEXT NOT NULL DEFAULT 'pending',
  input_json    JSONB NOT NULL DEFAULT '{}',
  output_json   JSONB NOT NULL DEFAULT '{}',
  error_message TEXT,
  started_at    TIMESTAMPTZ,
  completed_at  TIMESTAMPTZ,
  CONSTRAINT wf_step_status_chk CHECK (status IN ('pending','running','completed','failed','skipped'))
);
CREATE INDEX IF NOT EXISTS idx_wf_steps_execution ON workflow_steps(execution_id, started_at);
