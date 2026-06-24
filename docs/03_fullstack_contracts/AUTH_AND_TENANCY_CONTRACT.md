Status: Draft
Authority Level: Critical
Last Reviewed: 2026-06-22
Owner: Human

# AUTH_AND_TENANCY_CONTRACT.md
> Source: backend/gateway/middleware/auth-rbac.js, backend/gateway/middleware/auth.js, backend/gateway/middleware/jti-blocklist.js, backend/gateway/routes/v1-auth.routes.js, backend/services/auth/jwt_deps.py, backend/db/identity_auth_db/schema.sql

---

## 1. JWT Token Structure

### Token format
HS256 signed JWT (in production). Base64url(header).Base64url(payload).Base64url(signature)

### Payload claims
```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "iss": "crm-local",
  "aud": "crm-api",
  "exp": 1234567890,
  "jti": "unique-token-id-uuid",
  "role": "tenant_admin",
  "role_ids": ["role-admin"],
  "territory_ids": [],
  "scopes": [
    "leads.read",
    "leads.create",
    "leads.update",
    ...
  ]
}
```

| Claim | Type | Description |
|---|---|---|
| `sub` | string (UUID) | User ID — primary identity |
| `tenant_id` | string (UUID) | Tenant the user belongs to |
| `iss` | string | JWT issuer — `JWT_ISSUER` env var (default: `crm-local`) |
| `aud` | string | JWT audience — `JWT_AUDIENCE` env var (default: `crm-api`) |
| `exp` | integer | Unix timestamp of expiry |
| `jti` | string (UUID) | Unique token ID for revocation tracking |
| `role` | string | Primary role name (e.g. `tenant_admin`, `manager`) |
| `role_ids` | string[] | Role IDs array (e.g. `["role-admin"]`) |
| `territory_ids` | string[] | Territory scope for the user |
| `scopes` | string[] | All permission scopes granted (e.g. `["leads.read", "leads.create", ...]`) |

### Token TTLs
- **Access token:** 15 minutes (900 seconds) — `ACCESS_TOKEN_TTL_MS = 15 * 60 * 1000`
- **Refresh token:** 7 days (604,800 seconds) — `REFRESH_TOKEN_TTL_S = 7 * 24 * 60 * 60`

### Signing algorithm
- **Production:** HS256 with `JWT_SECRET` env var (via `jsonwebtoken` npm package)
- **RS256 alternative:** Supported in gateway auth.js (`JWT_PUBLIC_KEY` env var, PEM format)
- **Development:** Unsigned dev token when `JWT_SECRET` unset and `SKIP_JWT_VERIFICATION=true`
- **"alg:none" attack:** Blocked — `ALLOWED_ALGORITHMS = Set(['HS256', 'RS256'])` in gateway auth.js

---

## 2. Token Issuance

### Login (POST /api/v1/auth/login)
1. Client sends `{ email, password }` in request body (no JWT required)
2. Gateway queries DB for user by `(tenant_id, email)` — reads from identity_auth_db
3. Validates password hash (format: `sha256:{salt}:{hash}`)
4. Calls `_buildToken(sub=user_id, tenantId, scopes=allScopes, ttlMs=15min)`
5. Returns `{ data: { access_token, token_type: "Bearer" } }` — refresh token set as HttpOnly cookie

### Registration (POST /api/v1/auth/register)
1. Client sends `{ name, email, password, slug }`
2. Gateway creates Tenant row in org_tenant_db
3. Inserts `tenant_ref` rows into 6 domain schemas (identity_auth_db, lead_management_db, contact_account_db, opportunity_db, transaction_db, activity_task_db) in a single transaction
4. Creates User row in identity_auth_db.users
5. Fires POST /internal/activation/seed (non-blocking) to seed default pipeline for new tenant
6. Returns JWT (same format as login)

---

## 3. Token Refresh

### Refresh endpoint: POST /api/v1/auth/refresh
- **Auth required:** No — public endpoint
- **Refresh token source:** HttpOnly cookie (`refresh_token`) OR request body `{ refresh_token }` field
- **Process:**
  1. Read refresh token from cookie or body
  2. Validate token against `refresh_tokens` table (check not expired, not revoked)
  3. Mark old token as `rotated_at = NOW()` (single-use rotation)
  4. Issue new access token
  5. Issue new refresh token (stored in DB, set as cookie)
- **Rotation:** Single-use — each refresh token can only be used once. Using it generates a new refresh token.

---

## 4. Token Validation (Gateway)

Performed by `authMiddleware()` in `backend/gateway/middleware/auth-rbac.js` on every authenticated request:

```
Step 1: Extract Bearer token from Authorization header
        → 401 missing_bearer_token if absent or wrong format

Step 2: (Production only) Verify signature using verifyJwt()
        → 401 invalid_signature if signature fails
        → 401 unsupported_algorithm if alg not in ['HS256', 'RS256']

Step 3: Decode payload (base64url)
        → 401 invalid_token if decode fails

Step 4: Check exp claim
        → 401 expired_or_missing_exp if exp <= now

Step 5: Check nbf claim (if present)
        → 401 token_not_yet_valid if nbf > now

Step 6: Validate sub (string, non-empty) and tenant_id (string, non-empty)
        → 401 missing_required_claims if absent

Step 7: Validate iss and aud present
        → 401 missing_iss_or_aud if absent

Step 8: Check jti against Redis JTI blocklist
        → 401 token_revoked if in blocklist

Step 9: Populate req.auth = {
          sub, user_id, tenant_id, role, scopes, role_ids, territory_ids, jti
        }
        → Pass to next middleware
```

