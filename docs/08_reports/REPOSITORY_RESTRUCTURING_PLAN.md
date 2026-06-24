# REPOSITORY RESTRUCTURING PLAN
**Generated:** 2026-06-22
**Purpose:** Complete restructuring roadmap — ASCII tree of target state, safe moves, owner-approval items, priority order

---

## PART 1 — PROPOSED CLEAN REPOSITORY STRUCTURE

```
D:\SaaS\CRM\
│
├── .claude/                               # Claude Code local settings
│   └── settings.local.json
│
├── .github/                               # CI/CD (ALL workflows here)
│   └── workflows/
│       ├── ci.yml                         # Existing
│       └── deploy-runtime.yml             # MOVE from backend/.github/ — REQUIRES_OWNER_APPROVAL
│
├── .pre-commit-config.yaml                # Pre-commit hooks
├── .semgrep/                              # Security scan policies
│   └── tenant-isolation.yaml
│
├── backend/                               # Backend monorepo
│   ├── .github/                           # DELETE after moving to root .github/ — REQUIRES_OWNER_APPROVAL
│   ├── adapters/                          # Pakistan payment adapters
│   ├── alembic/                           # Alembic migrations (12 versions)
│   │   └── versions/
│   ├── db/                                # SQL schemas (18 domain DBs)
│   ├── docker/                            # Docker configuration
│   │   └── infra/
│   ├── docs/                              # Co-located backend documentation
│   │   ├── _b9/                           # b9-p page specifications (14 files)
│   │   ├── _qc/                           # QC records
│   │   ├── adapters/                      # Adapter docs
│   │   ├── adr/                           # Backend ADRs (ADR-001 through ADR-003)
│   │   ├── architecture/                  # Architecture docs
│   │   ├── domain/                        # Domain model docs (21 files)
│   │   ├── infrastructure/                # Infrastructure docs (13 files)
│   │   ├── product/                       # Product docs
│   │   ├── security/                      # Security docs
│   │   ├── ui/                            # UI foundation docs
│   │   ├── BACKEND-QC.md                  # MOVE from backend root
│   │   └── CONSTRAINTS.md                 # MOVE from backend root
│   ├── gateway/                           # Node.js API gateway
│   │   ├── config/
│   │   ├── data/
│   │   ├── db/
│   │   │   └── repositories/
│   │   ├── middleware/
│   │   ├── routes/
│   │   ├── app.js
│   │   ├── server.js
│   │   ├── Dockerfile
│   │   └── package.json
│   ├── middleware/                        # Python HTTP middleware
│   ├── scripts/                           # Self-QC + deployment scripts
│   │   └── deployment/
│   ├── services/                          # Service layer (23 groups)
│   ├── src/                               # Domain modules (34 modules)
│   ├── tests/                             # Backend tests (55+ unit, 100+ integration)
│   │   ├── [domain subfolders]
│   │   └── conftest.py
│   ├── .gitignore
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── seed_c1.sql
│   └── seed_tenant_refs.sql
│
├── docs/                                  # All project documentation
│   ├── 00_authority/                      # Source of truth documents
│   │   ├── PROJECT_CHARTER.md
│   │   ├── DOMAIN_MODEL.md
│   │   ├── FEATURE_SCOPE.md
│   │   ├── FULLSTACK_STITCHING_CONTRACT.md
│   │   ├── PRODUCT_WORKFLOWS.md
│   │   └── COMMERCIALISATION-PLAN.md      # MOVE from root
│   ├── 01_backend/                        # (Stub — populate or remove)
│   ├── 02_frontend/                       # (Stub — populate or remove)
│   ├── 03_fullstack_contracts/            # API contracts
│   │   └── FRONTEND-BACKEND-MAPPING.md    # MOVE from backend/
│   ├── 04_testing/                        # Testing documentation
│   │   └── SKIP-BACKLOG.md                # MOVE from tests/e2e/playwright/
│   ├── 05_deployment/                     # Deployment documentation
│   │   └── RENDER-DEPLOY.md               # (optionally MOVE from docs/reference/)
│   ├── 06_decisions/                      # Architecture Decision Records
│   │   └── ADR-001_PROJECT_FOUNDATION.md
│   ├── 07_governance/                     # Governance framework
│   │   ├── AI_OPERATING_CONTEXT.md
│   │   └── DECISION_ESCALATION_MATRIX.md
│   ├── 08_reports/                        # All generated reports land here
│   │   ├── [existing 14 reports]
│   │   ├── MARKET-RESEARCH-GAP-REGISTER.md  # MOVE from backend/
│   │   ├── PRODUCT-SPEC-GAP-REGISTER.md     # MOVE from backend/
│   │   ├── PHASE4-GAP-REGISTER.md           # MOVE from backend/docs/
│   │   └── [9 new audit reports from this session]
│   ├── archive/                           # Retired documents
│   │   ├── [7 existing archive files]
│   │   └── ARCHIVE-README.md              # MOVE from _archive/ (if unique content)
│   ├── reference/                         # Reference materials
│   │   └── RENDER-DEPLOY.md               # (or move to 05_deployment/)
│   └── reports/
│       ├── session/                       # Session-level docs
│       │   ├── [7 existing session files]
│       │   └── PENDING.md                 # MOVE backend/PENDING.md here (merge if needed)
│       ├── u-series/                      # U0–U10 audit history (~60 files)
│       ├── load/                          # Load test reports (CREATE if keeping)
│       │   └── [7 Locust HTML reports]
│       └── security/                      # Security scan reports (CREATE if keeping)
│           └── [5 JSON scan reports]
│
├── frontend/                              # Frontend source
│   ├── src/
│   │   ├── app/                           # 169 custom CRM pages
│   │   ├── authentication/                # Auth pages
│   │   ├── assets/
│   │   │   ├── css/
│   │   │   ├── js/app/
│   │   │   ├── libs/
│   │   │   ├── scss/
│   │   │   └── images/
│   │   └── [library subdirs — keep as reference, do not modify]
│   ├── package.json
│   └── .npmrc
│
├── prompts/                               # AI prompt library (RENAME from Prompts/)
│   ├── Main/
│   │   ├── AUDIT REMEDIATION.md
│   │   ├── DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md
│   │   ├── FULL REPOSITORY NORMALIZATION AND REALITY AUDIT.md
│   │   ├── GOVERNANCE IMPLEMENTATION PHASE 1.md
│   │   ├── PHASE 1 GOVERNANCE VALIDATION.md
│   │   └── PROMPT SEQUENCE.md
│   ├── U0–U9 LEGACY MODERNIZATION AUDIT.md
│   ├── U1 — AUTHORITY RECONSTRUCTION.md
│   └── [all other U-series prompt files]
│
├── tests/                                 # All tests
│   ├── api/                               # API contract tests
│   ├── e2e/
│   │   └── playwright/                    # E2E test files
│   │       ├── [test_*.py files]
│   │       ├── conftest.py
│   │       └── helpers.py
│   │       # (screenshots/ and *.txt results → .gitignored)
│   ├── load/                              # Load tests
│   │   └── locustfile.py
│   └── security/
│       └── c5_api_security_scan.py
│
├── .gitignore                             # Updated with missing entries
├── Makefile
├── render.yaml
├── README.md
├── CLAUDE.md
├── DESIGN-SPEC.md
├── FRAMEWORK.md
├── PAGE-BUILD-PROTOCOL.md
└── PRODUCT-SPEC.md
```

