'use strict';

/**
 * Payment provider webhook ingestion routes.
 *
 * Docs: docs/integration-contracts.md — Pakistan Payments Webhooks
 *       docs/collections-engine-model.md — payment event ingest
 *
 * Pattern: verify HMAC signature → normalize via adapter → ingest to collections.
 * Always return 200 immediately. Processing is async (dead-letter on failure).
 *
 * Endpoints:
 *   POST /webhooks/payments/jazzcash   — pp_SecureHash HMAC-SHA256 verification
 *   POST /webhooks/payments/easypaisa  — HMAC signature field verification
 */

const crypto = require('crypto');
const express = require('express');
const { respondError } = require('../middleware/response-wrapper');

const router = express.Router();

// ── In-memory event log (replace with queue/DB in production) ──────────────────
const paymentWebhookLog = [];

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

// ── HMAC helpers ───────────────────────────────────────────────────────────────

function verifyHmacSha256(secret, payload, providedSignature) {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(typeof payload === 'string' ? payload : JSON.stringify(payload))
    .digest('hex');
  try {
    return crypto.timingSafeEqual(
      Buffer.from(expected, 'hex'),
      Buffer.from(providedSignature || '', 'hex'),
    );
  } catch {
    return false;
  }
}

// ── Canonical status normalizer ────────────────────────────────────────────────

function normalizeStatus(raw) {
  const s = String(raw || '').toLowerCase();
  if (['paid', 'success', '000'].includes(s)) return 'succeeded';
  if (['failed', 'failure', '001', 'rejected'].includes(s)) return 'failed';
  return 'pending';
}

// ── JazzCash webhook  POST /webhooks/payments/jazzcash ────────────────────────
router.post('/jazzcash', (req, res) => {
  const secret = process.env.JAZZCASH_HASH_KEY || '';
  const body = req.body || {};
  const providedHash = body.pp_SecureHash || '';

  // Verify HMAC: build sorted key-value string excluding pp_SecureHash itself.
  const sortedKeys = Object.keys(body)
    .filter((k) => k !== 'pp_SecureHash')
    .sort();
  const hashString = sortedKeys.map((k) => body[k]).join('&');
  const isValid = verifyHmacSha256(secret, hashString, providedHash);

  if (!isValid) {
    // Log failure but still return 200 to avoid provider retries for auth failures.
    paymentWebhookLog.push({
      provider: 'jazzcash',
      event_type: 'signature_failure',
      received_at: nowIso(),
      raw: body,
    });
    return res.status(200).json({ received: true });
  }

  const event = {
    provider: 'jazzcash',
    payment_ref: body.pp_TxnRefNo || body.pp_InvoiceRef || '',
    provider_txn_id: body.pp_TxnRefNo || '',
    status: normalizeStatus(body.pp_ResponseCode),
    amount_minor: Math.round(parseFloat(body.pp_Amount || '0') * 100),
    currency: 'PKR',
    occurred_at: body.pp_TxnDateTime
      ? new Date(body.pp_TxnDateTime).toISOString()
      : nowIso(),
    raw: body,
    received_at: nowIso(),
  };

  paymentWebhookLog.push(event);
  // TODO: forward to CollectionsService.ingest_payment(event) via internal queue

  return res.status(200).json({ received: true });
});

// ── Easypaisa webhook  POST /webhooks/payments/easypaisa ──────────────────────
router.post('/easypaisa', (req, res) => {
  const secret = process.env.EASYPAISA_STORE_PASSWORD || '';
  const body = req.body || {};
  const providedSig = body.signature || '';

  // Easypaisa HMAC: concatenate storeId + orderId + transactionId + status
  const sigString = [
    body.storeId,
    body.orderId,
    body.transactionId,
    body.transactionStatus,
  ]
    .filter(Boolean)
    .join('');
  const isValid = verifyHmacSha256(secret, sigString, providedSig);

  if (!isValid) {
    paymentWebhookLog.push({
      provider: 'easypaisa',
      event_type: 'signature_failure',
      received_at: nowIso(),
      raw: body,
    });
    return res.status(200).json({ received: true });
  }

  const event = {
    provider: 'easypaisa',
    payment_ref: body.orderId || '',
    provider_txn_id: body.transactionId || '',
    status: normalizeStatus(body.transactionStatus),
    amount_minor: Math.round(parseFloat(body.transactionAmount || '0') * 100),
    currency: 'PKR',
    occurred_at: body.transactionDateTime
      ? new Date(body.transactionDateTime).toISOString()
      : nowIso(),
    raw: body,
    received_at: nowIso(),
  };

  paymentWebhookLog.push(event);
  // TODO: forward to CollectionsService.ingest_payment(event) via internal queue

  return res.status(200).json({ received: true });
});

// ── Webhook log read (internal use / debugging) ───────────────────────────────
router.get('/log', (req, res) => {
  const provider = req.query.provider;
  const entries = provider
    ? paymentWebhookLog.filter((e) => e.provider === provider)
    : paymentWebhookLog;
  return res.status(200).json({ data: entries, meta: { count: entries.length } });
});

module.exports = router;
