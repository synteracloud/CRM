Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: Human

# OWNER APPROVAL ITEMS BEFORE PHASE 3 (FRONTEND AUTHORITY CAPTURE)
> Items requiring human owner decision before Frontend Authority Capture begins.
> These are blocking or high-risk items only. All SAFE_REPOSITORY_HYGIENE items are executed autonomously.

---

## Critical — Must Decide Before Launch

### OA-001: contacts.delete RBAC Scope Gap

**Issue:**
`contacts.delete` scope is referenced in `v1-contacts.routes.js` route guard (`requireScopes(['contacts.delete'])`) but does NOT exist in the SCOPES constant in `backend/gateway/config/rbac-scopes.js`. Effect: DELETE /contacts/:id returns 403 for ALL authenticated users including tenant_owner and super_admin.

**Evidence:**
- `backend/gateway/config/rbac-scopes.js` — grep for `contacts.delete` or `CONTACTS_DELETE` returns no matches
- `backend/gateway/routes/v1-contacts.routes.js` — `requireScopes(['contacts.delete'])` is present
- Verified 2026-06-23 in this audit

**Options:**
1. Add `CONTACTS_DELETE: 'contacts.delete'` to SCOPES constant and grant to `tenant_admin`, `super_admin` (and optionally `tenant_owner`)
2. Remove the `requireScopes(['contacts.delete'])` guard and replace with a simpler role check
3. Leave as-is (contacts cannot be deleted — accept as intentional product behavior)

**Risk:**
Critical — contacts cannot be deleted from the live system. Any data cleanup or GDPR deletion request is blocked. If option 3 is chosen, delete buttons in the frontend must be hidden for all roles.

**Recommendation:**
Option 1 — add the scope, grant to tenant_admin and super_admin. This is the lowest-risk path. A 2-line code change.

---

### OA-002: JTI Blocklist In-Memory Only

**Issue:**
The JWT revocation blocklist is implemented as an in-process `Set()` in `backend/gateway/middleware/jti-blocklist.js`. On gateway restart or multi-instance deployment, the blocklist is cleared. A user who logged out can continue accessing the API with a revoked access token for up to 15 minutes on any gateway instance that restarted or did not process the logout.

**Evidence:**
- `backend/gateway/middleware/jti-blocklist.js` — `const revokedJtis = new Set()`
- Render.com deployment: gateway runs as a single service instance. Multi-instance only occurs on scale-up.
- Gap G-CRIT-001 in BACKEND_GAP_REGISTER.md

**Options:**
1. Migrate JTI blocklist to Redis — key `jti:{jti}`, TTL = 15 minutes (matching access token TTL). Requires `redis-client.js` dependency in jti-blocklist.js.
2. Leave as-is — accept 15-minute window for revoked tokens. Acceptable on single-instance deployment.
3. Reduce access token TTL (e.g., 5 min) to shrink the exposure window.

**Risk:**
High — revoked tokens remain valid for up to 15 minutes on restart. On Render.com free tier (single instance), risk is low day-to-day. On any auto-scaling scenario, risk escalates.

**Recommendation:**
Option 2 (accept for launch), with Option 1 as a pre-scale milestone. Document in KNOWN_CONSTRAINTS as a scaling prerequisite.

---

### OA-003: JazzCash/Easypaisa Stub Mode

**Issue:**
Both payment adapters are in stub mode (`JAZZCASH_STUB_MODE=true`, `EASYPAISA_STUB_MODE=true` in `render.yaml`). No real payment processing occurs. The system cannot collect payments from customers.

**Evidence:**
- `render.yaml` — stub mode env vars set
- `backend/adapters/pakistan/payments/jazzcash.py` — stub adapter
- `backend/adapters/pakistan/payments/easypaisa.py` — stub adapter
- Constraint P-016 in AI_OPERATING_CONTEXT.md
- Gap G-HIGH-001 in BACKEND_GAP_REGISTER.md

