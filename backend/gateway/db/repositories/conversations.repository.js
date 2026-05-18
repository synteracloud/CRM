'use strict';

/**
 * Conversations repository — DB-backed CRUD for messaging_db.
 *
 * Docs: docs/whatsapp-execution-model.md
 *       docs/offline-sync.md
 *       db/messaging_db/schema.sql
 *
 * Schema: messaging_db (no explicit schema prefix — search_path assumed)
 * Tables: contacts, conversations, messages, message_events,
 *         message_idempotency, message_templates, sync_command_queue,
 *         webhook_dead_letter
 *
 * Dedup constraints:
 *   - contacts: UNIQUE (tenant_id, normalized_phone)
 *   - conversations: UNIQUE (tenant_id, channel, normalized_phone, business_context)
 *   - messages: UNIQUE (tenant_id, provider, provider_message_id)
 *   - message_idempotency: PK (tenant_id, provider, event_scope, source_event_id)
 *   - sync_command_queue: UNIQUE (tenant_id, idempotency_key)
 */

const { query, withTransaction } = require('../pool');

const VALID_CONVERSATION_STATES = ['open', 'resolved', 'waiting', 'bot_active'];
const VALID_MESSAGE_DIRECTIONS  = ['inbound', 'outbound'];
const VALID_MESSAGE_STATUSES    = ['queued', 'sent', 'delivered', 'read', 'failed'];
const VALID_SYNC_OPS            = ['create', 'update', 'delete'];
const VALID_SYNC_STATUSES       = ['pending', 'syncing', 'synced', 'failed', 'conflict', 'dead_letter'];

class ConversationsRepository {
  // ── Messaging Contacts ────────────────────────────────────────────────────────
  // (separate from CRM contacts — keyed on normalized_phone for WhatsApp dedup)

  async upsertContact(tenantId, data) {
    const { contact_id, normalized_phone, profile_name, locale, opt_in_whatsapp = true, tags = [] } = data;
    const { rows } = await query(
      `INSERT INTO contacts (contact_id, tenant_id, normalized_phone, profile_name, locale, opt_in_whatsapp, tags)
       VALUES ($1,$2,$3,$4,$5,$6,$7)
       ON CONFLICT (tenant_id, normalized_phone)
       DO UPDATE SET
         profile_name = EXCLUDED.profile_name,
         locale = COALESCE(EXCLUDED.locale, contacts.locale),
         opt_in_whatsapp = EXCLUDED.opt_in_whatsapp,
         updated_at = NOW()
       RETURNING *`,
      [contact_id, tenantId, normalized_phone, profile_name || null, locale || null,
       opt_in_whatsapp, JSON.stringify(tags)],
    );
    return rows[0];
  }

  async findContactByPhone(tenantId, normalizedPhone) {
    const { rows } = await query(
      `SELECT * FROM contacts WHERE tenant_id = $1 AND normalized_phone = $2`,
      [tenantId, normalizedPhone],
    );
    return rows[0] || null;
  }

  async findContactById(tenantId, contactId) {
    const { rows } = await query(
      `SELECT * FROM contacts WHERE tenant_id = $1 AND contact_id = $2`,
      [tenantId, contactId],
    );
    return rows[0] || null;
  }

  // ── Conversations ─────────────────────────────────────────────────────────────

  async upsertConversation(tenantId, data) {
    const {
      conversation_id,
      channel,
      normalized_phone,
      contact_id,
      business_context = 'general',
      state,
      active_entity_type,
      active_entity_id,
    } = data;

    const { rows } = await query(
      `INSERT INTO conversations
         (conversation_id, tenant_id, channel, normalized_phone, contact_id,
          business_context, state, active_entity_type, active_entity_id)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
       ON CONFLICT (tenant_id, channel, normalized_phone, business_context)
       DO UPDATE SET
         state = EXCLUDED.state,
         active_entity_type = EXCLUDED.active_entity_type,
         active_entity_id = EXCLUDED.active_entity_id,
         updated_at = NOW()
       RETURNING *`,
      [
        conversation_id, tenantId, channel, normalized_phone, contact_id,
        business_context, state, active_entity_type || null, active_entity_id || null,
      ],
    );
    return rows[0];
  }

  async findConversationById(tenantId, conversationId) {
    const { rows } = await query(
      `SELECT * FROM conversations WHERE tenant_id = $1 AND conversation_id = $2`,
      [tenantId, conversationId],
    );
    return rows[0] || null;
  }

