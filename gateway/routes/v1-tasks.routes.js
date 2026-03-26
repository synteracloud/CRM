const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { createTask, listTasks, rescheduleTask } = require('../services/activities-tasks.store');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['tasks.read']), (req, res) => {
  const tasks = listTasks(req.auth.tenant_id, req.query);
  return respondSuccess(res, tasks, {
    pagination: {
      page: Number(req.query.page || 1),
      page_size: Number(req.query.page_size || 25),
      total_items: tasks.length,
      total_pages: 1,
    },
  });
});

router.post(
  '/',
  requestValidationMiddleware([
    'entity_type',
    'entity_id',
    'title',
    'description',
    'status',
    'priority',
    'assigned_user_id',
    'entity_owner_user_id',
    'candidate_user_ids',
    'starts_at',
    'due_at',
  ]),
  requireScopes(['tasks.create']),
  (req, res) => {
    const result = createTask(req.body, req.auth);
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
  '/:task_id/reschedule',
  requestValidationMiddleware(['starts_at', 'due_at']),
  requireScopes(['tasks.update']),
  (req, res) => {
    const result = rescheduleTask(req.params.task_id, req.auth.tenant_id, req.body);

    if (result.notFound) {
      return respondError(res, 'not_found', 'Task not found.', [{ field: 'task_id', reason: 'not_found' }], 404);
    }

    if (result.errors) {
      return respondError(res, 'validation_error', 'One or more fields are invalid.', result.errors, 422);
    }

    return respondSuccess(res, result.data);
  },
);

module.exports = router;
