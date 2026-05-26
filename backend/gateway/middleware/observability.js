const crypto = require('crypto');

function generateTraceId() {
  return crypto.randomBytes(16).toString('hex');
}

function generateParentId() {
  return crypto.randomBytes(8).toString('hex');
}

function normalizeTraceId(incoming) {
  if (typeof incoming !== 'string') return null;
  const trace = incoming.trim().toLowerCase();
  return /^[a-f0-9]{32}$/.test(trace) ? trace : null;
}

// Parse W3C traceparent: 00-<trace-id>-<parent-id>-<flags>
function parseTraceparent(header) {
  if (typeof header !== 'string') return null;
  const parts = header.trim().split('-');
  if (parts.length !== 4 || parts[0] !== '00') return null;
  const traceId = parts[1];
  return /^[a-f0-9]{32}$/.test(traceId) ? traceId : null;
}

function observabilityMiddleware({ logger = console } = {}) {
  let inflight = 0;
  return function observe(req, res, next) {
    const startedAt = process.hrtime.bigint();

    // E-002: accept W3C traceparent first, fall back to x-trace-id, then generate
    const traceId = parseTraceparent(req.headers['traceparent'])
      || normalizeTraceId(req.headers['x-trace-id'])
      || generateTraceId();

    const parentId = generateParentId();
    const traceparent = `00-${traceId}-${parentId}-01`;

    req.trace_id = traceId;
    res.setHeader('x-trace-id', traceId);
    res.setHeader('traceparent', traceparent);
    inflight += 1;

    res.on('finish', () => {
      inflight = Math.max(inflight - 1, 0);
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
        inflight_requests: inflight,
        severity: res.statusCode >= 500 ? 'error' : 'info',
      });
    });

    next();
  };
}

module.exports = {
  observabilityMiddleware,
};
