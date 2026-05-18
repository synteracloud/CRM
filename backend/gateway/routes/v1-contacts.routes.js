const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { forwardRequest } = require('../middleware/transport-forward');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['contacts.read']), forwardRequest);
router.post('/', requestValidationMiddleware(), requireScopes(['contacts.create']), forwardRequest);
router.get('/:contact_id', requestValidationMiddleware(), requireScopes(['contacts.read']), forwardRequest);
router.patch('/:contact_id', requestValidationMiddleware(), requireScopes(['contacts.update']), forwardRequest);
router.delete('/:contact_id', requestValidationMiddleware(), requireScopes(['contacts.delete']), forwardRequest);

module.exports = router;