  async findActiveConversation(tenantId, { channel, normalizedPhone, businessContext = 'general' }) {
    const { rows } = await query(
      `SELECT * FROM conversations
       WHERE tenant_id = $1 AND channel = $2 AND normalized_phone = $3 AND business_context = $4`,
      [tenantId, channel, normalizedPhone, businessContext],
    );
    return rows[0] || null;
  }

  async listConversations(tenantId, { state, contact_id, limit = 25, offset = 0 } = {}) {
    const conditions = ['tenant_id = $1'];
    const params = [tenantId];
    let p = 2;

    if (state)      { conditions.push(`state = $${p++}`);      params.push(state); }
    if (contact_id) { conditions.push(`contact_id = $${p++}`); params.push(contact_id); }

    params.push(limit, offset);
    const { rows } = await query(
      `SELECT * FROM conversations
       WHERE ${conditions.join(' AND ')}
       ORDER BY updated_at DESC
       LIMIT $${p} OFFSET $${p + 1}`,
      params,
    );
    return rows;
  }

  async updateConversationState(tenantId, conversationId, { state, last_inbound_at, last_outbound_at }) {
    const sets = ['state = $3', 'updated_at = NOW()'];
    const params = [tenantId, conversationId, state];
    let p = 4;

    if (last_inbound_at)  { sets.push(`last_inbound_at = $${p++}`);  params.push(last_inbound_at); }
    if (last_outbound_at) { sets.push(`last_outbound_at = $${p++}`); params.push(last_outbound_at); }

    const { rows } = await query(
      `UPDATE conversations SET ${sets.join(', ')}
       WHERE tenant_id = $1 AND conversation_id = $2
       RETURNING *`,
      params,
    );
    return rows[0] || null;
  }

  // ── Messages ──────────────────────────────────────────────────────────────────

  // Insert with dedup — (tenant_id, provider, provider_message_id) is UNIQUE.
  // Returns null if the message already exists (idempotent ingest).
  async insertMessage(tenantId, data) {
    const {
      message_id,
      conversation_id,
      contact_id,
      direction,
      provider,
      provider_message_id,
      body,
      intent,
      status,
      payload_hash,
      occurred_at,
      metadata = {},
    } = data;

    const { rows } = await query(
      `INSERT INTO messages
         (message_id, tenant_id, conversation_id, contact_id, direction,
          provider, provider_message_id, body, intent, status, payload_hash,
          occurred_at, metadata)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
       ON CONFLICT (tenant_id, provider, provider_message_id) DO NOTHING
       RETURNING *`,
      [
        message_id, tenantId, conversation_id, contact_id, direction,
        provider, provider_message_id, body, intent, status, payload_hash,
        occurred_at, JSON.stringify(metadata),
      ],
    );
    return rows[0] || null;  // null = duplicate (suppressed)
  }

  async findMessageById(tenantId, messageId) {
    const { rows } = await query(
      `SELECT * FROM messages WHERE tenant_id = $1 AND message_id = $2`,
      [tenantId, messageId],
    );
    return rows[0] || null;
  }

  async listMessages(tenantId, conversationId, { limit = 50, offset = 0 } = {}) {
    const { rows } = await query(
      `SELECT * FROM messages
       WHERE tenant_id = $1 AND conversation_id = $2
       ORDER BY occurred_at ASC
       LIMIT $3 OFFSET $4`,
      [tenantId, conversationId, limit, offset],
    );
    return rows;
  }

  async updateMessageStatus(tenantId, messageId, { status, error_code }) {
    const { rows } = await query(
      `UPDATE messages
       SET status = $3, error_code = $4
       WHERE tenant_id = $1 AND message_id = $2
       RETURNING *`,
      [tenantId, messageId, status, error_code || null],
    );
    return rows[0] || null;
  }

  // ── Message Events ────────────────────────────────────────────────────────────

  async appendMessageEvent(tenantId, data) {
    const {
      event_id,
      message_id,
      conversation_id,
      contact_id,
      event_type,
      status,
      provider,
      provider_message_id,
      payload_hash,
      error_code,
      details = {},
      occurred_at,
    } = data;

    const { rows } = await query(
      `INSERT INTO message_events
         (event_id, tenant_id, message_id, conversation_id, contact_id,
          event_type, status, provider, provider_message_id, payload_hash,
          error_code, details, occurred_at)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
       RETURNING *`,
      [
        event_id, tenantId, message_id, conversation_id, contact_id,
        event_type, status, provider, provider_message_id, payload_hash,
        error_code || null, JSON.stringify(details), occurred_at,
      ],
    );
    return rows[0];
  }

