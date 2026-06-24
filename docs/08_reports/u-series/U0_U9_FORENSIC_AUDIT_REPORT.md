# U0–U9 FORENSIC AUDIT REPORT — Pakistan CRM OS

**Generated:** 2026-06-21 — Independent forensic audit
**Auditor:** Claude Sonnet 4.6 (fresh agent — no prior session context)
**Method:** Every claim verified against live repository evidence. No prior reports trusted.
**Audit scope:** All U-series phases U0 through U9 and cross-phase consistency

---

## Methodology

All verification was performed by:
1. Listing actual files with PowerShell Get-ChildItem (live filesystem)
2. Reading actual source files (gateway routes, Python modules, requirements.txt, pip-audit.json)
3. Running live PowerShell commands for U8 sealing verification
4. Counting items independently before comparing to claimed counts

---

## U0 — Repository Reality Discovery

### What Was Claimed
Four discovery documents were produced: REPOSITORY_REALITY_REPORT.md, WORKSPACE_BASELINE_AUDIT.md, REPOSITORY_TREE_INVENTORY.md, CURRENT_PROJECT_STATUS.md. Claims included: 75 custom HTML pages, 34 Python backend modules, 43 gateway route groups, 54 backend test files.

### What Was Verified

**Page count:** 169 total HTML files confirmed in frontend/src/app/. 75 custom CRM pages confirmed individually against the U0 list — all 75 present. ~94 NexLink library/demo pages confirmed as the remainder. ACCURATE.

**Backend Python modules:** 34 directories confirmed under backend/src/ via PowerShell listing. ACCURATE.

**Gateway route groups:** U0 claims 43 groups. Actual: 44 v1-*.routes.js files. INACCURATE BY 1. (U6 subsequently confirmed 44, so U0 undercounted by one route file.)

**Backend test files:** U0 claims "54 test files." Actual: 79 test_*.py files in backend/tests/ (PowerShell confirmed). This is a 46% undercount. Total across all test directories: 79 backend + 31 root tests = 110 test files. The claimed 54 matches no counting method we could construct.

**Architecture description:** 3-tier architecture (static frontend, Node.js gateway, Python FastAPI services) confirmed by file structure. ACCURATE.

**Integration inventory:** JazzCash/Easypaisa stubs, 4 WhatsApp adapters, render.yaml config — all confirmed present. ACCURATE.

### Discrepancies Found
- Gateway route count: 43 claimed, 44 actual
- Backend test file count: 54 claimed, 79 actual in backend/tests/ alone

### Confidence Level: MEDIUM
Core structural claims accurate. Quantitative claims for test files and route count are materially wrong.

---

## U1 — Authority Reconstruction

### What Was Claimed
Seven inventory documents produced covering features, modules, entities, workflows, roles/permissions, APIs, and an authority reconstruction report. Claims included: 63 RBAC scopes (at generation time), ~198 API routes (at generation time), 28 documented modules, no contract_lifecycle_management in inventory.

### What Was Verified

**API routes:** API_INVENTORY.md header still reads "43 files" after U7. The actual count is 44 files. The total route count was corrected from ~198 to 228 by U7 (FX-001) and is now accurate in the summary table. The header file count is a residual inaccuracy not corrected by U7.

**RBAC scope count:** Initially 63, corrected to 91 by U7 (FX-009). Current ROLE_PERMISSION_INVENTORY.md header shows "91 scopes" — ACCURATE post-U7.

**Spot-check — 5 API routes:**
- GET /leads (v1-leads.routes.js) — CONFIRMED
- GET /collections/overdue (v1-collections.routes.js) — CONFIRMED
- GET /territories/assignments (v1-territories.routes.js) — CONFIRMED
- GET /communications/engagement (v1-communications.routes.js) — CONFIRMED
- GET /tenants/current (v1-tenants.routes.js) — CONFIRMED

**Spot-check — Lead entity:** entities.py fields match ENTITY_INVENTORY.md Python-layer description (lead_id, tenant_id, owner_user_id, source, status, score, email, phone, company_name, created_at, converted_at). ACCURATE.

