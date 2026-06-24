# Bloat Cleanup Report
**Project:** Pakistan CRM OS
**Date:** 2026-06-24

---

## Summary Table

| Category | Pre-Cleanup Count | Post-Cleanup Count | Removed | Approx Size Freed |
|----------|------------------|--------------------|---------|-------------------|
| `__pycache__/` directories | 689 | 0 | 689 | ~est. 30-60 MB |
| `.pyc` files | 5,334 | 0 | 5,334 | included above |
| Playwright screenshots | 206 | 0 | 206 | 8.2 MB |
| `test-results/` dirs | 0 | 0 | 0 | N/A |
| `.tmp` / `.temp` files | 0 | 0 | 0 | N/A |
| `dist/` build dirs | 0 | 0 | 0 | N/A |
| `build/` dirs | 0 | 0 | 0 | N/A |
| `coverage/` dirs | 0 | 0 | 0 | N/A |

**Total files removed:** 5,540+
**Estimated space freed:** ~40-70 MB

---

## Cleanup Location Breakdown

### __pycache__ directories (689 removed)

Directories were distributed across:
- `backend/services/**` (all service modules)
- `backend/adapters/**`
- `backend/middleware/`
- `backend/scripts/`
- `tests/api/`
- `tests/e2e/playwright/`
- `tests/load/`

### .pyc files (5,334 removed)

Compiled bytecode from CPython 3.12 runs. Files matched pattern `*.pyc`, excluding `.git/`.

### Playwright screenshots (206 files / 8.2 MB removed)

Located in: `D:\SaaS\CRM\tests\e2e\playwright\screenshots\`

All were auto-generated test artifacts (file naming pattern: `tests_e2e_playwright_*.py__test_*.png`).
Test scripts preserved. Only the generated PNG outputs were deleted.

---

## Items NOT Cleaned (Safety Rules)

| Item | Size | Reason |
|------|------|--------|
| `node_modules/` (frontend) | Large | Runtime dependency |
| `node_modules/` (gateway) | Large | Runtime dependency |
| `bin/` (PostgreSQL binaries) | 561 MB | Required for local PostgreSQL |
| `data/` (PostgreSQL data) | 94 MB | Database files |
| `backend/.venv/` | Large | Python venv |
| `logs/*.log` | 64 KB | Runtime evidence; .gitignore handles |