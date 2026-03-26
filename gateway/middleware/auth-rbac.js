const { respondError } = require('./response-wrapper');

function decodeTokenPayload(token) {
  try {
    const normalized = token.replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=');
    const raw = Buffer.from(padded, 'base64').toString('utf8');
    const payload = JSON.parse(raw);
    return payload;
  } catch {
    return null;
  }
}

function authMiddleware() {
  return function authenticate(req, res, next) {
    const authHeader = req.headers.authorization || '';
    if (!authHeader.startsWith('Bearer ')) {
      return respondError(res, 'unauthorized', 'Missing bearer token.', [{ field: 'authorization', reason: 'missing_bearer_token' }], 401);
    }

    const token = authHeader.slice('Bearer '.length).trim();
    const claims = decodeTokenPayload(token);

    if (!claims || typeof claims !== 'object') {
      return respondError(res, 'unauthorized', 'Invalid bearer token.', [{ field: 'authorization', reason: 'invalid_token' }], 401);
    }

    const nowEpoch = Math.floor(Date.now() / 1000);
    if (typeof claims.exp !== 'number' || claims.exp <= nowEpoch) {
      return respondError(res, 'unauthorized', 'Token is expired or missing exp claim.', [{ field: 'authorization', reason: 'expired_or_missing_exp' }], 401);
    }

    if (typeof claims.sub !== 'string' || !claims.sub || typeof claims.tenant_id !== 'string' || !claims.tenant_id) {
      return respondError(res, 'unauthorized', 'Token is missing required claims.', [{ field: 'authorization', reason: 'missing_required_claims' }], 401);
    }

    req.auth = {
      sub: claims.sub,
      tenant_id: claims.tenant_id,
      scopes: Array.isArray(claims.scopes) ? claims.scopes : [],
      role_ids: Array.isArray(claims.role_ids) ? claims.role_ids : [],
    };

    return next();
  };
}

function requireScopes(requiredScopes = []) {
  return function authorize(req, res, next) {
    const tenantHeader = req.headers['x-tenant-id'];
    if (typeof tenantHeader !== 'string' || !tenantHeader.trim()) {
      return respondError(res, 'forbidden', 'Missing tenant context header.', [{ field: 'x-tenant-id', reason: 'missing_tenant_context' }], 403);
    }

    if (tenantHeader.trim() !== req.auth?.tenant_id) {
      return respondError(res, 'forbidden', 'Tenant context mismatch.', [{ field: 'x-tenant-id', reason: 'tenant_mismatch' }], 403);
    }

    const principalScopes = new Set(req.auth?.scopes || []);
    const missing = requiredScopes.filter((scope) => !principalScopes.has(scope));

    if (missing.length > 0) {
      return respondError(
        res,
        'forbidden',
        'Missing required scope for this operation.',
        missing.map((scope) => ({ field: 'scopes', reason: `missing_${scope}` })),
        403,
      );
    }

    return next();
  };
}

module.exports = {
  authMiddleware,
  requireScopes,
};
