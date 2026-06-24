Status: Active
Authority Level: Medium
Last Reviewed: 2026-06-23
Owner: AI

# DOC DRIFT REGISTER
> Documents that were accurate at one point but have since drifted from code/repository reality.

---

## Definition

**Doc drift** occurs when a document was correct when written but is now stale due to:
- A count changing (more tests added, schemas removed, etc.)
- A file moving from its documented location
- A status field not being updated
- A bug being fixed that docs still describe as open
- A decision being made that supersedes a TBD

---

## Drift Items

### DD-001: AI_OPERATING_CONTEXT.md — Database Schema Count
**Document:** `docs/07_governance/AI_OPERATING_CONTEXT.md`
**Drift:** Claimed "20 database schemas" — actual count is 18 (backend/db/ has 18 directories)
**Root cause:** Phase 2 Backend Authority Capture confirmed 18 but AI_OPERATING_CONTEXT.md was last updated with an earlier estimate
**Affected lines:** "20 database schemas + 12 Alembic migrations" (What is complete section) + FROZEN_DECISIONS table
**Fix applied:** **FIXED 2026-06-23** — changed to 18 in both locations
**Severity:** High — primary context doc read by every AI session

---

### DD-002: AI_OPERATING_CONTEXT.md — Playwright Test Count
**Document:** `docs/07_governance/AI_OPERATING_CONTEXT.md`
**Drift:** Claimed "23 Playwright E2E test files" — actual count is 25 (.py files in tests/e2e/playwright/)
**Root cause:** 2 additional Playwright test files added after AI_OPERATING_CONTEXT.md was written
**Fix applied:** **FIXED 2026-06-23** — changed to 25 in summary section and validation table
**Severity:** Medium — test count discrepancy; does not affect runtime

---

### DD-003: AI_OPERATING_CONTEXT.md — Document Status
**Document:** `docs/07_governance/AI_OPERATING_CONTEXT.md`
**Drift:** Status field was "Draft" — this is the primary context document actively used by all AI sessions
**Root cause:** Status never promoted after document was stabilized
**Fix applied:** **FIXED 2026-06-23** — promoted to Active
**Severity:** Medium — Status: Draft signals "don't trust" to future readers

---

### DD-004: BACKEND_GAP_REGISTER.md — G-HIGH-005 False Alarm
**Document:** `docs/08_reports/BACKEND_GAP_REGISTER.md`
**Drift:** G-HIGH-005 claimed `leads.delete` may be missing from SCOPES constant (TBD)
**Root cause:** Phase 2 did not verify leads.delete before publishing G-HIGH-005
**Code reality:** `LEADS_DELETE: 'leads.delete'` IS present in rbac-scopes.js line 21
**Fix applied:** **FIXED 2026-06-23** — G-HIGH-005 marked RESOLVED (NOT A GAP)
**Severity:** High — false alarm in a risk register misleads future triage

---

### DD-005: USER_ROLES_AND_PERMISSIONS.md — leads.delete TBD
**Document:** `docs/03_fullstack_contracts/USER_ROLES_AND_PERMISSIONS.md`
**Drift:** "leads.delete may have the same issue — TBD REQUIRES VERIFICATION"
**Root cause:** Carried over from G-HIGH-005 without verification
**Fix applied:** **FIXED 2026-06-23** — updated to confirmed: leads.delete IS in rbac-scopes.js
**Severity:** Medium

---

### DD-006: File Location Drift — backend/ root .md files → backend/docs/
**Documents:** backend/BACKEND-QC.md, backend/CONSTRAINTS.md, backend/FRONTEND-BACKEND-MAPPING.md, backend/PENDING.md, backend/market-research-gap-register.md, backend/product-spec-gap-register.md
**Drift:** APPROVAL_RECLASSIFICATION_REPORT.md planned moves to specific final locations. Files were moved to backend/docs/ (intermediate) but not to their canonical destinations.
**Fix applied:** **FIXED 2026-06-23:**
- backend/docs/PENDING.md → docs/reports/session/BACKEND-PENDING.md
- backend/docs/market-research-gap-register.md → docs/08_reports/MARKET-RESEARCH-GAP-REGISTER.md
- backend/docs/product-spec-gap-register.md → docs/08_reports/PRODUCT-SPEC-GAP-REGISTER.md
- backend/docs/FRONTEND-BACKEND-MAPPING.md → docs/03_fullstack_contracts/FRONTEND-BACKEND-MAPPING.md
- backend/docs/phase4-gap-register.md → docs/08_reports/PHASE4-GAP-REGISTER.md
**Severity:** Medium — files at wrong locations cause cross-references to fail

