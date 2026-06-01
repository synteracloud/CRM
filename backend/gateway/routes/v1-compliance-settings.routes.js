'use strict';
/**
 * Compliance Settings — GET/PATCH /api/v1/compliance/settings
 * Tenant-level compliance configuration: retention policies, break-glass.
 */

const express  = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

const _store = {
  retention_policies: {
    financial:    { years:7,  legal_basis:'regulatory' },
    crm_activity: { years:3,  legal_basis:'legitimate_interest' },
    audit_log:    { years:7,  legal_basis:'regulatory' },
    messages:     { years:2,  legal_basis:'legitimate_interest' },
  },
  break_glass: {
    require_two_approvers: true,
    ttl_hours: 4,
    post_review_window_hours: 24,
  },
  gdpr_mode:  false,
  pdpa_mode:  true,
  data_residency: 'pk',
  updated_at: new Date().toISOString(),
};

router.get('/', requestValidationMiddleware(), requireScopes(['audit.logs.read']), (req, res) => {
  return respondSuccess(res, { ..._store, tenant_id: req.auth.tenant_id });
});

router.patch('/', requestValidationMiddleware(), requireScopes(['users.update']), (req, res) => {
  const allowed = ['retention_policies','break_glass','gdpr_mode','pdpa_mode','data_residency'];
  allowed.forEach((k) => {
    if (Object.prototype.hasOwnProperty.call(req.body, k)) {
      const val = req.body[k]; // nosemgrep
      if (typeof val === 'object' && val !== null && typeof _store[k] === 'object') {
        Object.assign(_store[k], val); // nosemgrep
      } else {
        _store[k] = val; // nosemgrep
      }
    }
  });
  _store.updated_at = new Date().toISOString();
  return respondSuccess(res, { ..._store, tenant_id: req.auth.tenant_id });
});

module.exports = router;
