# DOCUMENTATION PLACEMENT AUDIT
**Generated:** 2026-06-22
**Scope:** All .md files in D:\SaaS\CRM (excluding .venv/, node_modules/, .pip-cache/, .npm-cache/, .playwright-browsers/)

---

## SUMMARY

| Status | Count |
|--------|-------|
| Correct | 116 |
| Misplaced | 17 |
| Legacy/Archive (correct) | 7 |
| Build artifact (README in cache dir) | 3 |

Total .md files audited: ~143

---

## ROOT LEVEL .md FILES

| File | Current Location | Correct Location | Status | Action |
|------|-----------------|-----------------|--------|--------|
| `CLAUDE.md` | Root | Root | CORRECT | Keep |
| `DESIGN-SPEC.md` | Root | Root | CORRECT | Keep |
| `FRAMEWORK.md` | Root | Root | CORRECT | Keep |
| `PAGE-BUILD-PROTOCOL.md` | Root | Root | CORRECT | Keep |
| `PRODUCT-SPEC.md` | Root | Root | CORRECT | Keep |
| `README.md` | Root | Root | CORRECT | Keep |
| `CONTRIBUTING.md` | Root | Root | CORRECT | Keep |
| `COMMERCIALISATION-PLAN.md` | Root | `docs/00_authority/` | MISPLACED | Move to docs/00_authority/ |
| `AUDIT REMEDIATION.md` | Root (untracked) | `Prompts/Main/` | MISPLACED | Root copy is duplicate of Prompts/Main/; gitignore root copy |
| `DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md` | Root (untracked) | `Prompts/Main/` | MISPLACED | Same — gitignore root copy |
| `GOVERNANCE IMPLEMENTATION PHASE 1.md` | Root (untracked) | `Prompts/Main/` | MISPLACED | Same — gitignore root copy |
| `PHASE 1 GOVERNANCE VALIDATION.md` | Root (untracked) | `Prompts/Main/` | MISPLACED | Same — gitignore root copy |
| `PROMPT SEQUENCE.md` | Root (untracked) | `Prompts/Main/` | MISPLACED | Same — gitignore root copy |
| `FULL REPOSITORY NORMALIZATION AND REALITY AUDIT.md` | Root (untracked) | `Prompts/Main/` | MISPLACED | Gitignore root copy |

---

## docs/ FOLDER .md FILES