**Module 29 (contract_lifecycle_management):** Module added by U7 (FX-013). Verified: backend/src/contract_lifecycle_management/api.py, entities.py, services.py all present. API_ENDPOINTS dict has 12 path entries. No gateway route file exists (v1-contracts.routes.js absent). ACCURATELY documented post-U7.

**Roles spot-check:** 7 canonical roles in rbac-scopes.js — confirmed by ROLE_PERMISSION_INVENTORY content. ACCURATE.

**Module 20 path inconsistency:** Originally said `services/activity.py` (file), corrected by U7 (FX-011) to `backend/services/activity/` (directory). MODULE_INVENTORY.md Module 20 now shows `backend/services/activity/`. ACCURATE post-U7.

### Discrepancies Found
- API_INVENTORY.md generation header still says "43 files" after U7 corrections — a residual oversight
- MODULE_INVENTORY.md "28 documented modules" figure is stale — U7 added Module 29, making it 29; actual src/ modules is 34

### Confidence Level: HIGH (post-U7)
Post-U7 corrections make the inventories substantially accurate. The remaining 43-vs-44 route file count in the header is a minor residual error.

---

## U2 — Documentation Catalogue

### What Was Claimed
DOC_CATALOGUE.md produced, cataloguing 130 files at U2 generation time. Updated post-U7 to 141 (130 + 11 files added by U5/U6/U7 outputs and _archive/README.md).

### What Was Verified

**Current .md file count:** 170 total .md files in the repository (excluding node_modules, .venv, pgsql). Subtract 3 auto-generated .pytest_cache/README.md files = 167 project-owned .md files. The DOC_CATALOGUE claims 141.

**Gap analysis:** 167 actual vs 141 catalogued = 26 files not in catalogue. These include:
- U8 outputs at root: WORKSPACE_SEALING_REPORT.md, C_DRIVE_LEAKAGE_AUDIT.md, SEALED_WORKSPACE_VALIDATION.md (3 files)
- U8 process prompt at root: U8 — WORKSPACE SEALING.md (1 file)
- U9 outputs in u-series: TEST_SUITE_PLAN.md, SECURITY_TEST_PLAN.md, LOAD_TEST_PLAN.md, HARDENING_PLAN.md, VALIDATION_COMMANDS.md (5 files)
- U9 process prompt at root: U9 — TEST SUITE PLANNING.md (1 file)
- U5/U6/U7 process prompts at root: U6 — DOC TO CODE DELTA ANALYSIS.md, U7 — DELTA REMEDIATION.md (2 files — U5 prompt was protected at U5 time, counted in 141; U6/U7 process prompts may have been generated after catalogue update)
- Current audit task file: U0–U9 LEGACY MODERNIZATION AUDIT.md (1 file)
- Other possible uncounted files: ~13 more

The DOC_CATALOGUE.md was last updated after U7 (FX-016) and does not include U8/U9 outputs. This is expected given the catalogue was not updated after U7.

**5 random entry classification spot-check:**
- CLAUDE.md: classified Authority/AUTHORITY/Active — CORRECT
- REPOSITORY_REALITY_REPORT.md: classified as Report — CORRECT
- docs/archive/REBUILD-PLAN.md: classified as Archive/SUPERSEDED — CORRECT
- backend/docs/domain/contract-lifecycle-management.md: classified as Reference — CORRECT
- docs/reports/session/SYSTEM-SNAPSHOT.md: classified as Report/HISTORICAL — CORRECT

### Discrepancies Found
- DOC_CATALOGUE count: 141 claimed, ~167 actual (26-file gap from U8/U9 outputs not catalogued)
- The catalogue is accurate as of U7 but has not been maintained since

### Confidence Level: MEDIUM
Catalogue was accurate when last updated (post-U7). Now stale by approximately 26 files. Classifications reviewed are correct.

---

## U3 — Documentation Normalization

### What Was Claimed
DOC_NORMALIZATION_REPORT.md, DOC_CONFLICT_REGISTER.md, DOC_DUPLICATION_REGISTER.md, DOC_STALE_REFERENCE_REPORT.md produced. 7 conflicts found (3 critical), 12 stale references found. 2 SUPERSEDED banners applied. Most issues flagged for human review.

