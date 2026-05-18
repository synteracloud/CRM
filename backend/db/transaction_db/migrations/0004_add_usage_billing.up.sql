-- Migration: 0004_add_usage_billing
-- Adds usage metering, billing meters, and usage aggregation tables.
-- Source: src/usage_billing/entities.py
--
-- Tracked event names (TRACKED_BILLABLE_EVENT_NAMES):
--   communication.message.sent.v1
--   communication.message.engagement.updated.v1
--   workflow.execution.completed.v1
--   notification.dispatched.v1
--   search.document.upserted.v1
--   job.succeeded.v1
--
-- Billing models: flat | per_unit | tiered | volume

SET search_path TO transaction_db, public;

-- ── Billing Meters ────────────────────────────────────────────────────────────
-- Source: src/usage_billing/entities.py MeterRateCard
-- One row per meter_code; tiers stored as JSONB for tiered/volume billing.
CREATE TABLE IF NOT EXISTS billing_meters (
  meter_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  meter_code     TEXT NOT NULL,                       -- e.g. "messages_sent"
  tenant_id      UUID,                                -- NULL = global default meter
  unit           TEXT NOT NULL,                       -- e.g. "message", "workflow_run"
  currency       TEXT NOT NULL DEFAULT 'PKR',
  billing_model  TEXT NOT NULL DEFAULT 'per_unit',
  unit_price     NUMERIC(18, 6),                      -- NULL for tiered billing
  tiers          JSONB NOT NULL DEFAULT '[]',         -- [{up_to, unit_price}] TierPrice[]
  active         BOOLEAN NOT NULL DEFAULT TRUE,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT billing_model_chk CHECK (billing_model IN ('flat', 'per_unit', 'tiered', 'volume')),
  UNIQUE (meter_code, COALESCE(tenant_id, '00000000-0000-0000-0000-000000000000'::UUID))
);
CREATE INDEX IF NOT EXISTS idx_billing_meters_code   ON billing_meters(meter_code, active);
CREATE INDEX IF NOT EXISTS idx_billing_meters_tenant ON billing_meters(tenant_id, active);

-- ── Usage Events (raw inbound tracked events) ─────────────────────────────────
-- Source: src/usage_billing/entities.py TrackedEvent
-- Immutable append-only ledger; deduplicated on (tenant_id, event_id).
CREATE TABLE IF NOT EXISTS usage_events (
  usage_event_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id        TEXT NOT NULL,                      -- source event ID from producer
  tenant_id       UUID NOT NULL,
  event_name      TEXT NOT NULL,
  occurred_at     TIMESTAMPTZ NOT NULL,
  payload         JSONB NOT NULL DEFAULT '{}',
  ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, event_id)
);
CREATE INDEX IF NOT EXISTS idx_usage_events_tenant      ON usage_events(tenant_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_events_event_name  ON usage_events(tenant_id, event_name, occurred_at DESC);

-- ── Usage Records (normalised, billable rows) ─────────────────────────────────
-- Source: src/usage_billing/entities.py UsageRecord
-- Created by metering pipeline; dedupe_key prevents double-counting.
CREATE TABLE IF NOT EXISTS usage_records (
  usage_record_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID NOT NULL,
  subscription_id    UUID NOT NULL,
  account_id         UUID NOT NULL,
  meter_code         TEXT NOT NULL,
  quantity           INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
  unit               TEXT NOT NULL,
  occurred_at        TIMESTAMPTZ NOT NULL,
  source_event_id    TEXT NOT NULL,
  source_event_name  TEXT NOT NULL,
  dedupe_key         TEXT NOT NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (dedupe_key)
);
CREATE INDEX IF NOT EXISTS idx_usage_records_tenant      ON usage_records(tenant_id, meter_code, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_records_sub         ON usage_records(subscription_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_records_event       ON usage_records(tenant_id, source_event_name);

-- ── Usage Aggregates ──────────────────────────────────────────────────────────
-- Source: src/usage_billing/entities.py UsageAggregate
-- Pre-rolled totals per billing period + meter; rebuilt by rating job.
CREATE TABLE IF NOT EXISTS usage_aggregates (
  aggregate_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id                UUID NOT NULL,
  subscription_id          UUID NOT NULL,
  account_id               UUID NOT NULL,
  meter_code               TEXT NOT NULL,
  unit                     TEXT NOT NULL,
  period_start             TIMESTAMPTZ NOT NULL,
  period_end               TIMESTAMPTZ NOT NULL,
  total_quantity           INTEGER NOT NULL DEFAULT 0 CHECK (total_quantity >= 0),
  source_usage_record_ids  JSONB NOT NULL DEFAULT '[]',  -- UUID[]
  computed_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (subscription_id, meter_code, period_start, period_end)
);
CREATE INDEX IF NOT EXISTS idx_usage_aggregates_tenant ON usage_aggregates(tenant_id, meter_code, period_start DESC);
CREATE INDEX IF NOT EXISTS idx_usage_aggregates_sub    ON usage_aggregates(subscription_id, period_start DESC);
