# WORKSPACE_RESTRUCTURING_PLAN.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U4 — Workspace Restructuring Plan)
**Inputs:** REPOSITORY_TREE_INVENTORY.md, DOC_CATALOGUE.md, DOCUMENT_CLASSIFICATION_MATRIX.md, DOCUMENT_OWNERSHIP_MATRIX.md, DOC_NORMALIZATION_REPORT.md, DOC_CONFLICT_REGISTER.md, DOC_DUPLICATION_REGISTER.md, DOC_STALE_REFERENCE_REPORT.md, WORKSPACE_BASELINE_AUDIT.md
**Status:** Planning only — NO files have been moved or modified.

---

## 1. Current State Problems

### Problem 1 — Root is swamped with 42 .md files

The repository root currently holds 42 project-owned .md files. A developer opening the repo sees `CLAUDE.md` (the mandatory session protocol) alongside `API_INVENTORY.md` (a discovery report), `CATALOGUE-MERGE-PLAN.md` (a completed and abandoned plan), and `DOC_DUPLICATION_REGISTER.md` (an internal audit output) — all at the same level, with no visual hierarchy to distinguish them.

**Expected state:** Root should hold ~8 active authority docs plus config files. All other .md files should be one level deep in a named folder.

### Problem 2 — U-series discovery outputs (27 files) are scattered at root

The U0, U1, U2, U3, and U4 discovery passes produced 27 output files that now sit at root alongside authority docs like `CLAUDE.md` and `FRAMEWORK.md`. These outputs are reference material and evidence archives, not session-critical documents. They inflate root and make authority docs harder to find.

### Problem 3 — Session reports are mixed with authority docs

`CHANGELOG.md`, `PROGRESS.md`, `PENDING.md`, `SESSION-HANDOFF.md`, `SYSTEM-SNAPSHOT.md`, `SCREEN-ARTEFACTS.md`, and `DOC-READ-LOG.md` are all session-maintenance docs that belong together. They currently sit at root alongside `DESIGN-SPEC.md` and `FRAMEWORK.md`, making it unclear which docs are governance and which are status updates.

### Problem 4 — Superseded and completed docs are not archived

Four root-level docs are either superseded or have no ongoing value:
- `DOC-CATALOGUE.md` — marked SUPERSEDED (U3 fix applied); replaced by `DOC_CATALOGUE.md`
- `REBUILD-PLAN.md` — marked SUPERSEDED and CLOSED; replaced by `COMMERCIALISATION-PLAN.md`
- `MAPPING-TRACKER.md` — marked COMPLETE (2026-05-27); no ongoing value
- `CATALOGUE-MERGE-PLAN.md` — marked COMPLETE (2026-05-22); no ongoing value

These should be in an archive folder, not at root alongside active docs.

### Problem 5 — `_archive/` is underused and named awkwardly

The existing `_archive/` folder at root holds only 3 files. Its underscore prefix gives it a "hidden" feel (like `.git` or `.npm-cache`). The 4 superseded root docs listed in Problem 4 should have gone here already but did not.

### Problem 6 — `backend/docs/` subtree is already well-organized

The `backend/docs/` directory tree (71 files across 9 subdirectories: `_b9/`, `_qc/`, `adapters/`, `adr/`, `architecture/`, `domain/`, `infrastructure/`, `product/`, `security/`, `ui/`) is properly organized and should NOT be touched. The problem is entirely at the root layer.

---

## 2. What Stays at Root

The following files must remain at root after restructuring. Do not move them.

