Status: Active
Authority Level: Medium
Owner: AI
Last Reviewed: 2026-06-22

---

# APPROVAL RECLASSIFICATION REPORT — Pakistan CRM OS

## Purpose

This report reclassifies all items previously listed under REQUIRES_OWNER_APPROVAL in REPOSITORY_RESTRUCTURING_PLAN.md, ROOT_LEVEL_CLEANUP_PLAN.md, LEGACY_AND_ARCHIVE_PLAN.md, and DOCUMENTATION_PLACEMENT_AUDIT.md against the new SAFE_REPOSITORY_HYGIENE tier defined in SAFE_REPOSITORY_HYGIENE_POLICY.md. It also reclassifies the Tier 3 and Tier 4 items from REMEDIATION_REPORT_2.md.

**New tier model applied:**
- Tier 0 — AUTONOMOUS: no approval needed, no report needed
- Tier 1 — SAFE_REPOSITORY_HYGIENE: no approval needed, execution report required
- Tier 2 — REQUIRES_APPROVAL: explicit human sign-off required before execution
- Tier 3 — PROHIBITED: never execute

**Classification principle:** Any action that could plausibly affect runtime behavior, CI/CD pipeline results, deployment, security enforcement, or test suite output is Tier 2 REQUIRES_APPROVAL regardless of how the action is described. Only pure repository organisation, documentation quality, and generated artifact cleanup actions qualify as Tier 1.

---

## SECTION 1 — CANDIDATE ACTION CLASSIFICATION (Step 2 from brief)

Classification of all 20 candidate action categories from the governance refinement brief:

| # | Candidate Action | Classification | Rationale |
|---|---|---|---|
| 1 | Documentation relocation (.md files between docs/ subfolders) | SAFE_REPOSITORY_HYGIENE | Pure file moves within docs/. No runtime, CI/CD, or import dependency. Fully reversible. Cross-references must be updated immediately after each move. |
| 2 | Documentation normalization (updating status/metadata fields) | SAFE_REPOSITORY_HYGIENE | Metadata edits within .md files. No functional change. Already partially covered under AUTONOMOUS but explicitly confirmed as Tier 1 when it accompanies a file move. |
| 3 | Folder restructuring (docs/ and reports/ only) | SAFE_REPOSITORY_HYGIENE | Creating subdirectories within docs/ or reorganising docs/ subdirectories does not affect any running code, CI/CD, or deployment. |
| 4 | Archive maintenance (moving files to docs/archive/) | SAFE_REPOSITORY_HYGIENE | Moving retired .md files to docs/archive/ is non-destructive and has no runtime impact. Retirement notices must be added at the same time. |
| 5 | Report relocation (moving generated reports to docs/08_reports/) | SAFE_REPOSITORY_HYGIENE | Gap registers, QC reports, and audit outputs are passive .md files. Moving them from backend/ or tests/ to docs/08_reports/ does not affect any import or CI step. |
| 6 | Report consolidation (merging superseded reports) | SAFE_REPOSITORY_HYGIENE | Merging two AI-generated reports that cover the same content is a documentation quality action with no runtime impact. Authority documents must not be merged without human review. |
| 7 | Generated artifact cleanup (git rm --cached __pycache__, .pyc, screenshots) | SAFE_REPOSITORY_HYGIENE | These are build artifacts that should never have been tracked. Removing them from git tracking does not affect runtime. Condition: confirm no CI step reads these file paths before executing. |
| 8 | Temporary artifact cleanup (removing .tmp, lock files from tracking) | SAFE_REPOSITORY_HYGIENE | Same rationale as #7. Condition: confirm files are not referenced in CI or startup scripts. |
| 9 | Output log cleanup (git rm --cached *.log) | SAFE_REPOSITORY_HYGIENE | Log files are runtime outputs, not inputs. Removing from git tracking does not affect any process. Condition: confirm no CI step reads the log file path. |
| 10 | Root-level cleanup (moving .md files from root to docs/) | SAFE_REPOSITORY_HYGIENE | Root .md prompt files and misplaced documentation files have no code dependencies. Moving them to docs/ or docs/archive/ is a documentation organisation action. |
| 11 | .gitignore improvements (adding new gitignore entries) | SAFE_REPOSITORY_HYGIENE | Adding entries to .gitignore only affects what git tracks. It does not change runtime behavior, CI pipeline logic, or any code. Existing tracked files are unaffected until git rm --cached is also run. |
| 12 | Documentation cross-reference fixes (updating paths after file moves) | SAFE_REPOSITORY_HYGIENE | Updating internal .md links to reflect new file paths is documentation maintenance. No code imports from .md files. |
| 13 | Authority reference fixes (updating stale doc references) | SAFE_REPOSITORY_HYGIENE | Same as #12. Updating paths in ACTIVE_AUTHORITY_DOCS table or OWNERSHIP blocks is metadata maintenance. |
| 14 | Archive placement fixes (moving legacy docs to archive) | SAFE_REPOSITORY_HYGIENE | Identical to #4 (archive maintenance). |
| 15 | Inventory updates (updating DOC_CATALOGUE.md counts) | AUTONOMOUS (Tier 0) | Content edits to an existing tracking document. Already covered under AUTONOMOUS inventory updates. Listed here for completeness — executes at Tier 0. |
| 16 | Governance metadata updates (Status, Last Reviewed fields) | AUTONOMOUS (Tier 0) | Content edits within existing .md files. Already AUTONOMOUS. Listed here for completeness. |
| 17 | Document status updates (Draft → Active promotions) | AUTONOMOUS (Tier 0) | Changing a Status: field in a document header is a documentation content edit. Already AUTONOMOUS. |
| 18 | Classification matrix updates | AUTONOMOUS (Tier 0) | Adding or updating rows in DOCUMENT_CLASSIFICATION_MATRIX.md is a documentation content edit. Already AUTONOMOUS. |
| 19 | Adding retirement/superseded notices to docs | AUTONOMOUS (Tier 0) | Adding a notice banner to an existing .md file is a documentation content edit already performed in prior sessions under AUTONOMOUS. Listed here for completeness. |
| 20 | Moving scripts between scripts/ folders | SAFE_REPOSITORY_HYGIENE | With condition: the script must be a standalone utility not imported by any Python module and not referenced in any Makefile target or CI step. If condition cannot be confirmed, escalate to REQUIRES_APPROVAL. |
| 21 | Moving backend .md files within backend/docs/ | SAFE_REPOSITORY_HYGIENE | backend/docs/ contains passive documentation files. Moving between subdirectories within backend/docs/ has no import dependency and no CI/CD impact. |

