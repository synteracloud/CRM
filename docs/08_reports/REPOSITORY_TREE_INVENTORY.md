# REPOSITORY TREE INVENTORY
**Generated:** 2026-06-22
**Audit scope:** D:\SaaS\CRM (all folders, all file types)

---

## SECTION 1 — ROOT LEVEL CONTENTS

| Item | Type | File Count | Key File Types | Classification | Status | Recommended Action |
|------|------|-----------|----------------|----------------|--------|-------------------|
| `CLAUDE.md` | File | 1 | MD | Authority Documentation | Correct | Keep at root |
| `DESIGN-SPEC.md` | File | 1 | MD | Authority Documentation | Correct | Keep at root |
| `FRAMEWORK.md` | File | 1 | MD | Authority Documentation | Correct | Keep at root |
| `PAGE-BUILD-PROTOCOL.md` | File | 1 | MD | Authority Documentation | Correct | Keep at root |
| `PRODUCT-SPEC.md` | File | 1 | MD | Authority Documentation | Correct | Keep at root |
| `README.md` | File | 1 | MD | Supporting Documentation | Correct | Keep at root |
| `CONTRIBUTING.md` | File | 1 | MD | Supporting Documentation | Correct | Keep at root |
| `COMMERCIALISATION-PLAN.md` | File | 1 | MD | Supporting Documentation | Misplaced | Move to docs/00_authority or docs/07_governance |
| `render.yaml` | File | 1 | YAML | Infrastructure | Correct | Keep at root |
| `.pre-commit-config.yaml` | File | 1 | YAML | Configuration | Correct | Keep at root |
| `.gitignore` | File | 1 | — | Configuration | Correct | Keep at root; needs updates (see §4) |
| `Makefile` | File | 1 | — | Script / Tooling | Correct | Keep at root |
| `seal.ps1` | File | 1 | PS1 | Script / Tooling | Misplaced | Move to bin/ or scripts/ |
| `gw.log` | File | 1 | LOG | Temporary Artifact | Misplaced | Add to .gitignore; delete or move to logs/ |
| `gateway_startup.log` | File | 1 | LOG | Temporary Artifact | Misplaced | Add to .gitignore; delete or move to logs/ |
| `gateway_err.log` | File | 1 | LOG | Temporary Artifact | Misplaced | Add to .gitignore; delete or move to logs/ |
| `.env.local` | File | 1 | — | Configuration | Misplaced | Should be in .gitignore (contains secrets) |
| `AUDIT REMEDIATION.md` | File | 1 | MD | Generated Report | Misplaced (untracked) | Move to Prompts/Main (already exists there) OR docs/reports/u-series/ |
| `DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md` | File | 1 | MD | Generated Report | Misplaced (untracked) | Move to Prompts/Main |
| `GOVERNANCE IMPLEMENTATION PHASE 1.md` | File | 1 | MD | Generated Report | Misplaced (untracked) | Move to Prompts/Main |
| `PHASE 1 GOVERNANCE VALIDATION.md` | File | 1 | MD | Generated Report | Misplaced (untracked) | Move to Prompts/Main |
| `PROMPT SEQUENCE.md` | File | 1 | MD | Generated Report | Misplaced (untracked) | Move to Prompts/Main |
| `FULL REPOSITORY NORMALIZATION AND REALITY AUDIT.md` | File | 1 | MD | Script / Tooling | Misplaced (untracked) | Move to Prompts/Main |
| `backend/` | Dir | 13,609 | PY, JS, SQL, MD | Active Source | Correct | Keep; internal cleanup needed |
| `frontend/` | Dir | 2,753 | HTML, JS, CSS, JSON | Active Source | Correct | Keep |
| `tests/` | Dir | 345 | PY, PNG, TXT, MD | Test Asset | Correct | Keep; results need cleanup |
| `docs/` | Dir | 93 | MD | Authority + Reports | Correct | Keep; empty subdirs need population |
| `bin/` | Dir | 4,416 | binary | Infrastructure | Misplaced | PostgreSQL 16 binaries; should be .gitignored |
| `data/` | Dir | 1,727 | binary | Infrastructure | Misplaced | Live PostgreSQL data; must be .gitignored |
| `Prompts/` | Dir | 17 | MD | Script / Tooling | Misplaced | Rename to prompts/ or move to docs/ |
| `_archive/` | Dir | 1 | MD | Archive | Redundant | Only contains README.md; merge into docs/archive/ |
| `c-seal/` | Dir | 2 | TXT | Generated Report | Correct (.gitignored) | Keep; already in .gitignore |
| `logs/` | Dir | 2 | LOG | Temporary Artifact | Misplaced | Should be .gitignored |
| `.github/` | Dir | 1 | YML | Infrastructure | Correct | Keep |
| `.claude/` | Dir | 1 | JSON | Configuration | Correct | Keep |
| `.semgrep/` | Dir | 1 | YAML | Configuration / Tooling | Correct | Keep |
| `.pytest_cache/` | Dir | — | — | Build Output | Correct (.gitignored) | Already in .gitignore |
| `.npm-cache/` | Dir | many | binary | Build Output | Correct (.gitignored) | Already in .gitignore |
| `.pip-cache/` | Dir | many | binary | Build Output | Correct (.gitignored) | Already in .gitignore |
| `.playwright-browsers/` | Dir | many | binary | Build Output | Correct (.gitignored) | Already in .gitignore |

