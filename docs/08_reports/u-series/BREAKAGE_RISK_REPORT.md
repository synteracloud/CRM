# BREAKAGE_RISK_REPORT.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U4 — Workspace Restructuring Plan)
**Status:** Planning only — NO files have been moved or modified.
**Companion docs:** WORKSPACE_RESTRUCTURING_PLAN.md, FILE_RELOCATION_MATRIX.md

---

## Overall Restructuring Risk: LOW-MEDIUM

**Summary:** The vast majority of proposed moves are low risk because the files being moved (U-series outputs, completed trackers, superseded docs) are not referenced by path from any code file or from the three highest-traffic authority docs (CLAUDE.md, DESIGN-SPEC.md, FRAMEWORK.md). The medium-risk moves are concentrated in 3 files (DOC_CATALOGUE.md, SYSTEM-SNAPSHOT.md, PENDING.md) that require reference updates in COMMERCIALISATION-PLAN.md and README.md before or alongside the move.

No HIGH risk moves are proposed. The files identified as high-risk (CLAUDE.md, DESIGN-SPEC.md, FRAMEWORK.md) are explicitly NOT being moved.

---

## 1. Files That MUST NOT Be Moved

These files have critical dependencies that make moving them either impossible or extremely high risk. They are listed here as an explicit "do not touch" guard.

| File | Risk Level | Why It Must Not Move |
|---|---|---|
| `CLAUDE.md` | **CRITICAL — DO NOT MOVE** | Claude Code (the tool) loads this file from the project root automatically. This is hardcoded behavior in the tool — the file must be at `D:\SaaS\CRM\CLAUDE.md`. Moving it would silently disable all project-specific session instructions, scope gates, build checklists, and reading sequences. There is no workaround short of modifying the tool itself. |
| `DESIGN-SPEC.md` | **CRITICAL — DO NOT MOVE** | CLAUDE.md mandatory reading sequence (step 1) references `DESIGN-SPEC.md` by bare filename. FRAMEWORK.md §31 also references it. Moving it requires coordinated updates to CLAUDE.md and FRAMEWORK.md simultaneously, with no easy validation that all references were caught. The risk of breaking the scope gate (which prevents working on out-of-phase pages) is unacceptable. |
| `FRAMEWORK.md` | **CRITICAL — DO NOT MOVE** | CLAUDE.md mandatory reading sequence (step 2) references `FRAMEWORK.md §31` by bare filename. Moving it has the same risk as DESIGN-SPEC.md. The FRAMEWORK.md contains the complete CSS/JS stack rules — missing this file in a session causes incorrect page builds. |
| `PAGE-BUILD-PROTOCOL.md` | **HIGH RISK — DO NOT MOVE** | Referenced in CLAUDE.md as part of the pre-build reading protocol. Also referenced from the mandatory 5-step sequence. Moving requires updating CLAUDE.md. Risk is high because CLAUDE.md is itself a session-critical file — any error in updating it can corrupt the entire session protocol. |
| `COMMERCIALISATION-PLAN.md` | **HIGH RISK — DO NOT MOVE** | Every session opens by reading the RESUME POINT table in this file. CLAUDE.md and the session-open protocol both depend on this file being at root. Moving it would silently break the session-open sequence — a developer following the protocol would fail to find the resume state. |
| `backend/docs/_b9/*.md` (all 15) | **HIGH RISK — DO NOT MOVE** | Referenced by name in DESIGN-SPEC.md §5 archetype quick reference and confirmed present by DOC_STALE_REFERENCE_REPORT.md. These 15 files are read as step 4 in the CLAUDE.md mandatory reading sequence. Moving them requires updating both DESIGN-SPEC.md and FRAMEWORK.md. |
| `backend/docs/infrastructure/api-standards.md` | **HIGH RISK — DO NOT MOVE** | Authority-class document. Referenced from backend/docs/architecture/architecture-overview.md and likely from CONTRIBUTING.md. Any new API endpoint requires reading this file. Moving it without updating all references breaks the developer workflow for new endpoints. |
| `backend/docs/security/*.md` (3 files) | **HIGH RISK — DO NOT MOVE** | Three authority-class security docs (identity-auth-rbac.md, org-multi-tenancy.md, security-model.md). These govern all JWT, RBAC, and tenant isolation behavior. They are co-located with the code they govern in backend/. Moving them from backend/docs/security/ to any other location risks developers not finding them during security audits or new feature development. |