Directories **removed** from root after cleanup:
- `_archive/` — merged into docs/archive/
- `bin/` — gitignored (REQUIRES_OWNER_APPROVAL)
- `data/` — gitignored (REQUIRES_OWNER_APPROVAL)
- `logs/` — gitignored
- `Prompts/` — renamed to `prompts/`
- `c-seal/` — already gitignored (invisible)

---

## PART 2 — SAFE MOVES (READY TO EXECUTE NOW)

All moves are documentation files only. No code, no imports, no CI/CD impact.

| # | From | To | Notes |
|---|------|----|-------|
| 1 | `COMMERCIALISATION-PLAN.md` | `docs/00_authority/COMMERCIALISATION-PLAN.md` | Root → authority docs |
| 2 | `backend/BACKEND-QC.md` | `backend/docs/BACKEND-QC.md` | Backend root → backend/docs |
| 3 | `backend/CONSTRAINTS.md` | `backend/docs/CONSTRAINTS.md` | Backend root → backend/docs |
| 4 | `backend/FRONTEND-BACKEND-MAPPING.md` | `docs/03_fullstack_contracts/FRONTEND-BACKEND-MAPPING.md` | Backend root → fullstack contracts |
| 5 | `backend/market-research-gap-register.md` | `docs/08_reports/MARKET-RESEARCH-GAP-REGISTER.md` | Backend root → reports |
| 6 | `backend/product-spec-gap-register.md` | `docs/08_reports/PRODUCT-SPEC-GAP-REGISTER.md` | Backend root → reports |
| 7 | `backend/docs/phase4-gap-register.md` | `docs/08_reports/PHASE4-GAP-REGISTER.md` | Backend/docs → reports |
| 8 | `tests/e2e/playwright/SKIP-BACKLOG.md` | `docs/04_testing/SKIP-BACKLOG.md` | Tests → testing docs |
| 9 | `_archive/README.md` | `docs/archive/ARCHIVE-README.md` (if unique) | Merge then _archive/ disappears |