**Options:**
1. Obtain JazzCash sandbox credentials, test in sandbox, then switch to live credentials
2. Obtain Easypaisa credentials separately
3. Launch with stub mode — block payment flows in frontend until credentials obtained
4. Defer to post-launch Phase C7

**Risk:**
High for commercial launch — billing-settings.html (G-04) payment section is static stub, and all POST /payments calls return stub responses. No revenue can be collected.

**Recommendation:**
Option 1+2 (obtain both sets of sandbox credentials before launch). This is the only commercial blocker besides the OA-001 contacts.delete bug.

---

## High — Should Decide Before Frontend Authority Capture

### OA-004: AI Inference Model Selection

**Issue:**
All AI functionality (ai-copilot.html M-01, ai-insights.html M-02) is rule-based weighted-sum only. No AI inference provider SDK is installed in `requirements.txt`. The AI copilot page is an "advisory-only shell." No OpenAI/Anthropic/Google SDK is present.

**Evidence:**
- `backend/src/ai_copilot/` — services use rule_based scoring
- `backend/requirements.txt` — no openai, anthropic, google-generativeai packages
- Constraint AI-001 in AI_OPERATING_CONTEXT.md
- Gap in BACKEND_GAP_REGISTER.md

**Options:**
1. Select an AI inference provider (Anthropic Claude, OpenAI GPT-4, Google Gemini) — add SDK, configure API key in render.yaml
2. Keep rule-based for launch — remove AI copilot from navigation or mark as "coming soon"
3. Implement a lightweight LLM call (Claude Haiku or GPT-3.5 mini) for low cost

**Risk:**
Medium for launch — AI copilot pages exist but show only rule-based insights. Not commercially blocking if marketed accurately. Blocking only if AI features are in the product pitch.

**Recommendation:**
Option 3 (Claude Haiku or equivalent) — adds inference capability with minimal cost. Configure ANTHROPIC_API_KEY in render.yaml.

---

### OA-005: contract_lifecycle_management — No Gateway Route

**Issue:**
`backend/src/contract_lifecycle_management/` contains a fully implemented Python module with 12 API endpoints defined in `api.py::API_ENDPOINTS`. However, no corresponding `v1-contracts.routes.js` file exists in `backend/gateway/routes/`. The contract management module has no live API surface.

**Evidence:**
- `backend/src/contract_lifecycle_management/api.py` — 12 API endpoints defined as constants
- `backend/gateway/routes/` — no v1-contracts.routes.js
- MODULE_INVENTORY.md §29 — "Human decision required: Add gateway route + RBAC scope"
- Gap G-MED-004 in BACKEND_GAP_REGISTER.md

**Options:**
1. Create `v1-contracts.routes.js` in gateway — expose all 12 endpoints, add RBAC scopes
2. Defer contract module — mark as Phase C7, hide in frontend
3. Archive the Python module as unused until needed

**Risk:**
Low for immediate launch — no frontend page maps to contracts. The module does not break anything if unexposed. Risk is wasted code if no contracts page is planned.

**Recommendation:**
Option 1 for completeness (the module is built and tested), or Option 2 if contracts are not in the active product pitch.

---

## Medium — Compliance / Policy Decisions

### OA-006: Security Test Artifacts (tests/security/*.json)

**Issue:**
Security scan output files (`.json`) in `tests/security/` may be compliance evidence or may be regenerated CI outputs. The owner must decide disposition before these are committed/removed.

**Evidence:**
- `tests/security/` directory (contents not read in this audit)
- APPROVAL_RECLASSIFICATION_REPORT.md R-07, L-08

**Options:**
1. Version-control as compliance evidence → move to `docs/reports/security/`
2. Gitignore as regenerated CI outputs → add `tests/security/*.json` to .gitignore

**Risk:**
Low — no runtime impact.

**Recommendation:**
Option 1 if the scans are point-in-time compliance artifacts. Option 2 if CI regenerates them on every run.

---

### OA-007: Load Test Reports (tests/load/reports/*.html)

**Issue:**
Load test HTML reports exist in `tests/load/reports/`. Two production reports (c5-prod-*.html) may be valuable performance evidence.