### What Was Verified

**SUPERSEDED banners applied:**
- docs/archive/DOC-CATALOGUE.md line 1: Banner reads `> **SUPERSEDED** — see [DOC_CATALOGUE.md](DOC_CATALOGUE.md) (U3 normalization, 2026-06-20)` — CONFIRMED
- docs/archive/REBUILD-PLAN.md line 1: Banner reads `> **SUPERSEDED** — see [COMMERCIALISATION-PLAN.md](COMMERCIALISATION-PLAN.md) (U3 normalization, 2026-06-20)` — CONFIRMED

**3 Critical conflicts still present:**
- C-001: SYSTEM-SNAPSHOT.md shows C3 as "← CURRENT"; COMMERCIALISATION-PLAN.md says "C6 ← CURRENT". Live verification of SYSTEM-SNAPSHOT.md confirms C3 is still shown as current (line 42: "C3 | Code Hardening | ← CURRENT — Redis..."). CONFLICT UNRESOLVED.
- C-002: COMMERCIALISATION-PLAN.md Status header says "C6 ← CURRENT (C5 complete 2026-06-02)" but RESUME POINT table shows C5 and C6 both as "⬜ pending". Verified in live COMMERCIALISATION-PLAN.md. CONFLICT UNRESOLVED.
- C-003: Frontend API wiring — docs claim "75/75 wired," code evidence says ~7% wired. CONFLICT UNRESOLVED (requires human decision).

**Stale references status:**
- SR-001, SR-002: Fixed by U5 ✓
- SR-003, SR-004, SR-005: U3 deferred these pending C-002 resolution; U5 fixed them anyway. The fixes themselves are technically correct (file path updates), but the documented procedure (defer until C-002 resolved) was not followed.
- SR-006 through SR-012: Still present in their respective documents.

**Procedural finding:** U3 explicitly documented that SR-003 and SR-004 should NOT be fixed "because C-002 means the file needs human review before any edits." U5 then fixed SR-003 and SR-004 without first resolving C-002. This contradicts the U3 rationale, though the fixes themselves are technically valid path updates.

### Discrepancies Found
- 7 of 12 stale references remain unresolved (SR-006 through SR-012)
- U5 overrode U3's "do not fix" recommendation for SR-003/SR-004 without resolving C-002
- 3 critical conflicts unresolved (intentionally deferred, but status is unchanged)

### Confidence Level: HIGH
Analysis was thorough and correctly identified conflicts. The procedural SR-003/SR-004 issue is a documentation inconsistency, not an error in the conflict analysis itself.

---

## U4 — Workspace Restructuring Plan

### What Was Claimed
WORKSPACE_RESTRUCTURING_PLAN.md, FILE_RELOCATION_MATRIX.md, FOLDER_PURPOSE_MATRIX.md, BREAKAGE_RISK_REPORT.md produced. Plan to move 42 files, retain 8 authority docs at root, create 5 new folders.

### What Was Verified

**Plan vs execution:** U5 moved exactly 42 files as planned. 5 folders created as planned. FILE_RELOCATION_MATRIX.md covered all 42 moves — confirmed by U5 RESTRUCTURING_EXECUTION_REPORT.md.

**Protected files list:** The plan lists 8 authority docs that must stay at root. U5 confirmed all 8 are present. However, the plan could not anticipate that U5 itself would create 3 new execution reports at root (RESTRUCTURING_EXECUTION_REPORT.md, STALE_LINK_FIX_REPORT.md, POST_RESTRUCTURE_VALIDATION.md), nor that U5-U9 process prompts would accumulate at root.

**Folder purpose matrix:** 5 folders created — docs/archive/, docs/reference/, docs/reports/session/, docs/reports/u-series/, docs/reports/ (parent). All confirmed to exist and contain the files assigned to them.

**Missing from plan:** The plan did not account for:
1. U5 execution reports being generated at root (not moved anywhere)
2. U6/U7/U8/U9 process prompts and execution reports accumulating at root
3. Result: root now has 20 .md files instead of the planned 8-9