---

## SECTION 2 — BACKEND TREE

| Folder | Parent | File Count | Key File Types | Classification | Status | Recommended Action |
|--------|--------|-----------|----------------|----------------|--------|-------------------|
| `backend/` | root | ~13,609 total | — | — | — | — |
| `backend/src/` | backend | 153 (ex-pycache) | PY | Active Source | Correct | Keep; 34 domain modules |
| `backend/services/` | backend | 143 (ex-pycache) | PY | Active Source | Correct | Keep; 23 service modules |
| `backend/gateway/` | backend | ~100+ | JS, JSON | Active Source | Correct | Node.js API gateway |
| `backend/adapters/` | backend | ~30+ | PY | Active Source | Correct | Pakistan payment adapters |
| `backend/middleware/` | backend | ~10 | PY | Active Source | Correct | Auth / rate-limit middleware |
| `backend/alembic/` | backend | 17 | PY | Migration / Database | Correct | 12 migration versions |
| `backend/db/` | backend | ~35+ | SQL, MD | Migration / Database | Correct | 18 domain schemas + migrations |
| `backend/tests/` | backend | ~110 | PY | Test Asset | Correct | Unit + integration tests |
| `backend/scripts/` | backend | ~17 | PY, SH | Script / Tooling | Correct | Self-QC automation scripts |
| `backend/docker/` | backend | 2 | Dockerfile, SH | Infrastructure | Correct | infra/Dockerfile + entrypoint.sh |
| `backend/docs/` | backend | ~80+ | MD | Supporting Documentation | Correct (co-located) | b9-p specs, domain docs, ADRs |
| `backend/.venv/` | backend | ~12,000 | PY, binary | Build Output | Correct (.gitignored) | Python virtual environment |
| `backend/.pytest_cache/` | backend | — | — | Build Output | Correct (.gitignored) | pytest cache |
| `backend/.github/` | backend | 2 | YML | Infrastructure | Duplicate Purpose | Nested .github; mirrors root .github — REQUIRES_OWNER_APPROVAL to reconcile |
| `backend/BACKEND-QC.md` | backend | 1 | MD | Supporting Documentation | Misplaced | Move to backend/docs/ or docs/08_reports/ |
| `backend/CONSTRAINTS.md` | backend | 1 | MD | Authority Documentation | Misplaced | Move to backend/docs/ |
| `backend/FRONTEND-BACKEND-MAPPING.md` | backend | 1 | MD | Supporting Documentation | Misplaced | Move to backend/docs/ or docs/03_fullstack_contracts/ |
| `backend/PENDING.md` | backend | 1 | MD | Generated Report | Misplaced | Move to docs/reports/session/ |
| `backend/market-research-gap-register.md` | backend | 1 | MD | Generated Report | Misplaced | Move to docs/08_reports/ |
| `backend/product-spec-gap-register.md` | backend | 1 | MD | Generated Report | Misplaced | Move to docs/08_reports/ |
| `backend/phase4-gap-register.md` | backend | 1 | MD | Generated Report | Misplaced | Move to docs/08_reports/ |
| `backend/.coverage` | backend | 1 | binary | Build Output | Not .gitignored | Add *.coverage to root .gitignore |
| `backend/seed_tenant_refs.sql` | backend | 1 | SQL | Migration / Database | Correct | Keep in backend/ root |
| `backend/seed_c1.sql` | backend | 1 | SQL | Migration / Database | Correct | Keep in backend/ root |

