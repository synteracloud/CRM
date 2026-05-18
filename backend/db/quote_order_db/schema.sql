-- QUOTE_ORDER_DB
-- CPQ quotes, quote line items, orders, order line items.
-- Source: docs/cpq-quotes-orders.md, docs/domain-model.md
-- Rule: Order is frozen snapshot of accepted quote — never mutated post-acceptance.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS quote_order_db;
SET search_path TO quote_order_db, public;

CREATE OR REPLACE FUNCTION quote_order_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Quotes ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS quotes (
  quote_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  opportunity_id  UUID NOT NULL,
  owner_id        UUID NOT NULL,
  status          TEXT NOT NULL DEFAULT 'draft',
  valid_until     DATE,
  total_amount    NUMERIC(18,2) NOT NULL DEFAULT 0,
  currency        TEXT NOT NULL DEFAULT 'PKR',
  version_no      INTEGER NOT NULL DEFAULT 1,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  accepted_at     TIMESTAMPTZ,
  CONSTRAINT quotes_status_chk CHECK (status IN ('draft','pending_approval','approved','accepted','rejected','expired'))
);
CREATE TRIGGER trg_quotes_updated_at BEFORE UPDATE ON quotes
  FOR EACH ROW EXECUTE FUNCTION quote_order_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_quotes_opportunity ON quotes(tenant_id, opportunity_id);

-- ── Quote line items ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS quote_line_items (
  line_item_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quote_id      UUID NOT NULL REFERENCES quotes(quote_id) ON DELETE CASCADE,
  tenant_id     UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  product_id    UUID NOT NULL,
  quantity      NUMERIC(10,2) NOT NULL DEFAULT 1,
  unit_price    NUMERIC(18,2) NOT NULL,
  currency      TEXT NOT NULL DEFAULT 'PKR',
  discount_pct  NUMERIC(5,2) NOT NULL DEFAULT 0,
  total_price   NUMERIC(18,2) GENERATED ALWAYS AS (quantity * unit_price * (1 - discount_pct/100)) STORED,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Orders ─────────────────────────────────────────────────────────────────────
-- Immutable after creation. Frozen from accepted quote.
CREATE TABLE IF NOT EXISTS orders (
  order_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  quote_id        UUID NOT NULL REFERENCES quotes(quote_id) ON DELETE RESTRICT,
  opportunity_id  UUID NOT NULL,
  owner_id        UUID NOT NULL,
  status          TEXT NOT NULL DEFAULT 'pending_fulfillment',
  total_amount    NUMERIC(18,2) NOT NULL,
  currency        TEXT NOT NULL DEFAULT 'PKR',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT orders_status_chk CHECK (status IN ('pending_fulfillment','fulfilled','cancelled','refunded'))
);
CREATE TRIGGER trg_orders_updated_at BEFORE UPDATE ON orders
  FOR EACH ROW EXECUTE FUNCTION quote_order_db.set_updated_at();

-- ── Order line items (frozen copy from quote at acceptance) ────────────────────
CREATE TABLE IF NOT EXISTS order_line_items (
  line_item_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id      UUID NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  tenant_id     UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  product_id    UUID NOT NULL,
  product_name  TEXT NOT NULL,              -- denormalized snapshot at order time
  quantity      NUMERIC(10,2) NOT NULL,
  unit_price    NUMERIC(18,2) NOT NULL,
  currency      TEXT NOT NULL DEFAULT 'PKR',
  total_price   NUMERIC(18,2) NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