**Breakage risk accuracy:** BREAKAGE_RISK_REPORT.md correctly identified COMMERCIALISATION-PLAN.md as medium risk (10 link updates needed). U5 confirmed 10 edits applied to this file.

### Discrepancies Found
- The plan did not scope the fact that U5's own execution outputs would land at root — creating a structural gap immediately upon execution
- The U4 plan was accurate for the files that existed at plan time; the gap is forward-looking

### Confidence Level: HIGH
Plan was thorough and accurate for its scope. The post-execution root inflation is a structural gap not in the plan, not a plan accuracy issue.

---

## U5 — Workspace Restructuring Execution

### What Was Claimed
RESTRUCTURING_EXECUTION_REPORT.md, STALE_LINK_FIX_REPORT.md, POST_RESTRUCTURE_VALIDATION.md produced. 42 files moved, 0 errors, 17 reference edits across 6 documents. POST_RESTRUCTURE_VALIDATION result: PASS, "Final root .md file count: 9 files."

### What Was Verified

**Files at claimed new paths (spot-check):**
- docs/archive/DOC-CATALOGUE.md — CONFIRMED PRESENT
- docs/archive/REBUILD-PLAN.md — CONFIRMED PRESENT
- docs/reports/u-series/REPOSITORY_REALITY_REPORT.md — CONFIRMED PRESENT
- docs/reports/session/SYSTEM-SNAPSHOT.md — CONFIRMED PRESENT
- docs/reference/RENDER-DEPLOY.md — CONFIRMED PRESENT

**Protected files at original paths:**
- CLAUDE.md, DESIGN-SPEC.md, FRAMEWORK.md, PAGE-BUILD-PROTOCOL.md, COMMERCIALISATION-PLAN.md, PRODUCT-SPEC.md, README.md, CONTRIBUTING.md — ALL CONFIRMED AT ROOT

**Root file count claim:** POST_RESTRUCTURE_VALIDATION.md claims "Final root .md file count: 9 files (8 authority docs + U5 prompt)." The 3 U5 execution outputs themselves (RESTRUCTURING_EXECUTION_REPORT.md, STALE_LINK_FIX_REPORT.md, POST_RESTRUCTURE_VALIDATION.md) are at root and were created by U5. True root count immediately after U5 was therefore 12 (9 protected + 3 newly created outputs). The validation undercounts its own outputs.

**Location of U5 execution reports:** RESTRUCTURING_EXECUTION_REPORT.md, STALE_LINK_FIX_REPORT.md, POST_RESTRUCTURE_VALIDATION.md are at D:\SaaS\CRM\ root — NOT in docs/reports/u-series/. These were not moved to u-series because U5 moved pre-existing files, not its own outputs.

**Reference edits verified:** STALE_LINK_FIX_REPORT.md shows 22 named fixes (F-001 through F-022+). The current COMMERCIALISATION-PLAN.md references `docs/reports/session/SYSTEM-SNAPSHOT.md` and `docs/reports/session/PENDING.md` — confirming link updates were applied.

**_archive/ directory:** Retained README.md (redirect notice). Original 3 files moved to docs/archive/. CONFIRMED.

**U3 SR-003/SR-004 override:** U5 fixed SR-003 (COMMERCIALISATION-PLAN.md DOC-CATALOGUE reference) and SR-004 despite U3 recommending these not be fixed until C-002 is resolved. The fixes are technically correct path updates. The procedural deviation is documented in this report.

**Source code files:** No backend/ or frontend/ source files appear in the relocation matrix. No evidence of source code modification.

### Discrepancies Found
- POST_RESTRUCTURE_VALIDATION.md root count claim (9 files) is inaccurate — actual post-U5 root count was 12
- U5 execution reports are at root, not in u-series (structural gap)
- U5 overrode U3's SR-003/SR-004 deferral without resolving C-002

### Confidence Level: HIGH
Execution itself was accurate. The counting inconsistency and procedural override are documentation-level issues, not execution failures.

---

## U6 — Doc↔Code Delta Analysis

### What Was Claimed
DOC_CODE_DELTA_REPORT.md, UNDOCUMENTED_CODE_REGISTER.md, STALE_DOC_CLAIMS_REGISTER.md, DELTA_SUMMARY_REPORT.md produced. HIGH severity finding: contract_lifecycle_management undocumented. 30 underdocumented routes. Documentation accuracy score 8.4/10.

