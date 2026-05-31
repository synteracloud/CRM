'use strict';
/**
 * Org Settings — GET/PATCH /api/v1/org/settings
 * Scope: users.read (GET) / users.update (PATCH) — tenant_admin gated
 * Inline in-memory store; seeded with Pakistan defaults.
 */

const express  = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

const _store = {
  tenant_name:   'Pakistan CRM Demo',
  logo_url:      null,
  timezone:      'Asia/Karachi',
  date_format:   'DD/MM/YYYY',
  language_default: 'en',
  base_currency: 'PKR',
  lakh_crore_notation: true,
  business_hours: {
    start: '09:00', end: '19:00',
    days: ['mon','tue','wed','thu','fri','sat'],
    timezone: 'Asia/Karachi'
  },
  updated_at: new Date().toISOString(),
};

router.get('/', requestValidationMiddleware(), requireScopes(['users.read']), (req, res) => {
  return respondSuccess(res, { ..._store, tenant_id: req.auth.tenant_id });
});

router.patch('/', requestValidationMiddleware(), requireScopes(['users.update']), (req, res) => {
  const allowed = ['tenant_name','logo_url','timezone','date_format','language_default','base_currency','lakh_crore_notation','business_hours'];
  allowed.forEach((k) => { if (req.body[k] !== undefined) _store[k] = req.body[k]; });
  _store.updated_at = new Date().toISOString();
  return respondSuccess(res, { ..._store, tenant_id: req.auth.tenant_id });
});

module.exports = router;
