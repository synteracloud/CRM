# TEST_SUITE_PLAN.md — Pakistan CRM OS
**Generated:** 2026-06-21 — U9 Test Suite Planning
**Scope:** 228 APIs, 29 backend modules, 75 frontend pages, 7 roles, 91 scopes, 5 system workflows [module count corrected from 28 by U10 remediation 2026-06-21]
**Evidence base:** U0–U8 u-series reports, actual test files in backend/tests/ and tests/

---

## 1. Current Test Infrastructure Summary

| Layer | Files | Location | Runner |
|---|---|---|---|
| Backend unit/integration | 79 .py files | backend/tests/ | pytest (Python 3.12, .venv) | [corrected from 54 by U10 remediation 2026-06-21]
| E2E / Playwright | 23 .py files | tests/e2e/playwright/ | pytest + playwright 1.60.0 | [corrected from 25 by U10 remediation 2026-06-21]
| API contract tests | 8 .py files | tests/api/ | pytest + httpx | [corrected from 6 by U10 remediation 2026-06-21]
| Load tests | 1 locustfile.py | tests/load/ | locust 2.44.0 |
| Security scan | 1 c5_api_security_scan.py | tests/security/ | httpx (standalone script) |
| Dependency audit | pip-audit.json + semgrep reports | tests/security/ | pip-audit, semgrep |

**CI gate:** `pytest --cov=. --cov-fail-under=80` (ci.yml: backend-test job)

---

## 2. Test Type Definitions and Plans

---

### 2.1 Unit Tests

**Scope:** Backend service and entity layer — all 34 Python modules in `backend/src/`

**Tools:** pytest 9.0.3, Python 3.12 venv at `D:\SaaS\CRM\backend\.venv`

**Methodology:**
- Tests live in `backend/tests/test_<module_name>.py` (79 files, all 34 src/ modules covered) [corrected from 54 by U10 remediation 2026-06-21]
- Pattern: `unittest.TestCase` or plain `pytest` functions with in-memory data (no DB)
- `LeadService(event_sink=emitted.append)` pattern: inject event sink to capture emitted events, assert lifecycle transitions
- Coverage measured with pytest-cov, reported per-module with `--cov-report=term-missing`
- No external dependencies (DB, Redis, WhatsApp) in unit tests — fully isolated

**Modules confirmed covered by existing test files:**
- lead_management, customer_360_cdp, ticket_management, support_console, omnichannel_inbox
- campaigns, automation_journeys, workflow_engine, knowledge_base, rule_engine
- ai_copilot, ai_scoring, predictive_models, predictive_forecasting
- revenue_recognition, subscription_billing, usage_billing
- partner_channel_management, territory_management
- admin_control_center, role_based_ui, reporting_dashboards
- custom_object_framework, custom_objects, data_deduplication_engine
- event_bus, plugin_framework, external_apis_webhooks, execution_hardening
- communication_integrations, design_system, sales_cockpit, marketing_admin_workflow_ui
- contract_lifecycle_management (backend/tests/test_contract_lifecycle_management.py confirmed)

**Pakistan-specific unit tests (confirmed):**
- test_pakistan_payment_adapters.py — JazzCash and Easypaisa stub adapter tests
- test_whatsapp_lead_capture.py — WhatsApp inbound lead creation tests
- test_whatsapp_public.py — Meta webhook verification challenge tests

**Success criteria:** All 54 test files pass; coverage >= 80% (CI gate)
**Failure criteria:** Any test failure, or coverage drops below 80%
**Evidence requirements:** pytest terminal output + coverage.xml artifact (uploaded by ci.yml)

---

### 2.2 Integration Tests

**Scope:** API endpoint tests against the gateway with a running PostgreSQL instance; tests call real gateway HTTP handlers and verify response envelopes.

**Tools:** pytest + httpx 0.28.1; gateway at localhost:3000; PostgreSQL (CI: `sudo systemctl start postgresql`)

**Methodology:**
- `tests/api/` contract tests: 6 files (test_smoke_all_routes.py, test_billing_contract.py, test_integrations_contract.py, test_governance_contract.py, test_reports_contract.py, test_communications_contract.py)
- `test_smoke_all_routes.py` covers 44 GET routes, verifying HTTP 200 + `{data, meta: {request_id}}` envelope
- Contract tests verify domain-specific response schemas (billing plans, integration configs, governance labels)
- Auth acquired via `/dev-token` (NODE_ENV=development) or `/api/v1/auth/register` (production)
- `x-tenant-id` header required on all protected routes; confirmed in conftest.py
- E2E Playwright `conftest.py` `seed` fixture also exercises POST endpoints for leads, contacts, opportunities, cases, tasks, partners, territories, workflows, campaigns, articles, accounts, quotes