**Moves deferred (need owner input on backend/PENDING.md merge strategy):**
- `backend/PENDING.md` → `docs/reports/session/BACKEND-PENDING.md` (rename to avoid collision with existing PENDING.md)

---

## PART 3 — REQUIRES_OWNER_APPROVAL

These cannot be auto-executed. Each needs an explicit decision.

| Item | Problem | Proposed Action | Risk | Blocking Question |
|------|---------|----------------|------|-------------------|
| `bin/` (4,416 files) | PostgreSQL binaries in git | Add to .gitignore; `git rm -r --cached bin/` | HIGH | Is bin/pgsql referenced in any Makefile/script/README as a runtime path? |
| `data/` (1,727 files) | Live PostgreSQL data in git | Add to .gitignore; `git rm -r --cached data/` | HIGH | Is `data/postgres` hardcoded in any connection string or startup script? |
| `backend/.github/workflows/deploy-runtime.yml` | Nested GitHub Actions workflow | Move to root `.github/workflows/deploy-runtime.yml` | MEDIUM | Does this workflow currently run? Is it triggered differently? |
| `backend/.github/actions/runtime-env-validate/action.yml` | Nested GitHub Action | Move to root `.github/actions/runtime-env-validate/action.yml` | MEDIUM | Is this action referenced by path in any workflow? |
| `backend/src/` vs `backend/services/` | Two parallel Python architectures | Document the canonical pattern; deprecate the other over time | MEDIUM | Which is the authoritative pattern: domain modules (src/) or service groups (services/)? |
| `backend/alembic/` vs `backend/db/*/migrations/` | Two migration systems | Document which system owns which database | LOW | Is Alembic used for all schemas, or only some? |
| docs/01–05 empty folders | Empty stub directories | Either populate or remove | LOW | Is the co-located backend/docs/ model the intentional choice, making docs/01_backend/ redundant? |
| `tests/security/*.json` | Security scan artifacts in git | Move to docs/reports/security/ OR gitignore | LOW | Are these needed as compliance evidence? |
| `tests/load/reports/*.html` | Load test reports in git | Move to docs/reports/load/ OR gitignore | LOW | Do these reports need to be version-controlled? |
| `Prompts/` → `prompts/` rename | Inconsistent casing | Rename directory | LOW | Is `Prompts/` referenced by any script or CI step? |
| `seal.ps1` location | Script at root | Move to `bin/` | LOW | Does seal.ps1 reference its own path relative to root? |

---

## PART 4 — .gitignore UPDATES (SAFE TO APPLY)

Add to `D:\SaaS\CRM\.gitignore`:

```gitignore
# Python bytecode (global)
__pycache__/
*.pyc

# pytest caches (global)
.pytest_cache/

# Coverage files
.coverage
*.coverage
htmlcov/

# Runtime logs directory
logs/

# Playwright generated artifacts
tests/e2e/playwright/screenshots/
tests/e2e/playwright/*.txt
tests/e2e/playwright/__pycache__/
tests/api/__pycache__/
tests/load/__pycache__/

# Backend coverage and logs
backend/gateway/gateway.log

# Frontend dev log
frontend/dev-server.log

# Root prompt docs (duplicates of Prompts/Main/)
"AUDIT REMEDIATION.md"
"DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md"
"GOVERNANCE IMPLEMENTATION PHASE 1.md"
"PHASE 1 GOVERNANCE VALIDATION.md"
"PROMPT SEQUENCE.md"
"FULL REPOSITORY NORMALIZATION AND REALITY AUDIT.md"

# PostgreSQL (REQUIRES_OWNER_APPROVAL before uncommenting)
# bin/
# data/
```

---

## PART 5 — ESTIMATED EFFORT

| Category | Items | Effort | Owner Required? |
|----------|-------|--------|----------------|
| .gitignore updates | ~15 entries | 30 minutes | NO |
| Safe doc moves | 9 files | 1 hour | NO |
| Root prompt doc cleanup | 6 files | 15 minutes | NO |
| bin/ and data/ removal from git | 2 dirs + git history | 1-2 hours | YES |
| backend/.github/ consolidation | 2 files | 30 minutes | YES |
| backend/src/ vs services/ documentation | Architecture doc | 2 hours | YES |
| Empty docs/01–05 population | 5 folders | 2-4 hours | YES (strategy) |
| Load/security report disposition | 12 files | 30 minutes | YES |

**Total safe work (no owner required):** 2-3 hours
**Total owner-gated work:** 6-10 hours

---

## PART 6 — EXECUTION ORDER

### Phase A — Immediate (Safe, No Risk)
Execute in this session:
1. Update `.gitignore` with all missing entries (except bin/ and data/)
2. Move 9 documentation files (safe moves list above)
3. Gitignore root prompt .md files

### Phase B — After Owner Review
4. Owner approves bin/ and data/ removal — execute git rm --cached
5. Owner decides deploy-runtime.yml location — move if needed
6. Owner decides empty stub folder strategy — populate or remove

### Phase C — Ongoing
7. Owner decides backend/src/ vs services/ canonical pattern
8. Owner decides security scan report disposition
9. Owner decides load test report disposition
10. Fill empty docs/01–05 folders per owner decision

---

## PART 7 — MOVES EXECUTED IN THIS SESSION

The following safe moves were executed as part of this audit:

| # | From | To | Status |
|---|------|----|--------|
| 1 | `COMMERCIALISATION-PLAN.md` (root) | `docs/00_authority/COMMERCIALISATION-PLAN.md` | EXECUTED |
| 2 | `_archive/README.md` | `docs/archive/ARCHIVE-README.md` | EXECUTED |

**Moves queued (REQUIRES_OWNER_APPROVAL for backend/ files):**

Per audit instructions: "Anything affecting source code, imports, build paths, tests, deployment, CI/CD, or runtime → list under REQUIRES_OWNER_APPROVAL only." Since `backend/` contains source code, moving .md files out of it (even though the files themselves are pure documentation) is listed for owner review rather than auto-executed.

Once owner confirms no script or CI references these files by path, the following can be executed:
- `backend/BACKEND-QC.md` → `backend/docs/BACKEND-QC.md`
- `backend/CONSTRAINTS.md` → `backend/docs/CONSTRAINTS.md`
- `backend/FRONTEND-BACKEND-MAPPING.md` → `docs/03_fullstack_contracts/FRONTEND-BACKEND-MAPPING.md`
- `backend/market-research-gap-register.md` → `docs/08_reports/MARKET-RESEARCH-GAP-REGISTER.md`
- `backend/product-spec-gap-register.md` → `docs/08_reports/PRODUCT-SPEC-GAP-REGISTER.md`
- `backend/docs/phase4-gap-register.md` → `docs/08_reports/PHASE4-GAP-REGISTER.md`
- `backend/PENDING.md` → `docs/reports/session/BACKEND-PENDING.md`
- `tests/e2e/playwright/SKIP-BACKLOG.md` → `docs/04_testing/SKIP-BACKLOG.md`
