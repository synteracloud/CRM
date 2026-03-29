const crypto = require('crypto');

function generateTraceId() {
  return crypto.randomBytes(16).toString('hex');
}

function normalizeTraceId(incoming) {
  if (typeof incoming !== 'string') return null;
  const trace = incoming.trim().toLowerCase();
  return /^[a-f0-9]{32}$/.test(trace) ? trace : null;
}

function observabilityMiddleware({ logger = console } = {}) {
  return function observe(req, res, next) {
    const startedAt = process.hrtime.bigint();
    const incomingTrace = req.headers['x-trace-id'];
    const traceId = normalizeTraceId(incomingTrace) || generateTraceId();

    req.trace_id = traceId;
    res.setHeader('x-trace-id', traceId);

    res.on('finish', () => {
      const elapsedNs = process.hrtime.bigint() - startedAt;
      const elapsedMs = Number(elapsedNs / 1000000n);
      logger.info?.({
        event: 'http.request.completed',
        request_id: req.request_id,
        trace_id: req.trace_id,
        tenant_id: req.auth?.tenant_id || null,
        actor_id: req.auth?.sub || null,
        method: req.method,
        route: req.path,
        status_code: res.statusCode,
        duration_ms: elapsedMs,
      });
    });

    next();
  };
}

module.exports = {
  observabilityMiddleware,
};
