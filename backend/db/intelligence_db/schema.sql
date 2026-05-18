-- INTELLIGENCE_DB
-- Lead/opportunity scoring, model runs, forecast snapshots, feature weights.
-- Source: src/ai_scoring/entities.py
--
-- Entity types: lead | opportunity
-- Model status: active | deprecated | draft
-- Score range: 0–100 integer

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS intelligence_db;
SET search_path TO intelligence_db, public;

CREATE OR REPLACE FUNCTION intelligence_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Scoring Models ─────────────────────────────────────────────────────────────
-- Source: src/ai_scoring/entities.py SCORING_MODEL_FIELDS
-- Registry of model definitions; feature weights per model in model_feature_weights.
CREATE TABLE IF NOT EXISTS scoring_models (
  model_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  entity_type  TEXT NOT NULL,              -- lead | opportunity
  version      INTEGER NOT NULL DEFAULT 1,
  status       TEXT NOT NULL DEFAULT 'active',
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT scoring_model_entity_chk  CHECK (entity_type IN ('lead', 'opportunity')),
  CONSTRAINT scoring_model_status_chk  CHECK (status      IN ('active', 'deprecated', 'draft')),
  UNIQUE (tenant_id, entity_type, version)
);
CREATE TRIGGER trg_scoring_models_updated_at BEFORE UPDATE ON scoring_models
  FOR EACH ROW EXECUTE FUNCTION intelligence_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_scoring_models_tenant ON scoring_models(tenant_id, entity_type, status);

-- ── Model Feature Weights ──────────────────────────────────────────────────────
-- Source: src/ai_scoring/entities.py ScoringFactor (weight per factor_key)
CREATE TABLE IF NOT EXISTS model_feature_weights (
  weight_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_id     UUID NOT NULL REFERENCES scoring_models(model_id) ON DELETE CASCADE,
  tenant_id    UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  factor_key   TEXT NOT NULL,
  weight       NUMERIC(8, 4) NOT NULL CHECK (weight >= 0),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (model_id, factor_key)
);
CREATE INDEX IF NOT EXISTS idx_model_feature_weights_model ON model_feature_weights(model_id);

-- ── Lead Scores (latest score per lead) ───────────────────────────────────────
-- Source: src/ai_scoring/entities.py ScoringResult (entity_type = lead)
-- factors stored as JSONB array of {factor_key, weight, value, evidence}.
CREATE TABLE IF NOT EXISTS lead_scores (
  score_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  entity_id    UUID NOT NULL,              -- lead_id (cross-schema, enforced by app)
  entity_type  TEXT NOT NULL DEFAULT 'lead',
  model_id     UUID REFERENCES scoring_models(model_id) ON DELETE SET NULL,
  score        INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
  factors      JSONB NOT NULL DEFAULT '[]',
  scored_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, entity_id)          -- one current score per entity
);
CREATE INDEX IF NOT EXISTS idx_lead_scores_tenant       ON lead_scores(tenant_id, score DESC);
CREATE INDEX IF NOT EXISTS idx_lead_scores_tenant_model ON lead_scores(tenant_id, model_id);

-- ── Score History (immutable time-series) ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS score_history (
  history_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  entity_id    UUID NOT NULL,
  entity_type  TEXT NOT NULL,
  model_id     UUID REFERENCES scoring_models(model_id) ON DELETE SET NULL,
  score        INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
  factors      JSONB NOT NULL DEFAULT '[]',
  scored_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_score_history_entity ON score_history(tenant_id, entity_id, scored_at DESC);
CREATE INDEX IF NOT EXISTS idx_score_history_tenant ON score_history(tenant_id, entity_type, scored_at DESC);

-- ── Model Runs ────────────────────────────────────────────────────────────────
-- Tracks when scoring ran: how many entities scored, any errors.
CREATE TABLE IF NOT EXISTS model_runs (
  run_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  model_id         UUID NOT NULL REFERENCES scoring_models(model_id) ON DELETE RESTRICT,
  entity_type      TEXT NOT NULL,
  entities_scored  INTEGER NOT NULL DEFAULT 0,
  errors           INTEGER NOT NULL DEFAULT 0,
  status           TEXT NOT NULL DEFAULT 'running',   -- running | completed | failed
  started_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at     TIMESTAMPTZ,
  error_detail     TEXT
);
CREATE INDEX IF NOT EXISTS idx_model_runs_tenant ON model_runs(tenant_id, model_id, started_at DESC);

-- ── Forecast Snapshots ────────────────────────────────────────────────────────
-- Pipeline / revenue forecast snapshots used by predictive forecasting.
CREATE TABLE IF NOT EXISTS forecast_snapshots (
  snapshot_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  period_start   DATE NOT NULL,
  period_end     DATE NOT NULL,
  entity_type    TEXT NOT NULL DEFAULT 'opportunity',
  forecast_value NUMERIC(18, 2) NOT NULL DEFAULT 0,
  confidence     NUMERIC(5, 4),                     -- 0.0000–1.0000
  breakdown      JSONB NOT NULL DEFAULT '{}',        -- stage/owner breakdown
  model_run_id   UUID REFERENCES model_runs(run_id) ON DELETE SET NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT forecast_confidence_chk CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1))
);
CREATE INDEX IF NOT EXISTS idx_forecast_snapshots_tenant ON forecast_snapshots(tenant_id, period_start DESC);
