# SECURITY_TEST_PLAN.md — Pakistan CRM OS
**Generated:** 2026-06-21 — U9 Security Test Planning
**Evidence base:** U1 AUTHORITY_RECONSTRUCTION_REPORT, ROLE_PERMISSION_INVENTORY, U8 WORKSPACE_SEALING_REPORT, tests/security/pip-audit.json, tests/security/c5_api_security_scan.py

---

## Architecture Security Context

- **Gateway:** Node.js Express; JWT (HS256, `JWT_SECRET` env var); Redis JTI blocklist for revocation
- **Auth:** 15-min access tokens, 7-day rotating refresh tokens; `x-tenant-id` header required on all protected routes
- **RBAC:** 7 roles, 91 scopes, default-deny; enforced in `gateway/middleware/auth-rbac.js`
- **Multi-tenancy:** Row-level isolation via `tenant_id` column; `x-tenant-id` must match JWT `tenant_id`
- **Payment integrations:** JazzCash + Easypaisa in stub_mode=true (P-016 blocker); webhook signature validation present
- **WhatsApp:** 4 provider adapters; Meta webhook verification (hub.challenge GET + X-Hub-Signature-256 POST)
- **Known CVEs (pip-audit.json, 2026-06-20 — NOTE: file is STALE; see U10 correction below):**
  - pip 25.0.1: 4 CVEs (fix: upgrade to 26.1+)
  - python-jose: pip-audit.json shows 3.3.0 (stale) — **ACTUAL installed version is 3.5.0** (confirmed 2026-06-21 by pip install check; PROGRESS.md 2026-06-01 confirms "pip-audit python-jose upgraded"). 3 CVEs from 3.3.0 are RESOLVED in installed venv. [U10 CRIT-002 remediation 2026-06-21]
  - starlette 0.38.6: 3 CVEs including multipart DoS and Host header injection (fix: upgrade to 0.47.2+ — accepted risk, requirements.txt pins 0.38.6 for FastAPI 0.115 compat)

---

## Security Test Cases

### Category 1 — Authentication

| ID | Test | Method | Expected Result | Failure Impact |
|---|---|---|---|---|
| SEC-001 | Unauthenticated GET /leads returns 401 | automated (c5_api_security_scan.py) | HTTP 401, `{"error":{"code":"unauthorized"}}` | Critical |
| SEC-002 | Invalid JWT token returns 401 | automated (c5_api_security_scan.py) | HTTP 401 | Critical |
| SEC-003 | Expired JWT (>15 min) returns 401 | manual (craft expired token) | HTTP 401 with expiry error | Critical |
| SEC-004 | POST /auth/refresh with used refresh token returns 401 (single-use rotation) | automated pytest | HTTP 401 on second use | Critical |
| SEC-005 | DELETE /auth/sessions/current adds JTI to Redis blocklist; subsequent request with same token returns 401 | automated pytest (httpx) | HTTP 200 on logout; HTTP 401 on reuse | Critical |
| SEC-006 | POST /auth/refresh with missing cookie returns 401 | automated pytest | HTTP 401 | High |
| SEC-007 | POST /auth/forgot-password with unknown email returns 200 (no user enumeration) | automated pytest | HTTP 200 regardless of email existence | Medium |
| SEC-008 | POST /auth/register with existing email returns 409 | automated pytest | HTTP 409 | Medium |
| SEC-009 | Password not returned in any auth response (login, register, user GET) | automated pytest | No `password_hash` or `password` key in response body | High |
| SEC-010 | Dev token endpoint (`/dev-token`) unavailable in production (`NODE_ENV=production`) | manual (verify on Render) | HTTP 404 or 403 in prod | Critical |

**Implementation note:** SEC-003 to SEC-010 are not in existing c5_api_security_scan.py. Add to `tests/security/c5_api_security_scan.py` or new `tests/api/test_auth_security.py` using httpx.

---

### Category 2 — RBAC / Authorization

