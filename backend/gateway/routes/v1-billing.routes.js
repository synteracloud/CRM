'use strict';
/**
 * Billing & Subscription Settings — G-04
 * GET /billing/plans, GET /billing/subscription, POST /billing/subscription/upgrade,
 * POST /billing/subscription/downgrade, GET /billing/invoices, GET /billing/entitlements
 * Source: pricing-plans.md §7
 * P-016 NOTE: payment method config not wired — JAZZCASH_STUB_MODE=true until P-016 resolved.
 */

const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

const PLANS = [
  { plan_code: 'plan_starter',    label: 'Starter',    monthly_pkr: 1999,  annual_pkr: null,   seat_limit: 5,    description: '1–5 users, first-time CRM' },
  { plan_code: 'plan_growth',     label: 'Growth',     monthly_pkr: 5999,  annual_pkr: 61189,  seat_limit: 20,   description: '5–20 users, SMB active sales team' },
  { plan_code: 'plan_business',   label: 'Business',   monthly_pkr: 14999, annual_pkr: 143990, seat_limit: null, description: '20+ users, multi-branch' },
  { plan_code: 'plan_enterprise', label: 'Enterprise', monthly_pkr: null,  annual_pkr: null,   seat_limit: null, description: 'Large orgs, custom pricing' },
];

const _sub = {
  plan_code: 'plan_growth',
  plan_label: 'Growth',
  billing_cycle: 'annual',
  current_period_start: '2026-01-01',
  current_period_end: '2027-01-01',
  renewal_date: '2027-01-01',
  seat_limit: 20,
  seat_used: 5,
  is_trial: false,
  subscription_status: 'active',
  monthly_price_pkr: 5999,
  annual_price_pkr: 61189,
};

const _invoices = [
  { invoice_id: 'bill-2026-001', invoice_number: 'BILL-2026-001', period: 'Jan 2026 – Dec 2026', amount_pkr: 61189, status: 'paid', issued_at: '2026-01-01T00:00:00Z' },
  { invoice_id: 'bill-2025-001', invoice_number: 'BILL-2025-001', period: 'Jan 2025 – Dec 2025', amount_pkr: 59988, status: 'paid', issued_at: '2025-01-01T00:00:00Z' },
  { invoice_id: 'bill-2024-001', invoice_number: 'BILL-2024-001', period: 'Jan 2024 – Dec 2024', amount_pkr: 47988, status: 'paid', issued_at: '2024-01-01T00:00:00Z' },
];

const ENTITLEMENTS = [
  'payment_provider_callbacks', 'collections_automation', 'multi_pipeline',
  'shared_inbox', 'case_management', 'offline_sync',
];

// Public — no auth required
router.get('/plans', (req, res) => respondSuccess(res, PLANS));

router.get('/subscription', requestValidationMiddleware(), requireScopes(['billing.read']), (req, res) => {
  return respondSuccess(res, { ..._sub, tenant_id: req.auth.tenant_id });
});

router.post('/subscription/upgrade', requestValidationMiddleware(), requireScopes(['billing.manage']), (req, res) => {
  const { plan_code } = req.body;
  const plan = PLANS.find(p => p.plan_code === plan_code);
  if (!plan) return respondError(res, 'validation_error', `Unknown plan_code: ${plan_code}`, [], 422);
  _sub.plan_code    = plan.plan_code;
  _sub.plan_label   = plan.label;
  _sub.monthly_price_pkr = plan.monthly_pkr;
  _sub.annual_price_pkr  = plan.annual_pkr;
  return respondSuccess(res, { ..._sub, upgraded: true, effective: 'immediate' });
});

router.post('/subscription/downgrade', requestValidationMiddleware(), requireScopes(['billing.manage']), (req, res) => {
  return respondSuccess(res, { ..._sub, downgrade_scheduled: true, effective_date: _sub.current_period_end });
});

router.get('/invoices', requestValidationMiddleware(), requireScopes(['billing.read']), (req, res) => {
  return respondSuccess(res, _invoices);
});

router.get('/entitlements', requestValidationMiddleware(), requireScopes(['billing.read']), (req, res) => {
  return respondSuccess(res, ENTITLEMENTS);
});

module.exports = router;
