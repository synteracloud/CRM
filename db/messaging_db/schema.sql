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
