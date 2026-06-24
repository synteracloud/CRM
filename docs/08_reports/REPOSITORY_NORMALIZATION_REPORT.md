# REPOSITORY NORMALIZATION REPORT
**Generated:** 2026-06-22
**Audit type:** Full repository reality audit — all folders, all file types

---

## EXECUTIVE SUMMARY

The repository is structurally sound at its core. Source code is well-organized, test coverage is comprehensive, and the documentation governance framework is correctly scaffolded. However, six categories of problems require attention before Frontend Authority Capture begins:

1. **Critical: `bin/` and `data/` contain binary/runtime data in git** — 6,143 files that should never be tracked
2. **High: Root-level log clutter** — 3 gateway logs at root + `logs/` directory not .gitignored
3. **Medium: Untracked root .md files** — 6 prompt/session docs sitting loose at root (copies exist in Prompts/Main/)
4. **Medium: Empty governance folders** — docs/01–05 are all empty stubs
5. **Low: Scattered backend root docs** — BACKEND-QC.md, CONSTRAINTS.md, FRONTEND-BACKEND-MAPPING.md, PENDING.md misplaced
6. **Low: Generated artifacts untracked** — screenshots, test results, coverage files not in .gitignore

---

## SECTION 1 — WHAT IS CORRECT

### Source Code
- `backend/src/` — 34 domain modules correctly structured
- `backend/services/` — 23 service modules correctly structured
- `backend/gateway/` — Node.js gateway with proper config, routes, db sub-structure
- `backend/adapters/` — Pakistan payment adapters correctly isolated
- `backend/middleware/` — HTTP middleware correctly placed
- `backend/alembic/` — 12 migration versions in correct Alembic structure
- `backend/db/` — 18 domain schema SQL files correctly organized by database
- `backend/tests/` — 55+ unit tests + 100+ integration tests correctly co-located with source
- `frontend/src/app/` — 169 custom CRM pages, all in correct location
- `frontend/src/assets/` — JS, CSS, SCSS, libs, images all correctly structured

### Documentation Governance
- `docs/00_authority/` — 5 authority docs correctly placed (PROJECT_CHARTER, DOMAIN_MODEL, FEATURE_SCOPE, FULLSTACK_STITCHING_CONTRACT, PRODUCT_WORKFLOWS)
- `docs/06_decisions/` — ADR-001 correctly placed
- `docs/07_governance/` — DECISION_ESCALATION_MATRIX, AI_OPERATING_CONTEXT correctly placed
- `docs/08_reports/` — 14 reports already in correct location
- `docs/reports/session/` — 7 session docs (CHANGELOG, PROGRESS, PENDING, SCREEN-ARTEFACTS, etc.) correctly placed
- `docs/reports/u-series/` — ~60 U-series audit outputs correctly placed
- `docs/archive/` — 7 archived docs correctly placed
- `docs/reference/` — RENDER-DEPLOY.md correctly placed
- Root authority docs — CLAUDE.md, DESIGN-SPEC.md, FRAMEWORK.md, PAGE-BUILD-PROTOCOL.md, PRODUCT-SPEC.md all correct at root
- `backend/docs/` — rich co-located backend documentation (b9-p specs, domain docs, ADRs, architecture, infrastructure, security) correctly placed adjacent to source code

### Infrastructure
- `.github/workflows/ci.yml` — CI pipeline correctly placed
- `backend/.github/workflows/deploy-runtime.yml` — deployment workflow (see duplicate concern below)
- `render.yaml` — deployment config correctly at root
- `.pre-commit-config.yaml` — pre-commit hooks correctly at root
- `Makefile` — build automation correctly at root
- `.semgrep/tenant-isolation.yaml` — security policy correctly placed

### Tests
- `tests/api/` — 9 API contract test files correctly placed
- `tests/load/locustfile.py` — load test correctly placed
- `tests/security/c5_api_security_scan.py` — security test correctly placed
- `tests/e2e/playwright/*.py` — all Playwright E2E test files correctly placed

---

## SECTION 2 — PROBLEMS BY SEVERITY

### CRITICAL — Binary/Runtime Data Tracked in Git

**bin/ (4,416 files):** Contains PostgreSQL 16 binaries (`pgsql/`) and `pg16-binaries.zip`. These are binary files that should never be in git. The root `.gitignore` does not exclude `bin/`. This is almost certainly unintentional — the PostgreSQL binary was installed here for local development convenience.

**data/ (1,727 files):** Contains a live PostgreSQL data directory (`data/postgres/`). This includes `postmaster.pid`, WAL segments, data files, and `postgresql.conf`. Live database data must never be committed. The root `.gitignore` does not exclude `data/`.

