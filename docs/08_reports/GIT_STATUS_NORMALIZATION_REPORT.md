# GIT STATUS NORMALIZATION REPORT
Generated: 2026-06-24

## Change Classification

### Staged for Commit (Legitimate Changes)

#### New Documentation Files (docs/)
- `docs/00_authority/` — 6 authority files (COMMERCIALISATION-PLAN, DOMAIN_MODEL, FEATURE_SCOPE, FULLSTACK_STITCHING_CONTRACT, PRODUCT_WORKFLOWS, PROJECT_CHARTER)
- `docs/01_backend/` — 9 backend authority docs (API_CONTRACT, BACKEND_ARCHITECTURE, DATABASE_SCHEMA, etc.)
- `docs/02_frontend/README.md`
- `docs/03_frontend_authority/` — 16 frontend authority docs including L0 freeze pack
- `docs/03_fullstack_contracts/` — 7 contract docs
- `docs/04_testing/SKIP-BACKLOG.md`
- `docs/05_deployment/README.md`
- `docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md`
- `docs/07_governance/` — 6 governance policy docs
- `docs/08_reports/` — 90+ report files
- `docs/09_project_memory/` — 8 project memory registers
- `docs/archive/` — archived root-level docs
- `docs/reference/RENDER-DEPLOY.md`

#### New Backend Docs (backend/docs/)
- Renamed from `backend/*.md` to `backend/docs/*.md` (BACKEND-QC, CONSTRAINTS, FRONTEND-BACKEND-MAPPING, PENDING)
- Renamed from `backend/*.md` to `backend/docs/*.md` (market-research-gap-register, product-spec-gap-register)
- Modified: `backend/docs/architecture/architecture-overview.md`
- Modified: `backend/docs/architecture/domain-model.md`

#### Infrastructure Changes
- `.github/workflows/deploy-runtime.yml` — renamed from `backend/.github/workflows/`
- `.npmrc` — npm cache path sealed to D: drive
- `.gitignore` — hardened patterns

#### Source Code Changes
- `CLAUDE.md` — updated project instructions
- `FRAMEWORK.md` — updated framework spec
- `README.md` — updated project readme
- `frontend/src/assets/js/app/crm-shell.js` — sidebar fix + DUMMY_MODE fallback
- `_archive/README.md` — archive index

#### Generated Artifact Deletions (Correct — removing from tracking)
- 9 `tests/api/__pycache__/*.pyc` — staged as DELETED
- 8 `tests/e2e/playwright/__pycache__/*.pyc` — staged as DELETED
- 130+ `tests/e2e/playwright/screenshots/*.png` — staged as DELETED
- `tests/load/__pycache__/locustfile.cpython-312.pyc` — staged as DELETED

#### New Test File
- `tests/e2e/playwright/test_prod_smoke.py` — production smoke test

### Not Staged (Correctly Excluded)
- `node_modules/` — covered by .gitignore
- `backend/.venv/` — covered by .gitignore
- `data/postgres/` — covered by .gitignore
- `bin/pgsql/` — covered by .gitignore
- `Prompts/` — left untracked (prompt files, not source)

## Staging Commands Run
```bash
git add docs/
git add backend/docs/
git add .gitignore
git add .npmrc
git add .github/workflows/deploy-runtime.yml
git add -u   # staged all tracked modifications and deletions
git add tests/e2e/playwright/test_prod_smoke.py
git add _archive/README.md
```

## Final Staged Summary
354 files changed: 42,032 insertions(+), 257 deletions(-)

## Verdict: STATUS NORMALIZED
All legitimate changes staged. Generated artifacts staged as deletions. No junk in staging area.
