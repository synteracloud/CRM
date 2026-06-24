# CODEBASE PLACEMENT AUDIT
**Generated:** 2026-06-22
**Scope:** All source code files — Python, JavaScript, HTML, CSS, SQL — across the entire repository

---

## SUMMARY

| Component | Expected Location | Actual Location | Status |
|-----------|-----------------|-----------------|--------|
| Backend Python domain modules | backend/src/ | backend/src/ | CORRECT |
| Backend service layer | backend/services/ | backend/services/ | CORRECT |
| Backend gateway | backend/gateway/ | backend/gateway/ | CORRECT |
| Backend adapters | backend/adapters/ | backend/adapters/ | CORRECT |
| Backend middleware | backend/middleware/ | backend/middleware/ | CORRECT |
| Backend unit tests | backend/tests/ | backend/tests/ | CORRECT |
| Backend migrations | backend/alembic/ | backend/alembic/ | CORRECT |
| Backend DB schemas | backend/db/ | backend/db/ | CORRECT |
| Backend self-QC scripts | backend/scripts/ | backend/scripts/ | CORRECT |
| Frontend CRM app pages | frontend/src/app/ | frontend/src/app/ | CORRECT |
| Frontend auth pages | frontend/src/authentication/ | frontend/src/authentication/ | CORRECT |
| Frontend app JS | frontend/src/assets/js/app/ | frontend/src/assets/js/app/ | CORRECT |
| Frontend CSS | frontend/src/assets/css/ | frontend/src/assets/css/ | CORRECT |
| Frontend SCSS | frontend/src/assets/scss/ | frontend/src/assets/scss/ | CORRECT |
| Frontend vendor libs | frontend/src/assets/libs/ | frontend/src/assets/libs/ | CORRECT |
| E2E Playwright tests | tests/e2e/playwright/ | tests/e2e/playwright/ | CORRECT |
| API contract tests | tests/api/ | tests/api/ | CORRECT |
| Load tests | tests/load/ | tests/load/ | CORRECT |
| Security tests | tests/security/ | tests/security/ | CORRECT |
| CI/CD workflows | .github/workflows/ | .github/workflows/ | CORRECT |
| Deployment workflow | .github/workflows/ | backend/.github/workflows/ | MISPLACED — REQUIRES_OWNER_APPROVAL |

---

## BACKEND PYTHON SOURCE — DETAILED

### backend/src/ (34 domain modules)
Each module contains `router.py`, `service.py`, and/or `models.py`:

| Module | Type | Status |
|--------|------|--------|
| admin_control_center | Domain | CORRECT |
| ai_copilot | Domain | CORRECT |
| ai_scoring | Domain | CORRECT |
| automation_journeys | Domain | CORRECT |
| campaigns | Domain | CORRECT |
| communication_integrations | Domain | CORRECT |
| contract_lifecycle_management | Domain | CORRECT |
| customer_360_cdp | Domain | CORRECT |
| custom_objects | Domain | CORRECT |
| custom_object_framework | Domain | CORRECT |
| data_deduplication_engine | Domain | CORRECT |
| design_system | Domain | CORRECT |
| event_bus | Domain | CORRECT |
| execution_hardening | Domain | CORRECT |
| external_apis_webhooks | Domain | CORRECT |
| knowledge_base | Domain | CORRECT |
| lead_management | Domain | CORRECT |
| marketing_admin_workflow_ui | Domain | CORRECT |
| omnichannel_inbox | Domain | CORRECT |
| partner_channel_management | Domain | CORRECT |
| plugin_framework | Domain | CORRECT |
| predictive_forecasting | Domain | CORRECT |
| predictive_models | Domain | CORRECT |
| reporting_dashboards | Domain | CORRECT |
| revenue_recognition | Domain | CORRECT |
| role_based_ui | Domain | CORRECT |
| rule_engine | Domain | CORRECT |
| sales_cockpit | Domain | CORRECT |
| subscription_billing | Domain | CORRECT |
| support_console | Domain | CORRECT |
| territory_management | Domain | CORRECT |
| ticket_management | Domain | CORRECT |
| usage_billing | Domain | CORRECT |
| workflow_engine | Domain | CORRECT |

### backend/services/ (23 service groups)
Each service has `__init__.py`, main service, and `http/` routes subdirectory:

