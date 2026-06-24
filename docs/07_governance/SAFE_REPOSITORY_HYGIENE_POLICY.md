Status: Active
Authority Level: High
Owner: Shared
Last Reviewed: 2026-06-22

---

# SAFE_REPOSITORY_HYGIENE POLICY — Pakistan CRM OS

## Purpose

This document defines the SAFE_REPOSITORY_HYGIENE execution tier introduced in the June 2026 governance refinement. The tier was created because the existing two-tier model (AUTONOMOUS / REQUIRES_APPROVAL) left a policy gap: a large class of low-risk repository improvement actions — file moves, archive maintenance, report relocation, generated artifact cleanup — were classified as REQUIRES_APPROVAL solely because they involved moving files or touching paths outside `docs/`. In practice, these actions carry no risk to runtime behavior, security, data integrity, or deployment, and gating them behind owner approval created unnecessary friction in keeping the repository well-organized.

The SAFE_REPOSITORY_HYGIENE tier formally authorises AI agents to execute this class of action without explicit human sign-off, subject to the qualifying criteria, execution rules, and audit trail requirements stated in this document.

---

## Definition

**SAFE_REPOSITORY_HYGIENE** describes actions that reorganise, clarify, or maintain the repository's file structure and documentation without modifying any file that participates in runtime behavior, API contracts, database state, security enforcement, or deployment.

The distinguishing features of a SAFE_REPOSITORY_HYGIENE action are:

1. The repository works identically before and after the action.
2. No test suite output changes as a result of the action.
3. No CI/CD pipeline behavior changes as a result of the action.
4. No deployed service is affected by the action.
5. The action is fully reversible by moving files back to their original location or reverting the edit.

---

## Position in the Governance Tier Model

```
Tier 0 — AUTONOMOUS              AI acts freely; no record required
Tier 1 — SAFE_REPOSITORY_HYGIENE ← THIS TIER: AI acts freely; brief report required
Tier 2 — REQUIRES_APPROVAL       AI stops and waits for explicit human sign-off
Tier 3 — PROHIBITED              AI refuses regardless of instruction
```

Key distinctions:

**From AUTONOMOUS (Tier 0):** AUTONOMOUS actions are limited to documentation content edits within existing files (fixing wording, updating status fields, adding entries). SAFE_REPOSITORY_HYGIENE additionally permits moving, renaming, or adding notice banners to files — including files outside `docs/` — and adding `.gitignore` entries, provided the qualifying criteria are met. SAFE_REPOSITORY_HYGIENE requires an audit trail (brief execution report); AUTONOMOUS does not.

**From REQUIRES_APPROVAL (Tier 2):** REQUIRES_APPROVAL covers anything that could affect system behavior: schema changes, auth changes, new API endpoints, infrastructure modifications, deployment configuration, security boundary changes. SAFE_REPOSITORY_HYGIENE never touches any of these. If a candidate action could plausibly affect any of the protected areas listed in AI_OPERATING_CONTEXT.md, it is REQUIRES_APPROVAL, not SAFE_REPOSITORY_HYGIENE.

---

## Qualifying Criteria

An action qualifies as SAFE_REPOSITORY_HYGIENE if and only if ALL of the following are true:

### Must Not criteria (any single failure disqualifies the action)

| # | Criterion |
|---|-----------|
| MN-1 | Does NOT modify business logic in any source code file (.py, .js, .ts, .sql) |
| MN-2 | Does NOT modify API contracts (route definitions, request/response shapes, HTTP methods) |
| MN-3 | Does NOT modify database structure (schema.sql, Alembic migrations, constraint definitions) |
| MN-4 | Does NOT modify runtime behavior (middleware, auth, RBAC, rate limiting, webhook handlers) |
| MN-5 | Does NOT modify infrastructure configuration (render.yaml, Dockerfiles, docker-compose.yml) |
| MN-6 | Does NOT modify deployment behavior (CI/CD pipelines in .github/workflows/, build commands) |
| MN-7 | Does NOT modify security boundaries (CORS allowlist, helmet config, CSP headers, JTI blocklist) |
| MN-8 | Does NOT modify permissions or authentication (rbac-scopes.js, auth-rbac.js, token logic) |
| MN-9 | Does NOT modify application functionality (any file imported or required by running code) |
| MN-10 | Does NOT delete files from the repository entirely (moves to archive are permitted; deletions are not) |
| MN-11 | Does NOT touch files in PROTECTED_AREAS or DO_NOT_MODIFY_AREAS per AI_OPERATING_CONTEXT.md |
| MN-12 | Does NOT write to C: drive (C0 seal remains in force) |