**Evidence:**
- APPROVAL_RECLASSIFICATION_REPORT.md R-08, L-09

**Options:**
1. Version-control as performance evidence → move to `docs/reports/load/`
2. Gitignore as regenerated load test outputs

**Risk:**
Low — no runtime impact.

**Recommendation:**
Option 1 for the c5-prod-*.html reports (historical performance evidence). Option 2 for development-environment reports.

---

### OA-008: Password Hashing Algorithm (sha256 not bcrypt)

**Issue:**
Passwords are stored as `sha256:salt:hash`. SHA256 is a fast cryptographic hash, not a key-derivation function (KDF). This makes brute-force attacks significantly easier compared to bcrypt/argon2.

**Evidence:**
- `backend/gateway/routes/v1-auth.routes.js` — password hashing logic
- Gap G-MED-007 in BACKEND_GAP_REGISTER.md

**Options:**
1. Accept sha256 for launch — document as known risk, migrate post-launch
2. Migrate to bcrypt before launch (requires re-hashing existing user passwords)
3. Add argon2 or bcrypt with a migration script (re-hash on next login)

**Risk:**
Medium — not immediately exploitable without database access. If database is breached, sha256 passwords crack faster. In a SaaS context with small initial user base, risk is low at launch.

**Recommendation:**
Option 1 (accept for launch, document as P-xxx constraint). Plan migration for C7 when user base is established.

---

---

### OA-009: Refresh Token Not Revoked on Logout

**Issue:**
DELETE /auth/sessions/current (logout) only adds the access token JTI to the in-memory blocklist. It does NOT delete the refresh token from Redis. After logout, a stolen refresh token remains valid for 7 days — an attacker can call POST /auth/refresh to obtain fresh access tokens.

**Evidence:**
- `backend/gateway/routes/v1-auth.routes.js` lines 182–190: `addRevoked(jti, ACCESS_TOKEN_TTL_MS)` only; no Redis del call for refresh token
- `backend/gateway/routes/v1-auth.routes.js` lines 193–211: Refresh token stored at key `rt:{refreshToken}` in Redis (line 202)
- Verified 2026-06-23 in Phase 2.9 audit

**Options:**
1. In DELETE /sessions/current: also read the refresh token from the request cookie/body and call `redis.del('rt:{refreshToken}')` before responding
2. Accept as-is — document as known constraint (low risk on single-instance deployment with short-lived sessions)

**Risk:**
High — refresh token window is 7 days. Combined with G-CRIT-001 (in-memory JTI blocklist), logout provides no durable security guarantee on any restart or token theft scenario.

**Recommendation:**
Option 1 — add 2 lines to DELETE /sessions/current to delete the refresh token from Redis. This is the complete fix. Requires the refresh token to be present in the logout request (cookie `crm_refresh_token` already sent with requests).

---

## Summary Table

| # | Item | Severity | Frontend Blocker | Launch Blocker |
|---|------|----------|-----------------|---------------|
| OA-001 | contacts.delete scope gap | Critical | No (backend fix) | Yes (data management broken) |
| OA-002 | JTI blocklist in-memory | High | No | No (accept for single instance) |
| OA-003 | Payment stubs (JazzCash/Easypaisa) | High | No | Yes (no revenue) |
| OA-004 | AI inference model | Medium | No | No (feature, not blocker) |
| OA-005 | contract_lifecycle_management no gateway route | Medium | No | No |
| OA-006 | Security test artifacts disposition | Low | No | No |
| OA-007 | Load test reports disposition | Low | No | No |
| OA-008 | Password hashing algorithm | Medium | No | No (accept for launch) |
| OA-009 | Refresh token not revoked on logout | High | No | No (accept for launch, fix for scale) |

**Frontend Authority Capture blockers: NONE.** All items above are backend/infra decisions that do not block planning the frontend. Documentation of the frontend can proceed based on current code reality.

**Commercial launch blockers: OA-001 (2-line code fix), OA-003 (credentials required).**

---

*End OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md*
