---
Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: Human
Phase: 2.95
---

# OWNER CONFIRMATION REGISTER

> Items classified OWNER_CONFIRMATION_ONLY.
> These have a clear recommended path. Implementation proceeds on the recommendation unless the owner explicitly rejects it.
> The owner does not need to actively decide — silence = proceed.

---

## How to Use This Register

For each item:
1. Read the recommendation
2. If you agree (or have no strong objection) → do nothing, implementation proceeds
3. If you disagree → respond with your preferred option before the sprint starts
4. Each item has a "Last date to object" — after that, implementation proceeds on recommendation

---

## OA-001 — contacts.delete Scope Grant

**Recommendation:** Add `CONTACTS_DELETE: 'contacts.delete'` to SCOPES constant in rbac-scopes.js; grant to `tenant_admin` and `super_admin` in ROLE_SCOPES.

**Implementation:** 2 lines in rbac-scopes.js, 2 entries in ROLE_SCOPES. No API changes. No schema changes.

**What happens if owner does not respond:** Implementation proceeds with Option A (tenant_admin + super_admin) before C6 launch.

**What if owner objects:** Specify which roles should receive contacts.delete, or confirm Option C (contacts cannot be deleted — hide delete UI permanently).

**Deadline sensitivity:** CRITICAL — commercial launch blocker. Must be resolved before C6 go-live.

**Frontend dependency:** Frontend authority capture documents: "contacts delete button visible only to tenant_admin and super_admin." Once OA-001 is applied, delete functionality works correctly.

**Suggested sprint:** Pre-launch hotfix (2 lines, 15 minutes of work).

---

## OA-002 — JTI Blocklist Redis Migration

**Recommendation:** Accept in-memory JTI blocklist for C6 launch. Migrate to Redis in the Post-C6 Auth Hardening Sprint, bundled with OA-009.

**What happens if owner does not respond:** C6 launches with in-memory blocklist. Auth hardening sprint is scheduled for the first post-C6 development cycle.

**What if owner objects:** Owner may request Option A (fix before launch). In that case, ~10 lines in jti-blocklist.js using existing Redis client — low-risk change.

**Deadline sensitivity:** HIGH — should be resolved within first post-C6 sprint (before any auto-scaling or second instance is added).

**Frontend dependency:** None. Frontend behavior is identical either way.

**Suggested sprint:** Post-C6 Auth Hardening Sprint (bundle with OA-009).

---

## OA-004 — AI Inference Model

**Recommendation:** Keep rule-based weighted-sum scoring for C6 launch. Plan LLM integration for C7.

**What happens if owner does not respond:** AI pages (M-01, M-02) launch with rule-based advisory features. No LLM cost at launch.

**What if owner objects:** Owner may specify a provider (e.g., Anthropic Claude Haiku). In that case, add `anthropic` to requirements.txt + set ANTHROPIC_API_KEY in render.yaml. Prompt engineering for each AI feature would need to be designed.

**Deadline sensitivity:** MEDIUM — AI pages are functional at launch with rule-based model. LLM upgrade is additive.

**Frontend dependency:** None. M-01, M-02 display results from stable API contract regardless of backend model.

**Suggested sprint:** C7 Feature Sprint — AI Enhancement.

---

## OA-006 — Security Test Artifact Disposition

**Recommendation:** Move tests/security/*.json to docs/reports/security/ as version-controlled compliance evidence.

**What happens if owner does not respond:** Files are moved to docs/reports/security/. Compliance evidence preserved. .gitignore not modified for these files.

**What if owner objects:** If these are CI-regenerated outputs, owner specifies — files are then gitignored instead.

**Deadline sensitivity:** LOW — hygiene item, non-blocking.

**Frontend dependency:** None.

**Suggested sprint:** Next SAFE_REPOSITORY_HYGIENE pass.

---

## OA-007 — Load Test Report Disposition

**Recommendation:** Move tests/load/reports/c5-prod-*.html to docs/reports/load/ as performance baseline evidence. Gitignore development load test outputs.

**What happens if owner does not respond:** c5-prod-*.html preserved in docs/reports/load/. Dev reports gitignored.

**What if owner objects:** Owner may specify all load test outputs should be gitignored — in that case, all HTML reports are removed from tracking.

**Deadline sensitivity:** LOW — hygiene item, non-blocking.

**Frontend dependency:** None.

**Suggested sprint:** Next SAFE_REPOSITORY_HYGIENE pass.

---

## OA-008 — Password Hashing Algorithm

**Recommendation:** Accept SHA-256 for C6 launch with proper DB access controls documented. Plan transparent bcrypt re-hash-on-login for C7.

**What happens if owner does not respond:** C6 launches with SHA-256. C7 sprint plan includes Option C (transparent migration — bcrypt on first successful login post-deploy, no user disruption).

**What if owner objects:** Owner may request Option B (migrate before launch). This requires re-hashing all existing user passwords (requires DB access + downtime window).

**Deadline sensitivity:** MEDIUM — acceptable risk at C6 scale; must be addressed before significant user base growth.

**Frontend dependency:** None. Password form fields unchanged.

**Suggested sprint:** C7 Security Sprint — Credential Hardening.

---

## OA-009 — Refresh Token Revocation on Logout

**Recommendation:** Bundle with OA-002 in Post-C6 Auth Hardening Sprint. Fix DELETE /sessions/current to also delete rt:{refreshToken} from Redis.

**What happens if owner does not respond:** C6 launches with known logout gap (refresh token remains valid 7 days post-logout). Auth hardening sprint scheduled post-C6.

**What if owner objects:** Owner may request Option A (fix before launch). ~5 lines in v1-auth.routes.js — trivial change, can be done in pre-launch hotfix.

**Deadline sensitivity:** HIGH — should be in first post-C6 sprint. Combined with OA-002, the auth hardening sprint closes the entire stateless logout weakness.

**Frontend dependency:** None. Frontend logout behavior unchanged.

**Suggested sprint:** Post-C6 Auth Hardening Sprint (bundle with OA-002).

---

## Summary Table

| Item | Recommendation | If No Response | Deadline | Sprint |
|------|----------------|----------------|----------|--------|
| OA-001 | Grant contacts.delete to tenant_admin + super_admin | Proceed | Pre-launch (CRITICAL) | Pre-launch hotfix |
| OA-002 | Accept in-memory for C6; Redis in auth sprint | Proceed | Post-C6 Sprint 1 | Auth Hardening Sprint |
| OA-004 | Keep rule-based for C6 | Proceed | C7 | C7 AI Sprint |
| OA-006 | Move security JSONs to docs/reports/security/ | Proceed | Next hygiene pass | SAFE_REPOSITORY_HYGIENE |
| OA-007 | Move c5-prod reports to docs/reports/load/ | Proceed | Next hygiene pass | SAFE_REPOSITORY_HYGIENE |
| OA-008 | Accept SHA-256 for C6; bcrypt in C7 | Proceed | C7 | C7 Security Sprint |
| OA-009 | Bundle with OA-002 auth hardening sprint | Proceed | Post-C6 Sprint 1 | Auth Hardening Sprint |

---

*End OWNER_CONFIRMATION_REGISTER.md*
