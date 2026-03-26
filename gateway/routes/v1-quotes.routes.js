const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { isRfc3339Utc } = require('../validators/common');
const {
  createQuote,
  listQuotes,
  getQuoteById,
  acceptQuote,
  createOrderFromQuote,
} = require('../data/cpq-store');

const router = express.Router();

function validateQuoteBody(req, res, next) {
  const errors = [];
  const { opportunity_id, currency, valid_until, line_items, tax_percent } = req.body;

  if (typeof opportunity_id !== 'string' || !opportunity_id.trim()) {
    errors.push({ field: 'opportunity_id', reason: 'must_be_non_empty_string' });
  }

  if (typeof currency !== 'string' || !currency.trim()) {
    errors.push({ field: 'currency', reason: 'must_be_non_empty_string' });
  }

  if (!isRfc3339Utc(valid_until)) {
    errors.push({ field: 'valid_until', reason: 'must_be_rfc3339_utc' });
  }

  if (!Array.isArray(line_items) || line_items.length === 0) {
    errors.push({ field: 'line_items', reason: 'must_be_non_empty_array' });
  } else {
    line_items.forEach((item, index) => {
      if (typeof item.product_id !== 'string' || !item.product_id.trim()) {
        errors.push({ field: `line_items.${index}.product_id`, reason: 'must_be_non_empty_string' });
      }

      if (!Number.isFinite(Number(item.quantity)) || Number(item.quantity) <= 0) {
        errors.push({ field: `line_items.${index}.quantity`, reason: 'must_be_positive_number' });
      }

      if (!Number.isFinite(Number(item.list_price)) || Number(item.list_price) < 0) {
        errors.push({ field: `line_items.${index}.list_price`, reason: 'must_be_non_negative_number' });
      }

      if (
        item.discount_percent !== undefined
        && (!Number.isFinite(Number(item.discount_percent))
        || Number(item.discount_percent) < 0
        || Number(item.discount_percent) > 100)
      ) {
        errors.push({ field: `line_items.${index}.discount_percent`, reason: 'must_be_number_between_0_and_100' });
      }
    });
  }

  if (
    tax_percent !== undefined
    && (!Number.isFinite(Number(tax_percent)) || Number(tax_percent) < 0 || Number(tax_percent) > 100)
  ) {
    errors.push({ field: 'tax_percent', reason: 'must_be_number_between_0_and_100' });
  }

  if (errors.length > 0) {
    return respondError(res, 'validation_error', 'One or more fields are invalid.', errors, 422);
  }

  return next();
}

router.get('/', requestValidationMiddleware(), requireScopes(['quotes.read']), (req, res) => {
  return respondSuccess(res, listQuotes(req.auth.tenant_id));
});

router.post(
  '/',
  requestValidationMiddleware(['opportunity_id', 'currency', 'valid_until', 'line_items', 'tax_percent']),
  requireScopes(['quotes.create']),
  validateQuoteBody,
  (req, res) => {
    const quote = createQuote({
      tenant_id: req.auth.tenant_id,
      opportunity_id: req.body.opportunity_id,
      currency: req.body.currency,
      valid_until: req.body.valid_until,
      line_items: req.body.line_items,
      tax_percent: req.body.tax_percent,
    });

    return res.status(201).json({
      data: quote,
      meta: {
        request_id: req.request_id,
      },
    });
  },
);

router.get('/:quote_id', requestValidationMiddleware(), requireScopes(['quotes.read']), (req, res) => {
  const quote = getQuoteById(req.auth.tenant_id, req.params.quote_id);

  if (!quote) {
    return respondError(res, 'not_found', 'Quote not found.', [{ field: 'quote_id', reason: 'not_found' }], 404);
  }

  return respondSuccess(res, quote);
});

router.post('/:quote_id/acceptances', requestValidationMiddleware(), requireScopes(['quotes.accept']), (req, res) => {
  const quote = acceptQuote(req.auth.tenant_id, req.params.quote_id);

  if (!quote) {
    return respondError(res, 'not_found', 'Quote not found.', [{ field: 'quote_id', reason: 'not_found' }], 404);
  }

  return res.status(201).json({
    data: {
      quote_id: quote.quote_id,
      status: quote.status,
      accepted_at: quote.accepted_at,
    },
    meta: {
      request_id: req.request_id,
    },
  });
});

router.post('/:quote_id/orders', requestValidationMiddleware(), requireScopes(['orders.create']), (req, res) => {
  const quote = getQuoteById(req.auth.tenant_id, req.params.quote_id);

  if (!quote) {
    return respondError(res, 'not_found', 'Quote not found.', [{ field: 'quote_id', reason: 'not_found' }], 404);
  }

  if (quote.status !== 'accepted' || !quote.accepted_at) {
    return respondError(
      res,
      'conflict',
      'Quote must be accepted before conversion to order.',
      [{ field: 'status', reason: 'quote_not_accepted' }],
      409,
    );
  }

  const order = createOrderFromQuote(quote);

  return res.status(201).json({
    data: order,
    meta: {
      request_id: req.request_id,
    },
  });
});

module.exports = router;
