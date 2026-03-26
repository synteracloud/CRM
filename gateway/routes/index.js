const express = require('express');
const usersV1Router = require('./v1-users.routes');
const quotesV1Router = require('./v1-quotes.routes');
const ordersV1Router = require('./v1-orders.routes');
const { respondError } = require('../middleware/response-wrapper');

const router = express.Router();

router.use('/api/v1/users', usersV1Router);
router.use('/api/v1/quotes', quotesV1Router);
router.use('/api/v1/orders', ordersV1Router);

router.use((req, res) => respondError(res, 'not_found', 'The requested resource was not found.', [], 404));

module.exports = router;
