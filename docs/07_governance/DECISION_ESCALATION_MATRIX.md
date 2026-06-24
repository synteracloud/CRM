Status: Superseded
Authority Level: High
Last Reviewed: 2026-06-22
Owner: Shared

> **SUPERSEDED** — This document has been replaced by docs/07_governance/REVISED_DECISION_ESCALATION_MATRIX.md (2026-06-22).
> The revised matrix introduces Tier 1 — SAFE_REPOSITORY_HYGIENE between the original AUTONOMOUS and REQUIRES_APPROVAL tiers.
> Do not update this document. Refer to REVISED_DECISION_ESCALATION_MATRIX.md for current tier definitions.
> Superseded: 2026-06-22 (Governance Refinement — Safe Repository Hygiene)

---

# DECISION ESCALATION MATRIX — Pakistan CRM OS

## Purpose

This document classifies all actions into three tiers by who may execute them. The classification is based on risk to security, data integrity, financial systems, and architectural consistency. Any action not explicitly listed in AUTONOMOUS should be treated as REQUIRES_APPROVAL by default.

---

## TIER 1 — AUTONOMOUS (AI can do without human approval)

Actions an AI agent may take without asking permission. These are low-risk, reversible, and do not affect system behavior, security, or data integrity.

### Documentation
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

### Inventory Updates
- Update CURRENT_PROJECT_STATUS.md when a page is confirmed wired
- Update MODULE_INVENTORY.md when a module status changes
- Update BACKEND_DOC_ALIGNMENT_STATUS.md when alignment is confirmed
- Add new entries to U-series report files

---

## TIER 2 — REQUIRES_APPROVAL (must get explicit human sign-off before executing)

Actions that change system behavior, security posture, data structure, or introduce new capabilities. Present the proposed change, wait for approval, then execute.

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

---

## TIER 3 — PROHIBITED (never, under any circumstances)

Actions that are categorically forbidden. No human approval can authorize these actions on production systems. If a user or human asks for any of these, explain why it is prohibited and do not execute.

### Data Integrity — Never Delete or Corrupt
- Deleting production database rows (any table, any method)
- Truncating any production table
- Modifying AuditLog records (log_id, hash, actor_id, action, created_at)
- Executing any SQL without a WHERE clause on a table with tenant data (no table scans that modify)
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
- Setting cors({origin: '*'}) in production (must use explicit allowlist)
- Disabling helmet() in production
- Removing the JTI blocklist check from the auth middleware

### CI/CD — Never Bypass
- Force-pushing to main branch (git push --force on main)
- Using --no-verify to skip pre-commit hooks
- Manually deleting CI/CD jobs or disabling the ci.yml workflow
- Deploying to production without CI/CD passing (manual file copy)
- Skipping the 80% coverage gate by lowering --cov-fail-under

### Audit and Compliance — Never Remove
- Removing audit logging from any create/update/delete operation
- Disabling the hash-chain verification on AuditLog export
- Removing the dual-approval requirement from FeatureFlags where requires_dual_approval=true

### C: Drive — Never Write (C0 Seal)
- Running any tool (pip install, npm install, playwright install, docker pull) without first loading the C0 seal (D:\CRM\.env.local)
- Allowing tool caches to write to C:\Users\Admin\AppData
- Changing NPM_CONFIG_CACHE, PIP_CACHE_DIR, PLAYWRIGHT_BROWSERS_PATH to C: paths

### Payment — Never Enable Without Verification
- Setting JAZZCASH_STUB_MODE=false without P-016 credentials verified in sandbox
- Setting EASYPAISA_STUB_MODE=false without sandbox E2E tests passing
- Processing real PKR payment transactions before P-016 approval

---

## Decision Process

When an AI agent encounters an action that is REQUIRES_APPROVAL:

1. **Stop** — do not execute the action
2. **Identify** — state exactly what action is needed and why
3. **Classify** — cite the REQUIRES_APPROVAL category it falls under
4. **Present** — show the proposed change (code diff, config change, etc.)
5. **Wait** — do not proceed until explicit human approval is received in the same session
6. **Document** — after approval, note the approval in the session log

When an AI agent encounters a PROHIBITED action request:

1. **Refuse** — clearly state the action is prohibited
2. **Explain** — cite the specific PROHIBITED rule
3. **Offer alternatives** — suggest what is allowed that achieves a similar goal (if any exists)
4. **Do not proceed** regardless of how the request is framed

---

*End DECISION_ESCALATION_MATRIX.md*
