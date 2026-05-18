-- TERRITORY_DB
-- Territories, assignment rules, and subject-to-territory assignments.
-- Source: src/territory_management/entities.py
--
-- Territory hierarchy: parent_territory_id self-ref (nullable = root)
-- Subject types: user | team | account | lead
-- Owner types: user | team
-- Territory status: active | inactive

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS territory_db;
SET search_path TO territory_db, public;

CREATE OR REPLACE FUNCTION territory_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Territories ────────────────────────────────────────────────────────────────
-- Source: src/territory_management/entities.py Territory
-- Self-referencing hierarchy: parent_territory_id NULL = root territory.
CREATE TABLE IF NOT EXISTS territories (
  territory_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id             UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  name                  TEXT NOT NULL,
  code                  TEXT NOT NULL,              -- short unique code within tenant
  parent_territory_id   UUID REFERENCES territories(territory_id) ON DELETE RESTRICT,
  level                 INTEGER NOT NULL DEFAULT 0, -- 0 = root, increments per depth
  status                TEXT NOT NULL DEFAULT 'active',
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT territory_status_chk CHECK (status IN ('active', 'inactive')),
  CONSTRAINT territory_level_chk  CHECK (level >= 0),
  UNIQUE (tenant_id, code)
);
CREATE TRIGGER trg_territories_updated_at BEFORE UPDATE ON territories
  FOR EACH ROW EXECUTE FUNCTION territory_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_territories_tenant_status ON territories(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_territories_parent        ON territories(parent_territory_id);

-- ── Territory Rules ────────────────────────────────────────────────────────────
-- Source: src/territory_management/entities.py TerritoryRule
-- criteria stored as JSONB: key/value pairs for matching logic.
-- Rules are evaluated in ascending priority; first match wins.
CREATE TABLE IF NOT EXISTS territory_rules (
  rule_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  territory_id   UUID NOT NULL REFERENCES territories(territory_id) ON DELETE CASCADE,
  subject_type   TEXT NOT NULL,
  priority       INTEGER NOT NULL DEFAULT 0,
  criteria       JSONB NOT NULL DEFAULT '{}',   -- e.g. {"city": "Lahore", "source": "web"}
  owner_type     TEXT NOT NULL,
  owner_id       TEXT NOT NULL,                 -- user_id or team_id
  active         BOOLEAN NOT NULL DEFAULT TRUE,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT territory_rule_subject_chk CHECK (subject_type IN ('user', 'team', 'account', 'lead')),
  CONSTRAINT territory_rule_owner_chk   CHECK (owner_type   IN ('user', 'team'))
);
CREATE TRIGGER trg_territory_rules_updated_at BEFORE UPDATE ON territory_rules
  FOR EACH ROW EXECUTE FUNCTION territory_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_territory_rules_tenant    ON territory_rules(tenant_id, active, priority);
CREATE INDEX IF NOT EXISTS idx_territory_rules_territory ON territory_rules(territory_id, priority ASC);

-- ── Territory Assignments ──────────────────────────────────────────────────────
-- Source: src/territory_management/entities.py TerritoryAssignment
-- Records which territory + owner a subject (lead/account/etc.) was assigned to.
CREATE TABLE IF NOT EXISTS territory_assignments (
  assignment_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  subject_type     TEXT NOT NULL,
  subject_id       UUID NOT NULL,               -- lead_id | contact_id | account_id
  territory_id     UUID NOT NULL REFERENCES territories(territory_id) ON DELETE RESTRICT,
  owner_type       TEXT NOT NULL,
  owner_id         TEXT NOT NULL,               -- user_id or team_id
  assignment_rule  TEXT NOT NULL,               -- rule_id or "manual" or "system"
  assigned_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  superseded_at    TIMESTAMPTZ,                 -- NULL = current active assignment
  CONSTRAINT territory_assign_subject_chk CHECK (subject_type IN ('user', 'team', 'account', 'lead')),
  CONSTRAINT territory_assign_owner_chk   CHECK (owner_type   IN ('user', 'team'))
);
CREATE INDEX IF NOT EXISTS idx_territory_assignments_subject   ON territory_assignments(tenant_id, subject_type, subject_id);
CREATE INDEX IF NOT EXISTS idx_territory_assignments_territory ON territory_assignments(territory_id, assigned_at DESC);
CREATE INDEX IF NOT EXISTS idx_territory_assignments_active    ON territory_assignments(tenant_id, subject_type, subject_id)
  WHERE superseded_at IS NULL;
