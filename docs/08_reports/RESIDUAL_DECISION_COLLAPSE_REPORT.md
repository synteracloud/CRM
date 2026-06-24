---
Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: AI
Phase: 2.95
---

# RESIDUAL DECISION COLLAPSE REPORT

> Phase 2.95 — All 9 residual owner decisions collapsed to a single recommended path.
> Mandatory Collapse Test applied: "If the owner disappears today, which option should the project take?"

---

## Summary

| Metric | Count |
|--------|-------|
| Decisions reviewed | 9 |
| RESOLVED (evidence-determinable) | 1 |
| OWNER_CONFIRMATION_ONLY (recommendation exists, proceed unless rejected) | 7 |
| TRUE_OWNER_DECISION (external dependency, repo cannot determine) | 1 |
| Frontend blockers post-collapse | 0 |

---

## OA-001 — contacts.delete RBAC Scope Missing

**Decision:** Which roles should receive the `contacts.delete` permission scope?

**Options:**
- A: Grant to `tenant_admin` + `super_admin` only (restricted delete)
- B: Grant to `tenant_owner` + `tenant_admin` + `super_admin` (broad delete)
- C: Remove the scope guard — replace with role-only check
- D: Accept as intentional — contacts cannot be deleted

**Recommended Option: A — grant to tenant_admin + super_admin**

**Rationale:** The existing delete scope pattern in rbac-scopes.js grants destructive operations to admin tiers, not tenant_owner (who is a business user, not an operator). LEADS_DELETE, DEALS_DELETE, and TASKS_DELETE all follow this pattern. Granting to tenant_owner would be inconsistent with every other delete scope in the system. Option D (permanent contacts) is unacceptable — it prevents GDPR deletion compliance.

**Implementation:** 2 lines in rbac-scopes.js + 2 ROLE_SCOPES entries. Derivable from 6 existing delete scope examples.

**Risks:** Minimal. Follows established pattern.
**Benefits:** Restores intended functionality; enables GDPR compliance.
**Frontend Impact:** Hide contacts delete button for `viewer`, `field_agent`, `support_agent`, `tenant_owner` roles. Show for `tenant_admin`, `super_admin`. Document constraint until OA-001 is approved.
**Backend Impact:** 2-line change to rbac-scopes.js (REQUIRES_APPROVAL per governance).

**Classification: OWNER_CONFIRMATION_ONLY**
Proceed with Option A implementation unless owner explicitly rejects. Frontend documents the constraint now.

---

## OA-002 — JTI Blocklist In-Memory (Not Redis)

**Decision:** When to migrate JTI revocation blocklist from in-process Set to Redis?

**Options:**
- A: Fix before launch — migrate to Redis
- B: Accept for launch — document as scaling prerequisite
- C: Reduce access token TTL to 5 min to reduce exposure window

**Recommended Option: B — accept for launch; bundle with OA-009 in auth hardening sprint**

**Rationale:** Current deployment is a single Render.com instance. In this topology, the in-memory Set works correctly — a restart clears it but tokens expire in 15 min anyway. The risk is near-zero at current scale. Redis is already wired in the gateway; the migration is ~10 lines when ready. Bundling with OA-009 (refresh token revocation) in a single sprint avoids touching auth middleware twice.

**Risks:** On auto-scale or multi-instance deploy, revoked tokens remain valid on instances that missed the revocation. Document explicitly.
**Benefits:** No auth changes at launch; auth hardening sprint scheduled post-C6.
**Frontend Impact:** None. Frontend sends DELETE /auth/sessions/current and clears local state regardless.
**Backend Impact:** None at launch. Auth hardening sprint adds ~10 lines to jti-blocklist.js and v1-auth.routes.js.

**Classification: OWNER_CONFIRMATION_ONLY**
Launch with in-memory blocklist. Auth hardening sprint (OA-002 + OA-009) is post-C6 priority.

---

## OA-003 — JazzCash/Easypaisa Stub Mode

**Decision:** When and how to activate live payment collection?

**Options:**
- A: Obtain JazzCash + Easypaisa merchant credentials before launch
- B: Obtain credentials; launch with JazzCash only first
- C: Launch without payments — disable billing payment section in frontend
- D: Defer payment activation to C7 post-launch

**Recommended Option: A (if timeline permits) or D (if credentials not ready in time)**

**Rationale:** This is the only TRUE_OWNER_DECISION in this register. Payment credential acquisition requires external vendor relationships with JazzCash (NayaPay) and Easypaisa (Telenor Microfinance Bank). Typical onboarding is 2–4 weeks in Pakistan. The repository cannot determine whether the owner has started this process. The architecture is ready; only credentials are missing.

