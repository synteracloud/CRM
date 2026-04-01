const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { isRfc3339Utc } = require('../validators/common');

const router = express.Router();

const ALLOWED_STATUS_FLOW = Object.freeze({
  initiated: ['authorized', 'failed', 'canceled'],
  authorized: ['captured', 'failed', 'canceled'],
  captured: ['settled', 'partially_refunded', 'refunded', 'chargeback'],
  settled: ['partially_refunded', 'refunded', 'chargeback'],
  partially_refunded: ['refunded', 'chargeback'],
  failed: [],
  canceled: [],
  refunded: [],
  chargeback: [],
});

const payments = [];
const revenueLedger = [];
const paymentTransitionDedupe = new Set();

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

function parseDateBoundary(value, boundaryName) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) {
    return { error: { field: boundaryName, reason: 'must_be_iso_date_yyyy_mm_dd' } };
  }

  const parsed = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime())) {
    return { error: { field: boundaryName, reason: 'must_be_valid_date' } };
  }

  return { value: parsed };
}

function clonePayment(payment) {
  return {
    ...payment,
    status_flow: payment.status_flow.map((entry) => ({ ...entry })),
  };
}

function runPaymentTransaction(work) {
  const paymentDraft = payments.map(clonePayment);
  const revenueDraft = revenueLedger.map((entry) => ({ ...entry }));
  const dedupeDraft = new Set(paymentTransitionDedupe);
  const result = work({ paymentDraft, revenueDraft, dedupeDraft });

  payments.splice(0, payments.length, ...paymentDraft);
  revenueLedger.splice(0, revenueLedger.length, ...revenueDraft);
  paymentTransitionDedupe.clear();
  for (const key of dedupeDraft) paymentTransitionDedupe.add(key);
  return result;
}

router.get('/', requestValidationMiddleware(), requireScopes(['payments.read']), (req, res) => {
  const tenantId = req.auth.tenant_id;
  const filtered = payments.filter((payment) => payment.tenant_id === tenantId);
  return respondSuccess(res, filtered);
});

router.post(
  '/',
  requestValidationMiddleware([
    'subscription_id',
    'invoice_summary_id',
    'external_payment_ref',
    'payment_method_type',
    'amount',
    'currency',
  ]),
  requireScopes(['payments.create']),
  (req, res) => {
    const { subscription_id, invoice_summary_id, external_payment_ref, payment_method_type, amount, currency } = req.body;

    if (!subscription_id && !invoice_summary_id) {
      return respondError(res, 'validation_error', 'One or more fields are invalid.', [{ field: 'subscription_id', reason: 'subscription_or_invoice_required' }], 422);
    }

    if (typeof amount !== 'number' || amount <= 0) {
      return respondError(res, 'validation_error', 'One or more fields are invalid.', [{ field: 'amount', reason: 'must_be_positive_number' }], 422);
    }

    if (!/^[A-Z]{3}$/.test(currency || '')) {
      return respondError(res, 'validation_error', 'One or more fields are invalid.', [{ field: 'currency', reason: 'must_be_iso_4217_uppercase' }], 422);
    }

    const allowedMethods = new Set(['card', 'bank_transfer', 'wallet', 'ach', 'other']);
    if (!allowedMethods.has(payment_method_type)) {
      return respondError(res, 'validation_error', 'One or more fields are invalid.', [{ field: 'payment_method_type', reason: 'invalid_payment_method_type' }], 422);
    }

    const ts = nowIso();
    const payment = {
      payment_id: `pay_${Math.random().toString(36).slice(2, 14)}`,
      tenant_id: req.auth.tenant_id,
      subscription_id: subscription_id || null,
      invoice_summary_id: invoice_summary_id || null,
      external_payment_ref: external_payment_ref || null,
      payment_method_type,
      amount,
      currency,
      status: 'initiated',
      created_at: ts,
      updated_at: ts,
      status_flow: [
        {
          from_status: null,
          to_status: 'initiated',
          changed_at: ts,
          reason: 'payment_created',
        },
      ],
    };

    payments.push(payment);
    return res.status(201).json({ data: payment, meta: { request_id: req.request_id } });
  },
);

