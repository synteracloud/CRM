const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { listOrders, getOrderById } = require('../data/cpq-store');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['orders.read']), (req, res) => {
  return respondSuccess(res, listOrders(req.auth.tenant_id));
});

router.get('/:order_id', requestValidationMiddleware(), requireScopes(['orders.read']), (req, res) => {
  const order = getOrderById(req.auth.tenant_id, req.params.order_id);

  if (!order) {
    return respondError(res, 'not_found', 'Order not found.', [{ field: 'order_id', reason: 'not_found' }], 404);
  }

  return respondSuccess(res, order);
});

module.exports = router;