| File | Current Location | Correct Location | Status | Action |
|------|-----------------|-----------------|--------|--------|
| `docs/00_authority/PROJECT_CHARTER.md` | docs/00_authority/ | docs/00_authority/ | CORRECT | Keep |
| `docs/00_authority/PRODUCT_WORKFLOWS.md` | docs/00_authority/ | docs/00_authority/ | CORRECT | Keep |
| `docs/00_authority/FULLSTACK_STITCHING_CONTRACT.md` | docs/00_authority/ | docs/00_authority/ | CORRECT | Keep |
| `docs/00_authority/DOMAIN_MODEL.md` | docs/00_authority/ | docs/00_authority/ | CORRECT | Keep |
| `docs/00_authority/FEATURE_SCOPE.md` | docs/00_authority/ | docs/00_authority/ | CORRECT | Keep |
| `docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md` | docs/06_decisions/ | docs/06_decisions/ | CORRECT | Keep |
| `docs/07_governance/DECISION_ESCALATION_MATRIX.md` | docs/07_governance/ | docs/07_governance/ | CORRECT | Keep |
| `docs/07_governance/AI_OPERATING_CONTEXT.md` | docs/07_governance/ | docs/07_governance/ | CORRECT | Keep |
| `docs/08_reports/DOCUMENTATION_COVERAGE_MATRIX.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/ARCHITECTURAL_GAP_REGISTER.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/RECOMMENDED_ADR_ROADMAP.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/GOVERNANCE_IMPLEMENTATION_REPORT.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/GOVERNANCE_CONSISTENCY_AUDIT.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/REMEDIATION_REPORT.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/DOCUMENT_INVENTORY.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/DOCUMENT_CLASSIFICATION_MATRIX.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/DOCUMENT_NORMALIZATION_REPORT.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/DUPLICATION_ANALYSIS_REPORT.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/CONFLICT_ANALYSIS_REPORT.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/DOCUMENT_RETIREMENT_PLAN.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/REMEDIATION_REPORT_2.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/08_reports/AUTHORITY_MAPPING_MATRIX.md` | docs/08_reports/ | docs/08_reports/ | CORRECT | Keep |
| `docs/reference/RENDER-DEPLOY.md` | docs/reference/ | docs/reference/ or docs/05_deployment/ | CORRECT (acceptable) | Keep; optionally move to docs/05_deployment/ |
| `docs/archive/CATALOGUE-MERGE-PLAN.md` | docs/archive/ | docs/archive/ | CORRECT | Keep |
| `docs/archive/REBUILD-PLAN.md` | docs/archive/ | docs/archive/ | CORRECT | Keep |
| `docs/archive/deployment-pipelines.md` | docs/archive/ | docs/archive/ | CORRECT | Keep |
| `docs/archive/gap-register.md` | docs/archive/ | docs/archive/ | CORRECT | Keep |
| `docs/archive/FRAMEWORK-GAPS.md` | docs/archive/ | docs/archive/ | CORRECT | Keep |
| `docs/archive/CATALOGUE-MERGE-PLAN.md` | docs/archive/ | docs/archive/ | CORRECT | Keep |
| `docs/archive/MAPPING-TRACKER.md` | docs/archive/ | docs/archive/ | CORRECT | Keep |
| `docs/archive/DOC-CATALOGUE.md` | docs/archive/ | docs/archive/ | CORRECT | Keep |
| `docs/reports/session/CHANGELOG.md` | docs/reports/session/ | docs/reports/session/ | CORRECT | Keep |
| `docs/reports/session/PROGRESS.md` | docs/reports/session/ | docs/reports/session/ | CORRECT | Keep |
| `docs/reports/session/PENDING.md` | docs/reports/session/ | docs/reports/session/ | CORRECT | Keep |
| `docs/reports/session/SCREEN-ARTEFACTS.md` | docs/reports/session/ | docs/reports/session/ | CORRECT | Keep |
| `docs/reports/session/DOC-READ-LOG.md` | docs/reports/session/ | docs/reports/session/ | CORRECT | Keep |
| `docs/reports/session/SYSTEM-SNAPSHOT.md` | docs/reports/session/ | docs/reports/session/ | CORRECT | Keep |
| `docs/reports/session/SESSION-HANDOFF.md` | docs/reports/session/ | docs/reports/session/ | CORRECT | Keep |
| `docs/reports/u-series/*.md` (~60 files) | docs/reports/u-series/ | docs/reports/u-series/ | CORRECT | Keep all |

---

## BACKEND .md FILES

