# LEGACY AND ARCHIVE PLAN
**Generated:** 2026-06-22
**Scope:** All files/folders identified as Legacy, Archive, or candidates for disposition

---

## LEGEND

- **Keep in archive:** Content is historically valuable; preserve in docs/archive/
- **Keep as reference:** Not active but needed for template reference; do not delete
- **Delete (REQUIRES_OWNER_APPROVAL):** Safe to remove but needs explicit sign-off
- **Move to docs/archive/:** Safe doc-only move
- **Already archived:** Correctly in docs/archive/

---

## SECTION 1 — docs/archive/ CONTENTS (CORRECTLY ARCHIVED)

These files are already correctly placed in docs/archive/:

| Path | Classification | Content Summary | Disposition |
|------|---------------|-----------------|-------------|
| `docs/archive/CATALOGUE-MERGE-PLAN.md` | Archive | Plan for merging documentation catalogues (superseded) | Keep in archive |
| `docs/archive/REBUILD-PLAN.md` | Archive | Earlier rebuild planning doc (superseded by current design spec) | Keep in archive |
| `docs/archive/deployment-pipelines.md` | Archive | Old deployment pipeline documentation | Keep in archive |
| `docs/archive/gap-register.md` | Archive | Early gap register (superseded by more specific registers) | Keep in archive |
| `docs/archive/FRAMEWORK-GAPS.md` | Archive | Framework gap analysis (gaps now closed) | Keep in archive |
| `docs/archive/MAPPING-TRACKER.md` | Archive | Earlier mapping tracker | Keep in archive |
| `docs/archive/DOC-CATALOGUE.md` | Archive | Documentation catalogue snapshot | Keep in archive |

**Status: All 7 files correctly placed. No action required.**

---

## SECTION 2 — _archive/ DIRECTORY (ROOT — REDUNDANT)

| Path | Classification | Content Summary | Disposition | Risk |
|------|---------------|-----------------|-------------|------|
| `_archive/README.md` | Archive — Redundant location | README explaining the archive directory | Check if unique content; if not, delete; else merge to docs/archive/ | None |

**Action:** Read `_archive/README.md`, compare content with docs/archive/ contents. If it contains only a "this directory is the archive" note, the file is redundant. Move to docs/archive/ if content is unique; otherwise the empty directory disappears naturally.

---

## SECTION 3 — FRONTEND LIBRARY PAGES (LEGACY)

The following frontend/src/ subdirectories contain NexLink library template pages that predate the custom build phase:

| Path | Classification | Content Summary | Disposition | Risk |
|------|---------------|-----------------|-------------|------|
| `frontend/src/ai/` | Legacy — Library | AI demo pages from NexLink template | Keep as reference (do not edit or delete) | Medium — deleting would remove design reference |
| `frontend/src/chart/` | Legacy — Library | Chart demonstration pages | Keep as reference | Medium |
| `frontend/src/components/` | Legacy — Library | UI component demonstrations | Keep as reference | Medium |
| `frontend/src/email/` | Legacy — Library | Email template pages | Keep as reference | Medium |
| `frontend/src/extended-ui/` | Legacy — Library | Extended UI demos | Keep as reference | Medium |
| `frontend/src/forms/` | Legacy — Library | Form layout demos | Keep as reference | Medium |
| `frontend/src/icons/` | Legacy — Library | Icon library pages | Keep as reference | Medium |
| `frontend/src/maps/` | Legacy — Library | Map integration demos | Keep as reference | Medium |
| `frontend/src/pages/` | Legacy — Library | General template pages | Keep as reference | Medium |
| `frontend/src/table/` | Legacy — Library | Table demos | Keep as reference | Medium |

**Disposition:** Keep all library pages. They serve as design reference for the custom build phase. CLAUDE.md explicitly says "96 NexLink pages" from the "Library phase complete." Do NOT delete, rename, or modify these pages.

---

## SECTION 4 — U-SERIES PROMPT OUTPUTS IN docs/reports/u-series/

These are historical outputs from U0–U10 audit sessions. They are already correctly placed:

| Path | Classification | Content Summary | Disposition |
|------|---------------|-----------------|-------------|
| `docs/reports/u-series/U0 — REPOSITORY REALITY DISCOVERY.md` | Archive — Session output | First repo reality scan | Keep in u-series |
| `docs/reports/u-series/U1 — AUTHORITY RECONSTRUCTION.md` | Archive — Session output | Authority doc reconstruction | Keep in u-series |
| `docs/reports/u-series/U2 — DOCUMENTATION CATALOGUE.md` | Archive — Session output | Full doc catalogue | Keep in u-series |
| `docs/reports/u-series/U3 — DOCUMENTATION NORMALIZATION.md` | Archive — Session output | Doc normalization plan | Keep in u-series |
| `docs/reports/u-series/U4 — WORKSPACE RESTRUCTURING PLAN.md` | Archive — Session output | Restructuring plan | Keep in u-series |
| `docs/reports/u-series/U0_U9_FORENSIC_AUDIT_REPORT.md` | Archive — Session output | Cross-session forensic audit | Keep in u-series |
| `docs/reports/u-series/U10_FINAL_STATUS.md` | Archive — Session output | U10 completion status | Keep in u-series |
| All other u-series files (~55 files) | Archive — Session output | Various U-series report outputs | Keep in u-series |

