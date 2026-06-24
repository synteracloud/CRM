> **HISTORICAL** — U3 normalization report as of 2026-06-20. See [DOCUMENT_NORMALIZATION_REPORT.md](../../08_reports/DOCUMENT_NORMALIZATION_REPORT.md) for current normalization state.
> Content preserved for historical reference. Do not update this document.
> Retired: 2026-06-21 (Documentation Normalization Phase)

# DOC_NORMALIZATION_REPORT.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U3 — Documentation Normalization)
**Scope:** All 130 project-owned .md files catalogued in DOC_CATALOGUE.md
**Input documents:** DOC_CATALOGUE.md, DOCUMENT_CLASSIFICATION_MATRIX.md, DOCUMENT_OWNERSHIP_MATRIX.md, REPOSITORY_REALITY_REPORT.md, AUTHORITY_RECONSTRUCTION_REPORT.md

---

## 1. Summary

| Metric | Count |
|---|---|
| Total docs reviewed | 130 |
| Conflicts found | 7 |
| Duplications found | 2 |
| Stale references found | 12 |
| Superseded/archive flags found | 6 |
| Orphaned/abandoned docs found | 5 |
| **Total issues** | **32** |
| Fixes applied | 2 |
| Issues flagged for human review | 30 |

---

## 2. Issues Found by Type

| Type | Count | Severity distribution |
|---|---|---|
| Conflict | 7 | 3 Critical · 3 Moderate · 1 Minor |
| Duplication | 2 | 1 Actionable · 1 Acknowledged (different audiences) |
| Stale reference | 12 | 4 Count-stale · 5 Link-stale · 3 Status-stale |
| Superseded (needs banner) | 2 | 2 applied |
| Superseded (already marked) | 4 | 3 in _archive/ already correct · 1 CLOSED banner already present |
| Orphaned/abandoned | 5 | 5 flagged for human review |

---

## 3. Fixes Applied

| # | File | Fix | Evidence |
|---|---|---|---|
| 1 | `DOC-CATALOGUE.md` | Added SUPERSEDED banner at top: `> **SUPERSEDED** — see DOC_CATALOGUE.md (U3 normalization, 2026-06-20)` | DOC_CATALOGUE.md is the U2-generated authoritative replacement; DOCUMENT_OWNERSHIP_MATRIX.md explicitly recommends deprecation |
| 2 | `REBUILD-PLAN.md` | Added SUPERSEDED banner at top: `> **SUPERSEDED** — see COMMERCIALISATION-PLAN.md (U3 normalization, 2026-06-20)` | REBUILD-PLAN.md already has a CLOSED block; U3 banner adds the standard cross-reference format for consistency |

---

## 4. Issues Flagged but Not Fixed (require human judgment)

### 4.1 Critical Conflicts (3)

**C-001 — Phase completion status mismatch**
- `SYSTEM-SNAPSHOT.md` (last updated 2026-05-31) shows C3 as current phase; C4/C5/C6 as pending.
- `COMMERCIALISATION-PLAN.md` Status header says "C6 ← CURRENT (C5 complete 2026-06-02)".
- Neither document can be corrected without a human confirming the actual current C-phase.
- See DOC_CONFLICT_REGISTER.md C-001.

**C-002 — RESUME POINT table internal inconsistency in COMMERCIALISATION-PLAN.md**
- Status header says "C5 complete 2026-06-02 — all production gates pass; C6 ← CURRENT".
- RESUME POINT table in the same file shows C5 and C6 both as "⬜ pending".
- The RESUME POINT table was not updated when the Status header was updated.
- Cannot fix without human confirmation that C5 is genuinely complete.
- See DOC_CONFLICT_REGISTER.md C-002.

**C-003 — Frontend API wiring claim vs code evidence**
- `SYSTEM-SNAPSHOT.md` claims "75/75 wired to live API"; `COMMERCIALISATION-PLAN.md` carry-forward says "DUMMY_MODE: false".
- `AUTHORITY_RECONSTRUCTION_REPORT.md` (U1, code evidence 2026-06-20) reports "~7% wired: 5 pages confirmed wired; 70 still DUMMY_MODE".
- `WORKSPACE_BASELINE_AUDIT.md` (U0, code evidence 2026-06-20) reports "crm-api.js: DUMMY_MODE: true in all pages currently".
- This is a factual gap between what docs claim happened and what code shows on 2026-06-20.
- Cannot fix: requires human verification of crm-api.js current state and whether wiring was reverted or partially rolled back.
- See DOC_CONFLICT_REGISTER.md C-003.

### 4.2 Moderate Conflicts (3)

**C-004 — Document count: DOC-CATALOGUE.md claims 105; U2 counts 130**
Needs human decision on whether to retire DOC-CATALOGUE.md entirely or keep for historical record.