| File | Current Location | Correct Location | Status | Action |
|------|-----------------|-----------------|--------|--------|
| `backend/README.md` | backend/ | backend/ | CORRECT | Keep (standard project README) |
| `backend/BACKEND-QC.md` | backend/ | `backend/docs/` | MISPLACED | Move to backend/docs/ |
| `backend/CONSTRAINTS.md` | backend/ | `backend/docs/` | MISPLACED | Move to backend/docs/ |
| `backend/FRONTEND-BACKEND-MAPPING.md` | backend/ | `docs/03_fullstack_contracts/` | MISPLACED | Move to docs/03_fullstack_contracts/ |
| `backend/PENDING.md` | backend/ | `docs/reports/session/` | MISPLACED | Move (merge with existing PENDING.md or rename) |
| `backend/market-research-gap-register.md` | backend/ | `docs/08_reports/` | MISPLACED | Move to docs/08_reports/ |
| `backend/product-spec-gap-register.md` | backend/ | `docs/08_reports/` | MISPLACED | Move to docs/08_reports/ |
| `backend/gateway/README.md` | backend/gateway/ | backend/gateway/ | CORRECT | Keep (component README) |
| `backend/gateway/self-qc.md` | backend/gateway/ | backend/gateway/ or backend/docs/ | ACCEPTABLE | Keep co-located |
| `backend/db/activity_task_db/README.md` | backend/db/activity_task_db/ | backend/db/activity_task_db/ | CORRECT | Keep (component README) |
| `backend/db/activity_task_db/self-qc.md` | backend/db/activity_task_db/ | backend/db/ or backend/docs/ | ACCEPTABLE | Keep co-located |
| `backend/db/transaction_db/README.md` | backend/db/transaction_db/ | backend/db/transaction_db/ | CORRECT | Keep |
| `backend/db/transaction_db/self-qc.md` | backend/db/transaction_db/ | backend/db/transaction_db/ | ACCEPTABLE | Keep |
| `backend/db/transaction_db/transaction-policies.md` | backend/db/transaction_db/ | backend/db/transaction_db/ | CORRECT | Keep |
| `backend/docs/_b9/*.md` (14 files) | backend/docs/_b9/ | backend/docs/_b9/ | CORRECT | Keep (b9-p page specs) |
| `backend/docs/_qc/*.md` (3 files) | backend/docs/_qc/ | backend/docs/_qc/ | CORRECT | Keep |
| `backend/docs/adapters/*.md` (5 files) | backend/docs/adapters/ | backend/docs/adapters/ | CORRECT | Keep |
| `backend/docs/adr/*.md` (3 files) | backend/docs/adr/ | backend/docs/adr/ | CORRECT | Keep |
| `backend/docs/architecture/*.md` (5 files) | backend/docs/architecture/ | backend/docs/architecture/ | CORRECT | Keep |
| `backend/docs/domain/*.md` (21 files) | backend/docs/domain/ | backend/docs/domain/ | CORRECT | Keep |
| `backend/docs/infrastructure/*.md` (13 files) | backend/docs/infrastructure/ | backend/docs/infrastructure/ | CORRECT | Keep |
| `backend/docs/product/*.md` (4 files) | backend/docs/product/ | backend/docs/product/ | CORRECT | Keep |
| `backend/docs/security/*.md` (3 files) | backend/docs/security/ | backend/docs/security/ | CORRECT | Keep |
| `backend/docs/ui/*.md` (3 files) | backend/docs/ui/ | backend/docs/ui/ | CORRECT | Keep |
| `backend/docs/phase4-gap-register.md` | backend/docs/ | `docs/08_reports/` | MISPLACED | Move to docs/08_reports/ |

---

## TESTS .md FILES

| File | Current Location | Correct Location | Status | Action |
|------|-----------------|-----------------|--------|--------|
| `tests/e2e/playwright/SKIP-BACKLOG.md` | tests/e2e/playwright/ | `docs/04_testing/` | MISPLACED | Move to docs/04_testing/ |

---

## PROMPTS .md FILES

