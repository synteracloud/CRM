'use strict';
/**
 * Communication Engagement — A-08
 * GET /communications/engagement
 * Source: b9-p01 §2.9 + §5, CommunicationEngagementRM
 * Seed data mirrors crm-dummy.js COMMS_KPI + per-campaign channel breakdown
 */

const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

const _engagement = {
  delivery_rate:             91,
  open_rate:                 57,
  reply_rate:                18,
  failed_delivery_count:     34,
  low_delivery_channel_count: 0,
  whatsapp_opted_in:         843,
  whatsapp_opt_out_rate:     2.1,
  delivery_open_click_reply_rate: [
    { channel: 'whatsapp_broadcast', label: 'Eid Offer',   delivery: 94, open: 68, reply: 22 },
    { channel: 'email',              label: 'Q2 Launch',   delivery: 88, open: 42, reply: 8  },
    { channel: 'whatsapp_broadcast', label: 'Re-engage',   delivery: 91, open: 55, reply: 18 },
    { channel: 'email',              label: 'Enterprise',  delivery: 97, open: 51, reply: 12 },
    { channel: 'whatsapp_broadcast', label: 'Ramadan',     delivery: 89, open: 61, reply: 19 },
  ],
};

router.get('/engagement', requestValidationMiddleware(), requireScopes(['marketing.read']), (req, res) => {
  return respondSuccess(res, _engagement);
});

module.exports = router;
