const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { listAuditEvents } = require('../middleware/audit-log');

const router = express.Router();

router.get('/events', requestValidationMiddleware(), requireScopes(['audit.logs.read']), (req, res) => {
  const events = listAuditEvents(req.auth.tenant_id);
  return respondSuccess(res, events, {
    pagination: {
      page: Number(req.query.page || 1),
      page_size: Number(req.query.page_size || 25),
      total_items: events.length,
      total_pages: 1,
    },
  });
});

module.exports = router;