| File | Current Location | Correct Location | Status | Action |
|------|-----------------|-----------------|--------|--------|
| `Prompts/U1 — AUTHORITY RECONSTRUCTION.md` | Prompts/ | Prompts/ | CORRECT (in library) | Keep |
| `Prompts/U2 — DOCUMENTATION CATALOGUE.md` | Prompts/ | Prompts/ | CORRECT | Keep |
| `Prompts/U3 — DOCUMENTATION NORMALIZATION.md` | Prompts/ | Prompts/ | CORRECT | Keep |
| `Prompts/U4 — WORKSPACE RESTRUCTURING PLAN.md` | Prompts/ | Prompts/ | CORRECT | Keep |
| `Prompts/U0–U9 LEGACY MODERNIZATION AUDIT.md` | Prompts/ | Prompts/ | CORRECT | Keep |
| `Prompts/U5 — WORKSPACE RESTRUCTURING EXECUTION.md` | Prompts/ | Prompts/ | CORRECT | Keep |
| `Prompts/U6 — DOC TO CODE DELTA ANALYSIS.md` | Prompts/ | Prompts/ | CORRECT | Keep |
| `Prompts/U7 — DELTA REMEDIATION.md` | Prompts/ | Prompts/ | CORRECT | Keep |
| `Prompts/U8 — WORKSPACE SEALING.md` | Prompts/ | Prompts/ | CORRECT | Keep |
| `Prompts/U9 — TEST SUITE PLANNING.md` | Prompts/ | Prompts/ | CORRECT | Keep |
| `Prompts/U10 — U0–U9 AUDIT REMEDIATION.md` | Prompts/ | Prompts/ | CORRECT | Keep |
| `Prompts/Main/AUDIT REMEDIATION.md` | Prompts/Main/ | Prompts/Main/ | CORRECT | Keep |
| `Prompts/Main/DOCUMENTATION NORMALIZATION…md` | Prompts/Main/ | Prompts/Main/ | CORRECT | Keep |
| `Prompts/Main/FULL REPOSITORY NORMALIZATION…md` | Prompts/Main/ | Prompts/Main/ | CORRECT | Keep |
| `Prompts/Main/GOVERNANCE IMPLEMENTATION PHASE 1.md` | Prompts/Main/ | Prompts/Main/ | CORRECT | Keep |
| `Prompts/Main/PHASE 1 GOVERNANCE VALIDATION.md` | Prompts/Main/ | Prompts/Main/ | CORRECT | Keep |
| `Prompts/Main/PROMPT SEQUENCE.md` | Prompts/Main/ | Prompts/Main/ | CORRECT | Keep |

---

## BUILD ARTIFACT README FILES (NOT PROJECT DOCS)

These are auto-generated README files inside cache directories — they are not project documentation:

| File | Location | Classification | Action |
|------|----------|---------------|--------|
| `.pytest_cache/README.md` | root .pytest_cache/ | Build artifact | Gitignored with .pytest_cache/ |
| `backend/.pytest_cache/README.md` | backend .pytest_cache/ | Build artifact | Gitignored with .pytest_cache/ |
| `tests/e2e/playwright/.pytest_cache/README.md` | tests .pytest_cache/ | Build artifact | Gitignored with .pytest_cache/ |
| `bin/pgsql/doc/README-pldebugger.md` | bin/pgsql/ | Vendor doc | Will be removed when bin/ is gitignored |
| `_archive/README.md` | _archive/ | Redundant | Merge into docs/archive/ if unique |

---

## SOURCE CODE FILES IN DOCUMENTATION FOLDERS

**No source code files (.py, .js, .html, .css) were found in any docs/ subfolder.** The documentation tree is clean of code contamination.

---

## CROSS-REFERENCE: DUPLICATES BETWEEN docs/ AND docs/reports/u-series/

The following pairs may represent near-duplicates between the governance docs and the u-series reports:

| docs/08_reports/ file | docs/reports/u-series/ equivalent | Risk |
|-----------------------|----------------------------------|------|
| DOCUMENT_CLASSIFICATION_MATRIX.md | DOCUMENT_CLASSIFICATION_MATRIX.md | DUPLICATE FILENAME — verify content differs |
| DOCUMENT_NORMALIZATION_REPORT.md | DOC_NORMALIZATION_REPORT.md | Near-duplicate — different naming convention |

**Recommendation:** Verify these are not identical files split across two locations. If the u-series versions are historical (snapshots from U-series audit runs) and the docs/08_reports/ versions are the current live documents, this is acceptable. If they are byte-for-byte identical, consolidate.
