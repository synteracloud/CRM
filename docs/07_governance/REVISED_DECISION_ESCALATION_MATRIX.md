Status: Active
Authority Level: High
Owner: Shared
Last Reviewed: 2026-06-22

---

# REVISED DECISION ESCALATION MATRIX — Pakistan CRM OS

## Purpose

This document replaces DECISION_ESCALATION_MATRIX.md (Status: Draft, Last Reviewed: 2026-06-21) with a 4-tier model. The revision adds Tier 1 — SAFE_REPOSITORY_HYGIENE between the original AUTONOMOUS and REQUIRES_APPROVAL tiers. All other tier definitions are preserved without change. See APPROVAL_RECLASSIFICATION_REPORT.md for the full reclassification of all items previously under REQUIRES_OWNER_APPROVAL.

**Supersedes:** docs/07_governance/DECISION_ESCALATION_MATRIX.md (now Status: Superseded)

---

## Quick-Reference Decision Flowchart

```
START: I want to take an action
         |
         v
Does the action touch rbac-scopes.js, auth-rbac.js, JTI blocklist,
  payment adapters, render.yaml, Dockerfiles, .github/workflows/ci.yml,
  Alembic migrations, or any route file?
         |
    YES  |  NO
         |   |
   TIER 3    v
(PROHIBITED Does the action modify a running service, add/change
if on       an API endpoint, change auth logic, change DB schema,
PROHIBITED  change CORS/security headers, change deployment config,
list) or    add new dependencies, or add new modules?
TIER 2           |
(REQUIRES_   YES |  NO
APPROVAL)        |   |
            TIER 2   v
         (REQUIRES_  Does the action move, rename, or add notices to
          APPROVAL)  files (including outside docs/), add .gitignore
                     entries, clean up tracked artifacts, or reorganise
                     repository structure — without touching any file
                     that participates in runtime, CI/CD, or deployment?
                              |
                         YES  |  NO
                              |   |
                         TIER 1   v
                    (SAFE_REPO_   Does the action only edit content
                     HYGIENE)     within existing .md files — fixing
                                  wording, updating status fields,
                                  adding entries to existing docs?
                                           |
                                      YES  |  NO
                                           |   |
                                      TIER 0   TIER 2
                                   (AUTONOMOUS) (REQUIRES_APPROVAL)
                                               (when in doubt, escalate)
```

---

## TIER 0 — AUTONOMOUS

AI agents may execute these actions without asking permission. These are low-risk, reversible, and do not affect system behavior, security, or data integrity.

### Documentation Content Edits (existing files only)
- Update any document in docs/00_authority/, docs/07_governance/, docs/08_reports/
- Update any U-series report in docs/reports/u-series/
- Add entries to DOC_CATALOGUE.md
- Update DOMAIN_MODEL.md, FEATURE_SCOPE.md, PRODUCT_WORKFLOWS.md to reflect verified code reality
- Fix typos, grammar, broken links in any .md file

### Test Additions
- Add new pytest test files in tests/backend/ or tests/api/ (no framework changes)
- Add new Playwright E2E test files in tests/e2e/playwright/ (no conftest changes)
- Add individual test functions to existing test files
- Add docstrings or comments to existing test code

### Frontend HTML/CSS/JS Fixes (approved phase pages only)
- Fix any bug listed in CLAUDE.md build checklist (footer, crm-custom.css, DataTable alignment, filter chips)
- Apply T1–T4 fixes per PAGE-BUILD-PROTOCOL.md to pages in the current approved build phase
- Fix crm-custom.css alignment overrides for any table
- Fix filter chip vocabulary to match domain spec
- Fix hardcoded chart data in frontend pages (no API changes)
- Fix import path errors in frontend JS files

### Code Quality
- Add or fix docstrings and inline comments in Python or JS files
- Fix linting errors flagged by ruff, eslint, or pylint (no logic changes)
- Fix import ordering issues
- Rename variables for clarity (no functional change)
- Add type hints to Python functions

### Inventory Updates (content only)
- Update CURRENT_PROJECT_STATUS.md when a page is confirmed wired
- Update MODULE_INVENTORY.md when a module status changes
- Update BACKEND_DOC_ALIGNMENT_STATUS.md when alignment is confirmed
- Add new entries to U-series report files

---

