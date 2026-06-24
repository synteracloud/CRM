Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: Human

# RESIDUAL OWNER DECISION REGISTER — Phase 2.9
> Only genuine owner decisions that cannot be resolved from repository evidence alone.
> Each item proves why repository evidence is exhausted and why human judgment is required.

---

## How to Use This Register

These items require a human decision. For each:
1. Read the Evidence Reviewed section to understand what was inspected
2. Read Evidence Exhausted to understand why code cannot resolve it
3. Choose one of the options
4. Inform the development team of your decision

**Priority order for commercial launch:** OA-001 → OA-009/OA-002 (auth hardening) → OA-003 → OA-008 → OA-004 → OA-005 → OA-006/OA-007

---

## Critical — Must Decide Before Launch

### OA-001: contacts.delete RBAC Scope Missing
**Issue:** `contacts.delete` scope referenced in v1-contacts.routes.js but absent from rbac-scopes.js SCOPES constant. DELETE /contacts/:id returns 403 for ALL users including tenant_owner and super_admin.

**Evidence Reviewed:**
- `backend/gateway/config/rbac-scopes.js` — CONTACTS_DELETE absent (grep returns no match)
- `backend/gateway/routes/v1-contacts.routes.js` — `requireScopes(['contacts.delete'])` present on DELETE route
- `backend/gateway/config/rbac-scopes.js` — All other delete scopes follow pattern: `LEADS_DELETE: 'leads.delete'` (line 21), `DEALS_DELETE: 'deals.delete'`, etc.
- Fix pattern is fully derivable from 6 existing delete scope examples in rbac-scopes.js

**Evidence Exhausted:** The code fix is technically determinable (add 1 line to SCOPES constant, add scope to ROLE_SCOPES for tenant_admin + super_admin). But rbac-scopes.js is explicitly listed in REVISED_DECISION_ESCALATION_MATRIX.md as a TIER 2 touchpoint ("Does the action touch rbac-scopes.js?" → YES → TIER 2 REQUIRES_APPROVAL).

**Possible Resolutions:**
1. Add `CONTACTS_DELETE: 'contacts.delete'` to SCOPES, grant to tenant_admin + super_admin (and optionally tenant_owner)
2. Remove the requireScopes guard, replace with role-only check
3. Accept as intentional — contacts cannot be deleted (hide delete button in all frontends)

**Risks:** Option 3 means contacts are permanent. Any GDPR deletion request is unserviceable from the API.

**Tradeoffs:** Option 1 is 2 lines of code + 2 lines of ROLE_SCOPES grant. Option 3 requires frontend to hide all delete controls.

**Recommended Option:** Option 1 — match existing pattern.

**Why Repository Cannot Determine:** Which roles should receive contacts.delete scope (tenant_owner, tenant_admin, both, or all) is a product policy decision. The code pattern shows the how; the who requires owner judgment.

---

### OA-003: JazzCash/Easypaisa Stub Mode
**Issue:** Both payment adapters in STUB mode. No real payments can be collected.

**Evidence Reviewed:**
- `render.yaml` — `JAZZCASH_STUB_MODE=true`, `EASYPAISA_STUB_MODE=true`
- `backend/adapters/pakistan/payments/jazzcash.py` — stub adapter confirmed
- `backend/adapters/pakistan/payments/easypaisa.py` — stub adapter confirmed
- `backend/src/billing/` — billing module built and tested; adapter calls all stub

**Evidence Exhausted:** Activating live payments requires obtaining merchant credentials from JazzCash and Easypaisa — external vendor relationships. Repository contains no credentials and cannot generate them.

**Possible Resolutions:**
1. Obtain JazzCash merchant credentials + sandbox test → switch to live
2. Obtain Easypaisa credentials separately (may take longer)
3. Launch without payment — disable billing-settings.html (G-04) payment section in frontend
4. Defer to Phase C7 post-launch

**Risks:** Options 3/4 mean no revenue collection at launch.

**Tradeoffs:** Options 1+2 require vendor account applications (typically 2–4 weeks in Pakistan). Option 3 allows launch with free-tier CRM; billing can be enabled later.

**Recommended Option:** Option 1+2 (obtain both before launch), or Option 3 if timeline is critical.

**Why Repository Cannot Determine:** Vendor credential acquisition is a business relationship/commercial action, not a code decision.

---

## High — Security Hardening Before Scale

### OA-002: JTI Blocklist In-Memory
**Issue:** JTI revocation blocklist uses `new Set()` in-process memory. Gateway restart clears it. Multi-instance deployments accept revoked tokens on instances that didn't process the logout.

