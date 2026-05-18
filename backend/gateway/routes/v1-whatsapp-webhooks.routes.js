'use strict';

/**
 * WhatsApp provider webhook ingestion routes.
 *
 * Docs: docs/integration-contracts.md — WhatsApp Provider Contracts
 *       docs/whatsapp-execution-model.md
 *       docs/integration-end-to-end-auto-fix.md — Flow 1 (WhatsApp→Lead→Close)
 *
 * Endpoints:
 *   POST /webhooks/whatsapp/meta        — Meta Cloud API (X-Hub-Signature-256 HMAC)
 *   POST /webhooks/whatsapp/twilio      — Twilio (X-Twilio-Signature, form-urlencoded)
 *   POST /webhooks/whatsapp/360dialog   — 360dialog (d360-signature HMAC)
 *   POST /webhooks/whatsapp/gupshup     — Gupshup (no HMAC; source-IP trust expected)
 *   GET  /webhooks/whatsapp/meta        — Meta hub-challenge verification endpoint
 *   GET  /webhooks/whatsapp/log         — Internal event log (debug)
 *
 * Pattern: verify signature → normalise to canonical InboundMessage or StatusUpdate
 *          → dispatch to CONVERSATION_SERVICE_URL/internal/messages (fire-and-forget).
 * Always respond 200 immediately. Signature failures are logged but still 200'd
 * to prevent provider retry storms from revealing rejection behaviour.
 *
 * P-020: BEHAV-001 — every inbound message must be classified and routed.
 * Service call: POST {CONVERSATION_SERVICE_URL}/internal/messages
 */

const crypto = require('crypto');
const http   = require('http');
const https  = require('https');
const express = require('express');

const CONVERSATION_SERVICE_URL = process.env.CONVERSATION_SERVICE_URL || 'http://localhost:5002';

/**
 * Fire-and-forget POST to the conversation service.
 * Never throws — logs errors internally so webhook handlers always return 200.
 */
function dispatchToConversationService(event) {
  const url = `${CONVERSATION_SERVICE_URL}/internal/messages`;
  const payload = Buffer.from(JSON.stringify(event));
  const parsed  = new URL(url);
  const client  = parsed.protocol === 'https:' ? https : http;

  const req = client.request(
    {
      hostname: parsed.hostname,
      port:     parsed.port || (parsed.protocol === 'https:' ? 443 : 80),
      path:     parsed.pathname,
      method:   'POST',
      headers:  { 'Content-Type': 'application/json', 'Content-Length': payload.length },
    },
    (res) => {
      // Drain response to free socket
      res.resume();
    },
  );
  req.on('error', (err) => {
    whatsappWebhookLog.push({
      provider:    event.provider,
      event_type:  'conversation_service_error',
      error:       err.message,
      received_at: nowIso(),
    });
  });
  req.setTimeout(3000, () => req.destroy());
  req.write(payload);
  req.end();
}

const router = express.Router();

// ── In-memory log (replace with queue / DB in production) ────────────────────
const whatsappWebhookLog = [];

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

// ── HMAC helpers ──────────────────────────────────────────────────────────────

function hmacSha256Hex(secret, data) {
  return crypto.createHmac('sha256', secret).update(data).digest('hex');
}

function timingSafeEqualHex(a, b) {
  try {
    const aBuf = Buffer.from(a || '', 'hex');
    const bBuf = Buffer.from(b || '', 'hex');
    if (aBuf.length !== bBuf.length) return false;
    return crypto.timingSafeEqual(aBuf, bBuf);
  } catch {
    return false;
  }
}

// ── Canonical inbound message normaliser ─────────────────────────────────────

function buildInboundMessage(provider, from, to, messageId, text, timestamp, raw) {
  return {
    event_type: 'inbound_message',
    provider,
    from_number: from,
    to_number: to,
    provider_message_id: messageId,
    text: text || '',
    occurred_at: timestamp || nowIso(),
    raw,
    received_at: nowIso(),
  };
}

function buildStatusUpdate(provider, messageId, status, timestamp, raw) {
  return {
    event_type: 'status_update',
    provider,
    provider_message_id: messageId,
    status,         // sent | delivered | read | failed
    occurred_at: timestamp || nowIso(),
    raw,
    received_at: nowIso(),
  };
}

// ── Meta Cloud API ─────────────────────────────────────────────────────────────

// GET /webhooks/whatsapp/meta — hub challenge verification
router.get('/meta', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];
  if (mode === 'subscribe' && token === (process.env.META_VERIFY_TOKEN || '')) {
    return res.status(200).send(challenge);
  }
  return res.status(403).json({ error: 'forbidden' });
});

