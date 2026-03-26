const { respondError } = require('./response-wrapper');

function rateLimitHook({ evaluate }) {
  if (typeof evaluate !== 'function') {
    throw new Error('rateLimitHook requires an evaluate function');
  }

  return async function rateLimitMiddleware(req, res, next) {
    const outcome = await evaluate({
      path: req.path,
      method: req.method,
      subject: req.auth?.sub || 'anonymous',
      tenant_id: req.auth?.tenant_id || null,
      request_id: req.request_id,
    });

    if (!outcome || outcome.allowed !== false) {
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
