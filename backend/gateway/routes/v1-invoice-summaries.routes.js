const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['invoices.read']), (req, res) => {
  return respondSuccess(
    res,
    [
      {
        invoice_summary_id: 'inv_01JINVOICE000000000000001',
        tenant_id: req.auth.tenant_id,
        subscription_id: 'sub_01JBILLING000000000000001',
        external_invoice_ref: 'stripe_in_456',
        invoice_number: 'INV-2026-0001',
        amount_due: '499.00',
        amount_paid: '0.00',
        currency: 'USD',
        status: 'open',
        due_date: '2026-04-10',
        issued_at: '2026-03-26T12:00:00Z',
      },
    ],
    {
      pagination: {
        page: Number(req.query.page || 1),
        page_size: Number(req.query.page_size || 25),
        total_items: 1,
        total_pages: 1,
      },
    },
  );
});

router.post(
  '/',
  requestValidationMiddleware([
    'subscription_id',
    'external_invoice_ref',
    'invoice_number',
    'amount_due',
    'amount_paid',
    'currency',
    'status',
    'due_date',
    'issued_at',
  ]),
  requireScopes(['invoices.create']),
  (req, res) => {
    return res.status(201).json({
      data: {
        invoice_summary_id: 'inv_01JINVOICE000000000000NEW',
        tenant_id: req.auth.tenant_id,
        subscription_id: req.body.subscription_id,
        external_invoice_ref: req.body.external_invoice_ref,
        invoice_number: req.body.invoice_number,
        amount_due: req.body.amount_due,
        amount_paid: req.body.amount_paid,
        currency: req.body.currency,
        status: req.body.status,
        due_date: req.body.due_date,
        issued_at: req.body.issued_at,
      },
      meta: {
        request_id: req.request_id,
      },
    });
  },
);

// ── GET /invoice-summaries/:invoice_id ───────────────────────────────────────
// C-08 Invoice Detail: lookup a single invoice summary by invoice_number or id.
router.get('/:invoice_id', requestValidationMiddleware(), requireScopes(['invoices.read']), (req, res) => {
  const id = req.params.invoice_id;
  const SEED = {
    invoice_summary_id: 'inv_01JINVOICE000000000000001',
    tenant_id: req.auth.tenant_id,
    invoice_number: id.startsWith('INV') ? id : 'INV-2026-0001',
    account_id: 'acc_01JACCOUNT000000000000001',
    account_name: 'City Pharma Ltd',
    subscription_id: 'sub_01JBILLING000000000000001',
    amount_due: '499.00',
    amount_paid: '0.00',
    currency: 'PKR',
    status: 'open',
    due_date: '2026-04-10',
    issued_at: '2026-03-26T12:00:00Z',
    line_items: [
      { description: 'CRM Growth Plan — Monthly', qty: 1, unit_price: '499.00', discount: 0, total: '499.00' }
    ],
    payment_history: [],
  };
  return respondSuccess(res, SEED);
});

module.exports = router;
