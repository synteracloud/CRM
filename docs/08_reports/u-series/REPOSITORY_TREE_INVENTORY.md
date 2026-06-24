# REPOSITORY_TREE_INVENTORY.md
> Generated: 2026-06-20 — U0 Discovery Pass — evidence only, no doc trust

---

## Root Level — D:\SaaS\CRM\

```
D:\SaaS\CRM\
├── backend/                      Python FastAPI services + Node.js gateway
├── frontend/                     Static HTML/CSS/JS UI
├── bin/                          Bundled PostgreSQL 14 binaries (Windows)
├── data/                         (contents not inventoried — non-code)
├── c-seal/                       (contents not inventoried — unknown purpose)
├── logs/                         Runtime logs
├── tests/                        Root-level Playwright E2E tests + batch results
├── _archive/                     Archived files
├── .npm-cache/                   npm cache
├── .pip-cache/                   pip cache
├── .playwright-browsers/         Playwright browser binaries
├── .claude/                      Claude Code session state
├── .github/
│   └── workflows/
│       └── ci.yml                GitHub Actions CI/CD pipeline
├── .semgrep/                     Semgrep security rules (custom tenant-isolation)
├── .pytest_cache/                pytest cache
├── README.md
├── PRODUCT-SPEC.md
├── CLAUDE.md                     Claude Code instructions (project-specific)
├── DESIGN-SPEC.md                Master screen inventory — 75 custom pages, 13 archetypes
├── FRAMEWORK.md                  Frontend build protocol, CSS/JS stack rules
├── SCREEN-ARTEFACTS.md           QC records — browser-approved page log
├── SESSION-HANDOFF.md            Session context handoff doc
├── PENDING.md                    Pending issues tracker
├── PROGRESS.md                   Build progress log
├── PAGE-BUILD-PROTOCOL.md        Page build checklist
├── CHANGELOG.md                  Version changelog
├── CATALOGUE-MERGE-PLAN.md       Doc catalogue merge plan
├── DOC-READ-LOG.md               Documentation read tracking
├── MAPPING-TRACKER.md            API-to-UI mapping tracker
├── SYSTEM-SNAPSHOT.md            System state snapshot
├── DOC-CATALOGUE.md              Documentation catalogue index
├── COMMERCIALISATION-PLAN.md     Go-to-market planning
├── RENDER-DEPLOY.md              Render.com deployment guide
├── REBUILD-PLAN.md               Rebuild planning doc
├── CONTRIBUTING.md               Contributor guidelines
├── U0 — REPOSITORY REALITY DISCOVERY.md   (this scan trigger)
├── U1 — AUTHORITY RECONSTRUCTION.md       (companion doc)
├── render.yaml                   Render.com IaC — 3 services + PG + Redis
├── Makefile                      Build/dev task runner
├── seal.ps1                      PowerShell utility script
├── .pre-commit-config.yaml       Pre-commit hook config
├── .gitignore
├── .env.local                    Local environment overrides
├── gateway_startup.log           Gateway startup log
├── gateway_err.log               Gateway error log
└── gw.log                        Gateway runtime log
```

---

## backend/