router.post(
  '/:payment_id/status',
  requestValidationMiddleware(['status', 'changed_at', 'reason']),
  requireScopes(['payments.update']),
  (req, res) => {
    const payment = payments.find((p) => p.payment_id === req.params.payment_id && p.tenant_id === req.auth.tenant_id);
    if (!payment) {
      return respondError(res, 'not_found', 'Payment was not found.', [{ field: 'payment_id', reason: 'not_found' }], 404);
    }

    const { status, changed_at, reason } = req.body;

    if (!Object.prototype.hasOwnProperty.call(ALLOWED_STATUS_FLOW, status)) {
      return respondError(res, 'validation_error', 'One or more fields are invalid.', [{ field: 'status', reason: 'unknown_status' }], 422);
    }

    if (changed_at && !isRfc3339Utc(changed_at)) {
      return respondError(res, 'validation_error', 'One or more fields are invalid.', [{ field: 'changed_at', reason: 'must_be_rfc3339_utc' }], 422);
    }

    const validNextStates = ALLOWED_STATUS_FLOW[payment.status] || [];
    if (payment.status !== status && !validNextStates.includes(status)) {
      return respondError(
        res,
        'conflict',
        'Invalid payment status transition.',
        [{ field: 'status', reason: `invalid_transition_${payment.status}_to_${status}` }],
        409,
      );
    }

    const changedAt = changed_at || nowIso();
    const transitionKey = `${payment.tenant_id}:${payment.payment_id}:${status}:${changedAt}:${reason || ''}`;
    if (paymentTransitionDedupe.has(transitionKey)) {
      return respondSuccess(res, {
        payment_id: payment.payment_id,
        previous_status: payment.status,
        current_status: payment.status,
        changed_at: changedAt,
        status_flow: payment.status_flow,
      });
    }

    const response = runPaymentTransaction(({ paymentDraft, revenueDraft, dedupeDraft }) => {
      const paymentDraftRow = paymentDraft.find((p) => p.payment_id === payment.payment_id && p.tenant_id === req.auth.tenant_id);
      if (!paymentDraftRow) return null;

      const previousStatus = paymentDraftRow.status;
      paymentDraftRow.status = status;
      paymentDraftRow.updated_at = changedAt;
      paymentDraftRow.status_flow.push({
        from_status: previousStatus,
        to_status: status,
        changed_at: changedAt,
        reason: reason || null,
      });

      if (status === 'settled') {
        revenueDraft.push({
          tenant_id: paymentDraftRow.tenant_id,
          payment_id: paymentDraftRow.payment_id,
          amount_delta: paymentDraftRow.amount,
          currency: paymentDraftRow.currency,
          entry_type: 'recognition',
          recognized_at: changedAt,
        });
      } else if (status === 'partially_refunded' || status === 'refunded' || status === 'chargeback') {
        revenueDraft.push({
          tenant_id: paymentDraftRow.tenant_id,
          payment_id: paymentDraftRow.payment_id,
          amount_delta: -paymentDraftRow.amount,
          currency: paymentDraftRow.currency,
          entry_type: status === 'chargeback' ? 'chargeback_adjustment' : 'refund',
          recognized_at: changedAt,
        });
      }

      dedupeDraft.add(transitionKey);
      return {
        payment_id: paymentDraftRow.payment_id,
        previous_status: previousStatus,
        current_status: status,
        changed_at: changedAt,
        status_flow: paymentDraftRow.status_flow,
      };
    });

    return respondSuccess(res, response);
  },
);

router.get('/revenue/summary', requestValidationMiddleware(), requireScopes(['revenue.read']), (req, res) => {
  const fromDateRaw = req.query.from_date;
  const toDateRaw = req.query.to_date;

  if (!fromDateRaw || !toDateRaw) {
    return respondError(
      res,
      'validation_error',
      'One or more fields are invalid.',
      [
        { field: 'from_date', reason: 'required' },
        { field: 'to_date', reason: 'required' },
      ],
      422,
    );
  }

  const fromBoundary = parseDateBoundary(fromDateRaw, 'from_date');
  if (fromBoundary.error) {
    return respondError(res, 'validation_error', 'One or more fields are invalid.', [fromBoundary.error], 422);
  }

  const toBoundary = parseDateBoundary(toDateRaw, 'to_date');
  if (toBoundary.error) {
    return respondError(res, 'validation_error', 'One or more fields are invalid.', [toBoundary.error], 422);
  }

  const from = fromBoundary.value;
  const toExclusive = toBoundary.value;
  toExclusive.setUTCDate(toExclusive.getUTCDate() + 1);

  if (from >= toExclusive) {
    return respondError(res, 'validation_error', 'One or more fields are invalid.', [{ field: 'to_date', reason: 'must_be_on_or_after_from_date' }], 422);
  }

  const byCurrency = new Map();
  for (const entry of revenueLedger) {
    if (entry.tenant_id !== req.auth.tenant_id) continue;
    const recognizedAt = new Date(entry.recognized_at);
    if (recognizedAt < from || recognizedAt >= toExclusive) continue;

    byCurrency.set(entry.currency, (byCurrency.get(entry.currency) || 0) + entry.amount_delta);
  }

  const totals = [...byCurrency.entries()].map(([currencyCode, recognizedRevenue]) => ({
    currency: currencyCode,
    recognized_revenue: Number(recognizedRevenue.toFixed(2)),
  }));

  return respondSuccess(res, {
    from_date: fromDateRaw,
    to_date: toDateRaw,
    totals,
  });
});

module.exports = router;
