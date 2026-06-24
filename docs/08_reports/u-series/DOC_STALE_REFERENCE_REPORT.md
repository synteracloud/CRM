# DOC_STALE_REFERENCE_REPORT.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U3 — Documentation Normalization)
**Scope:** Stale, broken, or missing references found across the 130 project-owned .md files.

---

## How to read this report

| Column | Meaning |
|---|---|
| ID | Reference identifier (SR-001 onwards) |
| Source Doc | Document containing the stale reference |
| Reference | The specific link, path, or claim that is stale |
| Type | Internal link / File path / Page reference / Version reference / Count reference |
| Status | Fixed / Broken (file missing) / Stale (content changed) / Needs human review |
| Fix Applied | What was done, or why nothing was done |

---

## Stale References

### SR-001 — SYSTEM-SNAPSHOT.md line 18: points to DOC-CATALOGUE.md

| Field | Value |
|---|---|
| **Source Doc** | `SYSTEM-SNAPSHOT.md` line 18 |
| **Reference** | `` > - `DOC-CATALOGUE.md` — master index of every .md file in the project `` |
| **Type** | Internal link |
| **Status** | Stale — DOC-CATALOGUE.md is superseded by DOC_CATALOGUE.md (U2 output) |
| **Fix Applied** | None applied. DOC-CATALOGUE.md still exists (now with SUPERSEDED banner). The reference should be updated to `DOC_CATALOGUE.md` when SYSTEM-SNAPSHOT.md is next refreshed (recommended: refresh SYSTEM-SNAPSHOT.md fully — see DOC_NORMALIZATION_REPORT.md §4.1) |

---

### SR-002 — SYSTEM-SNAPSHOT.md line 292: non-negotiable rule cites DOC-CATALOGUE.md

| Field | Value |
|---|---|
| **Source Doc** | `SYSTEM-SNAPSHOT.md` line 292 |
| **Reference** | `Every new doc added to DOC-CATALOGUE.md same day it is written` |
| **Type** | File path reference (in a process rule) |
| **Status** | Stale — rule should reference `DOC_CATALOGUE.md` (U2 authoritative) |
| **Fix Applied** | None applied. The rule is inside SYSTEM-SNAPSHOT.md's Non-Negotiables table which needs a full refresh. Updating one rule in isolation risks inconsistency with the rest of the stale snapshot. |

---

### SR-003 — COMMERCIALISATION-PLAN.md line 61: non-negotiable rule cites DOC-CATALOGUE.md

| Field | Value |
|---|---|
| **Source Doc** | `COMMERCIALISATION-PLAN.md` line 61 |
| **Reference** | `Every new .md file catalogued in DOC-CATALOGUE.md same day it is written` |
| **Type** | File path reference (in a process rule) |
| **Status** | Stale — rule should reference `DOC_CATALOGUE.md` |
| **Fix Applied** | None applied. COMMERCIALISATION-PLAN.md is the active anchor document; a targeted one-line update is appropriate here, but was not applied because C-002 (RESUME POINT table inconsistency) means the file needs human review before any edits. Fixing rule while leaving C-002 unresolved risks creating a false impression that the file has been reviewed. |

---

### SR-004 — COMMERCIALISATION-PLAN.md line 666: Reference Documents table

| Field | Value |
|---|---|
| **Source Doc** | `COMMERCIALISATION-PLAN.md` line 666 |
| **Reference** | `` `DOC-CATALOGUE.md` — Master index of all .md files `` |
| **Type** | Internal link |
| **Status** | Stale — should reference `DOC_CATALOGUE.md` |
| **Fix Applied** | None applied. Same rationale as SR-003 — defer to human refresh of COMMERCIALISATION-PLAN.md. |

---

### SR-005 — README.md lines 115 and 131: file tree and doc index

