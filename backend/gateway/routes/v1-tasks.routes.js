const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { forwardRequest } = require('../middleware/transport-forward');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['tasks.read']), forwardRequest);
router.post('/', requestValidationMiddleware(), requireScopes(['tasks.create']), forwardRequest);
router.post('/:task_id/reschedule', requestValidationMiddleware(), requireScopes(['tasks.update']), forwardRequest);

module.exports = router;