```
backend/
├── src/                          Python module packages (34 domain modules)
│   ├── admin_control_center/     api.py, entities.py, services.py
│   ├── ai_copilot/               api.py, entities.py, services.py
│   ├── ai_scoring/               api.py, entities.py, services.py
│   ├── automation_journeys/      api.py, entities.py, services.py, events.py, workflow_mapping.py
│   ├── campaigns/                api.py, entities.py, services.py, segmentation.py, workspace.py, workflow_mapping.py
│   ├── communication_integrations/ api.py, entities.py, services.py
│   ├── contract_lifecycle_management/ api.py, entities.py, services.py
│   ├── custom_object_framework/  api.py, entities.py, services.py, layout.py
│   ├── custom_objects/           api.py, entities.py, services.py
│   ├── customer_360_cdp/         api.py, entities.py, services.py
│   ├── data_deduplication_engine/ entities.py, services.py (no api.py)
│   ├── design_system/            api.py, entities.py, services.py
│   ├── event_bus/                api.py, catalog_events.py, catalog_schema.py, core.py, handlers.py, interfaces.py, store.py
│   ├── execution_hardening/      concurrency.py
│   ├── external_apis_webhooks/   api.py, auth.py, entities.py, mapping.py, public_api_sdk.py, self_qc.py, services.py
│   ├── knowledge_base/           api.py, entities.py, services.py
│   ├── lead_management/          api.py, entities.py, services.py, events.py, workflow_mapping.py
│   ├── marketing_admin_workflow_ui/ api.py, entities.py, services.py
│   ├── omnichannel_inbox/        api.py, entities.py, services.py
│   ├── partner_channel_management/ api.py, entities.py, services.py
│   ├── plugin_framework/         api.py, entities.py, services.py, self_qc.py
│   ├── predictive_forecasting/   api.py, entities.py, services.py
│   ├── predictive_models/        api.py, entities.py, services.py
│   ├── reporting_dashboards/     api.py, entities.py, services.py
│   ├── revenue_recognition/      api.py, entities.py, services.py
│   ├── role_based_ui/            api.py, entities.py, services.py
│   ├── rule_engine/              api.py, cpq_api.py, cpq_rules.py, entities.py, services.py
│   ├── sales_cockpit/            api.py, workspace.py
│   ├── subscription_billing/     api.py, entities.py, services.py, workflow_mapping.py
│   ├── support_console/          api.py, entities.py, services.py
│   ├── territory_management/     api.py, entities.py, services.py
│   ├── ticket_management/        api.py, entities.py, services.py
│   ├── usage_billing/            api.py, entities.py, services.py
│   └── workflow_engine/          api.py, catalog.py, entities.py, services.py
│
├── services/                     Microservice runtime layer (FastAPI app + workers)
│   ├── app.py                    FastAPI application entrypoint
│   ├── bootstrap.py              Service bootstrap
│   ├── base.py                   Base classes
│   ├── models.py                 Shared SQLAlchemy models
│   ├── activity.py, ai_scores.py, campaigns.py, cases.py, collections.py
│   ├── concurrency.py, control_plane.py, conversations.py
│   ├── daily_summary.py, evaluator.py, eviction_worker.py
│   ├── followup.py, fuzzy_match.py, idempotency.py, inbox.py, intent.py
│   ├── jwt_deps.py, lead.py, overdue.py, parser.py, partners.py
│   ├── pipelines.py, recovery.py, reminders.py, repository.py, retry.py
│   ├── scheduler.py, stores.py, templates.py, territories.py
│   ├── transactions.py, workflows.py
│   └── [multiple engine.py, internal.py, public.py, service.py, repository.py across sub-dirs]
│
├── gateway/                      Node.js API gateway (Express)
│   ├── server.js                 Express server entrypoint
│   ├── routes/                   ~43 v1-*.routes.js files (one per API domain)
│   │   ├── v1-auth.routes.js
│   │   ├── v1-leads.routes.js
│   │   ├── v1-contacts.routes.js
│   │   ├── v1-accounts.routes.js
│   │   ├── v1-opportunities.routes.js
│   │   ├── v1-followups.routes.js
│   │   ├── v1-activities.routes.js
│   │   ├── v1-cases.routes.js
│   │   ├── v1-collections.routes.js
│   │   ├── v1-campaigns.routes.js
│   │   ├── v1-communications.routes.js
│   │   ├── v1-inbox.routes.js
│   │   ├── v1-quotes.routes.js
│   │   ├── v1-orders.routes.js
│   │   ├── v1-invoices.routes.js (via v1-invoice-summaries.routes.js)
│   │   ├── v1-subscriptions.routes.js
│   │   ├── v1-payments.routes.js
│   │   ├── v1-payment-webhooks.routes.js
│   │   ├── v1-whatsapp-webhooks.routes.js
│   │   ├── v1-billing.routes.js
│   │   ├── v1-workflows.routes.js
│   │   ├── v1-tasks.routes.js
│   │   ├── v1-users.routes.js
│   │   ├── v1-roles.routes.js
│   │   ├── v1-tenants.routes.js
│   │   ├── v1-territories.routes.js
│   │   ├── v1-partners.routes.js
│   │   ├── v1-knowledge.routes.js
│   │   ├── v1-reports.routes.js
│   │   ├── v1-ai.routes.js
│   │   ├── v1-audit.routes.js
│   │   ├── v1-segments.routes.js
│   │   ├── v1-templates.routes.js
│   │   ├── v1-org-settings.routes.js
│   │   ├── v1-integrations.routes.js
│   │   ├── v1-feature-flags-mgmt.routes.js
│   │   ├── v1-governance.routes.js
│   │   ├── v1-compliance-settings.routes.js
│   │   ├── v1-privacy.routes.js
│   │   ├── v1-notification-preferences.routes.js
│   │   ├── v1-forecasts.routes.js
│   │   ├── v1-price-books.routes.js
│   │   ├── v1-emails.routes.js
│   │   └── v1-sync.routes.js
│   ├── middleware/               Auth, RBAC, rate-limit, request-id, request-validation, observability, etc.
│   ├── Dockerfile
│   └── package.json
│
├── adapters/                     External integration adapter layer
│   ├── interfaces/               messaging_adapter.py, payment_adapter.py, compliance_adapter.py, locale_adapter.py, phone_formatter.py, types.py
│   └── pakistan/                 Pakistan-specific implementations
│       ├── bootstrap/registry.py
│       ├── compliance/pakistan_compliance_adapter.py
│       ├── localization/pakistan_locale_adapter.py, pakistan_phone_formatter.py
│       ├── messaging/dialog360_adapter.py, gupshup_adapter.py, meta_api_adapter.py, twilio_adapter.py
│       └── payments/base.py, easypaisa.py, jazzcash.py
│
├── db/                           SQL schema files by domain (20 domains + migrations)
│   ├── activity_task_db/schema.sql + supporting files
│   ├── audit_compliance_db/schema.sql
│   ├── campaign_db/schema.sql
│   ├── case_ticket_db/schema.sql
│   ├── contact_account_db/schema.sql
│   ├── feature_flag_db/schema.sql
│   ├── identity_auth_db/schema.sql
│   ├── intelligence_db/schema.sql
│   ├── knowledge_db/schema.sql
│   ├── lead_management_db/schema.sql
│   ├── messaging_db/schema.sql
│   ├── notification_db/schema.sql
│   ├── opportunity_db/schema.sql
│   ├── org_tenant_db/schema.sql
│   ├── quote_order_db/schema.sql
│   ├── territory_db/schema.sql
│   ├── transaction_db/schema.sql + 4 migration .sql files
│   └── workflow_db/schema.sql
│
├── alembic/                      Alembic migration management
│   └── versions/                 12 migration files
│       ├── 0001_followup_schema.py
│       ├── 0002_followup_states_leads_idempotency.py
│       ├── 0003_collections_conversations.py
│       ├── 0004_cases_schema.py
│       ├── 0005_inbox_schema.py
│       ├── 0006_territories_schema.py
│       ├── 0007_campaigns_schema.py
│       ├── 0008_partners_schema.py
│       ├── 0009_workflows_schema.py
│       ├── 0010_ai_scores_schema.py
│       ├── 0011_domain_schemas.py
│       └── 0012_lead_management_c1_columns.py
│
├── middleware/                   Python middleware
│   └── execution_control.py
│
├── scripts/                      Backend automation scripts
│   ├── qc_gate.sh
│   ├── self_qc_*.py              (17 self-QC automation scripts per domain)
│   └── [pyc compiled files]
│
├── tests/                        Backend pytest test suite (54 test files)
│   ├── test_lead_management.py, test_campaigns.py, test_cases_api.py, etc.
│   └── [see WORKSPACE_BASELINE_AUDIT for full list]
│
├── docs/                         Backend internal docs
├── docker/                       Docker support files
├── Dockerfile                    Python services Docker image
├── docker-compose.yml            Local dev compose
├── requirements.txt              Python 3.12 deps (FastAPI, SQLAlchemy, Alembic, etc.)
├── pyproject.toml                ruff + black config, ADR-002 import guard
├── alembic.ini
├── seed_tenant_refs.sql
├── seed_c1.sql
├── .env.example
├── BACKEND-QC.md
├── CONSTRAINTS.md
├── PENDING.md
├── README.md
├── FRONTEND-BACKEND-MAPPING.md
├── market-research-gap-register.md
└── product-spec-gap-register.md
```

