'use strict';

const express      = require('express');
const helmet       = require('helmet');
const cors         = require('cors');
const cookieParser = require('cookie-parser');
const routes  = require('./routes');
const { requestIdMiddleware }    = require('./middleware/request-id');
const { observabilityMiddleware } = require('./middleware/observability');
const { rateLimitHook }          = require('./middleware/rate-limit-hook');
const { respondError }           = require('./middleware/response-wrapper');
const { authMiddleware }         = require('./middleware/auth-rbac');
const { auditMiddleware }        = require('./middleware/audit-log');
const { idempotencyMiddleware }  = require('./middleware/idempotency');
const { buildRuntimeConfig }     = require('./config/runtime-config');
const logger = require('./middleware/logger');

// ── B-004: Production fail-fast ───────────────────────────────────────────────
if (process.env.NODE_ENV === 'production') {
  // JWT_PUBLIC_KEY_URL is only required for RS256; HS256 uses JWT_SECRET instead.
  // DATABASE_URL is required; REDIS_URL degrades gracefully to ioredis-mock if absent.
  const required = ['JWT_ISSUER', 'JWT_AUDIENCE', 'DATABASE_URL'];
  const missing = required.filter((k) => !process.env[k]);
  if (missing.length > 0) {
    console.error(`[FATAL] Missing required env vars: ${missing.join(', ')}. Refusing to start.`);
    process.exit(1);
  }
}

const app = express(); // nosemgrep: javascript.express.security.audit.express-check-csurf-middleware-usage — CSRF does not apply to JWT Bearer + SameSite=Strict cookie auth
const runtimeConfig = buildRuntimeConfig();
app.locals.runtimeConfig = runtimeConfig;
app.locals.logger = logger;

// ── Security headers (C3 — helmet) ───────────────────────────────────────────
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc:  ["'self'"],
      styleSrc:   ["'self'", "'unsafe-inline'"],
      imgSrc:     ["'self'", 'data:'],
      connectSrc: ["'self'"],
    },
  },
  hsts: { maxAge: 31536000, includeSubDomains: true },
}));

// ── CORS — explicit allowlist (C3) ────────────────────────────────────────────
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS || 'http://localhost:3001,http://localhost:3000')
  .split(',')
  .map((o) => o.trim())
  .filter(Boolean);

app.use(cors({
  origin: (origin, cb) => {
    // Allow requests with no origin (server-to-server, curl, Postman, tests)
    if (!origin || ALLOWED_ORIGINS.includes(origin)) return cb(null, true);
    cb(new Error(`CORS: origin '${origin}' not allowed`));
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'Accept', 'x-tenant-id', 'x-request-id', 'x-idempotency-key'],
  exposedHeaders: ['x-ratelimit-limit', 'x-ratelimit-remaining', 'x-ratelimit-reset'],
}));

// ── Raw body capture (HMAC webhook verification) ──────────────────────────────
app.use((req, res, next) => {
  let raw = '';
  req.on('data', (chunk) => { raw += chunk; });
  req.on('end', () => { req.rawBody = raw; });
  next();
});

app.use(express.json());
app.use(cookieParser());
app.use(requestIdMiddleware);
app.use(observabilityMiddleware({ logger }));

// ── Dev auth bootstrap (non-production only) ──────────────────────────────────
if (process.env.NODE_ENV !== 'production') {
  process.env.SKIP_JWT_VERIFICATION = 'true';
  const { SCOPES } = require('./config/rbac-scopes');
  const _th = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
  const DEV_TENANT_ID = '00000000-0000-0000-0000-000000000001';
  const _tp = Buffer.from(JSON.stringify({
    sub: 'dev-user-001', tenant_id: DEV_TENANT_ID,
    iss: 'crm-dev', aud: 'crm-api', exp: 4102444800,
    role: 'tenant_admin', role_ids: ['role-admin'],
    territory_ids: [], scopes: Object.values(SCOPES),
  })).toString('base64url');
  const DEV_TOKEN = `${_th}.${_tp}.${Buffer.from('dev').toString('base64url')}`;
  app.get('/dev-token', (req, res) => {
    res.json({ data: { token: DEV_TOKEN, tenant_id: DEV_TENANT_ID }, meta: {} });
  });
}

// ── Public probes — BEFORE auth middleware (Render health checker sends no auth) ─
app.get('/health', (req, res) => {
  res.status(200).json({
    status:  'ok',
    service: runtimeConfig.service.name,
    version: runtimeConfig.service.version,
    uptime:  Math.floor(process.uptime()),
  });
});

app.get('/ready', async (req, res) => {
  let dbOk = false;
  try {
    const { query } = require('./db/pool');
    await query('SELECT 1');
    dbOk = true;
  } catch {
    dbOk = false;
  }
  res.status(dbOk ? 200 : 503).json({
    status: dbOk ? 'ready' : 'not_ready',
    checks: { database: dbOk ? 'ok' : 'unreachable' },
  });
});

// ── Public auth routes (no JWT required) ─────────────────────────────────────
// register, forgot-password, reset-password, refresh are public by design.
// login (/sessions) is also public. Only logout (/sessions/current) requires auth.
const authPublicRouter = require('./routes/v1-auth.routes');
app.use('/api/v1/auth', (req, res, next) => {
  const PUBLIC_PATHS = ['/register', '/forgot-password', '/reset-password', '/refresh'];
  if (PUBLIC_PATHS.includes(req.path)) return authPublicRouter(req, res, next);
  return next();
});

app.use(authMiddleware());
app.use(rateLimitHook({}));
app.use(idempotencyMiddleware());
app.use(auditMiddleware({ strict: true }));

app.use('/api/v1', routes);

app.use((err, req, res, _next) => {
  if (err.message && err.message.startsWith('CORS:')) {
    return res.status(403).json({ error: { code: 'forbidden', message: err.message }, meta: {} });
  }
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return respondError(res, 'bad_request', 'Malformed JSON body.', [{ field: 'body', reason: 'invalid_json' }], 400);
  }
  logger.error({ event: 'unhandled_error', error: err.message, stack: err.stack });
  return respondError(res, 'internal_error', 'An unexpected error occurred.', [], 500);
});

module.exports = { app };
