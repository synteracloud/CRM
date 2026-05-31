'use strict';

const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { respondSuccess } = require('../middleware/response-wrapper');

const router = express.Router();

const _memEmails = [
  { email_id: 'em-001', tenant_id: null, to: 'tariq@citypharma.pk', subject: 'Follow-up on CRM proposal', status: 'delivered', sent_at: '2026-05-28T10:00:00Z' },
  { email_id: 'em-002', tenant_id: null, to: 'sana@nextech.pk',     subject: 'Demo booking confirmation',  status: 'opened',    sent_at: '2026-05-29T09:30:00Z' },
  { email_id: 'em-003', tenant_id: null, to: 'bilal@paksteel.pk',   subject: 'Invoice INV-2026-003',       status: 'delivered', sent_at: '2026-05-30T11:00:00Z' },
];

router.get('/', requestValidationMiddleware(), requireScopes(['emails.read']), (req, res) => {
  const data = _memEmails.map((e) => ({ ...e, tenant_id: req.auth.tenant_id }));
  return respondSuccess(res, data, { pagination: { page: 1, page_size: 25, total_items: data.length, total_pages: 1 } });
});

router.get('/engagements', requestValidationMiddleware(), requireScopes(['emails.read']), (req, res) => {
  return respondSuccess(res, [], { pagination: { page: 1, page_size: 25, total_items: 0, total_pages: 0 } });
});

router.get('/engagement-logs', requestValidationMiddleware(), requireScopes(['emails.read']), (req, res) => {
  return respondSuccess(res, [], { pagination: { page: 1, page_size: 25, total_items: 0, total_pages: 0 } });
});

router.post('/', requestValidationMiddleware(), requireScopes(['emails.send']), (req, res) => {
  return res.status(202).json({ data: { queued: true, email_id: `em-${Date.now()}` }, meta: {} });
});

router.post('/:email_id/events', requestValidationMiddleware(), requireScopes(['emails.track']), (req, res) => {
  return respondSuccess(res, { tracked: true });
});

module.exports = router;
