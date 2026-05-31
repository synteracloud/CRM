'use strict';

/**
 * Collections engine routes: subscriptions, invoices, payment ingestion, reconciliation.
 *
 * Docs: docs/collections-engine-model.md
 *       docs/integration-end-to-end-auto-fix.md — Flow 2
 *       docs/payments-revenue.md
 *
 * Flow: Subscription active → Invoice created → reminders scheduled →
 *       payment ingested → reconciliation run → invoice marked paid.
 *
 * DB layer: CollectionsRepository (gateway/db/repositories/collections.repository.js)
 * Fallback: in-memory arrays when DB_DISABLED=true or pg not installed.
 *
 * Note: DB invoice_summary requires subscription_id. Requests without
 *       subscription_id fall back to in-memory for invoice creation.
 */

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const router = express.Router();

// ── Repository bootstrap ───────────────────────────────────────────────────────
let repo = null;
let VALID_INVOICE_STATUSES, VALID_PAYMENT_STATUSES;

try {
  if (process.env.DB_DISABLED !== 'true') {
    const mod = require('../db/repositories/collections.repository');
    repo = new mod.CollectionsRepository();
    ({ VALID_INVOICE_STATUSES, VALID_PAYMENT_STATUSES } = mod);
  }
} catch (_e) {
  // pg not installed or DB unavailable — use in-memory fallback below.
}

if (!repo) {
  VALID_INVOICE_STATUSES = ['draft', 'open', 'paid', 'void', 'uncollectible'];
  VALID_PAYMENT_STATUSES = ['initiated', 'authorized', 'captured', 'settled', 'failed', 'canceled', 'partially_refunded', 'refunded', 'chargeback'];
}

// In-memory fallback stores (used only when repo === null)
const _memInvoices = [];
const _memPayments = [];