### Must criteria (all must be satisfied)

| # | Criterion |
|---|-----------|
| M-1 | Actions produce zero change to any test suite output |
| M-2 | Actions produce zero change to any CI/CD pipeline result |
| M-3 | All cross-references to moved files are updated in the same execution run |
| M-4 | An execution report is produced after the run (see Audit Trail Requirement below) |
| M-5 | The action is scoped exclusively to repository organisation, documentation quality, or artifact cleanup |

---

## Disqualifying Criteria

Any of the following immediately escalates an action to REQUIRES_APPROVAL regardless of how the action is described:

| Trigger | Escalation Reason |
|---------|------------------|
| The file is imported by any .py, .js, or .ts file | It participates in runtime; moving it may break imports |
| The file path is referenced in any .github/workflows/ file | Moving it changes CI/CD behavior |
| The file path is referenced in render.yaml, any Dockerfile, or docker-compose.yml | Moving it changes deployment behavior |
| The file contains executable code that is run directly (scripts called from Makefile, CI, startup) | It is not a passive document |
| The action would remove a file from git tracking that is referenced by runtime code | Potential runtime breakage |
| The action affects rbac-scopes.js, auth-rbac.js, jti-blocklist.js, or any middleware file | PROTECTED_AREA per AI_OPERATING_CONTEXT.md |
| The action affects .github/workflows/ci.yml | PROTECTED_AREA per AI_OPERATING_CONTEXT.md |
| The action affects backend/alembic/versions/ | PROTECTED_AREA per AI_OPERATING_CONTEXT.md |
| Uncertainty exists about whether a dependency exists | Default to REQUIRES_APPROVAL (escalation rule below) |

---

## Full Action List — SAFE_REPOSITORY_HYGIENE Authorised Actions

The following actions are formally classified as SAFE_REPOSITORY_HYGIENE. AI agents may execute any action on this list without seeking prior human approval, subject to the qualifying criteria above and the execution rules below.

### Category A — Documentation Relocation

| Action | Scope | Condition |
|--------|-------|-----------|
| Move .md files between docs/ subfolders | Any .md file in docs/ | File not referenced in CI/CD or runtime code |
| Move .md files from root to docs/ subfolders | Root-level .md files not in the Authority Doc keep list | File not imported or executed by any code |
| Move .md files from backend/ root to backend/docs/ | BACKEND-QC.md, CONSTRAINTS.md, PENDING.md | File not referenced in any Python import or script |
| Move .md files from backend/ to root docs/ | FRONTEND-BACKEND-MAPPING.md, gap registers | Same condition |
| Move .md files from tests/ to docs/ | SKIP-BACKLOG.md and similar planning docs | File not executed by pytest or any CI step |
| Move .md files from Prompts/ to docs/ or docs/archive/ | Completed session prompt files | No code references |

### Category B — Documentation Normalization

| Action | Scope |
|--------|-------|
| Update Status field (Draft → Active, Active → Retired) | Any governance, report, or authority document |
| Update Last Reviewed date field | Any document in docs/ |
| Update Authority Level field to reflect correct tier | Any governance document |
| Update Owner field | Any document in docs/ |
| Add OWNERSHIP block to document missing one | Any document in docs/ |
| Fix typos and grammar in any .md file | Repository-wide |
| Fix broken internal cross-references (update paths after file moves) | Repository-wide |
| Fix stale doc references (update links pointing to moved files) | Repository-wide |
| Add SUPERSEDED, HISTORICAL, or RETIRED notice banners to archive documents | Any document in docs/archive/ |
| Add redirect banners to stale session documents | docs/reports/session/ files only |
| Add cross-reference notices to documents with authority hierarchy relationships | Any document in docs/ |
| Update "DEFERS TO" entries in OWNERSHIP blocks | Any document in docs/ |

### Category C — Folder Restructuring (Documentation Only)