**Evidence Reviewed:**
- `backend/gateway/middleware/jti-blocklist.js` — `const revokedJtis = new Set()`
- Redis client already wired in gateway (`getRedisClient()` imported in auth routes)
- `render.yaml` — Redis service (crm-redis) confirmed live
- Single Render.com instance currently (no auto-scale configured)

**Evidence Exhausted:** The fix is technically determinable: migrate to `redis.setex('jti:{jti}', 900, '1')` with TTL = 15min. But implementing this involves changing auth middleware (TIER 2 per governance), and the timing decision (launch with in-memory vs. fix before scale) is an operations policy decision.

**Possible Resolutions:**
1. Fix now — migrate JTI blocklist to Redis before launch
2. Accept for launch — document as scaling prerequisite; fix when adding second instance
3. Reduce access token TTL (5 min) to shrink exposure window

**Risks:** On current single-instance Render.com deployment, risk is low (restart clears Set but tokens expire in 15 min anyway). Risk escalates on auto-scale or deploy.

**Tradeoffs:** Option 1 adds Redis dependency to jti-blocklist.js (2 files, ~10 lines). Option 2 accepts known risk with clear documentation.

**Recommended Option:** Option 2 (accept for launch, document). Combined with fixing OA-009 (refresh token revocation) in the same auth hardening sprint.

**Why Repository Cannot Determine:** Risk tolerance and sprint timing for security improvements are product/operations policy decisions.

---

### OA-009: Refresh Token Not Revoked on Logout (New — Discovered Phase 2.9)
**Issue:** DELETE /auth/sessions/current only revokes the access token JTI in memory. Refresh token (`rt:{refreshToken}` in Redis) remains valid for 7 days. Attacker with stolen refresh token can obtain fresh access tokens post-logout.

**Evidence Reviewed:**
- `backend/gateway/routes/v1-auth.routes.js` lines 183–190: only `addRevoked(jti, ACCESS_TOKEN_TTL_MS)` called on logout
- Lines 193–211: POST /auth/refresh reads `rt:{refreshToken}` from Redis — NOT deleted on logout
- Redis client available (`getRedisClient()`) and used in the same file

**Evidence Exhausted:** The fix is technically determinable: in DELETE /sessions/current, also read `req.cookies?.crm_refresh_token`, call `redis.del('rt:{refreshToken}')`, and clear the cookie. This is an auth route change (TIER 2 per governance).

**Possible Resolutions:**
1. Fix DELETE /sessions/current to also delete `rt:{refreshToken}` from Redis
2. Accept for launch — document as known constraint (low risk on single-instance, short-session use)
3. Add shorter refresh token TTL (e.g., 24h instead of 7 days) to reduce exposure window

**Risks:** Option 2 means any logged-out session can be re-authenticated with a stolen refresh token for up to 7 days. Combined with OA-002 (JTI blocklist clears on restart), the logout security model is weak.

**Tradeoffs:** Option 1 is 3–5 lines of code. Should be bundled with OA-002 Redis migration in a single auth hardening sprint. Option 3 reduces the exposure window without touching auth logic.

**Recommended Option:** Option 1 — bundle with OA-002 Redis migration as a single "auth hardening" sprint. Both issues have the same root cause (stateless logout).

**Why Repository Cannot Determine:** Auth security changes are explicitly TIER 2 per governance matrix ("Does the action touch auth-rbac.js, JTI blocklist, or any route file?" → YES).

---

## Medium — Should Decide Before or During Frontend Authority Capture

### OA-004: AI Inference Model Selection
**Issue:** All AI features use rule-based weighted-sum scoring. No LLM inference provider SDK is installed. ai-copilot.html (M-01) and ai-insights.html (M-02) are advisory-only shells.

**Evidence Reviewed:**
- `backend/requirements.txt` — no openai, anthropic, google-generativeai packages
- `backend/src/ai_copilot/services.py` — rule_based scoring functions
- `backend/src/ai_insights/services.py` — rule_based models

**Evidence Exhausted:** Provider selection (Anthropic Claude, OpenAI, Google Gemini, or none) requires knowledge of budget, data privacy requirements, and product positioning. Repository cannot supply these.

**Possible Resolutions:**
1. Add Claude Haiku (cheap, fast) — add `anthropic` to requirements.txt, set ANTHROPIC_API_KEY in render.yaml
2. Add OpenAI GPT-4o-mini — add `openai` to requirements.txt, set OPENAI_API_KEY
3. Keep rule-based for C6 launch, plan LLM for C7
4. Remove AI pages from navigation for now

