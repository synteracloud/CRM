# HARDENING_PLAN.md — Pakistan CRM OS
**Generated:** 2026-06-21 — U9 Security Hardening Planning
**Evidence base:** tests/security/pip-audit.json, tests/security/c5_api_security_scan.py (confirmed helmet.js headers, rate limiting, CORS), U1 AUTHORITY_RECONSTRUCTION_REPORT, U8 WORKSPACE_SEALING_REPORT, ci.yml (security-scan job), backend/pyproject.toml (ruff config), render.yaml

---

## Hardening Status Overview

| Area | Current State | Action Required | Priority | Effort |
|---|---|---|---|---|
| HTTP security headers | helmet.js configured (CSP, HSTS, X-Frame, X-Content-Type) — c5 scan verifies | Verify CSP policy string is not too permissive | Medium | 1h |
| Rate limiting | x-ratelimit-limit/remaining headers confirmed present (c5 scan) | Verify per-user limits distinct from per-IP; add endpoint-specific limits for auth routes | High | 4h |
| Input validation (Pydantic) | Pydantic v2.13.4 in all FastAPI services; gateway uses express body-parser with JSON schema | Verify max body size configured in gateway | High | 2h |
| Secret management | .env.local + render.yaml env vars; JWT_SECRET, DB URL, Redis URL are env vars | No hardcoded secrets confirmed (U8 C: path grep found none); align PIP_CACHE_DIR inconsistency | Low | 1h |
| Database query safety | SQLAlchemy 2.0.49 ORM (parameterized by default); no raw SQL confirmed by ruff TID251 rule | Verify all filter params go through ORM; no string interpolation in queries | Critical | 2h |
| CORS | CORS configured in gateway — c5 scan verifies allowed vs blocked origins | Verify allowed origin list in gateway matches actual Render frontend URL | High | 1h |
| Dependency CVEs | 2 active CVE packages (starlette, pip); python-jose RESOLVED [U10] | python-jose 3.5.0 installed (CVEs resolved — pip-audit.json was stale); upgrade starlette 0.47.2+, pip 26.1+ | High (starlette), Medium (pip) | 2h |
| WhatsApp webhook signature | X-Hub-Signature-256 HMAC-SHA256 verification — adapter code present | Verify WHATSAPP_APP_SECRET is set in render.yaml (not stub) | Critical | 1h |
| Payment webhook signature | JazzCash/Easypaisa signature check in adapters — stub_mode=True | Document signature verification as P-016 dependency; test in stub mode | High | 0h (blocked P-016) |
| Multi-tenancy isolation | x-tenant-id + JWT tenant_id match enforced in auth-rbac.js middleware | Semgrep custom rule `.semgrep/` catches routes missing tenant check; run in CI | Critical | 1h (CI already configured) |
| Token handling | HS256 JWT; JTI Redis blocklist on logout; single-use refresh rotation | Upgrade consideration: RS256 for asymmetric signing (future hardening) | Low | 8h (future) |

---

## 1. HTTP Security Headers

**Current state (confirmed by c5_api_security_scan.py):**
- `Content-Security-Policy` — present (helmet.js default or custom policy)
- `Strict-Transport-Security` — present
- `X-Frame-Options` — present
- `X-Content-Type-Options: nosniff` — present

**Hardening action:**
Verify the CSP `default-src` directive is not set to `'unsafe-inline'` or `'*'`. The CRM frontend uses jQuery, DataTables, and Bootstrap inline scripts from CDN — a permissive CSP is likely but should be documented.

```bash
# Check actual CSP header value:
curl -s https://crm-gateway-l3rm.onrender.com/health -I | grep -i content-security-policy
```

**Target CSP policy for gateway (static API server — no HTML):**
```
default-src 'none'; frame-ancestors 'none'
```

**Priority:** Medium | **Effort:** 1h

---

## 2. Rate Limiting

**Current state:** Rate limiting headers (`x-ratelimit-limit`, `x-ratelimit-remaining`) confirmed present in c5 scan. Redis is available and confirmed for this purpose.

**Hardening actions:**