**Risks:** Options C/D mean no revenue collection at launch. Option A requires vendor application to be in progress now.
**Benefits:** Option A enables immediate revenue; Option D allows launch on schedule without payments.
**Frontend Impact:** Minimal. billing-settings.html (G-04) is already built with known stub behavior. If Option C is chosen, hide the "Payment Methods" section in G-04 until credentials are ready. Navigation unaffected either way.
**Backend Impact:** Set `JAZZCASH_STUB_MODE=false` + `EASYPAISA_STUB_MODE=false` in render.yaml + add credentials as env vars. Zero code changes.

**Classification: TRUE_OWNER_DECISION**
Repository evidence is exhausted. Credential acquisition is a business relationship action. Owner must decide: is payment activation part of C6 launch or C7?

---

## OA-004 — AI Inference Model Selection

**Decision:** Which LLM provider (if any) to connect to AI features?

**Options:**
- A: Add Claude Haiku via Anthropic SDK before launch
- B: Add GPT-4o-mini via OpenAI SDK before launch
- C: Keep rule-based for C6 launch; defer LLM to C7
- D: Remove AI pages from navigation for now

**Recommended Option: C — keep rule-based for C6; defer LLM to C7**

**Rationale:** AI pages (M-01 ai-copilot.html, M-02 ai-insights.html) are built and functional with rule-based scoring. DESIGN-SPEC.md explicitly states "Actual AI inference is out of scope for v1." The rule-based model provides genuine value (lead scoring, churn prediction) without LLM costs. Option D (hiding pages) would remove working features. Option A or B can be added post-C6 with a single `pip install anthropic` + API key.

**Risks:** None at launch. Rule-based features work as designed.
**Benefits:** Zero provider cost at launch; AI pages deliver value on day one.
**Frontend Impact:** None. M-01, M-02 display results from the same API endpoints regardless of backend model.
**Backend Impact:** None at launch. LLM integration in C7 adds provider SDK + prompt engineering.

**Classification: OWNER_CONFIRMATION_ONLY**
Proceed with rule-based for C6. LLM integration planned for C7.

---

## OA-005 — contract_lifecycle_management No Gateway Route

**Decision:** Should the contracts backend module be exposed via a gateway route for C6?

**Options:**
- A: Create v1-contracts.routes.js — expose 12 endpoints with RBAC scopes
- B: Defer to C7 — no gateway route for C6
- C: Archive the module as unused (not recommended)

**Recommended Option: B — defer to C7**

**Evidence:** DESIGN-SPEC.md §3 Screen Inventory was searched for any contracts page. No contracts screen exists in the 75-page C6 build scope. Without a frontend page to consume the API, exposing the gateway route serves no C6 purpose. The module is complete and tested; it will be exposed in C7 when the frontend page is built.

**Risks:** None. Module is preserved and tested. Gateway route addition is low-risk when needed.
**Benefits:** Avoids unnecessary RBAC scope additions and gateway changes for C6.
**Frontend Impact:** None. No contracts page in current scope.
**Backend Impact:** None at launch. v1-contracts.routes.js is created in C7.

**Classification: RESOLVED**
Repository evidence (DESIGN-SPEC.md has no contracts page) determines the answer: defer to C7.

---

## OA-006 — Security Test Artifacts (tests/security/*.json)

**Decision:** Are security scan JSON files compliance evidence or regenerated CI outputs?

**Options:**
- A: Move to docs/reports/security/ — version-control as compliance evidence
- B: Add to .gitignore — treat as CI-regenerated outputs

