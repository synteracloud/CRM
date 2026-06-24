# Sealed Workspace Validation
**Project:** Pakistan CRM OS  
**Workspace root:** D:\SaaS\CRM  
**Audit date:** 2026-06-21

---

## Validation Checklist

| # | Tool | Check | Result | Evidence |
|---|------|-------|--------|----------|
| 1 | **npm** | Cache on D: | PASS | `npm config get cache` → `D:\npm-cache` (env override active) |
| 2 | **npm** | Prefix on D: | PASS | `npm config get prefix` → `D:\npm` (env override active) |
| 3 | **npm** | No C: in project .npmrc files | PASS | C: path grep on `frontend/.npmrc`, `gateway/.npmrc` → 0 hits |
| 4 | **npm** | User .npmrc clean | PASS | `C:\Users\Admin\.npmrc` contains `prefix=D:\npm` — no C: paths |
| 5 | **npm** | Builtin fallback overridden | PASS | `npm config list` shows builtin prefix annotated "overridden by env" |
| 6 | **node_modules** | Installed on D: | PASS | `D:\SaaS\CRM\frontend\node_modules` exists; no node_modules elsewhere in tree |
| 7 | **pnpm** | Store on D: | PASS | `store-dir = D:\dev-cache\pnpm-store` in env config; directory exists |
| 8 | **Vite** | No Vite config present | N/A | No `vite.config.*` found anywhere in workspace |
| 9 | **Vite** | No .vite cache on C: | PASS | `.vite` cache not found at any location (including C:) |
| 10 | **Python** | System Python not in PATH | N/A | `python`, `py`, `python3` all unrecognized — no system Python |
| 11 | **Python venv** | venv on D: | PASS | `D:\SaaS\CRM\backend\.venv` exists; Python at `.venv\Scripts\python.exe` |
| 12 | **pip** | Cache on D: | PASS | Active: `D:\LMS\workspace\.pip-cache` (from `pip.ini`) — drive = D: |
| 13 | **pip** | pip.ini does not point to C: | PASS | `C:\Users\Admin\AppData\Roaming\pip\pip.ini` → `cache-dir = D:\LMS\workspace\.pip-cache` |
| 14 | **pip** | PIP_CACHE_DIR env var | WARN | Session env var empty; `.env.local` declares `D:\pip-cache` (not auto-loaded); pip.ini active path differs but both D: |
| 15 | **pytest** | .pytest_cache on D: | PASS | `D:\SaaS\CRM\backend\.pytest_cache` exists on D: |
| 16 | **pytest** | Test outputs would land on D: | PASS | No pytest.ini/setup.cfg; default output dirs are relative to `D:\SaaS\CRM\backend\` |
| 17 | **Playwright** | PLAYWRIGHT_BROWSERS_PATH on D: | PASS | Env var = `D:\dev-cache\playwright`; directory exists |
| 18 | **Playwright** | Default C: browser path absent | PASS | `C:\Users\Admin\AppData\Local\ms-playwright` does NOT exist |
| 19 | **Playwright** | .npmrc browser path on D: | PASS | `playwright_browsers_path=D:\CRM\.playwright-browsers`; download skipped |
| 20 | **Playwright** | No playwright.config.* | N/A | Not present in workspace |
| 21 | **TEMP** | TEMP on D: | PASS | `$env:TEMP = D:\Temp` |
| 22 | **TMP** | TMP on D: | PASS | `$env:TMP = D:\Temp` |
| 23 | **NODE_PATH** | Not set (no global modules) | PASS | `$env:NODE_PATH` = empty |
| 24 | **Docker** | No C: host bind mounts | PASS | `docker-compose.yml` uses named volumes and relative bind mounts only |
| 25 | **Docker Desktop** | Data root on D: | N/A | Docker Desktop not locally installed (no settings.json found) |
| 26 | **CI/CD** | No C: paths in workflow files | PASS | `ci.yml` and `deploy-runtime.yml` both use `ubuntu-latest`; no Windows paths |
| 27 | **Config grep** | No hardcoded C: in any config | PASS | 0 hits across all 6 config files scanned |
| 28 | **Env vars** | Key tool vars not pointing to C: | PASS | All set env vars (npm_config_cache, PLAYWRIGHT_BROWSERS_PATH, TEMP, TMP) point to D: |

---

## Summary Counts

| Result | Count |
|--------|-------|
| PASS | 21 |
| WARN | 1 |
| FAIL | 0 |
| N/A | 6 |

---

## WARN Item Detail

**Check #14 — PIP_CACHE_DIR env var empty in session**

- `$env:PIP_CACHE_DIR` is not set in the current shell session.
- `.env.local` declares `PIP_CACHE_DIR=D:\pip-cache` but this file must be manually sourced; it is not automatically loaded.
- The active pip config (`pip.ini`) independently sets `cache-dir = D:\LMS\workspace\.pip-cache`.
- **Risk:** None — both `.env.local` value and `pip.ini` value are on D:. The WARN is about the inconsistency between the two, not about C: leakage.
- **Remediation (optional):** Update `.env.local` to set `PIP_CACHE_DIR=D:\LMS\workspace\.pip-cache` to match the active pip.ini, or update `pip.ini` to use `D:\pip-cache`.

---

## Overall Verdict

**PASS — Workspace is FULLY SEALED**

Zero tools are writing to C:. All active caches, package stores, virtualenvs, build outputs, temp files, and test artifacts are on the D: drive. The single WARN is an informational path-naming inconsistency between `.env.local` and `pip.ini`; it does not represent any C: drive leakage.
