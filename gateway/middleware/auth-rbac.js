const { respondError } = require('./response-wrapper');

function decodeJwtPayload(token) {
  try {
    const parts = token.split('.');
    const payloadPart = parts.length === 3 ? parts[1] : token;
    const normalized = payloadPart.replace(/-/g, '+').replace(/_/g, '/');
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
    const claims = decodeJwtPayload(token);

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

    req.auth = {
      sub: claims.sub,
      tenant_id: claims.tenant_id,
      scopes: Array.isArray(claims.scopes) ? claims.scopes.filter((s) => typeof s === 'string' && s) : [],
      role_ids: Array.isArray(claims.role_ids) ? claims.role_ids.filter((r) => typeof r === 'string' && r) : [],
      jti: typeof claims.jti === 'string' ? claims.jti : null,
    };

    return next();
  };
}

function requireScopes(requiredScopes = [], options = {}) {
  const requiredRoles = Array.isArray(options.requiredRoles) ? options.requiredRoles : [];

  return function authorize(req, res, next) {
    const tenantHeader = req.headers['x-tenant-id'];
    if (typeof tenantHeader !== 'string' || !tenantHeader.trim()) {
      return respondError(res, 'forbidden', 'Missing tenant context header.', [{ field: 'x-tenant-id', reason: 'missing_tenant_context' }], 403);
    }

    if (tenantHeader.trim() !== req.auth?.tenant_id) {
      return respondError(res, 'forbidden', 'Tenant context mismatch.', [{ field: 'x-tenant-id', reason: 'tenant_mismatch' }], 403);
    }

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

    return next();
  };
}

module.exports = {
  authMiddleware,
  requireScopes,
};