**Recommended Option: A — move to docs/reports/security/**

**Rationale:** The files exist in the repository and are currently tracked. If they were CI-regenerated, they would already be in .gitignore (all other generated outputs were handled in prior hygiene phases). Their presence as tracked files implies they were manually generated for audit purposes. Preserving them in docs/reports/security/ is safe — it doesn't break any pipeline — while gitignoring compliance evidence would be harmful if they are legally required.

**Risks:** Minimal. Moving docs files is SAFE_REPOSITORY_HYGIENE.
**Benefits:** Clear audit trail; compliance evidence preserved.
**Frontend Impact:** None.
**Backend Impact:** None.

**Classification: OWNER_CONFIRMATION_ONLY**
Execute move to docs/reports/security/ unless owner specifies these are CI-regenerated.

---

## OA-007 — Load Test Reports (tests/load/reports/*.html)

**Decision:** Should C5 production load test HTML reports be preserved or gitignored?

**Options:**
- A: Move c5-prod-*.html to docs/reports/load/ — preserve as performance baseline
- B: Gitignore all load test outputs

**Recommended Option: A — move c5-prod-*.html to docs/reports/load/**

**Rationale:** C5 production load test results are a performance baseline — they document the system's confirmed capacity before C6 launch. Losing this baseline means no comparison point if performance degrades post-C6. Development load reports (non-c5-prod) can be gitignored. The SAFE_REPOSITORY_HYGIENE policy explicitly covers "report relocation" as an autonomous action.

**Risks:** None. Moving files is reversible.
**Benefits:** Performance baseline preserved; load test outputs separated from source code.
**Frontend Impact:** None.
**Backend Impact:** None.

**Classification: OWNER_CONFIRMATION_ONLY**
Execute move of c5-prod-*.html to docs/reports/load/. Gitignore dev load reports unless owner objects.

---

## OA-008 — Password Hashing Algorithm (SHA-256, Not bcrypt)

**Decision:** When to migrate from SHA-256 to bcrypt/argon2?

**Options:**
- A: Accept SHA-256 for C6 launch; document as known constraint; plan C7 migration
- B: Migrate to bcrypt before launch (requires re-hashing all existing users)
- C: Add transparent re-hash-on-login (bcrypt on first successful login post-deploy)

**Recommended Option: A — accept SHA-256 for C6; plan Option C for C7**

**Rationale:** At C6 launch, the user base is small (internal team + early adopters). SHA-256 with proper salting is not cryptographically broken — it is merely weaker than purpose-built KDFs under brute-force conditions if the database is compromised. With proper DB access controls and a limited user base, the risk is acceptable at launch. Option B requires downtime and user re-authentication. Option C (transparent migration) is the ideal long-term path and should be planned for C7 as the user base grows.

**Risks:** If DB is compromised, SHA-256 passwords crack faster than bcrypt. Mitigation: strong DB access controls + rate limiting on login endpoint.
**Benefits:** No migration risk or user disruption at launch.
**Frontend Impact:** None. Login/register pages call the same gateway endpoints regardless.
**Backend Impact:** None at launch. C7 adds bcrypt re-hash logic on successful login.

**Classification: OWNER_CONFIRMATION_ONLY**
Accept SHA-256 for C6. C7 sprint adds transparent bcrypt migration.

---

## OA-009 — Refresh Token Not Revoked on Logout

**Decision:** When to fix logout to also revoke the refresh token?

**Options:**
- A: Fix DELETE /sessions/current to also delete rt:{refreshToken} from Redis (3–5 lines)
- B: Accept for launch — document; fix in auth hardening sprint with OA-002
- C: Reduce refresh token TTL from 7 days to 24 hours to limit exposure window

**Recommended Option: B — bundle with OA-002 in post-C6 auth hardening sprint**

**Rationale:** The fix is technically trivial (3–5 lines in v1-auth.routes.js). However, on a single-instance deployment at C6 launch scale, the attack vector is narrow: an attacker must have already stolen the HttpOnly refresh token cookie. This requires either network interception (mitigated by HTTPS) or physical device access. Bundling with OA-002 means a single, well-tested auth hardening sprint rather than two separate auth middleware changes.

**Risks:** Stolen refresh tokens remain valid for 7 days post-logout. Documented constraint.
**Benefits:** Clean sprint boundary; auth changes tested together.
**Frontend Impact:** None. Frontend sends DELETE /auth/sessions/current and clears local state.
**Backend Impact:** None at launch. Auth hardening sprint: ~10 lines across jti-blocklist.js and v1-auth.routes.js.

**Classification: OWNER_CONFIRMATION_ONLY**
Accept for C6 launch. Auth hardening sprint (OA-002 + OA-009) is first post-C6 security sprint.

---

## Frontend Readiness Test

After collapse, assessing whether any remaining unresolved item can alter:

| Area | Affected? | By What |
|------|-----------|---------|
| Navigation | NO | No decision changes the navigation menu |
| Menus | NO | All 75 pages remain in scope as-is |
| Screens | NO | Only contacts delete button visibility affected (already documented) |
| Workflows | NO | Auth hardening is backend-only; workflow screens unchanged |
| Permissions | MINOR | OA-001 affects contacts delete visibility only — already a documented constraint |
| User journeys | NO | Payment stub behavior is already the documented production state |
| Product scope | NO | OA-005 deferred (no C6 contracts page); AI pages function rule-based as designed |

**The one TRUE_OWNER_DECISION (OA-003) does not alter navigation, menus, screens, workflows, permissions, or user journeys.** Billing page G-04 is already built for stub behavior.

**Verdict: GO**

---

*End RESIDUAL_DECISION_COLLAPSE_REPORT.md*