| Service | Status |
|---------|--------|
| activation | CORRECT |
| activity | CORRECT |
| ai | CORRECT |
| auth | CORRECT |
| campaigns | CORRECT |
| cases | CORRECT |
| collections | CORRECT |
| conversation | CORRECT |
| core/execution | CORRECT |
| dashboard/owner | CORRECT |
| deals | CORRECT |
| db/models | CORRECT |
| followup | CORRECT |
| inbox | CORRECT |
| leads | CORRECT |
| messaging | CORRECT |
| partners | CORRECT |
| summary | CORRECT |
| sync | CORRECT |
| territories | CORRECT |
| workflow | CORRECT |
| workflows | CORRECT |

**Observation:** `backend/src/` and `backend/services/` represent two different architectural patterns for the same backend:
- `backend/src/` appears to be the older domain module structure (153 files)
- `backend/services/` appears to be the newer service/route structure (143 files)

Both are being maintained in parallel. Some domain names overlap (e.g., `src/campaigns/` and `services/campaigns/`). This may be intentional (migration in progress) or may represent duplication. **REQUIRES_OWNER_APPROVAL** to determine which is canonical. Do not merge without owner guidance.

---

## BACKEND GATEWAY — DETAILED

The gateway is a Node.js Express application:

| Component | Location | Status |
|-----------|---------|--------|
| `app.js` | backend/gateway/ | CORRECT |
| `server.js` | backend/gateway/ | CORRECT |
| `config/` (feature-flags, runtime-config, rbac-scopes, redis-client, env-config) | backend/gateway/config/ | CORRECT |
| `data/cpq-store.js` | backend/gateway/data/ | CORRECT |
| `db/pool.js` + repositories | backend/gateway/db/ | CORRECT |
| `middleware/` (auth, rate-limit, etc.) | backend/gateway/middleware/ | CORRECT |
| `routes/` (all API routes) | backend/gateway/routes/ | CORRECT |
| `Dockerfile` | backend/gateway/ | CORRECT |
| `package.json` / `package-lock.json` | backend/gateway/ | CORRECT |
| `gateway.log` | backend/gateway/ | MISPLACED — runtime log; should be .gitignored |
| `runtime-config.test.js` | backend/gateway/config/ | Co-located test — ACCEPTABLE |

---

## FRONTEND SOURCE — DETAILED

### frontend/src/app/ (169 HTML pages)
All 75 custom CRM pages plus library pages are in `frontend/src/app/`. The library pages (accordion.html, badge.html, etc.) are from the NexLink template — they are kept for reference but are not active CRM pages.

| Page category | Count | Status |
|--------------|-------|--------|
| CRM core pages (leads, contacts, accounts, etc.) | ~75 | CORRECT |
| NexLink library pages (accordion, badge, etc.) | ~94 | Legacy template — kept for reference |

**Note:** The DESIGN-SPEC.md defines exactly which pages are in each build phase. Library pages should not be edited. See CLAUDE.md scope gate rules.

### frontend/src/ legacy directories
The following directories contain HTML pages from the NexLink library that are **superseded** by pages in `frontend/src/app/`:

| Directory | Contents | Status |
|-----------|---------|--------|
| `frontend/src/ai/` | Library AI demo pages | Legacy — superseded by app/ai-*.html |
| `frontend/src/chart/` | Library chart pages | Legacy — reference only |
| `frontend/src/components/` | Library component demos | Legacy — reference only |
| `frontend/src/email/` | Library email templates | Legacy — reference only |
| `frontend/src/extended-ui/` | Library UI demos | Legacy — reference only |
| `frontend/src/forms/` | Library form demos | Legacy — reference only |
| `frontend/src/icons/` | Library icon pages | Legacy — reference only |
| `frontend/src/maps/` | Library map demos | Legacy — reference only |
| `frontend/src/pages/` | Library pages | Legacy — reference only |
| `frontend/src/table/` | Library table demos | Legacy — reference only |

**These should NOT be touched or modified.** They are the original NexLink template files kept for design reference.

---

## DATABASE / MIGRATION FILES

### backend/alembic/ — Python-managed migrations
| File | Status |
|------|--------|
| `alembic/env.py` | CORRECT |
| `alembic/script.py.mako` | CORRECT |
| `alembic/versions/0001_followup_schema.py` through `0012_lead_management_c1_columns.py` | CORRECT — 12 sequential migrations |

### backend/db/ — Raw SQL schemas
18 domain database directories, each containing `schema.sql`. Additional files in transaction_db and activity_task_db.