**Risks:** Options 3/4 mean AI pages exist but show only basic rule-based insights. Not commercially blocking unless AI is in the product pitch.

**Recommended Option:** Option 3 (rule-based for launch) — reduces scope. Plan LLM integration as C7 feature.

**Why Repository Cannot Determine:** Provider selection, API cost budget, and data privacy policy are business decisions.

---

### OA-005: contract_lifecycle_management No Gateway Route
**Issue:** backend/src/contract_lifecycle_management/ is fully implemented with 12 API endpoints. No v1-contracts.routes.js exists in gateway/routes/.

**Evidence Reviewed:**
- `backend/src/contract_lifecycle_management/api.py` — API_ENDPOINTS dict with 12 endpoint definitions
- `backend/gateway/routes/` — no v1-contracts.routes.js
- MODULE_INVENTORY.md §29 — notes "gateway route required; human decision"
- Pattern for adding route is clear from 43 existing v1-*.routes.js files

**Evidence Exhausted:** The gateway route could be created from the existing 12 endpoint definitions + any existing routes as pattern. But whether contracts are in the active product for C6 launch is a product scope decision.

**Possible Resolutions:**
1. Create v1-contracts.routes.js — expose all 12 endpoints with appropriate RBAC scopes
2. Defer contracts module to C7 — mark as inactive in frontend
3. Archive the Python module as unused (not recommended — module is tested and complete)

**Risks:** Option 2 means contracts page (if any) has no API. Option 1 requires RBAC scope additions for contracts.* (triggers OA-001 pattern — another scope update).

**Recommended Option:** Option 2 for C6 launch if no contracts page is in DESIGN-SPEC.md. Option 1 if a contracts page exists in the frontend.

**Why Repository Cannot Determine:** Whether contracts is in the C6 product pitch requires product roadmap knowledge not in the repository.

---

## Low — Policy Decisions (Non-Blocking for Launch)

### OA-006: Security Test Artifacts (tests/security/*.json)
**Issue:** JSON scan artifacts in tests/security/ — unclear if compliance evidence or regenerated CI outputs.

**Evidence Reviewed:** Directory confirmed to exist; specific files not read.

**Evidence Exhausted:** Whether these files are legally required compliance artifacts or CI-regenerated outputs requires knowledge of the compliance framework being followed.

**Possible Resolutions:**
1. Move to docs/reports/security/ — version-control as compliance evidence
2. Add to .gitignore — treat as regenerated CI outputs

**Recommended Option:** Option 1 if the scans were manually run for a compliance audit. Option 2 if CI regenerates them on every run.

**Why Repository Cannot Determine:** Compliance framework and evidence preservation policy are legal/compliance decisions.

---

### OA-007: Load Test Reports (tests/load/reports/*.html)
**Issue:** Load test HTML reports including c5-prod-*.html (production load test results from Phase C5).

**Evidence Reviewed:** Directory confirmed; c5-prod-*.html mentioned in APPROVAL_RECLASSIFICATION_REPORT.

**Possible Resolutions:**
1. Move c5-prod-*.html to docs/reports/load/ — version-control as performance evidence
2. Gitignore all load test outputs

**Recommended Option:** Option 1 for the c5-prod files (historical performance baseline). Option 2 for development reports.

**Why Repository Cannot Determine:** Performance evidence preservation is an engineering policy decision.

---

### OA-008: Password Hashing Algorithm (sha256 not bcrypt)
**Issue:** Passwords stored as sha256:salt:hash. SHA256 is not a KDF — more susceptible to brute-force than bcrypt/argon2.

**Evidence Reviewed:** v1-auth.routes.js password hashing pattern confirmed in prior audits. bcrypt not in package.json.

**Possible Resolutions:**
1. Accept sha256 for C6 launch — document as known constraint, migrate in C7
2. Migrate to bcrypt before launch (requires re-hashing existing users)
3. Add re-hash-on-login (transparent migration — bcrypt on first successful login post-deployment)

**Risks:** Option 1 is acceptable at small-scale launch with proper DB access controls. If DB is breached, sha256 passwords crack faster than bcrypt.

**Recommended Option:** Option 1 (accept for launch). Plan Option 3 (transparent migration) for C7 once user base is established.

**Why Repository Cannot Determine:** Security risk tolerance and migration timing are security policy decisions.

---

*End RESIDUAL_OWNER_DECISION_REGISTER.md*
