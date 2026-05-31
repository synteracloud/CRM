'use strict';
/**
 * Notification Preferences — GET/PATCH /api/v1/notification-preferences
 * Per-user preference store keyed by JWT user_id.
 */

const express  = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router  = express.Router();
const _prefs  = {};   // { [user_id]: prefObject }

const DEFAULT_PREFS = () => ({
  events: {
    new_lead:          { in_app:true,  email:true,  whatsapp:false, sms:false },
    followup_overdue:  { in_app:true,  email:true,  whatsapp:true,  sms:false },
    lead_assigned:     { in_app:true,  email:false, whatsapp:false, sms:false },
    sla_breach:        { in_app:true,  email:true,  whatsapp:false, sms:false },
    payment_received:  { in_app:true,  email:true,  whatsapp:true,  sms:false },
    quote_approved:    { in_app:true,  email:true,  whatsapp:false, sms:false },
    deal_won:          { in_app:true,  email:true,  whatsapp:false, sms:false },
    invoice_overdue:   { in_app:true,  email:true,  whatsapp:true,  sms:false },
  },
  quiet_hours: { enabled:false, start:'22:00', end:'08:00', timezone:'Asia/Karachi' },
  updated_at: new Date().toISOString(),
});

router.get('/', requestValidationMiddleware(), requireScopes(['users.read']), (req, res) => {
  const uid = req.auth.user_id || req.auth.sub;
  if (!_prefs[uid]) _prefs[uid] = DEFAULT_PREFS();
  return respondSuccess(res, { user_id: uid, ..._prefs[uid] });
});

router.patch('/', requestValidationMiddleware(), requireScopes(['users.update']), (req, res) => {
  const uid = req.auth.user_id || req.auth.sub;
  if (!_prefs[uid]) _prefs[uid] = DEFAULT_PREFS();
  if (req.body.events) {
    Object.entries(req.body.events).forEach(([k, v]) => {
      if (_prefs[uid].events[k]) Object.assign(_prefs[uid].events[k], v);
      else _prefs[uid].events[k] = v;
    });
  }
  if (req.body.quiet_hours) Object.assign(_prefs[uid].quiet_hours, req.body.quiet_hours);
  _prefs[uid].updated_at = new Date().toISOString();
  return respondSuccess(res, { user_id: uid, ..._prefs[uid] });
});

module.exports = router;