**Status: All correctly placed. No action required.**

---

## SECTION 5 — BACKEND DOCS (POTENTIALLY LEGACY)

These backend documentation files warrant review for currency:

| Path | Classification | Content Summary | Disposition | Risk |
|------|---------------|-----------------|-------------|------|
| `backend/PENDING.md` | Session doc | Backend pending tasks | Move to docs/reports/session/ | Low |
| `backend/market-research-gap-register.md` | Generated report | Market research gaps | Move to docs/08_reports/ | Low |
| `backend/product-spec-gap-register.md` | Generated report | Product spec gaps | Move to docs/08_reports/ | Low |
| `backend/docs/phase4-gap-register.md` | Generated report | Phase 4 gaps | Move to docs/08_reports/ | Low |
| `backend/BACKEND-QC.md` | QC report | Backend quality control notes | Move to backend/docs/ | Low |
| `backend/CONSTRAINTS.md` | Authority doc | Backend constraints | Move to backend/docs/ | Low |
| `backend/FRONTEND-BACKEND-MAPPING.md` | Contract doc | Frontend-backend API mapping | Move to docs/03_fullstack_contracts/ | Low |

---

## SECTION 6 — GENERATED SCAN REPORTS (MAY BE INTENTIONAL EVIDENCE)

| Path | Classification | Content Summary | Disposition | Risk |
|------|---------------|-----------------|-------------|------|
| `tests/security/pip-audit.json` | Generated artifact | pip dependency audit results | Move to docs/reports/security/ if keeping; else gitignore | None |
| `tests/security/semgrep-report.json` | Generated artifact | Semgrep security scan results | Same | None |
| `tests/security/semgrep-report-c3.json` | Generated artifact | Semgrep scan (cycle 3) | Same | None |
| `tests/security/semgrep-c3-final.json` | Generated artifact | Semgrep final cycle 3 | Same | None |
| `tests/security/c5-api-security-report.json` | Generated artifact | API security scan (cycle 5) | Same | None |

**Owner decision needed:** These JSON reports may be required as compliance evidence. If they need to be committed, create `docs/reports/security/` and move them there. If they are regenerated on each CI run, gitignore them.

---

## SECTION 7 — LOAD TEST REPORTS

| Path | Classification | Content Summary | Disposition | Risk |
|------|---------------|-----------------|-------------|------|
| `tests/load/reports/report-20260531-2058.html` | Generated artifact | Locust HTML report | Move to docs/reports/load/ if keeping | None |
| `tests/load/reports/report-20260601-*.html` (4 files) | Generated artifact | Locust HTML reports | Same | None |
| `tests/load/reports/c5-prod-*.html` (2 files) | Generated artifact | Locust production load reports | Same — higher value as prod evidence | None |

---

## SECTION 8 — c-seal BASELINE FILES

| Path | Classification | Content Summary | Disposition | Risk |
|------|---------------|-----------------|-------------|------|
| `c-seal/baseline.txt` | Generated artifact | Workspace seal baseline hash | Keep in c-seal/ (already .gitignored) | None |
| `c-seal/after-playwright.txt` | Generated artifact | Post-Playwright seal hash | Keep in c-seal/ (already .gitignored) | None |

**Status: Correctly handled — already .gitignored.**

---

## SECTION 9 — DISPOSITION SUMMARY

| Disposition | Count | Items |
|-------------|-------|-------|
| Already correctly archived | 7 | docs/archive/ files |
| Keep as reference (library pages) | 10 dirs | frontend/src library subdirs |
| Move to docs/08_reports/ | 3 | backend gap registers |
| Move to backend/docs/ | 2 | BACKEND-QC.md, CONSTRAINTS.md |
| Move to docs/03_fullstack_contracts/ | 1 | FRONTEND-BACKEND-MAPPING.md |
| Move to docs/reports/session/ | 1 | backend/PENDING.md |
| Owner decision needed | 5 | Security scan JSONs |
| Owner decision needed | 7 | Load test HTML reports |
| REQUIRES_OWNER_APPROVAL | 2 dirs | bin/, data/ |

---

## SAFE ARCHIVE MOVES (READY TO EXECUTE)

The following document moves are safe and can be executed immediately:

1. `backend/BACKEND-QC.md` → `backend/docs/BACKEND-QC.md`
2. `backend/CONSTRAINTS.md` → `backend/docs/CONSTRAINTS.md`
3. `backend/FRONTEND-BACKEND-MAPPING.md` → `docs/03_fullstack_contracts/FRONTEND-BACKEND-MAPPING.md`
4. `backend/market-research-gap-register.md` → `docs/08_reports/MARKET-RESEARCH-GAP-REGISTER.md`
5. `backend/product-spec-gap-register.md` → `docs/08_reports/PRODUCT-SPEC-GAP-REGISTER.md`
6. `backend/docs/phase4-gap-register.md` → `docs/08_reports/PHASE4-GAP-REGISTER.md`
7. `tests/e2e/playwright/SKIP-BACKLOG.md` → `docs/04_testing/SKIP-BACKLOG.md`
8. `COMMERCIALISATION-PLAN.md` (root) → `docs/00_authority/COMMERCIALISATION-PLAN.md`
9. `_archive/README.md` → `docs/archive/ARCHIVE-README.md` (if content is unique)
