---
Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: AI
Phase: 3.5 — Project Memory Layer Establishment
---

# SAFE_DEFAULT REGISTER

> All items resolved via safe deterministic defaults.
> Implementation proceeds on each default unless the owner explicitly objects.
> SD-001 through SD-011 from OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97.
> Owner Required: NO for all entries (except OA-001 which requires TIER 2 code-change approval).
> External Dependency: NO for all entries.

---

## SD-001: OA-001 — contacts.delete RBAC Scope Grant

**Item ID:** OA-001
**Safe Default ID:** SD-001
**Title:** contacts.delete scope missing — deterministic default: grant to tenant_admin + super_admin
**Classification:** SAFE_DEFAULT
**Current Status:** Default documented; 2-line code change pending TIER 2 approval
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md
**Evidence Source:** backend/gateway/config/rbac-scopes.js (6 existing delete scope examples as pattern); backend/gateway/routes/v1-contacts.routes.js (requireScopes(['contacts.delete']) present)
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97; DECISION_COLLAPSE_REGISTER.md Phase 3.25 (confirmed)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** contacts.delete scope is missing from rbac-scopes.js SCOPES constant. All 6 other delete operations follow identical pattern (LEADS_DELETE, DEALS_DELETE, etc.). The safe default — grant to tenant_admin and super_admin — is fully deterministic from existing patterns.

**Safe Default Detail:**
- Add `CONTACTS_DELETE: 'contacts.delete'` to SCOPES constant in backend/gateway/config/rbac-scopes.js
- Add `'contacts.delete'` to ROLE_SCOPES['tenant_admin'] array
- Add `'contacts.delete'` to ROLE_SCOPES['super_admin'] array
- Total change: 3 lines (1 SCOPES addition + 2 ROLE_SCOPES grants)

**Rationale:** Both roles already hold all other administrative delete scopes. Pattern is identical across 6 prior delete scopes. "Who gets contacts.delete?" = same roles that get every other delete scope. Fully deterministic — no judgment required.

**Frontend Assumption (active now):** contacts delete button visible to tenant_admin and super_admin only; hidden for all other roles until code change is applied. Per FINAL_CLASSIFIED_REGISTER.md frontend authority summary.

**Affected Components:** backend/gateway/config/rbac-scopes.js, backend/gateway/routes/v1-contacts.routes.js
**Affected Routes:** DELETE /contacts/:id
**Affected APIs:** Customer 360 CDP / Contacts API
**Affected Workflows:** GDPR deletion requests, data cleanup
**Affected Roles:** tenant_admin (gains contacts.delete), super_admin (gains contacts.delete); all others: no change

**Owner Required:** Code change approval required (TIER 2 per governance — rbac-scopes.js is PROTECTED)
**External Dependency:** NO

**Future Impact:** When applied: DELETE /contacts/:id returns 200 for tenant_admin and super_admin. All other roles continue to receive 403 (correct behavior). GDPR deletion requests become serviceable.

**Reopen Criteria:** If owner decides contacts should be non-deletable by policy (Option 3 from RESIDUAL_OWNER_DECISION_REGISTER.md) — would require hiding delete button in all frontends permanently.

**Related Documents:** backend/gateway/config/rbac-scopes.js, RESIDUAL_OWNER_DECISION_REGISTER.md OA-001, FRONTEND_PERMISSION_MATRIX.md
**Related Register Entries:** OA-001 (OWNER_DECISION_REGISTER.md — code change approval)

---

## SD-002: OA-002 + OA-009 — Post-C6 Auth Hardening Sprint

**Item IDs:** OA-002 (JTI blocklist), OA-009 (refresh token revocation)
**Safe Default ID:** SD-002
**Title:** Auth security hardening — accept for C6, fix in Post-C6 Auth Sprint
**Classification:** SAFE_DEFAULT
**Current Status:** Accepted for C6; sprint documented
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md (both items)
**Evidence Source:** backend/gateway/middleware/jti-blocklist.js (const revokedJtis = new Set()); backend/gateway/routes/v1-auth.routes.js lines 183–190 (no Redis del on logout); getRedisClient() available in auth routes
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97; DECISION_COLLAPSE_REGISTER.md Phase 3.25 (P-TBD-001, P-TBD-002)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** Both auth gaps are real but low-risk on C6 single-instance Render.com deployment (15-min access token TTL, managed Redis uptime, small user base). Bundle both fixes into a single Post-C6 Auth Sprint. Sprint plan is fully documented and implementable without further owner input.