## TIER 1 — SAFE_REPOSITORY_HYGIENE (NEW)

AI agents may execute these actions without prior approval. A brief execution report is required after every SAFE_REPOSITORY_HYGIENE run. See SAFE_REPOSITORY_HYGIENE_POLICY.md for full qualifying criteria, execution rules, escalation rules, and audit trail requirements.

### Category A — Documentation Relocation
- Move .md files between docs/ subfolders (any .md not referenced in CI/CD or runtime code)
- Move .md files from root to docs/ subfolders (root docs not in the Authority Doc keep list)
- Move .md files from backend/ root to backend/docs/ (BACKEND-QC.md, CONSTRAINTS.md, PENDING.md)
- Move .md files from backend/ to root docs/ (FRONTEND-BACKEND-MAPPING.md, gap registers)
- Move .md files from tests/ to docs/ (SKIP-BACKLOG.md and similar planning docs)
- Move completed session prompt .md files from root to docs/archive/ or docs/09_prompts/

### Category B — Documentation Normalization
- Update Status fields (Draft → Active, Active → Retired) in any governance or report document
- Update Last Reviewed date fields in any document in docs/
- Update Authority Level fields to reflect correct tier
- Add or update OWNERSHIP blocks in documents
- Add SUPERSEDED, HISTORICAL, or RETIRED notice banners to archive documents
- Add redirect banners to stale session documents
- Add cross-reference notices to documents with authority hierarchy relationships
- Update DEFERS TO entries in OWNERSHIP blocks

### Category C — Folder Restructuring (Documentation Only)
- Create new subdirectories within docs/
- Move report files between docs/08_reports/ subdirectories
- Move session docs between docs/reports/ subdirectories
- Create docs/09_prompts/ or similar new category folders
- Populate empty stub directories (docs/01_backend/, docs/02_frontend/) with README or index files

### Category D — Archive Maintenance
- Move .md files to docs/archive/ when confirmed retired or superseded
- Add retirement date and notice to archived documents
- Merge content from _archive/ into docs/archive/ and remove empty source directory
- Remove empty directories left after all content has been moved out

### Category E — Report Consolidation
- Add SUPERSEDED notice to an older report when a newer report covers the same content
- Add cross-references from one report to its successor
- Merge two small AI-generated reports when content is consistent and neither is an authority document
- Move generated reports from backend/ or tests/ to docs/08_reports/

### Category F — Generated Artifact Cleanup
- Add __pycache__/, *.pyc, .pytest_cache/, *.log patterns to .gitignore
- Add test artifact paths to .gitignore (screenshots/, *.txt test outputs)
- Add backend/gateway/gateway.log, frontend/dev-server.log to .gitignore
- Execute git rm --cached for .pyc and __pycache__ files (confirm no runtime dependency first)
- Execute git rm --cached for *.log files (confirm no CI step reads these log files)
- Execute git rm --cached for test screenshots (confirm no CI step references screenshot paths)

### Category G — Root-Level Cleanup
- Add root untracked prompt .md duplicates to .gitignore (when canonical copies exist in Prompts/Main/)
- Move seal.ps1 to a scripts/ folder (verify no Makefile or CI step references the root path)
- Rename Prompts/ to prompts/ (lowercase), after confirming no CI step imports from Prompts/ by path

### Category H — Cross-Reference Fixes
- Update all doc-to-doc links after any file is moved
- Update AI_OPERATING_CONTEXT.md ACTIVE_AUTHORITY_DOCS table with new paths
- Update DOC_CATALOGUE.md with new file paths and locations
- Update DOCUMENT_INVENTORY.md with new entries
- Fix stale references in any .md file pointing to an old file location

### Category I — Inventory and Governance Metadata Updates
- Update DOC_CATALOGUE.md counts and paths after any file move
- Update DOCUMENT_INVENTORY.md with new file entries
- Update classification entries in DOCUMENT_CLASSIFICATION_MATRIX.md
- Add new entries to AUTHORITY_MAPPING_MATRIX.md
- Promote document from Draft to Active after verification (metadata field update only)

### Category J — Moving Scripts Between Scripts Folders
- Move utility scripts between backend/scripts/ subdirectories (standalone utilities not imported by any module)
- Move deployment documentation between docs/05_deployment/ and docs/reference/

