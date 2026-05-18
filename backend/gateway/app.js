const express = require('express');
const routes = require('./routes');
const { requestIdMiddleware } = require('./middleware/request-id');
const { observabilityMiddleware } = require('./middleware/observability');
const { rateLimitHook } = require('./middleware/rate-limit-hook');
const { respondError } = require('./middleware/response-wrapper');
const { authMiddleware } = require('./middleware/auth-rbac');
const { auditMiddleware } = require('./middleware/audit-log');
const { idempotencyMiddleware } = require('./middleware/idempotency');
const { buildRuntimeConfig } = require('./config/runtime-config');
// P-022 — structured JSON logger (replaces app.locals.logger = console)
const logger = require('./middleware/logger');

const app = express();
const runtimeConfig = buildRuntimeConfig();

app.locals.runtimeConfig = runtimeConfig;
app.locals.logger = logger;

// ── Raw body capture (needed for HMAC signature verification in webhook routes) ─
app.use((req, res, next) => {
  let raw = '';
  req.on('data', (chunk) => { raw += chunk; });
  req.on('end', () => { req.rawBody = raw; });
  next();
});

app.use(express.json());
app.use(requestIdMiddleware);
// Pass the structured logger to observability middleware so request logs are JSON
app.use(observabilityMiddleware({ logger }));
app.use(authMiddleware());
app.use(rateLimitHook({}));
app.use(idempotencyMiddleware());
app.use(auditMiddleware({ strict: true }));

// ── Health + readiness probes (P-022) — mounted BEFORE /api/v1 and before auth ──
// These are public; no auth required.  Added here so they bypass all middleware.
app.get('/health', (req, res) => {
  res.status(200).json({
    status:  'ok',
    service: runtimeConfig.service.name,
    version: runtimeConfig.service.version,
    uptime:  Math.floor(process.uptime()),
  });
});

app.get('/ready', async (req, res) => {
  // Readiness probe — check DB connectivity.
  let dbOk = false;
  try {
    const { query } = require('./db/pool');
    await query('SELECT 1');
    dbOk = true;
  } catch {
    dbOk = false;
  }

  const status = dbOk ? 200 : 503;
  res.status(status).json({
    status: dbOk ? 'ready' : 'not_ready',
    checks: { database: dbOk ? 'ok' : 'unreachable' },
  });
});

app.use('/api/v1', routes);

app.use((err, req, res, next) => {
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return respondError(res, 'bad_request', 'Malformed JSON body.', [{ field: 'body', reason: 'invalid_json' }], 400);
  }

  logger.error({ event: 'unhandled_error', error: err.message, stack: err.stack });
  return respondError(res, 'internal_error', 'An unexpected error occurred.', [], 500);
});

module.exports = { app };