**Context:** 7 roles from rbac-scopes.js: `tenant_owner`, `tenant_admin`, `manager`, `agent`, `analyst`, `auditor`, `integration_service`

**Key restrictions to test:**
- `leads.delete` granted ONLY to `tenant_owner`, `tenant_admin` — NOT `manager`, `agent`, `analyst`, `auditor`
- `cases.admin` (assign, close, escalate, queue management) granted ONLY to `tenant_owner`, `tenant_admin`, `manager`
- `collections.reconcile` granted ONLY to `tenant_owner`, `tenant_admin`
- `audit.logs.read` granted ONLY to `tenant_owner`, `tenant_admin` (NOT `auditor` — auditor has only `audit.read`)
- `integrations.manage` granted ONLY to `tenant_owner`, `tenant_admin`

| ID | Test | Method | Expected Result | Failure Impact |
|---|---|---|---|---|
| SEC-011 | `agent` role calls DELETE /leads/:id → 403 | automated pytest (craft agent JWT) | HTTP 403, `{"error":{"code":"forbidden"}}` | Critical |
| SEC-012 | `analyst` role calls POST /leads → 403 (analyst has only leads.read) | automated pytest | HTTP 403 | High |
| SEC-013 | `auditor` role calls GET /audit → 200 (has audit.read) | automated pytest | HTTP 200 | High |
| SEC-014 | `auditor` role calls GET /audit/export → 403 (requires audit.logs.read) | automated pytest | HTTP 403 | High |
| SEC-015 | `agent` role calls POST /cases/:id/close → 403 (requires cases.admin) | automated pytest | HTTP 403 | High |
| SEC-016 | `manager` role calls DELETE /leads/:id → 403 (managers cannot delete leads) | automated pytest | HTTP 403 | High |
| SEC-017 | `analyst` role calls PATCH /integrations/:provider → 403 | automated pytest | HTTP 403 | High |
| SEC-018 | `agent` cannot call GET /inbox/presence (all agents) → 403 (requires inbox.admin) | automated pytest | HTTP 403 | Medium |
| SEC-019 | `agent` can call POST /inbox/conversations/:id/handoff only for own conversations | automated pytest (create conv as agent A, attempt handoff as agent B) | HTTP 403 when agent B not supervisor | High |
| SEC-020 | `integration_service` role has all 91 scopes (can call any endpoint) | automated pytest | HTTP 200 on every protected route | Medium |

**Implementation:** Create `tests/api/test_rbac_matrix.py`. Use `/dev-token` with role parameter if supported, or craft JWTs with different role claims. If gateway does not support role-specific dev tokens, test via direct JWT construction with known `JWT_SECRET` (dev environment only).

---

### Category 3 — Tenant Isolation (Multi-tenancy)

| ID | Test | Method | Expected Result | Failure Impact |
|---|---|---|---|---|
| SEC-021 | Tenant A JWT used with Tenant B's x-tenant-id header returns 401/403 | automated pytest | HTTP 401 or 403 — JWT tenant_id must match x-tenant-id | Critical |
| SEC-022 | Tenant A cannot list Tenant B's leads (different JWT, same gateway) | automated pytest (register 2 tenants, create lead in T-A, query as T-B) | HTTP 200 but empty data array for T-B | Critical |
| SEC-023 | Tenant A cannot access Tenant B's case by ID even if UUID guessed | automated pytest | HTTP 404 (not 403 — do not reveal existence) | Critical |
| SEC-024 | Missing x-tenant-id header returns 401 | automated pytest | HTTP 401 | High |
| SEC-025 | x-tenant-id header value of all-zeros UUID returns 401 (not a real tenant) | automated pytest | HTTP 401 | High |

**Evidence:** test_tenant_isolation.py exists in backend/tests/ — verify it covers SEC-021 through SEC-023 patterns. Cross-reference with semgrep custom rule in `.semgrep/` (tenant-isolation rule confirmed in ci.yml).

---

### Category 4 — Injection Attacks

