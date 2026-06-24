# U0–U9 FINAL STATUS — Pakistan CRM OS

**Generated:** 2026-06-21 — Independent forensic audit
**Auditor:** Claude Sonnet 4.6

---

## Verdict: PASS WITH FINDINGS

The U0–U9 legacy modernization audit series produced 39 output documents covering repository discovery, authority reconstruction, documentation cataloguing, normalization, workspace restructuring (plan + execution), doc-to-code delta analysis, delta remediation, workspace sealing, and test suite planning. The execution is substantially correct. Two critical findings, four high findings, and six medium findings are documented below.

The repository can enter a modern governance framework after remediating the two Critical findings. All other findings are quality improvements that should be addressed but do not block governance entry.

---

## Critical Findings

### CRIT-001 — Backend test file count systematically wrong across all phases

**Finding:** U0 claimed 54 backend test files. U9 inherited this figure without re-verifying. Actual count: 79 test_*.py files in backend/tests/ (verified by PowerShell). Total test files across all directories: 110.

**Impact:** Every test coverage claim in TEST_SUITE_PLAN.md and SECURITY_TEST_PLAN.md that references "54 backend tests" is based on a wrong baseline. The coverage analysis for CI gate verification (~80% threshold) was planned against an incorrect test inventory.

**Required action before governance entry:** Re-inventory backend/tests/ and tests/ directories. Update TEST_SUITE_PLAN.md §1 and §2.1 with the correct file counts (79 backend test_*.py files; 8 API contract tests; 23 E2E playwright tests). Verify whether the 79 actual files provide the claimed 80% coverage gate.

**Evidence:** PowerShell: Get-ChildItem backend/tests -Filter "test_*.py" -Recurse = 79 entries; TEST_SUITE_PLAN.md §1: "54 .py files"

---

### CRIT-002 — python-jose venv/requirements.txt version drift (security gap)

**Finding:** requirements.txt specifies python-jose[cryptography]==3.5.0 (which patches CVE-2024-33663, CVE-2024-33664, CVE-2024-29370). pip-audit.json (the installed .venv scan, 2026-06-20) shows python-jose 3.3.0 with all 3 CVEs active.

**Impact:** The installed production venv is running a vulnerable version. The CVE remediation encoded in requirements.txt has not been applied. SECURITY_TEST_PLAN.md correctly identified the 3.3.0 CVEs from pip-audit.json but did not flag that requirements.txt specifies a patched version — meaning the fix exists on paper but not in the environment.

**Required action before governance entry:** Run `pip install -r requirements.txt` inside the backend venv to upgrade python-jose from 3.3.0 to 3.5.0. Re-run pip-audit to confirm CVEs are resolved. Update pip-audit.json. Verify starlette is also at 0.38.6 (confirmed) and document the accepted risk for its 3 CVEs pending upgrade to 0.47.2+.

**Evidence:** requirements.txt line 12: `python-jose[cryptography]==3.5.0`; pip-audit.json: `"name":"python-jose","version":"3.3.0","vulns":[...]` (3 CVEs)

---

## High Findings

### HIGH-001 — U5 and U8 execution reports at root (structural gap)

**Finding:** Six execution reports are at D:\SaaS\CRM\ root rather than docs/reports/u-series/: RESTRUCTURING_EXECUTION_REPORT.md, STALE_LINK_FIX_REPORT.md, POST_RESTRUCTURE_VALIDATION.md (U5); WORKSPACE_SEALING_REPORT.md, C_DRIVE_LEAKAGE_AUDIT.md, SEALED_WORKSPACE_VALIDATION.md (U8). Root also has U5–U9 process prompts and the current audit task file — 20 .md files total at root vs the U4 plan's target of 8–9.

**Impact:** The restructuring goal (clean root with only authority docs) was immediately partially undone by U5/U8 generating outputs at root. The root is re-inflated. Any future session starting from root will again see non-authority docs mixed with authority docs.

**Required action:** Decision needed: move U5/U8 execution reports to docs/reports/u-series/ and establish a rule that all future phase execution reports land there. Update any cross-references.

**Evidence:** PowerShell root listing: 20 .md files at D:\SaaS\CRM\; U4 WORKSPACE_RESTRUCTURING_PLAN.md §2 target: 8-9 files.

---

### HIGH-002 — U5 overrode U3's explicit deferral recommendation for SR-003/SR-004

**Finding:** U3 documented that SR-003 and SR-004 (references to DOC-CATALOGUE.md in COMMERCIALISATION-PLAN.md) must not be fixed until C-002 is resolved by a human, because the COMMERCIALISATION-PLAN.md file "needs human review before any edits." U5 applied these fixes (F-003, F-004) without resolving C-002. C-002 remains unresolved.