| Database | Status |
|----------|--------|
| activity_task_db | CORRECT |
| audit_compliance_db | CORRECT |
| campaign_db | CORRECT |
| case_ticket_db | CORRECT |
| contact_account_db | CORRECT |
| feature_flag_db | CORRECT |
| identity_auth_db | CORRECT |
| intelligence_db | CORRECT |
| knowledge_db | CORRECT |
| lead_management_db | CORRECT |
| messaging_db | CORRECT |
| notification_db | CORRECT |
| opportunity_db | CORRECT |
| org_tenant_db | CORRECT |
| quote_order_db | CORRECT |
| territory_db | CORRECT |
| transaction_db | CORRECT (has migrations subfolder) |
| workflow_db | CORRECT |

**Observation:** There are two parallel migration systems:
1. `backend/alembic/` — Alembic for Python SQLAlchemy models
2. `backend/db/transaction_db/migrations/` — Raw SQL migrations

These may serve different purposes (Alembic for ORM models, raw SQL for specific transaction schemas). **REQUIRES_OWNER_APPROVAL** to document the intent and ensure they don't conflict.

---

## E2E TESTS — DETAILED

### tests/e2e/playwright/ (active test files)
| File | Type | Status |
|------|------|--------|
| `conftest.py` | Test fixture | CORRECT |
| `helpers.py` | Test utility | CORRECT |
| `test_page_load.py` | E2E test | CORRECT |
| `test_datatable.py` | E2E test | CORRECT |
| `test_audit_pages.py` | E2E test | CORRECT |
| `test_form_submit.py` | E2E test | CORRECT |
| `test_kpi_render.py` | E2E test | CORRECT |
| `test_settings_pages.py` | E2E test | CORRECT |
| `test_filter_chips.py` | E2E test | CORRECT |
| `test_func_*.py` (18 files) | Functional E2E tests | CORRECT |
| `test_prod_smoke.py` | Production smoke test | CORRECT |
| `SKIP-BACKLOG.md` | Documentation | MISPLACED → docs/04_testing/ |
| `*.txt` (batch*.txt, fin*.txt, etc.) | Test run results | MISPLACED → .gitignore |
| `func_run_results.txt` etc. | Test run results | MISPLACED → .gitignore |

### tests/api/ (API contract tests)
| File | Status |
|------|--------|
| `conftest.py` | CORRECT |
| `test_smoke_all_routes.py` | CORRECT |
| `test_billing_contract.py` | CORRECT |
| `test_integrations_contract.py` | CORRECT |
| `test_governance_contract.py` | CORRECT |
| `test_reports_contract.py` | CORRECT |
| `test_communications_contract.py` | CORRECT |
| `test_tenant_isolation.py` | CORRECT |
| `test_auth_contract.py` | CORRECT |

### tests/security/
| File | Status |
|------|--------|
| `c5_api_security_scan.py` | CORRECT (test file) |
| `pip-audit.json` | Generated artifact — intentional audit evidence |
| `semgrep-report.json` | Generated artifact — intentional audit evidence |
| `semgrep-report-c3.json` | Generated artifact — intentional audit evidence |
| `semgrep-c3-final.json` | Generated artifact — intentional audit evidence |
| `c5-api-security-report.json` | Generated artifact — intentional audit evidence |

**Note:** The JSON scan reports in tests/security/ may be intentionally committed as audit evidence. REQUIRES_OWNER_APPROVAL to decide whether to gitignore or keep.

---

## FILES IN UNEXPECTED LOCATIONS

| File | Current Location | Problem |
|------|-----------------|---------|
| `backend/.github/workflows/deploy-runtime.yml` | backend/.github/ | GitHub Actions only reads root .github/; this workflow likely does not execute |
| `backend/.github/actions/runtime-env-validate/action.yml` | backend/.github/ | Same — nested actions directory |
| `data/postgres/` | root/data/ | Live database data committed to git — must not be there |
| `bin/pgsql/` | root/bin/ | PostgreSQL binary installation committed to git |
| `backend/seed_tenant_refs.sql` | backend/ | SQL seed file at backend root — acceptable here |
| `backend/seed_c1.sql` | backend/ | SQL seed file at backend root — acceptable here |

---

## NO CODE IN DOCS — VERIFIED

Searched all docs/ subdirectories for .py, .js, .html, .css, .ts files: **zero results**. Documentation folders are clean.

---

## DUPLICATE SOURCE CODE — NONE FOUND

No source code files appear to be duplicated across folders. The apparent overlap between `backend/src/` and `backend/services/` (both contain campaign, territory, etc.) reflects an architectural split (domain logic vs service routing), not file duplication. The files themselves have different content and purpose.