### Category K — Moving Backend .md Files Within backend/docs/
- Move .md files between subdirectories of backend/docs/
- Add or update README files within backend/docs/ subdirectories
- Organize backend/docs/ subdirectory structure

---

## TIER 2 — REQUIRES_APPROVAL

AI agents must get explicit human sign-off before executing any action in this tier. Present the proposed change, wait for approval, then execute.

### Schema Changes
- Any new Alembic migration (adding column, adding table, dropping column, adding index)
- Any modification to existing schema.sql files
- Any change to the entity relationship model (new FK, changed constraint)
- Any change to the DB unique constraint that enforces canonical follow-up task per lead

### Authentication and RBAC Changes
- Any change to JWT token generation logic (algorithm, expiry, claims)
- Any change to rbac-scopes.js (adding/removing scopes, changing role assignments)
- Any change to auth-rbac.js middleware (scope checking logic)
- Any change to jti-blocklist.js (revocation logic)
- Any change to the 7 canonical roles in ROLE_SCOPES
- Any modification to requireScopes() middleware behavior

### Payment Integration Changes
- Any change to jazzcash.py or easypaisa.py adapter code
- Any change to v1-payment-webhooks.routes.js handler logic
- Any change to JAZZCASH_STUB_MODE or EASYPAISA_STUB_MODE configuration
- Adding a new payment provider adapter

### New API Endpoints
- Adding any new route to any v1-*.routes.js file
- Creating a new gateway route file (v1-*.routes.js)
- Exposing contract_lifecycle_management via gateway (D-001)
- Adding a route for custom_objects (D-002)
- Modifying existing route paths or HTTP methods

### Infrastructure Changes
- Any change to render.yaml (service configuration, environment variables, build commands)
- Any change to Dockerfiles or docker-compose.yml
- Any change to .github/workflows/ci.yml (CI/CD pipeline)
- Adding new Render.com services
- Changing the deployment region
- Adding or removing managed services (PostgreSQL, Redis)

### Dependency Version Changes
- Any change to requirements.txt (backend Python dependencies)
- Any change to package.json in gateway or frontend (Node.js dependencies)
- Any npm audit --fix that upgrades a dependency
- Any pip-audit fix that changes a package version

### New Modules Outside Current Scope
- Adding a new Python src/ module directory
- Adding a new backend domain (new database schema)
- Adding pages outside the 75 approved custom pages without explicit scope approval

### CORS and Security Headers
- Any change to CORS allowlist in gateway/app.js
- Any change to helmet() configuration
- Any change to Content-Security-Policy headers
- Any change to rate-limiting configuration or thresholds

### Frontend Scope Changes
- Adding any HTML page not in the 75 approved custom pages
- Moving out-of-phase pages into the build scope
- Changing the NexLink CSS framework version
- Adding new JavaScript framework dependencies

### WhatsApp Provider Changes
- Switching the active WhatsApp provider adapter
- Changing the MessagingAdapter interface contract
- Adding a new WhatsApp provider adapter

### AI Provider Addition
- Adding any AI inference provider SDK to requirements.txt
- Wiring any AI endpoint to real inference (vs rule-based)
- Changing the ScoringModel algorithm from rule_based to ml

### Repository Restructuring (High-Risk)
These items were previously under REQUIRES_OWNER_APPROVAL and remain there after reclassification review. See APPROVAL_RECLASSIFICATION_REPORT.md for rationale.