---

## frontend/

```
frontend/
└── src/
    ├── app/                      169 HTML pages total
    │   ├── [75 custom CRM pages — see REPOSITORY_REALITY_REPORT §2]
    │   └── [94 NexLink library/demo pages — components, charts, icons, forms, etc.]
    │
    ├── assets/
    │   ├── css/
    │   │   ├── styles.css        Main NexLink compiled CSS
    │   │   ├── styles-rtl.css    RTL variant
    │   │   └── crm-custom.css    DataTables alignment overrides + project fixes
    │   ├── js/
    │   │   ├── app/              ~110 crm-*.js page scripts
    │   │   │   ├── crm-shell.js          Shell: nav, sidebar, footer injection
    │   │   │   ├── crm-dummy.js          All dummy data (single source of truth)
    │   │   │   ├── crm-api.js            API abstraction (DUMMY_MODE flag)
    │   │   │   ├── crm-components.js     Shared components incl. pkr() formatter
    │   │   │   ├── crm-locale.js         RTL/LTR toggle
    │   │   │   └── [107 crm-<pagename>.js files — one per custom page]
    │   │   ├── main.js
    │   │   ├── appSettings.js
    │   │   ├── lottie.js
    │   │   ├── chart/
    │   │   ├── dashboard/
    │   │   └── plugins/
    │   ├── libs/                 Third-party JS/CSS libraries
    │   │   ├── jquery/jquery.min.js
    │   │   ├── bootstrap-select/
    │   │   ├── flaticon/         Icon font (flaticon uicons)
    │   │   ├── fontawesome/      FontAwesome 6
    │   │   ├── lucide/           Lucide icon font
    │   │   ├── node-waves/       Ripple effect
    │   │   └── simplebar/        Custom scrollbar
    │   ├── images/
    │   ├── json/
    │   ├── ajax/
    │   └── scss/
    │       └── basic/_basic.scss
    │
    ├── [Legacy HTML at src root — NexLink originals, pre-migration]
    │   activities.html, calendar.html, chat.html, customers.html, deals.html,
    │   employee.html, finance.html, index.html, index-rtl.html, leads.html,
    │   marketing.html, profile.html, review.html, sales.html, settings.html,
    │   task-management.html, team-management.html, user-management.html
    │
    ├── [Other src-root pages]
    │   ai/                       (AI section seed pages — own shell structure)
    │   authentication/
    │   chart/
    │   components/
    │   email/
    │   extended-ui/
    │   forms/
    │   icons/
    │   maps/
    │   pages/
    │   table/
    │
    └── serve.json                Static file server config (port 3001)
```

