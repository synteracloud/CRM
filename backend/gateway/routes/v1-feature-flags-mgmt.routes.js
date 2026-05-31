'use strict';
/**
 * Feature Flag Management — GET /api/v1/feature-flags, PATCH /api/v1/feature-flags/:key
 * Handles management (CRUD of flag state). Evaluation is via gateway/services/feature-flags.js.
 */

const express  = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

const _flags = [
  { flag_key:'contact.fuzzy_name_match',       label:'Fuzzy Duplicate Detection',       description:'Enable fuzzy contact name matching on create/import',         category:'data',      rule_type:'tenant_match', enabled:false, approval_required:true,  last_changed_by:null, last_changed_at:null, expires_at:null },
  { flag_key:'followup.smart_scheduling',      label:'Smart Follow-up Scheduling',      description:'AI-assisted optimal time suggestion for follow-ups',          category:'ai',        rule_type:'role_match',   enabled:false, approval_required:true,  last_changed_by:null, last_changed_at:null, expires_at:null },
  { flag_key:'collections.whatsapp_auto_send', label:'Auto WhatsApp Reminders',         description:'Automatically send WhatsApp reminders for overdue invoices',  category:'comms',     rule_type:'tenant_match', enabled:true,  approval_required:false, last_changed_by:null, last_changed_at:null, expires_at:null },
  { flag_key:'leads.ai_scoring',               label:'AI Lead Scoring',                 description:'Show ML-computed lead score on lead detail pages',            category:'ai',        rule_type:'percentage_rollout', enabled:true, approval_required:true, last_changed_by:null, last_changed_at:null, expires_at:null },
  { flag_key:'campaigns.urdu_templates',       label:'Urdu Campaign Templates',         description:'Enable Urdu-language campaign template selection (P-017)',    category:'comms',     rule_type:'tenant_match', enabled:false, approval_required:true,  last_changed_by:null, last_changed_at:null, expires_at:'2026-12-31T00:00:00Z' },
  { flag_key:'analytics.predictive_clv',       label:'Predictive CLV Display',          description:'Show CLV estimates on account and contact detail pages',      category:'analytics', rule_type:'role_match',   enabled:true,  approval_required:false, last_changed_by:null, last_changed_at:null, expires_at:null },
];

router.get('/', requestValidationMiddleware(), requireScopes(['audit.read']), (req, res) => {
  return respondSuccess(res, _flags, { total_items: _flags.length });
});

router.patch('/:flag_key', requestValidationMiddleware(), requireScopes(['users.update']), (req, res) => {
  const flag = _flags.find((f) => f.flag_key === req.params.flag_key);
  if (!flag) return respondError(res, 404, 'NOT_FOUND', 'Feature flag not found.');
  const allowed = ['enabled','rule_type','rule_value','expires_at'];
  allowed.forEach((k) => { if (req.body[k] !== undefined) flag[k] = req.body[k]; });
  flag.last_changed_by = req.auth.user_id || req.auth.sub;
  flag.last_changed_at = new Date().toISOString();
  return respondSuccess(res, flag);
});

module.exports = router;