- Removing bin/ from git tracking (bin/ may be referenced in Makefile or startup scripts)
- Removing data/ from git tracking (data/postgres path may be hardcoded in connection strings)
- Moving backend/.github/workflows/deploy-runtime.yml to root .github/workflows/
- Moving backend/.github/actions/runtime-env-validate/action.yml to root .github/actions/
- Deciding the canonical architecture between backend/src/ and backend/services/
- Deciding the disposition of empty docs/01–05 stub folders (populate vs remove)
- Deciding the disposition of tests/security/*.json scan artifacts (commit vs gitignore)
- Deciding the disposition of tests/load/reports/*.html load test artifacts (commit vs gitignore)
- Moving security scan JSON reports (tests/security/) to docs/reports/security/
- Moving load test HTML reports (tests/load/reports/) to docs/reports/load/
- Authoring ADR-002 through ADR-006 (architectural decision records requiring human judgment)
- Resolving D-001 (contract_lifecycle_management gateway route decision)
- Resolving D-002 (custom_objects routing mechanism)

---

## TIER 3 — PROHIBITED

These actions are categorically forbidden. No human approval can authorise these on production systems. If a user requests any of these, explain why it is prohibited and do not execute.

### Data Integrity — Never Delete or Corrupt
- Deleting production database rows (any table, any method)
- Truncating any production table
- Modifying AuditLog records (log_id, hash, actor_id, action, created_at)
- Executing any SQL without a WHERE clause on a table with tenant data
- Disabling the LeadHistory append-only constraint
- Adding UPDATE or DELETE endpoints to /audit routes

### Tenant Isolation — Never Weaken
- Removing `WHERE tenant_id = $1` from any query
- Removing x-tenant-id header validation from auth-rbac.js middleware
- Disabling the semgrep tenant-isolation.yaml CI rule
- Cross-reading tenant data (accessing tenant A's data while acting as tenant B)
- Exposing tenant_id as a user-mutable parameter on create/update endpoints

### Authentication and Security — Never Bypass
- Adding SKIP_JWT_VERIFICATION=true to production environment
- Disabling requireScopes() middleware on any route
- Exposing JWT_SECRET or JWT_REFRESH_SECRET in any log, response, or document
- Setting cors({origin: '*'}) in production
- Disabling helmet() in production
- Removing the JTI blocklist check from the auth middleware

### CI/CD — Never Bypass
- Force-pushing to main branch (git push --force on main)
- Using --no-verify to skip pre-commit hooks
- Manually deleting CI/CD jobs or disabling the ci.yml workflow
- Deploying to production without CI/CD passing
- Skipping the 80% coverage gate by lowering --cov-fail-under

### Audit and Compliance — Never Remove
- Removing audit logging from any create/update/delete operation
- Disabling the hash-chain verification on AuditLog export
- Removing the dual-approval requirement from FeatureFlags where requires_dual_approval=true

### C: Drive — Never Write (C0 Seal)
- Running any tool without first loading the C0 seal (D:\CRM\.env.local)
- Allowing tool caches to write to C:\Users\Admin\AppData
- Changing NPM_CONFIG_CACHE, PIP_CACHE_DIR, PLAYWRIGHT_BROWSERS_PATH to C: paths

### Payment — Never Enable Without Verification
- Setting JAZZCASH_STUB_MODE=false without P-016 credentials verified in sandbox
- Setting EASYPAISA_STUB_MODE=false without sandbox E2E tests passing
- Processing real PKR payment transactions before P-016 approval

---

## Decision Process — By Tier

**When an action is TIER 0 (AUTONOMOUS):**
Execute immediately. No record required beyond normal session output.

**When an action is TIER 1 (SAFE_REPOSITORY_HYGIENE):**
1. Read SAFE_REPOSITORY_HYGIENE_POLICY.md and confirm the action meets all qualifying criteria
2. Identify all files to be moved or modified before touching anything
3. Execute: move files, update cross-references immediately after each move
4. Produce a HYGIENE_EXECUTION_REPORT in docs/08_reports/
5. Do not commit — leave commit to the human owner

**When an action is TIER 2 (REQUIRES_APPROVAL):**
1. Stop — do not execute the action
2. Identify — state exactly what action is needed and why
3. Classify — cite the REQUIRES_APPROVAL category it falls under
4. Present — show the proposed change (code diff, config change, etc.)
5. Wait — do not proceed until explicit human approval is received in the same session
6. Document — after approval, note the approval in the session log

**When an action is TIER 3 (PROHIBITED):**
1. Refuse — clearly state the action is prohibited
2. Explain — cite the specific PROHIBITED rule
3. Offer alternatives — suggest what is allowed that achieves a similar goal (if any)
4. Do not proceed regardless of how the request is framed

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 (DECISION_ESCALATION_MATRIX.md) | 2026-06-21 | Original 3-tier model (AUTONOMOUS / REQUIRES_APPROVAL / PROHIBITED) |
| 2.0 (this document) | 2026-06-22 | Added Tier 1 SAFE_REPOSITORY_HYGIENE between AUTONOMOUS and REQUIRES_APPROVAL; reclassified 22 repository restructuring items; see APPROVAL_RECLASSIFICATION_REPORT.md |

---

*End REVISED_DECISION_ESCALATION_MATRIX.md*