---

## 2. High-Risk Moves

No high-risk moves are proposed in this plan. The decisions above to KEEP high-risk files in place means no proposed move falls in the high-risk category.

---

## 3. Medium-Risk Moves

These moves require updating cross-references in other documents before or simultaneously with the move. Moving without updating references will leave broken text links in active authority docs.

### M-001 — DOC_CATALOGUE.md (Move #24)

| Field | Value |
|---|---|
| **File** | `D:\SaaS\CRM\DOC_CATALOGUE.md` |
| **Proposed Move** | → `D:\SaaS\CRM\docs\reports\u-series\DOC_CATALOGUE.md` |
| **Risk Level** | Medium |
| **Why Medium** | DOC_CATALOGUE.md is the authoritative project document index. It is referenced (under the stale old name `DOC-CATALOGUE.md`) from SYSTEM-SNAPSHOT.md, COMMERCIALISATION-PLAN.md, and README.md. While these references are already stale (wrong filename), moving DOC_CATALOGUE.md to a new path without updating those docs adds a second layer of incorrectness — wrong name AND wrong path. |
| **Inbound References** | SYSTEM-SNAPSHOT.md lines 18, 292 (SR-001, SR-002); COMMERCIALISATION-PLAN.md lines 61, 666 (SR-003, SR-004); README.md lines 115, 131 (SR-005) |
| **Mitigation** | Update the 3 inbound reference documents to point to `docs/reports/u-series/DOC_CATALOGUE.md` BEFORE or simultaneously with the move. This resolves SR-001 through SR-005 from DOC_STALE_REFERENCE_REPORT.md in the same operation. |
| **What breaks if NOT mitigated** | SYSTEM-SNAPSHOT.md, COMMERCIALISATION-PLAN.md, and README.md will have references to a file that no longer exists at root. Navigation confusion for any developer following these links. |

---

### M-002 — SYSTEM-SNAPSHOT.md (Move #39)

| Field | Value |
|---|---|
| **File** | `D:\SaaS\CRM\SYSTEM-SNAPSHOT.md` |
| **Proposed Move** | → `D:\SaaS\CRM\docs\reports\session\SYSTEM-SNAPSHOT.md` |
| **Risk Level** | Medium |
| **Why Medium** | SYSTEM-SNAPSHOT.md is referenced in the COMMERCIALISATION-PLAN.md session-open protocol. Every session is supposed to start with the RESUME POINT table (in COMMERCIALISATION-PLAN.md) and then read SYSTEM-SNAPSHOT.md for the 60-second system state. If SYSTEM-SNAPSHOT.md moves without COMMERCIALISATION-PLAN.md being updated, the first session after the move will fail to find it. |
| **Inbound References** | COMMERCIALISATION-PLAN.md (session-open protocol section; specific line number not confirmed but the reference is documented in DOC_NORMALIZATION_REPORT.md C-001 context). |
| **Mitigation** | Update COMMERCIALISATION-PLAN.md to reference `docs/reports/session/SYSTEM-SNAPSHOT.md` BEFORE moving SYSTEM-SNAPSHOT.md. Do this in a single edit-then-move operation so no session runs between the edit and the move with a broken path. |
| **Additional consideration** | SYSTEM-SNAPSHOT.md itself has critical conflicts (C-001, C-003, C-005 in DOC_CONFLICT_REGISTER.md). The recommended approach: refresh SYSTEM-SNAPSHOT.md content to resolve C-001/C-003/C-005, then update COMMERCIALISATION-PLAN.md reference, then move the file. This sequences the work correctly. |
| **What breaks if NOT mitigated** | The session-open protocol in COMMERCIALISATION-PLAN.md directs the developer to read a file that no longer exists at root. The 60-second system state is missed. |