**Summary of candidate action classification:**
- SAFE_REPOSITORY_HYGIENE: 14 action categories (#1–#14, #20, #21 — items #15–#19 handled at Tier 0)
- AUTONOMOUS (Tier 0): 5 action categories (#15–#19, already covered by original matrix)
- REQUIRES_APPROVAL: 0 of the candidate categories
- PROHIBITED: 0 of the candidate categories

---

## SECTION 2 — RECLASSIFICATION OF REPOSITORY_RESTRUCTURING_PLAN.md REQUIRES_OWNER_APPROVAL ITEMS

Source: REPOSITORY_RESTRUCTURING_PLAN.md Part 3

| # | Item | Original Classification | New Classification | Rationale | Ready to Execute? |
|---|---|---|---|---|---|
| R-01 | bin/ directory — add to .gitignore and git rm -r --cached bin/ | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | bin/pgsql contains 4,416 PostgreSQL binary files. These may be referenced in Makefile targets, startup scripts, or README installation steps. Removing from git tracking without confirming these references could break local development setup. A confirmation step is required before execution. | No — owner must answer: "Is bin/pgsql referenced in any Makefile target, deployment script, or README?" |
| R-02 | data/ directory — add to .gitignore and git rm -r --cached data/ | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | data/postgres contains live PostgreSQL WAL files and postmaster.pid. The path may be hardcoded in connection strings or startup scripts. Same risk class as R-01. | No — owner must answer: "Is data/postgres path hardcoded in any connection string or config?" |
| R-03 | backend/.github/workflows/deploy-runtime.yml — move to root .github/workflows/ | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | GitHub Actions only reads .github/workflows/ at repository root. This move would change whether the workflow executes, how it is triggered, and potentially its path-based references. It is a CI/CD configuration change. | No — owner must answer: "Does this workflow currently run? Is it triggered from backend/?" |
| R-04 | backend/.github/actions/runtime-env-validate/action.yml — move to root .github/actions/ | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | This GitHub Action may be referenced by path in workflow files. Moving it changes the reference path and could break CI. This is a CI/CD configuration change. | No — verify no workflow references backend/.github/actions/ by path |
| R-05 | backend/src/ vs backend/services/ — document canonical pattern | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | This is an architectural decision about which Python module pattern is canonical. It affects future development direction. The documentation of the decision is Tier 0 (AUTONOMOUS) but the decision itself is human judgment. | No — human architectural decision required |
| R-06 | docs/01–05 empty stub folders — populate or remove | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | The strategy question (populate vs remove, which docs go where) requires human judgment. Once decided, the execution is SAFE_REPOSITORY_HYGIENE. | No — owner must decide strategy; execution is then Tier 1 |
| R-07 | tests/security/*.json — move to docs/reports/security/ or gitignore | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | These JSON files may be required as compliance evidence. The decision about whether to commit them as compliance artifacts or gitignore them as regenerated outputs is a compliance/legal judgment requiring human decision. | No — owner must decide: compliance evidence or regenerated output? |
| R-08 | tests/load/reports/*.html — move to docs/reports/load/ or gitignore | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | Same as R-07. The 2 production load test reports (c5-prod-*.html) may be especially valuable as performance evidence. Human decision required on disposition. | No — owner must decide: version-control as evidence or gitignore? |
| R-09 | Prompts/ → prompts/ rename (lowercase) | REQUIRES_OWNER_APPROVAL | SAFE_REPOSITORY_HYGIENE | A directory rename on case-insensitive Windows filesystems (NTFS) is effectively a no-op at the filesystem level for existing files. The rename is primarily a convention improvement. Condition: confirm no CI step, Makefile, or code imports from Prompts/ by path (a grep check is required). If confirmed, this is a pure cosmetic improvement. | Conditional — run grep check first to confirm no CI/code references `Prompts/` by path |
| R-10 | seal.ps1 location — move from root to bin/ or scripts/ | REQUIRES_OWNER_APPROVAL | SAFE_REPOSITORY_HYGIENE | seal.ps1 is a utility PowerShell script that manages the C0 seal. It is not imported by any Python or Node module. It is executed manually. Condition: verify that no Makefile target, CI step, or README installation instruction references seal.ps1 at the root path. If confirmed, moving to backend/scripts/ or a scripts/ folder is SAFE_REPOSITORY_HYGIENE. | Conditional — verify no Makefile/CI/README references root path |
| R-11 | backend/alembic/ vs backend/db/*/migrations/ — document which owns which | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | This involves documenting the migration architecture. The documentation is Tier 0 once the human decides, but the decision itself (which migration system owns which databases) is an architectural judgment requiring human input. | No — human must clarify architecture; documentation follows |

---

## SECTION 3 — RECLASSIFICATION OF ROOT_LEVEL_CLEANUP_PLAN.md ITEMS

Source: ROOT_LEVEL_CLEANUP_PLAN.md

| # | Item | Original Classification | New Classification | Rationale | Ready to Execute? |
|---|---|---|---|---|---|
| C-01 | COMMERCIALISATION-PLAN.md → docs/00_authority/ | SAFE (listed as safe in source) | SAFE_REPOSITORY_HYGIENE | Pure .md file move. No code dependency. Cross-references in CLAUDE.md context block and AI_OPERATING_CONTEXT.md must be updated after move. **NOTE: This move was already executed** (Part 7 of REPOSITORY_RESTRUCTURING_PLAN.md shows status EXECUTED). No further action required. | Already executed |
| C-02 | _archive/ → docs/archive/ merge | SAFE (listed as safe in source) | SAFE_REPOSITORY_HYGIENE | Moving _archive/README.md to docs/archive/ARCHIVE-README.md is a pure documentation organisation action. **NOTE: This move was already executed** (Part 7 of REPOSITORY_RESTRUCTURING_PLAN.md shows status EXECUTED). No further action required. | Already executed |
| C-03 | gw.log, gateway_startup.log, gateway_err.log → add to .gitignore | SAFE (listed as safe in source) | SAFE_REPOSITORY_HYGIENE | Adding log file patterns to .gitignore. No runtime impact. | Yes — Tier 1, ready |
| C-04 | .env.local → verify .gitignore coverage | SAFE (listed as safe in source) | SAFE_REPOSITORY_HYGIENE | Verifying that .gitignore pattern covers .env.local is a documentation/config check. If the entry is missing, adding it is Tier 1. | Yes — Tier 1, ready |
| C-05 | logs/ → add to .gitignore | SAFE (listed as safe in source) | SAFE_REPOSITORY_HYGIENE | Adding logs/ pattern to .gitignore. No runtime impact. | Yes — Tier 1, ready |
| C-06 | .pytest_cache/ → add to .gitignore | SAFE (listed as safe in source) | SAFE_REPOSITORY_HYGIENE | Adding .pytest_cache/ pattern to .gitignore. No runtime impact. | Yes — Tier 1, ready |
| C-07 | 6 root untracked prompt .md files → add to .gitignore or delete root copies | SAFE (listed as safe in source) | SAFE_REPOSITORY_HYGIENE | These are untracked duplicate files whose canonical versions exist in Prompts/Main/. Adding root copies to .gitignore or removing untracked copies is a non-destructive cleanup. | Yes — Tier 1, ready |
| C-08 | bin/ and data/ removal from git | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | See R-01 and R-02 above. Unchanged classification. | No — owner decision required |
| C-09 | Prompts/ → prompts/ rename | REQUIRES_OWNER_APPROVAL | SAFE_REPOSITORY_HYGIENE (conditional) | See R-09 above. Condition: confirm no CI/code path reference. | Conditional |

---

## SECTION 4 — RECLASSIFICATION OF LEGACY_AND_ARCHIVE_PLAN.md ITEMS

Source: LEGACY_AND_ARCHIVE_PLAN.md

| # | Item | Original Classification | New Classification | Rationale | Ready to Execute? |
|---|---|---|---|---|---|
| L-01 | backend/PENDING.md → docs/reports/session/BACKEND-PENDING.md | REQUIRES_OWNER_APPROVAL | SAFE_REPOSITORY_HYGIENE | backend/PENDING.md is a passive .md file. No Python module imports it. No CI step references it. The concern in the original plan was the merge strategy for an existing PENDING.md — this is now resolved by renaming the destination to BACKEND-PENDING.md to avoid collision. | Yes — Tier 1, ready |
| L-02 | backend/market-research-gap-register.md → docs/08_reports/MARKET-RESEARCH-GAP-REGISTER.md | REQUIRES_OWNER_APPROVAL | SAFE_REPOSITORY_HYGIENE | Pure .md file move from backend root to docs/08_reports/. No import dependency. No CI reference. | Yes — Tier 1, ready |
| L-03 | backend/product-spec-gap-register.md → docs/08_reports/PRODUCT-SPEC-GAP-REGISTER.md | REQUIRES_OWNER_APPROVAL | SAFE_REPOSITORY_HYGIENE | Same rationale as L-02. | Yes — Tier 1, ready |
| L-04 | backend/docs/phase4-gap-register.md → docs/08_reports/PHASE4-GAP-REGISTER.md | REQUIRES_OWNER_APPROVAL | SAFE_REPOSITORY_HYGIENE | Pure .md file move within documentation tree. No import dependency. | Yes — Tier 1, ready |
| L-05 | backend/BACKEND-QC.md → backend/docs/BACKEND-QC.md | REQUIRES_OWNER_APPROVAL | SAFE_REPOSITORY_HYGIENE | Moving a QC report .md file within the backend documentation tree. No Python module imports backend/BACKEND-QC.md. No CI step references it by path. | Yes — Tier 1, ready |
| L-06 | backend/CONSTRAINTS.md → backend/docs/CONSTRAINTS.md | REQUIRES_OWNER_APPROVAL | SAFE_REPOSITORY_HYGIENE | Moving a constraints documentation file within backend/docs/. No runtime import. Note: AI_OPERATING_CONTEXT.md references backend/CONSTRAINTS.md as an authority document — this cross-reference must be updated immediately after the move. | Yes — Tier 1, ready; update AI_OPERATING_CONTEXT.md cross-reference |
| L-07 | backend/FRONTEND-BACKEND-MAPPING.md → docs/03_fullstack_contracts/FRONTEND-BACKEND-MAPPING.md | REQUIRES_OWNER_APPROVAL | SAFE_REPOSITORY_HYGIENE | Pure .md file move to the correct location in docs/. No code dependency. Cross-references in other docs (DOCUMENTATION_PLACEMENT_AUDIT.md etc.) must be updated. | Yes — Tier 1, ready |
| L-08 | tests/security/*.json scan artifacts — move or gitignore | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | Owner must decide whether these JSON files are compliance evidence (commit to docs/reports/security/) or regenerated CI outputs (gitignore). See R-07 above. | No — owner decision required |
| L-09 | tests/load/reports/*.html load test reports — move or gitignore | REQUIRES_OWNER_APPROVAL | REQUIRES_APPROVAL | Same as L-08 / R-08. Owner must decide disposition. | No — owner decision required |
| L-10 | frontend/src/ library subdirectories — disposition | Keep as reference (already decided) | No change needed | LEGACY_AND_ARCHIVE_PLAN.md already correctly classifies these as "Keep as reference." No reclassification needed. | N/A — already resolved |

---

## SECTION 5 — RECLASSIFICATION OF DOCUMENTATION_PLACEMENT_AUDIT.md MISPLACED ITEMS

Source: DOCUMENTATION_PLACEMENT_AUDIT.md (17 misplaced items)

| # | Item | Original Classification | New Classification | Rationale | Ready to Execute? |
|---|---|---|---|---|---|
| D-01 | COMMERCIALISATION-PLAN.md root → docs/00_authority/ | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | Already executed (see C-01). | Already done |
| D-02 | AUDIT REMEDIATION.md root → gitignore root copy | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | Root copy is untracked duplicate of Prompts/Main/ canonical. Gitignoring or removing untracked copy is non-destructive. | Yes — Tier 1, ready |
| D-03 | DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md root → gitignore | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | Same as D-02. | Yes — Tier 1, ready |
| D-04 | GOVERNANCE IMPLEMENTATION PHASE 1.md root → gitignore | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | Same as D-02. | Yes — Tier 1, ready |
| D-05 | PHASE 1 GOVERNANCE VALIDATION.md root → gitignore | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | Same as D-02. | Yes — Tier 1, ready |
| D-06 | PROMPT SEQUENCE.md root → gitignore | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | Same as D-02. | Yes — Tier 1, ready |
| D-07 | FULL REPOSITORY NORMALIZATION AND REALITY AUDIT.md root → gitignore | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | Same as D-02. | Yes — Tier 1, ready |
| D-08 | backend/BACKEND-QC.md → backend/docs/ | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | See L-05 above. | Yes — Tier 1, ready |
| D-09 | backend/CONSTRAINTS.md → backend/docs/ | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | See L-06 above. | Yes — Tier 1, ready |
| D-10 | backend/FRONTEND-BACKEND-MAPPING.md → docs/03_fullstack_contracts/ | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | See L-07 above. | Yes — Tier 1, ready |
| D-11 | backend/PENDING.md → docs/reports/session/ | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | See L-01 above. | Yes — Tier 1, ready |
| D-12 | backend/market-research-gap-register.md → docs/08_reports/ | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | See L-02 above. | Yes — Tier 1, ready |
| D-13 | backend/product-spec-gap-register.md → docs/08_reports/ | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | See L-03 above. | Yes — Tier 1, ready |
| D-14 | backend/docs/phase4-gap-register.md → docs/08_reports/ | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | See L-04 above. | Yes — Tier 1, ready |
| D-15 | tests/e2e/playwright/SKIP-BACKLOG.md → docs/04_testing/ | MISPLACED — action required | SAFE_REPOSITORY_HYGIENE | SKIP-BACKLOG.md is a planning document within the test directory. No pytest conftest or CI step imports from it. Moving to docs/04_testing/ is a pure documentation organisation action. | Yes — Tier 1, ready |
| D-16 | docs/reference/RENDER-DEPLOY.md → docs/05_deployment/ (optional) | ACCEPTABLE — optional move | SAFE_REPOSITORY_HYGIENE | This is a low-priority cosmetic improvement. The file is acceptable at its current location. If moved, it is Tier 1. | Optional — Tier 1 if/when executed |
| D-17 | Verify DOCUMENT_CLASSIFICATION_MATRIX.md duplicate across docs/08_reports/ and docs/reports/u-series/ | INVESTIGATE | AUTONOMOUS (Tier 0) | This is a content verification task — reading two files and adding a SUPERSEDED notice to the older one if they are near-duplicates. Already partially executed in REMEDIATION_REPORT_2.md (DUP-009). | Already done (DUP-009 in REMEDIATION_REPORT_2.md) |

---

## SECTION 6 — RECLASSIFICATION OF REMEDIATION_REPORT_2.md TIER 3 AND TIER 4 ITEMS

Source: REMEDIATION_REPORT_2.md

### Tier 3 Items from REMEDIATION_REPORT_2.md (Archive Candidates Pending Human Decision)

| # | Item | Previous Status | New Classification | Rationale | Ready to Execute? |
|---|---|---|---|---|---|
| RR-T3-01 | U0–U9 LEGACY MODERNIZATION AUDIT.md (root) → docs/archive/ or docs/09_prompts/ | Tier 3 — human decision required | SAFE_REPOSITORY_HYGIENE | This is a completed session prompt file. Its outputs are preserved in docs/reports/u-series/. Moving it to docs/archive/ is a pure documentation organisation action with no runtime impact. The original Tier 3 classification reflected the old policy gap where file moves were always REQUIRES_OWNER_APPROVAL. Under the new tier model, this move qualifies as SAFE_REPOSITORY_HYGIENE. | Yes — Tier 1, ready |
| RR-T3-02 | U10 — U0–U9 AUDIT REMEDIATION.md (root) → docs/archive/ | Tier 3 — human decision required | SAFE_REPOSITORY_HYGIENE | Same rationale as RR-T3-01. Session prompt file with outputs already in docs/reports/u-series/U10_FINAL_STATUS.md. | Yes — Tier 1, ready |
| RR-T3-03 | U5 — WORKSPACE RESTRUCTURING EXECUTION.md (root) → docs/archive/ | Tier 3 — human decision required | SAFE_REPOSITORY_HYGIENE | Same rationale. Execution complete; outputs in u-series. | Yes — Tier 1, ready |
| RR-T3-04 | U6 — DOC TO CODE DELTA ANALYSIS.md (root) → docs/archive/ | Tier 3 — human decision required | SAFE_REPOSITORY_HYGIENE | Same rationale. | Yes — Tier 1, ready |
| RR-T3-05 | U7 — DELTA REMEDIATION.md (root) → docs/archive/ | Tier 3 — human decision required | SAFE_REPOSITORY_HYGIENE | Same rationale. Remediation complete. | Yes — Tier 1, ready |
| RR-T3-06 | U8 — WORKSPACE SEALING.md (root) → docs/archive/ | Tier 3 — human decision required | SAFE_REPOSITORY_HYGIENE | Same rationale. Seal complete. | Yes — Tier 1, ready |
| RR-T3-07 | U9 — TEST SUITE PLANNING.md (root) → docs/archive/ | Tier 3 — human decision required | SAFE_REPOSITORY_HYGIENE | Same rationale. Test suite built. | Yes — Tier 1, ready |
| RR-T3-08 | GOVERNANCE IMPLEMENTATION PHASE 1.md (root) → docs/archive/ | Tier 3 — human decision required | SAFE_REPOSITORY_HYGIENE | Phase 1 governance execution complete. Canonical copy in Prompts/Main/. | Yes — Tier 1, ready |
| RR-T3-09 | PHASE 1 GOVERNANCE VALIDATION.md (root) → docs/archive/ | Tier 3 — human decision required | SAFE_REPOSITORY_HYGIENE | Validation complete. Canonical copy in Prompts/Main/. | Yes — Tier 1, ready |
| RR-T3-10 | AUDIT REMEDIATION.md (root) → docs/archive/ after session validated | Tier 3 — human decision required | SAFE_REPOSITORY_HYGIENE | Session validated (REMEDIATION_REPORT_2.md confirms). Canonical copy in Prompts/Main/. | Yes — Tier 1, ready |
| RR-T3-11 | DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md (root) → docs/archive/ | Tier 3 — human decision required | SAFE_REPOSITORY_HYGIENE | Normalisation complete. Canonical copy in Prompts/Main/. | Yes — Tier 1, ready |

### Tier 4 Items from REMEDIATION_REPORT_2.md (Archive Documents — Notices Added)

These items were already executed in the REMEDIATION_REPORT_2.md session. All 7 docs/archive/ documents now have retirement notices. No further action required.

| # | Item | Status |
|---|---|---|
| RR-T4-01 | docs/archive/deployment-pipelines.md — retirement notice | Already executed (REMEDIATION_REPORT_2.md Tier 4) |
| RR-T4-02 | docs/archive/gap-register.md — retirement notice | Already executed |
| RR-T4-03 | docs/archive/FRAMEWORK-GAPS.md — retirement notice | Already executed |
| RR-T4-04 | docs/archive/CATALOGUE-MERGE-PLAN.md — retirement notice | Already executed |
| RR-T4-05 | docs/archive/MAPPING-TRACKER.md — retirement notice | Already executed |
| RR-T4-06 | docs/archive/DOC-CATALOGUE.md — notice pre-existing | No action required |
| RR-T4-07 | docs/archive/REBUILD-PLAN.md — notice pre-existing | No action required |

### Tier 5 Items from REMEDIATION_REPORT_2.md (Human Decision Required — Remain REQUIRES_APPROVAL)

| # | Item | New Classification | Rationale |
|---|---|---|---|
| RR-T5-01 | backend/docs/phase4-gap-register.md disposition (archive or merge) | SAFE_REPOSITORY_HYGIENE (reclassified) | Moving or archiving this file is a documentation organisation action. The content decision (archive vs merge) is minor; moving to docs/archive/ is the safe default. Reclassified from Tier 5 to Tier 1. |
| RR-T5-02 | backend/PENDING.md disposition (keep or merge) | SAFE_REPOSITORY_HYGIENE (reclassified) | See L-01. Moving to docs/reports/session/BACKEND-PENDING.md is Tier 1. |
| RR-T5-03 | PROMPT SEQUENCE.md disposition (archive or keep) | SAFE_REPOSITORY_HYGIENE (reclassified) | This is a session prompt file in the root directory. Moving to Prompts/Main/ (if not already there) or docs/archive/ is Tier 1. |
| RR-T5-04 | CONTRIBUTING.md (keep at root or move to docs/) | REQUIRES_APPROVAL | CONTRIBUTING.md follows GitHub convention (should be at root for GitHub to link it automatically). Moving it would affect GitHub repository discoverability features. Owner should confirm before moving. |

---

## SUMMARY

### Total Items Reviewed

| Source Document | Items Reviewed |
|---|---|
| REPOSITORY_RESTRUCTURING_PLAN.md Part 3 | 11 |
| ROOT_LEVEL_CLEANUP_PLAN.md | 9 |
| LEGACY_AND_ARCHIVE_PLAN.md | 10 |
| DOCUMENTATION_PLACEMENT_AUDIT.md | 17 |
| REMEDIATION_REPORT_2.md Tier 3/4/5 | 16 |
| Candidate action categories (Step 2) | 21 |
| **Total** | **84** |

Note: Many items appear in multiple source documents (e.g., backend/.md moves appear in both REPOSITORY_RESTRUCTURING_PLAN.md and DOCUMENTATION_PLACEMENT_AUDIT.md). After deduplication, the unique action items are:

### Unique Action Items After Deduplication

| Classification | Count | Summary |
|---|---|---|
| Already executed | 4 | COMMERCIALISATION-PLAN.md move, _archive/ merge, 7 archive notices (batched), DUP-009 |
| SAFE_REPOSITORY_HYGIENE — ready to execute | 28 | See detailed list below |
| SAFE_REPOSITORY_HYGIENE — conditional | 2 | Prompts/ rename (R-09), seal.ps1 move (R-10) — grep check required first |
| REQUIRES_APPROVAL — remains human-gated | 9 | bin/, data/, .github/ workflow moves, architectural decisions, compliance decisions |
| AUTONOMOUS (Tier 0) — already covered | 5 | Metadata edits, notices, catalogue entries |
| N/A — no action required | 3 | Library pages keep, RR-T4 already done, D-17 already done |

**Reclassified from REQUIRES_OWNER_APPROVAL to SAFE_REPOSITORY_HYGIENE: 28 unique actions can now proceed without human approval.**

**Remain REQUIRES_APPROVAL: 9 actions (bin/, data/, CI/CD moves, architectural decisions, compliance decisions).**

### Ready-to-Execute SAFE_REPOSITORY_HYGIENE Actions (Prioritized)

**Highest priority (misplaced files that affect cross-reference accuracy):**
1. backend/BACKEND-QC.md → backend/docs/BACKEND-QC.md
2. backend/CONSTRAINTS.md → backend/docs/CONSTRAINTS.md + update AI_OPERATING_CONTEXT.md cross-reference
3. backend/FRONTEND-BACKEND-MAPPING.md → docs/03_fullstack_contracts/FRONTEND-BACKEND-MAPPING.md
4. backend/PENDING.md → docs/reports/session/BACKEND-PENDING.md
5. backend/market-research-gap-register.md → docs/08_reports/MARKET-RESEARCH-GAP-REGISTER.md
6. backend/product-spec-gap-register.md → docs/08_reports/PRODUCT-SPEC-GAP-REGISTER.md
7. backend/docs/phase4-gap-register.md → docs/08_reports/PHASE4-GAP-REGISTER.md
8. tests/e2e/playwright/SKIP-BACKLOG.md → docs/04_testing/SKIP-BACKLOG.md

**Medium priority (root cleanup):**
9. Add .gitignore entries (log files, .pytest_cache/, test artifacts, root prompt duplicates)
10. Git rm --cached for .pyc, __pycache__, .pytest_cache files
11. Root session prompt files → docs/archive/ (11 files: RR-T3-01 through RR-T3-11)
12. Root untracked .md prompt duplicates → gitignore (D-02 through D-07)

**Lower priority (optional improvements):**
13. docs/reference/RENDER-DEPLOY.md → docs/05_deployment/ (optional)
14. Prompts/ → prompts/ rename (after grep confirmation)
15. seal.ps1 → scripts/ (after Makefile/CI confirmation)
16. Populate docs/01_backend/ and docs/02_frontend/ stub folders (after owner decides on strategy)

---

*End APPROVAL_RECLASSIFICATION_REPORT.md*
