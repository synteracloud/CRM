const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['pricing.read']), (req, res) => {
  return respondSuccess(
    res,
    [
      {
        price_book_id: 'pbk_01JPRICING000000000000001',
        tenant_id: req.auth.tenant_id,
        name: 'Standard USD',
        currency: 'USD',
        is_default: true,
        active_from: '2026-01-01T00:00:00Z',
        active_to: null,
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
  requestValidationMiddleware(['name', 'currency', 'is_default', 'active_from', 'active_to']),
  requireScopes(['pricing.create']),
  (req, res) => {
    const now = '2026-03-26T12:00:00Z';

    return res.status(201).json({
      data: {
        price_book_id: 'pbk_01JPRICING000000000000NEW',
        tenant_id: req.auth.tenant_id,
        name: req.body.name,
        currency: req.body.currency,
        is_default: req.body.is_default,
        active_from: req.body.active_from,
        active_to: req.body.active_to ?? null,
        created_at: now,
      },
      meta: {
        request_id: req.request_id,
      },
    });
  },
);

module.exports = router;