// POST /webhooks/whatsapp/meta
router.post('/meta', (req, res) => {
  const secret = process.env.META_APP_SECRET || '';
  const rawBody = req.rawBody || JSON.stringify(req.body || {});
  const sig = (req.headers['x-hub-signature-256'] || '').replace(/^sha256=/, '');
  const expected = hmacSha256Hex(secret, rawBody);

  const valid = timingSafeEqualHex(expected, sig);
  if (!valid) {
    whatsappWebhookLog.push({ provider: 'meta', event_type: 'signature_failure', received_at: nowIso() });
    return res.status(200).json({ received: true });
  }

  const body = req.body || {};
  const entries = (body.entry || []);
  for (const entry of entries) {
    for (const change of (entry.changes || [])) {
      const value = change.value || {};
      for (const msg of (value.messages || [])) {
        const event = buildInboundMessage(
          'meta',
          msg.from,
          value.metadata?.display_phone_number,
          msg.id,
          msg.text?.body,
          msg.timestamp ? new Date(Number(msg.timestamp) * 1000).toISOString() : null,
          msg,
        );
        whatsappWebhookLog.push(event);
        dispatchToConversationService(event);
      }
      for (const status of (value.statuses || [])) {
        const event = buildStatusUpdate(
          'meta',
          status.id,
          status.status,
          status.timestamp ? new Date(Number(status.timestamp) * 1000).toISOString() : null,
          status,
        );
        whatsappWebhookLog.push(event);
        // TODO: dispatch to ActivityEngine.record_delivery_status(event)
      }
    }
  }

  return res.status(200).json({ received: true });
});

// ── Twilio ─────────────────────────────────────────────────────────────────────

router.post('/twilio', (req, res) => {
  // Twilio uses URL + sorted params HMAC with auth token.
  // Full validation requires the raw request URL; simplified here to check
  // the X-Twilio-Signature header presence as a guard.
  const sig = req.headers['x-twilio-signature'];
  if (!sig) {
    whatsappWebhookLog.push({ provider: 'twilio', event_type: 'signature_missing', received_at: nowIso() });
    return res.status(200).json({ received: true });
  }

  const body = req.body || {};
  const event = buildInboundMessage(
    'twilio',
    body.From || '',
    body.To || '',
    body.MessageSid || '',
    body.Body || '',
    nowIso(),
    body,
  );
  whatsappWebhookLog.push(event);
  dispatchToConversationService(event);

  return res.status(200).json({ received: true });
});

// ── 360dialog ─────────────────────────────────────────────────────────────────

router.post('/360dialog', (req, res) => {
  const secret = process.env.DIALOG360_WEBHOOK_SECRET || '';
  const rawBody = req.rawBody || JSON.stringify(req.body || {});
  const sig = req.headers['d360-signature'] || '';
  const expected = hmacSha256Hex(secret, rawBody);

  if (secret && !timingSafeEqualHex(expected, sig)) {
    whatsappWebhookLog.push({ provider: '360dialog', event_type: 'signature_failure', received_at: nowIso() });
    return res.status(200).json({ received: true });
  }

  const body = req.body || {};
  for (const msg of (body.messages || [])) {
    const event = buildInboundMessage(
      '360dialog',
      msg.from,
      body.contacts?.[0]?.profile?.name,
      msg.id,
      msg.text?.body,
      msg.timestamp ? new Date(Number(msg.timestamp) * 1000).toISOString() : null,
      msg,
    );
    whatsappWebhookLog.push(event);
    dispatchToConversationService(event);
  }
  for (const status of (body.statuses || [])) {
    const event = buildStatusUpdate('360dialog', status.id, status.status, null, status);
    whatsappWebhookLog.push(event);
  }

  return res.status(200).json({ received: true });
});

// ── Gupshup ───────────────────────────────────────────────────────────────────

router.post('/gupshup', (req, res) => {
  // Gupshup does not send an HMAC signature; trust is via source IP allowlist
  // enforced at the load balancer / WAF layer.
  const body = req.body || {};
  const type = body.type || '';

  if (type === 'message') {
    const payload = body.payload || {};
    const event = buildInboundMessage(
      'gupshup',
      payload.sender?.phone || '',
      payload.destination || '',
      payload.id || '',
      payload.payload?.text || '',
      payload.timestamp ? new Date(Number(payload.timestamp)).toISOString() : null,
      payload,
    );
    whatsappWebhookLog.push(event);
    dispatchToConversationService(event);
  } else if (type === 'message-event' || type === 'message_event') {
    const payload = body.payload || {};
    const event = buildStatusUpdate(
      'gupshup',
      payload.id || '',
      payload.type || 'unknown',
      payload.timestamp ? new Date(Number(payload.timestamp)).toISOString() : null,
      payload,
    );
    whatsappWebhookLog.push(event);
  }

  return res.status(200).json({ received: true });
});

// ── Internal log endpoint (debug / ops) ──────────────────────────────────────

router.get('/log', (req, res) => {
  const provider = req.query.provider;
  const eventType = req.query.event_type;
  let entries = whatsappWebhookLog;
  if (provider)   entries = entries.filter((e) => e.provider === provider);
  if (eventType)  entries = entries.filter((e) => e.event_type === eventType);
  return res.status(200).json({ data: entries, meta: { count: entries.length } });
});

module.exports = router;
