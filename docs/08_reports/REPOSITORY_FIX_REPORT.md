# Repository Fix Report

**Date:** 2026-06-22
**Scope:** Full Repository Normalization — git hygiene, CI/CD relocation, doc reorganization

---

## Fix 1 — bin/ removal from git tracking

**Result:** bin/ was NOT tracked in git at the time of this audit (confirmed by `git ls-files | grep "^bin/"` returning 0 results). No action taken — files remain on disk, were never committed. The .gitignore update (Fix 3) now prevents future accidental tracking.

**Verification:** `git ls-files "bin/"` returns 0 files. PASS.

---

## Fix 2 — data/ removal from git tracking

**Result:** data/ was NOT tracked in git at the time of this audit (confirmed by `git ls-files | grep "^data/"` returning 0 results). No action taken — files remain on disk, were never committed. The .gitignore update (Fix 3) now prevents future accidental tracking.

**Verification:** `git ls-files "data/"` returns 0 files. PASS.

---

## Fix 3 — Log files removal from git tracking

**Result:** Log files (gw.log, gateway_startup.log, gateway_err.log) were NOT tracked in git — already excluded by the existing `*.log` rule in .gitignore. `git rm --cached` returned exit code 128 for all three (not found in index). No untracking needed.

**Log files present on disk:** gw.log, gateway_startup.log, gateway_err.log (3 files at repo root).

---

## Fix 4 — .gitignore additions

**Entries added to D:\SaaS\CRM\.gitignore:**

```
# PostgreSQL binaries and data
bin/
data/

# Logs (explicit)
logs/
gw.log
gateway_startup.log
gateway_err.log

# Python cache
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.coverage
htmlcov/
coverage.xml
*.egg-info/

# Playwright test artifacts
tests/e2e/playwright/screenshots/
tests/e2e/playwright/*.txt
tests/e2e/playwright/__pycache__/

# Node
frontend/node_modules/

# Environment
.env.*.local

# Build outputs
build/
*.min.js.map
```

**Entries preserved (already present):** `.npm-cache/`, `.pip-cache/`, `.venv/`, `node_modules/`, `dist/`, `*.log`, `.env`, `*.env`, `.env.local`, `c-seal/`, `.playwright-browsers/`, `.selenium-cache/`

---

## Fix 5 — CI/CD workflow moved to root

**Old path:** `D:\SaaS\CRM\backend\.github\workflows\deploy-runtime.yml`
**New path:** `D:\SaaS\CRM\.github\workflows\deploy-runtime.yml`

Content was copied verbatim (217 lines, full 4-stage pipeline: package-runtime, package-infra, deploy-dev, deploy-staging, deploy-prod).

Original file removed from `backend/.github/workflows/`. Root `.github/workflows/` already existed. File staged via `git add .github/workflows/deploy-runtime.yml`.

**Verification:**
- `Test-Path "D:\SaaS\CRM\.github\workflows\deploy-runtime.yml"` → True. PASS.
- `Test-Path "D:\SaaS\CRM\backend\.github\workflows\deploy-runtime.yml"` → False. PASS.

---

## Fix 6 — Backend root .md files moved to backend/docs/

**Files moved from `backend/` root to `backend/docs/`:**

| File | Action |
|---|---|
| BACKEND-QC.md | Copied to backend/docs/BACKEND-QC.md, original removed |
| CONSTRAINTS.md | Copied to backend/docs/CONSTRAINTS.md, original removed |
| PENDING.md | Copied to backend/docs/PENDING.md, original removed |
| FRONTEND-BACKEND-MAPPING.md | Copied to backend/docs/FRONTEND-BACKEND-MAPPING.md, original removed |
| product-spec-gap-register.md | Copied to backend/docs/product-spec-gap-register.md, original removed |
| market-research-gap-register.md | Copied to backend/docs/market-research-gap-register.md, original removed |

**Files kept at backend/ root (correct location):**
- `backend/README.md` — project-level readme, correct at root

**Conflict check:** None of these files existed in backend/docs/ prior to this operation.

---

## Fix 7 — Playwright screenshots untracked from git

**121 screenshot .png files removed from git index** via `git rm -r --cached tests/e2e/playwright/screenshots/`

Files remain on disk. They will no longer be tracked or committed.

**Playwright __pycache__ also removed:**
- 8 `.pyc` files removed from `tests/e2e/playwright/__pycache__/`

**Verification:** `git ls-files | grep "screenshots"` returns 0. PASS.

---

## Fix 8 — All __pycache__ / .pyc files untracked from git

**18 total tracked pycache/pyc files removed from git index:**

From `tests/api/__pycache__/` (9 files):
- conftest.cpython-312-pytest-9.0.3.pyc
- test_auth_contract.cpython-312-pytest-9.0.3.pyc
- test_billing_contract.cpython-312-pytest-9.0.3.pyc
- test_communications_contract.cpython-312-pytest-9.0.3.pyc
- test_governance_contract.cpython-312-pytest-9.0.3.pyc
- test_integrations_contract.cpython-312-pytest-9.0.3.pyc
- test_reports_contract.cpython-312-pytest-9.0.3.pyc
- test_smoke_all_routes.cpython-312-pytest-9.0.3.pyc
- test_tenant_isolation.cpython-312-pytest-9.0.3.pyc