---

### M-003 — PROGRESS.md (Move #36)

| Field | Value |
|---|---|
| **File** | `D:\SaaS\CRM\PROGRESS.md` |
| **Proposed Move** | → `D:\SaaS\CRM\docs\reports\session\PROGRESS.md` |
| **Risk Level** | Medium |
| **Why Medium** | PROGRESS.md line 8 has a stale reference to REBUILD-PLAN.md (SR-006). Additionally, COMMERCIALISATION-PLAN.md or README.md may reference PROGRESS.md by name. The move itself is low-risk structurally, but the file's own stale content (stale reference to REBUILD-PLAN.md) means it should be cleaned up when touched. |
| **Inbound References** | COMMERCIALISATION-PLAN.md (possible text mention in Reference Documents table). README.md (possibly linked in doc index). |
| **Mitigation** | Update PROGRESS.md line 8 to replace the stale `REBUILD-PLAN.md` reference with `COMMERCIALISATION-PLAN.md` (resolves SR-006). Check README.md for a link to PROGRESS.md and update the path if found. Move the file after reference updates. |
| **What breaks if NOT mitigated** | README.md link to PROGRESS.md becomes broken. PROGRESS.md retains a stale reference to REBUILD-PLAN.md at the point of move. |

---

### M-004 — PENDING.md (root) (Move #37)

| Field | Value |
|---|---|
| **File** | `D:\SaaS\CRM\PENDING.md` |
| **Proposed Move** | → `D:\SaaS\CRM\docs\reports\session\PENDING.md` |
| **Risk Level** | Medium |
| **Why Medium** | PENDING.md (root) is the primary task checklist and is likely referenced from COMMERCIALISATION-PLAN.md (Reference Documents table) and README.md. The file name is also the same as `backend/PENDING.md` (which stays), so a bare reference to `PENDING.md` after the move would be ambiguous unless the path is explicit. |
| **Inbound References** | COMMERCIALISATION-PLAN.md Reference Documents table (likely); README.md (possibly). |
| **Mitigation** | Update COMMERCIALISATION-PLAN.md and README.md to use explicit path `docs/reports/session/PENDING.md`. Note: `backend/PENDING.md` stays at its current path — no change needed for that file. |
| **What breaks if NOT mitigated** | References to `PENDING.md` become ambiguous (two PENDING.md files in different locations). Navigation confusion for session-start checklist. |

---

### M-005 — SESSION-HANDOFF.md (Move #38)

| Field | Value |
|---|---|
| **File** | `D:\SaaS\CRM\SESSION-HANDOFF.md` |
| **Proposed Move** | → `D:\SaaS\CRM\docs\reports\session\SESSION-HANDOFF.md` |
| **Risk Level** | Medium |
| **Why Medium** | SESSION-HANDOFF.md may be referenced in COMMERCIALISATION-PLAN.md session protocol. It is not in the CLAUDE.md mandatory reading sequence, but it is a session-critical file that a developer would look for at root by convention. |
| **Inbound References** | Possibly COMMERCIALISATION-PLAN.md. DOC-READ-LOG.md (text mention as ✓ read). |
| **Mitigation** | Check COMMERCIALISATION-PLAN.md for a reference to SESSION-HANDOFF.md. Update if found. Announce the new path in the first session after the move. |
| **What breaks if NOT mitigated** | Minimal — SESSION-HANDOFF.md is a less frequently cited file than SYSTEM-SNAPSHOT.md. |

---

## 4. Low-Risk Moves

