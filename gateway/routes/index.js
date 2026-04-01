const express = require('express');
const usersV1Router = require('./v1-users.routes');
const accountsV1Router = require('./v1-accounts.routes');
const contactsV1Router = require('./v1-contacts.routes');
const quotesV1Router = require('./v1-quotes.routes');
const ordersV1Router = require('./v1-orders.routes');
const paymentsV1Router = require('./v1-payments.routes');
const forecastsV1Router = require('./v1-forecasts.routes');
const subscriptionsV1Router = require('./v1-subscriptions.routes');
const invoiceSummariesV1Router = require('./v1-invoice-summaries.routes');
const activitiesV1Router = require('./v1-activities.routes');
const tasksV1Router = require('./v1-tasks.routes');
const priceBooksV1Router = require('./v1-price-books.routes');
const emailsV1Router = require('./v1-emails.routes');
const auditV1Router = require('./v1-audit.routes');
const { respondError } = require('../middleware/response-wrapper');

const router = express.Router();

const API_V1_PREFIX = '/api/v1';

router.use('/users', usersV1Router); // Mounted under /api/v1/users at gateway entrypoint.
router.use('/accounts', accountsV1Router);
router.use('/contacts', contactsV1Router);
router.use('/quotes', quotesV1Router);
router.use('/orders', ordersV1Router);
router.use('/payments', paymentsV1Router);
router.use('/forecasts', forecastsV1Router);
router.use('/subscriptions', subscriptionsV1Router);
router.use('/invoice-summaries', invoiceSummariesV1Router);
router.use('/activities', activitiesV1Router);
router.use('/tasks', tasksV1Router);
router.use('/price-books', priceBooksV1Router);
router.use('/emails', emailsV1Router);
router.use('/audits', auditV1Router);

router.use((req, res) => respondError(res, 'not_found', 'The requested resource was not found.', [], 404));

module.exports = router;
