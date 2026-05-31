'use strict';
/**
 * Custom Report Builder — H-07
 * GET /reports/definitions, POST /reports/definitions, POST /reports/execute
 * Source: b9-p10 §2.7, kpi-data-pipelines.md
 * Constraint: only canonical KPIs from kpi-data-pipelines.md + named RM fields as metric_key values
 */

const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

const MONTHS = ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'];

// kpi-data-pipelines.md canonical KPIs + named RM fields
const METRIC_SERIES = {
  weighted_pipeline:       { label: 'Weighted Pipeline (PKR)', data: [2800000, 3100000, 2600000, 3400000, 3900000, 4280000], currency: 'PKR' },
  lead_conversion_rate:    { label: 'Lead Conversion Rate (%)', data: [28, 31, 29, 33, 34, 33],    currency: null },
  open_pipeline_value:     { label: 'Open Pipeline (PKR)',      data: [5200000, 5800000, 4900000, 6100000, 7200000, 7900000], currency: 'PKR' },
  quote_acceptance_rate:   { label: 'Quote Acceptance Rate (%)', data: [42, 45, 38, 51, 48, 52],   currency: null },
  booked_revenue:          { label: 'Booked Revenue (PKR)',     data: [980000, 1150000, 890000, 1320000, 1480000, 1620000], currency: 'PKR' },
  cash_collected:          { label: 'Cash Collected (PKR)',     data: [840000, 920000, 780000, 1050000, 1180000, 1290000], currency: 'PKR' },
  invoice_collection_rate: { label: 'Collection Rate (%)',      data: [68, 72, 70, 75, 73, 73],     currency: null },
  subscription_churn_rate: { label: 'Churn Rate (%)',           data: [3.2, 2.8, 3.5, 2.1, 2.4, 2.2], currency: null },
  mrr:                     { label: 'MRR (PKR)',                data: [285000, 295000, 310000, 320000, 330000, 335000], currency: 'PKR' },
  arr:                     { label: 'ARR (PKR)',                data: [3420000, 3540000, 3720000, 3840000, 3960000, 4020000], currency: 'PKR' },
  collection_rate:         { label: 'Collection Rate (%)',      data: [68, 72, 70, 75, 73, 73],     currency: null },
  won_deals:               { label: 'Won Deals',                data: [4, 6, 5, 7, 8, 6],           currency: null },
  sla_breach_rate:         { label: 'SLA Breach Rate (%)',      data: [18, 14, 17, 12, 15, 16],     currency: null },
  avg_deal_cycle:          { label: 'Avg Deal Cycle (days)',    data: [42, 38, 45, 36, 33, 35],     currency: null },
  follow_up_completion:    { label: 'Follow-up Completion (%)', data: [72, 78, 74, 81, 83, 85],     currency: null },
};

const _definitions = [
  { report_id: 'rpt-001', name: 'Monthly Pipeline Summary',  metrics: ['weighted_pipeline', 'won_deals'],           group_by: 'period', chart_type: 'bar',  created_by: 'u-003', created_at: '2026-05-10T09:00:00Z' },
  { report_id: 'rpt-002', name: 'Collections Performance',   metrics: ['invoice_collection_rate', 'cash_collected'], group_by: 'period', chart_type: 'line', created_by: 'u-001', created_at: '2026-05-15T11:00:00Z' },
];

router.get('/definitions', requestValidationMiddleware(), requireScopes(['reports.read']), (req, res) => {
  return respondSuccess(res, _definitions);
});

router.post('/definitions', requestValidationMiddleware(), requireScopes(['reports.create']), (req, res) => {
  const { name, metrics, group_by, chart_type, schedule, deliver_to } = req.body;
  const def = {
    report_id:  'rpt-' + Date.now(),
    name:       name || 'Untitled Report',
    metrics:    metrics || [],
    group_by:   group_by || 'period',
    chart_type: chart_type || 'bar',
    schedule:   schedule || null,
    deliver_to: deliver_to || null,
    created_by: req.auth ? req.auth.sub : 'u-001',
    created_at: new Date().toISOString(),
  };
  _definitions.push(def);
  return respondSuccess(res, def);
});

router.post('/execute', requestValidationMiddleware(), requireScopes(['reports.read']), (req, res) => {
  const { metric_key, group_by } = req.body;
  const series = METRIC_SERIES[metric_key];
  if (!series) {
    return respondError(res, 'validation_error',
      `Unknown metric_key: "${metric_key}". Valid keys: ${Object.keys(METRIC_SERIES).join(', ')}`,
      [], 422);
  }
  return respondSuccess(res, {
    metric_key,
    label:    series.label,
    group_by: group_by || 'period',
    series:   MONTHS.map((m, i) => ({ label: m, value: series.data[i] })),
    currency: series.currency,
  });
});

module.exports = router;
