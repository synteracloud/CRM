const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['users.read']), (req, res) => {
  return respondSuccess(
    res,
    [
      {
        id: 'usr_01HZX7X4QW2D7B2K4A0G5R9M2C',
        email: 'jane.doe@example.com',
        display_name: 'Jane Doe',
        status: 'active',
        created_at: '2026-03-26T12:00:00Z',
        updated_at: '2026-03-26T12:00:00Z',
      },
    ],
    {
      pagination: {
        page: Number(req.query.page || 1),
        page_size: Number(req.query.page_size || 25),
        total_items: 1,
        total_pages: 1,
      },
    },
  );
});

router.post(
  '/',
  requestValidationMiddleware(['email', 'display_name', 'status']),
  requireScopes(['users.create']),
  (req, res) => {
    const now = '2026-03-26T12:00:00Z';

    return res.status(201).json({
      data: {
        id: 'usr_01NEW7X4QW2D7B2K4A0G5R9M2C',
        email: req.body.email,
        display_name: req.body.display_name,
        status: req.body.status,
        created_at: now,
        updated_at: now,
      },
      meta: {
        request_id: req.request_id,
      },
    });
  },
);

// POST /:user_id/roles — assign a role to a user
// Spec: security/identity-auth-rbac.md §4.3
// Requires users.manage_roles scope. Anti-escalation check: caller cannot grant
// permissions above their own effective set (enforced at identity service layer).
router.post(
  '/:user_id/roles',
  requestValidationMiddleware(['role_id']),
  requireScopes(['users.manage_roles']),
  (req, res) => {
    const { user_id } = req.params;
    const { role_id } = req.body;

    if (!role_id || typeof role_id !== 'string') {
      return respondError(res, 'validation_error', 'role_id is required.', [{ field: 'role_id', reason: 'required' }], 422);
    }

    const now = new Date().toISOString();
    return res.status(201).json({
      data: {
        user_role_id: `ur_${Date.now()}`,
        tenant_id:    req.auth.tenant_id,
        user_id,
        role_id,
        assigned_by_user_id: req.auth.sub,
        assigned_at: now,
      },
      meta: { request_id: req.request_id },
    });
  },
);

module.exports = router;
