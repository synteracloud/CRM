# FOLDER_PURPOSE_MATRIX.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U4 — Workspace Restructuring Plan)
**Status:** Planning only — folders and files have not been created or moved.
**Companion doc:** WORKSPACE_RESTRUCTURING_PLAN.md (full rationale), FILE_RELOCATION_MATRIX.md (per-file moves)

---

## How to read this matrix

Each row describes one folder in the proposed structure. Folders that are part of the existing `backend/docs/` subtree are listed as a group — they are unchanged and described for reference only.

---

## Root (D:\SaaS\CRM\)

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\` (root) |
| **Purpose** | Repository root. Holds mandatory tool files, GitHub convention files, top-level config, and the small set of authority docs that must be immediately visible or that are hardcoded into Claude Code's loading behavior. |
| **Who Owns It** | Project Lead (authority docs), Developer (config files), DevOps (deploy config) |
| **Naming Convention** | SCREAMING-KEBAB-CASE.md for authority docs (e.g., DESIGN-SPEC.md). Config files follow their own conventions (.gitignore, render.yaml, etc.). |
| **What Belongs Here** | CLAUDE.md, README.md, CONTRIBUTING.md, DESIGN-SPEC.md, FRAMEWORK.md, PAGE-BUILD-PROTOCOL.md, COMMERCIALISATION-PLAN.md, PRODUCT-SPEC.md. Config files: render.yaml, Makefile, seal.ps1, .pre-commit-config.yaml, .gitignore, .env.local. Runtime logs: gateway_startup.log, gateway_err.log, gw.log. |
| **What Does NOT Belong Here** | Session reports (PROGRESS.md, PENDING.md, SYSTEM-SNAPSHOT.md, etc.), U-series outputs (API_INVENTORY.md, DOC_CATALOGUE.md, etc.), superseded docs (REBUILD-PLAN.md, DOC-CATALOGUE.md), completed trackers (MAPPING-TRACKER.md, CATALOGUE-MERGE-PLAN.md), deployment runbooks (RENDER-DEPLOY.md). |
| **Target File Count** | 8 .md files (down from 42) |

---

## docs/

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\docs\` |
| **Purpose** | Top-level container for all project documentation that does not need to be at root. Acts as the documentation root for: reference material, generated reports, and archived content. Contains only subfolders — no files should be placed directly in docs/ itself. |
| **Who Owns It** | No single owner — each subfolder has its own owner. |
| **Naming Convention** | Subfolders only. Subfolders are lowercase with no prefix. |
| **What Belongs Here** | Subfolders: reference/, reports/, archive/. Nothing else. |
| **What Does NOT Belong Here** | Individual .md files placed directly at docs/ level. All files must go into a named subfolder. |

---

## docs/reference/

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\docs\reference\` |
| **Purpose** | Active reference documents that are consulted during work but do not belong in the mandatory CLAUDE.md reading sequence and have no hardcoded tool dependency requiring root placement. Contains how-to guides, runbooks, and operational guides. |
| **Who Owns It** | DevOps (deployment docs), Developer (technical how-tos) |
| **Naming Convention** | SCREAMING-KEBAB-CASE.md (consistent with root authority docs). Example: RENDER-DEPLOY.md. |
| **What Belongs Here** | RENDER-DEPLOY.md (deployment guide). Future additions: any new operational runbook, how-to guide, or reference doc that does not need to be in the CLAUDE.md reading sequence. |
| **What Does NOT Belong Here** | Authority docs in the CLAUDE.md reading sequence (those stay at root). Domain specs, ADRs, and architecture docs (those belong in backend/docs/). Discovery/inventory reports (those belong in docs/reports/u-series/). |
| **Initial File Count** | 1 (RENDER-DEPLOY.md) |

---

## docs/reports/

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\docs\reports\` |
| **Purpose** | Container for all generated reports. Contains subfolders organized by report type. No files placed directly here — all files go into session/ or u-series/ subfolders. |
| **Who Owns It** | Claude/AI (reports are generated) |
| **Naming Convention** | Subfolders only. |
| **What Belongs Here** | Subfolders: session/, u-series/. Nothing else. |
| **What Does NOT Belong Here** | Individual files. Files from backend/docs/ (backend reports stay in backend/ tree). |

---

## docs/reports/session/

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\docs\reports\session\` |
| **Purpose** | Session-maintenance documents. These are created and updated during build sessions to track progress, record QC sign-offs, log state for handoffs, and maintain continuity across sessions. They are not authority docs (they don't govern how work is done) and not discovery reports (they don't inventory the codebase). They are operational records of what happened. |
| **Who Owns It** | Claude/AI (documents are written and updated during sessions), QA/Claude (QC records like SCREEN-ARTEFACTS.md) |
| **Naming Convention** | SCREAMING-KEBAB-CASE.md. Consistent with existing filenames (PROGRESS.md, PENDING.md, etc.). No renaming of existing files. |
| **What Belongs Here** | CHANGELOG.md (version history), PROGRESS.md (build tracker), PENDING.md (task checklist), SESSION-HANDOFF.md (session handoff state), SYSTEM-SNAPSHOT.md (60-second system state), SCREEN-ARTEFACTS.md (QC sign-off records), DOC-READ-LOG.md (cross-session read continuity log). Future: any new per-session status or tracking doc. |
| **What Does NOT Belong Here** | U-series discovery outputs (those go in u-series/). Authority docs (those go at root or in backend/docs/). Backend-specific docs (backend/PENDING.md, backend/BACKEND-QC.md stay in backend/). |
| **Initial File Count** | 7 |

---

## docs/reports/u-series/

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\docs\reports\u-series\` |
| **Purpose** | All U-pass process prompt documents and their output files. The U-series is a structured discovery and normalization methodology (U0 = Discovery, U1 = Authority Reconstruction, U2 = Documentation Catalogue, U3 = Normalization, U4 = Restructuring, and future passes). This folder groups all outputs by methodology, making it easy to answer "what did U1 produce?" or "where is the current canonical catalogue?" |
| **Who Owns It** | Claude/AI (all outputs are generated), Project Lead (prompt docs are authored by Project Lead) |
| **Naming Convention** | Two conventions in use, both preserved: (1) Process prompt docs: "U# — TITLE.md" format with em-dash and space padding, e.g., `U0 — REPOSITORY REALITY DISCOVERY.md`. (2) Output files: SCREAMING_SNAKE_CASE.md, e.g., `API_INVENTORY.md`, `DOC_CATALOGUE.md`. No renaming of existing files. |
| **What Belongs Here** | U-pass prompt docs (U0 through U4 and future passes). All output files generated by each U-pass. The master catalogue (DOC_CATALOGUE.md) lives here. |
| **What Does NOT Belong Here** | Session docs (those go in session/). Archive content (goes in archive/). Authority docs (stay at root or backend/docs/). |
| **Initial File Count** | 31 (5 prompt docs + 4 U0 outputs + 7 U1 outputs + 3 U2 outputs + 4 U3 outputs + 4 U4 outputs) |
| **Note on DOC_CATALOGUE.md** | The authoritative project document catalogue (`DOC_CATALOGUE.md`) lives in this folder after the restructuring. Any reference to it must use the path `docs/reports/u-series/DOC_CATALOGUE.md`. |

---

## docs/archive/

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\docs\archive\` |
| **Purpose** | Superseded, closed, and completed documents retained for historical audit trail. These documents must NOT be consulted for current guidance. They exist only as a record of what was decided, planned, or built at a past point in time. |
| **Who Owns It** | No active owner — documents here have no current maintainer. Admission is managed by any team member or Claude. Removal requires human approval. |
| **Naming Convention** | Preserve original filename exactly. Do not rename files when archiving — the original name is part of the historical record. |
| **What Belongs Here** | Docs marked SUPERSEDED with a named replacement. Docs marked CLOSED. Plans or trackers marked COMPLETE with no ongoing reference value. Docs confirmed as orphaned after human review. The three files currently in `_archive/` at root (deployment-pipelines.md, FRAMEWORK-GAPS.md, gap-register.md). |
| **What Does NOT Belong Here** | Active docs of any kind. Docs that are stale but still referenced (stale != archived). Docs pending human decision (they stay in place until decided). |
| **Initial File Count** | 10 (3 from _archive/ + 4 superseded/complete root docs + 3 others that already have SUPERSEDED banners) |
| **Organization** | Flat single folder at current scale (10 files). If archive exceeds 20 files in a future phase, sub-organize by year (docs/archive/2026/). |
| **Replaces** | `_archive/` at root. The `_archive/` folder at root should be vacated after its 3 files move here. |

---

## _archive/ (VACATED)

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\_archive\` (existing) |
| **Purpose** | Existing archive folder — to be vacated. Contents move to docs/archive/. |
| **Post-restructuring state** | Empty, or kept with a single `_archive/README.md` that says: "Contents of this folder were moved to docs/archive/ during the 2026-06-20 workspace restructuring. See docs/archive/ for all archived documents." If truly empty, can be deleted (note: git will not track an empty folder). |

---

## backend/ (UNCHANGED)

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\backend\` |
| **Purpose** | Python FastAPI services, Node.js API gateway, database schemas, migration files, adapter layer, and backend documentation. All backend code and backend-specific documentation lives here. |
| **Who Owns It** | Developer (code and specs), QA/Claude (QC reports), DevOps (deployment) |
| **Naming Convention** | Backend root .md files: SCREAMING-KEBAB-CASE.md (BACKEND-QC.md, CONSTRAINTS.md, etc.). Backend docs: kebab-case.md (existing convention in backend/docs/). |
| **What Belongs Here** | All Python source, Node.js gateway, DB schemas, Alembic migrations, adapter layer, backend/ root .md files (README.md, BACKEND-QC.md, CONSTRAINTS.md, FRONTEND-BACKEND-MAPPING.md, PENDING.md, market-research-gap-register.md, product-spec-gap-register.md). The entire backend/docs/ subtree. |
| **What Does NOT Belong Here** | Frontend code (that lives in frontend/). Root-level authority docs (CLAUDE.md, DESIGN-SPEC.md, etc.). Session reports and U-series outputs (those move to docs/). |
| **Change from current state** | None — entire backend/ tree is unchanged. |

---

## backend/docs/ (UNCHANGED — 9 subdirectories)

| Subfolder | Purpose | Who Owns It | Naming Convention | File Count |
|---|---|---|---|---|
| `backend/docs/_b9/` | Page archetype specs (b9-p01 through b9-p14). The 15 archetype specs that define layout zones, field contracts, and API routes for each of the 13 page archetypes (A-M). Read as step 4 in CLAUDE.md pre-build reading sequence. | Developer | b9-pNN-topic.md | 15 |
| `backend/docs/_qc/` | QC read logs and quality-check validation matrices. Completed records of Phase 4 QC passes. | QA/Claude | descriptive-kebab.md | 3 |
| `backend/docs/adapters/` | Pakistan-specific adapter documentation: WhatsApp execution model, conversational action spec, integration flow traces, compliance adapter, architecture overview. | Developer | descriptive-kebab.md | 5 |
| `backend/docs/adr/` | Architecture Decision Records (ADR-001 through ADR-003). Formally accepted decisions for: DDD + Microservices, Adapter Pattern, WhatsApp-First. | Developer | ADR-NNN.md | 3 |
| `backend/docs/architecture/` | System architecture reference: overview, capability matrix, data architecture, domain model (79 entities), service map. | Developer | descriptive-kebab.md | 5 |
| `backend/docs/domain/` | Domain-specific technical specs: 21 docs covering every business domain (campaigns, cases, CPQ, followups, opportunities, etc.). | Developer | domain-topic.md | 21 |
| `backend/docs/infrastructure/` | Infrastructure technical specs: API standards, concurrency control, distributed locks, event catalog, execution hardening, feature flags, idempotency, integration contracts, KPI pipelines, observability, offline sync, scheduler, workflow catalog, workflow DSL, runtime deployment. | Developer | descriptive-kebab.md | 15 |
| `backend/docs/product/` | Product-level specs: activation model, adoption UX, localization, pricing plans. | Developer / Project Lead | descriptive-kebab.md | 4 |
| `backend/docs/security/` | Security authority docs: identity/auth/RBAC, org multi-tenancy, security model. All three are Authority-class. | Developer | descriptive-kebab.md | 3 |
| `backend/docs/ui/` | UI reference docs: read models catalogue, UI foundations, UI system rules. | Developer | descriptive-kebab.md | 3 |

---

## frontend/ (UNCHANGED)

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\frontend\` |
| **Purpose** | Static HTML/CSS/JS frontend. NexLink-based admin UI. Contains 169 HTML pages (75 custom CRM pages + 94 NexLink library/demo pages). |
| **Who Owns It** | Developer, Claude/AI (page builds) |
| **Naming Convention** | HTML: kebab-case.html. JS: crm-pagename.js. CSS: descriptive-kebab.css. |
| **What Belongs Here** | All frontend source files. No .md files should be added to frontend/. |
| **What Does NOT Belong Here** | .md documentation files (none currently present in frontend/src/). |
| **Change from current state** | None. |

---

## tests/ (UNCHANGED)

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\tests\` |
| **Purpose** | Root-level E2E test suite (Playwright + contract tests). Backend pytest suite is separate at backend/tests/. |
| **Who Owns It** | QA/Claude |
| **Naming Convention** | test_*.py for Python test files. SCREAMING-KEBAB-CASE.md for documentation. |
| **What Belongs Here** | All Playwright E2E tests, contract tests, conftest.py, helpers.py, locustfile.py, SKIP-BACKLOG.md. |
| **What Does NOT Belong Here** | Test artefacts from completed runs (batch[1-8]_results.txt, *.png screenshots) — these are already present and accumulating. Consider a tests/artefacts/ subfolder in a future clean-up pass (out of scope for this restructuring). |
| **Change from current state** | None. SKIP-BACKLOG.md stays at tests/e2e/playwright/. |

---

## bin/ (UNCHANGED)

| Field | Value |
|---|---|
| **Folder** | `D:\SaaS\CRM\bin\` |
| **Purpose** | Bundled PostgreSQL 14 Windows binaries for local development. |
| **Who Owns It** | DevOps |
| **What Belongs Here** | PostgreSQL binary distribution (bin/pgsql/). |
| **Change from current state** | None. The bin/pgsql/doc/README-pldebugger.md is a third-party library doc — excluded from project doc management. |

---

## Summary Table — All Proposed Folders

| Folder | New / Existing | Files After Restructuring | Owner | Purpose in One Line |
|---|---|---|---|---|
| `D:\SaaS\CRM\` (root) | Existing | 8 .md files | Project Lead / Developer | Mandatory tool files, GitHub conventions, authority docs in reading sequence |
| `docs/` | **NEW** | 0 files (subfolders only) | N/A | Documentation root — contains only subfolders |
| `docs/reference/` | **NEW** | 1 | DevOps | Active reference docs not in mandatory reading sequence |
| `docs/reports/` | **NEW** | 0 files (subfolders only) | N/A | Report container — contains only subfolders |
| `docs/reports/session/` | **NEW** | 7 | Claude/AI | Session-maintenance docs: progress, state, QC records |
| `docs/reports/u-series/` | **NEW** | 31 | Claude/AI | All U-pass prompts and output files |
| `docs/archive/` | **NEW** | 10 | None (historical) | Superseded, closed, and completed docs |
| `_archive/` | Existing → vacated | 0 | None | Vacated; contents moved to docs/archive/ |
| `backend/` | Existing | 79 .md files | Developer / QA | Backend code + all backend docs (unchanged) |
| `frontend/` | Existing | 0 .md files | Developer | Frontend HTML/CSS/JS (unchanged) |
| `tests/` | Existing | 1 .md file | QA | E2E test suite (unchanged) |
