-- CAMPAIGN_DB
-- Campaigns, segment definitions, journey definitions, and journey instances.
-- Source: src/campaigns/entities.py
--         src/automation_journeys/entities.py
--
-- Campaign status: draft | active | completed
-- Membership status: pending | active | completed | removed
-- Journey instance status: running | waiting | completed | failed | stopped
-- Step actions: email | update | assign | delay

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS campaign_db;
SET search_path TO campaign_db, public;

CREATE OR REPLACE FUNCTION campaign_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Segment Definitions ────────────────────────────────────────────────────────
-- Source: src/campaigns/entities.py SegmentDefinition
-- rules stored as JSONB array of {field, operator, value} objects.
CREATE TABLE IF NOT EXISTS campaign_segments (
  segment_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  name         TEXT NOT NULL,
  description  TEXT,
  entity_type  TEXT NOT NULL DEFAULT 'lead',
  rules        JSONB NOT NULL DEFAULT '[]',    -- SegmentRule[]
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT segment_entity_type_chk CHECK (entity_type IN ('lead', 'contact'))
);
CREATE TRIGGER trg_campaign_segments_updated_at BEFORE UPDATE ON campaign_segments
  FOR EACH ROW EXECUTE FUNCTION campaign_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_campaign_segments_tenant ON campaign_segments(tenant_id);

-- ── Campaigns ──────────────────────────────────────────────────────────────────
-- Source: src/campaigns/entities.py Campaign
CREATE TABLE IF NOT EXISTS campaigns (
  campaign_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  owner_user_id   UUID NOT NULL,
  name            TEXT NOT NULL,
  description     TEXT,
  status          TEXT NOT NULL DEFAULT 'draft',
  segment_id      UUID REFERENCES campaign_segments(segment_id) ON DELETE SET NULL,
  starts_at       TIMESTAMPTZ,
  ends_at         TIMESTAMPTZ,
  activated_at    TIMESTAMPTZ,
  completed_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT campaign_status_chk CHECK (status IN ('draft', 'active', 'completed'))
);
CREATE TRIGGER trg_campaigns_updated_at BEFORE UPDATE ON campaigns
  FOR EACH ROW EXECUTE FUNCTION campaign_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_campaigns_tenant_status  ON campaigns(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_campaigns_tenant_owner   ON campaigns(tenant_id, owner_user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_tenant_updated ON campaigns(tenant_id, updated_at DESC);

-- ── Campaign Lead Links ────────────────────────────────────────────────────────
-- Source: src/campaigns/entities.py CampaignLeadLink
CREATE TABLE IF NOT EXISTS campaign_lead_links (
  campaign_lead_link_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id              UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  campaign_id            UUID NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
  lead_id                UUID NOT NULL,              -- FK enforced by app (cross-schema)
  membership_status      TEXT NOT NULL DEFAULT 'pending',
  linked_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT lead_link_status_chk CHECK (membership_status IN ('pending', 'active', 'completed', 'removed')),
  UNIQUE (campaign_id, lead_id)
);
CREATE TRIGGER trg_campaign_lead_links_updated_at BEFORE UPDATE ON campaign_lead_links
  FOR EACH ROW EXECUTE FUNCTION campaign_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_campaign_lead_links_campaign ON campaign_lead_links(campaign_id, membership_status);
CREATE INDEX IF NOT EXISTS idx_campaign_lead_links_lead     ON campaign_lead_links(tenant_id, lead_id);

-- ── Campaign Contact Links ─────────────────────────────────────────────────────
-- Source: src/campaigns/entities.py CampaignContactLink
CREATE TABLE IF NOT EXISTS campaign_contact_links (
  campaign_contact_link_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id                 UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  campaign_id               UUID NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
  contact_id                UUID NOT NULL,           -- FK enforced by app (cross-schema)
  membership_status         TEXT NOT NULL DEFAULT 'pending',
  linked_at                 TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT contact_link_status_chk CHECK (membership_status IN ('pending', 'active', 'completed', 'removed')),
  UNIQUE (campaign_id, contact_id)
);
CREATE TRIGGER trg_campaign_contact_links_updated_at BEFORE UPDATE ON campaign_contact_links
  FOR EACH ROW EXECUTE FUNCTION campaign_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_campaign_contact_links_campaign ON campaign_contact_links(campaign_id, membership_status);
CREATE INDEX IF NOT EXISTS idx_campaign_contact_links_contact  ON campaign_contact_links(tenant_id, contact_id);

-- ── Journey Definitions ────────────────────────────────────────────────────────
-- Source: src/automation_journeys/entities.py JourneyDefinition + JourneyStep
-- steps stored as JSONB array of {step_id, action, config, delay_seconds}.
CREATE TABLE IF NOT EXISTS journey_definitions (
  journey_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  name           TEXT NOT NULL,
  trigger_event  TEXT NOT NULL,
  steps          JSONB NOT NULL DEFAULT '[]',   -- JourneyStep[]
  is_active      BOOLEAN NOT NULL DEFAULT TRUE,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TRIGGER trg_journey_definitions_updated_at BEFORE UPDATE ON journey_definitions
  FOR EACH ROW EXECUTE FUNCTION campaign_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_journey_definitions_tenant        ON journey_definitions(tenant_id, is_active);
CREATE INDEX IF NOT EXISTS idx_journey_definitions_trigger_event ON journey_definitions(tenant_id, trigger_event);

-- ── Journey Instances ──────────────────────────────────────────────────────────
-- Source: src/automation_journeys/entities.py JourneyInstance
-- execution_log stored as JSONB array; one entry per step executed.
CREATE TABLE IF NOT EXISTS journey_instances (
  instance_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  journey_id           UUID NOT NULL REFERENCES journey_definitions(journey_id) ON DELETE RESTRICT,
  trigger_event        TEXT NOT NULL,
  trigger_event_id     TEXT NOT NULL,            -- external event ID that fired the journey
  status               TEXT NOT NULL DEFAULT 'running',
  current_step_index   INTEGER NOT NULL DEFAULT 0,
  started_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  waiting_until        TIMESTAMPTZ,
  completed_at         TIMESTAMPTZ,
  error_message        TEXT,
  execution_log        JSONB NOT NULL DEFAULT '[]',
  CONSTRAINT journey_instance_status_chk CHECK (
    status IN ('running', 'waiting', 'completed', 'failed', 'stopped')
  )
);
CREATE INDEX IF NOT EXISTS idx_journey_instances_tenant_status ON journey_instances(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_journey_instances_journey       ON journey_instances(journey_id, status);
CREATE INDEX IF NOT EXISTS idx_journey_instances_waiting       ON journey_instances(waiting_until) WHERE status = 'waiting';

-- ── Journey Step Events (immutable step execution records) ────────────────────
CREATE TABLE IF NOT EXISTS journey_step_events (
  step_event_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  instance_id      UUID NOT NULL REFERENCES journey_instances(instance_id) ON DELETE CASCADE,
  tenant_id        UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  step_id          TEXT NOT NULL,
  action           TEXT NOT NULL,
  outcome          TEXT NOT NULL,   -- success | failed | skipped
  detail           JSONB NOT NULL DEFAULT '{}',
  executed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_journey_step_events_instance ON journey_step_events(instance_id, executed_at);
