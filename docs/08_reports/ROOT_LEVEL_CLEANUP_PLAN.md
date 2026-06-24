# ROOT LEVEL CLEANUP PLAN
**Generated:** 2026-06-22
**Target:** D:\SaaS\CRM\ (root directory)
**Goal:** Root should contain only essential config files, README.md, CLAUDE.md, and key authority docs

---

## CURRENT ROOT INVENTORY

| Item | Type | Should Stay? | Proposed Destination | Risk | Action |
|------|------|-------------|---------------------|------|--------|
| `CLAUDE.md` | Authority doc | YES | Root | None | Keep |
| `DESIGN-SPEC.md` | Authority doc | YES | Root | None | Keep |
| `FRAMEWORK.md` | Authority doc | YES | Root | None | Keep |
| `PAGE-BUILD-PROTOCOL.md` | Authority doc | YES | Root | None | Keep |
| `PRODUCT-SPEC.md` | Authority doc | YES | Root | None | Keep |
| `README.md` | Project doc | YES | Root | None | Keep |
| `CONTRIBUTING.md` | Contributing guide | YES | Root | None | Keep |
| `render.yaml` | Deployment config | YES | Root | None | Keep |
| `.pre-commit-config.yaml` | Dev tooling | YES | Root | None | Keep |
| `.gitignore` | Version control | YES | Root | None | Keep + UPDATE |
| `Makefile` | Build automation | YES | Root | None | Keep |
| `COMMERCIALISATION-PLAN.md` | Strategic doc | NO | `docs/00_authority/` | Low — no code references | MOVE (SAFE) |
| `seal.ps1` | PowerShell script | NO | `bin/` or scripts folder | Low — verify no path deps | MOVE (SAFE — verify first) |
| `gw.log` | Runtime log | NO | .gitignore | None — log file | ADD TO .gitignore |
| `gateway_startup.log` | Runtime log | NO | .gitignore | None — log file | ADD TO .gitignore |
| `gateway_err.log` | Runtime log | NO | .gitignore | None — log file | ADD TO .gitignore |
| `.env.local` | Local env secrets | NO | Already .gitignored via `.env.local` pattern | High — verify pattern works | VERIFY .gitignore coverage |
| `AUDIT REMEDIATION.md` | Prompt doc (untracked) | NO | `Prompts/Main/` (copy exists) | None | DELETE root copy or add to .gitignore |
| `DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md` | Prompt doc (untracked) | NO | `Prompts/Main/` (copy exists) | None | DELETE root copy or add to .gitignore |
| `GOVERNANCE IMPLEMENTATION PHASE 1.md` | Prompt doc (untracked) | NO | `Prompts/Main/` (copy exists) | None | DELETE root copy or add to .gitignore |
| `PHASE 1 GOVERNANCE VALIDATION.md` | Prompt doc (untracked) | NO | `Prompts/Main/` (copy exists) | None | DELETE root copy or add to .gitignore |
| `PROMPT SEQUENCE.md` | Prompt doc (untracked) | NO | `Prompts/Main/` (copy exists) | None | DELETE root copy or add to .gitignore |
| `FULL REPOSITORY NORMALIZATION AND REALITY AUDIT.md` | Prompt doc (untracked) | NO | `Prompts/Main/` | None | DELETE root copy or add to .gitignore |
| `backend/` | Source code | YES | Root | None | Keep |
| `frontend/` | Source code | YES | Root | None | Keep |
| `tests/` | Test suite | YES | Root | None | Keep |
| `docs/` | Documentation | YES | Root | None | Keep |
| `Prompts/` | Prompt library | CONDITIONAL | Rename to `prompts/` | Low — no import deps | RENAME to `prompts/` (lowercase) |
| `bin/` | PostgreSQL binaries | NO | .gitignore | HIGH — large tracked binary | REQUIRES_OWNER_APPROVAL |
| `data/` | PostgreSQL data | NO | .gitignore | HIGH — live DB data in git | REQUIRES_OWNER_APPROVAL |
| `_archive/` | Redundant archive | NO | Merge → `docs/archive/` | Low | MERGE + REMOVE |
| `c-seal/` | Seal artifacts | HIDDEN | Already .gitignored | None | Keep (.gitignored) |
| `logs/` | Runtime logs | NO | .gitignore | None | ADD TO .gitignore |
| `.github/` | CI/CD | YES | Root | None | Keep |
| `.claude/` | AI tooling config | YES | Root | None | Keep |
| `.semgrep/` | Security policies | YES | Root | None | Keep |
| `.pytest_cache/` | Build artifact | NO | Add to .gitignore | None | ADD TO .gitignore |
| `.npm-cache/` | Build artifact | HIDDEN | Already .gitignored | None | Keep (.gitignored) |
| `.pip-cache/` | Build artifact | HIDDEN | Already .gitignored | None | Keep (.gitignored) |
| `.playwright-browsers/` | Browser binaries | HIDDEN | Already .gitignored | None | Keep (.gitignored) |

---

## .GITIGNORE ADDITIONS REQUIRED

The following entries need to be added to `D:\SaaS\CRM\.gitignore`:

```gitignore
# ---- ADDITIONS REQUIRED ----

# Local environment secrets
.env.local

# Root-level log files (explicit in case *.log pattern doesn't apply)
gw.log
gateway_startup.log
gateway_err.log
gateway_err.log

# Logs directory
logs/

# Root pytest cache
.pytest_cache/

# PostgreSQL runtime data (REQUIRES_OWNER_APPROVAL before adding)
# bin/
# data/

# Frontend dev server log
frontend/dev-server.log

# Backend coverage artifacts
backend/.coverage
.coverage

# Playwright test artifacts
tests/e2e/playwright/screenshots/
tests/e2e/playwright/*.txt
tests/e2e/playwright/__pycache__/

# Load test reports
tests/load/reports/

# API test pycache
tests/api/__pycache__/
tests/load/__pycache__/

# Gateway runtime log
backend/gateway/gateway.log

# Root untracked prompt docs (if keeping canonical in Prompts/Main/)
"AUDIT REMEDIATION.md"
"DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md"
"GOVERNANCE IMPLEMENTATION PHASE 1.md"
"PHASE 1 GOVERNANCE VALIDATION.md"
"PROMPT SEQUENCE.md"
"FULL REPOSITORY NORMALIZATION AND REALITY AUDIT.md"
```

---

## SAFE MOVES — ROOT LEVEL

These can be executed without owner approval (documentation only, no code impact):

### Move 1: COMMERCIALISATION-PLAN.md → docs/00_authority/
- **From:** `D:\SaaS\CRM\COMMERCIALISATION-PLAN.md`
- **To:** `D:\SaaS\CRM\docs\00_authority\COMMERCIALISATION-PLAN.md`
- **Risk:** Low. No code imports this file. It is referenced in CLAUDE.md context only. Update any cross-references.

### Move 2: Merge _archive/ → docs/archive/
- **Action:** Read `_archive/README.md`, check if content is unique vs docs/archive/ content, then move and delete `_archive/`
- **Risk:** None. `_archive/` contains only one file.

---

## REQUIRES_OWNER_APPROVAL

### Item A: bin/ directory
- **Problem:** 4,416 binary files (PostgreSQL 16 binaries) tracked in git
- **Evidence:** `bin/pgsql/` + `bin/pg16-binaries.zip`
- **Proposed fix:** Add `bin/` to `.gitignore`, then `git rm -r --cached bin/`
- **Risk:** Removes ~4,416 files from git history. CI/CD must not depend on bin/ path. Local PostgreSQL must be available by other means (PATH, Docker, or documented install step).
- **Blocking question:** Is `bin/pgsql` referenced in any Makefile target, deployment script, or README installation step?

### Item B: data/ directory
- **Problem:** 1,723 binary files (live PostgreSQL data directory) tracked in git
- **Evidence:** `data/postgres/pg_wal/`, `data/postgres/base/`, `postmaster.pid` etc.
- **Proposed fix:** Add `data/` to `.gitignore`, then `git rm -r --cached data/`
- **Risk:** Same as bin/. The PostgreSQL data directory should be initialized locally, not from git. Committing postmaster.pid and WAL files is dangerous.
- **Blocking question:** Is `data/postgres` path hardcoded in any connection string, config file, or startup script?

### Item C: backend/.github/ vs root .github/
- **Problem:** GitHub Actions only reads `.github/workflows/` at repository root. `backend/.github/workflows/deploy-runtime.yml` may not execute.
- **Proposed fix:** Move `backend/.github/workflows/deploy-runtime.yml` to `.github/workflows/deploy-runtime.yml`
- **Risk:** Medium. Could affect deployment pipeline. Must be tested in staging.

---

## CLEAN ROOT — TARGET STATE

After executing all safe moves and owner-approved changes, the root should contain:

```
D:\SaaS\CRM\
├── .github/                    # CI/CD workflows
├── .claude/                    # Claude Code settings
├── .semgrep/                   # Security scan policies
├── backend/                    # Backend source + tests + docs
├── frontend/                   # Frontend source + assets
├── tests/                      # E2E + API + load + security tests
├── docs/                       # All project documentation
├── prompts/                    # AI prompt library (renamed from Prompts/)
├── .gitignore                  # Updated
├── .pre-commit-config.yaml     # Pre-commit hooks
├── Makefile                    # Build automation
├── render.yaml                 # Deployment config
├── README.md                   # Project overview
├── CLAUDE.md                   # AI build instructions (authority)
├── DESIGN-SPEC.md              # Page design specification (authority)
├── FRAMEWORK.md                # Frontend build protocol (authority)
├── PAGE-BUILD-PROTOCOL.md      # Build protocol (authority)
└── PRODUCT-SPEC.md             # Product specification (authority)
```

Moved to docs/:
- `COMMERCIALISATION-PLAN.md` → `docs/00_authority/`

Removed from root (gitignored or merged):
- `gw.log`, `gateway_startup.log`, `gateway_err.log`
- `.env.local` (verify coverage)
- `logs/`
- `_archive/` (merged)
- 6 untracked prompt .md files
- `bin/` and `data/` (REQUIRES_OWNER_APPROVAL)
- `seal.ps1` (moved to scripts/ or bin/)
