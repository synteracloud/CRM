-- WhatsApp core execution schema: conversations, messages, and timeline events.

CREATE TABLE IF NOT EXISTS contacts (
  contact_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  normalized_phone TEXT NOT NULL,
  profile_name TEXT,
  locale TEXT,
  opt_in_whatsapp BOOLEAN NOT NULL DEFAULT TRUE,
  tags JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, normalized_phone)
);

CREATE TABLE IF NOT EXISTS conversations (
  conversation_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  channel TEXT NOT NULL,
  normalized_phone TEXT NOT NULL,
  contact_id TEXT NOT NULL REFERENCES contacts(contact_id),
  business_context TEXT NOT NULL DEFAULT 'general',
  state TEXT NOT NULL,
  active_entity_type TEXT,
  active_entity_id TEXT,
  last_inbound_at TIMESTAMPTZ,
  last_outbound_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, channel, normalized_phone, business_context)
);

CREATE TABLE IF NOT EXISTS messages (
  message_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  conversation_id TEXT NOT NULL REFERENCES conversations(conversation_id),
  contact_id TEXT NOT NULL REFERENCES contacts(contact_id),
  direction TEXT NOT NULL,
  provider TEXT NOT NULL,
  provider_message_id TEXT NOT NULL,
  body TEXT NOT NULL,
  intent TEXT NOT NULL,
  status TEXT NOT NULL,
  payload_hash TEXT NOT NULL,
  retry_count INTEGER NOT NULL DEFAULT 0,
  error_code TEXT,
  occurred_at TIMESTAMPTZ NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, provider, provider_message_id)
);

CREATE TABLE IF NOT EXISTS message_events (
  event_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  message_id TEXT NOT NULL REFERENCES messages(message_id),
  conversation_id TEXT NOT NULL REFERENCES conversations(conversation_id),
  contact_id TEXT NOT NULL REFERENCES contacts(contact_id),
  event_type TEXT NOT NULL,
  status TEXT NOT NULL,
  provider TEXT NOT NULL,
  provider_message_id TEXT NOT NULL,
  payload_hash TEXT NOT NULL,
  error_code TEXT,
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  occurred_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS message_idempotency (
  tenant_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  event_scope TEXT NOT NULL,
  source_event_id TEXT NOT NULL,
  processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (tenant_id, provider, event_scope, source_event_id)
);

CREATE INDEX IF NOT EXISTS idx_conversations_contact ON conversations (tenant_id, contact_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_occurred ON messages (conversation_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_message_events_conversation_occurred ON message_events (conversation_id, occurred_at DESC);

-- ── Message templates (versioned, provider-specific) ──────────────────────────
-- Source: docs/whatsapp-execution-model.md §2.2 (template-based outbound policy)
CREATE TABLE IF NOT EXISTS message_templates (
  template_id    TEXT PRIMARY KEY,
  tenant_id      TEXT NOT NULL,
  provider       TEXT NOT NULL,              -- meta | twilio | 360dialog | gupshup
  template_key   TEXT NOT NULL,
  locale         TEXT NOT NULL DEFAULT 'en',
  category       TEXT NOT NULL DEFAULT 'utility',  -- utility | marketing | authentication
  body           TEXT NOT NULL,
  params_schema  JSONB NOT NULL DEFAULT '[]',       -- ordered parameter definitions
  status         TEXT NOT NULL DEFAULT 'approved',
  version        INTEGER NOT NULL DEFAULT 1,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, provider, template_key, locale, version)
);
CREATE INDEX IF NOT EXISTS idx_message_templates_tenant_provider ON message_templates (tenant_id, provider);

-- ── Sync command queue (offline-first action persistence) ─────────────────────
-- Source: docs/offline-sync.md §4 (CommandRecord schema)
CREATE TABLE IF NOT EXISTS sync_command_queue (
  command_id        TEXT PRIMARY KEY,
  tenant_id         TEXT NOT NULL,
  device_id         TEXT NOT NULL,
  idempotency_key   TEXT NOT NULL,           -- (tenant_id + device_id + local_seq_no)
  entity_type       TEXT NOT NULL,
  entity_id         TEXT NOT NULL,
  op                TEXT NOT NULL,           -- create | update | delete
  payload           JSONB NOT NULL DEFAULT '{}',
  base_version      INTEGER NOT NULL DEFAULT 0,
  client_timestamp  TIMESTAMPTZ NOT NULL,
  status            TEXT NOT NULL DEFAULT 'pending',
  retry_count       INTEGER NOT NULL DEFAULT 0,
  last_error        TEXT,
  synced_at         TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, idempotency_key),
  CONSTRAINT sync_cmd_op_chk     CHECK (op     IN ('create','update','delete')),
  CONSTRAINT sync_cmd_status_chk CHECK (status IN ('pending','syncing','synced','failed','conflict','dead_letter'))
);
CREATE INDEX IF NOT EXISTS idx_sync_cmd_tenant_status ON sync_command_queue (tenant_id, status, client_timestamp);
CREATE INDEX IF NOT EXISTS idx_sync_cmd_entity        ON sync_command_queue (tenant_id, entity_type, entity_id);

-- ── Webhook dead-letter (failed webhook processing audit) ─────────────────────
-- Source: docs/integration-contracts.md (failure handling — dead-letter after N failures)
CREATE TABLE IF NOT EXISTS webhook_dead_letter (
  dead_letter_id   TEXT PRIMARY KEY,
  tenant_id        TEXT,
  provider         TEXT NOT NULL,
  endpoint         TEXT NOT NULL,            -- e.g. /webhooks/whatsapp/meta
  payload          JSONB NOT NULL DEFAULT '{}',
  headers          JSONB NOT NULL DEFAULT '{}',
  failure_reason   TEXT NOT NULL,
  attempt_count    INTEGER NOT NULL DEFAULT 1,
  first_failed_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_failed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at      TIMESTAMPTZ,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_wdl_provider_unresolved ON webhook_dead_letter (provider, last_failed_at DESC) WHERE resolved_at IS NULL;
