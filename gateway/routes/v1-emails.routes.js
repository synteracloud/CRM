const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { emailEngagementService } = require('../services/email-engagement.service');

const router = express.Router();

router.get(
  '/',
  requestValidationMiddleware(),
  requireScopes(['emails.read']),
  (req, res) => {
    const emails = emailEngagementService.listEmails(req.auth.tenant_id, req.query);
    return respondSuccess(res, emails, {
      pagination: {
        page: Number(req.query.page || 1),
        page_size: Number(req.query.page_size || 25),
        total_items: emails.length,
        total_pages: 1,
      },
    });
  },
);

router.post(
  '/',
  requestValidationMiddleware(['entity_type', 'entity_id', 'to_email', 'from_email', 'subject', 'body_text', 'body_html']),
  requireScopes(['emails.send']),
  (req, res) => {
    const result = emailEngagementService.createEmail(req.auth.tenant_id, req.body, req.auth.sub);
    if (result.errors) {
      return respondError(res, 'validation_error', 'One or more fields are invalid.', result.errors, 422);
    }

    return res.status(201).json({
      data: result.data,
      meta: {
        request_id: req.request_id,
      },
    });
  },
);

router.post(
  '/:email_id/events',
  requestValidationMiddleware(['event_type', 'event_time', 'link_url', 'user_agent', 'ip_address']),
  requireScopes(['emails.track']),
  (req, res) => {
    const result = emailEngagementService.trackEvent(req.auth.tenant_id, req.params.email_id, req.body);

    if (result.notFound) {
      return respondError(res, 'not_found', 'The requested resource was not found.', [{ field: 'email_id', reason: 'not_found' }], 404);
    }

    if (result.errors) {
      return respondError(res, 'validation_error', 'One or more fields are invalid.', result.errors, 422);
    }

    return respondSuccess(res, result.data);
  },
);

router.get(
  '/engagements',
  requestValidationMiddleware(),
  requireScopes(['emails.read']),
  (req, res) => {
    const result = emailEngagementService.getEntityEngagementMetrics(
      req.auth.tenant_id,
      req.query.entity_type,
      req.query.entity_id,
    );

    if (result.errors) {
      return respondError(res, 'validation_error', 'One or more fields are invalid.', result.errors, 422);
    }

    return respondSuccess(res, result.data);
  },
);

router.get(
  '/engagement-logs',
  requestValidationMiddleware(),
  requireScopes(['emails.read']),
  (req, res) => {
    const logs = emailEngagementService.listLogs(req.auth.tenant_id, req.query);
    return respondSuccess(res, logs, {
      pagination: {
        page: Number(req.query.page || 1),
        page_size: Number(req.query.page_size || 25),
        total_items: logs.length,
        total_pages: 1,
      },
    });
  },
);

module.exports = router;