| Action | Scope | Condition |
|--------|-------|-----------|
| Create new subdirectories within docs/ | docs/ tree only | No impact on CI/CD or runtime |
| Move report files between docs/08_reports/ subdirectories | docs/08_reports/ tree | File not referenced in CI/CD |
| Move session docs between docs/reports/session/ and docs/reports/u-series/ | docs/reports/ tree | File not referenced in runtime |
| Create docs/09_prompts/ or similar new category folder | docs/ tree | Administrative organization only |
| Populate empty stub directories (docs/01_backend/, docs/02_frontend/) | docs/ stub folders | Adding README or index files only |

### Category D — Archive Maintenance

| Action | Scope |
|--------|-------|
| Move .md files to docs/archive/ | Any document confirmed as retired or superseded |
| Add retirement date and notice to archived documents | Any document in docs/archive/ |
| Merge content from redundant archive locations (_archive/ → docs/archive/) | Redundant archive directories only |
| Remove empty directories left after moves | After all content has been moved out |

### Category E — Report Consolidation

| Action | Scope |
|--------|-------|
| Add SUPERSEDED notice to an older report when a newer report covers the same content | Any report in docs/08_reports/ or docs/reports/u-series/ |
| Add cross-reference from one report to its successor | Any report in docs/ |
| Merge two small reports into one when both are AI-generated and content is consistent | docs/08_reports/ only; no authority documents |
| Move generated reports from backend/ or tests/ to docs/08_reports/ | Gap registers, QC reports, scan outputs |

### Category F — Generated Artifact Cleanup

