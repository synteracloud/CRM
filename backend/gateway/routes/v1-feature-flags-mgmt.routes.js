'use strict';

/**
 * Feature Flag Management — GET /api/v1/feature-flags, PATCH /api/v1/feature-flags/:key
 *
 * A-007 (C3): Flag evaluations are cached in Redis with 60s TTL.
 * Cache key: `ff:{tenant_id}:{flag_key}`
 * PATCH invalidates the cache entry for the updated flag.
 */

const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { getRedisClient } = require('../config/redis-client');

const FF_CACHE_TTL = 60; // seconds

const router = express.Router();

const _flags = [
  { flag_key: 'contact.fuzzy_name_match',       label: 'Fuzzy Duplicate Detection',       description: 'Enable fuzzy contact name matching on create/import',         category: 'data',      rule_type: 'tenant_match',      enabled: false, approval_required: true,  last_changed_by: null, last_changed_at: null, expires_at: null },
  { flag_key: 'followup.smart_scheduling',       label: 'Smart Follow-up Scheduling',      description: 'AI-assisted optimal time suggestion for follow-ups',          category: 'ai',        rule_type: 'role_match',        enabled: false, approval_required: true,  last_changed_by: null, last_changed_at: null, expires_at: null },
  { flag_key: 'collections.whatsapp_auto_send',  label: 'Auto WhatsApp Reminders',         description: 'Automatically send WhatsApp reminders for overdue invoices',  category: 'comms',     rule_type: 'tenant_match',      enabled: true,  approval_required: false, last_changed_by: null, last_changed_at: null, expires_at: null },
  { flag_key: 'leads.ai_scoring',                label: 'AI Lead Scoring',                 description: 'Show ML-computed lead score on lead detail pages',            category: 'ai',        rule_type: 'percentage_rollout', enabled: true,  approval_required: true,  last_changed_by: null, last_changed_at: null, expires_at: null },
  { flag_key: 'campaigns.urdu_templates',        label: 'Urdu Campaign Templates',         description: 'Enable Urdu-language campaign template selection (P-017)',    category: 'comms',     rule_type: 'tenant_match',      enabled: false, approval_required: true,  last_changed_by: null, last_changed_at: null, expires_at: '2026-12-31T00:00:00Z' },
  { flag_key: 'analytics.predictive_clv',        label: 'Predictive CLV Display',          description: 'Show CLV estimates on account and contact detail pages',      category: 'analytics', rule_type: 'role_match',        enabled: true,  approval_required: false, last_changed_by: null, last_changed_at: null, expires_at: null },
];

async function _getCached(tenantId, flagKey) {
  try {
    const raw = await getRedisClient().get(`ff:${tenantId}:${flagKey}`);
    return raw ? JSON.parse(raw) : null;
  } catch (_e) {
    return null;
  }
}

async function _setCache(tenantId, flagKey, value) {
  try {
    await getRedisClient().setex(`ff:${tenantId}:${flagKey}`, FF_CACHE_TTL, JSON.stringify(value));
  } catch (_e) { /* non-fatal */ }
}

async function _invalidateCache(tenantId, flagKey) {
  try {
    await getRedisClient().del(`ff:${tenantId}:${flagKey}`);
  } catch (_e) { /* non-fatal */ }
}

// ── GET /feature-flags ────────────────────────────────────────────────────────
router.get('/', requestValidationMiddleware(), requireScopes(['audit.read']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const results = await Promise.all(_flags.map(async (flag) => {
    const cached = await _getCached(tenantId, flag.flag_key);
    if (cached) return cached;
    await _setCache(tenantId, flag.flag_key, flag);
    return flag;
  }));
  return respondSuccess(res, results, { total_items: results.length });
});

// ── PATCH /feature-flags/:flag_key ────────────────────────────────────────────
router.patch('/:flag_key', requestValidationMiddleware(), requireScopes(['users.update']), async (req, res) => {
  const flag = _flags.find((f) => f.flag_key === req.params.flag_key);
  if (!flag) return respondError(res, 'not_found', 'Feature flag not found.', [], 404);
  const allowed = ['enabled', 'rule_type', 'rule_value', 'expires_at'];
  allowed.forEach((k) => { if (req.body[k] !== undefined) flag[k] = req.body[k]; }); // nosemgrep
  flag.last_changed_by = req.auth.user_id || req.auth.sub;
  flag.last_changed_at = new Date().toISOString();
  await _invalidateCache(req.auth.tenant_id, flag.flag_key);
  return respondSuccess(res, flag);
});

module.exports = router;