| File | Why it stays |
|---|---|
| `CLAUDE.md` | Claude Code loads this automatically from project root. Hardcoded tool behavior. Cannot move. |
| `README.md` | GitHub convention: must be at root for repo landing page. |
| `CONTRIBUTING.md` | GitHub convention: developer onboarding doc lives at root. |
| `DESIGN-SPEC.md` | Mandatory step 1 in CLAUDE.md 5-step reading sequence. Moving it requires updating CLAUDE.md — highest breakage risk. Authority doc; must be prominent. |
| `FRAMEWORK.md` | Mandatory step 2 in CLAUDE.md reading sequence. Same risk as DESIGN-SPEC.md. |
| `PAGE-BUILD-PROTOCOL.md` | Referenced in CLAUDE.md reading sequence ("read before every page build"). |
| `COMMERCIALISATION-PLAN.md` | Active session anchor. Every session starts by reading the RESUME POINT table. Moving would break the session-open protocol. |
| `PRODUCT-SPEC.md` | Core product identity document (1022 lines); frequently referenced. Key authority doc per design principles. |
| `render.yaml` | Render.com IaC config — must be at root for Render Blueprint deploy. |
| `Makefile` | Build/dev task runner — root-level convention. |
| `seal.ps1` | Utility script — non-documentation, stays at root. |
| `.pre-commit-config.yaml` | Pre-commit hook config — root-level convention. |
| `.gitignore`, `.env.local`, log files | Runtime and config files — root-level convention. |

---

## 3. Proposed Folder Hierarchy

```
D:\SaaS\CRM\
│
├── CLAUDE.md                                  [STAYS — tool-loaded authority]
├── README.md                                  [STAYS — GitHub landing page]
├── CONTRIBUTING.md                            [STAYS — convention]
├── DESIGN-SPEC.md                             [STAYS — mandatory reading sequence]
├── FRAMEWORK.md                               [STAYS — mandatory reading sequence]
├── PAGE-BUILD-PROTOCOL.md                     [STAYS — mandatory reading sequence]
├── COMMERCIALISATION-PLAN.md                  [STAYS — active session anchor]
├── PRODUCT-SPEC.md                            [STAYS — core product identity]
│
├── docs/
│   │
│   ├── reference/                             [NEW — active reference docs with no root dependency]
│   │   └── RENDER-DEPLOY.md                   [MOVED from root]
│   │
│   ├── reports/
│   │   │
│   │   ├── session/                           [NEW — session-maintenance docs]
│   │   │   ├── CHANGELOG.md                   [MOVED from root]
│   │   │   ├── PROGRESS.md                    [MOVED from root]
│   │   │   ├── PENDING.md                     [MOVED from root]
│   │   │   ├── SESSION-HANDOFF.md             [MOVED from root]
│   │   │   ├── SYSTEM-SNAPSHOT.md             [MOVED from root]
│   │   │   ├── SCREEN-ARTEFACTS.md            [MOVED from root]
│   │   │   └── DOC-READ-LOG.md                [MOVED from root]
│   │   │
│   │   └── u-series/                          [NEW — all U-pass prompts and outputs]
│   │       │
│   │       ├── [Prompt docs]
│   │       ├── U0 — REPOSITORY REALITY DISCOVERY.md
│   │       ├── U1 — AUTHORITY RECONSTRUCTION.md
│   │       ├── U2 — DOCUMENTATION CATALOGUE.md
│   │       ├── U3 — DOCUMENTATION NORMALIZATION.md
│   │       ├── U4 — WORKSPACE RESTRUCTURING PLAN.md
│   │       │
│   │       ├── [U0 outputs — discovery]
│   │       ├── WORKSPACE_BASELINE_AUDIT.md
│   │       ├── REPOSITORY_REALITY_REPORT.md
│   │       ├── REPOSITORY_TREE_INVENTORY.md
│   │       ├── CURRENT_PROJECT_STATUS.md
│   │       │
│   │       ├── [U1 outputs — authority reconstruction]
│   │       ├── AUTHORITY_RECONSTRUCTION_REPORT.md
│   │       ├── FEATURE_INVENTORY.md
│   │       ├── MODULE_INVENTORY.md
│   │       ├── ENTITY_INVENTORY.md
│   │       ├── WORKFLOW_INVENTORY.md
│   │       ├── ROLE_PERMISSION_INVENTORY.md
│   │       ├── API_INVENTORY.md
│   │       │
│   │       ├── [U2 outputs — doc catalogue]
│   │       ├── DOC_CATALOGUE.md
│   │       ├── DOCUMENT_CLASSIFICATION_MATRIX.md
│   │       ├── DOCUMENT_OWNERSHIP_MATRIX.md
│   │       │
│   │       ├── [U3 outputs — normalization]
│   │       ├── DOC_NORMALIZATION_REPORT.md
│   │       ├── DOC_CONFLICT_REGISTER.md
│   │       ├── DOC_DUPLICATION_REGISTER.md
│   │       ├── DOC_STALE_REFERENCE_REPORT.md
│   │       │
│   │       └── [U4 outputs — restructuring plan]
│   │           ├── WORKSPACE_RESTRUCTURING_PLAN.md
│   │           ├── FILE_RELOCATION_MATRIX.md
│   │           ├── FOLDER_PURPOSE_MATRIX.md
│   │           └── BREAKAGE_RISK_REPORT.md
│   │
│   └── archive/                               [NEW — superseded + completed docs]
│       ├── DOC-CATALOGUE.md                   [MOVED from root — SUPERSEDED]
│       ├── REBUILD-PLAN.md                    [MOVED from root — SUPERSEDED]
│       ├── MAPPING-TRACKER.md                 [MOVED from root — COMPLETE]
│       ├── CATALOGUE-MERGE-PLAN.md            [MOVED from root — COMPLETE]
│       ├── deployment-pipelines.md            [MOVED from _archive/]
│       ├── FRAMEWORK-GAPS.md                  [MOVED from _archive/]
│       └── gap-register.md                    [MOVED from _archive/]
│
├── _archive/                                  [VACATED — contents moved to docs/archive/]
│                                              Delete or keep empty with a redirect note.
│
├── backend/                                   [UNCHANGED — entire tree stays as-is]
│   ├── BACKEND-QC.md                          [STAYS — contextually tied to backend/]
│   ├── CONSTRAINTS.md                         [STAYS — backend-specific constraints]
│   ├── FRONTEND-BACKEND-MAPPING.md            [STAYS — belongs with backend context]
│   ├── PENDING.md                             [STAYS — backend-specific pending items]
│   ├── market-research-gap-register.md        [STAYS — active market research]
│   ├── product-spec-gap-register.md           [STAYS — human decision pending on archival]
│   ├── README.md                              [STAYS — backend onboarding]
│   ├── db/                                    [UNCHANGED]
│   ├── gateway/                               [UNCHANGED]
│   └── docs/                                  [UNCHANGED — 71 files, 9 subdirs]
│       ├── _b9/     (15 archetype specs)
│       ├── _qc/     (3 QC logs)
│       ├── adapters/ (5 docs)
│       ├── adr/     (3 ADRs)
│       ├── architecture/ (5 docs)
│       ├── domain/  (21 docs)
│       ├── infrastructure/ (15 docs)
│       ├── product/ (4 docs)
│       ├── security/ (3 docs)
│       └── ui/      (3 docs)
│
├── frontend/                                  [UNCHANGED]
└── tests/                                     [UNCHANGED]
    └── e2e/playwright/SKIP-BACKLOG.md         [STAYS — belongs with test suite]
```

