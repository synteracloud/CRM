-- IDENTITY_AUTH_DB
-- Users, roles, permissions, sessions, refresh tokens.
-- Source: docs/identity-auth-rbac.md, docs/domain-model.md (identity domain)
-- Tenant isolation: every user is scoped to exactly one tenant.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS identity_auth_db;
SET search_path TO identity_auth_db, public;

CREATE OR REPLACE FUNCTION identity_auth_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

-- ── Tenants (reference — owned by org_tenant_db, mirrored here for FK) ────────
CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id   UUID PRIMARY KEY,
  status      TEXT NOT NULL DEFAULT 'active',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Users ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  user_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  email          TEXT NOT NULL,
  password_hash  TEXT,                        -- NULL for SSO-only users
  full_name      TEXT NOT NULL,
  status         TEXT NOT NULL DEFAULT 'active',
  last_login_at  TIMESTAMPTZ,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, email),
  CONSTRAINT users_status_chk CHECK (status IN ('active', 'suspended', 'deactivated'))
);
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION identity_auth_db.set_updated_at();

-- ── Roles ──────────────────────────────────────────────────────────────────────
-- 6 canonical roles per docs/identity-auth-rbac.md:
--   tenant_owner | tenant_admin | manager | agent | analyst | auditor | integration_service
CREATE TABLE IF NOT EXISTS roles (
  role_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  name        TEXT NOT NULL,
  description TEXT,
  is_system   BOOLEAN NOT NULL DEFAULT FALSE,  -- system roles cannot be deleted
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, name)
);

-- ── Permissions (scopes) ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS permissions (
  permission_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scope          TEXT NOT NULL UNIQUE,   -- e.g. "leads.read", "payments.create"
  description    TEXT,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Role → Permission mapping ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS role_permissions (
  role_id        UUID NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
  permission_id  UUID NOT NULL REFERENCES permissions(permission_id) ON DELETE CASCADE,
  granted_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (role_id, permission_id)
);

-- ── User → Role assignment ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_roles (
  user_id     UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  role_id     UUID NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
  tenant_id   UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  granted_by  UUID REFERENCES users(user_id) ON DELETE SET NULL,
  granted_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, role_id)
);

-- ── Sessions ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
  session_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  tenant_id    UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  token_hash   TEXT NOT NULL UNIQUE,
  ip_address   TEXT,
  user_agent   TEXT,
  expires_at   TIMESTAMPTZ NOT NULL,
  revoked_at   TIMESTAMPTZ,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id, expires_at);

-- ── Refresh tokens ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS refresh_tokens (
  token_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  tenant_id   UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  token_hash  TEXT NOT NULL UNIQUE,
  expires_at  TIMESTAMPTZ NOT NULL,
  rotated_at  TIMESTAMPTZ,
  revoked_at  TIMESTAMPTZ,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
