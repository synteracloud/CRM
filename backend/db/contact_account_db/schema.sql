-- CONTACT_ACCOUNT_DB
-- Contacts (person records), accounts (company records), account hierarchy.
-- Source: docs/domain-model.md (contact + account entities)
-- Deduplication: enforced by (tenant_id, phone_e164) UNIQUE on contacts.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS contact_account_db;
SET search_path TO contact_account_db, public;

CREATE OR REPLACE FUNCTION contact_account_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Contacts ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS contacts (
  contact_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  first_name    TEXT,
  last_name     TEXT,
  email         TEXT,
  phone_e164    TEXT NOT NULL,               -- E.164 normalized, primary identity key
  account_id    UUID,                        -- FK to accounts (nullable for contact-only)
  owner_id      UUID,
  status        TEXT NOT NULL DEFAULT 'active',
  lifecycle     TEXT NOT NULL DEFAULT 'lead',
  tags          JSONB NOT NULL DEFAULT '[]',
  version_no    INTEGER NOT NULL DEFAULT 1,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, phone_e164),
  CONSTRAINT contacts_status_chk    CHECK (status    IN ('active','inactive','blocked')),
  CONSTRAINT contacts_lifecycle_chk CHECK (lifecycle IN ('lead','prospect','customer','churned'))
);
CREATE TRIGGER trg_contacts_updated_at BEFORE UPDATE ON contacts
  FOR EACH ROW EXECUTE FUNCTION contact_account_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_contacts_tenant_phone ON contacts(tenant_id, phone_e164);
CREATE INDEX IF NOT EXISTS idx_contacts_tenant_email ON contacts(tenant_id, email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contacts_account       ON contacts(tenant_id, account_id) WHERE account_id IS NOT NULL;

-- ── Accounts (companies) ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS accounts (
  account_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id         UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  name              TEXT NOT NULL,
  domain            TEXT,
  industry          TEXT,
  size_band         TEXT,                    -- '1-10' | '11-50' | '51-200' | '201-1000' | '1000+'
  owner_id          UUID,
  parent_account_id UUID REFERENCES accounts(account_id) ON DELETE SET NULL,
  version_no        INTEGER NOT NULL DEFAULT 1,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TRIGGER trg_accounts_updated_at BEFORE UPDATE ON accounts
  FOR EACH ROW EXECUTE FUNCTION contact_account_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_accounts_tenant        ON accounts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_accounts_parent        ON accounts(parent_account_id) WHERE parent_account_id IS NOT NULL;

-- ── Account hierarchy (materialized path for fast tree queries) ────────────────
CREATE TABLE IF NOT EXISTS account_hierarchy (
  hierarchy_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id         UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  ancestor_id       UUID NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
  descendant_id     UUID NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
  depth             INTEGER NOT NULL DEFAULT 0,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (ancestor_id, descendant_id)
);
CREATE INDEX IF NOT EXISTS idx_account_hierarchy_descendant ON account_hierarchy(tenant_id, descendant_id);
