Status: Draft
Authority Level: High
Last Reviewed: 2026-06-22
Owner: Human

# SECURITY_DISCOVERY_REPORT.md
> Security posture findings from Phase 2 Backend Authority Capture

---

## 1. Security Summary

The backend has a well-structured security foundation with JWT auth, RBAC scopes, rate limiting, HMAC webhook verification, and HTTPS. However, several gaps present real risks that require human review before the system can be considered production-hardened.

---

## 2. Authentication Security

### Strengths

| Control | Implementation |
|---|---|
| JWT signature validation | Custom `verifyJwt()` — supports HS256 and RS256 |
| Algorithm allowlist | `ALLOWED_ALGORITHMS = Set(['HS256', 'RS256'])` — "alg:none" attack blocked |
| Constant-time comparison | Used for HS256 HMAC validation (prevents timing attacks) |
| Expiry enforcement | exp checked on every request; 401 on expired token |
| nbf enforcement | Not-before claim checked if present |
| JTI uniqueness | jti claim required and checked against blocklist |
| Claim presence validation | sub, tenant_id, iss, aud all validated before request proceeds |
| OTP TTL | 6-digit OTP stored in Redis with 15-minute TTL |
| Password hashing | sha256:salt:hash format (server-side salted) |
| Rotating refresh tokens | Single-use; rotation enforced on each refresh |
| HttpOnly cookie | Refresh token delivered as HttpOnly cookie |

### Weaknesses

| Issue | Severity | Detail |
|---|---|---|
| JTI blocklist is in-memory only | HIGH | `const revokedJtis = new Set()` in jti-blocklist.js. Revocations do not survive restarts. Multi-instance deployments: revoked tokens accepted by instances that didn't process the logout. Redis-backed JTI store is the production solution. |
| Development bypass token endpoint | MEDIUM | `POST /dev/token` exists in the gateway when `JWT_SECRET` is unset. Returns an unsigned JWT. Must be confirmed unreachable in production. |
| SKIP_JWT_VERIFICATION flag | MEDIUM | When set, JWT signature is not verified. Must be confirmed absent from production environment. |
| Password hash algorithm | LOW | sha256 is a fast hash (not bcrypt/argon2). Susceptible to faster brute-force. Decision: accept or migrate. |
| Refresh token on logout | LOW | DELETE /auth/sessions/current revokes JTI (access token) but it is unconfirmed whether the refresh token DB record is also revoked. If not, attacker with refresh token can generate new access tokens post-logout. |

---

## 3. Authorization Security

### Strengths

| Control | Implementation |
|---|---|
| Scope-based RBAC | All protected routes use `requireScopes(['scope.name'])` middleware |
| Tenant isolation in scope check | `x-tenant-id` header must match `JWT.tenant_id` on every request |
| Default-deny | Scopes not in ROLE_SCOPES[role] are denied |
| JWT carries scopes | No DB lookup per request for scope validation (scopes in token) |
| System workflow protection | PATCH blocked on `is_system=true` workflows |
| Feature flag dual approval | `requires_dual_approval` flag for sensitive flag toggles |

### Weaknesses

| Issue | Severity | Detail |
|---|---|---|
| contacts.delete scope gap (H-002) | HIGH | `contacts.delete` appears in route guard (`requireScopes(['contacts.delete'])`) but is ABSENT from the SCOPES constant. This means: (a) no role can be granted this scope, and (b) if scope is dynamically assigned, the route is either always-blocked or always-open depending on empty-set comparison logic. Requires human decision. |
| leads.delete scope unverified | MEDIUM | Similar pattern to contacts.delete may affect leads.delete. TBD — REQUIRES VERIFICATION. |
| No DB-level RLS | MEDIUM | All tenant isolation is application-layer. A SQL injection or bypass of WHERE clause could expose cross-tenant data. Mitigated by semgrep CI rule but not structural. |
| Scopes in JWT payload | LOW | Revoked role changes (user demoted) are not reflected until token expires (15 min). Acceptable for short TTL but worth noting. |

