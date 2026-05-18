const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['billing.read']), (req, res) => {
  return respondSuccess(
    res,
    [
      {
        subscription_id: 'sub_01JBILLING000000000000001',
        tenant_id: req.auth.tenant_id,
        account_id: 'acc_01JACCOUNT000000000000001',
        quote_id: 'qte_01JQUOTE000000000000001',
        external_subscription_ref: 'stripe_sub_123',
        plan_code: 'growth_monthly',
        status: 'active',
        start_date: '2026-03-01',
        end_date: null,
        renewal_date: '2026-04-01',
        created_at: '2026-03-01T00:00:00Z',
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
    'account_id',
    'quote_id',
    'external_subscription_ref',
    'plan_code',
    'status',
    'start_date',
    'end_date',
    'renewal_date',
  ]),
  requireScopes(['billing.create']),
  (req, res) => {
    const now = '2026-03-26T12:00:00Z';

    return res.status(201).json({
      data: {
        subscription_id: 'sub_01JBILLING000000000000NEW',
        tenant_id: req.auth.tenant_id,
        account_id: req.body.account_id,
        quote_id: req.body.quote_id ?? null,
        external_subscription_ref: req.body.external_subscription_ref,
        plan_code: req.body.plan_code,
        status: req.body.status,
        start_date: req.body.start_date,
        end_date: req.body.end_date ?? null,
        renewal_date: req.body.renewal_date ?? null,
        created_at: now,
      },
      meta: {
        request_id: req.request_id,
      },
    });
  },
);

module.exports = router;
