'use strict';
/**
 * Tenants — GET /api/v1/tenants/current
 * Returns current tenant's plan, seat usage, and entitlement summary.
 */

const express  = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

router.get('/current', requestValidationMiddleware(), requireScopes(['users.read']), (req, res) => {
  const tenantId = req.auth.tenant_id;
  return respondSuccess(res, {
    tenant_id:    tenantId,
    tenant_name:  'Pakistan CRM Demo',
    plan:         'growth',
    plan_label:   'Growth',
    seat_limit:   25,
    seat_used:    5,
    renewal_date: '2027-01-01',
    active_sessions: 2,
    entitlements: {
      leads:        { limit:-1,  used:0 },
      contacts:     { limit:-1,  used:0 },
      campaigns:    { limit:10,  used:2 },
      workflows:    { limit:10,  used:5 },
      ai_queries:   { limit:500, used:42 },
    },
    entitlement_limit:        10,
    enabled_feature_count:     4,
    entitlement_overage_count: 0,
    entitlements_at_limit:     0,
  });
});

module.exports = router;