From `tests/e2e/playwright/__pycache__/` (8 files — removed in Fix 7):
- conftest, test_audit_pages, test_datatable, test_filter_chips, test_form_submit, test_kpi_render, test_page_load, test_settings_pages

From `tests/load/__pycache__/` (1 file):
- locustfile.cpython-312.pyc

**Verification:** `git ls-files | grep -E "__pycache__|\.pyc$"` returns 0. PASS.

---

## Fix 9 — Duplicate root prompt files

**Finding:** 6+ prompt .md files exist at repo root that appear to be duplicates of files in `Prompts/Main/`. These were NOT moved or deleted as instructed — files are untouched. The canonical location is `Prompts/Main/`. The root copies are acknowledged as duplicates for future manual cleanup.

**No action taken.** Files documented here for record.

---

## Fix 10 — Empty docs stubs populated

**5 README.md files created:**

| Directory | File created | Purpose description |
|---|---|---|
| docs/01_backend/ | README.md | Backend architecture docs — populated during Backend Authority Capture phase |
| docs/02_frontend/ | README.md | Frontend architecture docs — populated during Frontend Authority Capture phase |
| docs/03_fullstack_contracts/ | README.md | Full-stack integration contracts — populated during contract documentation phase |
| docs/04_testing/ | README.md | Test strategy and coverage docs — populated during Testing Authority Capture phase |
| docs/05_deployment/ | README.md | Deployment and infrastructure docs — populated during Deployment Authority Capture phase |

---

## Git Status Summary

**Total staged/changed files:** 180 (from `git status --short | wc -l`)

**Key staged changes:**
- `A  .github/workflows/deploy-runtime.yml` — workflow added at correct root location
- `M  .gitignore` — entries added for bin/, data/, pycache, screenshots, logs
- `D  backend/.github/workflows/deploy-runtime.yml` — original workflow deleted
- `D  backend/BACKEND-QC.md`, `D  backend/CONSTRAINTS.md`, `D  backend/PENDING.md`, `D  backend/FRONTEND-BACKEND-MAPPING.md`, `D  backend/market-research-gap-register.md`, `D  backend/product-spec-gap-register.md` — moved to backend/docs/
- `D  tests/api/__pycache__/*.pyc` — 9 pyc files untracked
- `D  tests/e2e/playwright/__pycache__/*.pyc` — 8 pyc files untracked
- `D  tests/e2e/playwright/screenshots/*.png` — 121 screenshot files untracked
- `D  tests/load/__pycache__/locustfile.cpython-312.pyc` — 1 pyc file untracked

**Not yet staged (untracked new files):**
- backend/docs/ new files (BACKEND-QC.md, CONSTRAINTS.md, PENDING.md, FRONTEND-BACKEND-MAPPING.md, market-research-gap-register.md, product-spec-gap-register.md)
- docs/01_backend/README.md through docs/05_deployment/README.md
- Various audit .md files at root (approved content awaiting staging decision)

---

## Recommended Commit Message

```
chore(repo): normalize git hygiene and repo structure

- Add bin/, data/, __pycache__, screenshots, and explicit log paths to .gitignore
- Untrack all .pyc / __pycache__ files from git index (18 files)
- Untrack 121 playwright screenshot .png files from git index
- Move deploy-runtime.yml from backend/.github/ to root .github/workflows/ (was never executing)
- Move 6 misplaced backend docs from backend/ root to backend/docs/
- Add README.md stubs to docs/01_backend/ through docs/05_deployment/

No application source code (.py, .js, .html, .css) was modified.
No database migration files were touched.
All removed files remain on disk — only git tracking was changed.
```

---

## Verification Checklist

| Check | Command | Expected | Result |
|---|---|---|---|
| bin/ untracked | `git ls-files \| grep "^bin/"` | 0 files | PASS — 0 |
| data/ untracked | `git ls-files \| grep "^data/"` | 0 files | PASS — 0 |
| log files not tracked | `git ls-files \| grep "\.log$"` | 0 files | PASS — 0 |
| __pycache__ / .pyc untracked | `git ls-files \| grep "__pycache__\|\.pyc$"` | 0 files | PASS — 0 |
| screenshots untracked | `git ls-files \| grep "screenshots"` | 0 files | PASS — 0 |
| Workflow at root | `Test-Path .github/workflows/deploy-runtime.yml` | True | PASS |
| Workflow removed from backend | `Test-Path backend/.github/workflows/deploy-runtime.yml` | False | PASS |
| backend/docs/ new files | `Test-Path backend/docs/BACKEND-QC.md` | True | PASS |
| Docs stubs created | `Test-Path docs/01_backend/README.md` | True | PASS |

**All checks: PASS**

---

## Remaining Items (Cannot Be Fixed Automatically)

1. **Duplicate root prompt files** — 6+ .md files at repo root are duplicates of Prompts/Main/ content. Manual cleanup required. Do not delete without confirming canonical version in Prompts/Main/ is up to date.

2. **backend/.venv/ in glob results** — The .venv directory at `backend/.venv/` contains hundreds of .md and other files from pip packages. These appear in Glob results but are correctly excluded from git tracking by `.venv/` in .gitignore. No action needed — confirm .venv is not tracked: `git ls-files backend/.venv | wc -l` should be 0.

3. **Staged deletions from prior sessions** — Several root .md files (CHANGELOG.md, DOC-CATALOGUE.md, etc.) show as `D` (deleted, staged) from earlier work sessions. These are pre-existing staged deletions not introduced by this normalization run.
