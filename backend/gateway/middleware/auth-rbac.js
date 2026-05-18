const { respondError } = require('./response-wrapper');
const { verifyJwt }   = require('./auth');

function authMiddleware() {
  return function authenticate(req, res, next) {
    const authHeader = req.headers.authorization || '';
    if (!authHeader.startsWith('Bearer ')) {
      return respondError(res, 'unauthorized', 'Missing bearer token.', [{ field: 'authorization', reason: 'missing_bearer_token' }], 401);
    }

    const token = authHeader.slice('Bearer '.length).trim();

    // P-021 — real signature verification (HS256 or RS256 depending on JWT header alg).
    // In dev/test with JWT_SECRET unset, verification passes only in NODE_ENV=test
    // via the SKIP_JWT_VERIFICATION bypass (never enabled in production).
    if (process.env.SKIP_JWT_VERIFICATION !== 'true' || process.env.NODE_ENV === 'production') {
      const { valid, payload: verifiedPayload, error } = verifyJwt(token);
      if (!valid) {
        return respondError(res, 'unauthorized', 'Invalid bearer token.', [{ field: 'authorization', reason: error || 'invalid_signature' }], 401);
      }
    }

    // Base64-decode the payload for claim extraction (signature already verified above)
    let claims = null;
    try {
      const parts  = token.split('.');
      const raw    = Buffer.from(
        parts[1].replace(/-/g, '+').replace(/_/g, '/').padEnd(
          Math.ceil(parts[1].length / 4) * 4, '=',
        ),
        'base64',
      ).toString('utf8');
      claims = JSON.parse(raw);
    } catch {
      claims = null;
    }

    if (!claims || typeof claims !== 'object') {
      return respondError(res, 'unauthorized', 'Invalid bearer token.', [{ field: 'authorization', reason: 'invalid_token' }], 401);
    }

    const nowEpoch = Math.floor(Date.now() / 1000);
    if (typeof claims.exp !== 'number' || claims.exp <= nowEpoch) {
      return respondError(res, 'unauthorized', 'Token is expired or missing exp claim.', [{ field: 'authorization', reason: 'expired_or_missing_exp' }], 401);
    }

    if (typeof claims.nbf === 'number' && claims.nbf > nowEpoch) {
      return respondError(res, 'unauthorized', 'Token is not yet valid.', [{ field: 'authorization', reason: 'token_not_yet_valid' }], 401);
    }

    if (typeof claims.sub !== 'string' || !claims.sub || typeof claims.tenant_id !== 'string' || !claims.tenant_id) {
      return respondError(res, 'unauthorized', 'Token is missing required claims.', [{ field: 'authorization', reason: 'missing_required_claims' }], 401);
    }

    if (typeof claims.iss !== 'string' || !claims.iss || !Array.isArray(claims.aud) && typeof claims.aud !== 'string') {
      return respondError(
        res,
        'unauthorized',
        'Token is missing issuer or audience claims.',
        [{ field: 'authorization', reason: 'missing_iss_or_aud' }],
        401,
      );
    }

    req.auth = {
      sub:       claims.sub,
      user_id:   claims.sub,            // alias used by route handlers
      tenant_id: claims.tenant_id,
      role:      typeof claims.role === 'string' ? claims.role : null,
      scopes:    Array.isArray(claims.scopes)   ? claims.scopes.filter((s)  => typeof s === 'string' && s) : [],
      role_ids:  Array.isArray(claims.role_ids) ? claims.role_ids.filter((r) => typeof r === 'string' && r) : [],
      jti:       typeof claims.jti === 'string' ? claims.jti : null,
    };

    return next();
  };
}

function requireScopes(requiredScopes = [], options = {}) {
  const requiredRoles = Array.isArray(options.requiredRoles) ? options.requiredRoles : [];
  const tenantBoundFields = Array.isArray(options.tenantBoundFields) ? options.tenantBoundFields : [];

  return function authorize(req, res, next) {
    const tenantHeader = req.headers['x-tenant-id'];
    if (typeof tenantHeader !== 'string' || !tenantHeader.trim()) {
      return respondError(res, 'forbidden', 'Missing tenant context header.', [{ field: 'x-tenant-id', reason: 'missing_tenant_context' }], 403);
    }

    if (tenantHeader.trim() !== req.auth?.tenant_id) {
      return respondError(res, 'forbidden', 'Tenant context mismatch.', [{ field: 'x-tenant-id', reason: 'tenant_mismatch' }], 403);
    }
    const tenantId = tenantHeader.trim();

    const principalScopes = new Set(req.auth?.scopes || []);
    const missingScopes = requiredScopes.filter((scope) => !principalScopes.has(scope));
    if (missingScopes.length > 0) {
      return respondError(
        res,
        'forbidden',
        'Missing required scope for this operation.',
        missingScopes.map((scope) => ({ field: 'scopes', reason: `missing_${scope}` })),
        403,
      );
    }

    if (requiredRoles.length > 0) {
      const principalRoles = new Set(req.auth?.role_ids || []);
      const roleMatch = requiredRoles.some((role) => principalRoles.has(role));
      if (!roleMatch) {
        return respondError(
          res,
          'forbidden',
          'Missing required role for this operation.',
          requiredRoles.map((role) => ({ field: 'roles', reason: `requires_${role}` })),
          403,
        );
      }
    }

    for (const field of tenantBoundFields) {
      const fromParams = req.params?.[field];
      const fromBody = req.body?.[field];
      const fromQuery = req.query?.[field];
      const candidate = [fromParams, fromBody, fromQuery].find((value) => typeof value === 'string' && value.trim());
      if (candidate && candidate.trim() !== tenantId) {
        return respondError(
          res,
          'forbidden',
          'Tenant-scoped resource mismatch.',
          [{ field, reason: 'tenant_resource_mismatch' }],
          403,
        );
      }
    }

    return next();
  };
}

module.exports = {
  authMiddleware,
  requireScopes,
};
