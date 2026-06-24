# STALE_LINK_FIX_REPORT.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U5 — Workspace Restructuring Execution)
**Scope:** All reference updates applied during U5 execution, plus unresolved references flagged for human review.

---

## References Fixed

### Fix Group 1 — DOC_CATALOGUE.md new path (resolves SR-001, SR-002, SR-003, SR-004, SR-005)

All references to the old superseded `DOC-CATALOGUE.md` (name and path) were updated to point to the authoritative `docs/reports/u-series/DOC_CATALOGUE.md`.

| # | Source Doc | Old Reference | New Reference | SR Resolved |
|---|---|---|---|---|
| F-001 | `SYSTEM-SNAPSHOT.md` line 18 | `` `DOC-CATALOGUE.md` — master index of every .md file `` | `` `docs/reports/u-series/DOC_CATALOGUE.md` — master index of every .md file `` | SR-001 |
| F-002 | `SYSTEM-SNAPSHOT.md` line 292 | `Every new doc added to DOC-CATALOGUE.md same day it is written` | `Every new doc added to \`docs/reports/u-series/DOC_CATALOGUE.md\` same day it is written` | SR-002 |
| F-003 | `COMMERCIALISATION-PLAN.md` line 61 | `` `DOC-CATALOGUE.md` rule `` | `` `docs/reports/u-series/DOC_CATALOGUE.md` rule `` | SR-003 |
| F-004 | `COMMERCIALISATION-PLAN.md` line 666 | `` `DOC-CATALOGUE.md` \| Master index of all .md files `` | `` `docs/reports/u-series/DOC_CATALOGUE.md` \| Master index of all .md files `` | SR-004 |
| F-005 | `README.md` line 115 | `` └── DOC-CATALOGUE.md  # Full document index `` | `` └── docs/reports/u-series/DOC_CATALOGUE.md  # Full document index (130+ docs) `` | SR-005 (partial) |
| F-006 | `README.md` line 131 | `` [`DOC-CATALOGUE.md`](DOC-CATALOGUE.md) \| Index of all 90+ project documents `` | `` [`docs/reports/u-series/DOC_CATALOGUE.md`](...) \| Index of all 130+ project documents `` | SR-005 (partial) |

---

### Fix Group 2 — SYSTEM-SNAPSHOT.md new path (resolves M-002)

All navigational references to `SYSTEM-SNAPSHOT.md` in the active session protocol were updated to `docs/reports/session/SYSTEM-SNAPSHOT.md`.

| # | Source Doc | Location | Old Reference | New Reference |
|---|---|---|---|---|
| F-007 | `COMMERCIALISATION-PLAN.md` | Line 15 (RESUME POINT) | `` `SYSTEM-SNAPSHOT.md` `` | `` `docs/reports/session/SYSTEM-SNAPSHOT.md` `` |
| F-008 | `COMMERCIALISATION-PLAN.md` | Line 36 (Session protocol step 1) | `` `SYSTEM-SNAPSHOT.md` `` | `` `docs/reports/session/SYSTEM-SNAPSHOT.md` `` |
| F-009 | `COMMERCIALISATION-PLAN.md` | Line 605 (C6 Step 4) | `` `SYSTEM-SNAPSHOT.md` `` | `` `docs/reports/session/SYSTEM-SNAPSHOT.md` `` |
| F-010 | `COMMERCIALISATION-PLAN.md` | Line 612 (C6 Gate) | `` `SYSTEM-SNAPSHOT.md` `` | `` `docs/reports/session/SYSTEM-SNAPSHOT.md` `` |
| F-011 | `COMMERCIALISATION-PLAN.md` | Line 657 (Reference Documents table) | `` `SYSTEM-SNAPSHOT.md` `` | `` `docs/reports/session/SYSTEM-SNAPSHOT.md` `` |

---

### Fix Group 3 — PENDING.md new path (resolves M-004)

| # | Source Doc | Location | Old Reference | New Reference |
|---|---|---|---|---|
| F-012 | `COMMERCIALISATION-PLAN.md` | Line 6 (Task tracker header) | `` `PENDING.md` (root) `` | `` `docs/reports/session/PENDING.md` `` |
| F-013 | `COMMERCIALISATION-PLAN.md` | Line 15 (RESUME POINT) | `` `PENDING.md` Commercialisation section `` | `` `docs/reports/session/PENDING.md` Commercialisation section `` |
| F-014 | `COMMERCIALISATION-PLAN.md` | Line 38 (Session protocol step 3) | `` `PENDING.md` Commercialisation section `` | `` `docs/reports/session/PENDING.md` Commercialisation section `` |
| F-015 | `COMMERCIALISATION-PLAN.md` | Line 43 (Session close step 1) | `` `PENDING.md` `` | `` `docs/reports/session/PENDING.md` `` |
| F-016 | `COMMERCIALISATION-PLAN.md` | Line 606 (C6 Step 4) | `` `PENDING.md` `` | `` `docs/reports/session/PENDING.md` `` |
| F-017 | `COMMERCIALISATION-PLAN.md` | Line 612 (C6 Gate) | `` `PENDING.md` `` | `` `docs/reports/session/PENDING.md` `` |
| F-018 | `COMMERCIALISATION-PLAN.md` | Line 658 (Reference Documents table) | `` `PENDING.md` `` | `` `docs/reports/session/PENDING.md` `` |
| F-019 | `README.md` | Line 113 (Project Structure tree) | `` ├── PENDING.md  # Task checklist — 229 tasks `` | `` ├── docs/reports/session/PENDING.md  # Task checklist `` |

---

### Fix Group 4 — PROGRESS.md new path (resolves M-003 + SR-006)

