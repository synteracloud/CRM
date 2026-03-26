const express = require('express');
const usersV1Router = require('./v1-users.routes');
const accountsV1Router = require('./v1-accounts.routes');
const contactsV1Router = require('./v1-contacts.routes');
const { respondError } = require('../middleware/response-wrapper');

const router = express.Router();

router.use('/api/v1/users', usersV1Router);
router.use('/api/v1/accounts', accountsV1Router);
router.use('/api/v1/contacts', contactsV1Router);

router.use((req, res) => respondError(res, 'not_found', 'The requested resource was not found.', [], 404));

module.exports = router;
