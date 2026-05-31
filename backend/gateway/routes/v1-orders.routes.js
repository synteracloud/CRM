'use strict';

const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');

const router = express.Router();

const _memOrders = [
  { order_id: 'ord-001', tenant_id: null, quote_id: 'qt-001', account_id: '00000000-0000-0000-0000-000000000020', status: 'confirmed', total_amount: 450000, currency: 'PKR', created_at: '2026-05-20T10:00:00Z' },
  { order_id: 'ord-002', tenant_id: null, quote_id: 'qt-002', account_id: '00000000-0000-0000-0000-000000000021', status: 'fulfilled', total_amount: 250000, currency: 'PKR', created_at: '2026-05-22T09:00:00Z' },
];

router.get('/', requestValidationMiddleware(), requireScopes(['orders.read']), (req, res) => {
  const data = _memOrders.map((o) => ({ ...o, tenant_id: req.auth.tenant_id }));
  return respondSuccess(res, data, { pagination: { page: 1, page_size: 25, total_items: data.length, total_pages: 1 } });
});

router.get('/:order_id', requestValidationMiddleware(), requireScopes(['orders.read']), (req, res) => {
  const order = _memOrders.find((o) => o.order_id === req.params.order_id);
  if (!order) return respondError(res, 'not_found', 'Order not found.', [], 404);
  return respondSuccess(res, { ...order, tenant_id: req.auth.tenant_id });
});

module.exports = router;
