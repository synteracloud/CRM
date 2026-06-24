Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: Shared

# API_CONTRACT.md
> Source: backend/gateway/app.js, backend/gateway/routes/v1-*.routes.js (44 files), backend/gateway/middleware/*, backend/gateway/config/rbac-scopes.js
> All API_INVENTORY.md entries are incorporated by reference. This document adds depth on contract patterns.

---

## 1. Gateway Routing Pattern

The Express.js gateway (`backend/gateway/`) handles all inbound API traffic. Routes are mounted at `/api/v1/*` and map to 44 domain route files.

**Route mounting (from app.js):**
```
app.use('/api/v1', routes);   // routes = require('./routes') — aggregates all 44 route files
```

**How Express routes to FastAPI:**
- Most routes in the gateway execute **directly** using an in-memory store or a PostgreSQL pool (`gateway/db/pool`) — they do not proxy to FastAPI.
- Routes that proxy to FastAPI use `http.request()` or `postJson()` to call `FOLLOWUP_SERVICE_URL` (default `http://localhost:5002`).
- FastAPI public routes are mounted at the same paths (e.g. `/api/v1/cases`, `/api/v1/inbox`) — the gateway's transport-forward middleware routes matching paths to the FastAPI service.
- Internal FastAPI routes (`/internal/*`) are called directly by the gateway and are not exposed to the public internet.

**Dual routing note:** Some domains have both a gateway handler AND a FastAPI handler at the same path. In production, `GATEWAY_UPSTREAM_BASE_URL` controls which tier serves the request. When set, the gateway forwards the request to FastAPI. When unset, the gateway uses its own in-memory/DB handler.

---

## 2. Request Lifecycle

For an authenticated API request:

```
1. Browser sends: POST /api/v1/leads
   Headers: Authorization: Bearer <JWT>, x-tenant-id: <uuid>, Idempotency-Key: <key>, Content-Type: application/json

2. Gateway receives request on port 3000

3. Middleware pipeline (in order):
   a. Helmet — sets security headers on response
   b. CORS — validates Origin header against ALLOWED_ORIGINS; preflight handled
   c. Raw body capture — stores req.rawBody for HMAC webhook verification
   d. express.json() — parses JSON body → req.body
   e. cookieParser — parses cookies → req.cookies
   f. requestIdMiddleware — generates UUID req.request_id, sets x-request-id response header
   g. observabilityMiddleware — parses/generates trace ID, sets x-trace-id response header, starts timer
   h. authMiddleware — extracts Bearer JWT, verifies signature (HS256/RS256), validates exp/nbf/sub/tenant_id/iss/aud claims, checks JTI blocklist, populates req.auth
   i. rateLimitHook — checks Redis sliding window; returns 429 if exceeded
   j. idempotencyMiddleware — checks Idempotency-Key; replays cached response if key seen before; blocks in-flight duplicates
   k. auditMiddleware — if POST/PATCH/DELETE matches ACTIONS_BY_ROUTE, registers post-response audit callback

4. Route handler executes:
   - Calls requireScopes([SCOPES.LEADS_CREATE]) — validates x-tenant-id == JWT.tenant_id and required scopes present
   - Validates request body
   - Executes business logic (DB query or proxy to FastAPI)
   - Calls respondSuccess(res, data, meta) or respondError(res, code, message, details, status)

5. observabilityMiddleware 'finish' callback fires:
   - Calculates duration_ms
   - Logs structured JSON with method/route/status_code/duration_ms/tenant_id/actor_id

6. auditMiddleware 'finish' callback fires (if applicable):
   - Appends audit event to in-memory hash chain

7. Response sent to browser:
   { "data": {...}, "meta": { "request_id": "uuid" } }
```

---

## 3. Authentication Flow

### Token issuance (POST /auth/login or POST /auth/register)
- Login: validates email/password (sha256:salt:hash comparison from DB), returns `access_token` + sets `refresh_token` as HttpOnly cookie
- Register: creates Tenant + User in DB, seeds pipeline, returns JWT
- Token building (`_buildToken` in v1-auth.routes.js):
  - In production with `JWT_SECRET`: signed HS256 JWT via `jsonwebtoken` npm package
  - In dev without JWT_SECRET: unsigned dev token (only valid with SKIP_JWT_VERIFICATION=true)

### JWT token structure (from auth-rbac.js + jwt_deps.py)

```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "iss": "crm-local",
  "aud": "crm-api",
  "exp": 1234567890,
  "jti": "unique-token-id",
  "role": "tenant_admin",
  "role_ids": ["role-admin"],
  "territory_ids": [],
  "scopes": ["leads.read", "leads.create", ...]
}
```

- **Algorithm**: HS256 (production with JWT_SECRET) or RS256 (with JWT_PUBLIC_KEY PEM)
- **"alg:none" vulnerability**: Explicitly blocked — ALLOWED_ALGORITHMS = Set(['HS256', 'RS256'])
- **Access token TTL**: 15 minutes
- **Refresh token TTL**: 7 days (single-use rotating)

### Token validation (gateway layer — auth-rbac.js)
1. Extract `Authorization: Bearer <token>` header
2. Reject if not "Bearer " prefix → 401 missing_bearer_token
3. In production: verify signature using `verifyJwt()` (custom crypto implementation, no external library)
4. Decode payload
5. Check `exp` claim → 401 expired_or_missing_exp
6. Check `nbf` claim if present → 401 token_not_yet_valid
7. Validate `sub` (string, non-empty) and `tenant_id` (string, non-empty) → 401 missing_required_claims
8. Validate `iss` and `aud` present → 401 missing_iss_or_aud
9. Check `jti` against Redis JTI blocklist → 401 token_revoked
10. Populate `req.auth = { sub, user_id, tenant_id, role, scopes, role_ids, territory_ids, jti }`

### Token validation (FastAPI layer — services/auth/jwt_deps.py)
- Uses `python-jose` library
- `get_current_user` Depends validates HS256 JWT
- Returns `TokenClaims` dataclass with same fields as gateway

### Tenant context enforcement (requireScopes — auth-rbac.js)
1. `x-tenant-id` header must be present and non-empty → 403 missing_tenant_context
2. `x-tenant-id` header value must equal `req.auth.tenant_id` → 403 tenant_mismatch
3. Required scopes must all be present in `req.auth.scopes` → 403 missing_{scope}
4. Optional: required role_ids check (additional role constraint beyond scopes)
5. Optional: `tenantBoundFields` — checks that params/body/query fields match tenant_id

---

## 4. Standard Request/Response Envelope

### Success response
```json
{
  "data": <entity | array | null>,
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "total": 42,
    "limit": 50,
    "offset": 0,
    "idempotency": { "replayed": true }
  }
}
```
- `data`: entity object (single resource) or array (list)
- `meta`: always present; includes request_id; pagination fields when applicable; idempotency.replayed when serving cached response

### Error response
```json
{
  "error": {
    "code": "validation_error",
    "message": "One or more fields are invalid.",
    "details": [
      { "field": "email", "reason": "required" },
      { "field": "phone_e164", "reason": "invalid_format" }
    ]
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

---

## 5. Pagination Pattern

**Style:** Offset-based pagination.

**Query parameters:**
- `limit` — integer, max varies by endpoint (leads: max 200; collections: max 200; most: unspecified cap)
- `offset` — integer, defaults to 0

**Response meta:**
```json
"meta": {
  "total": 150,
  "limit": 50,
  "offset": 0,
  "request_id": "..."
}
```

**Endpoints with confirmed pagination:** GET /leads, GET /collections/invoices, GET /cases, GET /campaigns, GET /partners, GET /workflows, GET /inbox/conversations, GET /ai/scores/leads, GET /ai/predictions/churn, GET /ai/estimates/clv, GET /ai/copilot/suggestions, GET /followups

---

## 6. Filtering Pattern

Filter parameters are passed as query string parameters. Common patterns:

| Parameter | Type | Endpoints |
|---|---|---|
| status | TEXT | /leads, /cases, /campaigns, /subscriptions, /workflows, /territories |
| stage | TEXT | /leads, /opportunities |
| priority | TEXT | /leads, /cases |
| owner_id | UUID | /leads, /opportunities, /followups |
| contact_id | UUID | /cases, /followups |
| account_id | UUID | /cases, /collections |
| queue_id | UUID | /cases, /inbox |
| score_band | TEXT | /ai/scores/leads |
| risk_band | TEXT | /ai/predictions/churn |
| is_active | BOOL | /territories |
| include_dismissed | BOOL | /ai/copilot/suggestions |
| lead_id | UUID | /followups |
| assigned_agent_id | UUID | /inbox/conversations |
| channel | TEXT | /inbox/conversations |

---

## 7. Sorting Pattern

Endpoints return results in a defined sort order (not caller-configurable in v1):

| Endpoint | Sort Order |
|---|---|
| GET /leads | updated_at DESC (implied) |
| GET /inbox/conversations | last_message_at DESC |
| GET /ai/scores/leads | score DESC |
| GET /ai/predictions/churn | churn_probability DESC |
| GET /ai/estimates/clv | estimated_clv DESC |
| GET /ai/copilot/suggestions | priority weight DESC (urgent=4, high=3, medium=2, low=1) |
| GET /territories | routing_priority ASC |
| GET /workflows/runs | started_at DESC |

Caller-specified sort order: NOT supported in v1.

---

## 8. Standard HTTP Status Codes

| HTTP Status | Error Code | When Used |
|---|---|---|
| 200 | — | Successful GET, PATCH |
| 201 | — | Successful POST (resource created) — CONFIRMED: resource-creation endpoints (POST /accounts, POST /leads, POST /contacts, POST /auth/register) return 201; operation-like POSTs (session/refresh) return 200 |
| 400 | bad_request | Malformed JSON body |
| 401 | unauthorized | Missing/invalid/expired JWT, revoked JTI |
| 403 | forbidden | CORS violation, missing x-tenant-id, tenant mismatch, missing scope |
| 404 | not_found | Resource not found |
| 409 | conflict | Duplicate resource, optimistic lock version mismatch, idempotency key reused with different payload, request already in-flight |
| 422 | validation_error | Pydantic validation failure, missing required fields, invalid field format, business rule violation |
| 429 | rate_limited | Rate limit exceeded |
| 500 | internal_error | Unhandled exception |
| 503 | service_unavailable | Downstream service unreachable |

---

## 9. Versioning Strategy

- All public API routes are prefixed `/api/v1/`
- No v2 routes exist
- Gateway health probes (`/health`, `/ready`) are unversioned
- FastAPI internal routes (`/internal/*`) are unversioned
- No API versioning header (`API-Version`) implemented

---

## 10. Idempotency

**Required on:** All write methods (POST, PUT, PATCH, DELETE).
**Header:** `Idempotency-Key` (case-insensitive; also accepted as `idempotency-key` or `x-idempotency-key`)
**Scope key:** `{tenant_id}:{METHOD}:{canonical_path}:{idempotency_key}`
**Behavior:**
- First request: executes normally; stores response in in-memory `recordStore`
- Subsequent identical request (same key + same body hash): returns cached response with `meta.idempotency.replayed: true`
- Same key + different body hash: 409 conflict `idempotency_key_reused_with_different_payload`
- In-flight duplicate: 409 conflict `request_in_progress`
- Cache: in-memory Map (not Redis-backed — does not survive gateway restarts)
- In-flight TTL: 5 minutes

---

## 11. Public Endpoints (No Auth Required)

| Path | Method | Purpose |
|---|---|---|
| /health | GET | Liveness probe |
| /ready | GET | DB readiness check |
| /api/v1/auth/login | POST | Email/password login |
| /api/v1/auth/register | POST | Tenant + user registration |
| /api/v1/auth/refresh | POST | Access token refresh (uses HttpOnly cookie) |
| /api/v1/auth/forgot-password | POST | OTP generation for password reset |
| /api/v1/auth/reset-password | POST | Password reset with OTP |
| /api/v1/auth/sessions | POST | Legacy IdP token exchange (returns 501) |
| /api/v1/whatsapp-webhooks/meta | GET | Meta webhook verification (hub.challenge) |
| /api/v1/whatsapp-webhooks/meta | POST | Meta inbound webhook (HMAC signature auth) |
| /api/v1/whatsapp-webhooks/twilio | POST | Twilio inbound webhook |
| /api/v1/whatsapp-webhooks/360dialog | POST | 360dialog inbound webhook |
| /api/v1/whatsapp-webhooks/gupshup | POST | Gupshup inbound webhook |
| /api/v1/payment-webhooks/jazzcash | POST | JazzCash webhook (HMAC auth) |
| /api/v1/payment-webhooks/easypaisa | POST | Easypaisa webhook (HMAC auth) |
| /dev-token | GET | Dev JWT generation (non-production only) |

---

*End API_CONTRACT.md*