| # | Source Doc | Location | Old Reference | New Reference |
|---|---|---|---|---|
| F-020 | `COMMERCIALISATION-PLAN.md` | Line 7 (Session log header) | `` `PROGRESS.md` `` | `` `docs/reports/session/PROGRESS.md` `` |
| F-021 | `COMMERCIALISATION-PLAN.md` | Line 46 (Session close step 4) | `` `PROGRESS.md` `` | `` `docs/reports/session/PROGRESS.md` `` |
| F-022 | `COMMERCIALISATION-PLAN.md` | Line 607 (C6 Step 4) | `` `PROGRESS.md` `` | `` `docs/reports/session/PROGRESS.md` `` |
| F-023 | `COMMERCIALISATION-PLAN.md` | Line 659 (Reference Documents table) | `` `PROGRESS.md` `` | `` `docs/reports/session/PROGRESS.md` `` |
| F-024 | `PROGRESS.md` | Line 8 (header anchor) | `` `REBUILD-PLAN.md` — 6 phases, ~21 weeks to 10/10. Task checklist: `PENDING.md` (root). `` | `` `COMMERCIALISATION-PLAN.md` — commercialisation phases C0–C6. Task checklist: `docs/reports/session/PENDING.md`. `` |

Note: F-024 also resolves SR-006 (PROGRESS.md stale reference to REBUILD-PLAN.md).

---

### Fix Group 5 — SCREEN-ARTEFACTS.md new path

| # | Source Doc | Location | Old Reference | New Reference |
|---|---|---|---|---|
| F-025 | `COMMERCIALISATION-PLAN.md` | Line 660 (Reference Documents table) | `` `SCREEN-ARTEFACTS.md` `` | `` `docs/reports/session/SCREEN-ARTEFACTS.md` `` |
| F-026 | `CLAUDE.md` | Line 62 (Current phase section) | `` `D:\CRM\SCREEN-ARTEFACTS.md` `` | `` `D:\CRM\docs\reports\session\SCREEN-ARTEFACTS.md` `` |

Note: F-026 was an undocumented reference discovered during execution. BREAKAGE_RISK_REPORT.md noted "Verify DESIGN-SPEC.md does not link to it by path" but did not check CLAUDE.md. Found and fixed proactively.

---

### Fix Group 6 — CHANGELOG.md new path

| # | Source Doc | Location | Old Reference | New Reference |
|---|---|---|---|---|
| F-027 | `COMMERCIALISATION-PLAN.md` | Line 592 (C6 Step 2) | `` `CHANGELOG.md` `` | `` `docs/reports/session/CHANGELOG.md` `` |

---

### Fix Group 7 — REBUILD-PLAN.md new path (archive)

| # | Source Doc | Location | Old Reference | New Reference |
|---|---|---|---|---|
| F-028 | `README.md` | Line 112 (Project Structure tree) | `` ├── REBUILD-PLAN.md # 10/10 roadmap (6 phases, ~21 weeks) `` | `` ├── docs/archive/REBUILD-PLAN.md   # 10/10 roadmap — SUPERSEDED `` |
| F-029 | `README.md` | Line 125 (Documentation Index table) | `` [`REBUILD-PLAN.md`](REBUILD-PLAN.md) `` | `` [`docs/archive/REBUILD-PLAN.md`](docs/archive/REBUILD-PLAN.md) (SUPERSEDED) `` |
| F-030 | `COMMERCIALISATION-PLAN.md` | Line 656 (Reference Documents table) | `` `REBUILD-PLAN.md` \| CLOSED `` | `` `docs/archive/REBUILD-PLAN.md` \| CLOSED `` |

---

## References NOT Fixed (Acceptable — No Action Required)

These references were found but intentionally left as-is:

| Source Doc | Reference | Reason Not Fixed |
|---|---|---|
| `COMMERCIALISATION-PLAN.md` line 4 | `REBUILD-PLAN.md` is closed — historical note | Explanatory prose; not a navigation link. Contextually correct as written. |
| `COMMERCIALISATION-PLAN.md` line 8 | `Predecessor: REBUILD-PLAN.md` | Predecessor declaration; not navigation. |
| `COMMERCIALISATION-PLAN.md` line 60 | `REBUILD-PLAN.md` — carried forward (rule source) | Source attribution for an inherited rule; not a file navigation link. |
| `COMMERCIALISATION-PLAN.md` line 82 | "inherited state from REBUILD-PLAN.md at closure" | Historical context note; readers will find it in docs/archive/. |
| `COMMERCIALISATION-PLAN.md` line 577 | "assessment from REBUILD-PLAN.md" | C5 instruction to review historical document; readable from docs/archive/. |
| All references inside `docs/archive/` | Various stale references | Archive documents are historical records; internal references are expected to be stale. No fix needed. |

---

## References Flagged for Human Review

None. All navigational references in active authority docs have been resolved.

---

## Total Fix Count

| Category | Count |
|---|---|
| References fixed | 30 edits across 4 documents |
| SR-items resolved | SR-001, SR-002, SR-003, SR-004, SR-005, SR-006 (6 of 12 SRs from DOC_STALE_REFERENCE_REPORT.md) |
| SR-items not fixed (point-in-time snapshots) | SR-007, SR-009, SR-010, SR-011 — acceptable, in archive/snapshot docs |
| SR-items not fixed (need full file refresh) | SR-008 — inside superseded DOC-CATALOGUE.md (now in archive) |
| SR-items not applicable | SR-012 — was already verified correct |
| Undocumented references found and fixed | 1 (F-026: CLAUDE.md line 62) |