### What Was Verified

**contract_lifecycle_management HIGH severity finding:**
- backend/src/contract_lifecycle_management/ — api.py, entities.py, services.py, __init__.py — ALL CONFIRMED PRESENT
- v1-contracts.routes.js — CONFIRMED ABSENT (no gateway route exists)
- 12 API_ENDPOINTS in api.py — CONFIRMED (GET/POST /contracts, GET /contracts/{id}, POST /contracts/{id}/review, etc.)
- Finding is accurate and still relevant (resolved only by documentation in U7; gateway route decision deferred to human)

**30 underdocumented routes:**
- v1-collections.routes.js: 11 routes confirmed by direct router count; U1 claimed ~4. Delta: +7. CONFIRMED.
- v1-partners.routes.js: 13 routes (partnersRouter 11 + dealRegistrationsRouter 2). U1 claimed ~5. Delta: +8. CONFIRMED.
- v1-territories.routes.js: 11 routes confirmed by direct router count. U1 claimed ~5. Delta: +6. CONFIRMED.
- The "30 underdocumented" total was the aggregate; individual domain deltas confirmed.

**Route domain file count:** DOC_CODE_DELTA_REPORT.md states "Route domain files: 44" for both documented and actual. This is accurate. API_INVENTORY.md generation header (still saying "43 files") was NOT corrected by U7.

**Accuracy score 8.4/10:** Confirmed present in DELTA_SUMMARY_REPORT.md line 117 (Overall row in a scoring table). Score is credible given the finding that structural documentation is accurate but quantitative claims are stale.

**backend/services/ dual-layer discovery:** U6 correctly identified that MODULE_INVENTORY.md inconsistently referenced src/ and services/ paths. This was partially resolved by U7 (FX-011, FX-012).

### Discrepancies Found
- No significant discrepancies between U6 claims and live code evidence
- Minor: "28 modules documented" claim should acknowledge the U7-era Module 29 (contract_lifecycle_management) that would bring it to 29

### Confidence Level: HIGH
U6 analysis is well-grounded in code evidence. Claims about underdocumented routes are confirmed by direct route file inspection.

---

## U7 — Delta Remediation

### What Was Claimed
DOC_CODE_REMEDIATION_REPORT.md, BACKEND_DOC_ALIGNMENT_STATUS.md produced. 21 of 26 identified items fixed, 5 deferred. Key fixes: RBAC 63→91, API ~198→228, Module 29 added, DOC_CATALOGUE 130→141, Module 20 path corrected.

### What Was Verified

**FX-001 (API route count ~198→228):** API_INVENTORY.md Summary by Method shows Total: 228. CONFIRMED.

**FX-009 (RBAC scope count 63→91):** ROLE_PERMISSION_INVENTORY.md header shows "Complete Scope Inventory (91 scopes)"; role table shows tenant_owner "All (91)". CONFIRMED.

**FX-011 (Module 20 path):** MODULE_INVENTORY.md Module 20 now shows `backend/services/activity/, backend/services/followup/`. CONFIRMED.

**FX-013 (Module 29 added):** MODULE_INVENTORY.md Module 29 (Contract Lifecycle Management) present with 12 API paths. CONFIRMED.

**FX-016 (DOC_CATALOGUE 130→141):** DOC_CATALOGUE.md header shows "141 (130 at U2 generation + 11 added by U5/U6/U7 outputs and _archive/README.md)". CONFIRMED.

**Residual error not fixed:** API_INVENTORY.md generation header still reads "evidence from backend/gateway/routes/v1-*.routes.js (43 files)" — should be 44. This was not corrected by any FX entry.

**5 deferred items (D-001 through D-005):** All confirmed appropriately deferred:
- D-001: Contract lifecycle gateway route — no v1-contracts.routes.js exists (deferred by design)
- D-002: Custom objects gateway route — no v1-custom-objects.routes.js exists (deferred by design)
- D-003: Entity DB schema attributions — ENTITY_INVENTORY.md not updated (deferred by design)
- D-004: Listed as "RESOLVED by FX-015" in report (contradicts "deferred" classification in summary table)
- D-005: 4 backend docs placement — confirmed unchanged (deferred by design)