---

### DD-007: SKIP-BACKLOG.md Not Moved
**Document:** `tests/e2e/playwright/SKIP-BACKLOG.md`
**Drift:** APPROVAL_RECLASSIFICATION_REPORT.md D-15 classified this as SAFE_REPOSITORY_HYGIENE → docs/04_testing/. Not executed in prior session.
**Fix applied:** **FIXED 2026-06-23** — moved to docs/04_testing/SKIP-BACKLOG.md
**Severity:** Low

---

### DD-008: COMMERCIALISATION-PLAN.md Duplicate at Root
**Document:** Root `COMMERCIALISATION-PLAN.md` (tracked by git, M — modified)
**Drift:** C-01 in APPROVAL_RECLASSIFICATION_REPORT said "Already executed" — file moved to docs/00_authority/. But root copy was NOT removed from git tracking. Two copies now exist.
**Fix NOT applied:** Removing a tracked file from git requires `git rm` which is a git operation outside SAFE_REPOSITORY_HYGIENE scope. Requires careful execution.
**Recommended action:** Run `git rm COMMERCIALISATION-PLAN.md` after confirming docs/00_authority/ copy is current. Then commit.
**Severity:** Low — causes confusion but no runtime impact

---

### DD-009: Documents Still Showing Status: Draft Should Be Active
**Documents affected (not individually read in this session):**
- docs/01_backend/BACKEND_ARCHITECTURE.md (Status: Draft)
- docs/01_backend/DATABASE_SCHEMA.md (Status: Draft)
- docs/01_backend/API_CONTRACT.md (Status: Draft)
- docs/01_backend/SERVICE_CATALOG.md (Status: Draft)
- docs/00_authority/PROJECT_CHARTER.md (Status: unknown — likely Draft)
- docs/08_reports/BACKEND_GAP_REGISTER.md (Status: Draft)
**Root cause:** Batch status promotion from Draft → Active was planned but the individual docs were not updated.
**Fix NOT applied:** Requires reading each file before editing. Deferred to next SAFE_REPOSITORY_HYGIENE pass.
**Recommended action:** Promote all 01_backend/ docs and 00_authority/ docs to Status: Active in a single batch edit session.
**Severity:** Medium — Status: Draft on authority documents signals untrusted content

---

### DD-010: SERVICE_CATALOG.md — Service Count
**Document:** `docs/01_backend/SERVICE_CATALOG.md`
**Drift:** Likely claims 22 cross-cutting services; actual backend/services/ has 23 directories
**Fix NOT applied:** SERVICE_CATALOG.md not fully read in this session; status field not confirmed.
**Recommended action:** Read SERVICE_CATALOG.md, update count to 23, add `summary/` service as a documented entry.
**Severity:** Low

---

## Fixed Items Summary

| # | Document | Drift Type | Fixed |
|---|----------|-----------|-------|
| DD-001 | AI_OPERATING_CONTEXT.md | Schema count (20→18) | ✓ |
| DD-002 | AI_OPERATING_CONTEXT.md | Playwright count (23→25) | ✓ |
| DD-003 | AI_OPERATING_CONTEXT.md | Status Draft→Active | ✓ |
| DD-004 | BACKEND_GAP_REGISTER.md | G-HIGH-005 false alarm | ✓ |
| DD-005 | USER_ROLES_AND_PERMISSIONS.md | leads.delete TBD resolved | ✓ |
| DD-006 | 5 backend/docs/ files | Wrong final location | ✓ |
| DD-007 | SKIP-BACKLOG.md | Wrong location | ✓ |

## Remaining Drift Items (not fixed this session)

| # | Document | Drift Type | Blocker |
|---|----------|-----------|---------|
| DD-008 | COMMERCIALISATION-PLAN.md (root) | Duplicate | Needs git rm |
| DD-009 | Multiple authority docs | Status: Draft | Batch edit needed |
| DD-010 | SERVICE_CATALOG.md | Service count | Needs full read |

---

*End DOC_DRIFT_REGISTER.md*