  // ── Idempotency ───────────────────────────────────────────────────────────────

  // Returns true if already processed (duplicate), false if newly claimed.
  async claimIdempotencyKey(tenantId, { provider, event_scope, source_event_id }) {
    const { rows } = await query(
      `INSERT INTO message_idempotency (tenant_id, provider, event_scope, source_event_id)
       VALUES ($1,$2,$3,$4)
       ON CONFLICT (tenant_id, provider, event_scope, source_event_id) DO NOTHING
       RETURNING processed_at`,
      [tenantId, provider, event_scope, source_event_id],
    );
    return rows.length === 0;  // true = already processed (conflict = duplicate)
  }

  // ── Message Templates ─────────────────────────────────────────────────────────

  async findTemplate(tenantId, { provider, template_key, locale = 'en' }) {
    const { rows } = await query(
      `SELECT * FROM message_templates
       WHERE tenant_id = $1 AND provider = $2 AND template_key = $3 AND locale = $4
         AND status = 'approved'
       ORDER BY version DESC
       LIMIT 1`,
      [tenantId, provider, template_key, locale],
    );
    return rows[0] || null;
  }

  async upsertTemplate(tenantId, data) {
    const {
      template_id,
      provider,
      template_key,
      locale = 'en',
      category = 'utility',
      body,
      params_schema = [],
      status = 'approved',
      version = 1,
    } = data;

    const { rows } = await query(
      `INSERT INTO message_templates
         (template_id, tenant_id, provider, template_key, locale, category, body, params_schema, status, version)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
       ON CONFLICT (tenant_id, provider, template_key, locale, version)
       DO UPDATE SET
         body = EXCLUDED.body,
         params_schema = EXCLUDED.params_schema,
         status = EXCLUDED.status,
         updated_at = NOW()
       RETURNING *`,
      [template_id, tenantId, provider, template_key, locale, category,
       body, JSON.stringify(params_schema), status, version],
    );
    return rows[0];
  }

  // ── Sync Command Queue ────────────────────────────────────────────────────────

  async enqueueSyncCommand(tenantId, data) {
    const {
      command_id,
      device_id,
      idempotency_key,
      entity_type,
      entity_id,
      op,
      payload = {},
      base_version = 0,
      client_timestamp,
    } = data;

    const { rows } = await query(
      `INSERT INTO sync_command_queue
         (command_id, tenant_id, device_id, idempotency_key, entity_type, entity_id,
          op, payload, base_version, client_timestamp)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
       ON CONFLICT (tenant_id, idempotency_key) DO NOTHING
       RETURNING *`,
      [
        command_id, tenantId, device_id, idempotency_key, entity_type, entity_id,
        op, JSON.stringify(payload), base_version, client_timestamp,
      ],
    );
    return rows[0] || null;  // null = duplicate idempotency key (suppressed)
  }

  async listPendingSyncCommands(tenantId, { device_id, limit = 50 } = {}) {
    const conditions = ["tenant_id = $1 AND status = 'pending'"];
    const params = [tenantId];
    let p = 2;

    if (device_id) { conditions.push(`device_id = $${p++}`); params.push(device_id); }
    params.push(limit);

    const { rows } = await query(
      `SELECT * FROM sync_command_queue
       WHERE ${conditions.join(' AND ')}
       ORDER BY client_timestamp ASC
       LIMIT $${p}`,
      params,
    );
    return rows;
  }

  async updateSyncCommandStatus(tenantId, commandId, { status, last_error, synced_at }) {
    const { rows } = await query(
      `UPDATE sync_command_queue
       SET status = $3, last_error = $4, synced_at = $5,
           retry_count = CASE WHEN $3 = 'failed' THEN retry_count + 1 ELSE retry_count END
       WHERE tenant_id = $1 AND command_id = $2
       RETURNING *`,
      [tenantId, commandId, status, last_error || null, synced_at || null],
    );
    return rows[0] || null;
  }
}

module.exports = {
  ConversationsRepository,
  VALID_CONVERSATION_STATES,
  VALID_MESSAGE_DIRECTIONS,
  VALID_MESSAGE_STATUSES,
  VALID_SYNC_OPS,
  VALID_SYNC_STATUSES,
};
