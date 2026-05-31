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

// ── B-004: Production fail-fast — refuse to start with missing critical env vars ─
if (process.env.NODE_ENV === 'production') {
  const required = ['JWT_ISSUER', 'JWT_AUDIENCE', 'JWT_PUBLIC_KEY_URL', 'DATABASE_URL'];
  const missing = required.filter((k) => !process.env[k]);
  if (missing.length > 0) {
    // eslint-disable-next-line no-console
    console.error(`[FATAL] Missing required env vars: ${missing.join(', ')}. Refusing to start.`);
    process.exit(1);
  }
}

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

// ── Dev auth bootstrap (non-production only) ──────────────────────────────────
// Sets SKIP_JWT_VERIFICATION so the auth middleware skips signature checks.
// Mounts /dev-token before auth middleware so it needs no Bearer token.
if (process.env.NODE_ENV !== 'production') {
  process.env.SKIP_JWT_VERIFICATION = 'true';
  const { SCOPES } = require('./config/rbac-scopes');
  const _th = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
  const _tp = Buffer.from(JSON.stringify({
    sub: 'dev-user-001', tenant_id: 'tenant-dev-001',
    iss: 'crm-dev', aud: 'crm-api', exp: 4102444800,
    role: 'tenant_admin', role_ids: ['role-admin'],
    territory_ids: [], scopes: Object.values(SCOPES),
  })).toString('base64url');
  const DEV_TOKEN = `${_th}.${_tp}.${Buffer.from('dev').toString('base64url')}`;
  app.get('/dev-token', (req, res) => {
    res.json({ data: { token: DEV_TOKEN, tenant_id: 'tenant-dev-001' }, meta: {} });
  });
}

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
