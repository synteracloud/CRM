# Workspace Sealing Report
**Project:** Pakistan CRM OS  
**Workspace root:** D:\SaaS\CRM  
**Audit date:** 2026-06-21  
**Auditor:** Claude (automated tooling audit)

---

## Executive Summary

**Overall verdict: FULLY SEALED**

All active tooling has been redirected off the C: drive onto D:. No tool is currently writing to C:. The one surface labelled RISK (pip cache path mismatch between `PIP_CACHE_DIR` env var and the active pip.ini) is non-critical because the effective path (`D:\LMS\workspace\.pip-cache`) is still on D:.

---

## Per-Tool Findings

### 1. npm

**Status: SEALED**

All three npm path dimensions are redirected to D:.

| Setting | Effective value | Source |
|---------|----------------|--------|
| `cache` | `D:\npm-cache` | `$env:npm_config_cache` (env override, highest priority) |
| `prefix` | `D:\npm` | `$env:npm_config_prefix` (env override, highest priority) |
| Builtin fallback | `C:\Users\Admin\AppData\Roaming\npm` | npm builtin — **overridden by env, not active** |
| User .npmrc prefix | `D:\npm` | `C:\Users\Admin\.npmrc` |

The env-level overrides (`cache = D:\npm-cache`, `prefix = D:\npm`) take precedence over the builtin C: defaults, confirmed by `npm config list` output showing the builtin prefix annotated as "overridden by env".

**Project .npmrc files**

- `D:\SaaS\CRM\frontend\.npmrc` — sets `cache=D:\CRM\.npm-cache`, `playwright_browsers_path=D:\CRM\.playwright-browsers`. No C: paths. Note: this path (`D:\CRM\.npm-cache`) differs from the active effective cache (`D:\npm-cache` from env); the env var wins. Harmless discrepancy.
- `D:\SaaS\CRM\backend\gateway\.npmrc` — sets `cache=D:\CRM\.cache\npm`. No C: paths.
- `C:\Users\Admin\.npmrc` — sets `prefix=D:\npm`. No C: paths.

### 2. node_modules

**Status: SEALED**

`D:\SaaS\CRM\frontend\node_modules` exists on D:. No `node_modules` directories found anywhere else in the workspace tree.

### 3. Vite / Build Outputs

**Status: NOT PRESENT (no Vite config)**

