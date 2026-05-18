const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { forwardRequest } = require('../middleware/transport-forward');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['activities.read']), forwardRequest);
router.post('/', requestValidationMiddleware(), requireScopes(['activities.create']), forwardRequest);

module.exports = router;