**U9 module count inconsistency:** TEST_SUITE_PLAN.md (U9) says scope includes "28 backend modules" — using the pre-U7 module count, not the post-U7 count of 29. Minor carry-forward error in U9.

### Discrepancies Found
- API_INVENTORY.md header "43 files" not corrected (should be 44)
- D-004 listed as deferred but actually resolved by FX-015 (internal inconsistency in REMEDIATION_REPORT)

### Confidence Level: HIGH
All major claimed corrections verified in the live documents. The "43 files" header and D-004 classification are minor errors.

---

## U8 — Workspace Sealing

### What Was Claimed
WORKSPACE_SEALING_REPORT.md, C_DRIVE_LEAKAGE_AUDIT.md, SEALED_WORKSPACE_VALIDATION.md produced. Overall verdict: "FULLY SEALED." All tools verified writing to D:. WARN item: PIP_CACHE_DIR inconsistency between .env.local and pip.ini.

**Note:** All three U8 output files are at D:\SaaS\CRM\ root, NOT in docs/reports/u-series/. The audit prompt expected them in u-series.

### What Was Verified (Live Commands)

| Claim | Command | Result | Match? |
|---|---|---|---|
| npm cache → D:\npm-cache | npm config get cache | D:\npm-cache | YES |
| npm prefix → D:\npm | npm config get prefix | D:\npm | YES |
| PLAYWRIGHT_BROWSERS_PATH → D:\ | $env:PLAYWRIGHT_BROWSERS_PATH | D:\dev-cache\playwright | YES |
| TEMP → D:\Temp | $env:TEMP | D:\Temp | YES |
| node_modules on D: | Test-Path frontend/node_modules | True | YES |
| pip.ini cache → D:\ | Get-Content pip.ini | cache-dir = D:\LMS\workspace\.pip-cache | YES |
| PIP_CACHE_DIR not set | $env:PIP_CACHE_DIR | (empty) | YES |

**WARN item verification:** pip.ini (C:\Users\Admin\AppData\Roaming\pip\pip.ini) sets cache-dir to D:\LMS\workspace\.pip-cache. PIP_CACHE_DIR env var is not set. The WORKSPACE_SEALING_REPORT.md noted a discrepancy between .env.local (D:\pip-cache) and pip.ini (D:\LMS\workspace\.pip-cache). Both are on D:, no C: leakage. WARN status confirmed accurate.

**U8 report location:** WORKSPACE_SEALING_REPORT.md, C_DRIVE_LEAKAGE_AUDIT.md, SEALED_WORKSPACE_VALIDATION.md are at D:\SaaS\CRM\ root — not moved to docs/reports/u-series/. This is structurally consistent with U5/U6/U7 execution outputs also remaining at root, but it means the audit prompt's instruction to find them in u-series is incorrect.

### Discrepancies Found
- No discrepancies in sealing claims — all verified accurate
- Structural: U8 output files are at root, not in u-series (same pattern as U5 outputs)

### Confidence Level: HIGH
All sealing claims verified by live command execution. No C: drive leakage confirmed.

---

## U9 — Test Suite Planning

### What Was Claimed
TEST_SUITE_PLAN.md, SECURITY_TEST_PLAN.md, LOAD_TEST_PLAN.md, HARDENING_PLAN.md, VALIDATION_COMMANDS.md produced. Scope: 228 APIs, 28 backend modules, 75 frontend pages. Key claims: python-jose 3.3.0 (3 CVEs), starlette 0.38.6 (3 CVEs), locust 2.44.0, 54 backend test files, 25 E2E playwright files.

### What Was Verified

**python-jose version and CVEs:** SECURITY_TEST_PLAN.md claims "python-jose 3.3.0: 3 CVEs." pip-audit.json (tests/security/pip-audit.json) confirms python-jose 3.3.0 is installed in the .venv with 3 CVEs (PYSEC-2024-232, PYSEC-2024-233, PYSEC-2025-185). ACCURATE against pip-audit.json.

