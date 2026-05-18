const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { forwardRequest } = require('../middleware/transport-forward');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['emails.read']), forwardRequest);
router.post('/', requestValidationMiddleware(), requireScopes(['emails.send']), forwardRequest);
router.post('/:email_id/events', requestValidationMiddleware(), requireScopes(['emails.track']), forwardRequest);
router.get('/engagements', requestValidationMiddleware(), requireScopes(['emails.read']), forwardRequest);
router.get('/engagement-logs', requestValidationMiddleware(), requireScopes(['emails.read']), forwardRequest);

module.exports = router;
