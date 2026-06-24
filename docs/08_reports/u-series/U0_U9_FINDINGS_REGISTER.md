# U0–U9 FINDINGS REGISTER — Pakistan CRM OS

**Generated:** 2026-06-21 — Independent forensic audit
**Auditor:** Claude Sonnet 4.6

---

## Severity Key

| Severity | Meaning |
|---|---|
| Critical | Blocks trust in the phase output or represents a security/governance gap |
| High | Materially wrong claim; affects downstream decisions |
| Medium | Wrong or stale claim; causes confusion but does not block decisions |
| Low | Minor inaccuracy; cosmetic or edge-case impact |
| Info | Informational; consistent with claims; no action required |

## Status Key

| Status | Meaning |
|---|---|
| Confirmed | Verified present in live code/files |
| Unresolved | Issue is still present in the repository |
| False Positive | Audit claim was wrong; original phase was correct |

---

## Findings

| ID | Phase | Finding | Severity | Evidence | Status |
|---|---|---|---|---|---|
| F-001 | U0/U9 | Backend test file count claimed as 54; actual is 79 test_*.py files in backend/tests/ (plus 31 in root tests/ = 110 total). The 54 figure matches no counting method. U9 inherited this error from U0 without re-verifying. | Critical | PowerShell: Get-ChildItem backend/tests -Filter "test_*.py" -Recurse returns 79 entries | Unresolved |
| F-002 | U9 | python-jose version drift: requirements.txt specifies 3.5.0 but pip-audit.json (installed .venv) shows 3.3.0. The .venv has not been rebuilt since requirements.txt was updated. Three CVEs remain in the installed package that have been patched in 3.5.0. U9 correctly reported the 3.3.0 installed version but did not flag the requirements.txt mismatch. | Critical | requirements.txt line 12: `python-jose[cryptography]==3.5.0`; pip-audit.json: `"name":"python-jose","version":"3.3.0","vulns":[...]` | Unresolved |
| F-003 | U5/U8 | Execution reports for U5 and U8 are at D:\SaaS\CRM\ root, NOT in docs/reports/u-series/. Affected files: RESTRUCTURING_EXECUTION_REPORT.md, STALE_LINK_FIX_REPORT.md, POST_RESTRUCTURE_VALIDATION.md (U5), WORKSPACE_SEALING_REPORT.md, C_DRIVE_LEAKAGE_AUDIT.md, SEALED_WORKSPACE_VALIDATION.md (U8). Root now has 20 .md files vs the U4 plan's target of 8-9. | High | PowerShell listing of D:\SaaS\CRM\ root .md files; file listing confirmed | Unresolved |
| F-004 | U3/U5 | U3 explicitly documented that SR-003 and SR-004 must NOT be fixed until C-002 is resolved by a human, because COMMERCIALISATION-PLAN.md needs human verification before edits. U5 fixed SR-003 (F-003 in STALE_LINK_FIX_REPORT.md) and SR-004 (F-004) without resolving C-002. C-002 remains unresolved. | High | DOC_STALE_REFERENCE_REPORT.md SR-003: "cannot fix...defer to human refresh"; STALE_LINK_FIX_REPORT.md F-003/F-004: fixes applied; DOC_CONFLICT_REGISTER.md C-002: still unresolved | Unresolved |
| F-005 | U0 | Gateway route group count: U0 claims 43 gateway route groups. Actual: 44 v1-*.routes.js files confirmed by PowerShell directory listing. The gateway README mentions 43 but the actual file count is 44. | High | PowerShell: Get-ChildItem backend/gateway/routes -Filter "v1-*.routes.js" returns 44 entries; REPOSITORY_REALITY_REPORT.md §3 says "43 — all v1-*.routes.js confirmed" | Unresolved |
| F-006 | U5 | POST_RESTRUCTURE_VALIDATION.md claims "Final root .md file count: 9 files (8 authority docs + U5 prompt)." However U5 itself created 3 output files at root during execution (RESTRUCTURING_EXECUTION_REPORT.md, STALE_LINK_FIX_REPORT.md, POST_RESTRUCTURE_VALIDATION.md itself). True post-U5 root .md count was 12, not 9. | High | POST_RESTRUCTURE_VALIDATION.md line 104; U5 output files confirmed at D:\SaaS\CRM\ root | Confirmed |
| F-007 | U7 | API_INVENTORY.md generation header still reads "evidence from backend/gateway/routes/v1-*.routes.js (43 files)" after U7 corrections. U6 correctly identified 44 files. U7 fixed route counts but did not correct this header. | Medium | API_INVENTORY.md line 2: "(43 files)"; PowerShell confirms 44 files; U6 DOC_CODE_DELTA_REPORT.md "Route domain files: 44" | Unresolved |
| F-008 | U2 | DOC_CATALOGUE.md claims 141 project-owned .md files. Actual count: 170 total (PowerShell); 167 excluding .pytest_cache/README.md auto-generated files. Gap: 26 files. U8 and U9 outputs not catalogued after U7. Catalogue is stale. | Medium | PowerShell: Get-ChildItem D:\SaaS\CRM -Filter "*.md" -Recurse (excluding library dirs) = 170; DOC_CATALOGUE.md header: 141 | Unresolved |
| F-009 | U9 | TEST_SUITE_PLAN.md scope header says "28 backend modules." U7 (FX-013) added Module 29 (contract_lifecycle_management) to MODULE_INVENTORY.md. U9 uses the pre-U7 count. | Medium | TEST_SUITE_PLAN.md line 3: "28 backend modules"; MODULE_INVENTORY.md Module 29 confirmed present | Unresolved |
| F-010 | U9 | E2E Playwright test count: TEST_SUITE_PLAN.md claims "25 .py files" in tests/e2e/playwright/. Actual: 23 files. API contract test count: claimed "6 .py files" in tests/api/; actual 8 (test_tenant_isolation.py and test_auth_contract.py are absent from the claimed list). | Medium | PowerShell: Get-ChildItem tests\e2e\playwright -Filter "test_*.py" = 23; Get-ChildItem tests\api -Filter "test_*.py" = 8 | Confirmed |
| F-011 | U3 | 7 of 12 stale references documented in DOC_STALE_REFERENCE_REPORT.md remain unresolved: SR-006 (PROGRESS.md REBUILD-PLAN ref), SR-007 (CURRENT_PROJECT_STATUS.md commercialization status), SR-008 (DOC-CATALOGUE.md REBUILD-PLAN ref — in superseded doc, acceptable), SR-009 (DOC-CATALOGUE.md count — superseded doc, acceptable), SR-010 (DOC-READ-LOG.md count 109), SR-011 (SYSTEM-SNAPSHOT.md "78 active docs"), SR-012 (DOC_CATALOGUE.md archive reference). | Medium | DOC_STALE_REFERENCE_REPORT.md SR-006 through SR-012; live docs confirm each is still present | Unresolved |
| F-012 | U3 | Three critical conflicts from DOC_CONFLICT_REGISTER.md remain unresolved: C-001 (SYSTEM-SNAPSHOT.md shows C3 current vs COMMERCIALISATION-PLAN.md C6 current), C-002 (COMMERCIALISATION-PLAN.md internal inconsistency — Status header says C5 complete but RESUME POINT shows C5/C6 pending), C-003 (frontend API wiring docs claim 75/75 but code shows ~7%). These were correctly deferred to human review. Flagged here for completeness. | Medium | SYSTEM-SNAPSHOT.md line 42: "C3 | Code Hardening | ← CURRENT"; COMMERCIALISATION-PLAN.md line 5: "C6 ← CURRENT" and line 25: "C5 | ⬜ pending" | Unresolved |
| F-013 | U7 | D-004 in REMEDIATION_REPORT.md is listed in the deferred items section but its status field reads "RESOLVED by FX-015." This contradicts the summary table which counts 5 deferred items. The count of 5 deferred items is overstated by 1 — there are effectively 4 open deferrals. | Low | DOC_CODE_REMEDIATION_REPORT.md D-004 section: "Status: RESOLVED by FX-015"; Summary table: "5 items deferred" | Confirmed |
| F-014 | U4 | U4 WORKSPACE_RESTRUCTURING_PLAN.md does not scope for its own execution outputs (U5/U6/U7/U8/U9 reports) landing at root. The plan correctly identifies 8 authority docs that must stay; but as phases execute, root accumulates additional files not covered by the plan. Root now has 20 .md files. | Low | WORKSPACE_RESTRUCTURING_PLAN.md §2 list; live root file count confirmed at 20 .md files | Confirmed |
| F-015 | U6 | DELTA_SUMMARY_REPORT.md §3 notes "28 documented modules" as baseline. This was accurate at U6 generation time (contract_lifecycle_management was found as undocumented). After U7 adds Module 29, the "28 documented" figure in U6 becomes stale but U6 is a point-in-time report so this is expected. Minor clarity issue. | Low | DELTA_SUMMARY_REPORT.md "all 28 documented modules"; MODULE_INVENTORY.md now has 29 | Confirmed |
| F-016 | U2 | DOC_CATALOGUE.md was not updated after U7 to reflect U8 and U9 outputs (approximately 11 files). The catalogue rule in COMMERCIALISATION-PLAN.md requires "every new .md file catalogued same day." This rule was not followed for U8/U9 outputs. | Low | DOC_CATALOGUE.md header: "141"; U8/U9 produced ~10 new .md files not in catalogue | Unresolved |
| F-017 | U1 | Two open deferrals from U7 remain active: D-002 (custom objects gateway route unconfirmed — no v1-custom-objects.routes.js exists) and D-003 (5 entity DB schema attributions missing for Sprint 5B entities). Both correctly deferred; D-005 (4 backend docs placement) also open. | Info | DOC_CODE_REMEDIATION_REPORT.md D-002, D-003, D-005; confirmed no custom objects route file | Confirmed |
| F-018 | U8 | All U8 workspace sealing claims verified by live command execution. npm cache (D:\npm-cache), npm prefix (D:\npm), PLAYWRIGHT_BROWSERS_PATH (D:\dev-cache\playwright), TEMP (D:\Temp), pip.ini (D:\LMS\workspace\.pip-cache), node_modules (D:\SaaS\CRM\frontend\node_modules) — all on D:. WARN item (PIP_CACHE_DIR inconsistency) confirmed still present and non-critical. | Info | Live PowerShell: npm config get cache = D:\npm-cache; npm config get prefix = D:\npm; $env:PLAYWRIGHT_BROWSERS_PATH = D:\dev-cache\playwright; $env:TEMP = D:\Temp; pip.ini cache-dir = D:\LMS\workspace\.pip-cache | Confirmed |
| F-019 | U9 | locust version 2.44.0: confirmed in pip-audit.json. starlette 0.38.6 CVEs: confirmed (3 CVEs). pip 25.0.1 CVEs: confirmed (4 CVEs). VALIDATION_COMMANDS.md paths spot-checked as correct. | Info | pip-audit.json: locust 2.44.0 (no vulns); starlette 0.38.6 (3 vulns); pip 25.0.1 (4 vulns) | Confirmed |
| F-020 | U1 | All 75 custom HTML pages verified present: followups.html, leads.html, contacts.html, dashboard.html, marketing-workspace.html, workflow-builder.html, ai-copilot.html + all 68 others from U0 list. | Info | PowerShell: all 75 pages returned True for Test-Path | Confirmed |
| F-021 | U1 | All 34 backend src/ module directories confirmed. All 44 gateway route files confirmed. contract_lifecycle_management module confirmed with api.py, entities.py, services.py. No gateway route for custom_objects or contract_lifecycle_management. | Info | PowerShell: 34 directories in backend/src/; 44 v1-*.routes.js files; individual module files read | Confirmed |
| F-022 | U0 | SUPERSEDED banners applied to DOC-CATALOGUE.md (line 1) and REBUILD-PLAN.md (line 1) as claimed by U3. Both confirmed present. | Info | Read: docs/archive/DOC-CATALOGUE.md line 1; docs/archive/REBUILD-PLAN.md line 1 | Confirmed |

---

*End U0_U9_FINDINGS_REGISTER.md*
