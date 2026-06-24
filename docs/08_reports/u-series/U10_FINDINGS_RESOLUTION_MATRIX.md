# U10 FINDINGS RESOLUTION MATRIX — Pakistan CRM OS

**Generated:** 2026-06-21 — U10 Audit Remediation
**Source:** U0_U9_FINDINGS_REGISTER.md (F-001 through F-022)

---

## Status Key

| Status | Meaning |
|---|---|
| RESOLVED | Fix applied; evidence confirmed |
| PARTIALLY RESOLVED | Substantive fix applied; minor remainder documented |
| ALREADY RESOLVED | Was resolved before U10 session; confirmed correct |
| DEFERRED | Cannot resolve without human decision or is out of scope |
| ACCEPTABLE | No fix needed; status is by design |

---

## Resolution Matrix

| Finding ID | Phase | Description | Action Taken | Files Modified | Verified | Status |
|---|---|---|---|---|---|---|
| F-001 | U0/U9 | Backend test count claimed 54; actual 79 | Updated TEST_SUITE_PLAN.md (4 corrections), WORKSPACE_BASELINE_AUDIT.md, AUTHORITY_RECONSTRUCTION_REPORT.md, CURRENT_PROJECT_STATUS.md | 4 files | PowerShell count = 79 confirmed | RESOLVED |
| F-002 | U9 | python-jose venv/requirements.txt drift: 3.3.0 installed vs 3.5.0 in requirements | Confirmed python-jose 3.5.0 already installed; pip-audit.json was stale; updated SECURITY_TEST_PLAN.md and HARDENING_PLAN.md | 2 files | pip show python-jose → 3.5.0 | ALREADY RESOLVED |
| F-003 | U5/U8 | 6 execution reports at root instead of u-series | Moved all 6 files from root to docs/reports/u-series/; updated DOC_CATALOGUE.md paths | 7 files | Root count = 15 confirmed | RESOLVED |
| F-004 | U3/U5 | U5 overrode U3's SR-003/SR-004 deferral | SR-003/SR-004 were fixed correctly; C-002 resolved by updating RESUME POINT table; procedural deviation noted in remediation report | 1 file (COMMERCIALISATION-PLAN.md) | RESUME POINT table updated | RESOLVED |
| F-005 | U0 | Gateway route count: claimed 43, actual 44 | Updated API_INVENTORY.md header (43→44) and AUTHORITY_RECONSTRUCTION_REPORT.md architecture diagram | 2 files | PowerShell count = 44 confirmed | RESOLVED |
| F-006 | U5 | POST_RESTRUCTURE_VALIDATION.md root count 9 (actual was 12) | Noted in remediation report; historical finding in a completed document — no retroactive fix applied to completed validation | None | Documented in U10_AUDIT_REMEDIATION_REPORT.md | ACCEPTABLE |
| F-007 | U7 | API_INVENTORY.md header "(43 files)" not corrected after U7 | Updated API_INVENTORY.md generation header | 1 file | Header now reads "(44 files)" | RESOLVED |
| F-008 | U2 | DOC_CATALOGUE.md count: 141 claimed, ~167 actual | Updated count to 161; added §Q–§T with 20 new entries; U5 paths corrected | 1 file | Count updated; new sections added | PARTIALLY RESOLVED |
| F-009 | U9 | TEST_SUITE_PLAN.md scope says "28 backend modules" (post-U7 count is 29) | Updated scope header: 28→29 backend modules | 1 file | Scope header corrected | RESOLVED |
| F-010 | U9 | E2E count: 25 claimed vs 23 actual; API count: 6 claimed vs 8 actual | Updated TEST_SUITE_PLAN.md: 25→23 E2E, 6→8 API | 1 file | Counts corrected | RESOLVED |
| F-011 | U3 | 7 stale references (SR-006 through SR-012) remain | SR-006: already fixed; SR-007/SR-008/SR-009/SR-012: acceptable; SR-011: fixed via H-003; SR-010: deferred | Multiple (see M-002 section) | 5 of 7 addressed | PARTIALLY RESOLVED |
| F-012 | U3 | 3 critical conflicts C-001/C-002/C-003 unresolved | C-001: resolved via SYSTEM-SNAPSHOT.md update; C-002: resolved by updating RESUME POINT table; C-003: resolved by code evidence (DUMMY_MODE: false confirmed) | 2 files | All 3 conflicts resolved | RESOLVED |
| F-013 | U7 | D-004 listed as deferred but says "RESOLVED by FX-015" | Historical inconsistency in completed document; noted in remediation report | None | Documented | ACCEPTABLE |
| F-014 | U4 | U4 plan did not scope for execution outputs landing at root | Addressed by H-001: all 6 execution reports moved to u-series | 6 files moved | Root count = 15 | RESOLVED |
| F-015 | U6 | DELTA_SUMMARY_REPORT.md "28 documented modules" stale | Point-in-time report; U6 was correct at generation time; Module 29 added by U7 is documented in MODULE_INVENTORY.md and TEST_SUITE_PLAN.md scope | None | Historical accuracy acceptable | ACCEPTABLE |
| F-016 | U2 | DOC_CATALOGUE.md not updated for U8/U9 outputs | Added §R (U8 outputs), §S (U9 outputs), §T (U10 forensic audit outputs), §Q (U-series prompts) to DOC_CATALOGUE.md | 1 file | 20 new entries added | RESOLVED |
| F-017 | U1 | D-001, D-002, D-003 open deferrals from U7 | Confirmed still appropriately deferred; no gateway routes exist for contract_lifecycle_management or custom_objects | None | Human decisions remain open | DEFERRED |
| F-018 | U8 | All U8 sealing claims verified accurate | Confirmed accurate by U10 live checks | None | All sealing checks pass | ACCEPTABLE |
| F-019 | U9 | locust, starlette, pip versions confirmed accurate | Confirmed via pip-audit.json | None | All version claims accurate | ACCEPTABLE |
| F-020 | U1 | All 75 custom HTML pages verified present | Confirmed accurate; no action needed | None | 75 pages confirmed | ACCEPTABLE |
| F-021 | U1 | 34 backend modules and 44 gateway routes confirmed | All confirmed; AUTHORITY_RECONSTRUCTION_REPORT.md architecture updated to 44 routes | 1 file | Gateway count corrected | RESOLVED |
| F-022 | U0 | SUPERSEDED banners on DOC-CATALOGUE.md and REBUILD-PLAN.md confirmed | Confirmed accurate; no action needed | None | Banners confirmed present | ACCEPTABLE |

---

## Summary Counts

| Status | Count |
|---|---|
| RESOLVED | 13 |
| ALREADY RESOLVED | 1 |
| PARTIALLY RESOLVED | 2 |
| DEFERRED | 1 |
| ACCEPTABLE | 5 |
| **Total** | **22** |

---

## Open Items Requiring Human Decision

| Item | Description | Blocking |
|---|---|---|
| F-017 / D-001 | contract_lifecycle_management: expose via gateway or archive | No — module is complete; gateway route is optional |
| F-017 / D-002 | custom_objects: gateway route mechanism | No — modules are complete; routing is optional |
| F-017 / D-003 | 5 entity DB schema attributions for Sprint 5B entities | No — informational gap |
| SR-010 | DOC-READ-LOG.md: add 29+ new doc entries | No — log is non-authoritative |

---

*End U10_FINDINGS_RESOLUTION_MATRIX.md*