**Impact:** The fixes themselves are technically correct (path updates). However, the documented precondition for making edits to COMMERCIALISATION-PLAN.md was bypassed. The file has now been edited by Claude without human confirmation of the C5/C6 phase status — which was exactly the scenario U3 was trying to prevent.

**Required action:** Human must review COMMERCIALISATION-PLAN.md and either confirm C5 is complete and update the RESUME POINT table, or correct the Status header to match the RESUME POINT table's "⬜ pending" entries.

**Evidence:** DOC_STALE_REFERENCE_REPORT.md SR-003/SR-004: "Fix Applied: None applied...defer to human refresh"; STALE_LINK_FIX_REPORT.md F-003, F-004: fixes applied; DOC_CONFLICT_REGISTER.md C-002: still unresolved.

---

### HIGH-003 — 3 critical conflicts unresolved (C-001, C-002, C-003)

**Finding:** All three critical conflicts identified by U3 remain unresolved:
- C-001: SYSTEM-SNAPSHOT.md shows C3 as current; COMMERCIALISATION-PLAN.md says C6 is current
- C-002: COMMERCIALISATION-PLAN.md internal inconsistency (Status header ≠ RESUME POINT table)
- C-003: Frontend API wiring: docs claim 75/75 wired; code evidence shows ~7% wired

**Impact:** Any session reading SYSTEM-SNAPSHOT.md at start will receive incorrect current-phase information. The session protocol is broken for C-001/C-002. C-003 means a developer acting on the wiring claim could miss that DUMMY_MODE is true in ~93% of pages.

**Required action:** Human must: (1) Update SYSTEM-SNAPSHOT.md with current C-phase; (2) Reconcile COMMERCIALISATION-PLAN.md Status header with RESUME POINT table; (3) Audit crm-api.js to determine actual DUMMY_MODE state and update documentation accordingly.

**Evidence:** SYSTEM-SNAPSHOT.md line 42: C3 shown as current; COMMERCIALISATION-PLAN.md line 5: C6 current + lines 24-25: C5/C6 pending; DOC_CONFLICT_REGISTER.md C-001/C-002/C-003.

---

### HIGH-004 — API_INVENTORY.md header file count not corrected after U7

**Finding:** API_INVENTORY.md generation header reads "evidence from backend/gateway/routes/v1-*.routes.js (43 files)." U6 confirmed 44 files; U7 corrected route counts but did not correct this header. Actual: 44 files.

**Impact:** Consumers of API_INVENTORY.md will see an inaccurate file count. While the route data itself was corrected by U7, the header creates a discrepancy that erodes trust in the document's accuracy.

**Required action:** Update API_INVENTORY.md line 2: "(43 files)" → "(44 files)".

**Evidence:** API_INVENTORY.md line 2; PowerShell: 44 v1-*.routes.js files; U6 DOC_CODE_DELTA_REPORT.md: "Route domain files: 44."

---

## Medium Findings

### MED-001 — DOC_CATALOGUE.md count stale (141 vs ~167 actual)

26 project-owned .md files have been created since the catalogue was last updated (post-U7). The COMMERCIALISATION-PLAN.md non-negotiable rule requires same-day cataloguing of new docs.

**Required action:** Update DOC_CATALOGUE.md to include all U8/U9 outputs and process prompts. Target count: ~167.

---

### MED-002 — 7 of 12 U3 stale references remain unresolved

SR-006 (PROGRESS.md), SR-010 (DOC-READ-LOG.md count), SR-011 (SYSTEM-SNAPSHOT.md doc count) are the highest-priority unresolved stale references. SR-007/SR-008/SR-009 are in superseded or historical documents and are acceptable as-is.

**Required action:** Fix SR-006 (PROGRESS.md REBUILD-PLAN.md reference), SR-010 (DOC-READ-LOG.md — add 29+ new doc entries), SR-011 (SYSTEM-SNAPSHOT.md doc count — update as part of full SYSTEM-SNAPSHOT.md refresh).

---

### MED-003 — Root .md file inflation (20 files vs planned 8-9)

U5 aimed for 8-9 root .md files. Current: 20. The surplus includes U5/U8 execution reports (6 files), U6-U9 process prompts (4 files), and the current audit task file. No policy exists for managing future phase outputs.

**Required action:** Define and enforce a root file policy: execution reports land in docs/reports/u-series/; process prompts (U-series prompts) land in docs/reports/u-series/ immediately after the phase completes.

---

### MED-004 — U9 module count stale (28 vs post-U7 count of 29)

