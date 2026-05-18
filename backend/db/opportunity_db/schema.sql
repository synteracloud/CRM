-- OPPORTUNITY_DB
-- Opportunities (pipeline deals), line items, forecast records.
-- Source: docs/opportunities-pipeline.md, docs/domain-model.md
-- Events: opportunity.stage.changed.v1, opportunity.closed.v1 on stage transitions.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS opportunity_db;
SET search_path TO opportunity_db, public;

CREATE OR REPLACE FUNCTION opportunity_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Opportunities ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS opportunities (
  opportunity_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  account_id         UUID,
  contact_id         UUID,
  owner_id           UUID NOT NULL,
  name               TEXT NOT NULL,
  stage              TEXT NOT NULL DEFAULT 'qualification',
  amount             NUMERIC(18,2),
  currency           TEXT NOT NULL DEFAULT 'PKR',
  close_date         DATE,
  probability        SMALLINT DEFAULT 0,      -- 0-100
  forecast_category  TEXT NOT NULL DEFAULT 'pipeline',
  close_reason       TEXT,                    -- populated on won/lost
  version_no         INTEGER NOT NULL DEFAULT 1,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  closed_at          TIMESTAMPTZ,
  CONSTRAINT opp_stage_chk       CHECK (stage             IN ('qualification','discovery','proposal','negotiation','closed_won','closed_lost')),
  CONSTRAINT opp_probability_chk CHECK (probability        BETWEEN 0 AND 100),
  CONSTRAINT opp_forecast_chk    CHECK (forecast_category  IN ('pipeline','best_case','commit','closed','omitted'))
);
CREATE TRIGGER trg_opportunities_updated_at BEFORE UPDATE ON opportunities
  FOR EACH ROW EXECUTE FUNCTION opportunity_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_opp_tenant_owner ON opportunities(tenant_id, owner_id);
CREATE INDEX IF NOT EXISTS idx_opp_tenant_stage ON opportunities(tenant_id, stage);

-- ── Opportunity line items ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS opportunity_line_items (
  line_item_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  opportunity_id  UUID NOT NULL REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,
  tenant_id       UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  product_id      UUID NOT NULL,
  quantity        NUMERIC(10,2) NOT NULL DEFAULT 1,
  unit_price      NUMERIC(18,2) NOT NULL,
  currency        TEXT NOT NULL DEFAULT 'PKR',
  discount_pct    NUMERIC(5,2) NOT NULL DEFAULT 0,
  total_price     NUMERIC(18,2) GENERATED ALWAYS AS (quantity * unit_price * (1 - discount_pct/100)) STORED,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Forecast records (period snapshots) ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS forecast_records (
  forecast_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  opportunity_id     UUID NOT NULL REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,
  tenant_id          UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  owner_id           UUID NOT NULL,
  forecast_category  TEXT NOT NULL,
  amount             NUMERIC(18,2) NOT NULL,
  currency           TEXT NOT NULL DEFAULT 'PKR',
  period             TEXT NOT NULL,           -- e.g. "2026-Q2"
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_forecast_tenant_period ON forecast_records(tenant_id, period);