| ID | Test | Method | Expected Result | Failure Impact |
|---|---|---|---|---|
| SEC-026 | SQL injection in GET /leads?stage=' OR 1=1-- | automated (c5_api_security_scan.py check 3) | HTTP 200 or 422 (never 5xx) | Critical |
| SEC-027 | SQL injection in GET /contacts?email=admin'@test.com | automated pytest | HTTP 200 or 422, no DB error exposed | Critical |
| SEC-028 | NoSQL-style injection in GET /leads?owner_id[$gt]=0 | automated pytest | HTTP 400 or 422 (filter param validation) | High |
| SEC-029 | XSS payload in POST /auth/register name field (`<script>alert(1)</script>`) | automated (c5_api_security_scan.py check 3) | HTTP 200/201 (stored but sanitized); name not reflected back in response with script tag | High |
| SEC-030 | XSS in GET /leads?stage=<img+src=x+onerror=alert(1)> | automated pytest | HTTP 200 or 422; no script execution in JSON response | Medium |
| SEC-031 | Path traversal in GET /api/v1/../../../etc/passwd | automated pytest | HTTP 404 — gateway does not route traversal paths | Critical |
| SEC-032 | Large body POST /leads with 10MB payload | automated pytest | HTTP 413 or connection timeout; no memory exhaustion | High |

---

### Category 5 — API Security (Headers, CORS, Rate Limiting)

