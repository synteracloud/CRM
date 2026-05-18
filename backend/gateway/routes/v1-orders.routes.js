const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { forwardRequest } = require('../middleware/transport-forward');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['orders.read']), forwardRequest);
router.get('/:order_id', requestValidationMiddleware(), requireScopes(['orders.read']), forwardRequest);

module.exports = router;
