# C: Drive Leakage Audit
**Project:** Pakistan CRM OS
**Workspace root:** D:\SaaS\CRM
**Audit date:** 2026-06-24
**Baseline:** Prior audit 2026-06-21 (u-series\C_DRIVE_LEAKAGE_AUDIT.md)

---

## Audit Table

| Tool | Current Path | C: Risk | Fix Applied | Final State |
|------|-------------|---------|-------------|-------------|
| **npm cache** (env var) | `D:\npm-cache` | None | None required | SEALED |
| **npm cache** (root .npmrc) | `D:\SaaS\CRM\.workspace\cache\npm` | None | Created root .npmrc | SEALED |
| **npm cache** (frontend .npmrc) | `D:\CRM\.npm-cache` | None | None | SEALED |
| **npm tmp** | `undefined` (not set) | None | None | SEALED |
| **TEMP / TMP** | `D:\Temp` | None | None | SEALED |
| **node_modules** | `D:\SaaS\CRM\frontend\node_modules` + gateway | None | None | SEALED |
| **Python venv** | `D:\SaaS\CRM\backend\.venv` | None | None | SEALED |
| **pip cache** | `D:\LMS\workspace\.pip-cache` (pip.ini) | None | None (both on D:) | SEALED |
| **pytest cache** | `D:\SaaS\CRM\backend\.pytest_cache` | None | None | SEALED |
| **Playwright browsers** | `D:\dev-cache\playwright` (env) | None | None | SEALED |
| **PostgreSQL bin** | `D:\SaaS\CRM\bin` | None | None | SEALED |
| **PostgreSQL data** | `D:\SaaS\CRM\data` | None | None | SEALED |
| **CI/CD (GitHub Actions)** | `ubuntu-latest` runner | None | None | SEALED |
| **frontend package.json** | No C: paths in scripts | None | None | SEALED |
| **gateway package.json** | No C: paths in scripts | None | None | SEALED |
| **.workspace/ dirs** | `D:\SaaS\CRM\.workspace\*` | None | Created new | SEALED |

---

## New Findings vs. Baseline (2026-06-21)

| Finding | Assessment |
|---------|------------|
| Root `.npmrc` was absent | Minor gap — no active leakage since env var wins, but fresh clone without env var would default to C:. **Fixed**: root .npmrc created. |
| All other items | Unchanged — confirmed SEALED |

**No C: leakage found or unresolved.**

---

## Legend

| Status | Meaning |
|--------|---------|
| **SEALED** | Confirmed writing to D: or neutral |
| **LEAKING** | Confirmed writing to C: |
| **RISK** | Default would write to C:, no redirect confirmed |
| **NOT PRESENT** | Tool not installed or not used |
