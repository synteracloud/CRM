# U0–U9 CONTRADICTION REGISTER — Pakistan CRM OS

**Generated:** 2026-06-21 — Independent forensic audit
**Auditor:** Claude Sonnet 4.6

---

## Format

Each entry records a contradiction between two phases, or between a phase output and live code/files.

| Column | Meaning |
|---|---|
| ID | Contradiction identifier |
| Phase A | First phase or source |
| Phase B | Second phase or source |
| Claim A | Specific claim from Phase A |
| Claim B | Specific claim from Phase B (contradicts A) |
| Verdict | Which is correct; or if both are partially wrong |

---

## Contradictions

### CONT-001 — Gateway route file count

| Field | Value |
|---|---|
| **Phase A** | U0 (REPOSITORY_REALITY_REPORT.md §3) |
| **Claim A** | "Gateway API Route Groups (43 — all v1-*.routes.js confirmed)" |
| **Phase B** | U6 (DOC_CODE_DELTA_REPORT.md §1) |
| **Claim B** | "Route domain files: 44" (both documented and actual) |
| **Phase C (live)** | PowerShell Get-ChildItem on backend/gateway/routes/ |
| **Claim C** | 44 v1-*.routes.js files returned |
| **Verdict** | U0 undercounted by 1. U6 is correct. The 44th file exists. API_INVENTORY.md header (still saying "43 files") is also wrong. |

---

### CONT-002 — Backend test file count

| Field | Value |
|---|---|
| **Phase A** | U0 (REPOSITORY_REALITY_REPORT.md §6) |
| **Claim A** | "54 test files" cover all 34 src/ modules |
| **Phase B** | U9 (TEST_SUITE_PLAN.md §1) |
| **Claim B** | "54 .py files" in backend/tests/ |
| **Phase C (live)** | PowerShell Get-ChildItem on backend/tests/ -Filter "test_*.py" |
| **Claim C** | 79 test_*.py files |
| **Verdict** | Both U0 and U9 are wrong. Actual is 79. U9 copied U0's figure without re-verifying. The 54 count appears to correspond to a state earlier than the current repository. |

---

### CONT-003 — Commercialization phase current status

| Field | Value |
|---|---|
| **Phase A** | docs/reports/session/SYSTEM-SNAPSHOT.md (last updated 2026-06-01) |
| **Claim A** | "C3 | Code Hardening | ← CURRENT" |
| **Phase B** | COMMERCIALISATION-PLAN.md (Status header) |
| **Claim B** | "C6 ← CURRENT (C5 complete 2026-06-02 — all production gates pass)" |
| **Verdict** | C-001 contradiction flagged by U3, deferred to human. Still unresolved. Cannot determine correct current phase from documentation alone due to C-002 (same file is internally inconsistent). |

---

### CONT-004 — COMMERCIALISATION-PLAN.md C5/C6 internal inconsistency

| Field | Value |
|---|---|
| **Phase A** | COMMERCIALISATION-PLAN.md Status header (line 5) |
| **Claim A** | "C6 ← CURRENT (C5 complete 2026-06-02 — all production gates pass)" |
| **Phase B** | COMMERCIALISATION-PLAN.md RESUME POINT table (lines 24-25) |
| **Claim B** | C5: "⬜ pending"; C6: "⬜ pending" |
| **Verdict** | C-002 internal contradiction in the same file. Status header was updated; RESUME POINT table was not. Cannot resolve without human confirmation. Still unresolved. |

---

### CONT-005 — Frontend API wiring percentage

| Field | Value |
|---|---|
| **Phase A** | SYSTEM-SNAPSHOT.md + COMMERCIALISATION-PLAN.md carry-forward |
| **Claim A** | SYSTEM-SNAPSHOT.md: "75/75 wired to live API"; COMMERCIALISATION-PLAN.md: "DUMMY_MODE: false in crm-api.js" |
| **Phase B** | U0/U1 code evidence (REPOSITORY_REALITY_REPORT.md §7, AUTHORITY_RECONSTRUCTION_REPORT.md) |
| **Claim B** | "~7% wired: 5 pages confirmed wired; 70 still DUMMY_MODE"; "DUMMY_MODE: true in all pages currently" |
| **Verdict** | C-003 contradiction. U0/U1 represent ground truth from code scan. SYSTEM-SNAPSHOT.md and COMMERCIALISATION-PLAN.md carry-forward are stale or incorrect. |

