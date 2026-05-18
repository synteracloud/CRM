const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { forwardRequest } = require('../middleware/transport-forward');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['accounts.read']), forwardRequest);
router.post('/', requestValidationMiddleware(), requireScopes(['accounts.create']), forwardRequest);
router.get('/:account_id', requestValidationMiddleware(), requireScopes(['accounts.read']), forwardRequest);
router.patch('/:account_id', requestValidationMiddleware(), requireScopes(['accounts.update']), forwardRequest);
router.delete('/:account_id', requestValidationMiddleware(), requireScopes(['accounts.delete']), forwardRequest);
router.put('/:account_id/contacts/:contact_id', requestValidationMiddleware(), requireScopes(['accounts.contacts.link']), forwardRequest);
router.delete('/:account_id/contacts/:contact_id', requestValidationMiddleware(), requireScopes(['accounts.contacts.unlink']), forwardRequest);

module.exports = router;
