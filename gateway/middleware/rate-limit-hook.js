const { respondError } = require('./response-wrapper');

const buckets = new Map();
const WINDOW_MS = 60 * 1000;

function endpointLimit(method, path) {
  const key = `${method.toUpperCase()} ${path}`;
  if (/POST \/api\/v1\/(payments|emails|users|forecasts)/.test(key)) return 20;
  if (method.toUpperCase() === 'GET') return 300;
  return 120;
}

function localEvaluate({ path, method, subject, tenant_id }) {
  const limit = endpointLimit(method, path);
  const now = Date.now();
  const bucketKey = `${tenant_id || 'unknown'}:${subject}:${method.toUpperCase()}:${path}`;
  let bucket = buckets.get(bucketKey);

  if (!bucket || now >= bucket.resetAt) {
    bucket = {
      count: 0,
      resetAt: now + WINDOW_MS,
    };
  }

  bucket.count += 1;
  buckets.set(bucketKey, bucket);

  if (bucket.count <= limit) {
    return { allowed: true, limit, remaining: Math.max(limit - bucket.count, 0), reset_at: bucket.resetAt };
  }

  return {
    allowed: false,
    retry_after_seconds: Math.ceil((bucket.resetAt - now) / 1000),
    limit,
    remaining: 0,
    reset_at: bucket.resetAt,
  };
}

function rateLimitHook({ evaluate }) {
  const evaluator = typeof evaluate === 'function' ? evaluate : localEvaluate;

  return async function rateLimitMiddleware(req, res, next) {
    const outcome = await evaluator({
      path: req.path,
      method: req.method,
      subject: req.auth?.sub || 'anonymous',
      tenant_id: req.auth?.tenant_id || null,
      request_id: req.request_id,
    });

    if (!outcome || outcome.allowed !== false) {
      if (outcome && typeof outcome.limit === 'number') {
        res.setHeader('x-ratelimit-limit', String(outcome.limit));
        res.setHeader('x-ratelimit-remaining', String(outcome.remaining ?? 0));
        if (typeof outcome.reset_at === 'number') {
          res.setHeader('x-ratelimit-reset', String(Math.floor(outcome.reset_at / 1000)));
        }
      }
      return next();
    }

    if (typeof outcome.retry_after_seconds === 'number') {
      res.setHeader('retry-after', String(outcome.retry_after_seconds));
    }

    return respondError(
      res,
      'rate_limited',
      'Rate limit exceeded. Please retry later.',
      [{ field: 'request', reason: 'rate_limit_exceeded' }],
      429,
    );
  };
}

module.exports = {
  rateLimitHook,
};
