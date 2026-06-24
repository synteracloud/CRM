Status: Draft
Authority Level: High
Last Reviewed: 2026-06-22
Owner: Shared

# BACKEND_ARCHITECTURE_REPORT.md
> Architecture discovery findings from Phase 2 Backend Authority Capture

---

## 1. Architecture Pattern Confirmed

**Type:** 3-tier with internal service mesh pattern

```
[Static HTML Frontend] 
         ↓ HTTP/S
[Express.js API Gateway — port 3000]
    ↙ direct SQL (pg pool)    ↘ HTTP proxy (fetchJson/postJson)
[PostgreSQL 14 + Redis]    [FastAPI Python Services — port 5002]
                                        ↓ SQLAlchemy
                                  [PostgreSQL 14]
```

**Key finding:** Both tiers (gateway and FastAPI) connect directly to PostgreSQL. The gateway uses the Node.js `pg` package directly for auth routes and some domain routes. FastAPI services use SQLAlchemy ORM. There is no shared ORM layer or service abstraction between the two tiers — each operates on its own DB connection pool.

---

## 2. Gateway Architecture

**Runtime:** Node.js, Express 4.x
**Port:** 3000 (configurable via PORT env var)
**Route files:** 44 v1-*.routes.js files in `backend/gateway/routes/`
**Startup:** `backend/gateway/server.js` → `buildRuntimeConfig()` → `app.listen(port)`
**Middleware count:** 14 middleware items applied in order

**Middleware order (confirmed from app.js):**
1. `requestId` — generates UUID per request
2. `helmet` — security headers (CSP, HSTS, XFO)
3. `cors` — from ALLOWED_ORIGINS env var
4. `express.json` (10mb limit)
5. `rawBodyCapture` — saves raw body for webhook HMAC verification
6. `express.urlencoded` (extended: true)
7. `cookieParser`
8. `rateLimitHook` — Redis sliding window
9. `observabilityMiddleware` — W3C traceparent, structured log on response
10. `idempotencyMiddleware` — Idempotency-Key enforcement
11. Auth bypass for public paths (`/auth/login`, `/auth/register`, etc.)
12. `authMiddleware()` — JWT validation
13. Routes
14. Global error handler

**Internal service proxy pattern:** Route handlers use `fetchJson(url)` and `postJson(url, body)` helper functions to proxy calls to the FastAPI service layer at `GATEWAY_UPSTREAM_BASE_URL` (default: `http://localhost:5002`).

---

## 3. FastAPI Service Architecture

**Runtime:** Python 3.x, FastAPI + Uvicorn
**Port:** 5002 (configurable via PORT env var)
**Entry:** `backend/services/app.py`
**Router mount points:**
- `/internal/*` — all internal routers (called only by gateway)
- `/api/v1/*` — public routers (intended for direct client calls in some cases)

**Service singletons (instantiated on startup):**
- `FollowupEnforcementEngine`
- `CollectionsService`
- `ActivityControlEngine`
- `ConversationService`
- `SyncService`
- `ActivationOrchestrator`
- `ExecutionControlPlane`
- `AIService`

**Domain modules (34):** in `backend/src/` — each follows api.py / services.py / entities.py pattern

**DI pattern:** `Depends(get_db)` for SQLAlchemy sessions; `Depends(get_current_user)` for TokenClaims

---

## 4. Configuration Architecture

**Gateway config validation:** `env-config.js` — validates required env vars in production, blocks startup if missing (SERVICE_NAME, SERVICE_VERSION, REGION, JWT_ISSUER, JWT_AUDIENCE)

**Runtime config:** `buildRuntimeConfig()` — loads env, applies safe overrides (PORT, LOG_LEVEL, REGION only). Sensitive keys (JWT_SECRET, DATABASE_URL, REDIS_URL) cannot appear in RUNTIME_CONFIG_OVERRIDES.

**Feature flags:** `feature_flag_db.feature_flags` table. Safe-by-default = OFF (default_value=false). Evaluated by `ff:{tenant_id}:{flag_key}` Redis cache (when available).

---

## 5. Dual-Tier Routing (Key Finding)

Some domains have both a gateway route handler AND a FastAPI public route handler at the same URL path:
- Gateway handles: auth, some lead operations (direct SQL)
- FastAPI handles: cases, inbox, AI, followups, collections (proxied via gateway)
- Both handle: depends on GATEWAY_UPSTREAM_BASE_URL — if set, gateway proxies to FastAPI; if unset, gateway may handle direct

**Risk:** Route handling ownership is not always clear from configuration alone. Callers must verify where business logic actually executes for each route.

---

## 6. Key Architecture Decisions

| Decision | Implementation |
|---|---|
| Tenancy model | Application-level tenant_id on every table; not DB RLS |
| Token strategy | Stateless JWT; refresh token DB-persisted |
| Idempotency | Two layers: gateway in-memory Map + FastAPI GlobalIdempotencyLedger |
| Audit log | In-memory hash-chain (strict=false, not DB-backed in gateway) |
| Feature flags | DB table + Redis cache; safe-by-default |
| Cross-schema FK | NOT USED — application-layer only |
| Soft delete | Not universal — leads use repo.softDelete(); most entities use status flags |
| Rate limiting | Redis sliding window; fail-open on Redis unavailability |

---

## 7. Architecture Gaps Found

| Gap | Risk | Location |
|---|---|---|
| JTI blocklist in-memory only | Revoked tokens accepted by other gateway instances | gateway/middleware/jti-blocklist.js |
| Dual-tier routing ambiguity | Business logic location unclear for some routes | app.js + v1-*.routes.js |
| No message broker | Event-driven patterns are in-process only; no durability guarantees | services/app.py |
| Outbox table with no publisher | DB events never dispatched | transaction_db.outbox_event |
| No PostgreSQL RLS | All tenant isolation is application-layer | All DB schemas |
| AI models: rule-based only | M-01 AI page is advisory-only shell | services/ai/ |

---

*End BACKEND_ARCHITECTURE_REPORT.md*