No `vite.config.*` file exists anywhere under `D:\SaaS\CRM`. The frontend uses a plain `http-server` for dev serving and `sass` for CSS compilation. There is no Vite build pipeline. Build outputs (compiled CSS) land in `D:\SaaS\CRM\frontend\src\assets\css\` — on D:. No `.vite` cache directory was found.

### 4. pnpm

**Status: SEALED**

`store-dir = D:\dev-cache\pnpm-store` is set in the npm environment config (visible in `npm config list`). The directory `D:\dev-cache\pnpm-store` exists on D:. No C: path involvement.

### 5. Python / pip / backend

**Status: SEALED**

Python is not installed as a system/user executable (`python`, `py`, `python3` all resolve to "not found" in the system PATH). Python is only accessible via the project virtualenv at `D:\SaaS\CRM\backend\.venv\Scripts\python.exe` — located on D:.

**pip cache:** Configured by `C:\Users\Admin\AppData\Roaming\pip\pip.ini`:
```
[global]
cache-dir = D:\LMS\workspace\.pip-cache
```
The effective pip cache directory is `D:\LMS\workspace\.pip-cache` — on D:.

**Note on path mismatch:** The `PIP_CACHE_DIR` environment variable is empty (not set in the current session environment). The `.env.local` file declares `PIP_CACHE_DIR=D:\pip-cache`, but `.env.local` is not automatically loaded by the shell — it is an application hint file. The active pip.ini setting (`D:\LMS\workspace\.pip-cache`) is what pip actually uses. Both paths are on D:; there is no C: leakage, but there is an inconsistency between the hint in `.env.local` and the actual pip.ini config.

**venv:** `D:\SaaS\CRM\backend\.venv` — on D:. Correct location within project.

**pyproject.toml:** Contains only ruff linter config with no path references. No C: paths.

**pytest:** `.pytest_cache` directory exists at `D:\SaaS\CRM\backend\.pytest_cache` — on D:. No `pytest.ini` or `setup.cfg` found (pytest uses defaults / pyproject.toml only). No test-results, coverage, or reports directories currently exist (they would be created at test runtime inside `D:\SaaS\CRM\backend\` — on D:).

### 6. Playwright

**Status: SEALED**

The `PLAYWRIGHT_BROWSERS_PATH` environment variable is set to `D:\dev-cache\playwright` in the active shell environment. The directory exists. The default C: path (`C:\Users\Admin\AppData\Local\ms-playwright`) does **not** exist, confirming browsers were never downloaded to C:.

No `playwright.config.*` file exists in the workspace — Playwright is present via test infrastructure only.

**Note:** `D:\SaaS\CRM\frontend\.npmrc` also sets `playwright_browsers_path=D:\CRM\.playwright-browsers` and `playwright_skip_browser_download=1`. The env var (`D:\dev-cache\playwright`) takes precedence over the .npmrc setting; the .npmrc acts as a fallback guard with browser download skipped. Both are on D:.

### 7. Environment Variables

**Status: SEALED**

| Variable | Value | Assessment |
|---|---|---|
| `npm_config_cache` | `D:\npm-cache` | D: — SEALED |
| `PLAYWRIGHT_BROWSERS_PATH` | `D:\dev-cache\playwright` | D: — SEALED |
| `PIP_CACHE_DIR` | (empty) | Not set in session; pip.ini active path is D: |
| `TEMP` | `D:\Temp` | D: — SEALED |
| `TMP` | `D:\Temp` | D: — SEALED |
| `NODE_PATH` | (empty) | Not set — no global node modules path |

### 8. Docker

**Status: SEALED (container-internal volumes only)**

`D:\SaaS\CRM\backend\docker-compose.yml` uses one named volume (`postgres_data`) and two bind mounts (`./db`, `./migrations`) — both relative to the project directory on D:. No host C: paths are referenced. Docker Desktop settings files were not found in the standard locations; Docker may not be locally installed (it runs in CI via GitHub Actions on ubuntu-latest runners).

### 9. CI/CD

**Status: SEALED (runs on Linux, no Windows paths)**

Both workflow files (`.github/workflows/ci.yml` and `backend/.github/workflows/deploy-runtime.yml`) run on `ubuntu-latest`. No Windows drive paths appear in either file. All paths referenced are Unix-style relative paths within the repository.

### 10. C: Path Grep across all config files

**Status: CLEAN**

A scan for `C:\` or `C:/` across all config files returned zero hits:

- `D:\SaaS\CRM\frontend\.npmrc` — CLEAN
- `D:\SaaS\CRM\backend\gateway\.npmrc` — CLEAN
- `C:\Users\Admin\.npmrc` — CLEAN
- `D:\SaaS\CRM\backend\pyproject.toml` — CLEAN
- `D:\SaaS\CRM\.env.local` — CLEAN
- `D:\SaaS\CRM\backend\.env.example` — CLEAN

---

## Remediation Items

No LEAKING items found. One minor inconsistency to be aware of (not a blocker):

**PIP_CACHE_DIR inconsistency (INFORMATIONAL)**

`.env.local` declares `PIP_CACHE_DIR=D:\pip-cache` but this env file is not automatically sourced by the shell. The active pip config (`pip.ini`) independently sets the cache to `D:\LMS\workspace\.pip-cache`. If `.env.local` is ever sourced, the pip cache would land at `D:\pip-cache` rather than `D:\LMS\workspace\.pip-cache`. Both are on D:; there is no C: risk. To eliminate the discrepancy, align `.env.local`'s `PIP_CACHE_DIR` with the `pip.ini` path, or update `pip.ini` to match `.env.local`.

---

## Conclusion

The workspace is **FULLY SEALED**. All six active toolchains (npm, node_modules, pnpm, Python/pip/venv, Playwright, TEMP/TMP) write exclusively to the D: drive. The C: drive contains only read-only system installations (Node.js binary at `C:\Program Files\nodejs\node.exe`), configuration files in user AppData, and the builtin npm prefix fallback — all of which are overridden by D: paths at the env or config level.