### Token validation (FastAPI — jwt_deps.py)
Uses `python-jose` library. `get_current_user` Depends validates HS256 JWT with `JWT_SECRET_KEY` env var. Returns `TokenClaims` dataclass. Both layers validate independently.

---

## 5. Multi-Tenancy: How tenant_id Flows Through Requests

Every authenticated request must include:
1. **JWT claim:** `tenant_id` embedded in the token at issuance
2. **Header:** `x-tenant-id: {tenant-uuid}` on every API call

**Enforcement** (in `requireScopes()` in auth-rbac.js):
```
Step 1: Check x-tenant-id header present and non-empty
        → 403 missing_tenant_context if absent

Step 2: Check x-tenant-id header value == req.auth.tenant_id (from JWT)
        → 403 tenant_mismatch if they don't match

Step 3: Proceed to scope checks
```

**Data query isolation:** All DB queries include `WHERE tenant_id = $1` using the validated `req.auth.tenant_id`. The gateway never uses the raw `x-tenant-id` header for data queries — only the JWT claim is trusted for DB filtering.

**Tenant-scoped resource validation (optional per route):**
`requireScopes(scopes, { tenantBoundFields: ['tenant_id'] })` — validates that `tenant_id` in params/body/query matches the authenticated tenant. Used on routes where tenant_id might appear in the request body.

---

## 6. Tenant Isolation Enforcement

### Gateway layer
- Every route handler extracts `req.auth.tenant_id` (from JWT) for DB queries
- `requireScopes()` enforces `x-tenant-id == JWT.tenant_id` on all protected routes
- No cross-tenant data access is possible through the normal API path

### Database layer
- Every domain table has `tenant_id UUID NOT NULL` column
- FK to local `tenant_ref` table (prevents orphaned data)
- Application-level WHERE clause — `WHERE tenant_id = $1` — on all queries
- No DB-level Row Level Security (RLS) — CONFIRMED ABSENT (Phase 3.25, R-TBD-002): 18 schema.sql files contain no `ENABLE ROW LEVEL SECURITY` or `CREATE POLICY` statements. Application-layer isolation only. Accepted architecture trade-off (G-LOW-004 SAFE-DEFAULT).

### FastAPI layer
- `TokenClaims` passed to every route handler includes `tenant_id`
- Service methods filter by `tenant_id` from JWT claims

---

## 7. Session Management

**Type:** Stateless JWT-based sessions (no server-side session state for access tokens).

- Access tokens are short-lived (15min) and stateless
- Refresh tokens are DB-persisted in `identity_auth_db.refresh_tokens`
- Session records in `identity_auth_db.sessions` track login events with IP and user agent
- JTI revocation via in-memory Set (gateway) — see note below

**JTI Revocation Storage:**
```javascript
// backend/gateway/middleware/jti-blocklist.js
const revokedJtis = new Set(); // in-memory
function addRevoked(jti) { revokedJtis.add(jti); }
function isRevoked(jti) { return revokedJtis.has(jti); }
```
**Important limitation:** The JTI blocklist is **in-memory only**. It does not survive gateway restarts or multi-instance deployments. CONFIRMED (G-CRIT-001, Phase 2.9): `revokedJtis = new Set()` in jti-blocklist.js. In production with multiple gateway instances, a revoked token would still be accepted by other instances. SAFE-DEFAULT OA-002 applies: accept for C6 single-instance Render.com deployment; migrate to `redis.setex('jti:{jti}', 900, '1')` in Post-C6 Auth Hardening Sprint.

---

## 8. Logout / Token Invalidation

### Logout endpoint: DELETE /api/v1/auth/sessions/current
- **Auth required:** Yes (JWT required)
- **Process:**
  1. Extract `jti` from `req.auth`
  2. Call `addRevoked(jti)` — adds JTI to in-memory blocklist
  3. Returns 200 success
- **Effect:** Subsequent requests with the same access token will be rejected (401 token_revoked) as long as the gateway instance is running
- **Limitation:** Does NOT invalidate refresh tokens — CONFIRMED (G-HIGH-002, Phase 2.9): logout handler only calls `addRevoked(jti)`; `rt:{refreshToken}` Redis key is NOT deleted. Refresh token remains valid for 7 days post-logout. SAFE-DEFAULT OA-009: accept for C6; fix in Post-C6 Auth Sprint (delete `rt:{refreshToken}` from Redis on logout).
- **Client responsibility:** Client should also clear stored tokens (localStorage/cookies) on logout

---

## 9. OTP Flow (Password Reset)

### Step 1: POST /api/v1/auth/forgot-password
- Body: `{ email, tenant_id }`
- Generates 6-digit numeric OTP
- Stores OTP in Redis with key `otp:{tenant_id}:{email}`, TTL 15 minutes
- Sends OTP via SendGrid email (when SENDGRID_API_KEY set) or logs in dev

### Step 2: POST /api/v1/auth/reset-password
- Body: `{ email, tenant_id, otp, new_password }`
- Validates OTP from Redis
- Updates `password_hash` in identity_auth_db.users
- Deletes OTP from Redis

---

## 10. Frontend Integration Requirements

The frontend must:
1. Store access token (in memory or localStorage)
2. Store refresh token (as HttpOnly cookie — set by gateway automatically)
3. Include `Authorization: Bearer <token>` header on every API call
4. Include `x-tenant-id: <tenant-uuid>` header on every authenticated API call
5. Handle 401 responses by attempting token refresh (POST /auth/refresh)
6. Handle 401 after refresh failure by redirecting to login
7. On logout: call DELETE /auth/sessions/current, then clear local token storage

---

*End AUTH_AND_TENANCY_CONTRACT.md*