**C-005 — SYSTEM-SNAPSHOT.md claims "78 active docs"; U2 counts 130**
SYSTEM-SNAPSHOT.md is stale (last updated 2026-05-31). Cannot update the snapshot count without verifying all other snapshot data is also current.

**C-006 — DOC-READ-LOG.md claims 109 total docs; U2 counts 130**
DOC-READ-LOG.md was last updated 2026-05-31. 21 new docs were added since (U0/U1/U2 outputs). Count needs updating; the "W" (to-read) entries also need adding for the 21 new docs. This requires a human to schedule a read-through.

### 4.3 Minor Conflict (1)

**C-007 — README.md claims "90+ project documents"; U2 counts 130**
Minor because README is a GitHub landing page; the exact count is secondary to the links.

### 4.4 Stale References (12)

See DOC_STALE_REFERENCE_REPORT.md for full details. Key flagged items requiring human action:
- 5 occurrences of `DOC-CATALOGUE.md` being cited as the authoritative index (should be `DOC_CATALOGUE.md`) across SYSTEM-SNAPSHOT.md, COMMERCIALISATION-PLAN.md, README.md, and PROGRESS.md.
- `CURRENT_PROJECT_STATUS.md` says "Commercialization phase work not started" — stale per COMMERCIALISATION-PLAN.md state.
- `DOC-CATALOGUE.md` "How to use" section points to `REBUILD-PLAN.md` for roadmap — stale (superseded doc).

### 4.5 Orphaned/Abandoned Documents (5)

See DOC_DUPLICATION_REGISTER.md §Orphaned for details. Documents that are not actively cross-referenced from any governing or frequently-read doc:
- `backend/docs/domain/enterprise-depth.md`
- `backend/docs/domain/data-governance-ownership.md`
- `backend/docs/_b9/b9-p08-mobile-responsiveness-system.md`
- `CATALOGUE-MERGE-PLAN.md`
- `backend/product-spec-gap-register.md`

---

## 5. Recommendations for Human Review

| Priority | Document | Action Needed |
|---|---|---|
| Immediate | `COMMERCIALISATION-PLAN.md` | Update RESUME POINT table to match Status header (C5/C6 status); confirm which phase is actually current |
| Immediate | `SYSTEM-SNAPSHOT.md` | Full refresh: update C-phase status, doc count (78→130), wiring status per code evidence |
| High | `AUTHORITY_RECONSTRUCTION_REPORT.md` §12 vs build docs | Verify actual crm-api.js DUMMY_MODE state; reconcile "75/75 wired" claim with U0/U1 code evidence |
| High | `DOC-READ-LOG.md` | Add 21 new U0/U1/U2 docs (and 4 U3 docs after today) as [W] entries; update running total |
| High | `README.md` | Update doc count ("90+") and link target (DOC-CATALOGUE.md → DOC_CATALOGUE.md) |
| Medium | `CATALOGUE-MERGE-PLAN.md` | Move to `_archive/` — work is complete; no ongoing value |
| Medium | `backend/docs/domain/enterprise-depth.md` | Confirm it is actively used; add cross-reference from DESIGN-SPEC.md or a domain spec |
| Medium | `backend/docs/domain/data-governance-ownership.md` | Clarify relationship with `data-governance-layer.md`; add cross-reference or merge note |
| Medium | `backend/docs/_b9/b9-p08-mobile-responsiveness-system.md` | Confirm referenced from FRAMEWORK.md or a b9-p spec; add cross-reference |
| Low | `backend/product-spec-gap-register.md` | Confirm whether gaps are still open; update or archive |
| Low | `PROGRESS.md` line 8 | Update "Rebuild plan: REBUILD-PLAN.md" reference to COMMERCIALISATION-PLAN.md |

---

## 6. Documentation Health Score

**Overall: Fair**

The core technical specification documents (backend/docs/ subtree: architecture, domain, infrastructure, security, adapters, ADRs) are in **Good** health — 57 Developer-owned documents with no critical conflicts and accurate cross-references.

The session/status layer is in **Poor** health — 4 active session docs (SYSTEM-SNAPSHOT.md, PROGRESS.md, COMMERCIALISATION-PLAN.md, DOC-READ-LOG.md) contain stale or conflicting information about the current commercialization phase and frontend wiring status, with counts differing by 21–52 documents from U2 ground truth.

The catalogue layer has been addressed by U2 (DOC_CATALOGUE.md is authoritative); the old DOC-CATALOGUE.md has been marked superseded by this normalization pass.

**Upgrade path to Good:** Refresh SYSTEM-SNAPSHOT.md and COMMERCIALISATION-PLAN.md RESUME POINT table with verified current state. Update DOC-READ-LOG.md with 21 new entries. Retire CATALOGUE-MERGE-PLAN.md to _archive/. Result: 3 critical conflicts resolved, health score upgrades to Good.