function nowIso() { return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'); }

// ── GET /collections/invoices ─────────────────────────────────────────────────
router.get('/invoices', requestValidationMiddleware(), requireScopes([SCOPES.COLLECTIONS_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { subscription_id, status } = req.query;
  const limit  = Math.min(parseInt(req.query.limit  || '25', 10), 200);
  const offset = parseInt(req.query.offset || '0', 10);

  if (repo) {
    try {
      const rows = await repo.listInvoices(tenantId, { subscription_id, status, limit, offset });
      return respondSuccess(res, rows, { count: rows.length, limit, offset });
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  const todayStr = new Date().toISOString().slice(0, 10);
  let rows = _memInvoices.filter((i) => i.tenant_id === tenantId);
  if (status)          rows = rows.filter((i) => i.status          === status);
  if (subscription_id) rows = rows.filter((i) => i.subscription_id === subscription_id);
  const page = rows.slice(offset, offset + limit).map((i) => ({
    ...i,
    is_overdue: !['paid', 'void', 'uncollectible'].includes(i.status) && i.due_date < todayStr,
  }));
  return respondSuccess(res, page, { count: page.length, total: rows.length, limit, offset });
});

// ── POST /collections/invoices ────────────────────────────────────────────────
// subscription_id required for DB path (invoice_summary FK constraint).
router.post(
  '/invoices',
  requestValidationMiddleware(['amount_due', 'currency', 'due_date', 'invoice_number']),
  requireScopes([SCOPES.COLLECTIONS_INVOICE]),
  async (req, res) => {
    const { subscription_id, invoice_number, amount_due, currency, due_date, issued_at, external_invoice_ref, account_name, account_tier } = req.body;
    const tenantId = req.auth.tenant_id;

    if (typeof amount_due !== 'number' || amount_due <= 0)
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid field.', [{ field: 'amount_due', reason: 'must_be_positive' }]);
    if (!/^[A-Z]{3}$/.test(currency || ''))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid field.', [{ field: 'currency', reason: 'must_be_iso4217' }]);
    if (isNaN(Date.parse(due_date)))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid field.', [{ field: 'due_date', reason: 'must_be_iso8601' }]);

    if (repo && subscription_id) {
      try {
        const invoice = await repo.createInvoice(tenantId, {
          invoice_summary_id:   randomUUID(),
          subscription_id,
          external_invoice_ref: external_invoice_ref || null,
          invoice_number,
          amount_due,
          currency,
          status:               'open',
          due_date,
          issued_at:            issued_at || nowIso(),
        });
        return res.status(201).json({ data: invoice, meta: { request_id: req.request_id } });
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    // In-memory fallback (no subscription_id required)
    const ts = nowIso();
    const invoice = {
      invoice_id:           `inv_${Math.random().toString(36).slice(2, 14)}`,
      tenant_id:            tenantId,
      subscription_id:      subscription_id || null,
      invoice_number,
      account_name:         account_name     || null,
      account_tier:         account_tier     || null,
      amount_due,
      amount_paid:          0,
      currency,
      due_date,
      status:               'open',
      is_overdue:           false,
      issued_at:            issued_at || ts,
      last_reminder_at:     null,
      created_at:           ts,
      updated_at:           ts,
    };
    _memInvoices.push(invoice);
    return res.status(201).json({ data: invoice, meta: { request_id: req.request_id } });
  },
);

// ── GET /collections/invoices/:invoice_id ─────────────────────────────────────
router.get('/invoices/:invoice_id', requestValidationMiddleware(), requireScopes([SCOPES.COLLECTIONS_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { invoice_id } = req.params;

  if (repo) {
    try {
      const invoice = await repo.findInvoiceById(tenantId, invoice_id);
      if (!invoice) return respondError(res, 404, 'NOT_FOUND', 'Invoice not found.');
      return respondSuccess(res, invoice);
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  const inv = _memInvoices.find((i) => i.invoice_summary_id === invoice_id && i.tenant_id === tenantId);
  if (!inv) return respondError(res, 404, 'NOT_FOUND', 'Invoice not found.');
  return respondSuccess(res, inv);
});

// ── POST /collections/invoices/:invoice_id/payments — ingest payment ──────────
router.post(
  '/invoices/:invoice_id/payments',
  requestValidationMiddleware(['amount', 'currency', 'payment_method_type']),
  requireScopes([SCOPES.COLLECTIONS_INVOICE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { invoice_id } = req.params;
    const { amount, currency, payment_method_type, external_payment_ref, occurred_at } = req.body;

    if (typeof amount !== 'number' || amount <= 0)
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid field.', [{ field: 'amount', reason: 'must_be_positive' }]);

    if (repo) {
      try {
        const invoice = await repo.findInvoiceById(tenantId, invoice_id);
        if (!invoice) return respondError(res, 404, 'NOT_FOUND', 'Invoice not found.');
        if (invoice.status === 'paid' || invoice.status === 'void')
          return respondError(res, 409, 'CONFLICT', `Invoice is already ${invoice.status}.`);
        if (currency !== invoice.currency)
          return respondError(res, 422, 'VALIDATION_ERROR', 'Currency mismatch.', [{ field: 'currency', reason: 'must_match_invoice' }]);

        // Create payment event record (simpler than full payment FSM for ingestion)
        const event = await repo.createPaymentEvent(tenantId, {
          payment_event_id:    randomUUID(),
          invoice_summary_id:  invoice_id,
          external_payment_ref: external_payment_ref || null,
          event_type:          'settled',
          amount,
          currency,
          event_time:          occurred_at || nowIso(),
          status:              'succeeded',
        });

        const newAmountPaid = Number(invoice.amount_paid) + amount;
        const newStatus     = newAmountPaid >= Number(invoice.amount_due) ? 'paid' : 'open';
        const updated = await repo.updateInvoiceStatus(tenantId, invoice_id, {
          status:      newStatus,
          amount_paid: newAmountPaid,
        });

        return res.status(201).json({ data: { payment_event: event, invoice: updated }, meta: { request_id: req.request_id } });
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    const inv = _memInvoices.find((i) => i.invoice_summary_id === invoice_id && i.tenant_id === tenantId);
    if (!inv) return respondError(res, 404, 'NOT_FOUND', 'Invoice not found.');
    if (inv.status === 'paid' || inv.status === 'void')
      return respondError(res, 409, 'CONFLICT', `Invoice is already ${inv.status}.`);
    if (currency !== inv.currency)
      return respondError(res, 422, 'VALIDATION_ERROR', 'Currency mismatch.', [{ field: 'currency', reason: 'must_match_invoice' }]);

    const ts = nowIso();
    const payment = {
      payment_event_id: `pmt_${Math.random().toString(36).slice(2, 14)}`,
      tenant_id:        tenantId,
      invoice_id,
      amount,
      currency,
      payment_method_type,
      status:           'succeeded',
      occurred_at:      occurred_at || ts,
      created_at:       ts,
    };
    _memPayments.push(payment);

    inv.amount_paid = (inv.amount_paid || 0) + amount;
    inv.updated_at  = ts;
    inv.status      = inv.amount_paid >= inv.amount_due ? 'paid' : 'open';

    return res.status(201).json({ data: { payment, invoice: inv }, meta: { request_id: req.request_id } });
  },
);

// ── GET /collections/subscriptions ────────────────────────────────────────────
router.get('/subscriptions', requestValidationMiddleware(), requireScopes([SCOPES.COLLECTIONS_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { account_id, status } = req.query;
  const limit  = Math.min(parseInt(req.query.limit  || '25', 10), 200);
  const offset = parseInt(req.query.offset || '0', 10);

  if (repo) {
    try {
      const rows = await repo.listSubscriptions(tenantId, { account_id, status, limit, offset });
      return respondSuccess(res, rows, { count: rows.length, limit, offset });
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  return respondSuccess(res, [], { count: 0 });
});

// ── POST /collections/subscriptions ───────────────────────────────────────────
router.post(
  '/subscriptions',
  requestValidationMiddleware(['account_id', 'plan_code', 'start_date']),
  requireScopes([SCOPES.COLLECTIONS_INVOICE]),
  async (req, res) => {
    const { account_id, plan_code, start_date, end_date, renewal_date, external_subscription_ref, quote_id } = req.body;
    const tenantId = req.auth.tenant_id;

    if (repo) {
      try {
        const sub = await repo.createSubscription(tenantId, {
          subscription_id:          randomUUID(),
          account_id,
          plan_code,
          start_date,
          end_date:                 end_date                || null,
          renewal_date:             renewal_date            || null,
          external_subscription_ref: external_subscription_ref || null,
          quote_id:                 quote_id                || null,
          status:                   'active',
        });
        return res.status(201).json({ data: sub, meta: { request_id: req.request_id } });
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    return respondError(res, 503, 'SERVICE_UNAVAILABLE', 'Subscriptions require DB connection.');
  },
);

// ── GET /collections/overdue ──────────────────────────────────────────────────
router.get('/overdue', requestValidationMiddleware(), requireScopes([SCOPES.COLLECTIONS_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const now = new Date().toISOString().split('T')[0];  // YYYY-MM-DD

  if (repo) {
    try {
      // List open invoices whose due_date < today
      const rows = await repo.listInvoices(tenantId, { status: 'open', limit: 200, offset: 0 });
      const overdue = rows.filter((i) => i.due_date < now);
      return respondSuccess(res, overdue, { count: overdue.length });
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  const nowDate = new Date();
  const overdue = _memInvoices.filter(
    (i) => i.tenant_id === tenantId && i.status !== 'paid' && i.status !== 'void' && new Date(i.due_date) < nowDate,
  );
  return respondSuccess(res, overdue, { count: overdue.length });
});

// ── POST /collections/reconcile ───────────────────────────────────────────────
router.post(
  '/reconcile',
  requestValidationMiddleware(),
  requireScopes([SCOPES.COLLECTIONS_RECONCILE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;

    if (repo) {
      // DB-backed reconciliation: list open invoices and check amount_paid vs amount_due
      try {
        const invoices = await repo.listInvoices(tenantId, { limit: 500, offset: 0 });
        let matched = 0;
        let unmatched = 0;
        for (const inv of invoices) {
          if (Math.abs(Number(inv.amount_paid) - Number(inv.amount_due)) < 0.001) matched++;
          else unmatched++;
        }
        return respondSuccess(res, {
          invoices_checked: invoices.length,
          matched,
          unmatched,
          reconciled_at: nowIso(),
        });
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    const tenantInvoices = _memInvoices.filter((i) => i.tenant_id === tenantId);
    const tenantPayments = _memPayments.filter((p) => p.tenant_id === tenantId);
    let matched = 0;
    let unmatched = 0;
    for (const inv of tenantInvoices) {
      const invPayments = tenantPayments.filter((p) => p.invoice_id === inv.invoice_id);
      const totalPaid   = invPayments.reduce((sum, p) => sum + p.amount, 0);
      if (Math.abs(totalPaid - inv.amount_paid) < 0.001) matched++;
      else unmatched++;
    }
    return respondSuccess(res, { invoices_checked: tenantInvoices.length, matched, unmatched, reconciled_at: nowIso() });
  },
);

// ── POST /collections/invoices/:invoice_id/payments/:payment_id/proof ─────────
// Docs: BEHAV-003, docs/collections-engine-model.md §6.4.0
// Upload payment proof (proof_url + optional note) for cash/manual payments.
// Caller uploads the file externally (e.g. to cloud storage) and provides the URL.
// Sets verification_status to 'pending_verification' until verified/rejected via PATCH below.
router.post(
  '/invoices/:invoice_id/payments/:payment_id/proof',
  requestValidationMiddleware(['proof_url']),
  requireScopes([SCOPES.COLLECTIONS_INVOICE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { invoice_id, payment_id } = req.params;
    const { proof_url, proof_note, entered_by } = req.body;

    if (!proof_url || typeof proof_url !== 'string' || !proof_url.startsWith('http'))
      return respondError(res, 422, 'VALIDATION_ERROR', 'proof_url must be a valid URL.');

    if (repo) {
      // DB: payment table does not yet have proof columns — return 501 pending schema migration.
      // TODO (post-P-025): add proof_url, proof_note, verification_status, entered_by columns
      //   to transaction_db.payment and implement DB-backed proof storage here.
      return respondError(res, 501, 'NOT_IMPLEMENTED', 'Proof upload requires DB schema migration (see P-025). Use in-memory mode for now.');
    }

    const payment = _memPayments.find(
      (p) => p.payment_event_id === payment_id && p.tenant_id === tenantId,
    );
    if (!payment) return respondError(res, 404, 'NOT_FOUND', 'Payment not found.');

    payment.proof_url           = proof_url;
    payment.proof_note          = proof_note || null;
    payment.entered_by          = entered_by || req.auth.user_id || null;
    payment.verification_status = 'pending_verification';
    payment.updated_at          = nowIso();

    return res.status(201).json({ data: payment, meta: { request_id: req.request_id } });
  },
);

// ── PATCH /collections/invoices/:invoice_id/payments/:payment_id/proof/verify ─
// Docs: BEHAV-003, docs/collections-engine-model.md §6.4.0
// Approve or reject a payment proof.  Sets verification_status to verified|rejected.
// verification_status ∈ { verified, rejected }; rejected requires a rejection_reason.
router.patch(
  '/invoices/:invoice_id/payments/:payment_id/proof/verify',
  requestValidationMiddleware(['verification_status']),
  requireScopes([SCOPES.COLLECTIONS_RECONCILE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { invoice_id, payment_id } = req.params;
    const { verification_status, rejection_reason } = req.body;

    const VALID_VERIFY_STATUSES = ['verified', 'rejected'];
    if (!VALID_VERIFY_STATUSES.includes(verification_status))
      return respondError(res, 422, 'VALIDATION_ERROR', `verification_status must be one of: ${VALID_VERIFY_STATUSES.join(', ')}.`);
    if (verification_status === 'rejected' && !rejection_reason)
      return respondError(res, 422, 'VALIDATION_ERROR', 'rejection_reason is required when rejecting proof.');

    if (repo) {
      // DB: proof verification columns not yet in schema — same TODO as proof upload above.
      return respondError(res, 501, 'NOT_IMPLEMENTED', 'Proof verification requires DB schema migration (see P-025).');
    }

    const payment = _memPayments.find(
      (p) => p.payment_event_id === payment_id && p.tenant_id === tenantId,
    );
    if (!payment) return respondError(res, 404, 'NOT_FOUND', 'Payment not found.');
    if (!payment.proof_url)
      return respondError(res, 409, 'CONFLICT', 'No proof uploaded for this payment yet.');

    payment.verification_status = verification_status;
    payment.verified_by         = req.auth.user_id || null;
    payment.verified_at         = nowIso();
    if (verification_status === 'rejected') {
      payment.rejection_reason  = rejection_reason;
    }
    payment.updated_at = nowIso();

    return respondSuccess(res, payment);
  },
);

// ── POST /collections/invoices/:invoice_id/reminders ──────────────────────────
router.post(
  '/invoices/:invoice_id/reminders',
  requestValidationMiddleware(),
  requireScopes([SCOPES.COLLECTIONS_INVOICE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { invoice_id } = req.params;
    const { channel, message, scheduled_for } = req.body;

    if (repo) {
      try {
        const invoice = await repo.findInvoiceById(tenantId, invoice_id);
        if (!invoice) return respondError(res, 404, 'NOT_FOUND', 'Invoice not found.');
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    } else {
      const inv = _memInvoices.find((i) => i.invoice_id === invoice_id && i.tenant_id === tenantId);
      if (!inv) return respondError(res, 404, 'NOT_FOUND', 'Invoice not found.');
      inv.last_reminder_at = nowIso();
    }

    const reminder = {
      reminder_id:   `rem_${Math.random().toString(36).slice(2, 14)}`,
      invoice_id,
      tenant_id:     tenantId,
      channel:       channel       || 'whatsapp',
      message:       message       || null,
      scheduled_for: scheduled_for || nowIso(),
      status:        'scheduled',
      created_at:    nowIso(),
    };
    return res.status(201).json({ data: reminder, meta: { request_id: req.request_id } });
  },
);

module.exports = router;
