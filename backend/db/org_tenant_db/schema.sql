-- ORG_TENANT_DB
-- Tenants, entitlements, organizations, memberships.
-- Source: docs/org-multi-tenancy.md, docs/domain-model.md (tenant domain)
-- Hard isolation: no cross-tenant data access at any layer.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS org_tenant_db;
SET search_path TO org_tenant_db, public;

CREATE OR REPLACE FUNCTION org_tenant_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

-- ── Tenants ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tenants (
  tenant_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  slug        TEXT NOT NULL UNIQUE,          -- URL-safe identifier
  status      TEXT NOT NULL DEFAULT 'active',
  plan        TEXT NOT NULL DEFAULT 'starter',
  region      TEXT NOT NULL DEFAULT 'ap-south-1',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT tenants_status_chk  CHECK (status IN ('active', 'suspended', 'deactivated', 'trial')),
  CONSTRAINT tenants_plan_chk    CHECK (plan   IN ('starter', 'growth', 'enterprise'))
);
CREATE TRIGGER trg_tenants_updated_at BEFORE UPDATE ON tenants
  FOR EACH ROW EXECUTE FUNCTION org_tenant_db.set_updated_at();

-- ── Tenant entitlements (feature gates per plan) ───────────────────────────────
CREATE TABLE IF NOT EXISTS tenant_entitlements (
  entitlement_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  feature         TEXT NOT NULL,             -- e.g. "whatsapp", "ai_scoring"
  enabled         BOOLEAN NOT NULL DEFAULT TRUE,
  value_limit     INTEGER,                   -- NULL = unlimited
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, feature)
);
CREATE TRIGGER trg_tenant_entitlements_updated_at BEFORE UPDATE ON tenant_entitlements
  FOR EACH ROW EXECUTE FUNCTION org_tenant_db.set_updated_at();

-- ── Organizations (sub-units within a tenant) ──────────────────────────────────
CREATE TABLE IF NOT EXISTS organizations (
  org_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
  name        TEXT NOT NULL,
  type        TEXT NOT NULL DEFAULT 'team',  -- team | division | region
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, name)
);
CREATE TRIGGER trg_organizations_updated_at BEFORE UPDATE ON organizations
  FOR EACH ROW EXECUTE FUNCTION org_tenant_db.set_updated_at();

-- ── Organization memberships ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS organization_memberships (
  membership_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id         UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
  tenant_id      UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
  user_id        UUID NOT NULL,              -- FK enforced by app (cross-schema)
  role           TEXT NOT NULL DEFAULT 'member',
  joined_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (org_id, user_id),
  CONSTRAINT org_membership_role_chk CHECK (role IN ('owner', 'admin', 'member', 'viewer'))
);
CREATE INDEX IF NOT EXISTS idx_org_memberships_tenant_user ON organization_memberships(tenant_id, user_id);
