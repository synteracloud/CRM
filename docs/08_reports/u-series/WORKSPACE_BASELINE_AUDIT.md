# WORKSPACE_BASELINE_AUDIT.md
> Generated: 2026-06-20 — U0 Discovery Pass — evidence from code only

---

## 1. Tech Stack (Actual)

### Frontend
| Component | Technology | Evidence |
|---|---|---|
| Base theme | NexLink (Bootstrap 5 admin template) | styles.css, NexLink class chains throughout HTML |
| CSS framework | Bootstrap 5 | class names, component structure |
| JS base | jQuery 3.x | jquery.min.js in libs/ |
| DataTables | DataTables v2 | crm-custom.css contains DT v2 header fix |
| Charts | ApexCharts (primary) | referenced in crm-dashboard.js, crm-sales-analytics.js |
| Charts | Chart.js | chartjs.html demo page, plugin dir |
| Maps | Leaflet, jsvectormap | leaflet.html, jsvectormap.html |
| Icons | FontAwesome 6, Flaticon (uicons), Lucide | all in assets/libs/ |
| Date picker | Flatpickr | flatpickr.html, crm-marketing-analytics.js |
| Scrollbar | Simplebar | simplebar.html, simplebar.min.js |
| Ripple | node-waves | waves.min.js |
| Select | bootstrap-select | bootstrap-select.min.js |
| Animation | Lottie | lottie.js |
| RTL | Built-in via crm-locale.js | styles-rtl.css, dir attribute pattern |
| Build system | None — pure static | serve.json: static file server, no bundler |
| Dev server | npm run serve (port 3001) | serve.json in frontend/src/ |

### Backend — Gateway
| Component | Technology | Evidence |
|---|---|---|
| Runtime | Node.js (v20 per CI) | gateway/package.json, ci.yml |
| Framework | Express.js | gateway middleware structure, route files |
| Auth | JWT (HS256/RS256) | v1-auth.routes.js, jwt_deps.py pattern |
| Caching | Redis | render.yaml crm-redis, gateway env vars |
| Request ID | Custom middleware | request-id.js in gateway |
| Rate limiting | Custom middleware | rate-limit-hook.js in adapters/ |
| Validation | Custom middleware | request-validation.js |
| Observability | Custom tracing | observability.js, tracing.js |
| Idempotency | Custom | idempotency.js |

### Backend — Services
| Component | Technology | Evidence |
|---|---|---|
| Runtime | Python 3.12 | pyproject.toml target-version, ci.yml |
| Framework | FastAPI 0.115.0 | requirements.txt |
| ASGI server | Uvicorn 0.48.0 | requirements.txt, render.yaml startCommand |
| Data validation | Pydantic 2.13.4 | requirements.txt |
| ORM | SQLAlchemy 2.0.49 | requirements.txt |
| Migrations | Alembic 1.18.4 | requirements.txt, alembic/ directory |
| Database driver | psycopg2-binary 2.9.10 | requirements.txt |
| Auth/crypto | python-jose 3.5.0, cryptography 48.0.0 | requirements.txt |
| HTTP client | httpx 0.28.1 | requirements.txt |
| Linting | ruff | pyproject.toml |
| Formatting | black | ci.yml |
| Arch guard | ruff TID251 (ADR-002) | pyproject.toml banned-api rules |

### Database
| Component | Technology | Evidence |
|---|---|---|
| Primary DB | PostgreSQL (14, bundled; free plan on Render) | bin/pgsql/, render.yaml |
| Cache/queue | Redis (free plan on Render, 25MB) | render.yaml |
| Schema mgmt | Alembic (12 migrations) + raw SQL (20 schema files) | alembic/versions/, db/ |

### Deployment
| Component | Technology | Evidence |
|---|---|---|
| Platform | Render.com | render.yaml |
| CI/CD | GitHub Actions | .github/workflows/ci.yml |
| Containers | Docker (gateway + services) | Dockerfile in gateway/, backend/ |
| Region | Singapore (closest to Pakistan) | render.yaml region: singapore |
| Frontend | Render static site (no build step) | render.yaml type: static |

---

## 2. Frontend Pages — Built vs Planned

### Custom CRM Pages (DESIGN-SPEC.md §3)

