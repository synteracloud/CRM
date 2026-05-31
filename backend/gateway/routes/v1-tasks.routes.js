const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { forwardRequest } = require('../middleware/transport-forward');

// Downstream service contract — response must include these fields per record:
// task_id, title, status (open|in_progress|completed), due_at (ISO8601),
// owner_id, entity_type (lead|opportunity|contact|null), entity_id, priority (hot|warm|cold)

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['tasks.read']), forwardRequest);
router.post('/', requestValidationMiddleware(), requireScopes(['tasks.create']), forwardRequest);
router.post('/:task_id/reschedule', requestValidationMiddleware(), requireScopes(['tasks.update']), forwardRequest);

module.exports = router;