**Safe Default Detail — OA-002:**
- Current: `const revokedJtis = new Set()` in jti-blocklist.js
- Default fix (Post-C6): migrate to `redis.setex('jti:{jti}', 900, '1')` with TTL = 15 minutes
- Files: backend/gateway/middleware/jti-blocklist.js (2 files, ~10 lines)
- Risk accepted for C6: gateway restart clears Set but tokens expire in 15 min anyway

**Safe Default Detail — OA-009:**
- Current: DELETE /sessions/current only calls addRevoked(jti, ACCESS_TOKEN_TTL_MS); does NOT delete refresh token
- Default fix (Post-C6): also read req.cookies?.crm_refresh_token, call redis.del('rt:{refreshToken}'), clear cookie
- Files: backend/gateway/routes/v1-auth.routes.js (3–5 lines)
- Risk accepted for C6: 7-day refresh token window; accepted on single-instance, short-session use

**Rationale:** Single Render.com instance; 15-min access token TTL limits exposure; managed Redis uptime is high; user base at C6 is small. Risk is low, not zero. Sprint plan is fully deterministic from code.

**Affected Components:** backend/gateway/middleware/jti-blocklist.js (OA-002), backend/gateway/routes/v1-auth.routes.js (OA-009)
**Affected Routes:** DELETE /auth/sessions/current (logout), all authenticated routes (JTI check)
**Affected APIs:** Auth API
**Affected Workflows:** Login/logout security model
**Affected Roles:** All authenticated users

**Owner Required:** NO (accepted risk; sprint plan documented)
**External Dependency:** NO

**Future Impact:** Post-C6 Auth Sprint (single sprint covers both): apply OA-002 Redis migration + OA-009 refresh token deletion. Both are auth route changes (TIER 2) so require TIER 2 review at implementation time.

**Reopen Criteria:** If multi-instance deployment is added before the Auth Sprint completes (risk escalates — must fix OA-002 first).

**Related Documents:** backend/gateway/middleware/jti-blocklist.js, backend/gateway/routes/v1-auth.routes.js, RESIDUAL_OWNER_DECISION_REGISTER.md OA-002 + OA-009
**Related Register Entries:** AUTH-C7b (OUT_OF_SCOPE_REGISTER.md)

---

## SD-003: OA-006 — Security Test Artifacts Disposition