---

## 4. Design Rationale for Each Folder

### `docs/reference/`

**Purpose:** Active reference docs that are consulted during work but are not part of the mandatory session-open reading sequence and have no hardcoded tool dependency that requires root placement.

**Current candidate:** `RENDER-DEPLOY.md` (deployment guide — actively referenced, but not required to be at root). Future candidates: any new how-to guide, runbook, or reference document that does not need to be in CLAUDE.md's reading sequence.

**Why not merge with backend/docs/:** The backend/docs/ subtree is organized by technical domain (architecture, domain, infrastructure, etc.). Root-level reference docs serve a different audience (DevOps, general developer) and a different lifecycle (deployment instructions, operational guides).

### `docs/reports/session/`

**Purpose:** Session-maintenance docs — documents that are written and updated during build sessions to track progress, hand off state, record QC sign-offs, and log what was read. These are produced and consumed by Claude during active sessions. They are NOT authority documents (they don't govern how work is done) and NOT discovery reports (they don't inventory the codebase). They are operational logs.

**Files:** `CHANGELOG.md`, `PROGRESS.md`, `PENDING.md` (root), `SESSION-HANDOFF.md`, `SYSTEM-SNAPSHOT.md`, `SCREEN-ARTEFACTS.md`, `DOC-READ-LOG.md`.