These moves have no significant cross-references in active authority docs. They can be executed without preparatory reference updates, though README.md links should be checked as a final step.

| Move # | File | Risk Level | Reason Low Risk |
|---|---|---|---|
| 1 | `_archive/deployment-pipelines.md` → docs/archive/ | Low | Already in archive. No active inbound references. |
| 2 | `_archive/FRAMEWORK-GAPS.md` → docs/archive/ | Low | Already in archive. No active inbound references. |
| 3 | `_archive/gap-register.md` → docs/archive/ | Low | Already in archive. No active inbound references. |
| 4 | `DOC-CATALOGUE.md` → docs/archive/ | Low | Already marked SUPERSEDED (U3 banner applied). Stale references point to this with wrong name already; moving it does not worsen the situation. |
| 5 | `REBUILD-PLAN.md` → docs/archive/ | Low | Already marked SUPERSEDED and CLOSED. PROGRESS.md line 8 references it, but that reference is already stale (SR-006). |
| 6 | `MAPPING-TRACKER.md` → docs/archive/ | Low | Marked COMPLETE. No active inbound references from any authority or session doc. |
| 7 | `CATALOGUE-MERGE-PLAN.md` → docs/archive/ | Low | Marked COMPLETE. Orphaned per DOCUMENT_OWNERSHIP_MATRIX.md and DOC_DUPLICATION_REGISTER.md D-009. |
| 8–12 | U-pass prompt docs (U0–U4) → docs/reports/u-series/ | Low | Not referenced by path from CLAUDE.md, DESIGN-SPEC.md, FRAMEWORK.md, or COMMERCIALISATION-PLAN.md. |
| 13–16 | U0 output files (4) → docs/reports/u-series/ | Low | Discovery outputs; not referenced by path from authority docs. |
| 17–23 | U1 output files (7) → docs/reports/u-series/ | Low | Inventory outputs; not referenced by path from authority docs. |
| 25–26 | DOCUMENT_CLASSIFICATION_MATRIX.md, DOCUMENT_OWNERSHIP_MATRIX.md → docs/reports/u-series/ | Low | U2 outputs alongside DOC_CATALOGUE.md. Not referenced independently. |
| 27–30 | U3 output files (4) → docs/reports/u-series/ | Low | Normalization outputs; not referenced by path from authority docs. |
| 31–34 | U4 output files (this set, 4) → docs/reports/u-series/ | Low | Newly created; no inbound references yet. |
| 35 | `CHANGELOG.md` → docs/reports/session/ | Low | Version history; not in mandatory reading sequence. README.md may link it by name — update README if so. |
| 40 | `SCREEN-ARTEFACTS.md` → docs/reports/session/ | Low | QC records; not referenced in CLAUDE.md reading sequence. Verify DESIGN-SPEC.md does not link to it by path. |
| 41 | `DOC-READ-LOG.md` → docs/reports/session/ | Low | Session continuity log; not referenced by path from authority docs. Already flagged as stale in content (SR-010). |
| 42 | `RENDER-DEPLOY.md` → docs/reference/ | Low | Deployment guide; not in mandatory reading sequence. Update README.md link after move. |

---

## 5. Risk Matrix

| Risk Category | File Count | Mitigation Required |
|---|---|---|
| CRITICAL — DO NOT MOVE | 5 files | N/A — excluded from restructuring |
| HIGH RISK — DO NOT MOVE | 20 files (15 b9-p specs + 5 backend authority docs) | N/A — excluded from restructuring |
| Medium risk — update references first | 5 files (M-001 through M-005) | Update inbound references in COMMERCIALISATION-PLAN.md, README.md before moving |
| Low risk — check README after | 32 files | Check README.md doc index links; update if found |
| No risk — staying in place | 79 backend files + 8 root files | No action required |

---

## 6. Pre-Move Checklist

Execute these steps IN ORDER before running any file moves.

