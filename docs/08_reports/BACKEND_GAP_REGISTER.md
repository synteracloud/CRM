Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: Human

# BACKEND_GAP_REGISTER.md
> All backend implementation gaps found during Phase 2 Backend Authority Capture

---

## Gap Classification

- **Critical:** Prevents production operation; must be resolved before launch
- **High:** Security risk or missing functionality; should be resolved before launch
- **Medium:** Technical debt or incomplete feature; should be tracked and planned
- **Low:** Minor gap; acceptable for initial launch

---

## Critical Gaps

### G-CRIT-001: JTI Blocklist In-Memory Only
**Category:** Security  
**Source:** `backend/gateway/middleware/jti-blocklist.js`  
**Detail:** The JTI revocation list (`revokedJtis = new Set()`) is in-process memory only. Restarts clear it. Multi-instance deployments accept revoked tokens on instances that did not process the logout.  
**Impact:** Logged-out users can continue accessing the API with their revoked access token for up to 15 minutes.  
**Required fix:** Migrate JTI blocklist to Redis with key `rt:{jti}`, TTL matching access token TTL (15 min).  
**Safe Default (SD-002, Phase 2.97):** Accept in-memory for C6 single-instance launch. Migrate to Redis in Post-C6 Auth Hardening Sprint (bundle with G-HIGH-002). Sprint spec: `redis.setex('jti:{jti}', 900, '1')` using existing `getRedisClient()`.  
**Status:** SAFE-DEFAULT applied — deferred to Post-C6 Auth Sprint

---

### G-CRIT-002: contacts.delete Scope Absent from SCOPES Constant
**Category:** Security / Authorization  
**Source:** `backend/gateway/config/rbac-scopes.js`, `backend/gateway/routes/v1-contacts.routes.js`  
**Detail:** `contacts.delete` is referenced in `requireScopes(['contacts.delete'])` on the DELETE /contacts/:id route, but does not exist in the SCOPES constant object. Effect depends on how `requireScopes` handles unknown scope strings.  
**Impact:** Either DELETE /contacts/:id is permanently inaccessible (all users get 403) or the route has no effective scope guard.  
**Required fix:** Add `contacts.delete` to SCOPES constant; explicitly grant to `tenant_admin` and `super_admin` roles.  
**Safe Default (SD-001, Phase 2.97):** Grant CONTACTS_DELETE to tenant_admin + super_admin. Pattern is deterministic from existing 6 delete scope examples in rbac-scopes.js. Fix is 2 lines in SCOPES + 2 entries in ROLE_SCOPES. Code change requires owner approval per governance matrix (TIER 2 — rbac-scopes.js is protected). Safe default is documented; implementation pending approval.  
**Status:** SAFE-DEFAULT documented — implementation requires owner sign-off

---

## High Gaps

### G-HIGH-001: Payment Integrations in STUB Mode
**Category:** Functionality  
**Source:** `render.yaml` (JAZZCASH_STUB_MODE=true, EASYPAISA_STUB_MODE=true)  
**Detail:** Both JazzCash and Easypaisa adapters are in stub mode. No real payment processing occurs.  
**Impact:** The system cannot collect payments from customers.  
**Blockers:** P-016 (live credentials not obtained)  
**Owner:** Human — obtain credentials

### G-HIGH-002: Refresh Token NOT Revoked on Logout — CONFIRMED
**Category:** Security  
**Source:** `backend/gateway/routes/v1-auth.routes.js` lines 182–190  
**Detail:** VERIFIED 2026-06-23: DELETE /sessions/current ONLY adds the JTI to the in-memory blocklist (`addRevoked(jti, ACCESS_TOKEN_TTL_MS)`). It does NOT delete the refresh token from Redis (`rt:{refreshToken}` key remains live). After logout, an attacker with the refresh token can call POST /auth/refresh to obtain a fresh access token for up to 7 days.  
**Impact:** High — 7-day refresh token window remains open post-logout. Combined with G-CRIT-001 (in-memory JTI blocklist), the security posture on logout is compound-weak.  
**Required fix:** DELETE /sessions/current must also delete the `rt:{refreshToken}` key from Redis using the stored refresh token associated with the user's session.  
**Safe Default (SD-002, Phase 2.97):** Accept for C6 launch (single instance, small user base). Bundle fix with G-CRIT-001 in Post-C6 Auth Hardening Sprint. Fix spec: read `req.cookies?.crm_refresh_token`, call `redis.del('rt:{refreshToken}')`, clear cookie.  
**Status:** SAFE-DEFAULT applied — deferred to Post-C6 Auth Sprint

### G-HIGH-003: No Message Broker — In-Process Events Only
**Category:** Architecture  
**Source:** `backend/services/app.py`, absence of broker dependencies  
**Detail:** All events are in-process. Service restart drops all in-flight events. No durability guarantee on event delivery.  
**Impact:** Lead assignment, collections reminders, SLA notifications can be lost on restart.  
**Owner:** Human architecture decision

### G-HIGH-004: Outbox Publisher Not Implemented
**Category:** Architecture  
**Source:** `backend/db/transaction_db/schema.sql` (outbox_event table exists but no publisher found)  
**Detail:** The outbox pattern table is defined. No code was found that polls it and publishes events. Payment/billing domain events are never dispatched.  
**Impact:** Downstream consumers of payment events would never receive them.  
**Owner:** Human decision: implement or remove outbox table

### G-HIGH-005: leads.delete Scope Gap — RESOLVED (NOT A GAP)
**Category:** Security / Authorization  
**Source:** `backend/gateway/config/rbac-scopes.js` line 21  
**Detail:** VERIFIED 2026-06-23: `LEADS_DELETE: 'leads.delete'` IS present in the SCOPES constant (rbac-scopes.js line 21). No gap exists. v1-leads.routes.js does not call `requireScopes(['leads.delete'])` — leads.delete is defined but not yet wired to a route guard (informational only).  
**Status:** CLOSED — not a gap. The scope exists in the constant.

