Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: Shared

# BACKEND_ARCHITECTURE.md
> Source: backend/gateway/app.js, backend/gateway/server.js, backend/gateway/middleware/*, backend/gateway/config/*, backend/services/app.py, backend/services/bootstrap.py, backend/services/db/__init__.py

---

## 1. Overall Architecture Pattern

**Pakistan CRM** uses a **3-tier architecture** with an Express.js API gateway fronting a FastAPI Python service layer.

```
Browser / Mobile (static HTML frontend)
    │  Bearer JWT + x-tenant-id header
    │
Express.js API Gateway (Node.js — backend/gateway/)
    │  Runs on PORT env var (default 3000)
    │  Handles: auth, RBAC, rate limiting, idempotency, audit logging, CORS
    │  Routes: /api/v1/* → 44 route group files
    │
    ├─ Direct handlers (in-memory + PostgreSQL pool via gateway/db/pool)
    │    Used for: auth, leads, contacts, accounts, opportunities, etc.
    │
    └─ FastAPI Proxy (HTTP to localhost:5002 / FOLLOWUP_SERVICE_URL)
         Used for: followup enforcement, collections, activities, conversations,
                   sync, territories, workflows, partners, AI, campaigns, cases, inbox
         FastAPI Python Services (backend/services/)
             │  Uvicorn on port 5002
             │
             SQLAlchemy ORM
             │
             PostgreSQL 14 (18 domain schemas) + Redis (rate limiting, OTP, JTI blocklist)
```

---

## 2. Service Layer Diagram

```
                    ┌─────────────────────────────────┐
                    │  Express.js Gateway (port 3000)  │
                    │  backend/gateway/                │
                    │                                  │
                    │  Middleware stack (in order):    │
                    │  1. Helmet (security headers)    │
                    │  2. CORS (explicit allowlist)    │
                    │  3. Raw body capture (webhooks)  │
                    │  4. express.json()               │
                    │  5. cookieParser                 │
                    │  6. requestIdMiddleware          │
                    │  7. observabilityMiddleware      │
                    │  8. (public auth paths bypass)   │
                    │  9. authMiddleware (JWT)         │
                    │  10. rateLimitHook (Redis)       │
                    │  11. idempotencyMiddleware       │
                    │  12. auditMiddleware             │
                    │  13. /api/v1 routes              │
                    └──────────────┬──────────────────┘
                                   │
              ┌────────────────────┴──────────────────────┐
              │                                           │
    ┌─────────▼──────────┐                    ┌──────────▼─────────┐
    │  PostgreSQL Pool   │                    │  FastAPI Services  │
    │  (gateway/db/)     │                    │  port 5002         │
    │  Direct SQL for    │                    │  backend/services/ │
    │  auth, leads,      │                    │                    │
    │  contacts, etc.    │                    │  Routers:          │
    └────────────────────┘                    │  /internal/*       │
                                              │  /api/v1/*         │
                                              └──────────┬─────────┘
                                                         │
                                              ┌──────────▼─────────┐
                                              │  SQLAlchemy ORM    │
                                              │  sessionmaker      │
                                              │  pool_pre_ping     │
                                              └──────────┬─────────┘
                                                         │
                                              ┌──────────▼─────────┐
                                              │  PostgreSQL 14     │
                                              │  18 domain schemas │
                                              └────────────────────┘
```

---

## 3. Module Organisation

### backend/gateway/ — Express.js API gateway

| Directory | Purpose |
|---|---|
| `gateway/routes/` | 44 v1-*.routes.js files — one per domain (leads, contacts, cases, etc.) |
| `gateway/middleware/` | auth.js, auth-rbac.js, audit-log.js, idempotency.js, logger.js, observability.js, rate-limit-hook.js, request-id.js, request-validation.js, response-wrapper.js, jti-blocklist.js, transport-forward.js |
| `gateway/config/` | rbac-scopes.js (SCOPES + ROLE_SCOPES), redis-client.js, env-config.js, runtime-config.js, feature-flags.js |
| `gateway/db/` | PostgreSQL pool, repositories per domain |
| `gateway/types/` | api.js (CANONICAL_ERROR_CODES) |
| `gateway/validators/` | Request validation middleware |
| `gateway/data/` | In-memory seed data (dev/stub mode) |
| `gateway/entities/` | Entity definitions for gateway layer |

### backend/services/ — FastAPI Python service layer

| Directory | Purpose |
|---|---|
| `services/followup/` | Follow-up enforcement engine — scheduling, escalation, next-action |
| `services/collections/` | Invoice/payment/reconciliation lifecycle |
| `services/activity/` | Activity timeline control engine |
| `services/conversation/` | WhatsApp message classification + conversation state |
| `services/sync/` | Offline-first sync command queue |
| `services/activation/` | Tenant pipeline seeding on registration |
| `services/territories/` | Territory assignment and routing |
| `services/workflows/` | Workflow definition + execution |
| `services/partners/` | Partner + commission management |
| `services/ai/` | AI scoring (rule-based), churn prediction, CLV, copilot |
| `services/campaigns/` | Campaign + segment management |
| `services/cases/` | Case/ticket management |
| `services/inbox/` | Shared inbox conversations |
| `services/core/` | Cross-cutting: idempotency ledger, retry executor, concurrency controller, transaction manager, recovery queue, execution control plane |
| `services/auth/` | JWT validation dependency for FastAPI routes |
| `services/summary/` | Daily WhatsApp summary scheduler |
| `services/db/` | SQLAlchemy engine, sessionmaker, ORM models |

### backend/src/ — 34 domain modules (Python, domain-logic layer)

34 domain modules under `src/` provide Pydantic entities, service logic, and repositories. Each module follows the pattern: `api.py` (FastAPI router), `services.py` (business logic), `entities.py` (Pydantic schemas + DB models).

---

## 4. Middleware Stack

Middleware runs on every authenticated request in this order (from backend/gateway/app.js):

| Order | Middleware | Source | Purpose |
|---|---|---|---|
| 1 | Helmet | helmet npm package | Security headers: CSP, HSTS (1yr + subdomains), X-Frame-Options, etc. |
| 2 | CORS | cors npm package | Explicit origin allowlist from ALLOWED_ORIGINS env var. Credentials: true. |
| 3 | Raw body capture | inline | Captures raw request body string for HMAC webhook signature verification |
| 4 | express.json() | express | JSON body parsing |
| 5 | cookieParser | cookie-parser | Refresh token cookie parsing |
| 6 | requestIdMiddleware | middleware/request-id.js | Assigns unique request_id to every request |
| 7 | observabilityMiddleware | middleware/observability.js | W3C traceparent propagation; structured JSON logging of completed requests |
| 8 | Auth bypass | inline | Public auth paths (/login, /register, /forgot-password, /reset-password, /refresh, /sessions) skip auth middleware |
| 9 | authMiddleware | middleware/auth-rbac.js | JWT validation (HS256/RS256), exp/nbf/sub/tenant_id/iss/aud claim validation, JTI revocation check |
| 10 | rateLimitHook | middleware/rate-limit-hook.js | Redis sliding-window rate limiting. GET: 300/min; POST payments/emails/users/forecasts: 20/min; audit: 10/min; other writes: 120/min |
| 11 | idempotencyMiddleware | middleware/idempotency.js | Idempotency-Key header required on all write methods; replay cached responses; reject key reuse with payload drift |
| 12 | auditMiddleware | middleware/audit-log.js | Hash-chain audit log appended on mutating requests matching ACTIONS_BY_ROUTE map |
| 13 | /api/v1 routes | routes/index.js | Domain route handlers |
| 14 | Global error handler | inline | CORS errors → 403; JSON parse errors → 400; unhandled → 500 |

### CORS Configuration (from app.js)
- **Origins**: `ALLOWED_ORIGINS` env var (comma-separated). Defaults: `http://localhost:3001,http://localhost:3000`
- **Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS
- **Allowed headers**: Content-Type, Authorization, Accept, x-tenant-id, x-request-id, x-idempotency-key, idempotency-key, Idempotency-Key
- **Exposed headers**: x-ratelimit-limit, x-ratelimit-remaining, x-ratelimit-reset
- **Credentials**: true (refresh token cookies)

### Rate Limiting Details (from middleware/rate-limit-hook.js)
- **Backend**: Redis sliding window. Falls back to in-process Map if Redis unavailable (fail open).
- **Bucket key**: `rl:{tenant_id}:{user_sub}:{METHOD}:{canonical_path}`
- **Window**: 60 seconds
- **Limits by endpoint type**:
  - GET requests: 300 per window
  - POST /payments, /emails, /users, /forecasts: 20 per window
  - POST /audit: 10 per window
  - All other writes: 120 per window
- **Response headers**: x-ratelimit-limit, x-ratelimit-remaining, x-ratelimit-reset
- **Exceeded**: 429 with Retry-After header

---

## 5. Configuration Management

### Gateway (Node.js)
**Source**: `backend/gateway/config/env-config.js` and `config/runtime-config.js`

Key env vars consumed by gateway:

| Env Var | Required | Default | Purpose |
|---|---|---|---|
| NODE_ENV | No | development | Enables/disables dev-only features |
| PORT | No | 3000 | HTTP listen port |
| LOG_LEVEL | No | info | debug/info/warn/error |
| SERVICE_NAME | Yes (prod) | crm-gateway | Logged with every entry |
| SERVICE_VERSION | Yes (prod) | dev | Service version tag |
| REGION | Yes (prod) | local | Deployment region tag |
| JWT_SECRET | No (dev) | — | HS256 signing secret (required in production with HS256) |
| JWT_PUBLIC_KEY | No | — | RS256 public key PEM (alternative to JWT_SECRET) |
| JWT_ISSUER | Yes (prod) | crm-local | Expected `iss` claim |
| JWT_AUDIENCE | Yes (prod) | crm-api | Expected `aud` claim |
| DATABASE_URL | Yes (prod) | — | PostgreSQL connection string |
| REDIS_URL | No | — | Redis connection URL; falls back to ioredis-mock if absent |
| ALLOWED_ORIGINS | No | localhost:3001,3000 | CORS origin allowlist |
| SENDGRID_API_KEY | No | — | Enables live email sending (OTP, welcome) |
| FOLLOWUP_SERVICE_URL | No | http://localhost:5002 | FastAPI service base URL |
| SKIP_JWT_VERIFICATION | No | — | Dev bypass; blocked in production |
| JAZZCASH_STUB_MODE | No | true | Keeps JazzCash in stub mode |
| EASYPAISA_STUB_MODE | No | true | Keeps Easypaisa in stub mode |
| FEATURE_FLAGS | No | {} | JSON object of feature flag overrides |
| RUNTIME_CONFIG_OVERRIDES | No | {} | Overrides for PORT/LOG_LEVEL/REGION only |

**Production fail-fast**: If NODE_ENV=production and JWT_ISSUER, JWT_AUDIENCE, or DATABASE_URL are missing, the gateway exits with a fatal error on startup.

### FastAPI Services (Python)
**Source**: `backend/services/db/__init__.py`, `backend/services/app.py`

| Env Var | Default | Purpose |
|---|---|---|
| DATABASE_URL | postgresql+psycopg2://crm:changeme@localhost:5432/crm | SQLAlchemy connection string |
| JWT_SECRET_KEY | dev-secret-change-in-production | HS256 verification in FastAPI layer |
| JWT_ISSUER | (empty) | Expected iss claim for FastAPI JWT validation |
| JWT_AUDIENCE | (empty) | Expected aud claim |
| LOG_LEVEL | INFO | Python logging level |
| SERVICE_NAME | crm-python-services | Service name for log output |
| DAILY_SUMMARY_ENABLED | true | Enable daily WhatsApp summary job |
| DAILY_SUMMARY_UTC_HOUR | 3 | UTC hour for daily summary (03:00 UTC = 08:00 PKT) |
| DAILY_SUMMARY_OWNER_PHONE | (empty) | Phone for daily summary recipient |
| DAILY_SUMMARY_TENANT_ID | tenant-dev-001 | Tenant for daily summary |
| IDEMPOTENCY_TTL_SECONDS | 86400 | Python idempotency record TTL |
| IDEMPOTENCY_EVICT_INTERVAL | 3600 | Eviction sweep interval |
| MIGRATE_SECRET | (empty) | Secret for POST /internal/migrate endpoint |

---

## 6. Startup Sequence

### Gateway startup (backend/gateway/server.js → app.js)
1. `buildRuntimeConfig()` — validates and loads env config; fails fast if required vars missing in production
2. Helmet, CORS, body parsers, cookie parser mounted
3. Observability and request ID middleware mounted
4. Dev token endpoint mounted (non-production only)
5. `/health` and `/ready` probes mounted (before auth middleware)
6. Public auth router mounted for `/api/v1/auth` public paths
7. `authMiddleware()` mounted (all subsequent routes require JWT)
8. `rateLimitHook()` mounted
9. `idempotencyMiddleware()` mounted
10. `auditMiddleware()` mounted
11. `/api/v1` domain routes mounted (44 route files)
12. Global error handler mounted
13. `app.listen(port)` — gateway accepts connections

### FastAPI startup (backend/services/app.py lifespan)
1. JSON logging configured
2. FastAPI app created with lifespan context manager
3. On lifespan startup:
   a. `startup()` called — initialises `GlobalIdempotencyLedger`, starts `EvictionWorker` daemon thread
   b. Service singletons instantiated: `ActivityControlEngine`, `FollowupEnforcementEngine`, `CollectionsService`, `SyncService`
   c. Internal HTTP routers injected with singletons via `set_*()` calls
   d. Non-test: `ActivationOrchestrator` and `ExecutionControlPlane` instantiated; public routers injected
   e. Background `_overdue_scanner` asyncio task started (60-second polling cycle — marks overdue followup tasks)
   f. Background `_daily_summary_scheduler` asyncio task started (daily WhatsApp summary at DAILY_SUMMARY_UTC_HOUR)
4. Routers mounted: internal (/internal/*) and public (/api/v1/*)
5. Exception handlers registered
6. Uvicorn accepts connections on port 5002

---

## 7. Dependency Injection Pattern

### Gateway (Express.js)
- No formal DI framework. Modules use `require()` singletons.
- Service singletons are module-level variables injected via exported `set_*()` functions.
- Example: `set_followup_engine(engine)` called in lifespan, imported by route handlers.

### FastAPI (Python)
- FastAPI native dependency injection via `Depends()`.
- `get_db()` — yields SQLAlchemy `Session` from `sessionmaker`; closes on exit.
- `get_current_user()` — validates Bearer JWT via `python-jose`, returns `TokenClaims` dataclass.
- Route handlers declare `db: Session = Depends(get_db)` and `user: TokenClaims = Depends(get_current_user)`.

```python
# Pattern used across all FastAPI route handlers:
@router.get("/api/v1/cases")
def list_cases(
    db: Session = Depends(get_db),
    user: TokenClaims = Depends(get_current_user),
):
    ...
```

---

## 8. Error Handling Architecture

### Gateway error format (from middleware/response-wrapper.js + types/api.js)

**Success response:**
```json
{
  "data": { ... },
  "meta": { "request_id": "uuid" }
}
```

**Error response:**
```json
{
  "error": {
    "code": "validation_error",
    "message": "Human-readable description.",
    "details": [
      { "field": "email", "reason": "required" }
    ]
  },
  "meta": { "request_id": "uuid" }
}
```

**CANONICAL_ERROR_CODES mapping (types/api.js):**
| Code | HTTP Status |
|---|---|
| bad_request | 400 |
| unauthorized | 401 |
| forbidden | 403 |
| not_found | 404 |
| conflict | 409 |
| validation_error | 422 |
| rate_limited | 429 |
| internal_error | 500 |
| service_unavailable | 503 |

**Error propagation:**
1. Route handler calls `respondError(res, code, message, details, statusOverride)`
2. `response-wrapper.js` resolves HTTP status from CANONICAL_ERROR_CODES or statusOverride
3. JSON response written with `{ error: { code, message, details }, meta: { request_id } }`
4. Global error handler catches uncaught Express errors: CORS → 403; JSON parse → 400; all others → 500

### FastAPI error format (from services/app.py exception handlers)

Same envelope shape. HTTPException handler maps status codes:
```json
{
  "error": { "code": "not_found", "message": "..." },
  "meta": { "request_id": "generated-uuid" }
}
```

Unhandled exceptions → 500 `internal_error`.

---

## 9. Observability

### Logging (both tiers)
- **Gateway**: Pure Node.js structured JSON logger (`middleware/logger.js`). One JSON object per line to stdout.
  - Fields: `timestamp` (ISO-8601 UTC), `level`, `service`, `env`, plus caller-supplied fields.
  - On every completed request: `event`, `request_id`, `trace_id`, `tenant_id`, `actor_id`, `method`, `route`, `status_code`, `duration_ms`, `inflight_requests`, `severity`.
- **FastAPI**: `_JsonFormatter` Python logging formatter. Same JSON-per-line stdout approach.
  - Fields: `timestamp`, `level`, `service`, `env`, `logger`, `message`, `exception` (if error).

### Tracing (W3C traceparent — from middleware/observability.js)
- Gateway accepts `traceparent` (W3C) or `x-trace-id` headers; generates a random 32-hex trace ID if neither present.
- Trace ID propagated via `x-trace-id` and `traceparent` response headers.
- `trace_id` included in all log entries.
- No distributed tracing backend configured (Jaeger/Zipkin: CONFIRMED ABSENT — no Jaeger/Zipkin/OTEL dependencies in package.json or requirements.txt; trace_id is log-only in C6). C7 observability sprint planned if needed.

### Metrics
- No Prometheus/Datadog metrics endpoint found in code.
- Inflight request count tracked in-process by observability middleware (`inflight_requests` logged per request).
- Rate limit headers (`x-ratelimit-*`) expose per-user consumption.
- `/ready` endpoint performs DB liveness check (SELECT 1).

### Audit Log (from middleware/audit-log.js)
- In-memory hash-chain audit log (in-process). Written to DB via audit_compliance_db schema.
- Events recorded for 20+ mutation routes (see ACTIONS_BY_ROUTE map in audit-log.js).
- Non-strict mode (`strict: false`) — mutations without audit mapping are allowed through (not blocked).

---

*End BACKEND_ARCHITECTURE.md*