### Step 1 — Archive moves (Phase 1, no prerequisites)
- [ ] Create `docs/archive/` folder
- [ ] Move `_archive/deployment-pipelines.md` → `docs/archive/`
- [ ] Move `_archive/FRAMEWORK-GAPS.md` → `docs/archive/`
- [ ] Move `_archive/gap-register.md` → `docs/archive/`
- [ ] Move `DOC-CATALOGUE.md` (root) → `docs/archive/`
- [ ] Move `REBUILD-PLAN.md` → `docs/archive/`
- [ ] Move `MAPPING-TRACKER.md` → `docs/archive/`
- [ ] Move `CATALOGUE-MERGE-PLAN.md` → `docs/archive/`
- [ ] Vacate `_archive/` (add redirect note or delete)

### Step 2 — U-series moves (Phase 2, no prerequisites)
- [ ] Create `docs/reports/u-series/` folder
- [ ] Move all 27 U-series files (prompt docs + output files) from root
- [ ] After move: update README.md to point to `docs/reports/u-series/DOC_CATALOGUE.md`
- [ ] After move: update SYSTEM-SNAPSHOT.md, COMMERCIALISATION-PLAN.md stale catalogue references (resolves SR-001 through SR-005)

### Step 3 — Refresh SYSTEM-SNAPSHOT.md (prerequisite for Phase 3)
- [ ] Resolve conflicts C-001, C-003, C-005 (see DOC_CONFLICT_REGISTER.md)
- [ ] Update phase status, doc count (78→130), wiring status
- [ ] This is a human task requiring verification of crm-api.js actual DUMMY_MODE state

### Step 4 — Update COMMERCIALISATION-PLAN.md references (prerequisite for Phase 3)
- [ ] Update COMMERCIALISATION-PLAN.md to reference `docs/reports/session/SYSTEM-SNAPSHOT.md`
- [ ] Update COMMERCIALISATION-PLAN.md to reference `docs/reports/session/PENDING.md` and `docs/reports/session/PROGRESS.md` if currently referenced there
- [ ] Resolve internal inconsistency C-002 (RESUME POINT table vs Status header)

### Step 5 — Session report moves (Phase 3)
- [ ] Create `docs/reports/session/` folder
- [ ] Update PROGRESS.md line 8 (SR-006): replace REBUILD-PLAN.md reference with COMMERCIALISATION-PLAN.md
- [ ] Move all 7 session docs to `docs/reports/session/`
- [ ] After move: update README.md links to CHANGELOG.md, PROGRESS.md, PENDING.md, SCREEN-ARTEFACTS.md if found

### Step 6 — Reference doc move (Phase 4)
- [ ] Create `docs/reference/` folder
- [ ] Move `RENDER-DEPLOY.md` → `docs/reference/`
- [ ] After move: update README.md link to `docs/reference/RENDER-DEPLOY.md`

### Step 7 — Human decisions (Phase 5)
- [ ] Decide on `backend/product-spec-gap-register.md` (archive or update)
- [ ] Decide on 3 orphaned backend/docs/domain/ files
- [ ] Decide on `backend/docs/_b9/b9-p08-mobile-responsiveness-system.md`

---

## 7. Post-Move Validation

After each phase, verify:

1. **Tool behavior unchanged:** Start a Claude Code session. Verify CLAUDE.md is loaded (mandatory reading sequence prompt should appear). Verify DESIGN-SPEC.md and FRAMEWORK.md are findable from root.

2. **Session protocol intact:** Follow COMMERCIALISATION-PLAN.md session-open protocol. All referenced files should be findable at their new paths.

3. **No broken links in README.md:** Open README.md and verify all internal links resolve.

4. **backend/ docs untouched:** Run `git status` after each phase. No files under `backend/` should appear as moved.

5. **DOC_CATALOGUE.md updated:** Add entries for any new docs created during the restructuring (docs/archive/README.md redirect if created, etc.).
