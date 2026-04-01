const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { forwardRequest } = require('../middleware/transport-forward');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['quotes.read']), forwardRequest);
router.post('/', requestValidationMiddleware(), requireScopes(['quotes.create']), forwardRequest);
router.get('/:quote_id', requestValidationMiddleware(), requireScopes(['quotes.read']), forwardRequest);
router.post('/:quote_id/acceptances', requestValidationMiddleware(), requireScopes(['quotes.accept']), forwardRequest);
router.post('/:quote_id/orders', requestValidationMiddleware(), requireScopes(['orders.create']), forwardRequest);

module.exports = router;
