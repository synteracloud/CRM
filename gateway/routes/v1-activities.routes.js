const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { createActivity, listActivities } = require('../services/activities-tasks.store');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['activities.read']), (req, res) => {
  const activities = listActivities(req.auth.tenant_id, req.query);
  return respondSuccess(res, activities, {
    pagination: {
      page: Number(req.query.page || 1),
      page_size: Number(req.query.page_size || 25),
      total_items: activities.length,
      total_pages: 1,
    },
  });
});

router.post(
  '/',
  requestValidationMiddleware(['entity_type', 'entity_id', 'event_type', 'event_time', 'payload_json', 'source_service', 'actor_user_id']),
  requireScopes(['activities.create']),
  (req, res) => {
    const result = createActivity(req.body, req.auth);
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

module.exports = router;