| Action | Scope | Condition |
|--------|-------|-----------|
| Add __pycache__/ entries to .gitignore | Root .gitignore | Add entry only; do not git rm yet |
| Add *.pyc entries to .gitignore | Root .gitignore | Same |
| Add .pytest_cache/ to .gitignore | Root .gitignore | Same |
| Add *.log entries to .gitignore | Root .gitignore | Same |
| Add test artifact paths to .gitignore | tests/e2e/playwright/screenshots/, tests/e2e/playwright/*.txt | Same |
| Add backend/gateway/gateway.log to .gitignore | Root .gitignore | Same |
| Add frontend/dev-server.log to .gitignore | Root .gitignore | Same |
| Execute git rm --cached for .pyc and __pycache__ files | Already-tracked artifacts only | Confirm no runtime dependency first |
| Execute git rm --cached for *.log files | Already-tracked log files only | Confirm no CI step reads these log files |
| Execute git rm --cached for test screenshots | Already-tracked screenshot files in tests/ | Confirm no CI step references screenshot paths |

### Category G — Root-Level Cleanup

| Action | Scope | Condition |
|--------|-------|-----------|
| Move completed session prompt .md files from root to docs/archive/ or docs/09_prompts/ | Root-level U0–U10 prompt files | Canonical copies in Prompts/Main/ must exist |
| Add root untracked prompt .md files to .gitignore | Root-level duplicates of Prompts/Main/ files | Files are untracked and have canonical copies elsewhere |
| Move seal.ps1 to a scripts/ folder | Root-level utility scripts | Verify no Makefile or CI step references the root path |
| Rename Prompts/ to prompts/ (lowercase) | Prompts/ directory | Verify no CI step, Makefile, or code imports from Prompts/ by path |

### Category H — Cross-Reference Fixes

| Action | Scope |
|--------|-------|
| Update all doc-to-doc links after a file is moved | Any .md file containing links to moved file |
| Update AI_OPERATING_CONTEXT.md ACTIVE_AUTHORITY_DOCS table with new paths | docs/07_governance/AI_OPERATING_CONTEXT.md |
| Update DOC_CATALOGUE.md with new file paths and locations | docs/reports/u-series/DOC_CATALOGUE.md |
| Update DOCUMENT_INVENTORY.md with new entries | docs/08_reports/DOCUMENT_INVENTORY.md |
| Fix stale references from old location to new location in any .md file | Repository-wide .md files |

### Category I — Inventory and Governance Metadata Updates

| Action | Scope |
|--------|-------|
| Update DOC_CATALOGUE.md counts and paths after any file move | docs/reports/u-series/DOC_CATALOGUE.md |
| Update DOCUMENT_INVENTORY.md with new file entries | docs/08_reports/DOCUMENT_INVENTORY.md |
| Update governance metadata fields (Status, Last Reviewed, Owner) | Any document in docs/ |
| Update classification entries in DOCUMENT_CLASSIFICATION_MATRIX.md | docs/08_reports/ only |
| Add new entries to AUTHORITY_MAPPING_MATRIX.md | docs/08_reports/AUTHORITY_MAPPING_MATRIX.md |
| Promote document from Draft to Active after verification | Any document in docs/07_governance/ or docs/00_authority/ (metadata only) |

### Category J — Moving Scripts Between Scripts Folders

| Action | Scope | Condition |
|--------|-------|-----------|
| Move utility scripts between backend/scripts/ subdirectories | backend/scripts/ only | Script is a standalone utility, not imported by any module |
| Move deployment documentation from one docs/ subfolder to another | docs/05_deployment/ and docs/reference/ | No CI/CD step references the file path |

### Category K — Moving Backend .md Files Within backend/docs/

| Action | Scope |
|--------|-------|
| Move .md files between subdirectories of backend/docs/ | backend/docs/ tree only |
| Add or update README files within backend/docs/ subdirectories | backend/docs/ tree only |
| Organize backend/docs/_b9/, _qc/, adapters/, adr/, architecture/, domain/, infrastructure/ | backend/docs/ tree only |

---

## Execution Rules

**Rule E-1 — No bundling with feature work.** SAFE_REPOSITORY_HYGIENE tasks must be executed in a dedicated session or a clearly demarcated segment of a session. They must not be bundled with feature development, backend changes, or frontend page builds. Mixing hygiene actions with functional changes makes audit trails unreadable.

**Rule E-2 — Identify before touching.** Before moving any file, read the file and identify all cross-references to it in other documents. Do not move a file and then hunt for references — identify all references first, then move.

**Rule E-3 — Update cross-references immediately.** After moving any file, update all cross-references in the same operation before moving the next file. Never leave a broken cross-reference in an intermediate state.

**Rule E-4 — Use Read + Write + Remove-Item, not Move-Item.** File moves must be executed using Read (to read the original), Write (to write to the new location), and Remove-Item (to delete the original). This ensures an audit trail of what was written to the new location.

**Rule E-5 — No commit.** SAFE_REPOSITORY_HYGIENE execution does not include committing changes. Stage changes and produce the execution report, then leave the commit to the human owner.

**Rule E-6 — Stop on unexpected dependency.** If a file move reveals an unexpected dependency (e.g., a source code file imports from the file being moved, or a CI step references the path), stop the move immediately, revert if partially executed, and escalate to REQUIRES_APPROVAL.

**Rule E-7 — Do not delete.** SAFE_REPOSITORY_HYGIENE never permanently deletes files from the repository. Files may be moved to docs/archive/ or have content merged into another file. Files are removed from git tracking only when they are generated artifacts (logs, __pycache__, screenshots) that should never have been tracked.

**Rule E-8 — Scope to docs/ and non-runtime paths.** When in doubt about whether a file participates in runtime, assume it does and escalate to REQUIRES_APPROVAL.

---

## Escalation Rule

**If uncertain, default to REQUIRES_APPROVAL.**

The SAFE_REPOSITORY_HYGIENE tier is defined by a clear boundary: no change to anything that could affect how the system runs, deploys, or authenticates. If an action is on the boundary of that definition, it is not in SAFE_REPOSITORY_HYGIENE. Classify it as REQUIRES_APPROVAL, present the proposed action to the human owner, and wait for explicit sign-off.

---

## Audit Trail Requirement

Every SAFE_REPOSITORY_HYGIENE execution run must produce a brief HYGIENE_EXECUTION_REPORT file in docs/08_reports/ containing at minimum:

| Section | Content |
|---------|---------|
| Execution date | ISO date |
| Actions taken | Table: file moved from / to, or file modified, with reason |
| Cross-references updated | List of files updated with new paths |
| .gitignore additions | Entries added |
| git rm --cached actions | Files removed from tracking |
| Files not touched | Any items from the plan that were deferred |
| Escalations | Any items that were escalated to REQUIRES_APPROVAL mid-run |
| Verification | Confirmation that no source code, CI/CD, or runtime files were modified |

The report is the evidence that the execution stayed within SAFE_REPOSITORY_HYGIENE bounds.

---

*End SAFE_REPOSITORY_HYGIENE_POLICY.md*