**Important note on SYSTEM-SNAPSHOT.md:** COMMERCIALISATION-PLAN.md references SYSTEM-SNAPSHOT.md in the session-open protocol. Moving it requires updating that reference in COMMERCIALISATION-PLAN.md. This must be done before or simultaneously with the move.

### `docs/reports/u-series/`

**Purpose:** All U-pass process prompts and their output files. The U-series (U0 through U4 and beyond) is a structured discovery methodology. Its outputs are evidence archives — they document what was found at a point in time, not what should be done. They are not authority docs and should not sit at root.

**Naming convention:** All U-series outputs retain their exact filenames. The `U0 — REPOSITORY REALITY DISCOVERY.md` naming convention (with em-dash) is preserved. No renaming required.

**Why a dedicated subfolder rather than docs/reports/ directly:** The U-series will continue to grow with future U-passes. A dedicated subfolder groups them by methodology, making it easy to find all outputs from a given pass (e.g., "what did U1 produce?").

### `docs/archive/`

**Purpose:** Superseded, closed, and completed docs retained for audit trail. These documents contain historical value but must NOT be consulted for current guidance.

**Replaces:** The existing `_archive/` folder at root. Contents of `_archive/` are consolidated here. The `_archive/` folder at root can be vacated (kept empty with a README redirect, or deleted).

**Archive organization:** Single flat folder — no date-based sub-organization needed at current scale (10 files). If the archive grows beyond 20 files in a future phase, sub-organize by year (e.g., `docs/archive/2026/`).

**Admission criteria for docs/archive/:**
1. Docs marked SUPERSEDED (have a formal replacement)
2. Docs marked COMPLETE with no ongoing reference value
3. Docs marked CLOSED
4. Orphaned docs confirmed to have no active use (human decision required)

---

## 5. Migration Phases

### Phase 1 — Archive and Vacate (lowest risk, do first)

**What:** Move the contents of `_archive/` to `docs/archive/`. Move the 4 superseded/completed root docs to `docs/archive/`.

**Files:**
- `_archive/deployment-pipelines.md` → `docs/archive/deployment-pipelines.md`
- `_archive/FRAMEWORK-GAPS.md` → `docs/archive/FRAMEWORK-GAPS.md`
- `_archive/gap-register.md` → `docs/archive/gap-register.md`
- `DOC-CATALOGUE.md` (root, SUPERSEDED) → `docs/archive/DOC-CATALOGUE.md`
- `REBUILD-PLAN.md` (SUPERSEDED) → `docs/archive/REBUILD-PLAN.md`
- `MAPPING-TRACKER.md` (COMPLETE) → `docs/archive/MAPPING-TRACKER.md`
- `CATALOGUE-MERGE-PLAN.md` (COMPLETE) → `docs/archive/CATALOGUE-MERGE-PLAN.md`

**Risk:** Low. All these files are superseded or inactive. No authority doc references them for current guidance.

**Post-move action:** Vacate or remove `_archive/`. If keeping it empty, add a `_archive/README.md` with one line: "Contents moved to docs/archive/ (2026-06-20 restructuring).".

---

### Phase 2 — Move U-Series Outputs (low risk)

**What:** Create `docs/reports/u-series/` and move all U-pass prompts and output files from root.

**Files:** All 27 U-series files (5 prompt docs + 4 U0 outputs + 7 U1 outputs + 3 U2 outputs + 4 U3 outputs + 4 U4 outputs).

**Risk:** Low. These files are not referenced by path from CLAUDE.md, DESIGN-SPEC.md, FRAMEWORK.md, or COMMERCIALISATION-PLAN.md. They are referenced by name in README.md and DOC-READ-LOG.md but those references are text mentions, not clickable hyperlinks with explicit paths.

**Post-move action:** Update README.md doc index to point to `docs/reports/u-series/DOC_CATALOGUE.md` as the authoritative catalogue (resolves SR-005 from DOC_STALE_REFERENCE_REPORT.md).

---

### Phase 3 — Move Session Reports (medium risk — update references first)

**What:** Create `docs/reports/session/` and move 7 session-maintenance docs.