**Known gaps vs 228 API surface:**
- smoke test covers 44 of 228 routes (19%)
- Missing: all POST/PATCH/DELETE endpoints in smoke test
- Missing: WhatsApp webhook routes (POST /whatsapp-webhooks/*)
- Missing: Payment webhook routes (POST /payment-webhooks/*)
- Missing: Sub-resource endpoints (/opportunities/:id/line-items, /followups/:id/complete, /followups/:id/snooze)
- Missing: State-machine transition endpoints (cases assign/resolve/close/reopen/escalate)
- Missing: Workflow publish/simulate/retry/cancel

**Recommended additions (priority order):**
1. Add POST/PATCH tests for leads, contacts, opportunities, cases (highest traffic)
2. Add state transition tests: case state machine (14 routes), workflow lifecycle (11 routes)
3. Add webhook signature validation tests

**Success criteria:** All smoke routes return 200 with correct envelope; all contract assertions pass
**Failure criteria:** Any HTTP 5xx; missing envelope keys; assertion failure
**Evidence requirements:** pytest terminal output; ci.yml uploads to GitHub artifacts

---

### 2.3 End-to-End (E2E) Tests

**Scope:** All 75 frontend custom pages; key functional workflows via browser

**Tools:** Playwright 1.60.0, Chromium browser at `D:\dev-cache\playwright`, pytest-based runner

**Methodology:**
- `tests/e2e/playwright/conftest.py` provides:
  - `browser` fixture (session-scoped Chromium launch)
  - `page` fixture (per-test page with screenshot-on-fail)
  - `authed_page` fixture (localStorage-injected JWT + tenant_id)
  - `auth_credentials` / `seed` fixtures (session-scoped, creates 14 entity records via API)
- `BASE_URL` defaults to `http://localhost:3001` (http-server on frontend); override via `BASE_URL` env var for production (`onrender.com`)
- `GATEWAY_URL` defaults to `http://localhost:3000`; production: `https://crm-gateway-l3rm.onrender.com`

**Confirmed test files and their coverage:**

| File | What it tests |
|---|---|
| test_page_load.py | All 75 pages: HTTP 200, sidebar present, header present, zero JS errors |
| test_datatable.py | DataTable pages: rows rendered, columns visible (leads, contacts, accounts, followups, tasks, cases, invoices, collections, partners, territories, roles, audit-log) |
| test_kpi_render.py | KPI dashboard pages: tiles have numeric content (dashboard, leads-dashboard, sales-dashboard, etc.) |
| test_form_submit.py | Form pages: lead-new, contact-new first steps visible and interactive |
| test_filter_chips.py | Filter chip nav-pills-custom: active class toggles on click |
| test_audit_pages.py | Audit/compliance pages: tables render, hash-chain elements visible |
| test_settings_pages.py | Settings pages: two-pane layout, list-group nav, no double-footer |
| test_func_leads.py | Lead workflow: create lead, verify in list, check detail page |
| test_func_contacts.py | Contact workflow: create, list, detail |
| test_func_sales.py | Sales pipeline: opportunities, stage display |
| test_func_cases.py | Case lifecycle: create case, view detail, comment |
| test_func_finance.py | Finance: collections, invoices, subscriptions |
| test_func_quotes_orders.py | CPQ: quote builder, order creation flow |
| test_func_inbox_knowledge.py | Inbox claim/send, knowledge article |
| test_func_marketing.py | Campaign creation, segment display |
| test_func_automation.py | Workflow builder, run detail |
| test_func_partners_territories.py | Partner list/detail, territory assignment |
| test_func_audit_compliance.py | Audit log, RBAC audit, data governance |
| test_func_identity_settings.py | User management, roles, integrations, org settings |
| test_func_ai.py | AI insights, copilot query |
| test_func_accounts.py | Account list, detail |
| test_func_activities.py | Activity feed, task queue |
| test_prod_smoke.py | Production smoke: all 75 pages via onrender.com |

**Screenshot evidence:** 200+ PNG files confirmed in tests/e2e/playwright/screenshots/

**Known gaps:**
- No authenticated multi-role E2E tests (all E2E tests use single dev token / registered user)
- No E2E tests for RTL (Urdu) mode
- No E2E tests for mobile viewport (360px WhatsApp mobile)
- WhatsApp webhook inbound simulation not tested via browser

**Success criteria:** All 75 page_load tests pass (HTTP 200, sidebar, header, zero JS errors); all functional flow tests complete their happy path
**Failure criteria:** HTTP 4xx/5xx on any page; missing sidebar/header element; JS error in critical path
**Evidence requirements:** pytest output + screenshots saved to tests/e2e/playwright/screenshots/

---

### 2.4 Security Tests

**Scope:** Authentication, RBAC, injection, headers, tenant isolation, webhook signatures
**Reference:** See SECURITY_TEST_PLAN.md for full detail
**Tools:** c5_api_security_scan.py (httpx, standalone), semgrep, pip-audit

**Current security test artifacts:**
- tests/security/pip-audit.json — dependency CVE audit (4 CVEs found: pip, python-jose, starlette — see SECURITY_TEST_PLAN.md)
- tests/security/semgrep-report.json — static analysis report
- tests/security/c5-api-security-report.json — runtime security scan (7 categories: headers, auth enforcement, SQLi/XSS, error safety, CORS, rate limiting, info disclosure)

**Success criteria:** c5 scan 0 failures; semgrep 0 critical findings; pip-audit 0 Critical-rated CVEs
**Failure criteria:** Any 5xx from injection attempts; missing auth header blocks; rate-limit headers absent; stack traces in 404 responses
**Evidence requirements:** JSON report files in tests/security/

---

### 2.5 Load Tests

**Scope:** Gateway throughput under concurrent load; 6 scenarios covering highest-traffic endpoints
**Reference:** See LOAD_TEST_PLAN.md for full detail
**Tools:** locust 2.44.0 (confirmed in requirements.txt and tests/load/locustfile.py)

**Existing scenarios:** FollowupQueueUser, LeadCreationUser, CollectionsQueueUser, CasesCRUDUser, InboxUser, OnboardingFlowUser
**Existing reports:** 7 HTML reports in tests/load/reports/ confirming tests have been run

**Success criteria:** p95 per target: GET /followups < 500ms, POST /leads < 800ms, GET /cases < 600ms, GET /inbox/conversations < 700ms, full onboarding flow < 2000ms
**Failure criteria:** Error rate > 1%; p99 > 3s; any 5xx under baseline load
**Evidence requirements:** Locust HTML report at tests/load/reports/

---

### 2.6 Regression Tests (PR Gate)

**What runs on every PR (from ci.yml):**

| Job | Command | Gate |
|---|---|---|
| backend-lint | `ruff check . && black --check .` | Must pass |
| backend-test | `pytest --cov=. --cov-fail-under=80 -q --tb=short --ignore=.venv` | 80% coverage required |
| security-scan | `pip-audit`, `npm audit --audit-level=critical`, `semgrep` | Informational (|| true) |
| arch-guard | `ruff check services/core/ --select TID251` | Must pass — ADR-002 adapter boundary |
| gateway-lint | `npx eslint . --ext .js --max-warnings 0` | Informational (|| true) |
| api-contracts | `pytest tests/api/ -q --tb=short` | Requires gateway running |

**Regression test rule:** backend-test and arch-guard are hard gates; all others are informational in CI. Recommend promoting security-scan to hard gate (remove `|| true`).

---

## 3. Test Priority Matrix

Based on U6 delta findings (under-documented = risk areas) and U7 alignment status:

### P0 — Critical (test immediately, block release on failure)

| Module/Domain | Reason | Current Coverage |
|---|---|---|
| Auth (7 routes) | Token issuance, refresh, revocation — all security depends on this | test_enforcement.py, c5 scan |
| Leads (8 routes) | Highest-traffic; stage transitions write LeadHistory | test_lead_management.py, E2E func tests |
| Cases (14 routes) | Most complex state machine; 14-day reopen window; optimistic concurrency | test_ticket_management.py |
| RBAC / Tenant isolation | Multi-tenant SaaS — tenant A cannot see tenant B | test_tenant_isolation.py, c5 scan |
| WhatsApp webhooks (6 routes) | U6 found 5 underdocumented; primary communication channel | test_whatsapp_lead_capture.py |
| Payment webhooks (3 routes) | Stub mode — but signature validation must still work | test_pakistan_payment_adapters.py |

### P1 — High (cover before Phase 6 live-API wiring)

| Module/Domain | Reason | Current Coverage |
|---|---|---|
| Collections (11 routes) | U6 found +7 underdocumented routes (was 4, actually 11) | test_collections_engine.py |
| Partners (13 routes) | U6 found +8 underdocumented (was 5, actually 13); commission approval is financial | test_partner_channel_management.py |
| Territories (11 routes) | U6 found +6 underdocumented; territory rules drive lead assignment (WF-004) | test_territory_management.py |
| Campaigns (10 routes) | U6 found +5 underdocumented; Urdu approval gate (P-017) untested | test_campaigns.py |
| Workflows (11 routes) | 5 system workflows; simulate/retry/cancel paths need integration test | test_workflow_engine.py |
| Inbox (11 routes) | Agent capacity cap, handoff supervisor rule, 10-conversation limit | test_omnichannel_inbox.py |

### P2 — Medium (cover before GA)

| Module/Domain | Reason | Current Coverage |
|---|---|---|
| Quotes/CPQ (5 routes) | Discount > 10% approval routing; accept → order creation | test_cpq_engine.py |
| AI endpoints (13 routes) | Advisory-only; rule-based; all PARTIALLY-ALIGNED | test_ai_copilot.py, test_ai_scoring.py |
| Billing (6 routes) | U6 found billing has more routes than documented | test_subscription_billing.py |
| Governance/Privacy (9 routes) | GDPR/PDPA SAR flow; retention config | test_admin_control_center.py |
| Contract Lifecycle (12 routes) | HUMAN-DECISION-REQUIRED; backend complete but no gateway route | test_contract_lifecycle_management.py |

### P3 — Low (cover at best effort)

| Module/Domain | Reason | Current Coverage |
|---|---|---|
| Activities (2 routes) | PARTIALLY-ALIGNED, low complexity | test_activity_control_engine.py |
| Tasks (3 routes) | PARTIALLY-ALIGNED | test_employee_activity_monitor.py |
| Forecasts (3 routes) | Read-only; WF-005 triggers refresh | test_predictive_forecasting.py |
| Templates (4 routes) | CRUD only | (campaigns tests cover indirectly) |
| Sync (2 routes) | Simple trigger/status pattern | test_sync_service.py |

---

## 4. Current Coverage Estimate

| Layer | Estimated Coverage | Basis |
|---|---|---|
| Backend Python modules | >= 80% (CI-enforced) | 54 test files, all 34 src/ modules covered; .coverage file exists |
| Gateway API routes | ~19% explicit smoke (44/228) | test_smoke_all_routes.py covers 44 GET routes |
| Gateway routes (via E2E seed) | ~30% additional | conftest.py seed creates records via POST for 14 entity types |
| Frontend pages | 100% page-load | test_page_load.py covers all 75 custom pages |
| Frontend functional | ~70% | 15 func_ test files cover main workflows |
| RBAC enforcement | ~40% | test_enforcement.py + c5 scan; only tenant_owner role tested in E2E |
| Webhook routes | ~30% | meta GET verification; provider inbound handlers not integration-tested |

**Overall:** Backend unit coverage >= 80% (enforced). API route integration coverage is the primary gap — 70% of routes lack explicit integration test assertions beyond smoke (HTTP 200 + envelope).

---

## 5. Coverage Gaps — What Is NOT Tested That Should Be

### Critical gaps

1. **Multi-role RBAC matrix testing** — No test verifies that `agent` role cannot call `DELETE /leads/:id` (requires `leads.delete`, granted only to `tenant_owner` and `tenant_admin`). The 7 roles x 91 scopes matrix has no systematic test coverage.

2. **Case state machine negative paths** — No test verifies 409 on stale `version_no` (optimistic concurrency), 422 on reopen after 14 days, or 422 on resolving an already-resolved case.

3. **Tenant isolation** — test_tenant_isolation.py exists but needs verification that Tenant A's JWT cannot list Tenant B's leads even with a valid token (cross-tenant data leak).

4. **Webhook signature validation** — Meta HMAC challenge for WhatsApp; JazzCash/Easypaisa stub-mode signature. The c5 scan does not test webhook signature rejection.

5. **Workflow system workflow immutability** — No test verifies that `PATCH /workflows/wf-001` returns 403 FORBIDDEN (is_system=true blocks edit).

6. **Agent capacity cap** — `POST /inbox/conversations/:id/claim` when `open_conversation_count >= 10` must return error; no test covers this.

### High gaps

7. **CSV export/import** — GET /leads/export and POST /leads/import (phone dedup) have no integration test.

8. **Paginated list behavior** — No test verifies `limit=200` cap on leads, or that `offset` pagination returns correct second page.

9. **Collections payment proof upload** — POST `/collections/invoices/:id/payments/:pid/proof` returns 501 (P-025 pending); no test asserts this graceful degradation.

10. **WhatsApp Urdu campaign gate (P-017)** — POST /campaigns/:id/activate with `urdu_approved_by` missing must return 422; no test.

11. **Feature flag dual-approval** — PATCH /admin/feature-flags/:id with `requires_dual_approval=true` needs a second approver; no test.

12. **Mobile viewport E2E** — No Playwright test runs at 360px (WhatsApp mobile target from DESIGN-SPEC.md).

---

*End TEST_SUITE_PLAN.md*
