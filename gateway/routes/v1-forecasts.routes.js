const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const {
  validateOpportunityCollection,
  buildForecastModel,
  buildForecastAggregation,
} = require('../services/forecasting');

const router = express.Router();

router.post(
  '/model',
  requestValidationMiddleware(['opportunities']),
  requireScopes(['forecasts.read']),
  (req, res) => {
    const { opportunities } = req.body;
    const validationErrors = validateOpportunityCollection(opportunities);

    if (validationErrors.length > 0) {
      return respondError(res, 'validation_error', 'Opportunities payload contains invalid records.', validationErrors, 422);
    }

    return respondSuccess(res, {
      opportunities: buildForecastModel(opportunities),
    });
  },
);

router.post(
  '/aggregate',
  requestValidationMiddleware(['opportunities', 'group_by']),
  requireScopes(['forecasts.read']),
  (req, res) => {
    const { opportunities, group_by: groupBy = 'stage' } = req.body;
    const validationErrors = validateOpportunityCollection(opportunities);

    if (!['stage', 'forecast_category'].includes(groupBy)) {
      validationErrors.push({ field: 'group_by', reason: 'must_be_stage_or_forecast_category' });
    }

    if (validationErrors.length > 0) {
      return respondError(res, 'validation_error', 'Opportunities payload contains invalid records.', validationErrors, 422);
    }

    return respondSuccess(res, buildForecastAggregation(opportunities, groupBy));
  },
);

module.exports = router;