| Field | Value |
|---|---|
| **Source Doc** | `README.md` lines 115 and 131 |
| **Reference** | Line 115: `└── DOC-CATALOGUE.md  # Full document index` · Line 131: `[\`DOC-CATALOGUE.md\`](DOC-CATALOGUE.md) \| Index of all 90+ project documents` |
| **Type** | Internal link + Count reference |
| **Status** | Stale — link target should be `DOC_CATALOGUE.md`; count "90+" should be "130" |
| **Fix Applied** | None applied. README.md is a GitHub-facing public document; updating it without verifying other README content is current would risk a partial update. Recommend full README review when SYSTEM-SNAPSHOT.md is refreshed. |

---

### SR-006 — PROGRESS.md line 8: references REBUILD-PLAN.md as active anchor

| Field | Value |
|---|---|
| **Source Doc** | `PROGRESS.md` line 8 |
| **Reference** | `Rebuild plan: REBUILD-PLAN.md — 6 phases, ~21 weeks to 10/10. Task checklist: PENDING.md (root).` |
| **Type** | Internal link |
| **Status** | Stale — REBUILD-PLAN.md is CLOSED and SUPERSEDED; COMMERCIALISATION-PLAN.md is the active anchor |
| **Fix Applied** | None applied. PROGRESS.md is a session-by-session log; the stale header reference is a lower-priority fix that should be done at the next session's log update. |

---

### SR-007 — CURRENT_PROJECT_STATUS.md: "commercialization phase work not started"

| Field | Value |
|---|---|
| **Source Doc** | `CURRENT_PROJECT_STATUS.md` (U0 output, line 173) |
| **Reference** | `6. Commercialization phase — COMMERCIALISATION-PLAN.md exists but work not started` |
| **Type** | Status reference |
| **Status** | Stale — per COMMERCIALISATION-PLAN.md, C0 through C4 are complete (and C5/C6 status is disputed by C-002). CURRENT_PROJECT_STATUS.md was generated as a U0 point-in-time snapshot and correctly reflects the state observed during U0 discovery. |
| **Fix Applied** | None applied. CURRENT_PROJECT_STATUS.md is a U0 report — a snapshot in time. It is not designed to be updated. The stale content is expected and acceptable. Future sessions should read COMMERCIALISATION-PLAN.md (not CURRENT_PROJECT_STATUS.md) for current phase status. |

---

### SR-008 — DOC-CATALOGUE.md "How to use" section: points to REBUILD-PLAN.md for roadmap

| Field | Value |
|---|---|
| **Source Doc** | `DOC-CATALOGUE.md` (now SUPERSEDED) "How to use" table |
| **Reference** | `Understand the roadmap and phase gates → §A → REBUILD-PLAN.md` |
| **Type** | Internal link |
| **Status** | Stale — REBUILD-PLAN.md is CLOSED and SUPERSEDED; COMMERCIALISATION-PLAN.md is the active anchor |
| **Fix Applied** | None applied. DOC-CATALOGUE.md itself has been marked SUPERSEDED (U3 fix applied). This stale reference is now inside a deprecated document and does not need separate correction. The DOC_CATALOGUE.md (U2, authoritative) does not contain this "How to use" navigation issue. |

---

### SR-009 — DOC-CATALOGUE.md scope header: claims 105 active + 3 archived

| Field | Value |
|---|---|
| **Source Doc** | `DOC-CATALOGUE.md` header line 4 |
| **Reference** | `105 active + 0 planned + 3 archived. (Count last verified 2026-05-28)` |
| **Type** | Count reference |
| **Status** | Stale — U2 confirms 130 total docs; 21 new docs added after 2026-05-28 |
| **Fix Applied** | None applied. DOC-CATALOGUE.md has been marked SUPERSEDED (U3 fix applied). Updating the count in a superseded document would be confusing. |

---

### SR-010 — DOC-READ-LOG.md: total count claims 109 docs