**Pre-move required:** Update `COMMERCIALISATION-PLAN.md` to reference `docs/reports/session/SYSTEM-SNAPSHOT.md` rather than bare `SYSTEM-SNAPSHOT.md` (resolves SR-001, SR-002 in context). This must happen before the move.

**Files:** `CHANGELOG.md`, `PROGRESS.md`, `PENDING.md`, `SESSION-HANDOFF.md`, `SYSTEM-SNAPSHOT.md`, `SCREEN-ARTEFACTS.md`, `DOC-READ-LOG.md`.

**Risk:** Medium. `SYSTEM-SNAPSHOT.md` is referenced by COMMERCIALISATION-PLAN.md in the session-open protocol. `SCREEN-ARTEFACTS.md` may be referenced by name in DESIGN-SPEC.md or CLAUDE.md. Update all references before moving. See BREAKAGE_RISK_REPORT.md for full dependency map.

---

### Phase 4 — Move Reference Docs (low risk)

**What:** Create `docs/reference/` and move `RENDER-DEPLOY.md`.

**Files:** `RENDER-DEPLOY.md`.

**Post-move action:** Update the link in README.md from `RENDER-DEPLOY.md` to `docs/reference/RENDER-DEPLOY.md`.

**Risk:** Low. RENDER-DEPLOY.md is not in the mandatory session reading sequence. The only breakage is a README.md link update.

---

### Phase 5 — Human Decisions (require confirmation before acting)

**What:** Review and decide on 5 orphaned/candidate-for-archive docs.

**Decisions required:**
1. `backend/product-spec-gap-register.md` — are all gaps resolved? If yes, move to `docs/archive/`. If not, surface open items in `PENDING.md`.
2. `backend/docs/domain/enterprise-depth.md` — is this actively consulted? If yes, add explicit cross-reference from `backend/docs/architecture/architecture-overview.md`. If no, move to `docs/archive/`.
3. `backend/docs/domain/data-governance-ownership.md` — clarify relationship with `data-governance-layer.md`. Add companion cross-reference or merge.
4. `backend/docs/_b9/b9-p08-mobile-responsiveness-system.md` — add cross-reference from FRAMEWORK.md §31 if still consulted, or archive.
5. `SYSTEM-SNAPSHOT.md` (already proposed to move) — requires a full content refresh before moving: update C-phase status, doc count, and wiring status (see DOC_NORMALIZATION_REPORT.md §5).

---

## 6. Governance Rules Going Forward

### Rule G-01 — Root admission policy

Only the following categories of files may live at root:
- Config files: render.yaml, Makefile, seal.ps1, .pre-commit-config.yaml, .gitignore, .env.local
- Runtime logs: gateway_startup.log, gateway_err.log, gw.log
- Authority docs in the CLAUDE.md mandatory reading sequence: CLAUDE.md, DESIGN-SPEC.md, FRAMEWORK.md, PAGE-BUILD-PROTOCOL.md, COMMERCIALISATION-PLAN.md
- Standard GitHub convention: README.md, CONTRIBUTING.md
- Core product identity: PRODUCT-SPEC.md

All other .md files go into `docs/` sub-folders on creation. No exceptions without explicit approval.

### Rule G-02 — U-series output placement

All future U-pass prompt docs and their outputs are created directly in `docs/reports/u-series/`. They are never created at root. Naming convention: uppercase snake-case for outputs (e.g., `MODULE_INVENTORY.md`), existing "U# — TITLE.md" format retained for prompt docs.

### Rule G-03 — Session report placement

Session-maintenance docs (`PROGRESS.md`, `PENDING.md`, `SESSION-HANDOFF.md`, `SYSTEM-SNAPSHOT.md`, `CHANGELOG.md`, etc.) live in `docs/reports/session/`. When COMMERCIALISATION-PLAN.md is next updated, update its "read first" references to include the `docs/reports/session/` prefix.

### Rule G-04 — Archive admission

A doc enters `docs/archive/` when it meets any of these criteria:
- Marked SUPERSEDED with a named replacement doc
- Task/plan marked COMPLETE with no further reference value
- Marked CLOSED
- Confirmed orphaned (no active inbound references from Authority or Reference docs)

Adding to archive does not require a separate decision — it can be done by Claude during sessions when the criteria are met. Removal from archive requires human approval.

