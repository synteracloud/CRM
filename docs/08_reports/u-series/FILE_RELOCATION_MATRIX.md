# FILE_RELOCATION_MATRIX.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U4 — Workspace Restructuring Plan)
**Status:** Planning only — NO files have been moved or modified.
**Companion doc:** WORKSPACE_RESTRUCTURING_PLAN.md (rationale), BREAKAGE_RISK_REPORT.md (risk details)

---

## Part A — Files That Move

Files are grouped by migration phase (see WORKSPACE_RESTRUCTURING_PLAN.md §5 for phase details).

---

### Phase 1 — Archive Consolidation (7 files)

Move existing `_archive/` contents plus 4 superseded/completed root docs to new `docs/archive/`.

| # | Current Path | Proposed Path | Reason | Dependencies | Risk |
|---|---|---|---|---|---|
| 1 | `D:\SaaS\CRM\_archive\deployment-pipelines.md` | `D:\SaaS\CRM\docs\archive\deployment-pipelines.md` | Already in archive; consolidate into unified docs/archive/ home | Superseded by `backend/docs/infrastructure/runtime-deployment.md` (noted in DOC_CATALOGUE.md §B). DOC_STALE_REFERENCE_REPORT.md SR-012 confirms the supersession chain is accurate. | Low |
| 2 | `D:\SaaS\CRM\_archive\FRAMEWORK-GAPS.md` | `D:\SaaS\CRM\docs\archive\FRAMEWORK-GAPS.md` | Already in archive; consolidate into unified docs/archive/ home | Superseded by inline FRAMEWORK.md annotations. No active inbound references. | Low |
| 3 | `D:\SaaS\CRM\_archive\gap-register.md` | `D:\SaaS\CRM\docs\archive\gap-register.md` | Already in archive; consolidate into unified docs/archive/ home | Superseded by backend/docs/phase4-gap-register.md and backend/BACKEND-QC.md. No active inbound references. | Low |
| 4 | `D:\SaaS\CRM\DOC-CATALOGUE.md` | `D:\SaaS\CRM\docs\archive\DOC-CATALOGUE.md` | Marked SUPERSEDED (U3 normalization 2026-06-20). Replaced by DOC_CATALOGUE.md. SUPERSEDED banner already applied. | Referenced (stale) from: SYSTEM-SNAPSHOT.md (SR-001, SR-002), COMMERCIALISATION-PLAN.md (SR-003, SR-004), README.md (SR-005). All references are stale and point to this file with the wrong name (should be DOC_CATALOGUE.md). Moving does not worsen the breakage. | Low |
| 5 | `D:\SaaS\CRM\REBUILD-PLAN.md` | `D:\SaaS\CRM\docs\archive\REBUILD-PLAN.md` | Marked SUPERSEDED and CLOSED 2026-05-31. Replaced by COMMERCIALISATION-PLAN.md. SUPERSEDED banner applied (U3 fix). | Referenced (stale) from: PROGRESS.md line 8 (SR-006), DOC-CATALOGUE.md "How to use" (SR-008, already in superseded doc). | Low |
| 6 | `D:\SaaS\CRM\MAPPING-TRACKER.md` | `D:\SaaS\CRM\docs\archive\MAPPING-TRACKER.md` | Status: COMPLETE (2026-05-27). All 22 backend route files inventoried. No ongoing value. Outputs (FRONTEND-BACKEND-MAPPING.md, PAGE-BUILD-PROTOCOL.md) are live. | DOC_CATALOGUE.md §A lists it as Reference/Complete. DOC-READ-LOG.md has it as ✓. No active authority doc references it for current work. | Low |
| 7 | `D:\SaaS\CRM\CATALOGUE-MERGE-PLAN.md` | `D:\SaaS\CRM\docs\archive\CATALOGUE-MERGE-PLAN.md` | Status: COMPLETE (2026-05-22). All 7 merge steps done. Sub-catalogues deleted. No ongoing value. DOC_DUPLICATION_REGISTER.md D-009 recommends archiving. | DOC_CATALOGUE.md §A lists it as Report/Complete. Not referenced from SYSTEM-SNAPSHOT.md, PENDING.md, or any active session doc (flagged as orphaned in DOCUMENT_OWNERSHIP_MATRIX.md). | Low |

---

### Phase 2 — U-Series Output Relocation (31 files)

Move all U-pass prompt docs and output files from root to `docs/reports/u-series/`.

