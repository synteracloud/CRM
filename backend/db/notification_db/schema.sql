-- NOTIFICATION_DB
-- User-facing notifications, templates, delivery log.
-- Source: docs/service-map.md (Notification Orchestrator), docs/domain-model.md
-- Rule: Notification Orchestrator owns dispatch; Communication Service owns CRM threads.
--       These are distinct — notifications are system alerts, not conversation messages.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS notification_db;
SET search_path TO notification_db, public;

CREATE OR REPLACE FUNCTION notification_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Notifications ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
  notification_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  recipient_user_id  UUID NOT NULL,
  type               TEXT NOT NULL,          -- e.g. "lead_assigned", "followup_overdue"
  channel            TEXT NOT NULL,          -- in_app | email | sms
  status             TEXT NOT NULL DEFAULT 'pending',
  subject            TEXT,
  body               TEXT NOT NULL,
  metadata           JSONB NOT NULL DEFAULT '{}',
  sent_at            TIMESTAMPTZ,
  delivered_at       TIMESTAMPTZ,
  read_at            TIMESTAMPTZ,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT notif_channel_chk CHECK (channel IN ('in_app','email','sms','push')),
  CONSTRAINT notif_status_chk  CHECK (status  IN ('pending','sent','delivered','read','failed'))
);
CREATE TRIGGER trg_notifications_updated_at BEFORE UPDATE ON notifications
  FOR EACH ROW EXECUTE FUNCTION notification_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_notif_recipient ON notifications(tenant_id, recipient_user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notif_unread    ON notifications(tenant_id, recipient_user_id, status) WHERE status NOT IN ('read','failed');

-- ── Notification templates ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notification_templates (
  template_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,  -- NULL = system template
  key          TEXT NOT NULL,
  locale       TEXT NOT NULL DEFAULT 'en',
  channel      TEXT NOT NULL,
  subject      TEXT,
  body         TEXT NOT NULL,               -- Handlebars/Jinja2 template string
  version      INTEGER NOT NULL DEFAULT 1,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (key, locale, channel, version)
);
CREATE TRIGGER trg_notif_templates_updated_at BEFORE UPDATE ON notification_templates
  FOR EACH ROW EXECUTE FUNCTION notification_db.set_updated_at();

-- ── Delivery log ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS delivery_log (
  log_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  notification_id      UUID NOT NULL REFERENCES notifications(notification_id) ON DELETE CASCADE,
  tenant_id            UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  provider             TEXT NOT NULL,        -- sendgrid | twilio | in_app
  provider_message_id  TEXT,
  status               TEXT NOT NULL,
  error_code           TEXT,
  attempted_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_delivery_log_notif ON delivery_log(notification_id, attempted_at DESC);