TEST_SUITE_PLAN.md scope header uses pre-U7 module count. Module 29 (contract_lifecycle_management) added by U7 FX-013 is not reflected in U9 scope.

**Required action:** Update TEST_SUITE_PLAN.md scope header from "28 backend modules" to "29 backend modules" (documented) or "34 src/ modules" (actual).

---

### MED-005 — 3 human-decision deferrals still open (D-001, D-002, D-003 from U7)

D-001 (contract_lifecycle_management gateway route decision), D-002 (custom objects gateway route), D-003 (5 entity DB schema attributions). These are correctly deferred but represent open governance gaps.

**Required action:** Human project lead to decide: expose contract_lifecycle_management via gateway or archive as deferred scope. Confirm custom objects routing mechanism. Add Sprint 5B entity DB schema attributions to ENTITY_INVENTORY.md.

---

### MED-006 — D-005 from U7 still open (4 backend docs with unclear placement)

backend/product-spec-gap-register.md, enterprise-depth.md, data-governance-ownership.md, b9-p08-mobile-responsiveness-system.md — found during U5 restructuring scan. Placement not yet decided.

**Required action:** Human to confirm: leave in backend/docs/ or move to docs/archive/.

---

## Low Findings

- POST_RESTRUCTURE_VALIDATION.md root count says 9 but actual post-U5 count was 12 (self-counting error)
- D-004 in DOC_CODE_REMEDIATION_REPORT.md listed as deferred but also says "RESOLVED by FX-015" (minor inconsistency)
- DOC-READ-LOG.md abandoned since 2026-05-31; 29+ new docs not logged (Low — log is non-authoritative)
- psycopg2-binary version drift: requirements.txt says 2.9.10, installed is 2.9.12 (no CVEs; informational)
- npm "unknown env config store-dir" warning on every npm command (pnpm config bleeding into npm)

---

## Recommended Next Actions (Priority Order)

| Priority | Action | Owner | Rationale |
|---|---|---|---|
| 1 | Rebuild venv: `pip install -r requirements.txt` — upgrade python-jose from 3.3.0 to 3.5.0 | Developer | Critical security gap — active CVEs in installed environment |
| 2 | Human review of COMMERCIALISATION-PLAN.md — resolve C-002 (Status header vs RESUME POINT table inconsistency) | Project Lead | Blocks accurate session startup protocol and C-001 resolution |
| 3 | Re-inventory test files — update TEST_SUITE_PLAN.md with correct counts (79 backend tests, 8 API contract tests, 23 E2E playwright tests) | Claude | Wrong baseline makes coverage claims unverifiable |
| 4 | Update SYSTEM-SNAPSHOT.md with current C-phase status — resolves C-001 | Project Lead + Claude | Session startup protocol broken; developers misled about current phase |
| 5 | Fix API_INVENTORY.md header: "(43 files)" → "(44 files)" | Claude | Minor but creates visible inaccuracy in a high-reference document |
| 6 | Move U5/U8 execution reports to docs/reports/u-series/ | Claude | Restore the root-cleanliness goal of U4/U5 |
| 7 | Update DOC_CATALOGUE.md to include U8/U9 outputs (~26 new files) | Claude | Restore catalogue accuracy per COMMERCIALISATION-PLAN.md rule |
| 8 | Decide on contract_lifecycle_management gateway route (D-001) | Project Lead | Only undocumented complete backend module; needs gateway or explicit archive |
| 9 | Refresh DOC-READ-LOG.md with 29+ new docs | Claude | Session protocol compliance |
| 10 | Decide on custom objects routing (D-002), entity schema attributions (D-003), 4 backend doc placements (D-005) | Project Lead + Claude | Complete open deferrals from U7 |

---

## Remediation Scope Before Modern Governance Framework Entry

**Blockers (must fix before entry):**
1. CRIT-001: Correct test file count baseline — update TEST_SUITE_PLAN.md
2. CRIT-002: Rebuild venv to apply python-jose 3.5.0 from requirements.txt; re-run pip-audit

**Pre-entry housekeeping (strongly recommended):**
3. HIGH-002 and HIGH-003: Resolve C-001/C-002 with human input; update SYSTEM-SNAPSHOT.md
4. HIGH-004: Correct API_INVENTORY.md header (1-line fix)
5. MED-001: Update DOC_CATALOGUE.md count

**Post-entry cleanup (defer acceptable):**
6. HIGH-001: Move execution reports to u-series; establish root policy
7. MED-002 through MED-006: Stale references, open deferrals, module counts

---

*End U0_U9_FINAL_STATUS.md*