| Field | Value |
|---|---|
| **Source Doc** | `DOC-READ-LOG.md` header line 5 |
| **Reference** | `Running total: 105 ✓ / 4 W / 0 ⬜ / 109 total` (last updated 2026-05-31) |
| **Type** | Count reference |
| **Status** | Stale — U2 count is 130 docs; 21 docs added after 2026-05-31 are not logged. Includes: 4 U0 outputs, 7 U1 outputs, 3 U2 outputs, and 7 other files not in DOC-READ-LOG.md. Note: 4 U3 outputs from today (DOC_NORMALIZATION_REPORT.md, DOC_CONFLICT_REGISTER.md, DOC_DUPLICATION_REGISTER.md, DOC_STALE_REFERENCE_REPORT.md) should also be added. |
| **Fix Applied** | None applied. DOC-READ-LOG.md requires adding 21+ [W] entries and updating the running total. This is a manual task — each new entry requires the actual filename to be recorded. See DOC_CONFLICT_REGISTER.md C-006 for the full list of files to add. |

---

### SR-011 — SYSTEM-SNAPSHOT.md doc count: "78 active docs"

| Field | Value |
|---|---|
| **Source Doc** | `SYSTEM-SNAPSHOT.md` lines 55 and 68 |
| **Reference** | "78 active docs in 9 subdirs" and "78 active docs — 55 core spec files + 15 B9 UI specs + 3 QC docs + 3 ADRs + 1 enterprise-depth + 1 gap register" |
| **Type** | Count reference |
| **Status** | Stale — reflects the backend/docs/ subdirectory count as of 2026-05-31. U2 counts 130 total project docs. SYSTEM-SNAPSHOT.md was counting only the backend/docs/ subtree files, not the root-level authority docs, U0/U1/U2 output reports, or tests/. |
| **Fix Applied** | None applied. SYSTEM-SNAPSHOT.md requires a full refresh (see DOC_NORMALIZATION_REPORT.md recommendation). Updating the count in isolation while C-001 and C-003 remain unresolved is not recommended. |

---

### SR-012 — _archive/deployment-pipelines.md: superseded reference target does not match current path

| Field | Value |
|---|---|
| **Source Doc** | `DOC_CATALOGUE.md` §B (Archive section) |
| **Reference** | States "_archive/deployment-pipelines.md is Superseded by `backend/docs/infrastructure/runtime-deployment.md`" |
| **Type** | File path reference |
| **Status** | Verified correct — `backend/docs/infrastructure/runtime-deployment.md` exists and is Active per DOC_CATALOGUE.md §L. The supersession reference is accurate. |
| **Fix Applied** | No fix needed — reference is correct. Logged here for completeness to confirm the archive chain is valid. |

---

## Files with No Broken References (verified clean)

The following files were checked for cross-references and found to have no stale or broken links:

| File | Checked for | Result |
|---|---|---|
| `backend/docs/infrastructure/runtime-deployment.md` | Supersedes `_archive/deployment-pipelines.md` | Clean — superseded file confirmed in `_archive/` |
| `COMMERCIALISATION-PLAN.md` §Reference Documents table | All 12 referenced files | All 12 files confirmed present in repository |
| `DESIGN-SPEC.md` | References to b9-p spec files (§5 archetype quick ref) | All 15 b9-p files confirmed in `backend/docs/_b9/` |
| `FRAMEWORK.md` | References to b9-p specs, crm-custom.css, crm-shell.js | Referenced files confirmed in `frontend/src/assets/` |
| `CLAUDE.md` | References to DESIGN-SPEC.md, FRAMEWORK.md, crm-custom.css, crm-shell.js | All confirmed present |
| `backend/docs/phase4-gap-register.md` | A-006 and A-007 (Redis, FeatureFlag) — referenced as C3 targets | Noted as addressed in C3 per COMMERCIALISATION-PLAN.md |
| `_archive/FRAMEWORK-GAPS.md` | Superseded by inline FRAMEWORK.md annotations | FRAMEWORK.md confirmed active at 3401 lines |
| `_archive/gap-register.md` | Superseded by `backend/docs/phase4-gap-register.md` + `BACKEND-QC.md` | Both files confirmed present |
