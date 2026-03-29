const crypto = require('crypto');
const { respondError } = require('./response-wrapper');

const recordStore = new Map();
const WRITE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

function fingerprintRequest(req) {
  return crypto
    .createHash('sha256')
    .update(JSON.stringify({
      body: req.body || null,
      query: req.query || null,
    }))
    .digest('hex');
}

function idempotencyMiddleware() {
  return function idempotency(req, res, next) {
    if (!WRITE_METHODS.has(req.method.toUpperCase())) return next();

    const key = req.headers['idempotency-key'];
    if (typeof key !== 'string' || !key.trim()) {
      return respondError(
        res,
        'validation_error',
        'One or more fields are invalid.',
        [{ field: 'idempotency_key', reason: 'required_for_write_operations' }],
        422,
      );
    }

    const routeKey = `${req.auth?.tenant_id || 'unknown'}:${req.method.toUpperCase()}:${req.path}:${key.trim()}`;
    const fingerprint = fingerprintRequest(req);
    const existing = recordStore.get(routeKey);

    if (existing) {
      if (existing.fingerprint !== fingerprint) {
        return respondError(
          res,
          'conflict',
          'Idempotency key was already used with a different payload.',
          [{ field: 'idempotency_key', reason: 'idempotency_key_payload_mismatch' }],
          409,
        );
      }

      res.status(existing.status).json({
        ...existing.body,
        meta: {
          ...(existing.body.meta || {}),
          request_id: req.request_id,
          idempotency: {
            replayed: true,
          },
        },
      });
      return;
    }

    const originalJson = res.json.bind(res);
    res.json = (payload) => {
      recordStore.set(routeKey, {
        fingerprint,
        status: res.statusCode,
        body: payload,
      });
      return originalJson(payload);
    };

    next();
  };
}

module.exports = {
  idempotencyMiddleware,
};