**Item ID:** OA-006
**Safe Default ID:** SD-003
**Title:** Security test artifacts in tests/security/*.json — move to docs/reports/security/
**Classification:** SAFE_DEFAULT
**Current Status:** Pending next hygiene pass
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md
**Evidence Source:** tests/security/ directory; APPROVAL_RECLASSIFICATION_REPORT.md R-07, L-08
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** Conservative compliance evidence preservation is the safer default. Move JSON scan artifacts to docs/reports/security/ as version-controlled compliance evidence.

**Safe Default Detail:** `git mv tests/security/*.json docs/reports/security/` (or equivalent move). Version-control as compliance artifacts.

**Rationale:** If the scans were run for a compliance audit (likely, given the tests/security/ location), they should be preserved as evidence. Gitignoring them would lose compliance history. Conservative default: preserve.

**Affected Components:** tests/security/*.json, docs/reports/security/
**Affected Routes:** N/A
**Affected APIs:** N/A
**Affected Workflows:** CI security scan job
**Affected Roles:** N/A (infrastructure/compliance)

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** After move: update CI workflow if it references tests/security/*.json paths. Add tests/security/*.json pattern to .gitignore if they are regenerated on each CI run (to avoid tracking future outputs).

**Reopen Criteria:** If compliance framework requires these files to stay in tests/security/.

**Related Documents:** tests/security/, docs/reports/security/, .github/workflows/ci.yml
**Related Register Entries:** None

---

## SD-004: OA-007 — Load Test Reports Disposition

**Item ID:** OA-007
**Safe Default ID:** SD-004
**Title:** Load test reports in tests/load/reports/ — preserve c5-prod-* files
**Classification:** SAFE_DEFAULT
**Current Status:** Pending next hygiene pass
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md
**Evidence Source:** tests/load/reports/c5-prod-*.html (production load test results from Phase C5)
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** Phase C5 production load test results are a performance baseline. Move c5-prod-*.html to docs/reports/load/. Gitignore non-c5-prod (development) load test outputs.

**Safe Default Detail:**
- `git mv tests/load/reports/c5-prod-*.html docs/reports/load/`
- Add `tests/load/reports/` (excluding c5-prod files) to .gitignore

**Rationale:** c5-prod-*.html are historical performance evidence from the production smoke test phase. They should be preserved. Development/local load test outputs do not need version control.

**Affected Components:** tests/load/reports/, docs/reports/load/
**Affected Routes:** N/A
**Affected APIs:** N/A
**Affected Workflows:** Load testing
**Affected Roles:** N/A

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** New load test runs produce output in tests/load/reports/ (gitignored). Preserve significant baselines by moving to docs/reports/load/ manually.

**Reopen Criteria:** If all load test outputs should be version-controlled.

**Related Documents:** tests/load/reports/, docs/reports/load/
**Related Register Entries:** None

---

## SD-005: OA-008 — Password Hashing Accept SHA-256 for C6

**Item ID:** OA-008
**Safe Default ID:** SD-005
**Title:** Password hashing SHA-256 — accept for C6, plan bcrypt for C7
**Classification:** SAFE_DEFAULT
**Current Status:** Accepted for C6
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md
**Evidence Source:** backend/gateway/routes/v1-auth.routes.js (SHA-256 hashing); package.json (no bcrypt/argon2)
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** Accept SHA-256 for C6 launch. At C6 scale (small user base), Render.com managed PostgreSQL DB access controls mitigate the brute-force risk sufficiently. Plan transparent re-hash-on-login (bcrypt) for C7 Security Sprint.

**Safe Default Detail:**
- C6: No change. SHA-256:salt:hash pattern remains.
- C7: On first successful login post-deploy, if hash is SHA-256 format: verify with SHA-256, then re-hash with bcrypt and update DB. Transparent to user.
- Implementation: ~15 lines in v1-auth.routes.js. Add `bcrypt` to package.json.

**Rationale:** Risk at small scale with managed DB: low (brute-force requires DB access). Risk at scale: medium (if DB is breached). Re-hash-on-login (Option C) is the cleanest migration with zero user disruption.

**Affected Components:** backend/gateway/routes/v1-auth.routes.js
**Affected Routes:** POST /auth/login, POST /auth/register
**Affected APIs:** Auth API
**Affected Workflows:** Login, registration
**Affected Roles:** All users

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** C7 Security Sprint: add bcrypt to package.json, implement re-hash-on-login logic. Users transparently upgraded to bcrypt on next login.

**Reopen Criteria:** If a data breach occurs before C7 bcrypt migration (must accelerate C7 sprint).

**Related Documents:** backend/gateway/routes/v1-auth.routes.js, RESIDUAL_OWNER_DECISION_REGISTER.md OA-008
**Related Register Entries:** AUTH-C7 (OUT_OF_SCOPE_REGISTER.md)

---

## SD-006: G-HIGH-003 — No Message Broker

**Item ID:** G-HIGH-003
**Safe Default ID:** SD-006
**Title:** No message broker — accept in-process events for C6
**Classification:** SAFE_DEFAULT
**Current Status:** Accepted for C6
**Original Source:** BACKEND_GAP_REGISTER.md
**Evidence Source:** backend/src/event_bus/core.py InMemoryEventBus; no broker dependency in requirements.txt or package.json
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** In-process event dispatch via InMemoryEventBus is acceptable for C6 single-instance deployment. Message broker adds operational complexity not justified until multi-instance. Evaluate at C7.

**Rationale:** Single Render.com instance; event loss on restart is possible but rare; volume is C6-scale (small). InMemoryEventBus has retry + dead-letter queue built in. Broker complexity (RabbitMQ, Redis Streams, etc.) is premature at launch.

**Affected Components:** backend/src/event_bus/core.py, all event publishers in backend/services/
**Affected Routes:** N/A (internal events)
**Affected APIs:** N/A (internal)
**Affected Workflows:** All 5 system workflows (event-driven)
**Affected Roles:** N/A

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** C7 Architecture Sprint: evaluate message broker when multi-instance deployment is needed. InMemoryEventBus interface is stable — swap implementation without changing publishers.

**Reopen Criteria:** If multi-instance deployment is needed before C7 (escalates event loss risk).

**Related Documents:** backend/src/event_bus/, backend/docs/infrastructure/event-catalog.md
**Related Register Entries:** BROKER-C7 (OUT_OF_SCOPE_REGISTER.md), EVENT_BUS_TBD (AUTO_CLOSED_REGISTER.md)

---

## SD-007: G-HIGH-004 — Outbox Publisher Not Implemented

**Item ID:** G-HIGH-004
**Safe Default ID:** SD-007
**Title:** Outbox publisher absent — accept for C6 (payments in stub mode)
**Classification:** SAFE_DEFAULT
**Current Status:** Accepted for C6
**Original Source:** BACKEND_GAP_REGISTER.md
**Evidence Source:** grep -r "outbox" backend/src/ = no matches; db/transaction_db/schema.sql outbox table exists
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** Outbox publisher is a C7 concern. C6 payment domain is in stub mode (OA-003 unresolved). Outbox pattern becomes mandatory when real payments activate. Outbox table schema is already in place.

**Rationale:** The outbox pattern ensures at-least-once delivery for payment events. Since all payment processing is stubbed in C6, there are no real payment events to lose. Implementing the publisher before payments are live would be premature.

**Affected Components:** backend/db/transaction_db/schema.sql (outbox table), backend/src/ (no publisher yet)
**Affected Routes:** Payment processing routes (when activated)
**Affected APIs:** Billing/Payment API
**Affected Workflows:** WF-002 (collections invoicing)
**Affected Roles:** N/A

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** When OA-003 is resolved (payment credentials received): implement outbox publisher in backend/src/billing/ using the existing outbox table. Treat as mandatory in the same sprint as payment activation.

**Reopen Criteria:** If payment mode is switched from stub to live before the outbox publisher is implemented.

**Related Documents:** backend/db/transaction_db/schema.sql, OA-003 (EXTERNAL_DEPENDENCY_REGISTER.md)
**Related Register Entries:** OUTBOX_TBD (AUTO_CLOSED_REGISTER.md)

---

## SD-008: G-MED-001 — No External Task Scheduler

**Item ID:** G-MED-001
**Safe Default ID:** SD-008
**Title:** No external task scheduler — accept for C6
**Classification:** SAFE_DEFAULT
**Current Status:** Accepted for C6
**Original Source:** BACKEND_GAP_REGISTER.md
**Evidence Source:** db/activity_task_db/schema.sql task_schedule table exists but unused; no Celery/APScheduler in requirements.txt
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** task_schedule table is unused in C6. No scheduled task runner is needed at C6 scale. Implement Celery Beat or APScheduler in C7 when scheduled tasks become required.

**Rationale:** All C6 system workflows (WF-001 through WF-005) are event-driven (not schedule-based). No timed background jobs are currently active. The task_schedule table was built speculatively. Celery Beat adds operational complexity (worker process) not justified until needed.

**Affected Components:** db/activity_task_db/schema.sql (task_schedule table unused), backend/ (no scheduler process)
**Affected Routes:** N/A
**Affected APIs:** N/A
**Affected Workflows:** N/A (all workflows are event-triggered, not schedule-triggered)
**Affected Roles:** N/A

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** C7: when scheduled tasks are required (e.g., daily digest emails, weekly reports), add Celery Beat (natural fit for Python/FastAPI stack) or APScheduler. Use task_schedule table as queue.

**Reopen Criteria:** If a C6 feature requires scheduled execution (must implement scheduler before feature can launch).

**Related Documents:** db/activity_task_db/schema.sql, backend/requirements.txt
**Related Register Entries:** SCHED-C7 (OUT_OF_SCOPE_REGISTER.md)

---

## SD-009: D-005 — 4 Backend Archive Docs in Wrong Location

**Item ID:** D-005
**Safe Default ID:** SD-009
**Title:** 4 backend archive docs — move to docs/08_reports/ via SAFE_REPOSITORY_HYGIENE
**Classification:** SAFE_DEFAULT
**Current Status:** Pending hygiene pass
**Original Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md
**Evidence Source:** backend/docs/phase4-gap-register.md and 3 other historical artifact docs
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** The 4 files are historical build-phase artifacts. They belong in docs/08_reports/ or docs/_archive/, not in backend/docs/. Apply SAFE_REPOSITORY_HYGIENE (no owner decision needed for organizational moves of historical artifacts).

**Safe Default Detail:**
- `git mv backend/docs/phase4-gap-register.md docs/08_reports/`
- Apply same pattern to the other 3 historical artifact docs
- Verify no file is referenced in active authority docs before moving

**Rationale:** backend/docs/ should contain current architecture documentation only. Historical gap registers and phase reports belong in docs/08_reports/ (per SAFE_REPOSITORY_HYGIENE_POLICY.md).

**Affected Components:** backend/docs/ (4 files), docs/08_reports/
**Affected Routes:** N/A
**Affected APIs:** N/A
**Affected Workflows:** N/A
**Affected Roles:** N/A

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** After move: backend/docs/ is clean. Historical artifacts are findable in docs/08_reports/. Update any cross-references in active docs if they reference the moved files.

**Reopen Criteria:** N/A — hygiene task, permanently closed once executed.

**Related Documents:** backend/docs/phase4-gap-register.md, docs/08_reports/, SAFE_REPOSITORY_HYGIENE_POLICY.md
**Related Register Entries:** None

---

## SD-010: G-LOW-003 — Rate Limit Fails Open on Redis Outage

**Item ID:** G-LOW-003
**Safe Default ID:** SD-010
**Title:** Rate limiter fails open on Redis outage — accept for C6
**Classification:** SAFE_DEFAULT
**Current Status:** Accepted for C6
**Original Source:** BACKEND_GAP_REGISTER.md
**Evidence Source:** backend/gateway/config/redis-client.js (fail-open pattern); render.yaml (managed Redis crm-redis)
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** Fail-open on Redis outage is a known, accepted pattern for rate limiters at C6 scale. Render.com managed Redis has high uptime. Adding fail-closed complexity is premature before scale.

**Rationale:** If Redis is unavailable, rate limiting is disabled and all requests pass through. Risk: brief unprotected window during Redis restart. Mitigation: Render.com managed Redis SLA. Fail-closed would block all requests on Redis outage — worse user experience than brief unprotected window at C6 scale.

**Affected Components:** backend/gateway/config/redis-client.js, backend/gateway/middleware/rate-limit-hook.js
**Affected Routes:** All rate-limited routes (auth endpoints, API endpoints)
**Affected APIs:** All
**Affected Workflows:** All
**Affected Roles:** All

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** C7 hardening: consider fail-closed for auth endpoints (POST /auth/login, POST /auth/register) specifically, while keeping fail-open for non-auth routes.

**Reopen Criteria:** If a rate-limit bypass attack occurs during a Redis outage window (accelerates C7 hardening).

**Related Documents:** backend/gateway/config/redis-client.js, backend/gateway/middleware/rate-limit-hook.js
**Related Register Entries:** None

---

## SD-011: G-LOW-004 — No PostgreSQL RLS

**Item ID:** G-LOW-004
**Safe Default ID:** SD-011
**Title:** No PostgreSQL Row Level Security — accepted architecture trade-off
**Classification:** SAFE_DEFAULT
**Current Status:** Permanent — no change planned
**Original Source:** BACKEND_GAP_REGISTER.md
**Evidence Source:** All 18 DB schemas (no RLS policies); .semgrep/tenant-isolation.yaml (application-layer enforcement); gateway/middleware/auth-rbac.js (x-tenant-id binding)
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** Application-layer tenant isolation with semgrep CI enforcement is the accepted architecture. PostgreSQL RLS would require Alembic migrations + performance impact analysis — out of scope for C6. Semgrep CI guard provides equivalent protection at the code level.

**Rationale:** The architecture decision (ADR-001) establishes application-layer isolation enforced by x-tenant-id binding on every SQL query. Semgrep CI rule (.semgrep/tenant-isolation.yaml) enforces this pattern — any query that omits tenant_id binding fails CI. This is the documented and frozen architecture. Adding PostgreSQL RLS would be additive complexity without a proven gap in the current model.

**Affected Components:** All 18 DB schemas, .semgrep/tenant-isolation.yaml, gateway/middleware/auth-rbac.js
**Affected Routes:** All DB-backed routes
**Affected APIs:** All
**Affected Workflows:** All
**Affected Roles:** All (tenant isolation applies to all roles)

**Owner Required:** NO (architecture decision confirmed; no change)
**External Dependency:** NO

**Future Impact:** None. Architecture is frozen. If RLS is added in future, it is additive — existing application-layer isolation remains.

**Reopen Criteria:** If a cross-tenant data leak is discovered in production (would require emergency RLS implementation).

**Related Documents:** ADR-001_PROJECT_FOUNDATION.md, .semgrep/tenant-isolation.yaml, AI_OPERATING_CONTEXT.md FROZEN_DECISIONS
**Related Register Entries:** None

---

*End SAFE_DEFAULT_REGISTER.md — 12 items (SD-001 through SD-011, with SD-002 covering 2 items OA-002+OA-009) — Phase 3.5 (2026-06-23)*
