# BASELINE COMMIT REPORT
Generated: 2026-06-24

## Commit Details

| Field | Value |
|-------|-------|
| Commit Hash | c89553692 |
| Branch | main |
| Author | synteracloud |
| Co-Author | Claude Sonnet 4.6 |
| Files Changed | 361 |
| Insertions | 42,365 |
| Deletions | 257 |

## Commit Message
```
chore: pre-frontend sealed repository baseline

- Complete governance, backend authority, and frontend authority documentation
- Repository normalization: docs/ restructured into 00_authority through 09_project_memory
- Frontend Authority Capture (Phase 3): 12 authority docs + L0 freeze pack
- Project Memory Layer: 8 registers in docs/09_project_memory/
- Workspace sealing: removed 689 __pycache__ dirs, 5334 .pyc files, 206 screenshots (~380MB)
- Removed pg16-binaries.zip (300MB redundant archive)
- .gitignore hardened, .npmrc sealed to D: drive
- All prompt files relocated to Prompts/Main/
- docs/ reports consolidated into docs/08_reports/
- Baseline git hygiene reports written to docs/08_reports/
```

## Key Changes in Commit

### Documentation Restructure
- `docs/00_authority/` — 6 product authority files
- `docs/01_backend/` — 9 backend authority docs
- `docs/03_frontend_authority/` — 16 frontend authority + L0 freeze docs
- `docs/03_fullstack_contracts/` — 7 fullstack contract docs
- `docs/07_governance/` — 6 governance policy docs
- `docs/08_reports/` — 95+ consolidated report files
- `docs/09_project_memory/` — 8 project memory registers

### File Renames (git rename-detected)
- `COMMERCIALISATION-PLAN.md` → `docs/00_authority/COMMERCIALISATION-PLAN.md`
- `backend/.github/workflows/deploy-runtime.yml` → `.github/workflows/deploy-runtime.yml`
- `backend/BACKEND-QC.md` → `backend/docs/BACKEND-QC.md`
- `backend/CONSTRAINTS.md` → `backend/docs/CONSTRAINTS.md`
- (+ 4 more backend doc renames)

### Generated Artifact Removals
- 148 files removed from git tracking (pyc, pycache, screenshots)

## Git Warnings (Non-Critical)
```
fatal: renaming pack to '...pack' failed: File exists
error: failed to perform geometric repack
error: task 'geometric-repack' failed
```
These are Windows file permission warnings on git's internal optimization process. The commit completed successfully and is not affected.

## Verdict: COMMIT SUCCESSFUL
Hash: c89553692 — pre-frontend sealed repository baseline committed.