---

## tests/ (root-level E2E suite)

```
tests/
├── conftest.py                   Playwright fixtures + base URL config
├── test_page_load.py             Smoke: all 75+ custom pages load with CRM shell
├── test_datatable.py             DataTable rows populated on list pages
├── test_filter_chips.py          Filter chip clickability
├── test_form_submit.py           Form load + basic submit
├── test_kpi_render.py            KPI tiles have non-empty content
├── test_settings_pages.py        Settings pages render
├── test_audit_pages.py           Audit pages render
├── test_func_leads.py            Functional: leads, followups, lead-new wizard
├── test_func_contacts.py         Functional: contacts, contact-new
├── test_func_sales.py            Functional: opp-new, sales pages
├── test_func_finance.py          Functional: invoices, collections, subscriptions
├── test_func_cases.py            Functional: cases, case-new, cases-detail
├── test_func_marketing.py        Functional: campaign-new
├── test_func_automation.py       Functional: workflow-builder, report-builder
├── test_func_ai.py               Functional: ai-copilot chat
├── test_func_accounts.py         Functional: accounts search
├── test_func_activities.py       Functional: tasks
├── test_func_audit_compliance.py Functional: audit-log, export
├── test_func_identity_settings.py Functional: users, integrations, org-settings
├── test_func_inbox_knowledge.py  Functional: inbox-thread, knowledge-article
├── test_func_partners_territories.py Functional: partners, territories
├── test_func_quotes_orders.py    Functional: quote-builder
├── test_auth_contract.py         API contract: auth endpoints
├── test_billing_contract.py      API contract: billing endpoints
├── test_communications_contract.py API contract: communications
├── test_governance_contract.py   API contract: governance
├── test_integrations_contract.py API contract: integrations
├── test_reports_contract.py      API contract: reports
├── test_smoke_all_routes.py      Gateway smoke: all API routes return 2xx/4xx (not 5xx)
├── test_tenant_isolation.py      Multi-tenant data isolation tests
├── test_prod_smoke.py            Production smoke tests
├── helpers.py                    Shared test utilities
├── locustfile.py                 Locust load test
├── c5_api_security_scan.py       Security scanner
├── batch[1-8]*_results.txt       Historical test batch run outputs
├── *.png                         Playwright screenshot artifacts (200+)
└── [report-*.html, *.json]       Pytest HTML reports + security scan outputs
```

---

## bin/

```
bin/
└── pgsql/                        PostgreSQL 14 Windows binary distribution
    └── bin/                      clusterdb.exe, createdb.exe, initdb.exe, postgres.exe, etc.
```

---

*End REPOSITORY_TREE_INVENTORY.md*