---

## 4. Webhook Security

### Strengths

| Control | Implementation |
|---|---|
| HMAC signature verification | WhatsApp and payment webhooks verify HMAC-SHA256 signature from raw body |
| Raw body capture | `rawBodyCapture` middleware saves `Buffer` before JSON parsing; signature verified from original bytes |
| Webhook dead-letter | Failed webhook ingestion recorded in `messaging_db.webhook_dead_letter` |

### Weaknesses

| Issue | Severity | Detail |
|---|---|---|
| No replay attack prevention | MEDIUM | WhatsApp webhooks don't check timestamp freshness. Old webhook payloads with valid signatures can be replayed. |
| HMAC key rotation | LOW | No key rotation mechanism confirmed for JazzCash/Easypaisa HMAC keys. |

---

## 5. Transport and Infrastructure Security

### Strengths

| Control | Implementation |
|---|---|
| HTTPS enforcement | TLS terminated by Render.com load balancer |
| Helmet security headers | helmet() middleware: CSP, HSTS, X-Frame-Options, X-Content-Type-Options |
| CORS allowlist | `ALLOWED_ORIGINS` env var controls cross-origin access |
| Rate limiting | Redis sliding window (fails-open on Redis unavailability) |
| SameSite cookie | HttpOnly cookie for refresh token |

### Weaknesses

| Issue | Severity | Detail |
|---|---|---|
| Rate limit fail-open | MEDIUM | When Redis is unavailable, rate limiting falls back to in-memory Map and requests are allowed. Brute-force on login is possible during Redis outage. |
| ALLOWED_ORIGINS misconfiguration risk | LOW | If ALLOWED_ORIGINS is set to `*` in production, CORS protection is disabled. |

---

## 6. Payment Security

| Control | Implementation | Status |
|---|---|---|
| JAZZCASH_STUB_MODE | All JazzCash calls are synthetic | ACTIVE (stub) |
| EASYPAISA_STUB_MODE | All Easypaisa calls are synthetic | ACTIVE (stub) |
| Payment FSM | DB functions enforce valid status transitions | Active |
| Revenue ledger | Auto-created on payment status transitions | Active |
| Proof URL validation | HTTPS URL required on proof upload | Active |

**Note:** Payment adapters are in STUB mode. No real payment credentials are in the system. The stub path returns synthetic success without making external API calls.

---

## 7. Data Security

| Control | Status |
|---|---|
| Audit log immutability | ACTIVE — PostgreSQL RULE blocks UPDATE/DELETE on audit_log |
| Audit log hash-chain | ACTIVE — SHA256 chain verified before append |
| Custom fields JSONB | No PII scanning on JSONB fields (TBD REQUIRES VERIFICATION) |
| Encryption at rest | Managed by Render.com infrastructure (TBD) |
| Field-level encryption | NOT IMPLEMENTED — no column-level encryption found |

---

## 8. Security Gaps Register

| ID | Issue | Severity | Action required |
|---|---|---|---|
| S-001 | JTI blocklist in-memory only | HIGH | Migrate to Redis-backed JTI store before multi-instance |
| S-002 | contacts.delete scope missing from SCOPES | HIGH | Add scope to SCOPES constant; verify intended role grant |
| S-003 | Dev token endpoint in production risk | MEDIUM | Confirm /dev/token blocked by env check in production |
| S-004 | SKIP_JWT_VERIFICATION production risk | MEDIUM | Confirm absent from render.yaml and prod env |
| S-005 | Rate limit fail-open on Redis outage | MEDIUM | Consider fail-closed mode for auth endpoints |
| S-006 | Refresh token revocation on logout | LOW | Confirm DELETE /auth/sessions/current also revokes refresh token |
| S-007 | Password hash algorithm (sha256) | LOW | Human decision: accept sha256 or migrate to bcrypt/argon2 |
| S-008 | Webhook replay attack | MEDIUM | Add timestamp freshness check to webhook HMAC verification |

---

*End SECURITY_DISCOVERY_REPORT.md*