| Archetype | Count Planned | Count Built | Files Confirmed |
|---|---|---|---|
| A — Dashboard/KPI | 13 | 13 | dashboard.html, leads-dashboard.html, contacts-health.html, sales-dashboard.html, quotes-dashboard.html, subscriptions-dashboard.html, support-dashboard.html, engagement-dashboard.html, knowledge-dashboard.html, workflows-dashboard.html, tenants-dashboard.html, identity-dashboard.html, audit-dashboard.html |
| B — List/Queue | 11 | 11 | followups.html, leads.html, contacts.html, accounts.html, cases.html, activity.html, tasks.html, collections.html, invoices.html, users.html, partners.html |
| C — Entity Detail | 12 | 12 | leads-detail.html, contacts-detail.html, accounts-detail.html, opportunities-detail.html, cases-detail.html, quotes-detail.html, orders-detail.html, invoices-detail.html, subscriptions-detail.html, workflow-run-detail.html, partners-detail.html, knowledge-article.html |
| D — Sales Cockpit | 1 | 1 | sales-cockpit.html |
| E — Support Console | 1 | 1 | support-console.html |
| F — Marketing Workspace | 1 | 1 | marketing-workspace.html |
| G — Settings/Admin | 9 | 9 | org-settings.html, user-management-crm.html, roles.html, billing-settings.html, integrations.html, notifications.html, feature-flags.html, compliance.html, territories.html |
| H — Reporting/Analytics | 7 | 7 | sales-analytics.html, marketing-analytics.html, support-analytics.html, finance-analytics.html, workflow-analytics.html, audit-report.html, report-builder.html |
| I — Form/Wizard | 6 | 6 | lead-new.html, contact-new.html, opportunity-new.html, case-new.html, quote-builder.html, campaign-new.html |
| J — Audit/Compliance | 5 | 5 | audit-log.html, compliance-report.html, data-governance.html, rbac-audit.html, privacy.html |
| K — Builder/Canvas | 4 | 4 | workflow-builder.html, object-builder.html, rule-builder.html, approval-lanes.html |
| L — Inbox/Communication | 3 | 3 | inbox.html, inbox-thread.html, routing-config.html |
| M — AI/Copilot | 2 | 2 | ai-copilot.html, ai-insights.html |
| **TOTAL** | **75** | **75** | All 75 custom HTML pages present in app/ |

**Status of all 75:** Marked ⏳ in DESIGN-SPEC.md — HTML built and browser-approved, pending full live-API re-verification pass.

### NexLink Library Pages (inherited from theme)
- Approximately 94 demo/component pages present in app/ (accordion, alerts, badge, carousel, forms, charts, icons, etc.)
- **Total pages in app/: 169**

### Legacy Pages at frontend/src/ root
18 .html files remaining at the src root (pre-migration originals — activities.html, calendar.html, chat.html, etc.). These are the NexLink originals that the custom app/ pages replaced. Not served by the app navigation.

---

## 3. CSS/JS Assets Present

| Asset | Location | Purpose |
|---|---|---|
| styles.css | assets/css/ | NexLink compiled main CSS |
| styles-rtl.css | assets/css/ | RTL variant |
| crm-custom.css | assets/css/ | DataTables v2 header fix, per-table alignment rules |
| crm-shell.js | assets/js/app/ | Shell: nav injection, sidebar, footer at runtime |
| crm-dummy.js | assets/js/app/ | All dummy data (entities: leads, contacts, opportunities, etc.) |
| crm-api.js | assets/js/app/ | API abstraction layer (DUMMY_MODE: true in all pages currently) |
| crm-components.js | assets/js/app/ | Shared UI: pkr() PKR formatter, badge helpers |
| crm-locale.js | assets/js/app/ | RTL/LTR toggle |
| crm-[pagename].js | assets/js/app/ | 107 page-specific scripts (one per custom page) |
| crm-shell.js.bak | assets/js/app/ | Backup of shell script |

---

## 4. Configuration Files Present

| File | Purpose |
|---|---|
| backend/requirements.txt | Python production dependencies |
| backend/pyproject.toml | ruff/black config + ADR-002 import guards |
| backend/alembic.ini | Alembic migration config |
| backend/docker-compose.yml | Local dev environment |
| backend/Dockerfile | Python services container |
| backend/gateway/Dockerfile | Gateway container |
| backend/.env.example | Environment variable template |
| .env.local | Local overrides (not in git) |
| render.yaml | Render.com IaC deployment spec |
| .pre-commit-config.yaml | Pre-commit hooks |
| .semgrep/ | Custom semgrep security rules |
| frontend/src/serve.json | Static dev server config |
| .gitignore | Git ignore rules |

---

## 5. Documentation Files Present (22 root-level)

