# REPOSITORY CLASSIFICATION MATRIX
**Generated:** 2026-06-22
**Audit scope:** D:\SaaS\CRM — all meaningful folders (cache/venv/node_modules excluded)

---

## SUMMARY COUNTS BY CLASSIFICATION

| Classification | Count | Examples |
|----------------|-------|---------|
| Active Source | 18 | backend/src, backend/services, backend/gateway, backend/adapters, backend/middleware, frontend/src/app, frontend/src/assets/js, frontend/src/assets/css, frontend/src/assets/libs, frontend/src/authentication |
| Authority Documentation | 9 | docs/00_authority/, docs/07_governance/, CLAUDE.md, DESIGN-SPEC.md, FRAMEWORK.md, PAGE-BUILD-PROTOCOL.md, PRODUCT-SPEC.md, backend/CONSTRAINTS.md |
| Supporting Documentation | 8 | README.md, CONTRIBUTING.md, backend/docs/, docs/reference/, backend/db/*.md, backend/gateway/README.md |
| Generated Report | 6 | docs/08_reports/, docs/reports/session/, docs/reports/u-series/, tests/load/reports/, tests/security/*.json, tests/e2e/playwright/screenshots/ |
| Test Asset | 6 | tests/e2e/playwright/*.py, tests/api/, tests/load/, tests/security/*.py, backend/tests/ |
| Script / Tooling | 4 | backend/scripts/, Prompts/, Makefile, seal.ps1, .pre-commit-config.yaml, .semgrep/ |
| Configuration | 5 | render.yaml, .gitignore, .claude/, backend/.github/, .pre-commit-config.yaml |
| Infrastructure | 3 | .github/, backend/docker/, backend/.github/ |
| Migration / Database | 3 | backend/alembic/, backend/db/, data/postgres/ |
| Build Output | 7 | .pytest_cache/, .npm-cache/, .pip-cache/, .playwright-browsers/, backend/.venv/, backend/__pycache__ dirs, tests/__pycache__ dirs |
| Temporary Artifact | 4 | gw.log, gateway_startup.log, gateway_err.log, logs/, dev-server.log, tests/e2e/playwright/*.txt |
| Legacy | 1 | frontend/src/* (library pages: ai/, chart/, email/, etc.) |
| Archive | 2 | docs/archive/, _archive/ |
| Unknown | 0 | — |
| Misplaced | 11 | See detailed list below |
| Duplicate Purpose | 2 | backend/.github/ mirrors root .github/; _archive/ redundant with docs/archive/ |

---

## ACTIVE SOURCE FOLDERS

| Folder | Language/Type | Purpose | Status |
|--------|--------------|---------|--------|
| `backend/src/` | Python | Domain business logic — 34 modules (admin_control_center, ai_copilot, campaigns, etc.) | Correct |
| `backend/services/` | Python | Service layer — 23 service groups (followup, conversation, activity, etc.) | Correct |
| `backend/gateway/` | Node.js | API gateway — Express server with auth, routing, DB repositories | Correct |
| `backend/adapters/` | Python | Pakistan payment adapters (JazzCash, EasyPaisa, etc.) | Correct |
| `backend/middleware/` | Python | HTTP middleware (auth, rate-limit, CORS) | Correct |
| `frontend/src/app/` | HTML/JS | 169 custom CRM pages (active build phase) | Correct |
| `frontend/src/authentication/` | HTML | Login, register, forgot-password pages | Correct |
| `frontend/src/assets/js/app/` | JS | crm-shell.js, dummy data, page scripts | Correct |
| `frontend/src/assets/js/` | JS | Dashboard, chart, plugin scripts | Correct |
| `frontend/src/assets/css/` | CSS | crm-custom.css and custom stylesheets | Correct |
| `frontend/src/assets/scss/` | SCSS | SCSS source files | Correct |
| `frontend/src/assets/libs/` | JS/CSS | Vendored libraries (Bootstrap, jQuery, DataTables, etc.) | Correct |
| `frontend/src/assets/images/` | Images | Static images and icons | Correct |
| `frontend/src/assets/ajax/` | JSON | AJAX data fixtures | Correct |
| `frontend/src/assets/json/` | JSON | JSON data fixtures | Correct |

---

## MISPLACED FILES AND FOLDERS (DETAILED)

| Item | Current Location | Problem | Correct Location |
|------|-----------------|---------|-----------------|
| `gw.log` | root | Runtime log at root | `logs/` or .gitignored |
| `gateway_startup.log` | root | Runtime log at root | `logs/` or .gitignored |
| `gateway_err.log` | root | Runtime log at root | `logs/` or .gitignored |
| `seal.ps1` | root | Script at root; should be in tooling folder | `bin/` or `scripts/` |
| `.env.local` | root | Secrets file at root; not .gitignored by name | Must be .gitignored (already is via `.env.local` pattern) — VERIFY |
| `COMMERCIALISATION-PLAN.md` | root | Strategic doc mixed with build docs | `docs/00_authority/` or `docs/07_governance/` |
| `AUDIT REMEDIATION.md` | root (untracked) | Prompt doc at root | `Prompts/Main/` (copy exists there) |
| `DOCUMENTATION NORMALIZATION…md` | root (untracked) | Prompt doc at root | `Prompts/Main/` (copy exists there) |
| `GOVERNANCE IMPLEMENTATION PHASE 1.md` | root (untracked) | Prompt doc at root | `Prompts/Main/` (copy exists there) |
| `PHASE 1 GOVERNANCE VALIDATION.md` | root (untracked) | Prompt doc at root | `Prompts/Main/` (copy exists there) |
| `PROMPT SEQUENCE.md` | root (untracked) | Prompt doc at root | `Prompts/Main/` (copy exists there) |
| `FULL REPOSITORY NORMALIZATION AND REALITY AUDIT.md` | root (untracked) | Prompt doc at root | `Prompts/Main/` |
| `Prompts/` (directory) | root | Prompt library at root | Rename to `prompts/` or move to `docs/prompts/` |
| `_archive/` (directory) | root | Root archive redundant with docs/archive/ | Merge contents into `docs/archive/`; remove `_archive/` |
| `bin/` (directory) | root | PostgreSQL 16 binaries — no business code | Should be .gitignored; REQUIRES_OWNER_APPROVAL |
| `data/` (directory) | root | Live PostgreSQL data — runtime data | Must be .gitignored; REQUIRES_OWNER_APPROVAL |
| `logs/` (directory) | root | Runtime logs at root | Should be .gitignored |
| `backend/BACKEND-QC.md` | backend root | QC doc at backend root | `backend/docs/` or `docs/08_reports/` |
| `backend/CONSTRAINTS.md` | backend root | Authority doc at backend root | `backend/docs/` |
| `backend/FRONTEND-BACKEND-MAPPING.md` | backend root | Contract doc at backend root | `docs/03_fullstack_contracts/` |
| `backend/PENDING.md` | backend root | Session doc at backend root | `docs/reports/session/` |
| `backend/market-research-gap-register.md` | backend root | Report at backend root | `docs/08_reports/` |
| `backend/product-spec-gap-register.md` | backend root | Report at backend root | `docs/08_reports/` |
| `backend/docs/phase4-gap-register.md` | backend/docs | Report in backend/docs | `docs/08_reports/` |
| `tests/e2e/playwright/SKIP-BACKLOG.md` | tests/e2e | Testing doc in test folder | `docs/04_testing/` |
| `tests/load/reports/` | tests/load | Generated HTML reports in tests | `docs/reports/` or .gitignored |
| `tests/security/*.json` | tests/security | Scan result artifacts | `docs/reports/` or .gitignored |
| `tests/e2e/playwright/*.txt` | tests/e2e | Test run results (batch*.txt, fin*.txt) | .gitignored |
| `frontend/dev-server.log` | frontend root | Runtime log | .gitignored |
| `backend/.coverage` | backend root | Coverage artifact | .gitignored (needs entry) |
| `backend/gateway/gateway.log` | backend/gateway | Runtime log | .gitignored |

---

## DUPLICATE PURPOSE FOLDERS

| Folder A | Folder B | Conflict |
|----------|----------|---------|
| `_archive/` (root) | `docs/archive/` | Root _archive/ contains only README.md; docs/archive/ has 7 archived documents. Root folder is redundant. |
| `backend/.github/workflows/` | `.github/workflows/` | Two GitHub Actions configurations — one at repo root (ci.yml) and one nested in backend/ (deploy-runtime.yml). These may interact unexpectedly. REQUIRES_OWNER_APPROVAL to evaluate. |

---

## EMPTY FOLDERS (STUBS WITH NO CONTENT)

These folders exist in the governance structure but contain zero files:

| Folder | Intended Purpose | Recommended Action |
|--------|-----------------|-------------------|
| `docs/01_backend/` | Backend documentation index | Populate with symlinks/index, or populate from backend/docs/ |
| `docs/02_frontend/` | Frontend documentation | Populate with frontend build protocol summaries |
| `docs/03_fullstack_contracts/` | API contracts and mapping | Move backend/FRONTEND-BACKEND-MAPPING.md here |
| `docs/04_testing/` | Testing documentation | Move tests/e2e/playwright/SKIP-BACKLOG.md here |
| `docs/05_deployment/` | Deployment documentation | Move docs/reference/RENDER-DEPLOY.md here OR create index |

---

## GENERATED ARTIFACTS IN SOURCE CONTROL

Files that are generated by tools and should not be tracked in git:

| Path | Generated By | Status |
|------|-------------|--------|
| `backend/.coverage` | pytest-cov | In repo; NOT in .gitignore |
| `tests/e2e/playwright/screenshots/*.png` | Playwright | In repo; NOT in .gitignore |
| `tests/e2e/playwright/*.txt` (batch*.txt, fin*.txt, etc.) | pytest runs | In repo; NOT in .gitignore |
| `tests/load/reports/*.html` | Locust | In repo; NOT in .gitignore |
| `tests/security/*.json` (semgrep-report*.json, pip-audit.json) | Semgrep/pip-audit | In repo (may be intentional as evidence) |
| `backend/gateway/gateway.log` | Gateway server | In repo; NOT in .gitignore |
| `frontend/dev-server.log` | npm dev server | In repo; NOT in .gitignore |
| `gw.log`, `gateway_startup.log`, `gateway_err.log` | Gateway server | At root; NOT in .gitignore |
| `logs/gateway.log`, `logs/frontend.log` | Runtime servers | In logs/; logs/ NOT in .gitignore |
| `data/postgres/` | PostgreSQL | 1,723 binary files; NOT in .gitignore |
| `bin/pgsql/` | PostgreSQL install | 4,416 binary files; NOT in .gitignore |
| `tests/e2e/playwright/__pycache__/` | Python bytecode | In repo; should be .gitignored |
| `tests/api/__pycache__/` | Python bytecode | In repo; should be .gitignored |
| `tests/load/__pycache__/` | Python bytecode | In repo; should be .gitignored |