---

### CONT-006 — U3 SR-003/SR-004 deferral vs U5 execution

| Field | Value |
|---|---|
| **Phase A** | U3 (DOC_STALE_REFERENCE_REPORT.md SR-003, SR-004) |
| **Claim A** | SR-003 and SR-004 "cannot fix without human review because C-002 means the file [COMMERCIALISATION-PLAN.md] needs human review before any edits" |
| **Phase B** | U5 (STALE_LINK_FIX_REPORT.md F-003, F-004) |
| **Claim B** | SR-003 fix applied to COMMERCIALISATION-PLAN.md line 61; SR-004 fix applied to COMMERCIALISATION-PLAN.md line 666 |
| **Verdict** | U5 contradicted U3's explicit deferral rationale. The edits themselves are technically correct (DOC-CATALOGUE.md → docs/reports/u-series/DOC_CATALOGUE.md path updates). However C-002 was not resolved before the edits, violating U3's documented precondition. |

---

### CONT-007 — U5 root file count self-contradiction

| Field | Value |
|---|---|
| **Phase A** | U5 (POST_RESTRUCTURE_VALIDATION.md §3) |
| **Claim A** | "Final root .md file count: 9 files (8 authority docs + U5 prompt). Target was 8 authority docs + U5. Correct." |
| **Phase B** | U5 execution (RESTRUCTURING_EXECUTION_REPORT.md + STALE_LINK_FIX_REPORT.md + POST_RESTRUCTURE_VALIDATION.md) |
| **Claim B** | Three output files exist at D:\SaaS\CRM\ root, created by U5 during execution |
| **Verdict** | U5's own count excludes its own outputs. True post-U5 root count was 12 (9 protected + 3 newly created). The validation document does not count the 3 files it and its sibling documents represent. |

---

### CONT-008 — python-jose requirements.txt vs venv

| Field | Value |
|---|---|
| **Phase A** | backend/requirements.txt |
| **Claim A** | `python-jose[cryptography]==3.5.0` |
| **Phase B** | tests/security/pip-audit.json (installed .venv) |
| **Claim B** | `"name":"python-jose","version":"3.3.0"` with 3 CVEs |
| **Verdict** | Requirements specifies 3.5.0; installed version is 3.3.0. The venv was not rebuilt after requirements.txt was updated. U9 correctly reported 3.3.0 from pip-audit.json but did not identify this drift. The net security posture is worse than requirements.txt suggests. |

---

### CONT-009 — U7 module count vs U9 scope

| Field | Value |
|---|---|
| **Phase A** | U7 (DOC_CODE_REMEDIATION_REPORT.md FX-013) |
| **Claim A** | "Added Module 29 (Contract Lifecycle Management)" to MODULE_INVENTORY.md |
| **Phase B** | U9 (TEST_SUITE_PLAN.md scope header) |
| **Claim B** | "Scope: 228 APIs, 28 backend modules, 75 frontend pages, 7 roles, 91 scopes" |
| **Verdict** | U9 was generated after U7 but uses the pre-U7 module count of 28. U7 established 29 modules. Minor carry-forward error. |

---

### CONT-010 — U6 44 route files vs API_INVENTORY.md header post-U7

| Field | Value |
|---|---|
| **Phase A** | U6 (DOC_CODE_DELTA_REPORT.md §1) |
| **Claim A** | "Route domain files: 44" (confirmed actual count) |
| **Phase B** | API_INVENTORY.md generation header (post-U7) |
| **Claim B** | "evidence from backend/gateway/routes/v1-*.routes.js (43 files)" |
| **Verdict** | U6 correctly identified 44. U7 corrected route counts but did not update the header. The header value is wrong and contradicts U6's confirmed finding. |

---

*End U0_U9_CONTRADICTION_REGISTER.md*
