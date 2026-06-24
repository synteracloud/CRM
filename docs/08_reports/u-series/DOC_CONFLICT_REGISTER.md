> **HISTORICAL** — Covers pre-governance conflicts as of 2026-06-20 (U3). Most conflicts documented here have been resolved. See [CONFLICT_ANALYSIS_REPORT.md](../../08_reports/CONFLICT_ANALYSIS_REPORT.md) for current conflict state.
> Content preserved for historical reference. Do not update this document.
> Retired: 2026-06-21 (Documentation Normalization Phase — DUP-010 resolution)

# DOC_CONFLICT_REGISTER.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U3 — Documentation Normalization)
**Scope:** Contradictory factual claims between documents, verified from DOC_CATALOGUE.md, DOCUMENT_OWNERSHIP_MATRIX.md, REPOSITORY_REALITY_REPORT.md, and AUTHORITY_RECONSTRUCTION_REPORT.md.

---

## How to read this register

| Column | Meaning |
|---|---|
| ID | Conflict identifier (C-001 through C-007) |
| Doc A / Claim in A | First document and its specific claim |
| Doc B / Claim in B | Second document and its contradicting claim |
| Severity | Critical (blocks decisions) · Moderate (causes confusion) · Minor (cosmetic) |
| Resolution | Fixed / Flagged for human review / Acknowledged |

---

## Conflicts

### C-001 — Commercialization phase current status

| Field | Value |
|---|---|
| **Doc A** | `SYSTEM-SNAPSHOT.md` (last updated 2026-05-31, line 43) |
| **Claim in A** | C3 (Code Hardening) is "← CURRENT"; C4, C5, C6 all show "⬜ pending" |
| **Doc B** | `COMMERCIALISATION-PLAN.md` (Status header, line 5) |
| **Claim in B** | "Status: C6 ← CURRENT (C5 complete 2026-06-02 — all production gates pass)" with C4 shown as "✓ COMPLETE 2026-06-01" in the RESUME POINT table |
| **Severity** | **Critical** — any developer reading SYSTEM-SNAPSHOT.md at session start will be directed to work on C3 items that have already been completed |
| **Resolution** | **Flagged for human review** — SYSTEM-SNAPSHOT.md requires a full refresh; the actual current phase cannot be determined from docs alone because C-002 shows COMMERCIALISATION-PLAN.md itself is internally inconsistent |

---

### C-002 — COMMERCIALISATION-PLAN.md internal inconsistency (C5/C6 status)

| Field | Value |
|---|---|
| **Doc A** | `COMMERCIALISATION-PLAN.md` Status header (line 5) |
| **Claim in A** | "C6 ← CURRENT (C5 complete 2026-06-02 — all production gates pass)" |
| **Doc B** | `COMMERCIALISATION-PLAN.md` RESUME POINT table (lines 19–26, same file) |
| **Claim in B** | C5 row: "⬜ pending"; C6 row: "⬜ pending" |
| **Severity** | **Critical** — the RESUME POINT table is the first thing read every session per the session protocol; it contradicts the Status header in the same document |
| **Resolution** | **Flagged for human review** — the Status header appears to have been updated after C5 completion but the RESUME POINT table was not updated. Human must confirm C5 gate was met and update the RESUME POINT table accordingly |

---

### C-003 — Frontend API wiring: doc claims vs code evidence

| Field | Value |
|---|---|
| **Doc A** | `SYSTEM-SNAPSHOT.md` (line 62) and `COMMERCIALISATION-PLAN.md` Build Phase Carry-Forward (line 92) |
| **Claim in A** | SYSTEM-SNAPSHOT.md: "75/75 wired to live API". COMMERCIALISATION-PLAN.md: "DUMMY_MODE: false in crm-api.js — all pages call live API with graceful dummy fallback" |
| **Doc B** | `AUTHORITY_RECONSTRUCTION_REPORT.md` §12 (line 324) and `WORKSPACE_BASELINE_AUDIT.md` (line 116) |
| **Claim in B** | AUTHORITY_RECONSTRUCTION_REPORT.md: "Frontend↔API integration: ~7% wired — 5 pages confirmed wired; 70 still DUMMY_MODE". WORKSPACE_BASELINE_AUDIT.md: "crm-api.js: DUMMY_MODE: true in all pages currently" |
| **Severity** | **Critical** — if DUMMY_MODE is still true in code, then commercial launch would ship with dummy data visible. The U0/U1 reports are based on code scan of 2026-06-20 and represent ground truth |
| **Resolution** | **Flagged for human review** — requires human to: (1) inspect crm-api.js current DUMMY_MODE value; (2) confirm whether the 5 inline stub route pages (G-04, G-05, H-07, J-03, A-08) are truly "wired" or just hitting in-memory stubs; (3) update SYSTEM-SNAPSHOT.md Frontend row accordingly |