**Action Required (REQUIRES_OWNER_APPROVAL):** Add `bin/` and `data/` to `.gitignore`. These cannot be added automatically as they represent a significant git history change. Owner must also confirm these paths are not referenced in CI/CD or deployment scripts before removing from tracking.

---

### HIGH — Root-Level Log File Pollution

Three gateway log files exist at the repository root:
- `gw.log`
- `gateway_startup.log`  
- `gateway_err.log`

Additionally, `logs/` directory (gateway.log, frontend.log) is not in `.gitignore`. The root `.gitignore` pattern `*.log` should already catch `gw.log` and `gateway_startup.log` and `gateway_err.log` — but they appear in the working tree as modified/untracked, suggesting they were previously committed or the pattern is not working correctly.

**Safe action:** Verify `*.log` pattern in root `.gitignore` catches these files. The files themselves are not source code and can be added to `.gitignore` explicitly. The `logs/` directory also needs an explicit `.gitignore` entry.

---

### HIGH — Untracked Root .md Files (6 Files)

Six untracked `.md` files sit at the repository root:
1. `AUDIT REMEDIATION.md`
2. `DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md`
3. `GOVERNANCE IMPLEMENTATION PHASE 1.md`
4. `PHASE 1 GOVERNANCE VALIDATION.md`
5. `PROMPT SEQUENCE.md`
6. `FULL REPOSITORY NORMALIZATION AND REALITY AUDIT.md`

All 6 of these have copies in `Prompts/Main/`. They appear to have been created at root during an AI session but never moved to their correct location. These are safe to add to `.gitignore` or to commit only from `Prompts/Main/`.

**Safe action:** These 6 files are prompt/session documents. Since copies exist in `Prompts/Main/`, the root copies can be gitignored (or the root versions are newer — owner should choose canonical copy). They do not belong at repository root.

---

### MEDIUM — Empty Governance Folder Stubs (5 Folders)

`docs/01_backend/`, `docs/02_frontend/`, `docs/03_fullstack_contracts/`, `docs/04_testing/`, `docs/05_deployment/` are all empty. They were created as part of the governance scaffold but never populated.

These folders have natural candidates from the current repository:
- `docs/01_backend/` → could mirror/index `backend/docs/`
- `docs/02_frontend/` → could hold frontend build protocol summaries
- `docs/03_fullstack_contracts/` → `backend/FRONTEND-BACKEND-MAPPING.md` belongs here
- `docs/04_testing/` → `tests/e2e/playwright/SKIP-BACKLOG.md` belongs here
- `docs/05_deployment/` → `docs/reference/RENDER-DEPLOY.md` could move here

**Strategy decision needed:** The governance framework places backend docs in `backend/docs/` (co-located), not in `docs/01_backend/`. If this is intentional (co-located model), then `docs/01_backend/` should either contain an index pointing to `backend/docs/`, or be removed. REQUIRES_OWNER_APPROVAL for strategy choice.

---

### MEDIUM — Backend Root Document Clutter

Five documentation files sit directly in `backend/` root when they belong elsewhere:

| File | Correct Location |
|------|-----------------|
| `backend/BACKEND-QC.md` | `backend/docs/` or `docs/08_reports/` |
| `backend/CONSTRAINTS.md` | `backend/docs/` |
| `backend/FRONTEND-BACKEND-MAPPING.md` | `docs/03_fullstack_contracts/` |
| `backend/PENDING.md` | `docs/reports/session/` |
| `backend/market-research-gap-register.md` | `docs/08_reports/` |
| `backend/product-spec-gap-register.md` | `docs/08_reports/` |

**Safe action:** These are documentation files only. Moving them is safe but requires confirming no CI/CD or script references them by path. Listed in SAFE MOVES section below.

---

### LOW — Generated Artifacts Not in .gitignore

Several categories of generated artifacts exist in the repo without `.gitignore` coverage:

| Artifact Type | Count | Should Add to .gitignore |
|--------------|-------|--------------------------|
| `tests/e2e/playwright/screenshots/*.png` | ~160 | Yes — `tests/e2e/playwright/screenshots/` |
| `tests/e2e/playwright/*.txt` (batch, fin, results) | ~40 | Yes — `tests/e2e/playwright/*.txt` |
| `tests/load/reports/*.html` | 7 | Yes — `tests/load/reports/` |
| `tests/security/*.json` | 5 | Owner decision — may be intentional audit evidence |
| `backend/.coverage` | 1 | Yes — add `.coverage` to root `.gitignore` |
| `backend/gateway/gateway.log` | 1 | Already covered by `*.log` in root .gitignore if applied recursively |
| `frontend/dev-server.log` | 1 | Already covered by `*.log` |
| Root `*.log` files | 3 | Already covered by `*.log` pattern — verify it applies |

