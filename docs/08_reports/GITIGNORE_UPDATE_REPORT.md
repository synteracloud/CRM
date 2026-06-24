# .gitignore Update Report
**Project:** Pakistan CRM OS
**Date:** 2026-06-24
**File:** D:\SaaS\CRM\.gitignore

---

## Entries Added (10 new entries)

| Entry | Section | Reason Added |
|-------|---------|--------------|
| `*.pyc` | Python cache | Was missing (only `*.py[cod]` and `*.pyo` existed) |
| `*.pyd` | Python cache | Windows Python DLL extension — not previously covered |
| `.Python` | Python | Python symlink in venv root |
| `test-results/` | Test outputs | Playwright/pytest test-results dirs |
| `playwright-report/` | Test outputs | Playwright HTML report output |
| `.npm/` | Node | npm local cache dir |
| `.workspace/` | Temp/cache | New workspace-local cache dirs |
| `*.tmp` | Temp | Temporary files |
| `*.temp` | Temp | Temporary files (alternate extension) |
| `tests/e2e/screenshots/` | Screenshots | Top-level e2e screenshots path |
| `.DS_Store` | OS artefacts | macOS finder metadata |
| `Thumbs.db` | OS artefacts | Windows thumbnail cache |

---

## Entries Already Present (kept unchanged)

| Entry | Section |
|-------|---------|
| `__pycache__/` | Python cache |
| `*.py[cod]` | Python cache |
| `*.pyo` | Python cache |
| `.pytest_cache/` | Python cache |
| `.coverage` | Python cache |
| `htmlcov/` | Python cache |
| `coverage.xml` | Python cache |
| `*.egg-info/` | Python cache |
| `tests/e2e/playwright/screenshots/` | Playwright |
| `tests/e2e/playwright/*.txt` | Playwright |
| `tests/e2e/playwright/__pycache__/` | Playwright |
| `node_modules/` | Node |
| `frontend/node_modules/` | Node |
| `*.log` | Logs |
| `logs/` | Logs |
| `gw.log` | Logs |
| `gateway_startup.log` | Logs |
| `gateway_err.log` | Logs |
| `dist/` | Build |
| `build/` | Build |
| `*.min.js.map` | Build |
| `.venv/` | Virtualenv |
| `.npm-cache/` | npm cache |
| `.pip-cache/` | pip cache |
| `.playwright-browsers/` | Playwright |
| `.selenium-cache/` | Selenium |
| `bin/` | PostgreSQL |
| `data/` | PostgreSQL |
| `.env` | Environment |
| `*.env` | Environment |
| `.env.local` | Environment |
| `.env.*.local` | Environment |
| `c-seal/` | Workspace |