---

## SECTION 3 — FRONTEND TREE

| Folder | Parent | File Count | Key File Types | Classification | Status | Recommended Action |
|--------|--------|-----------|----------------|----------------|--------|-------------------|
| `frontend/` | root | 2,753 total | — | — | — | — |
| `frontend/src/app/` | frontend | 169 | HTML | Active Source | Correct | 169 custom app pages |
| `frontend/src/assets/js/app/` | frontend | ~10 | JS | Active Source | Correct | crm-shell.js and page scripts |
| `frontend/src/assets/js/` | frontend | ~50 | JS | Active Source | Correct | Dashboard, charts, plugins |
| `frontend/src/assets/css/` | frontend | ~10 | CSS | Active Source | Correct | Custom CSS including crm-custom.css |
| `frontend/src/assets/scss/` | frontend | ~50 | SCSS | Active Source | Correct | SCSS sources |
| `frontend/src/assets/libs/` | frontend | ~800 | JS, CSS | Active Source | Correct | Vendored third-party libraries |
| `frontend/src/assets/images/` | frontend | ~200 | PNG, SVG | Active Source | Correct | Static image assets |
| `frontend/src/assets/ajax/` | frontend | ~5 | JSON | Active Source | Correct | AJAX data fixtures |
| `frontend/src/assets/json/` | frontend | ~5 | JSON | Active Source | Correct | JSON data fixtures |
| `frontend/src/ai/` | frontend | ~5 | HTML | Active Source | Legacy/Superseded | Library AI pages; superseded by src/app/ |
| `frontend/src/authentication/` | frontend | ~10 | HTML | Active Source | Active | Auth/login pages |
| `frontend/src/chart/` | frontend | ~5 | HTML | Legacy | Library pages | Superseded by app/ |
| `frontend/src/components/` | frontend | ~5 | HTML | Legacy | Library pages | Superseded by app/ |
| `frontend/src/email/` | frontend | ~5 | HTML | Legacy | Library pages | Superseded by app/ |
| `frontend/src/extended-ui/` | frontend | ~5 | HTML | Legacy | Library pages | Superseded by app/ |
| `frontend/src/forms/` | frontend | ~5 | HTML | Legacy | Library pages | Superseded by app/ |
| `frontend/src/icons/` | frontend | ~5 | HTML | Legacy | Library pages | Superseded by app/ |
| `frontend/src/maps/` | frontend | ~3 | HTML | Legacy | Library pages | Superseded by app/ |
| `frontend/src/pages/` | frontend | ~5 | HTML | Legacy | Library pages | Superseded by app/ |
| `frontend/src/table/` | frontend | ~3 | HTML | Legacy | Library pages | Superseded by app/ |
| `frontend/node_modules/` | frontend | ~1,500 | JS | Build Output | Correct (.gitignored) | npm dependencies |
| `frontend/dev-server.log` | frontend | 1 | LOG | Temporary Artifact | Not .gitignored | Add to .gitignore |

---

## SECTION 4 — TESTS TREE

| Folder | Parent | File Count | Key File Types | Classification | Status | Recommended Action |
|--------|--------|-----------|----------------|----------------|--------|-------------------|
| `tests/` | root | 345 total | — | — | — | — |
| `tests/e2e/playwright/` | tests | ~80 PY + ~180 PNG + ~40 TXT | PY, PNG, TXT | Test Asset + Generated Report | Mixed | Test .py files correct; PNG screenshots and .txt results are generated artifacts |
| `tests/e2e/playwright/screenshots/` | tests | ~160 | PNG | Generated Report | Should be .gitignored | 160+ Playwright screenshots; not tracked by intent |
| `tests/e2e/playwright/__pycache__/` | tests | — | PYC | Build Output | Should be .gitignored | Already in backend/.gitignore; add to root |
| `tests/api/` | tests | ~9 | PY | Test Asset | Correct | API contract tests |
| `tests/load/` | tests | ~3 | PY, LOG | Test Asset | Correct | Locust load tests |
| `tests/load/reports/` | tests | 7 | HTML | Generated Report | Misplaced | Move to docs/reports/ or add to .gitignore |
| `tests/security/` | tests | ~6 | JSON, PY | Test Asset + Generated Report | Mixed | .py is test asset; .json are scan results (generated) |
| `tests/e2e/playwright/SKIP-BACKLOG.md` | tests | 1 | MD | Supporting Documentation | Misplaced | Move to docs/04_testing/ |
| `tests/e2e/playwright/*.txt` | tests | ~40+ | TXT | Generated Report | Misplaced | Test run result files; add to .gitignore |
| `tests/e2e/playwright/.pytest_cache/` | tests | — | — | Build Output | Should be .gitignored | Already in backend/.gitignore pattern |