| File | Purpose |
|---|---|
| README.md | Project overview |
| PRODUCT-SPEC.md | Product requirements |
| DESIGN-SPEC.md | Master screen inventory + build phases |
| FRAMEWORK.md | Frontend build protocol, CSS/JS stack rules |
| CLAUDE.md | AI build instructions |
| SCREEN-ARTEFACTS.md | QC log of browser-approved pages |
| SESSION-HANDOFF.md | Session context handoff |
| PENDING.md | Open issues tracker |
| PROGRESS.md | Build progress log |
| PAGE-BUILD-PROTOCOL.md | Page build checklist |
| CHANGELOG.md | Version history |
| CATALOGUE-MERGE-PLAN.md | Doc consolidation plan |
| DOC-READ-LOG.md | Doc read tracking |
| MAPPING-TRACKER.md | API↔UI mapping tracker |
| SYSTEM-SNAPSHOT.md | System state snapshot |
| DOC-CATALOGUE.md | Documentation index |
| COMMERCIALISATION-PLAN.md | Go-to-market plan |
| RENDER-DEPLOY.md | Render.com deployment guide |
| REBUILD-PLAN.md | Rebuild planning |
| CONTRIBUTING.md | Contributor guide |
| U0 — REPOSITORY REALITY DISCOVERY.md | This scan trigger |
| U1 — AUTHORITY RECONSTRUCTION.md | Companion authority doc |

---

## 6. Backend Scripts Present

| Script | Purpose |
|---|---|
| backend/scripts/qc_gate.sh | QC gate shell script |
| backend/scripts/self_qc_automation_journeys.py | Automation journeys self-QC |
| backend/scripts/self_qc_b5_integrations.py | B5 integrations self-QC |
| backend/scripts/self_qc_b8_cpq_rules_engine.py | CPQ rules engine self-QC |
| backend/scripts/self_qc_campaigns_segmentation.py | Campaigns/segmentation self-QC |
| backend/scripts/self_qc_event_bus.py | Event bus self-QC |
| backend/scripts/self_qc_execution_hardening.py | Execution hardening self-QC |
| backend/scripts/self_qc_failure_recovery.py | Failure recovery self-QC |
| backend/scripts/self_qc_final_supervisor.py | Final supervisor QC |
| backend/scripts/self_qc_integration_end_to_end.py | Integration E2E self-QC |
| backend/scripts/self_qc_lead_management.py | Lead management self-QC |
| backend/scripts/self_qc_omnichannel_inbox.py | Inbox self-QC |
| backend/scripts/self_qc_system_hardening.py | System hardening self-QC |
| backend/scripts/self_qc_ticket_management.py | Ticket management self-QC |
| backend/scripts/self_qc_workflow_engine.py | Workflow engine self-QC |

---

## 7. Backend: Present

**Yes** — full Python FastAPI services layer (34 domain modules in src/) + Node.js Express gateway with 43 API route groups. See REPOSITORY_REALITY_REPORT for detail.

---

## 8. Tests: Present

| Suite | Location | Count | Type |
|---|---|---|---|
| Backend unit/integration | backend/tests/ | 79 .py test files | pytest | [corrected from 54 by U10 remediation 2026-06-21]
| Frontend E2E | tests/ (root) | ~30 .py test files | Playwright |
| API contract | tests/ (root) | 7 contract test files | httpx + pytest |
| Load testing | tests/locustfile.py | 1 file | Locust |
| Security scan | tests/c5_api_security_scan.py | 1 file | custom |
| CI coverage threshold | ci.yml | 80% minimum enforced | pytest-cov |

Screenshot evidence of E2E runs: 200+ .png artifacts in tests/ directory.
Batch test result logs: batch1–batch8 (multiple iterations) in tests/.

---

## 9. CI/CD: Present

**File:** `.github/workflows/ci.yml`
**Trigger:** push to main/feat/fix/chore branches + PRs to main + version tags (v*.*.*)
**Jobs:**
1. backend-lint (ruff + black)
2. backend-test (pytest ≥80% coverage)
3. security-scan (pip-audit + npm audit + semgrep)
4. arch-guard (ADR-002 ruff TID251)
5. gateway-lint (ESLint)
6. api-contracts (httpx contract tests against live gateway)
7. build-gateway (Docker image)
8. build-services (Docker image)
9. deploy-staging (Render.com webhook, on main push)
10. smoke-staging (pytest smoke against staging URL)
11. deploy-prod (Render.com webhook, on version tag)

---

## 10. Deployment Assets: Present

| Asset | Description |
|---|---|
| render.yaml | Render.com Blueprint — 3 web services + PostgreSQL + Redis |
| backend/Dockerfile | Python services image |
| backend/gateway/Dockerfile | Node.js gateway image |
| backend/docker-compose.yml | Local dev stack |
| RENDER-DEPLOY.md | Manual deployment guide |

---

*End WORKSPACE_BASELINE_AUDIT.md*
