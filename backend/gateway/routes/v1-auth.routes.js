'use strict';

/**
 * Auth session management endpoints.
 *
 * Spec: security/identity-auth-rbac.md §4.1–4.3
 *
 * Endpoints:
 *   POST   /api/v1/auth/sessions         — login (IdP token exchange)
 *   DELETE /api/v1/auth/sessions/current — logout (revoke current jti)
 */

const express = require('express');
const { respondError } = require('../middleware/response-wrapper');
const { addRevoked } = require('../middleware/jti-blocklist');

const router = express.Router();

// POST /auth/sessions — login / IdP token exchange
// Spec: identity-auth-rbac.md §4.1
// Full IdP integration is pending (requires external OIDC provider).
// This endpoint validates the request shape and returns the correct envelope.
router.post('/sessions', (req, res) => {
  const { tenant_id, idp_token } = req.body || {};

  if (!tenant_id || typeof tenant_id !== 'string') {
    return respondError(res, 'validation_error', 'tenant_id is required.', [{ field: 'tenant_id', reason: 'required' }], 422);
  }
  if (!idp_token || typeof idp_token !== 'string') {
    return respondError(res, 'validation_error', 'idp_token is required.', [{ field: 'idp_token', reason: 'required' }], 422);
  }

  // IdP verification not yet wired — return 501 until OIDC provider is configured.
  return res.status(501).json({
    error: {
      code: 'not_implemented',
      message: 'IdP token exchange not yet configured. Set JWT_PUBLIC_KEY_URL and restart.',
    },
    meta: { request_id: req.request_id },
  });
});

// DELETE /auth/sessions/current — logout (revoke current session)
// Spec: identity-auth-rbac.md §4.2
// Requires a valid Bearer token — authMiddleware runs before this handler.
// Adds the token's jti to the in-memory blocklist so it is rejected on next use.
router.delete('/sessions/current', (req, res) => {
  const jti = req.auth?.jti;

  if (!jti) {
    return respondError(res, 'unauthorized', 'No jti claim in token — cannot revoke.', [{ field: 'authorization', reason: 'missing_jti' }], 401);
  }

  // TTL: remaining token lifetime (access token max is 15 min; use that as upper bound)
  const ACCESS_TOKEN_MAX_TTL_MS = 15 * 60 * 1000;
  addRevoked(jti, ACCESS_TOKEN_MAX_TTL_MS);

  return res.status(200).json({
    data: { revoked: true },
    meta: { request_id: req.request_id },
  });
});

module.exports = router;