| # | Current Path | Proposed Path | Reason | Dependencies | Risk |
|---|---|---|---|---|---|
| 8 | `D:\SaaS\CRM\U0 — REPOSITORY REALITY DISCOVERY.md` | `D:\SaaS\CRM\docs\reports\u-series\U0 — REPOSITORY REALITY DISCOVERY.md` | Process prompt doc; not a session governance doc. Should live with its outputs. | Not referenced by path from CLAUDE.md, DESIGN-SPEC.md, or FRAMEWORK.md. DOC_CATALOGUE.md §A lists it as Authority / Active — but it is a process directive, not a session rule. | Low |
| 9 | `D:\SaaS\CRM\U1 — AUTHORITY RECONSTRUCTION.md` | `D:\SaaS\CRM\docs\reports\u-series\U1 — AUTHORITY RECONSTRUCTION.md` | Process prompt doc; not a session governance doc. Should live with its outputs. | Same rationale as #8. | Low |
| 10 | `D:\SaaS\CRM\U2 — DOCUMENTATION CATALOGUE.md` | `D:\SaaS\CRM\docs\reports\u-series\U2 — DOCUMENTATION CATALOGUE.md` | Process prompt doc. | Same rationale as #8. | Low |
| 11 | `D:\SaaS\CRM\U3 — DOCUMENTATION NORMALIZATION.md` | `D:\SaaS\CRM\docs\reports\u-series\U3 — DOCUMENTATION NORMALIZATION.md` | Process prompt doc. | Same rationale as #8. | Low |
| 12 | `D:\SaaS\CRM\U4 — WORKSPACE RESTRUCTURING PLAN.md` | `D:\SaaS\CRM\docs\reports\u-series\U4 — WORKSPACE RESTRUCTURING PLAN.md` | Process prompt doc (this pass). | Same rationale as #8. Created at root per task instructions; plan proposes eventual relocation. | Low |
| 13 | `D:\SaaS\CRM\WORKSPACE_BASELINE_AUDIT.md` | `D:\SaaS\CRM\docs\reports\u-series\WORKSPACE_BASELINE_AUDIT.md` | U0 discovery output. Not a session doc; evidence archive. | Referenced by name from AUTHORITY_RECONSTRUCTION_REPORT.md (contextual mention). Not path-referenced from any authority doc. | Low |
| 14 | `D:\SaaS\CRM\REPOSITORY_REALITY_REPORT.md` | `D:\SaaS\CRM\docs\reports\u-series\REPOSITORY_REALITY_REPORT.md` | U0 discovery output. | Not path-referenced from any authority doc. | Low |
| 15 | `D:\SaaS\CRM\REPOSITORY_TREE_INVENTORY.md` | `D:\SaaS\CRM\docs\reports\u-series\REPOSITORY_TREE_INVENTORY.md` | U0 discovery output. | Not path-referenced from any authority doc. | Low |
| 16 | `D:\SaaS\CRM\CURRENT_PROJECT_STATUS.md` | `D:\SaaS\CRM\docs\reports\u-series\CURRENT_PROJECT_STATUS.md` | U0 discovery output. DOC_STALE_REFERENCE_REPORT.md SR-007 confirms this is a point-in-time snapshot and not designed to be updated. | Not path-referenced from any authority doc. | Low |
| 17 | `D:\SaaS\CRM\AUTHORITY_RECONSTRUCTION_REPORT.md` | `D:\SaaS\CRM\docs\reports\u-series\AUTHORITY_RECONSTRUCTION_REPORT.md` | U1 authority reconstruction output. | DOC_NORMALIZATION_REPORT.md §4.1 C-003 references it for evidence (DUMMY_MODE claim). Text mention, not path link. | Low |
| 18 | `D:\SaaS\CRM\FEATURE_INVENTORY.md` | `D:\SaaS\CRM\docs\reports\u-series\FEATURE_INVENTORY.md` | U1 output. Evidence archive of feature status. | Not path-referenced from any authority doc. | Low |
| 19 | `D:\SaaS\CRM\MODULE_INVENTORY.md` | `D:\SaaS\CRM\docs\reports\u-series\MODULE_INVENTORY.md` | U1 output. | Not path-referenced from any authority doc. | Low |
| 20 | `D:\SaaS\CRM\ENTITY_INVENTORY.md` | `D:\SaaS\CRM\docs\reports\u-series\ENTITY_INVENTORY.md` | U1 output. | Not path-referenced from any authority doc. May be referenced by name from README.md documentation index. | Low |
| 21 | `D:\SaaS\CRM\WORKFLOW_INVENTORY.md` | `D:\SaaS\CRM\docs\reports\u-series\WORKFLOW_INVENTORY.md` | U1 output. | Not path-referenced from any authority doc. | Low |
| 22 | `D:\SaaS\CRM\ROLE_PERMISSION_INVENTORY.md` | `D:\SaaS\CRM\docs\reports\u-series\ROLE_PERMISSION_INVENTORY.md` | U1 output. | Not path-referenced from any authority doc. | Low |
| 23 | `D:\SaaS\CRM\API_INVENTORY.md` | `D:\SaaS\CRM\docs\reports\u-series\API_INVENTORY.md` | U1 output. ~199 API endpoints inventory. | May be referenced by name from README.md documentation index. Not path-referenced. | Low |
| 24 | `D:\SaaS\CRM\DOC_CATALOGUE.md` | `D:\SaaS\CRM\docs\reports\u-series\DOC_CATALOGUE.md` | U2 authoritative catalogue output. Should live with its sibling U2 outputs. | **Referenced (stale name) from:** SYSTEM-SNAPSHOT.md (lines 18, 292 — SR-001, SR-002), COMMERCIALISATION-PLAN.md (lines 61, 666 — SR-003, SR-004), README.md (lines 115, 131 — SR-005). All references use the old `DOC-CATALOGUE.md` name — they need updating regardless of move. After move, update to `docs/reports/u-series/DOC_CATALOGUE.md`. | Medium |
| 25 | `D:\SaaS\CRM\DOCUMENT_CLASSIFICATION_MATRIX.md` | `D:\SaaS\CRM\docs\reports\u-series\DOCUMENT_CLASSIFICATION_MATRIX.md` | U2 output. | Not path-referenced from any authority doc. | Low |
| 26 | `D:\SaaS\CRM\DOCUMENT_OWNERSHIP_MATRIX.md` | `D:\SaaS\CRM\docs\reports\u-series\DOCUMENT_OWNERSHIP_MATRIX.md` | U2 output. | Not path-referenced from any authority doc. | Low |
| 27 | `D:\SaaS\CRM\DOC_NORMALIZATION_REPORT.md` | `D:\SaaS\CRM\docs\reports\u-series\DOC_NORMALIZATION_REPORT.md` | U3 normalization report. | Not path-referenced from any authority doc. | Low |
| 28 | `D:\SaaS\CRM\DOC_CONFLICT_REGISTER.md` | `D:\SaaS\CRM\docs\reports\u-series\DOC_CONFLICT_REGISTER.md` | U3 conflict register. | DOC_NORMALIZATION_REPORT.md references it by name (text mention). | Low |
| 29 | `D:\SaaS\CRM\DOC_DUPLICATION_REGISTER.md` | `D:\SaaS\CRM\docs\reports\u-series\DOC_DUPLICATION_REGISTER.md` | U3 duplication register. | DOC_NORMALIZATION_REPORT.md references it by name (text mention). | Low |
| 30 | `D:\SaaS\CRM\DOC_STALE_REFERENCE_REPORT.md` | `D:\SaaS\CRM\docs\reports\u-series\DOC_STALE_REFERENCE_REPORT.md` | U3 stale reference report. | DOC_NORMALIZATION_REPORT.md references it by name (text mention). | Low |
| 31 | `D:\SaaS\CRM\WORKSPACE_RESTRUCTURING_PLAN.md` | `D:\SaaS\CRM\docs\reports\u-series\WORKSPACE_RESTRUCTURING_PLAN.md` | U4 output (this file's sibling). Created at root per task instructions; plan proposes eventual relocation. | No inbound references yet (newly created). | Low |
| 32 | `D:\SaaS\CRM\FILE_RELOCATION_MATRIX.md` | `D:\SaaS\CRM\docs\reports\u-series\FILE_RELOCATION_MATRIX.md` | U4 output (this file itself). Created at root per task instructions; plan proposes eventual relocation. | No inbound references yet (newly created). | Low |
| 33 | `D:\SaaS\CRM\FOLDER_PURPOSE_MATRIX.md` | `D:\SaaS\CRM\docs\reports\u-series\FOLDER_PURPOSE_MATRIX.md` | U4 output. Created at root per task instructions. | No inbound references yet (newly created). | Low |
| 34 | `D:\SaaS\CRM\BREAKAGE_RISK_REPORT.md` | `D:\SaaS\CRM\docs\reports\u-series\BREAKAGE_RISK_REPORT.md` | U4 output. Created at root per task instructions. | No inbound references yet (newly created). | Low |

---

### Phase 3 — Session Report Relocation (7 files)

Move active session-maintenance docs from root to `docs/reports/session/`.

**Pre-condition:** Update `COMMERCIALISATION-PLAN.md` to reference `docs/reports/session/SYSTEM-SNAPSHOT.md` before moving SYSTEM-SNAPSHOT.md. See BREAKAGE_RISK_REPORT.md for details.

| # | Current Path | Proposed Path | Reason | Dependencies | Risk |
|---|---|---|---|---|---|
| 35 | `D:\SaaS\CRM\CHANGELOG.md` | `D:\SaaS\CRM\docs\reports\session\CHANGELOG.md` | Historical version log; session maintenance doc, not authority doc. Reduces root clutter. | May be referenced by name from README.md. Not path-referenced from CLAUDE.md, DESIGN-SPEC.md, or FRAMEWORK.md. | Low |
| 36 | `D:\SaaS\CRM\PROGRESS.md` | `D:\SaaS\CRM\docs\reports\session\PROGRESS.md` | Session build tracker. Not in mandatory reading sequence. Reduces root clutter. | PROGRESS.md line 8 has stale reference to REBUILD-PLAN.md (SR-006). COMMERCIALISATION-PLAN.md may reference PROGRESS.md by name. Text mentions only — path update needed in README.md if it links here. | Medium |
| 37 | `D:\SaaS\CRM\PENDING.md` | `D:\SaaS\CRM\docs\reports\session\PENDING.md` | Root-level pending items tracker (separate from backend/PENDING.md which stays). | COMMERCIALISATION-PLAN.md references PENDING.md (text mention). README.md may reference it. Update README.md reference if linked. Note: `backend/PENDING.md` is unaffected. | Medium |
| 38 | `D:\SaaS\CRM\SESSION-HANDOFF.md` | `D:\SaaS\CRM\docs\reports\session\SESSION-HANDOFF.md` | Session handoff doc; consumed within sessions, not a root-level governance doc. | May be mentioned in COMMERCIALISATION-PLAN.md session protocol. DOC-READ-LOG.md has it as ✓ (text ref). | Medium |
| 39 | `D:\SaaS\CRM\SYSTEM-SNAPSHOT.md` | `D:\SaaS\CRM\docs\reports\session\SYSTEM-SNAPSHOT.md` | Session snapshot doc; referenced from COMMERCIALISATION-PLAN.md in session-open protocol. Not a root-level governance doc. | **COMMERCIALISATION-PLAN.md references SYSTEM-SNAPSHOT.md in session protocol.** Update COMMERCIALISATION-PLAN.md to use new path BEFORE moving this file. Also referenced in DOC_CONFLICT_REGISTER.md (C-001, C-003, C-005) as a text mention. | Medium |
| 40 | `D:\SaaS\CRM\SCREEN-ARTEFACTS.md` | `D:\SaaS\CRM\docs\reports\session\SCREEN-ARTEFACTS.md` | QC records and browser sign-offs; historical record, not session governance. | Referenced in DOC_CATALOGUE.md §A. Not path-referenced from CLAUDE.md mandatory reading sequence. Verify DESIGN-SPEC.md does not link to it by path. | Low |
| 41 | `D:\SaaS\CRM\DOC-READ-LOG.md` | `D:\SaaS\CRM\docs\reports\session\DOC-READ-LOG.md` | Cross-session read continuity log; session maintenance doc. Referenced in DOC_CATALOGUE.md as a root reference doc but its purpose is session-internal. | DOC_CATALOGUE.md lists it. DOC_STALE_REFERENCE_REPORT.md SR-010 flags its count as stale. Moving it does not worsen the stale count problem. | Low |

---

### Phase 4 — Reference Doc Relocation (1 file)

| # | Current Path | Proposed Path | Reason | Dependencies | Risk |
|---|---|---|---|---|---|
| 42 | `D:\SaaS\CRM\RENDER-DEPLOY.md` | `D:\SaaS\CRM\docs\reference\RENDER-DEPLOY.md` | Deployment guide; not in mandatory reading sequence; not a session doc. Belongs in reference, not at root. | Referenced from README.md (likely). Update README.md link after move. Referenced from COMMERCIALISATION-PLAN.md Reference Documents table (line 666 context). | Low |

---

### Phase 5 — Human Decision Required (not yet proposed for move)

These files are orphaned or have unresolved questions. They are listed here for completeness. No move is proposed until a human confirms the action.

| # | File | Current Path | Candidate Destination | Condition for Moving |
|---|---|---|---|---|
| — | `backend/product-spec-gap-register.md` | `D:\SaaS\CRM\backend\product-spec-gap-register.md` | `D:\SaaS\CRM\docs\archive\product-spec-gap-register.md` | Human confirms all gaps resolved during Phase 4. If open gaps remain, surface them in PENDING.md instead. |
| — | `backend/docs/domain/enterprise-depth.md` | `D:\SaaS\CRM\backend\docs\domain\enterprise-depth.md` | No move proposed — add cross-reference from architecture-overview.md if active | Human confirms whether this doc is actively consulted for multi-tenant/territory features. |
| — | `backend/docs/domain/data-governance-ownership.md` | `D:\SaaS\CRM\backend\docs\domain\data-governance-ownership.md` | No move — add companion cross-reference | Human confirms whether to merge with data-governance-layer.md or keep as companion doc. |
| — | `backend/docs/_b9/b9-p08-mobile-responsiveness-system.md` | `D:\SaaS\CRM\backend\docs\_b9\b9-p08-mobile-responsiveness-system.md` | No move — add cross-reference from FRAMEWORK.md §31 | Human confirms whether this doc is in the active reading flow. |

---

## Part B — Files That Stay

Files listed here do not move. Their current location is correct and appropriate.

### Root Authority Docs (MUST NOT MOVE)

| File | Current Path | Reason to Stay |
|---|---|---|
| `CLAUDE.md` | `D:\SaaS\CRM\CLAUDE.md` | Claude Code tool loads this from project root automatically. Moving it breaks the tool. |
| `DESIGN-SPEC.md` | `D:\SaaS\CRM\DESIGN-SPEC.md` | Referenced by name in CLAUDE.md 5-step reading sequence (step 1). Highest breakage risk. |
| `FRAMEWORK.md` | `D:\SaaS\CRM\FRAMEWORK.md` | Referenced by name in CLAUDE.md 5-step reading sequence (step 2). Highest breakage risk. |
| `PAGE-BUILD-PROTOCOL.md` | `D:\SaaS\CRM\PAGE-BUILD-PROTOCOL.md` | Referenced in CLAUDE.md ("mandatory read before every page build"). |
| `COMMERCIALISATION-PLAN.md` | `D:\SaaS\CRM\COMMERCIALISATION-PLAN.md` | Active session anchor; every session starts with RESUME POINT table. Moving breaks session protocol. |
| `PRODUCT-SPEC.md` | `D:\SaaS\CRM\PRODUCT-SPEC.md` | Core product identity; frequently referenced. Key authority doc that must remain prominent. |
| `README.md` | `D:\SaaS\CRM\README.md` | GitHub convention. |
| `CONTRIBUTING.md` | `D:\SaaS\CRM\CONTRIBUTING.md` | GitHub convention. |

### Backend Root (STAYS)

| File | Current Path | Reason to Stay |
|---|---|---|
| `backend/README.md` | `D:\SaaS\CRM\backend\README.md` | Backend system identity; contextually placed next to backend code. |
| `backend/BACKEND-QC.md` | `D:\SaaS\CRM\backend\BACKEND-QC.md` | Backend QC log; belongs with backend team deliverables. |
| `backend/CONSTRAINTS.md` | `D:\SaaS\CRM\backend\CONSTRAINTS.md` | Backend build constraints; contextually appropriate in backend/. Referenced in DOC_CATALOGUE.md as Authority/Active. |
| `backend/FRONTEND-BACKEND-MAPPING.md` | `D:\SaaS\CRM\backend\FRONTEND-BACKEND-MAPPING.md` | Frontend↔backend mapping; contextually belongs near backend route files. |
| `backend/PENDING.md` | `D:\SaaS\CRM\backend\PENDING.md` | Backend-specific pending items (P-016, P-017). Separate from root PENDING.md. |
| `backend/market-research-gap-register.md` | `D:\SaaS\CRM\backend\market-research-gap-register.md` | Active market research gaps; 2 resolved (MR-004/005), 5 open. Contextually backend. |
| `backend/product-spec-gap-register.md` | `D:\SaaS\CRM\backend\product-spec-gap-register.md` | Orphaned — stays pending human decision (see Phase 5 above). |

### Backend DB Docs (STAYS)

| File | Reason |
|---|---|
| `backend/db/activity_task_db/README.md` | Co-located with the schema it documents. |
| `backend/db/activity_task_db/self-qc.md` | Co-located with the schema it QCs. |
| `backend/db/transaction_db/README.md` | Co-located with the schema it documents. |
| `backend/db/transaction_db/self-qc.md` | Co-located with the schema it QCs. |
| `backend/db/transaction_db/transaction-policies.md` | Authority doc for the transaction_db; must be co-located with that schema. |

### Backend Gateway Docs (STAYS)

| File | Reason |
|---|---|
| `backend/gateway/README.md` | Gateway onboarding doc; contextually co-located with gateway code. |
| `backend/gateway/self-qc.md` | Gateway QC report; co-located with gateway. |

### Backend/docs/ — Entire Subtree (STAYS UNCHANGED)

The entire `backend/docs/` subtree (71 files across 9 subdirectories) is well-organized and purpose-appropriate. No moves proposed.

| Subdirectory | File Count | Status |
|---|---|---|
| `backend/docs/_b9/` | 15 | Active archetype specs — referenced from DESIGN-SPEC.md and CLAUDE.md reading sequence |
| `backend/docs/_qc/` | 3 | Complete QC logs — stays for audit trail |
| `backend/docs/adapters/` | 5 | Active Pakistan adapter specs |
| `backend/docs/adr/` | 3 | Active ADRs |
| `backend/docs/architecture/` | 5 | Active architecture specs |
| `backend/docs/domain/` | 21 | Active domain specs (3 orphaned — human decision pending) |
| `backend/docs/infrastructure/` | 15 | Active infrastructure specs (6 are authority-level) |
| `backend/docs/product/` | 4 | Active product specs |
| `backend/docs/security/` | 3 | Active security authority docs |
| `backend/docs/ui/` | 3 | Active UI specs |

### Tests (STAYS)

| File | Reason |
|---|---|
| `tests/e2e/playwright/SKIP-BACKLOG.md` | Co-located with the Playwright test suite it documents. |

---

## Part C — Reference Updates Required After Moving

When files move, these cross-references must be updated in the same session.

| Move # | Moved File | Source Doc to Update | Current Reference | Update To |
|---|---|---|---|---|
| 24 | DOC_CATALOGUE.md → docs/reports/u-series/ | `SYSTEM-SNAPSHOT.md` lines 18, 292 | `DOC-CATALOGUE.md` (wrong name + wrong path) | `docs/reports/u-series/DOC_CATALOGUE.md` |
| 24 | DOC_CATALOGUE.md → docs/reports/u-series/ | `COMMERCIALISATION-PLAN.md` lines 61, 666 | `DOC-CATALOGUE.md` (wrong name + wrong path) | `docs/reports/u-series/DOC_CATALOGUE.md` |
| 24 | DOC_CATALOGUE.md → docs/reports/u-series/ | `README.md` lines 115, 131 | `DOC-CATALOGUE.md` (wrong name + wrong path) | `docs/reports/u-series/DOC_CATALOGUE.md` |
| 39 | SYSTEM-SNAPSHOT.md → docs/reports/session/ | `COMMERCIALISATION-PLAN.md` (session protocol) | `SYSTEM-SNAPSHOT.md` | `docs/reports/session/SYSTEM-SNAPSHOT.md` |
| 37 | PENDING.md → docs/reports/session/ | `README.md` (if linked) | `PENDING.md` | `docs/reports/session/PENDING.md` |
| 36 | PROGRESS.md → docs/reports/session/ | `README.md` (if linked) | `PROGRESS.md` | `docs/reports/session/PROGRESS.md` |
| 35 | CHANGELOG.md → docs/reports/session/ | `README.md` (if linked) | `CHANGELOG.md` | `docs/reports/session/CHANGELOG.md` |
| 42 | RENDER-DEPLOY.md → docs/reference/ | `README.md` (if linked) | `RENDER-DEPLOY.md` | `docs/reference/RENDER-DEPLOY.md` |