**Critical version inconsistency NOT identified by U9:** requirements.txt specifies `python-jose[cryptography]==3.5.0` but pip-audit.json confirms 3.3.0 is installed. The .venv is out of sync with requirements.txt. U9 correctly reported the installed version (3.3.0) but did not flag the requirements.txt mismatch, which means the intended upgrade to 3.5.0 has not been applied to the venv. This is a security gap.

**starlette CVEs:** Claimed "3 CVEs including multipart DoS and Host header injection." pip-audit.json confirms starlette 0.38.6 with 3 CVEs (CVE-2024-47874 multipart DoS, CVE-2025-54121 blocking, PYSEC-2026-161 Host header). ACCURATE.

**pip CVEs:** Claimed "pip 25.0.1: 4 CVEs." pip-audit.json confirms pip 25.0.1 with 4 CVEs. ACCURATE.

**locust version:** Claimed 2.44.0. pip-audit.json confirms locust 2.44.0. ACCURATE.

**Backend test files:** TEST_SUITE_PLAN.md claims "54 .py files" in backend/tests/. Actual: 79 test_*.py files. This is the same undercount as U0 — U9 inherited U0's incorrect figure without re-verifying. INACCURATE.

**E2E playwright files:** TEST_SUITE_PLAN.md claims "25 .py files" in tests/e2e/playwright/. Actual: 23 files in tests/e2e/playwright/. Additionally, tests/api/ has 8 files (not 6 as claimed — test_tenant_isolation.py and test_auth_contract.py are unlisted). INACCURATE.

**28 vs 29 backend modules in scope:** TEST_SUITE_PLAN.md scope header says "28 backend modules." Post-U7, MODULE_INVENTORY.md has 29 modules. The scope figure is stale (uses pre-U7 count). MINOR INACCURACY.

**VALIDATION_COMMANDS.md paths:** Spot-checked venv path (D:\SaaS\CRM\backend\.venv\Scripts\python.exe) — directory confirmed present. npm cache path (D:\npm-cache) — confirmed by live command. Paths appear correct.

**Coverage claims:** ~80% backend, ~19% API smoke, ~70% E2E workflow — UNVERIFIABLE without running tests. No evidence cited in U9 beyond the CI gate specification.

### Discrepancies Found
- Backend test file count: 54 claimed, 79 actual (46% undercount — same error as U0)
- E2E playwright file count: 25 claimed, 23 actual
- API contract test count: 6 claimed, 8 actual (2 files unlisted: test_tenant_isolation.py, test_auth_contract.py)
- Scope says "28 backend modules" but U7 established 29
- requirements.txt/venv version drift for python-jose (3.5.0 in requirements vs 3.3.0 in venv) not identified

### Confidence Level: MEDIUM
CVE and tooling claims are accurate. Test file counts are materially wrong (inherited from U0 without re-verification). The requirements.txt/venv version drift is a security-relevant gap missed by U9.

---

## Cross-Phase Consistency

| Check | Finding |
|---|---|
| U0 page count (75) ↔ U9 test scope (75 pages) | CONSISTENT |
| U1 API count (228 after U7) ↔ U9 security plan scope (228) | CONSISTENT |
| U2 doc count (141 after U7) ↔ current actual (167) | INCONSISTENT — 26-file gap |
| U0 test count (54) ↔ U9 test count (54) | CONSISTENTLY WRONG — both say 54, actual is 79 |
| U5 PASS verdict ↔ file locations on disk | MOSTLY CONSISTENT — files are at new paths; U5 reports themselves at root is an expected structural artefact |
| U8 FULLY SEALED ↔ live commands | CONFIRMED |
| U6 confirms 44 route files ↔ API_INVENTORY.md header (43 files) | INCONSISTENT — U7 did not correct the header |
| U3 C-002 unresolved ↔ U5 fixes SR-003/SR-004 | PROCEDURAL INCONSISTENCY — U5 acted against U3's stated deferral rationale |
| U7 adds Module 29 ↔ U9 scope says 28 modules | INCONSISTENT — U9 did not pick up U7's addition |

---

*End U0_U9_FORENSIC_AUDIT_REPORT.md*
