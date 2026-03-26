const express = require('express');
const usersV1Router = require('./v1-users.routes');
const priceBooksV1Router = require('./v1-price-books.routes');
const subscriptionsV1Router = require('./v1-subscriptions.routes');
const invoiceSummariesV1Router = require('./v1-invoice-summaries.routes');
const { respondError } = require('../middleware/response-wrapper');

const router = express.Router();

router.use('/api/v1/users', usersV1Router);
router.use('/api/v1/price-books', priceBooksV1Router);
router.use('/api/v1/subscriptions', subscriptionsV1Router);
router.use('/api/v1/invoice-summaries', invoiceSummariesV1Router);

router.use((req, res) => respondError(res, 'not_found', 'The requested resource was not found.', [], 404));

module.exports = router;
