-- LEAD_MANAGEMENT_DB
-- Leads, assignments, history.
-- Source: docs/domain-model.md (lead entity), docs/followup-enforcement-model.md
-- Every lead MUST have an owner. Every lead MUST have a follow-up scheduled.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS lead_management_db;
SET search_path TO lead_management_db, public;

CREATE OR REPLACE FUNCTION lead_management_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Leads ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS leads (
  lead_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  contact_id       UUID NOT NULL,            -- FK enforced by app (cross-schema)
  owner_id         UUID NOT NULL,            -- mandatory — no orphan leads
  stage            TEXT NOT NULL DEFAULT 'new',
  status           TEXT NOT NULL DEFAULT 'open',
  priority         TEXT NOT NULL DEFAULT 'warm',
  source           TEXT NOT NULL DEFAULT 'manual',  -- whatsapp | web | import | manual
  campaign_id      UUID,
  last_activity_at TIMESTAMPTZ,
  version_no       INTEGER NOT NULL DEFAULT 1,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT leads_stage_chk    CHECK (stage    IN ('new','qualifying','nurturing','proposal','negotiation','won','lost','disqualified')),
  CONSTRAINT leads_status_chk   CHECK (status   IN ('open','working','idle','closed')),
  CONSTRAINT leads_priority_chk CHECK (priority IN ('hot','warm','cold')),
  CONSTRAINT leads_source_chk   CHECK (source   IN ('whatsapp','web','import','manual','referral','campaign'))
);
CREATE TRIGGER trg_leads_updated_at BEFORE UPDATE ON leads
  FOR EACH ROW EXECUTE FUNCTION lead_management_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_leads_tenant_owner     ON leads(tenant_id, owner_id);
CREATE INDEX IF NOT EXISTS idx_leads_tenant_stage     ON leads(tenant_id, stage);
CREATE INDEX IF NOT EXISTS idx_leads_tenant_updated   ON leads(tenant_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_contact          ON leads(tenant_id, contact_id);

-- ── Lead assignments ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lead_assignments (
  assignment_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id         UUID NOT NULL REFERENCES leads(lead_id) ON DELETE CASCADE,
  tenant_id       UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  owner_id        UUID NOT NULL,
  assigned_by     UUID,                      -- NULL = system assignment
  reason          TEXT,
  assigned_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lead_assignments_lead ON lead_assignments(lead_id, assigned_at DESC);

-- ── Lead field history (immutable audit trail of field changes) ────────────────
CREATE TABLE IF NOT EXISTS lead_history (
  history_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id      UUID NOT NULL REFERENCES leads(lead_id) ON DELETE CASCADE,
  tenant_id    UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  field_name   TEXT NOT NULL,
  old_value    TEXT,
  new_value    TEXT,
  changed_by   UUID NOT NULL,
  changed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lead_history_lead ON lead_history(lead_id, changed_at DESC);