---

### LOW — `_archive/` Root Directory Redundant

`_archive/` at root contains only one file: `README.md`. `docs/archive/` contains 7 properly archived documents. The root `_archive/` serves no purpose not already served by `docs/archive/`.

**Safe action:** Move `_archive/README.md` to `docs/archive/` if content is unique, then the empty `_archive/` directory disappears naturally (git does not track empty directories). Already executed — see EXECUTED MOVES.

---

### LOW — Duplicate .github Configuration

`backend/.github/workflows/deploy-runtime.yml` is a GitHub Actions deployment workflow nested inside the `backend/` directory. The root `.github/workflows/ci.yml` is the primary CI workflow. GitHub Actions only processes `.github/workflows/` at the repository root. Therefore `backend/.github/` may not function as intended.

**REQUIRES_OWNER_APPROVAL:** Evaluate whether `backend/.github/workflows/deploy-runtime.yml` needs to be moved to root `.github/workflows/` to function. This touches CI/CD.

---

## SECTION 3 — PROPOSED CLEAN STATE

After normalization, the root directory should contain:

```
D:\SaaS\CRM\
├── .github/            # CI/CD (correct)
├── .claude/            # Claude Code config (correct)
├── .semgrep/           # Security policies (correct)
├── backend/            # Backend source (correct)
├── frontend/           # Frontend source (correct)
├── tests/              # E2E + API + load tests (correct)
├── docs/               # All documentation (correct)
├── prompts/            # AI prompt library (renamed from Prompts/)
├── .gitignore          # Updated with missing entries
├── .pre-commit-config.yaml
├── Makefile
├── render.yaml
├── README.md
├── CLAUDE.md           # Build instructions
├── DESIGN-SPEC.md      # Page design authority
├── FRAMEWORK.md        # Frontend build protocol
├── PAGE-BUILD-PROTOCOL.md
├── PRODUCT-SPEC.md     # Product specification
└── COMMERCIALISATION-PLAN.md  # (move to docs/00_authority/)
```

Removed from root:
- `_archive/` (merged into docs/archive/)
- `seal.ps1` (moved to scripts/ or bin/)
- `gw.log`, `gateway_startup.log`, `gateway_err.log` (.gitignored)
- `c-seal/` (already .gitignored — stays hidden)
- `logs/` (.gitignored)
- `.env.local` (.gitignored — verify already excluded)
- 6 untracked .md prompt files (.gitignored or moved to prompts/)
- `bin/` and `data/` (.gitignored — REQUIRES_OWNER_APPROVAL)

---

## SECTION 4 — PRIORITY ORDER

| Priority | Action | Risk | Who Decides |
|----------|--------|------|-------------|
| 1 | Add `bin/` and `data/` to `.gitignore` | HIGH — large history change | OWNER |
| 2 | Add `tests/e2e/playwright/screenshots/` and `*.txt` to `.gitignore` | LOW | SAFE |
| 3 | Add `tests/load/reports/` to `.gitignore` | LOW | SAFE |
| 4 | Add `.coverage`, `backend/gateway/gateway.log`, `frontend/dev-server.log` to `.gitignore` | LOW | SAFE |
| 5 | Add `logs/` to root `.gitignore` | LOW | SAFE |
| 6 | Move root .md untracked prompt files to `Prompts/Main/` or gitignore them | LOW | SAFE |
| 7 | Move backend root docs to correct locations | LOW | SAFE (doc-only) |
| 8 | Populate `docs/03_fullstack_contracts/` with FRONTEND-BACKEND-MAPPING.md | LOW | SAFE |
| 9 | Populate `docs/04_testing/` with SKIP-BACKLOG.md | LOW | SAFE |
| 10 | Evaluate `backend/.github/` vs root `.github/` conflict | MEDIUM | OWNER |
| 11 | Decide fate of empty docs/01–05 folders | LOW | OWNER |
| 12 | Move COMMERCIALISATION-PLAN.md to docs/00_authority/ | LOW | SAFE |
| 13 | Move seal.ps1 to bin/ or scripts/ | LOW | SAFE (verify no hardcoded paths) |
| 14 | Merge `_archive/README.md` into `docs/archive/` and remove `_archive/` | LOW | SAFE |