---

### C-004 — Document total count: DOC-CATALOGUE.md vs U2

| Field | Value |
|---|---|
| **Doc A** | `DOC-CATALOGUE.md` header (line 4) |
| **Claim in A** | "105 active + 0 planned + 3 archived" — count last verified 2026-05-28 |
| **Doc B** | `DOC_CATALOGUE.md` (U2 output, 2026-06-20) |
| **Claim in B** | 130 total project .md files |
| **Severity** | **Moderate** — DOC-CATALOGUE.md has been marked SUPERSEDED (U3 fix applied); this conflict is now a historical artefact in a deprecated doc |
| **Resolution** | **Acknowledged** — DOC-CATALOGUE.md now carries the U3 SUPERSEDED banner. The count discrepancy (25 files) is explained by the 11 U0/U1 output files added in this documentation cycle plus earlier additions not captured. No further action needed on count |

---

### C-005 — Documentation area score: SYSTEM-SNAPSHOT.md claims "78 active docs"

| Field | Value |
|---|---|
| **Doc A** | `SYSTEM-SNAPSHOT.md` Scores by Area table (line 55) and Documentation section (line 68) |
| **Claim in A** | "78 active docs in 9 subdirs" |
| **Doc B** | `DOC_CATALOGUE.md` (U2 output, 2026-06-20) |
| **Claim in B** | 130 total project .md files (22 Authority + 63 Reference + 36 Report + 5 Historical + 3 Archive) |
| **Severity** | **Moderate** — causes confusion when comparing documentation health over time; SYSTEM-SNAPSHOT.md's "78 active docs" reflects the state at 2026-05-31 (the 55 backend/docs files + 15 b9-p specs + some root docs), not the full count including root level session docs, U0/U1/U2 outputs, and tests |
| **Resolution** | **Flagged for human review** — SYSTEM-SNAPSHOT.md requires a full refresh (tied to C-001 resolution); count update should be done together |

---

### C-006 — DOC-READ-LOG.md total: claims 109; U2 counts 130

| Field | Value |
|---|---|
| **Doc A** | `DOC-READ-LOG.md` header (line 5) |
| **Claim in A** | "Running total: 105 ✓ / 4 W / 0 ⬜ / 109 total" (last updated 2026-05-31) |
| **Doc B** | `DOC_CATALOGUE.md` (U2 output, 2026-06-20) |
| **Claim in B** | 130 total project .md files |
| **Severity** | **Moderate** — DOC-READ-LOG.md is used as a continuity log to prove every doc was read; missing 21 entries means 21 docs (U0/U1/U2 outputs) have no confirmed-read status |
| **Resolution** | **Flagged for human review** — DOC-READ-LOG.md needs 21 new [W] entries added for: WORKSPACE_BASELINE_AUDIT.md, REPOSITORY_REALITY_REPORT.md, REPOSITORY_TREE_INVENTORY.md, CURRENT_PROJECT_STATUS.md, AUTHORITY_RECONSTRUCTION_REPORT.md, FEATURE_INVENTORY.md, MODULE_INVENTORY.md, ENTITY_INVENTORY.md, WORKFLOW_INVENTORY.md, ROLE_PERMISSION_INVENTORY.md, API_INVENTORY.md, DOC_CATALOGUE.md, DOCUMENT_CLASSIFICATION_MATRIX.md, DOCUMENT_OWNERSHIP_MATRIX.md, and the 4 U3 outputs from this session. Running total update: 109 → 134+ |

---

### C-007 — README.md claims "90+" project documents

| Field | Value |
|---|---|
| **Doc A** | `README.md` doc index table (line 131) |
| **Claim in A** | "Index of all 90+ project documents" (linking to DOC-CATALOGUE.md) |
| **Doc B** | `DOC_CATALOGUE.md` (U2 output, 2026-06-20) |
| **Claim in B** | 130 total project .md files |
| **Severity** | **Minor** — README is a GitHub landing page; the exact count is secondary to the link destination |
| **Resolution** | **Flagged for human review** — update README.md line 131 to link to `DOC_CATALOGUE.md` and update count from "90+" to "130" when next editing README |
