# C: Drive Leakage Audit
**Project:** Pakistan CRM OS  
**Workspace root:** D:\SaaS\CRM  
**Audit date:** 2026-06-21

---

## Audit Table

| Tool | Path Type | Actual / Default Path | Status | Remediation |
|------|-----------|----------------------|--------|-------------|
| **npm** | Cache | `D:\npm-cache` (env override) | SEALED | None |
| **npm** | Global prefix | `D:\npm` (env override) | SEALED | None |
| **npm** | Builtin prefix fallback | `C:\Users\Admin\AppData\Roaming\npm` | SEALED | Overridden by env — not active |
| **npm** | User .npmrc prefix | `D:\npm` (`C:\Users\Admin\.npmrc`) | SEALED | None |
| **npm** | frontend .npmrc cache | `D:\CRM\.npm-cache` | SEALED | Env var wins; both on D: |
| **npm** | gateway .npmrc cache | `D:\CRM\.cache\npm` | SEALED | None |
| **node_modules** | Install location | `D:\SaaS\CRM\frontend\node_modules` | SEALED | None |
| **pnpm** | Store dir | `D:\dev-cache\pnpm-store` | SEALED | None |
| **Vite** | Build outDir | N/A — no Vite config present | NOT PRESENT | N/A |
| **Vite** | Cache dir (.vite) | N/A — no Vite installed | NOT PRESENT | N/A |
| **SASS / http-server** | Build outputs | `D:\SaaS\CRM\frontend\src\assets\css\` | SEALED | None |
| **Python (system)** | Executable | Not installed (not in PATH) | NOT PRESENT | N/A |
| **Python (venv)** | venv location | `D:\SaaS\CRM\backend\.venv` | SEALED | None |
| **pip** | Cache dir (active) | `D:\LMS\workspace\.pip-cache` (via pip.ini) | SEALED | None |
| **pip** | Cache dir (.env.local hint) | `D:\pip-cache` (not auto-loaded) | SEALED | Paths differ but both on D: — align for consistency |
| **pip** | Config source | `C:\Users\Admin\AppData\Roaming\pip\pip.ini` | SEALED | Config file on C:, points to D: |
| **pip** | PIP_CACHE_DIR env var | (empty — not set in session) | SEALED | pip.ini active path is D: |
| **pytest** | Cache dir | `D:\SaaS\CRM\backend\.pytest_cache` | SEALED | None |
| **pytest** | test-results / coverage | Not yet created (will be in `D:\SaaS\CRM\backend\`) | SEALED | None |
| **pytest** | pytest.ini / setup.cfg | Not present — uses pyproject.toml defaults | NOT PRESENT | N/A |
| **Playwright** | Browsers path (env) | `D:\dev-cache\playwright` | SEALED | None |
| **Playwright** | Browsers path (.npmrc) | `D:\CRM\.playwright-browsers` (skip download=1) | SEALED | Env var takes precedence |
| **Playwright** | Default C: path | `C:\Users\Admin\AppData\Local\ms-playwright` | SEALED | Directory does not exist |
| **Playwright** | playwright.config.* | Not present in workspace | NOT PRESENT | N/A |
| **TEMP / TMP** | Temp directories | `D:\Temp` (both vars) | SEALED | None |
| **NODE_PATH** | Global node modules | (empty — not set) | SEALED | None |
| **Docker** | Named volume | `postgres_data` (internal — managed by Docker) | SEALED | No host C: bind mount |
| **Docker** | Bind mounts | `./db`, `./migrations` (relative to D: project) | SEALED | None |
| **Docker** | Desktop data root | Docker Desktop not locally installed | NOT PRESENT | N/A |
| **CI/CD (GitHub Actions)** | Runner OS | `ubuntu-latest` — no Windows paths | SEALED | None |
| **CI/CD** | Hardcoded C: paths | None found in either workflow file | SEALED | None |

---

## Legend

| Status | Meaning |
|--------|---------|
| **SEALED** | Confirmed writing to D: or neutral (no write path) |
| **LEAKING** | Confirmed writing to C: |
| **RISK** | Default would write to C:, no redirect confirmed |
| **NOT PRESENT** | Tool not installed or not used in this project |

---

## C: Path Grep Results

Scan of all config files for literal `C:\` or `C:/` patterns:

| File | Hits | Verdict |
|------|------|---------|
| `D:\SaaS\CRM\frontend\.npmrc` | 0 | CLEAN |
| `D:\SaaS\CRM\backend\gateway\.npmrc` | 0 | CLEAN |
| `C:\Users\Admin\.npmrc` | 0 | CLEAN |
| `D:\SaaS\CRM\backend\pyproject.toml` | 0 | CLEAN |
| `D:\SaaS\CRM\.env.local` | 0 | CLEAN |
| `D:\SaaS\CRM\backend\.env.example` | 0 | CLEAN |

**No hardcoded C: paths found in any config file.**
