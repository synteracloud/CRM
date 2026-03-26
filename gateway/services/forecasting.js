const { isPlainObject } = require('../validators/common');

const FORECAST_CATEGORY_WEIGHTS = Object.freeze({
  pipeline: 0.25,
  best_case: 0.5,
  commit: 0.75,
  closed: 1,
  omitted: 0,
});

function isIsoDate(value) {
  if (typeof value !== 'string') return false;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(`${value}T00:00:00.000Z`);
  return !Number.isNaN(date.getTime()) && date.toISOString().startsWith(value);
}

function validateOpportunity(opportunity, index) {
  const errors = [];
  const fieldPrefix = `opportunities[${index}]`;

  if (!isPlainObject(opportunity)) {
    return [{ field: fieldPrefix, reason: 'must_be_json_object' }];
  }

  const requiredStringFields = ['opportunity_id', 'tenant_id', 'stage', 'forecast_category'];
  for (const field of requiredStringFields) {
    if (typeof opportunity[field] !== 'string' || !opportunity[field].trim()) {
      errors.push({ field: `${fieldPrefix}.${field}`, reason: 'must_be_non_empty_string' });
    }
  }

  if (typeof opportunity.amount !== 'number' || Number.isNaN(opportunity.amount) || opportunity.amount < 0) {
    errors.push({ field: `${fieldPrefix}.amount`, reason: 'must_be_non_negative_number' });
  }

  if (!isIsoDate(opportunity.close_date)) {
    errors.push({ field: `${fieldPrefix}.close_date`, reason: 'must_be_iso_date_yyyy_mm_dd' });
  }

  if (typeof opportunity.is_closed !== 'boolean') {
    errors.push({ field: `${fieldPrefix}.is_closed`, reason: 'must_be_boolean' });
  }

  if (typeof opportunity.is_won !== 'boolean') {
    errors.push({ field: `${fieldPrefix}.is_won`, reason: 'must_be_boolean' });
  }

  if (opportunity.is_won === true && opportunity.is_closed !== true) {
    errors.push({ field: `${fieldPrefix}.is_won`, reason: 'won_opportunity_must_be_closed' });
  }

  if (typeof opportunity.forecast_category === 'string' && FORECAST_CATEGORY_WEIGHTS[opportunity.forecast_category] === undefined) {
    errors.push({
      field: `${fieldPrefix}.forecast_category`,
      reason: 'must_be_one_of_pipeline_best_case_commit_closed_omitted',
    });
  }

  return errors;
}

function validateOpportunityCollection(opportunities) {
  if (!Array.isArray(opportunities) || opportunities.length === 0) {
    return [{ field: 'opportunities', reason: 'must_be_non_empty_array' }];
  }

  const errors = [];
  opportunities.forEach((opportunity, index) => {
    errors.push(...validateOpportunity(opportunity, index));
  });

  return errors;
}

function toModeledOpportunity(opportunity) {
  const probability = FORECAST_CATEGORY_WEIGHTS[opportunity.forecast_category];
  const weightedAmount = Number((opportunity.amount * probability).toFixed(2));

  return {
    opportunity_id: opportunity.opportunity_id,
    tenant_id: opportunity.tenant_id,
    stage: opportunity.stage,
    forecast_category: opportunity.forecast_category,
    amount: opportunity.amount,
    close_date: opportunity.close_date,
    is_closed: opportunity.is_closed,
    is_won: opportunity.is_won,
    probability,
    weighted_amount: weightedAmount,
  };
}

function addToBucket(map, key, opportunity) {
  const current = map.get(key) || {
    key,
    opportunity_count: 0,
    total_amount: 0,
    weighted_amount: 0,
    closed_won_amount: 0,
  };

  const probability = FORECAST_CATEGORY_WEIGHTS[opportunity.forecast_category];
  current.opportunity_count += 1;
  current.total_amount += opportunity.amount;
  current.weighted_amount += opportunity.amount * probability;
  if (opportunity.is_closed && opportunity.is_won) {
    current.closed_won_amount += opportunity.amount;
  }

  map.set(key, current);
}

function normalizeBuckets(map) {
  return [...map.values()]
    .map((bucket) => ({
      ...bucket,
      total_amount: Number(bucket.total_amount.toFixed(2)),
      weighted_amount: Number(bucket.weighted_amount.toFixed(2)),
      closed_won_amount: Number(bucket.closed_won_amount.toFixed(2)),
    }))
    .sort((a, b) => a.key.localeCompare(b.key));
}

function buildForecastModel(opportunities) {
  return opportunities.map(toModeledOpportunity);
}

function buildForecastAggregation(opportunities, groupBy = 'stage') {
  const stageBuckets = new Map();
  const categoryBuckets = new Map();
  const closeMonthBuckets = new Map();

  const totals = {
    opportunity_count: 0,
    open_count: 0,
    closed_count: 0,
    won_count: 0,
    lost_count: 0,
    total_amount: 0,
    open_amount: 0,
    won_amount: 0,
    weighted_amount: 0,
  };

  for (const opportunity of opportunities) {
    const probability = FORECAST_CATEGORY_WEIGHTS[opportunity.forecast_category];

    totals.opportunity_count += 1;
    totals.total_amount += opportunity.amount;
    totals.weighted_amount += opportunity.amount * probability;

    if (opportunity.is_closed) {
      totals.closed_count += 1;
      if (opportunity.is_won) {
        totals.won_count += 1;
        totals.won_amount += opportunity.amount;
      } else {
        totals.lost_count += 1;
      }
    } else {
      totals.open_count += 1;
      totals.open_amount += opportunity.amount;
    }

    addToBucket(stageBuckets, opportunity.stage, opportunity);
    addToBucket(categoryBuckets, opportunity.forecast_category, opportunity);
    addToBucket(closeMonthBuckets, opportunity.close_date.slice(0, 7), opportunity);
  }

  const groupedBy = groupBy === 'forecast_category' ? normalizeBuckets(categoryBuckets) : normalizeBuckets(stageBuckets);

  return {
    totals: {
      ...totals,
      total_amount: Number(totals.total_amount.toFixed(2)),
      open_amount: Number(totals.open_amount.toFixed(2)),
      won_amount: Number(totals.won_amount.toFixed(2)),
      weighted_amount: Number(totals.weighted_amount.toFixed(2)),
    },
    grouped_by: groupBy,
    groups: groupedBy,
    by_forecast_category: normalizeBuckets(categoryBuckets),
    by_close_month: normalizeBuckets(closeMonthBuckets),
  };
}

module.exports = {
  FORECAST_CATEGORY_WEIGHTS,
  validateOpportunityCollection,
  buildForecastModel,
  buildForecastAggregation,
};