| Route | Current Limit (inferred) | Recommended |
|---|---|---|
| POST /auth/login | Unknown | 10 requests/min per IP (brute-force protection) |
| POST /auth/register | Unknown | 5 requests/min per IP (registration flood protection) |
| POST /auth/forgot-password | Unknown | 3 requests/min per IP (OTP abuse protection) |
| POST /leads/import | Unknown | 2 requests/min per tenant (bulk import throttle) |
| POST /whatsapp-webhooks/* | Unknown | 500 requests/min per IP (webhook burst allowance) |
| GET /api/v1/* (general) | Unknown | 300 requests/min per tenant |

**Verify configuration in:** `backend/gateway/middleware/` or `backend/gateway/server.js` — look for `express-rate-limit` or `rate-limiter-flexible` usage.

**Priority:** High | **Effort:** 4h (audit existing limits + add endpoint-specific overrides)

---

## 3. Input Validation

**Current state:**
- Python services use Pydantic v2.13.4 for all request/response models
- Gateway uses `express.json()` body parser with no explicit `limit` override found (need verification)
- `ruff` with `TID251` rule enforces adapter boundary (ADR-002)

**Hardening actions:**

**3a. Gateway body size limit:**
Verify `express.json({ limit: '1mb' })` or similar is configured in `backend/gateway/server.js`. Without a limit, POST /leads/import with a 100MB CSV body could exhaust memory.

```javascript
// Required in gateway/server.js:
app.use(express.json({ limit: '5mb' })); // or appropriate limit for CSV import
app.use(express.urlencoded({ extended: true, limit: '5mb' }));
```

**3b. Phone number validation:**
`contact_phone_e164` fields: verify E.164 regex `^\+923[0-9]{9}$` or `^\+[1-9][0-9]{7,14}$` is enforced at gateway level (not just Pydantic layer) to catch malformed phones before they reach the service.

**3c. SQL filter params:**
All list endpoints accept query params (stage, owner_id, status, priority, source). Verify gateway passes these as parameterized arguments to downstream FastAPI, not as string interpolation.

**Priority:** High | **Effort:** 2h

---

## 4. Secret Management

**Current state (U8 confirmed):**
- `D:\SaaS\CRM\.env.local` — contains local dev secrets (PIP_CACHE_DIR, etc.) — NOT committed to git
- `D:\SaaS\CRM\backend\.env.example` — template only, no real secrets
- `render.yaml` — production env vars defined (JAZZCASH_STUB_MODE, EASYPAISA_STUB_MODE, NODE_ENV)
- `JWT_SECRET`, `DATABASE_URL`, `REDIS_URL` are environment variables on Render — not in any committed file
- C: path grep returned CLEAN for all config files (U8)

**Hardening actions:**

**4a. Confirm JWT_SECRET entropy:**
JWT_SECRET should be at least 32 random bytes (256 bits). Verify via Render dashboard that the secret is not a short human-readable string.

**4b. PIP_CACHE_DIR inconsistency (minor):**
`.env.local` declares `PIP_CACHE_DIR=D:\pip-cache` but `pip.ini` uses `D:\LMS\workspace\.pip-cache`. Align these (U8 informational finding).

**4c. .env.local in .gitignore:**
Confirm `.env.local` is in `.gitignore`. No action if already excluded.

**4d. Render dashboard audit:**
Review all env vars on Render to confirm:
- No `*_SECRET`, `*_KEY`, or `DATABASE_URL` values visible in build logs
- `JAZZCASH_STUB_MODE=true` set in production until P-016 is resolved

**Priority:** Low (secrets are env vars) | **Effort:** 1h

---

## 5. Database Security

**Current state:**
- SQLAlchemy 2.0.49 ORM — parameterized queries by default
- psycopg2-binary 2.9.12 (PostgreSQL adapter)
- 20 separate domain databases with schema-per-domain isolation
- Alembic 1.18.4 for migrations

**Hardening actions:**

**5a. No raw SQL grep:**
```bash
# Verify no raw string-interpolated SQL:
grep -r "f\"SELECT\|f'SELECT\|execute(.*%.*)\|execute(.*format(" D:\SaaS\CRM\backend\src\ D:\SaaS\CRM\backend\services\
```
If any hits: replace with SQLAlchemy text() with bindparams.

**5b. Connection pool limits:**
Verify `pool_size` and `max_overflow` in SQLAlchemy engine config. Under load (100 users), uncontrolled pool growth causes `FATAL: remaining connection slots are reserved for non-replication superuser connections`.

Recommended:
```python
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, pool_timeout=30)
```

**5c. Alembic migration safety:**
All 12 confirmed migrations should be reviewed for:
- No `DROP COLUMN` without `IF EXISTS`
- No data-altering migrations without backup point

**Priority:** Critical (raw SQL) / High (connection pool) | **Effort:** 2h

---

## 6. CORS Configuration

**Current state (c5 scan confirmed):**
- Unlisted origin `https://evil.example.com` blocked (403 or no ACAO header)
- Allowed origin `https://crm-frontend-0gde.onrender.com` accepted

**Hardening actions:**

**6a. Verify allowed origins list in gateway:**
Check `backend/gateway/server.js` or gateway middleware for CORS allowed origins. Should be:
```javascript
const allowedOrigins = [
  'https://crm-frontend-0gde.onrender.com',
  // Add any additional staging/local origins in NODE_ENV != 'production'
];
```

**6b. Reject wildcard origin (`*`) in production:**
Ensure CORS config does NOT use `origin: '*'` when `NODE_ENV=production`.

**6c. Preflight caching:**
Add `maxAge: 600` (10 minutes) to CORS config to reduce OPTIONS preflight requests from mobile clients.

**Priority:** High | **Effort:** 1h

---

## 7. Dependency Scanning

**Current state:**
- `pip-audit` run in CI (`security-scan` job, with `|| true` — informational only)
- `npm audit --audit-level=critical` run in CI for gateway
- `semgrep` with `--config=auto` and custom `.semgrep/` tenant isolation rule

**Known CVEs requiring immediate action:**

### python-jose — RESOLVED [U10 CRIT-002 2026-06-21]
- ~~CVE-2024-33664, CVE-2024-33663, CVE-2024-29370~~ — **RESOLVED in installed venv**
- pip-audit.json (2026-06-20) showed 3.3.0 (stale scan) — actual installed version is **3.5.0** (confirmed by pip install check 2026-06-21; PROGRESS.md 2026-06-01 confirms "pip-audit python-jose upgraded" during C3)
- requirements.txt has been at `python-jose[cryptography]==3.5.0` since C3
- No further action required

### starlette 0.38.6 (HIGH — runtime DoS risk)
- CVE-2024-47874: Multipart form with no filename buffers to memory with no size limit → OOM
- GHSA-86qp-5c8j-p5mr: Host header injection — URL reconstruction based on unvalidated Host
- CVE-2025-54121: Large file upload blocks event loop
- **Fix:** `pip install starlette>=0.47.2` — this also upgrades FastAPI's dependency
- **Note:** FastAPI depends on Starlette. Upgrade FastAPI first: `pip install fastapi>=0.115.5` which pulls starlette>=0.40.0. Then pin starlette>=0.47.2 explicitly.

### pip 25.0.1 (MEDIUM — development tooling only)
- 4 CVEs related to tar/ZIP extraction and path traversal in wheel installation
- **Fix:** `pip install --upgrade pip>=26.1`
- **Impact:** Only affects the development/CI environment, not production runtime

**Hardening action for CI:**
Change security-scan job to fail on Critical CVEs:
```yaml
- name: pip-audit
  run: |
    pip install pip-audit
    pip-audit --requirement backend/requirements.txt --fail-on-severity critical
```

**Priority:** High (starlette) / Medium (pip) | **Effort:** 2h total | [python-jose RESOLVED — U10 CRIT-002 2026-06-21]

---

## 8. WhatsApp / Payment Webhook Verification

**Current state:**
- WhatsApp Meta adapter: `X-Hub-Signature-256` HMAC-SHA256 verification code present in `adapters/pakistan/messaging/meta_api_adapter.py`
- GET /whatsapp-webhooks/meta: hub.verify_token challenge implemented
- JazzCash/Easypaisa: signature verification in adapter code; stub_mode=True blocks live payments

**Hardening actions:**

**8a. Verify WHATSAPP_APP_SECRET is set in render.yaml:**
```yaml
# Required in render.yaml for signature verification to work:
- key: WHATSAPP_APP_SECRET
  value: <Meta App Secret from WhatsApp Business settings>
```
Without this, signature verification may fall back to accepting all requests. Check the adapter for `if not app_secret: skip_verification` patterns.

**8b. Replay attack prevention:**
Verify WhatsApp webhook handler checks `X-Hub-Signature-256` timestamp nonce to prevent replay attacks. Meta includes a timestamp in the header; request older than 5 minutes should be rejected.

**8c. JazzCash/Easypaisa (P-016):**
When P-016 is resolved (real credentials obtained):
1. Set `JAZZCASH_STUB_MODE=false` and `EASYPAISA_STUB_MODE=false` in render.yaml
2. Add integration tests for actual signature verification
3. Run SEC-043 and SEC-044 tests against real signature

**Priority:** Critical | **Effort:** 1h (verify existing code) + P-016 hours for live activation

---

## 9. Multi-Tenancy Row-Level Security

**Current state:**
- Application-level isolation enforced in gateway middleware (`auth-rbac.js`)
- `x-tenant-id` header must match JWT `tenant_id` on every request
- Semgrep custom rule in `.semgrep/` detects gateway routes missing tenant check
- 20 domain databases, each schema scoped by `tenant_id` column

**Hardening actions:**

**9a. PostgreSQL Row-Level Security (RLS):**
Currently isolation is application-level only. Consider adding PostgreSQL RLS as a defense-in-depth second layer:
```sql
-- Example for lead_management_db:
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON leads
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```
This prevents any raw SQL query (e.g., from a compromised service) from reading cross-tenant data.

**Effort estimate:** 8h (apply to 20 databases) — Medium priority

**9b. Verify semgrep rule coverage:**
Confirm `.semgrep/` rule fires on every route file. Run manually:
```bash
D:\SaaS\CRM\backend\.venv\Scripts\semgrep --config=D:\SaaS\CRM\.semgrep\ D:\SaaS\CRM\backend\gateway\routes\
```

**Priority:** Critical (semgrep CI verification) / Medium (RLS addition) | **Effort:** 1h (semgrep) + 8h (RLS)

---

## Hardening Summary Table

| Priority | Item | Action | Effort | Owner |
|---|---|---|---|---|
| ~~Critical~~ | ~~python-jose CVE~~ | **RESOLVED** — 3.5.0 installed; pip-audit.json was stale [U10 2026-06-21] | 0h | Done |
| Critical | starlette CVE | Upgrade to >=0.47.2 in requirements.txt | 1h | Dev |
| Critical | No raw SQL | Grep + fix any f-string SQL | 2h | Dev |
| Critical | WhatsApp secret set | Verify WHATSAPP_APP_SECRET in render.yaml | 1h | DevOps |
| Critical | Semgrep CI hard gate | Remove `|| true` from semgrep CI step | 0.5h | Dev |
| High | Rate limit auth routes | Add per-IP rate limit to /auth/* | 4h | Dev |
| High | Gateway body size limit | Add express.json({ limit: '5mb' }) | 0.5h | Dev |
| High | CORS origin list | Audit and harden allowed origins | 1h | Dev |
| High | Starlette Host header | Upgrade starlette (same as CVE action above) | — | Dev |
| High | pip-audit CI hard gate | Change to --fail-on-severity critical | 0.5h | Dev |
| Medium | CSP policy audit | Check CSP is not 'unsafe-inline' | 1h | Dev |
| Medium | pip CVE | Upgrade pip >=26.1 in CI | 0.5h | DevOps |
| Medium | Connection pool limits | Set pool_size, max_overflow in SQLAlchemy | 2h | Dev |
| Low | RS256 JWT signing | Asymmetric signing for enhanced key rotation | 8h | Dev (future) |
| Low | PostgreSQL RLS | Row-level security as defense-in-depth | 8h | Dev (future) |
| Low | PIP_CACHE_DIR align | Align .env.local with pip.ini | 0.5h | DevOps |

---

*End HARDENING_PLAN.md*