---

## SECTION 5 — DOCS TREE

| Folder | Parent | File Count | Key File Types | Classification | Status | Recommended Action |
|--------|--------|-----------|----------------|----------------|--------|-------------------|
| `docs/` | root | 93 total | MD | — | — | — |
| `docs/00_authority/` | docs | 5 | MD | Authority Documentation | Correct | PROJECT_CHARTER, DOMAIN_MODEL, FEATURE_SCOPE, etc. |
| `docs/01_backend/` | docs | 0 | — | — | EMPTY | Placeholder; populate from backend/docs/ OR remove |
| `docs/02_frontend/` | docs | 0 | — | — | EMPTY | Placeholder; populate OR remove |
| `docs/03_fullstack_contracts/` | docs | 0 | — | — | EMPTY | Placeholder; candidate for FRONTEND-BACKEND-MAPPING.md |
| `docs/04_testing/` | docs | 0 | — | — | EMPTY | Placeholder; candidate for SKIP-BACKLOG.md |
| `docs/05_deployment/` | docs | 0 | — | — | EMPTY | Placeholder; candidate for render.yaml documentation |
| `docs/06_decisions/` | docs | 1 | MD | Decision Records | Correct | ADR-001_PROJECT_FOUNDATION.md |
| `docs/07_governance/` | docs | 2 | MD | Authority Documentation | Correct | DECISION_ESCALATION_MATRIX, AI_OPERATING_CONTEXT |
| `docs/08_reports/` | docs | 14+ | MD | Generated Report | Correct | All report outputs land here |
| `docs/reference/` | docs | 1 | MD | Supporting Documentation | Correct | RENDER-DEPLOY.md |
| `docs/archive/` | docs | 7 | MD | Archive | Correct | Retired docs correctly placed |
| `docs/reports/session/` | docs | 7 | MD | Generated Report | Correct | CHANGELOG, PROGRESS, PENDING, SCREEN-ARTEFACTS, etc. |
| `docs/reports/u-series/` | docs | ~60 | MD | Generated Report | Correct | All U0–U10 audit outputs |

---

## SECTION 6 — OTHER ROOT FOLDERS

| Folder | Parent | File Count | Key File Types | Classification | Status | Recommended Action |
|--------|--------|-----------|----------------|----------------|--------|-------------------|
| `bin/` | root | 4,416 | binary, SQL | Infrastructure | Misplaced | PostgreSQL 16 binaries (pgsql/) + pg16-binaries.zip; must be .gitignored — REQUIRES_OWNER_APPROVAL |
| `data/` | root | 1,727 | binary | Infrastructure | Misplaced | Live PostgreSQL data directory (data/postgres/); must be .gitignored — REQUIRES_OWNER_APPROVAL |
| `Prompts/` | root | 17 | MD | Script / Tooling | Misplaced | AI prompt library; rename to `prompts/` (lowercase) or move to docs/prompts/ |
| `_archive/` | root | 1 | MD | Archive | Redundant | Contains only README.md; root _archive/ is redundant given docs/archive/ exists |
| `c-seal/` | root | 2 | TXT | Generated Report | Correct | Baseline seal files; correctly .gitignored |
| `logs/` | root | 2 | LOG | Temporary Artifact | Not .gitignored | gateway.log + frontend.log; should be .gitignored |
| `.github/` | root | 1 | YML | Infrastructure | Correct | ci.yml workflow |
| `.claude/` | root | 1 | JSON | Configuration | Correct | settings.local.json |
| `.semgrep/` | root | 1 | YAML | Configuration | Correct | tenant-isolation.yaml security policy |
| `.pytest_cache/` | root | — | — | Build Output | Not in root .gitignore | Root-level pytest cache; add to .gitignore |
| `.npm-cache/` | root | many | binary | Build Output | Correctly .gitignored | Keep .gitignore entry |
| `.pip-cache/` | root | many | binary | Build Output | Correctly .gitignored | Keep .gitignore entry |
| `.playwright-browsers/` | root | many | binary | Build Output | Correctly .gitignored | Keep .gitignore entry |