### Rule G-05 — DOC_CATALOGUE.md is the master catalogue

`docs/reports/u-series/DOC_CATALOGUE.md` is the authoritative document index. When any new .md file is created, it must be added to DOC_CATALOGUE.md in the same session. The old `DOC-CATALOGUE.md` (now in docs/archive/) must never be updated.

### Rule G-06 — backend/docs/ is stable

The `backend/docs/` subtree is not touched by documentation restructuring operations. Any new backend technical docs go into their existing sub-category (domain, infrastructure, security, etc.) following the existing naming conventions.

### Rule G-07 — Naming conventions by folder

| Folder | Convention |
|---|---|
| Root authority docs | SCREAMING-KEBAB-CASE.md (e.g., DESIGN-SPEC.md) |
| docs/reference/ | SCREAMING-KEBAB-CASE.md |
| docs/reports/session/ | SCREAMING-KEBAB-CASE.md |
| docs/reports/u-series/ prompts | "U# — TITLE.md" (em-dash, space-padded) |
| docs/reports/u-series/ outputs | SCREAMING_SNAKE_CASE.md (e.g., API_INVENTORY.md) |
| docs/archive/ | Preserve original filename (no renaming) |
| backend/docs/ | kebab-case.md (existing convention) |

---

## 7. Root State: Before and After

### Before (42 .md files at root)

```
CLAUDE.md, COMMERCIALISATION-PLAN.md, CONTRIBUTING.md, DESIGN-SPEC.md, FRAMEWORK.md,
PAGE-BUILD-PROTOCOL.md, PRODUCT-SPEC.md, README.md, RENDER-DEPLOY.md,
CHANGELOG.md, SCREEN-ARTEFACTS.md, SESSION-HANDOFF.md, PENDING.md, PROGRESS.md,
SYSTEM-SNAPSHOT.md, REBUILD-PLAN.md, MAPPING-TRACKER.md, DOC-CATALOGUE.md,
DOC-READ-LOG.md, CATALOGUE-MERGE-PLAN.md,
U0 — REPOSITORY REALITY DISCOVERY.md, U1 — AUTHORITY RECONSTRUCTION.md,
U2 — DOCUMENTATION CATALOGUE.md, U3 — DOCUMENTATION NORMALIZATION.md,
U4 — WORKSPACE RESTRUCTURING PLAN.md, WORKSPACE_BASELINE_AUDIT.md,
REPOSITORY_REALITY_REPORT.md, REPOSITORY_TREE_INVENTORY.md, CURRENT_PROJECT_STATUS.md,
AUTHORITY_RECONSTRUCTION_REPORT.md, FEATURE_INVENTORY.md, MODULE_INVENTORY.md,
ENTITY_INVENTORY.md, WORKFLOW_INVENTORY.md, ROLE_PERMISSION_INVENTORY.md,
API_INVENTORY.md, DOC_CATALOGUE.md, DOCUMENT_CLASSIFICATION_MATRIX.md,
DOCUMENT_OWNERSHIP_MATRIX.md, DOC_NORMALIZATION_REPORT.md, DOC_CONFLICT_REGISTER.md,
DOC_DUPLICATION_REGISTER.md, DOC_STALE_REFERENCE_REPORT.md,
WORKSPACE_RESTRUCTURING_PLAN.md, FILE_RELOCATION_MATRIX.md,
FOLDER_PURPOSE_MATRIX.md, BREAKAGE_RISK_REPORT.md
```

### After (8 .md files at root)

```
CLAUDE.md, README.md, CONTRIBUTING.md,
DESIGN-SPEC.md, FRAMEWORK.md, PAGE-BUILD-PROTOCOL.md,
COMMERCIALISATION-PLAN.md, PRODUCT-SPEC.md
```

**Reduction: 42 → 8 root .md files (81% reduction)**

All moved files are findable at:
- `docs/reference/` — 1 file
- `docs/reports/session/` — 7 files
- `docs/reports/u-series/` — 31 files (27 current + 4 U4 outputs)
- `docs/archive/` — 10 files
- `backend/` subtree — unchanged (79 files)
- `tests/` subtree — unchanged (1 file)
