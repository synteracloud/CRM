const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { forwardRequest } = require('../middleware/transport-forward');

const router = express.Router();

router.post('/model', requestValidationMiddleware(), requireScopes(['forecasts.read']), forwardRequest);
router.post('/aggregate', requestValidationMiddleware(), requireScopes(['forecasts.read']), forwardRequest);

module.exports = router;