| ID | Test | Method | Expected Result | Failure Impact |
|---|---|---|---|---|
| SEC-033 | GET /health returns Content-Security-Policy header | automated (c5 check 1) | CSP header present (helmet.js configured) | High |
| SEC-034 | GET /health returns Strict-Transport-Security header | automated (c5 check 1) | HSTS header present | High |
| SEC-035 | GET /health returns X-Frame-Options header | automated (c5 check 1) | X-Frame-Options: DENY or SAMEORIGIN | High |
| SEC-036 | GET /health returns X-Content-Type-Options: nosniff | automated (c5 check 1) | Header present | Medium |
| SEC-037 | CORS blocks requests from unlisted origin (https://evil.example.com) | automated (c5 check 5) | HTTP 403 or no Access-Control-Allow-Origin header | High |
| SEC-038 | CORS allows registered Render frontend origin | automated (c5 check 5) | HTTP 200 with correct ACAO header | High |
| SEC-039 | Rate limit headers present on GET /leads | automated (c5 check 6) | x-ratelimit-limit and x-ratelimit-remaining present | Medium |
| SEC-040 | Rapid-fire 100 requests to POST /auth/login triggers rate limit (429) | automated pytest | HTTP 429 after threshold | High |
| SEC-041 | Error responses do not expose stack traces or internal paths | automated (c5 check 4) | No "Traceback", "at Object", "node_modules" in 4xx/5xx body | High |
| SEC-042 | GET /health does not expose database URL, secrets, or connection strings | automated (c5 check 7) | Health body < 500 chars; no "password", "secret", "DATABASE_URL" | High |

---

### Category 6 — Payment Security

| ID | Test | Method | Expected Result | Failure Impact |
|---|---|---|---|---|
| SEC-043 | POST /payment-webhooks/jazzcash without valid signature returns 401 | automated pytest | HTTP 401 or 403 (signature verification must reject) | Critical |
| SEC-044 | POST /payment-webhooks/easypaisa without valid signature returns 401 | automated pytest | HTTP 401 or 403 | Critical |
| SEC-045 | POST /payment-webhooks/jazzcash with replayed old signature returns 401 (replay protection) | manual (if timestamp nonce implemented) | HTTP 401 | High |
| SEC-046 | Payment data (card numbers, account numbers) not logged to stdout | manual (review gateway logs after payment POST) | No sensitive payment fields in application logs | Critical |
| SEC-047 | JazzCash stub_mode=true confirmed in production config | manual (check render.yaml env vars on Render dashboard) | JAZZCASH_STUB_MODE=true in production | High |

---

### Category 7 — WhatsApp Webhook Security

| ID | Test | Method | Expected Result | Failure Impact |
|---|---|---|---|---|
| SEC-048 | GET /whatsapp-webhooks/meta without hub.verify_token returns 403 | automated pytest | HTTP 403 | High |
| SEC-049 | GET /whatsapp-webhooks/meta with correct hub.verify_token and hub.challenge returns hub.challenge | automated pytest | HTTP 200, body = hub.challenge value | High |
| SEC-050 | POST /whatsapp-webhooks/meta without X-Hub-Signature-256 returns 401 | automated pytest | HTTP 401 | Critical |
| SEC-051 | POST /whatsapp-webhooks/meta with invalid X-Hub-Signature-256 returns 401 | automated pytest | HTTP 401 | Critical |
| SEC-052 | Valid Meta webhook event creates inbox conversation (integration) | automated pytest (requires WhatsApp adapter mock) | Conversation created in omnichannel_inbox | Medium |

---

### Category 8 — Sensitive Data Protection

| ID | Test | Method | Expected Result | Failure Impact |
|---|---|---|---|---|
| SEC-053 | GET /users/:user_id does not return password_hash | automated pytest | No `password_hash` key in response | Critical |
| SEC-054 | GET /auth/login response does not include refresh_token in body (cookie only) | automated pytest | refresh_token not in response JSON; Set-Cookie header present | High |
| SEC-055 | JWT secret not in any API response or error body | manual code review + grep | No `JWT_SECRET` value in responses | Critical |
| SEC-056 | GET /roles/:id response does not expose implementation-internal fields (e.g., password_hash of user) | automated pytest | Only role fields (id, name, label, permissions) returned | Medium |
| SEC-057 | Audit log export (GET /audit/export) is restricted to audit.logs.read scope (not audit.read) | automated pytest (auditor role test) | HTTP 403 for auditor; HTTP 200 for tenant_admin | High |
| SEC-058 | AuditLog hash-chain integrity: GET /audit/export CSV hash-chain verifiable | manual (download export, verify hash chain) | Each entry's hash matches SHA256 of previous + fields | High |

---

## Known CVEs Requiring Action

From tests/security/pip-audit.json (2026-06-20):

| Package | Current | CVE IDs | Fix Version | Priority |
|---|---|---|---|---|
| python-jose | **3.5.0 installed** (pip-audit.json stale — showed 3.3.0) | CVE-2024-33663, CVE-2024-33664, CVE-2024-29370 — **RESOLVED in 3.5.0** | N/A — already at 3.5.0 | **RESOLVED** [U10 2026-06-21] |
| starlette | 0.38.6 | GHSA-86qp-5c8j-p5mr (Host header injection), CVE-2024-47874 (multipart DoS), CVE-2025-54121 (file upload block) | 0.47.2 | High |
| pip | 25.0.1 | CVE-2025-8869 (symlink in tar), CVE-2026-1703 (path traversal in wheel), CVE-2026-3219 (tar/ZIP confusion), CVE-2026-6357 (module import ordering) | 26.1 | Medium (dev tooling, not production runtime) |

**Remediation priority:**
1. ~~Upgrade python-jose to >= 3.4.0~~ — **RESOLVED**: python-jose 3.5.0 already installed (pip-audit.json was stale). [U10 CRIT-002 2026-06-21]
2. Upgrade starlette to >= 0.47.2 (multipart DoS affects all FastAPI endpoints that accept form uploads)
3. Upgrade pip >= 26.1 (dev tooling only, lower runtime risk)

---

## Running the Security Scan

```powershell
# From D:\SaaS\CRM\backend\.venv environment:
D:\SaaS\CRM\backend\.venv\Scripts\python.exe tests/security/c5_api_security_scan.py http://localhost:3000
# Against production:
D:\SaaS\CRM\backend\.venv\Scripts\python.exe tests/security/c5_api_security_scan.py https://crm-gateway-l3rm.onrender.com
```

---

*End SECURITY_TEST_PLAN.md*