---

## Medium Gaps

### G-MED-001: No External Scheduler for task_schedule Table
**Category:** Functionality  
**Source:** `backend/db/activity_task_db/schema.sql` (task_schedule table)  
**Detail:** The task_schedule table defines cron/delayed/recurring job configs with concurrency and misfire policies. No job runner was found that reads this table and fires scheduled tasks.  
**Impact:** Scheduled tasks in the table are never executed.  
**Owner:** Human — implement scheduler or document as future scope

### G-MED-002: SLA Breach Events — RESOLVED (NOT A GAP)
**Category:** Functionality  
**Source:** `backend/services/cases/service.py` lines 120, 134, 137, 140, 144  
**Detail:** VERIFIED 2026-06-23: SLA breach events ARE emitted from `services/cases/service.py`. Confirmed event types: `case.sla.first_response_breached.v1` and `case.sla.resolution_breached.v1`. The event catalog in `backend/src/event_bus/catalog_events.py` lines 35–37 also registers all 3 SLA breach event types. The automation_journeys module wires `case.sla.breached.v1` to the case-escalation journey. SLA infrastructure is fully implemented.  
**Status:** CLOSED — not a gap. SLA breach events are emitted by services/cases/service.py.

### G-MED-003: Dev Token Endpoint — RESOLVED (NOT A GAP)
**Category:** Security  
**Source:** `render.yaml` line 37, `backend/gateway/routes/v1-auth.routes.js` (POST /dev/token)  
**Detail:** VERIFIED 2026-06-23: `JWT_SECRET` is explicitly set in render.yaml (line 37, key name `JWT_SECRET`). The dev token endpoint only fires when JWT_SECRET is absent. In production, JWT_SECRET is always present, so the dev endpoint is always disabled.  
**Status:** CLOSED — not a gap. Dev token endpoint is inactive in production.

### G-MED-004: Custom Objects — No Gateway Route File Found
**Category:** Architecture  
**Source:** `backend/src/custom_object_framework/`, `backend/src/custom_objects/` (Python modules exist); no v1-custom-objects.routes.js found  
**Detail:** The custom object builder and runtime modules exist in src/ but no corresponding gateway route file was found. Either the gateway route is missing or these modules are accessed via an undiscovered catch-all route.  
**Phase 2.97 status:** OWNER-REQUIRED (D-002) — whether K-02 (object-builder.html) is an active C6 feature or advisory shell is a product scope decision. Frontend builds K-02 as advisory shell pending decision. See OWNER_REQUIRED_COMPRESSION_REPORT.md.  
**Owner:** Human — product scope decision required

### G-MED-005: Urdu WhatsApp Template Approval Blocker (P-017)
**Category:** Functionality  
**Source:** Campaign/template validation  
**Detail:** Urdu WhatsApp templates require `urdu_approved_by` field. Native speaker approval gate not established.  
**Impact:** WhatsApp campaigns targeting Urdu speakers cannot launch.  
**Owner:** Human

### G-MED-006: Idempotency-Key Not Generated by Frontend
**Category:** Integration  
**Source:** Gap V-002 in VALIDATION_PARITY.md  
**Detail:** Frontend does not auto-generate Idempotency-Key headers. All form submissions will return 422 when pages are wired to live API.  
**Owner:** Frontend build task when wiring pages

### G-MED-007: Password Hash Algorithm (sha256 not bcrypt)
**Category:** Security  
**Source:** `backend/gateway/routes/v1-auth.routes.js`  
**Detail:** Passwords stored as `sha256:salt:hash`. SHA256 is a fast cryptographic hash, not a key-derivation function. More susceptible to brute-force than bcrypt/argon2.  
**Owner:** Human decision: accept for now or migrate

---

## Low Gaps

### G-LOW-001: DB Connection Pool Size — RESOLVED (CONFIGURABLE)
**Category:** Operations  
**Source:** `backend/gateway/db/pool.js` lines 18–19  
**Detail:** VERIFIED 2026-06-23: Pool size is `DB_POOL_MAX` env var, default 10. Pool idle timeout is `DB_POOL_IDLE_MS` (default 10000ms). Connection acquire timeout is `DB_POOL_CONN_TIMEOUT` (default 5000ms). All pool parameters are runtime-configurable via env vars without code changes.  
**Status:** CLOSED — not a gap. Pool is configurable. Set DB_POOL_MAX in render.yaml to increase under load.

### G-LOW-002: Cross-Schema FK Integrity Not Enforced at DB Level
**Category:** Data Integrity  
**Source:** All 18 DB schemas  
**Detail:** Cross-domain references (e.g. contact_id on leads) are not FK-constrained. Application layer must enforce consistency. Referential integrity failures cannot be detected by the DB.  
**Owner:** Architecture decision (accepted trade-off for schema autonomy)

### G-LOW-003: Rate Limit Fails Open on Redis Outage
**Category:** Security  
**Source:** `backend/gateway/config/redis-client.js`  
**Detail:** When Redis is unavailable, rate limiting falls back to in-memory Map. Brute-force attacks on login are possible during Redis outage.  
**Owner:** Human — consider fail-closed for auth endpoints specifically

### G-LOW-004: No DB RLS
**Category:** Security  
**Source:** All DB schemas  
**Detail:** No PostgreSQL Row Level Security found. Tenant isolation is application-layer only.  
**Owner:** Architecture decision (accepted; mitigated by semgrep CI rule)

---

*End BACKEND_GAP_REGISTER.md*
