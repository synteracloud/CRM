# Changelog

All notable changes to the Pakistan CRM OS are documented here.

Format: [Semantic Versioning](https://semver.org). Each entry covers a build session or phase.

---

## [Unreleased]

---

## [0.39.0] — 2026-05-31 — Phase 6 wiring extension: all 75 pages live

### Backend — 5 new inline gateway routes

| Route file | Endpoints | Pages served |
|---|---|---|
| `v1-billing.routes.js` | `GET /billing/plans`, `GET/PATCH /billing/subscription`, `POST /billing/subscription/upgrade|downgrade`, `GET /billing/invoices`, `GET /billing/entitlements` | G-04 |
| `v1-integrations.routes.js` | `GET /integrations`, `PATCH /integrations/:provider`, `POST /integrations/:provider/test` (4 seeded providers) | G-05 |
| `v1-governance.routes.js` | `GET /governance/classification|retention|sar`, `POST /governance/sar` (30-day SLA due date) | J-03 |
| `v1-reports.routes.js` | `GET/POST /reports/definitions`, `POST /reports/execute` (8 canonical KPIs + 7 named RM metrics) | H-07 |
| `v1-communications.routes.js` | `GET /communications/engagement` (CommunicationEngagementRM shape, 5 channel rows) | A-08 |

All routes use inline in-memory store with Pakistan-locale seed data. No downstream service dependency. External providers (billing, integration APIs, governance service) are pluggable by swapping the inline store for a real proxy.

### Frontend — 5 JS drivers rewritten

| Page | Driver | Primary API call(s) |
|---|---|---|
| G-04 billing-settings.html | crm-billing-settings.js | `billing.plan()` → #bill-plan/#bill-seats/#bill-renewal; `billing.invoices()` → #billing-invoices tbody |
| G-05 integrations.html | crm-integrations.js | `integrations.list()` → per-provider status badges; `integrations.test(provider)` → test-connection button |
| J-03 data-governance.html | crm-data-governance.js | `governance.classification/retention/sarList()` + `privacy.consentList()` → 4 tabs |
| H-07 report-builder.html | crm-report-builder.js | `reports.execute({metric_key,group_by})` per metric → live ApexCharts; `reports.create()` → Save Report button enabled |
| A-08 engagement-dashboard.html | crm-engagement-dashboard.js | `communications.engagement()` → 6 KPI tiles + channel chart; `campaigns.list()` → campaign queue |

### crm-api.js — 5 new namespaces

`billing`, `integrations`, `governance`, `reports`, `communications`

### Spec docs amended

- `b9-p09-settings-admin.md` §4 — G-04 billing routes + subscription/invoice response shapes; G-05 integrations routes + provider shape
- `b9-p10-reporting-analytics.md` §2.7 — H-07 API routes table + report definition + execute response + valid metric_key list
- `b9-p01-dashboard-kpi.md` §5 — A-08 communications engagement route + full response shape

### Wiring totals

- **Previously wired:** 70 of 75 pages (5 externally blocked)
- **This session:** +5 pages (inline stubs)
- **Total wired:** 75 of 75 pages — **all browser-approved 2026-05-31**
- **Externally blocked:** 0

### P-016 exception preserved

G-04 billing-settings.html payment method section remains a static HTML stub (`JAZZCASH_STUB_MODE=true`). Plan card, seat count, renewal date, and invoice history are fully wired to `/billing/subscription` and `/billing/invoices`.

---

## [0.38.0] — 2026-05-30 — 12-page extension: all wirable pages now live

### Backend — 7 new inline gateway routes

| Route file | Endpoints | Pages served |
|---|---|---|
| `v1-org-settings.routes.js` | `GET/PATCH /org/settings` | G-01 |
| `v1-roles.routes.js` | `GET/POST/PATCH/DELETE /roles` (seeded 5 system roles) | G-03 |
| `v1-notification-preferences.routes.js` | `GET/PATCH /notification-preferences` (per-user keyed by JWT) | G-06 |
| `v1-feature-flags-mgmt.routes.js` | `GET /feature-flags`, `PATCH /feature-flags/:key` (6 seeded flags) | G-07 |
| `v1-compliance-settings.routes.js` | `GET/PATCH /compliance/settings` (retention + break-glass config) | G-08 |
| `v1-privacy.routes.js` | `GET/PATCH /privacy/consent`, `GET/POST /privacy/requests` (4 seeded contacts) | J-05 |
| `v1-tenants.routes.js` | `GET /tenants/current` (plan + entitlement summary) | A-11 |

**Also:** `GET /invoice-summaries/:id` added to `v1-invoice-summaries.routes.js` — C-08 Invoice Detail

All new routes use inline in-memory store with Pakistan-locale seed data. No downstream service dependency.

### Frontend — 12 JS drivers rewritten

| Page | Driver | Primary API call(s) |
|---|---|---|
| L-01 inbox.html | crm-inbox.js | `inbox.conversations.list()` + claim/handoff/send message wired |
| L-02 inbox-thread.html | crm-inbox-thread.js | `inbox.conversations.get(?id=)` + send/reassign/close |
| A-13 audit-dashboard.html | crm-audit-dashboard.js | `audits.list(500)` → computed metrics + chart |
| G-01 org-settings.html | crm-org-settings.js | `orgSettings.get()` / `.update()` |
| G-03 roles.html | crm-roles.js | `roles.list()` / `.update()` |
| G-06 notifications.html | crm-notifications.js | `notificationPreferences.get()` / `.update()` |
| G-07 feature-flags.html | crm-feature-flags.js | `featureFlags.list()` / `.update()` — approval gate enforced |
| G-08 compliance.html | crm-compliance-settings.js | `complianceSettings.get()` / `.update()` |
| J-05 privacy.html | crm-privacy.js | `privacy.consentList/Update()` + `privacy.dsrList/Create()` |
| A-11 tenants-dashboard.html | crm-tenants-dashboard.js | `tenants.current()` + `users.list()` + `featureFlags.list()` |
| A-03 contacts-health.html | crm-contacts-health.js | `contacts.list(500)` → computed CustomerMasterHealthRM |
| C-08 invoices-detail.html | crm-invoices-detail.js | `invoiceSummaries.getById(?id=)` + record payment |

### crm-api.js — 7 new namespaces + 1 method

`orgSettings`, `roles`, `notificationPreferences`, `featureFlags`, `complianceSettings`, `privacy`, `tenants`, `invoiceSummaries.getById()`

### Wiring totals
- **Previously wired:** 58 pages (Waves 1–3)
- **This session:** +12 pages
- **Total wired:** 70 of 75 pages
- **Remaining externally blocked:** 5 (G-04 P-016, G-05 integration service, J-03 Python activity service, H-07 report query API, A-08 email engagement data)

---

## [0.37.0] — 2026-05-30 — MR-004 + MR-005: Daily Summary + Excel Import/Export

### MR-004 — Automated Daily WhatsApp Activity Summary to Managers

**Backend (Python):**
- `services/summary/__init__.py` + `services/summary/daily_summary.py`
  - `DailySummaryReport` dataclass — aggregates leads, follow-ups, payments, escalations
  - `compute_daily_summary(tenant_id, db)` — SQLAlchemy queries; safe zero-fill when `db=None`
  - `format_summary_message(report, lang)` — i18n EN + UR (P-017 gate on UR; downgrades to EN until sign-off)
  - `send_daily_summary(...)` — dry-run mode (log only) when messaging engine absent
- `services/app.py` — `_daily_summary_scheduler()` background task registered in lifespan
  - Fires daily at `DAILY_SUMMARY_UTC_HOUR` (default 03:00 UTC = 08:00 PKT)
  - Env: `DAILY_SUMMARY_ENABLED`, `DAILY_SUMMARY_UTC_HOUR`, `DAILY_SUMMARY_OWNER_PHONE`, `DAILY_SUMMARY_TENANT_ID`, `DAILY_SUMMARY_LANG`
- `tests/summary/test_daily_summary.py` — 9 tests passing

### MR-005 — Excel / CSV Import + Export for Leads and Contacts

**Backend (gateway Node.js):**
- `GET /api/v1/leads/export` — RFC 4180 CSV, all lead fields, `Content-Disposition: attachment`
- `POST /api/v1/leads/import` — accepts `text/csv` or JSON array; dedup on phone_e164; returns `{ created, skipped, errors }`
- `GET /api/v1/contacts/export` — CSV export from in-memory store (inline, no downstream dependency)
- `POST /api/v1/contacts/import` — CSV/JSON import with phone dedup and tag parsing; always inline
- `v1-contacts.routes.js` rewritten — inline fallback for all CRUD when `GATEWAY_UPSTREAM_BASE_URL` absent; 4 seeded sample Pakistan contacts

**Frontend:**
- `crm-api.js` — `leads.export()`, `leads.import(body, ct)`, `contacts.export()`, `contacts.import(body, ct)`

**Tests:** 18 tests passing (logic tests covering CSV parsing, dedup, tag split, export header)

**Deferred:** `GET /api/v1/forecasts/summary` — H-01 now computes forecasts client-side; endpoint not needed.

---

## [0.36.0] — 2026-05-30 — Phase 6 Component 2: Wave 3 wiring (31 pages)

### Wave 3 — Steps 8–12 Tier 2 + Tier 3 wiring (31 JS drivers rewritten + crm-api.js additions)

**New API methods added to `crm-api.js`:**
- `accounts.list(params)` / `accounts.get(id)` — GET /accounts (Tier 3 opaque proxy)
- `orders.list(params)` / `orders.get(id)` — GET /orders (Tier 3 opaque proxy)

**Step 8 — Cases/Support (6 pages):** B-05, A-07, C-05 (URL param ?id=), E-01, H-03, I-04 → `CRM_API.cases.list/get/create`
**Step 9 — Knowledge + Campaigns + Routing (6 pages):** A-09, C-12, F-01, H-02, I-06 (segments live-loaded), L-03 → `CRM_API.knowledge.*`, `CRM_API.campaigns.*`, `CRM_API.inbox.queues.list`
**Step 10 — Workflows (6 pages):** A-10, C-10 (URL param ?id=), H-05, K-01 (save guard), K-02 (cfg only), K-03 (cfg only) → `CRM_API.workflows.runs.list/get`
**Step 11 — Partners + AI + Territories (5 pages):** B-11, C-11 (URL param ?id=), M-01 (risk flags live), M-02 (charts wired to live opps), G-09 (full table render) → `CRM_API.partners.*`, `CRM_API.ai.*`, `CRM_API.territories.list`
**Step 12 — Tier 3 opaque proxies (8 pages):** B-03, B-04, B-06, B-07, C-02, C-03, C-07, I-02 → `CRM_API.contacts/accounts/activities/tasks.*`; graceful fallback to dummy when downstream services unavailable

**Cumulative wired pages: 58** (Wave 1=6, Wave 2=21, Wave 3=31)

**Pattern on every driver:** parameterised `render(data...)` function; live API path with `Promise.all` where multi-source; individual `.catch()` fallbacks; pages never white-screen.

---

## [0.35.0] — 2026-05-30 — Phase 6 Component 2: Wave 2 wiring (22 pages)

### Wave 2 — Steps 2–7 Tier 1 wiring (21 JS drivers rewritten + crm-api.js additions)

**New API methods added to `crm-api.js`:**
- `opportunities.get(id)` — GET /opportunities/:id
- `opportunities.create(body)` — POST /opportunities
- `subscriptions.list(params)` / `subscriptions.get(id)` — GET /subscriptions
- `audits.list(params)` — GET /audits/events

**Pages wired (live API + graceful fallback to dummy):**

| Step | Page | Driver | Primary API call(s) |
|---|---|---|---|
| 2 | G-02 user-management-crm.html | crm-user-management-crm.js | users.list() |
| 2 | B-10 users.html | crm-users.js | users.list() |
| 2 | J-01 audit-log.html | crm-audit-log.js | audits.list() + users.list() |
| 2 | J-02 compliance-report.html | crm-compliance-report.js | audits.list() |
| 2 | H-06 audit-report.html | crm-audit-report.js | audits.list() |
| 2 | J-04 rbac-audit.html | crm-rbac-audit.js | users.list() |
| 3 | B-09 invoices.html | crm-invoices.js | invoiceSummaries.get() |
| 4 | I-03 opportunity-new.html | crm-opportunity-new.js | users + contacts + opps list; opportunities.create() on submit |
| 4 | I-05 quote-builder.html | crm-quote-builder.js | priceBooks + contacts + opps list; quotes.create() on submit |
| 5 | C-04 opportunities-detail.html | crm-opportunities-detail.js | opportunities.get(?id=) + tasks + activities + quotes (Promise.all) |
| 5 | C-06 quotes-detail.html | crm-quotes-detail.js | quotes.get(?id=) |
| 5 | C-09 subscriptions-detail.html | crm-subscriptions-detail.js | subscriptions.list() |
| 6 | A-02 leads-dashboard.html | crm-leads-dashboard.js | leads.list(500) → computed KPIs + chart |
| 6 | A-04 sales-dashboard.html | crm-sales-dashboard.js | opps + activities (Promise.all) → posture + KPIs + chart |
| 6 | A-05 quotes-dashboard.html | crm-quotes-dashboard.js | quotes.list() → posture + queue + breakdown |
| 6 | A-06 subscriptions-dashboard.html | crm-subscriptions-dashboard.js | subscriptions.list() → computed MRR/ARR/rate |
| 6 | D-01 sales-cockpit.html | crm-sales-cockpit.js | opps + tasks + activities (Promise.all) → DataTable + Kanban + pane |
| 6 | H-01 sales-analytics.html | crm-sales-analytics.js | 5-source Promise.all → KPI + 3 charts + rep table |
| 6 | H-04 finance-analytics.html | crm-finance-analytics.js | collections.list(500) → computed KPIs + aging + table |
| 7 | A-12 identity-dashboard.html | crm-identity-dashboard.js | users + audits (Promise.all) → posture + KPIs + chart |
| 7 | K-04 approval-lanes.html | crm-approval-lanes.js | quotes.list() → 4-lane board; approve button calls live API |

**Pattern applied to every driver:**
- `var cfg = window.CRM_CONFIG; var _d = window.CRM_DUMMY;`
- Parameterised `render(data...)` function
- `if (cfg && !cfg.DUMMY_MODE) { CRM_API.xxx.list().then(r => render(r.data)).catch(() => render(dummy)); } else { render(dummy); }`
- Pages never white-screen — gateway down → falls back to dummy data silently

**Wave 1 recap (6 pages wired 2026-05-30):** B-01, B-02, B-08, B-09 (reworked), I-01, C-01, A-01

**Cumulative wired pages:** 27 of ~50 wirable (Tier 1 complete; Tier 2/3 next)

---

## [0.34.0] — 2026-05-30 — Phase 6 Component 1 COMPLETE: T1–T4 audit + full doc sweep

### Phase 6 Component 1 — T1–T4 Protocol Audit (all 75 custom pages)

**Audit result:** 66/75 passed on first scan. 9 pages required fixes. All 75 now T1–T4 ✓, locked in SCREEN-ARTEFACTS.md.

**Fixes applied (18 discrete changes):**

| Category | File | Change |
|---|---|---|
| T1 | `lead-new.html` | Added missing `crm-custom.css` link |
| T2 | `dashboard.html` | Added IDs to 4 KPI `<h2>` elements + delta spans; JS setters in `crm-dashboard.js` |
| T2 | `followups.html` | `kpi-completed-today` now filters `due_at.startsWith(today)` — was counting all completed |
| T2 | `leads.html` | `+18%` growth delta now data-driven from `kpi.growth_delta` |
| T2 | `contacts.html` | 3 delta text spans now set by JS from `contactsKpi` |
| T2 | `collections.html` | `+12%`/`-3%` delta badges now set by JS from `collectionsKpi` |
| T2 | `leads-detail.html` | Lead Score card wired to `dummy.aiModelKpi.lead_score_demo` |
| T2 | `ai-insights.html` | `kpi-accuracy` reads from `aiModelKpi.model_accuracy` not hardcoded `'78%'` |
| T2 | `identity-dashboard.html` | `risk-dormant` computed from audit log (was `'0 (stub)'`) |
| T3 | `followups.html` | `dt-head-left` → `dt-head-center` on "Lead / Contact" `<th>` |
| T3 | `dashboard.html` | `dt-head-left` → `dt-head-center` on "Name" `<th>` |
| T3 | `crm-custom.css` | Added Place 3 CSS for `dt_Followups`, `dt_ScrollVertical`, `dt_Contacts` |
| T4 | `followups.html` | Filter chips `Soft/Medium/Strict` → `reminder/warning/escalated/reassigned` |
| T4 | `leads.html` | Filter chips `Contacted/Engaged` → `qualifying/nurturing` |
| T4 | `lead-new.html` | Stage dropdown `Contacted/Engaged` → `qualifying/nurturing` |
| T4 | `collections.html` | `statusBadge` expanded with `overdue/partial/unpaid`; render checks `row.is_overdue` first |
| data | `crm-dummy.js` | Added `paid_this_month_delta`, `collection_rate_delta`, `new_this_month`, `growth_delta`, `AI_MODEL_KPI` |
| js | 5 JS drivers | `crm-contacts.js`, `crm-collections.js`, `crm-leads.js`, `crm-leads-detail.js`, `crm-ai-insights.js` updated |

### Full doc sweep (all catalogued docs verified and updated)

**Architecture docs fixed:**
- `service-map.md` — AI & Predictive Models Service row + Domain Coverage Matrix entry added
- `capability-matrix.md` — AI scoring/copilot capability row + checklist entry added
- `architecture-overview.md` — service count 39→40; Domain tier ~15→~16
- `domain-model.md` — 12 Phase 5B supporting entity definitions added (SupportQueue, SLAPolicy, CaseEscalation, InboxQueue, AgentPresence, ConversationHandoff, MessageTemplate, CampaignSend, CampaignConversion, DealRegistration, PartnerActivityLog, WorkflowStep); entity count 67→79
- `data-architecture.md` — Phase 2 criteria "13 read models" → "15+ read models (see read-models.md)"
- `concurrency-control.md` — Sections E (Partners) and F (AI) added
- `gateway/README.md` — full 30-router directory tree + route map table added
- `gateway/self-qc.md` — Phase 5B route coverage note added
- `FRONTEND-BACKEND-MAPPING.md` — G-024 stale bug note fixed; Section 7 archetypes E/F/M updated

**DOC-CATALOGUE.md fixes:**
- §L header "no backend domain exists" → "all backend domains built"
- BACKEND-QC.md description "308/308" → "207 passed (Phase 4 snapshot)"
- domain-model.md count 62→79
- architecture-overview.md count 39→40
- service-map.md description updated
- concurrency-control.md description updated
- gateway README description updated
- gateway self-qc description updated
- §I Non-Negotiables: AI advisory-only rule added
- SESSION-HANDOFF.md description updated
- DOC-CATALOGUE.md §L section header fixed

**REBUILD-PLAN.md fixes:**
- Phase 4 header "IN PROGRESS" → "✓ COMPLETE"
- Stage 0 "308 tests" → "207 tests"
- Phase 5 "30 Verified Pages" → "75 Custom Pages ✓ COMPLETE"

---

## [0.33.0] — 2026-05-30 — Phase 5B CODE COMPLETE (all 7 backend domain sprints built)

### Added — 7 backend domain sprints (ORM → migration → gateway → service → tests)

**Sprint 5B-1 — Cases / Support Tickets** (`pages unblocked: B-05, C-05, E-01, A-07, H-03`)
- `services/db/models/cases.py` — 6 ORM models: Case (33 fields, SLA timers), CaseComment (immutable), CaseEscalation, SupportQueue, SLAPolicy, KnowledgeArticle
- `alembic/versions/0004_cases_schema.py` — 6 tables; PKT business-hour SLA timer; CHECK constraints on status/priority/source/sla_tier
- `gateway/routes/v1-cases.routes.js` + `v1-knowledge.routes.js` — 9 + 5 endpoints; casesRouter + supportRouter + knowledgeRouter
- `services/cases/entities.py` + `service.py` — state machine, PKT SLA computation (UTC+5, Mon–Sat 09:00–19:00), apply_transition guards
- `tests/cases/test_cases_state_machine.py` (14) + `test_cases_api.py` (15)

**Sprint 5B-2 — Shared Inbox / Routing** (`pages unblocked: L-01, L-02, L-03`)
- `services/db/models/inbox.py` — 3 ORM models: InboxQueue, AgentPresence, ConversationHandoff
- `alembic/versions/0005_inbox_schema.py` — extends conversations + 3 new tables
- `gateway/routes/v1-inbox.routes.js` — 11 endpoints; claim race-condition guard (assigned_agent_id IS NULL); handoff supervisor-only enforcement
- `services/inbox/entities.py` + `service.py` — auto_assign (round_robin/least_loaded), validate_claim, validate_handoff, presence computation
- `tests/inbox/test_inbox_service.py` (18) + `test_inbox_api.py` (16)

**Sprint 5B-3 — Territories** (`pages unblocked: G-09`)
- `services/db/models/territories.py` — 3 ORM models: Territory, TerritoryRule, TerritoryAssignment
- `alembic/versions/0006_territories_schema.py` — 3 tables; 2 partial unique indexes (one default per tenant; one active assignment per subject)
- `gateway/routes/v1-territories.routes.js` — 11 endpoints; dry-run evaluate; manual override supersedes chain
- `services/territories/entities.py` + `service.py` — 9 rule types, AND logic, priority→rule_count→uuid tiebreak conflict resolution
- `tests/territories/test_territories_service.py` (20) + `test_territories_api.py` (16)

**Sprint 5B-4 — Marketing / Campaigns** (`pages unblocked: F-01, I-06, A-08, H-02`)
- `services/db/models/campaigns.py` — 5 ORM models: Campaign (P-017 urdu_approved_by), CampaignSegment, MessageTemplate, CampaignSend, CampaignConversion
- `alembic/versions/0007_campaigns_schema.py` — 5 tables; SET NULL on template/segment delete
- `gateway/routes/v1-campaigns.routes.js` + `v1-segments.routes.js` + `v1-templates.routes.js` — 10 + 5 + 4 endpoints
- `services/campaigns/entities.py` + `service.py` — state machine, P-017 Urdu activation guard, WhatsApp opt-in gate, 30-day attribution window
- `tests/campaigns/test_campaigns_service.py` (22) + `test_campaigns_api.py` (18)

**Sprint 5B-5 — Partners** (`pages unblocked: B-11, C-11`)
- `services/db/models/partners.py` — 4 ORM models: Partner, DealRegistration, PartnerCommission (paid=immutable), PartnerActivityLog
- `alembic/versions/0008_partners_schema.py` — 4 tables; commission indexed on opportunity_id
- `gateway/routes/v1-partners.routes.js` — 13 endpoints; partnersRouter + dealRegsRouter; 409 on paid commission edit
- `services/partners/entities.py` + `service.py` — tier rates (Platinum 15%/Gold 10%/Silver 5%), commission lifecycle, deal expiry (Platinum 30d/Gold 45d/Silver none), calculate_commission(), compute_expiry_date()
- `tests/partners/test_partners_service.py` (22) + `test_partners_api.py` (18)

**Sprint 5B-6 — Workflow Execution Engine** (`pages unblocked: K-01, K-02, K-03, K-04, C-10, A-10, H-05`)
- `services/db/models/workflows.py` — 3 ORM models: WorkflowDefinition (workflow_key unique per tenant), WorkflowExecution (retry_count, parent_execution_id), WorkflowStep (append-only)
- `alembic/versions/0009_workflows_schema.py` — 3 tables; unique constraint on (tenant_id, workflow_key)
- `gateway/routes/v1-workflows.routes.js` — 10 endpoints; `/runs/*` declared before `/:id` (collision guard); 5 seeded catalog definitions + 8 executions
- `services/workflows/entities.py` + `service.py` — DSL validation, can_retry(), build_retry_execution(), finalize_execution(), simulate_execution(), compute_execution_stats()
- `tests/workflows/test_workflows_service.py` (26) + `test_workflows_api.py` (19)

**Sprint 5B-7 — AI / Predictive Models** (`pages unblocked: M-01, M-02, H-07`)
- `services/db/models/ai_scores.py` — 4 ORM models: LeadScore, ChurnPrediction, CLVEstimate, CopilotSuggestion; advisory-only (no auto-action)
- `alembic/versions/0010_ai_scores_schema.py` — 4 tables; 8 indexes; migration chain sealed 0001→0010
- `gateway/routes/v1-ai.routes.js` — 13 endpoints: lead scores (list/get/recompute), churn predictions (list/get), CLV estimates (list/get), copilot suggestions (list/dismiss/action), copilot query, model registry (list/get); 10 seeded lead scores + 5 churn predictions + 5 CLV estimates + 6 suggestions
- `services/ai/entities.py` — lead_score_v1 (9-feature weighted sum 0–100, hot/warm/cold/disqualified bands), churn_predict_v1 (risk accumulation → 0.000–1.000), clv_estimate_v1 (avg_monthly × horizon × retention_rate), 5-class intent classifier, validate_suggestion_body() (evidence_anchor guard), SCORING_MODELS catalog
- `services/ai/service.py` — AIService: score_lead, predict_churn, estimate_clv, build_suggestion, apply_dismiss, apply_action, handle_query, flag_stale, compute_score_stats
- `tests/ai/test_ai_service.py` (28) + `test_ai_api.py` (19)

### Modified — cross-file wiring for all 7 sprints

- `services/db/models/__init__.py` — 38 ORM models now registered (was 9)
- `gateway/config/rbac-scopes.js` — 6 AI scopes added; all 4 roles updated; total scope count now covers all 7 new domains
- `gateway/routes/index.js` — 15 domain routers mounted (was 8); `/ai` router added
- `frontend/src/assets/js/app/crm-api.js` — 20+ named API sections; `ai` section with 5 nested namespaces (scores/predictions/estimates/copilot/models) added
- `frontend/src/assets/js/app/crm-ai-copilot.js` — sendChat + dismiss wired to CRM_API.ai.copilot.query/dismiss when DUMMY_MODE=false
- `frontend/src/assets/js/app/crm-ai-insights.js` — loadLiveKpis() wired to CRM_API.ai endpoints when DUMMY_MODE=false
- `frontend/src/assets/js/app/crm-cases-detail.js` — claim/resolve wired
- `frontend/src/assets/js/app/crm-inbox.js` + `crm-inbox-thread.js` — claim/reassign/close wired
- `frontend/src/assets/js/app/crm-territories.js` — Edit button wired
- `frontend/src/assets/js/app/crm-campaign-new.js` — form submit wired
- `frontend/src/assets/js/app/crm-partners-detail.js` — Pay Commission button wired
- `frontend/src/assets/js/app/crm-workflow-builder.js` — Save button wired
- `frontend/src/assets/js/app/crm-workflow-run-detail.js` — Retry button wired
- `frontend/.npmrc` — `playwright_skip_browser_download=1` + `playwright_browsers_path=D:\CRM\.playwright-browsers` added (C: leakage guard)
- `PENDING.md` — Phase 5B 7/7 sprints marked complete; total 169/170 (99%)
- `SYSTEM-SNAPSHOT.md` — Fully refreshed: Phase 5B COMPLETE, Phase 6 ← NEXT, 38 ORM models, migration chain 0001→0010, ~500+ tests, 15 gateway routers

---

## [0.32.0] — 2026-05-29 — Phase 5B Specs Complete (all 7 sprint domain specs written)

### Added — 3 new domain spec docs for Phase 5B sprints

- `backend/docs/domain/marketing-campaigns.md` — Canonical backend spec for Sprint 5B-4. Campaign lifecycle state machine (draft→scheduled→active→paused→completed/cancelled); CampaignSegment rule engine (AND/OR boolean tree, 5 Pakistan preset segments); MessageTemplate contract; CampaignSend per-contact tracking; dispatch pipeline with 80 msg/min WhatsApp rate limit; delivery/read/reply receipt processing; WhatsApp opt-out (STOP / بند کریں) → `Contact.whatsapp_opted_in = false`; last-touch conversion attribution (30-day default window); P-017 Urdu approval gate baked into activation guard; 20 API endpoints; 7 events + 5 send-tracking events + 1 opt-out event; 3 scanner jobs.
- `backend/docs/domain/partners.md` — Canonical backend spec for Sprint 5B-5. Partner tier system (Platinum 15% / Gold 10% / Silver 5% commission); DealRegistration protection window (30 days Platinum, 45 days Gold); PartnerCommission lifecycle (pending→approved→paid; paid is immutable); exclusive last-write opportunity attribution; `Opportunity.attributed_partner_id` field added to `opportunities-pipeline.md`; 15 API endpoints; 11 events; 2 scanner jobs (registration expiry + tier review reminder).
- `backend/docs/domain/ai-predictive-models.md` — Canonical backend spec for Sprint 5B-7. Advisory-only architecture (no auto-action, evidence_anchor required on every suggestion); 3 rule-based v1 models: `lead_score_v1` (9-feature weighted sum 0–100, hot/warm/cold/disqualified bands), `churn_predict_v1` (risk factor accumulation → 0.000–1.000 probability, high/medium/low bands), `clv_estimate_v1` (avg_monthly_revenue × horizon × retention_rate); CopilotSuggestion entity (6 types, priority bands, dismiss/action tracking); 5-class rule-based conversational intent classifier (no LLM in v1); 15 API endpoints; 7 events; 5 scanner jobs.

### Modified — cross-references propagated

- `backend/docs/infrastructure/event-catalog.md` — 9 campaign send/attribution events added; 5 partner lifecycle events added; 7 AI events added; workflow coverage check table updated.
- `backend/docs/ui/read-models.md` — `PartnerPerformanceRM` and `PredictiveInsightRM` added to catalog and reporting coverage table.
- `backend/docs/_b9/b9-p14-ai-copilot.md` — Backend spec pointer to `ai-predictive-models.md` + `PredictiveInsightRM` added.
- `backend/docs/_b9/b9-p05-marketing-workspace.md` — Backend spec pointer to `marketing-campaigns.md` + `CommunicationEngagementRM` added.
- `backend/docs/domain/opportunities-pipeline.md` — `attributed_partner_id` field added to Opportunity entity schema.
- `REBUILD-PLAN.md` — Sprint 5B-4/5B-5/5B-7 spec paths updated from "Spec needed" to actual file paths; all 7 sprints noted as unblocked.
- `DOC-CATALOGUE.md` — §M section added for 3 new specs.

---

## [0.31.0] — 2026-05-29 — All 28 Cat 2 Pages Built (75 of 75 custom pages complete)

### Added — 28 Cat 2 pages (dummy-mode, no backend domain required)

**Archetype A — Dashboard (4)**
- `A-07` `support-dashboard.html` — Case SLA Ops Dashboard: posture strip, SLA breach KPIs, at-risk queue DataTable, case volume area chart.
- `A-08` `engagement-dashboard.html` — Engagement & Comms Dashboard: delivery/open/reply rate KPIs, active campaigns list, channel engagement bar chart.
- `A-09` `knowledge-dashboard.html` — Knowledge Base Dashboard: published/deflection/stale/zero-view KPIs, stale article queue, adoption trend chart.
- `A-10` `workflows-dashboard.html` — Workflow Automation Dashboard: posture strip, execution volume/success/failure KPIs, failed executions queue, pass/fail bar chart.

**Archetype B — List/Queue (2)**
- `B-05` `cases.html` — Case Queue: 4 KPI cards, DataTable with dual filter chips (Status × SLA), STATUS/SLA/PRI badges, custom cross-filter logic.
- `B-11` `partners.html` — Partner List: 4 KPI cards, DataTable with Tier × Status filter chips, PKR commission column, tier badges.

**Archetype C — Entity Detail (4)**
- `C-05` `cases-detail.html` — Case Detail: SLA timer identity strip, state-gated Claim/Resolve buttons, 3-tab pane (Conversation/Fields/Resolution), escalation controls by sla_state.
- `C-10` `workflow-run-detail.html` — Workflow Run Detail: execution identity strip, state-gated Retry button, 3-tab pane (Execution Log/Steps/Error Details), retry status context panel.
- `C-11` `partners-detail.html` — Partner Profile: 4-tab pane (Details/Opportunities/Commission Ledger/Relationship History), attribution summary context panel.
- `C-12` `knowledge-article.html` — Knowledge Article Detail: state-gated Publish/Edit buttons, 4-tab pane (Content/Version History/Related Articles/Feedback), article stats context panel.

**Archetype E — Support Console (1)**
- `E-01` `support-console.html` — Support Console: global SLA timer header, 3-pane layout (SLA queue / thread / customer context), click-to-select thread, escalation controls by sla_state.

**Archetype F — Marketing Workspace (1)**
- `F-01` `marketing-workspace.html` — Marketing Workspace: 4 KPI cards, campaigns DataTable, Status filter chips, TYPE/STATUS badges.

**Archetype G — Settings/Admin (1)**
- `G-09` `territories.html` — Territory Management: settings two-pane with list-group nav, territory tree table, rule editor, assignment strategy config.

**Archetype H — Analytics (3)**
- `H-02` `marketing-analytics.html` — Marketing Analytics: flatpickr date range, 4 KPI cards, channel engagement bar chart, WhatsApp opt-in trend chart, campaigns DataTable.
- `H-03` `support-analytics.html` — Support Analytics: flatpickr date range, 4 KPI cards, SLA breach trend line chart, case volume donut, cases DataTable.
- `H-05` `workflow-analytics.html` — Workflow Analytics: flatpickr date range, 4 KPI cards, pass/fail trend bar chart, failure rate by workflow bar chart, executions DataTable.
- `H-07` `report-builder.html` — Report Builder: 4-step wizard (metric selector / group-by / chart type / save), live ApexCharts preview panel.

**Archetype I — Form Wizard (2)**
- `I-04` `case-new.html` — New Case Form: 2-step wizard (Contact search + Subject/Priority → Queue/Category/Description), dummy success toast.
- `I-06` `campaign-new.html` — New Campaign Wizard: 2-step wizard (Name/Segment/Type → Template/Trigger/Schedule), P-017 Urdu string alert.

**Archetype K — Builder (4)**
- `K-01` `workflow-builder.html` — Workflow Builder: 3-pane layout (palette / canvas / inspector), simulated node graph using Bootstrap cards + CSS connectors, validate/simulate/save/publish interactions.
- `K-02` `object-builder.html` — Object Builder: object type selector, field list, layout canvas sections, layout preview form.
- `K-03` `rule-builder.html` — Rule Builder: condition row builder (dynamic add/remove), action row builder, pre-seeded discount approval routing rule, test rule simulation.
- `K-04` `approval-lanes.html` — Approval Lanes Kanban: 4-lane kanban (Draft/Pending/Approved/Rejected), quote cards with calcTotal() line-item math, discount badge.

**Archetype L — Inbox (3)**
- `L-01` `inbox.html` — Shared Inbox: channel filter chips, two-pane thread list + thread view, intent badges, auto-select first thread, relativeTime() helper.
- `L-02` `inbox-thread.html` — Inbox Thread View: WhatsApp-style bubbles, customer context strip, intent classification context panel, INTENT_ACTIONS suggested CTAs.
- `L-03` `routing-config.html` — Routing Configuration: settings two-pane, queue management table, agent capacity table, routing rules priority list, fallback config.

**Archetype M — AI (2)**
- `M-01` `ai-copilot.html` — AI Copilot: advisory banner, lead score card, next-action suggestion, risk flags, conversational CRM chat with intent classifier, all actions advisory only.
- `M-02` `ai-insights.html` — AI Insights Dashboard: win probability distribution bar chart, churn risk donut, CLV estimates bar chart, feature weight inspector read-only panel.

### Modified
- `crm-dummy.js` — 11 new datasets added: CASES, CASE_SLA_KPI, PARTNERS, CAMPAIGNS, COMMS_KPI, KNOWLEDGE_ARTICLES, KNOWLEDGE_KPI, WORKFLOW_EXECUTIONS, WORKFLOW_KPI, MESSAGE_THREADS, TERRITORIES. All exported in return object.
- `crm-custom.css` — DataTable body-alignment rules added for 7 new tables: dt_SlaQueue, dt_Cases, dt_Partners, dt_MarketingCampaigns, dt_SupportCases, dt_WorkflowExec, dt_Campaigns.
- `FRAMEWORK.md §18` — 28 new CRM_PAGE keys registered.

---

## [0.30.0] — 2026-05-29 — All Cat 1 Pages Complete (47 of 75 built)

### Added — 15 remaining Cat 1 pages

**Archetype A — Dashboard (1)**
- `A-11` `tenants-dashboard.html` — Tenant & Entitlement Dashboard: Plan/Seat/Feature KPIs, entitlements-at-limit queue, tenant summary card. Reads `d.tenantKpi` + `d.featureFlags`.

**Archetype B — List/Queue (1)**
- `B-04` `accounts.html` — Account List: Tier/Industry/City/Open Opps/Outstanding Balance columns, tier + balance filter chips. New `ACCOUNTS` dataset (12 records).

**Archetype C — Entity Detail (3)**
- `C-03` `accounts-detail.html` — Account Profile: 4-tab pane (Details/Contacts/Opportunities/Invoices), account health context panel. Demo a-002 (City Pharma Ltd).
- `C-07` `orders-detail.html` — Order Detail: immutable-after-activation badge, line items, fulfilment status, linked invoice/quote. New `ORDERS` dataset (2 records).
- `C-08` `invoices-detail.html` — Invoice Detail: Total/Paid/Balance KPI strip, payment history, proof attachments tab, reconciliation status. Demo i-001.

**Archetype G — Settings/Admin (7)**
- `G-01` `org-settings.html` — Organization Settings: Identity/Locale/Currency/Business Hours editor. Shared settings left-nav across all G pages.
- `G-03` `roles.html` — Role & Permission Editor: roles table from `d.roles.data`, permission registry (read-only), cannot delete role with active users.
- `G-04` `billing-settings.html` — Billing & Subscription: plan/seats/renewal from `d.tenantKpi`, payment method P-016 stub, invoice history.
- `G-05` `integrations.html` — Integration Settings: WhatsApp/Email/SMS/Push config, credentials masked last-4, test-connection button.
- `G-06` `notifications.html` — Notification Settings: per-event toggle table (In-App/Email/WhatsApp/SMS), quiet hours config.
- `G-07` `feature-flags.html` — Feature Flags: flag registry from `d.featureFlags`, 2-person approval modal on any toggle, all changes logged.
- `G-08` `compliance.html` — Compliance Settings: retention policy editor, data governance link, break-glass log stub.

**Archetype I — Form/Wizard (1)**
- `I-02` `contact-new.html` — New Contact Form: 2-step wizard (identity → account + tags), phone dedup warn on blur, tag multi-select.

**Archetype J — Audit/Compliance (2)**
- `J-03` `data-governance.html` — Data Governance Console: 4-tab (Classification/Retention/SAR/Consent), classification map + retention schedule from spec.
- `J-05` `privacy.html` — Consent & Privacy Manager: consent records from `d.contacts`, DSR list, erasure request form with reason required.

### Added — Dummy Data
- `ACCOUNTS` array (12 records) — account_id, name, tier, industry, owner_id, city, open_opps, outstanding_balance
- `ORDERS` array (2 records) — order_id, order_number, account_id, status, total_amount, line_items, fulfillment_status, invoice_ids
- `TENANT_KPI` object — plan_tier, seat_count, seat_limit, enabled_feature_count, entitlement_limit, renewal_date, active_sessions
- `FEATURE_FLAGS` array (6 records) — flag_key, label, enabled, category, description, rule_type
- `ROLES` array (4 records) — role_id, name, user_count, is_system, permissions[]

### Changed — Framework
- `FRAMEWORK.md §18` — 15 new CRM_PAGE keys registered
- `crm-custom.css` — `#dt_Accounts` alignment rule added
- `DESIGN-SPEC.md` — all 15 pages updated ⬜→⏳

### Fixed — Settings page layout bug (nav-pills collision)
- **Root cause:** `nav flex-column nav-pills` in page body collided with crm-shell.js sidebar CSS (which owns `.nav-pills` globally), constraining row height and clipping right-column content. Combined with missing `height:auto` on stacked cards, caused footer to appear mid-page on roles/billing/integrations/notifications/compliance.
- **Fix applied to 7 G-pages:** left nav → `list-group list-group-flush`; all right-column cards → `style="height:auto"`; container → `pb-4`.
- **Rule locked in:** `CLAUDE.md` §4 (new rule), `PAGE-BUILD-PROTOCOL.md` Step 20 (new), `FRAMEWORK.md` build checklist (new item).

### Status
- **Built total:** 47 of 75 custom pages
- **Cat 1 complete** — 0 Cat 1 unbuilt pages remain
- **Cat 2 remaining:** 28 pages — all blocked by missing backend domain

---

## [0.29.0] — 2026-05-29 — 22 Custom Pages Built + Cat 1 Complete

### Added — Custom Pages (this session)

**Archetype A — Dashboard (4 new)**
- `A-02` `leads-dashboard.html` — Lead Funnel Dashboard: posture strip, 6 KPI tiles, idle-leads queue, stage bar chart. Reads `CRM_DUMMY.leads/leadFunnelKpi/deltas`.
- `A-03` `contacts-health.html` — Customer Health Dashboard: completeness posture, 4 KPIs, open-cases queue, completeness bar chart. Reads `CRM_DUMMY.contacts/contactsKpi`.
- `A-05` `quotes-dashboard.html` — Quote Approval Dashboard: stalled-quote posture, 4 KPIs, pending-approval queue, discount-band bar chart. Reads `CRM_DUMMY.quotes`.
- `A-06` `subscriptions-dashboard.html` — Subscription Revenue Dashboard: churn-risk posture, MRR/ARR/Renewal Rate KPIs, delinquent-accounts queue, cohort retention area chart, expansion-vs-churn panel. P-016 stub comment. Reads `CRM_DUMMY.subscriptionKpi/subscriptions`.
- `A-12` `identity-dashboard.html` — Identity & Access Posture Dashboard: privileged-account posture, 4 KPIs, escalation queue, activity-type chart.
- `A-13` `audit-dashboard.html` — Platform Audit & Reliability Dashboard: deny-count posture, 4 KPIs, deny-event queue, action-type donut chart.

**Archetype B — List/Queue (3 new)**
- `B-06` `activity.html` — Activity Feed: read-only event log. Reads `CRM_DUMMY.activities`.
- `B-07` `tasks.html` — Task Queue: overdue-pinned. Reads `CRM_DUMMY.tasks`.
- `B-09` `invoices.html` — Invoice Queue: Total/Paid/Balance columns, overdue dates red, filter chips by status. New `INVOICES` dummy dataset (10 records).
- `B-10` `users.html` — User Directory: admin-only, role badge list, suspend + reset password actions.

**Archetype C — Entity Detail (3 new)**
- `C-02` `contacts-detail.html` — Customer 360: 4-tab main pane, related leads/activities, account health context. Demo c-001.
- `C-04` `opportunities-detail.html` — Opportunity Detail: re-processed, Quotes tab reads `CRM_DUMMY.quotes`.
- `C-06` `quotes-detail.html` — Quote Detail: line items, approval history, terms. Reads `CRM_DUMMY.quotes`.
- `C-09` `subscriptions-detail.html` — Subscription Detail: status-gated buttons (Renew/Suspend/Cancel), MRR/ARR strip, 4-tab pane, churn risk + expansion context. New `SUBSCRIPTIONS` dummy dataset (8 records). Demo sub-001.

**Archetype D — Sales Cockpit (1)**
- `D-01` `sales-cockpit.html` — Re-processed: pipeline rail, kanban, deal pane, forecast + next-actions all CRM_DUMMY-wired.

**Archetype G — Settings/Admin (1 new)**
- `G-02` `user-management-crm.html` — User Management Admin: posture strip (admin role count), 2-step Invite User wizard modal, Edit Role / Suspend / Reset Password confirm dialogs. Filter chips: Role + Status.

**Archetype H — Analytics (3 new)**
- `H-01` `sales-analytics.html` — Sales Analytics: weighted pipeline KPI, stage bar chart, forecast donut, lead funnel chart, rep performance table.
- `H-04` `finance-analytics.html` — Finance Analytics: aging buckets chart, revenue trend, collections table. P-016 stub.
- `H-06` `audit-report.html` — Audit Report: stacked allow/deny chart, hash-chain panel with row-click verify, privileged access log, signed CSV export.

**Archetype I — Forms/Wizard (3 new)**
- `I-01` `lead-new.html` — New Lead Form: 2-step wizard with inline dedup.
- `I-03` `opportunity-new.html` — New Opportunity Form: 2-step wizard, flatpickr close date.
- `I-05` `quote-builder.html` — CPQ Quote Builder: 4-step wizard, discount >10% approval routing, autosave every 60s after step 1.

**Archetype J — Audit/Compliance (3 rebuilt)**
- `J-01` `audit-log.html` — Rebuilt: shell fixed (removed hardcoded header/aside), summary badges wired to CRM_DUMMY.
- `J-02` `compliance-report.html` — Rebuilt: KPIs now derived from CRM_DUMMY.AUDIT_LOG counts (no Math.random).
- `J-04` `rbac-audit.html` — Rebuilt: permission matrix + alerts from CRM_DUMMY.users; assignment log from CRM_DUMMY.rbacAssignmentLog.

### Added — Dummy Data
- `INVOICES` array (10 records) — invoice_id, invoice_number, account_name, total_amount, paid_amount, status, due_date
- `SUBSCRIPTIONS` array (8 records) — subscription_id, plan, account_id, mrr, arr, status, billing_cycle, churn_risk
- `SUBSCRIPTION_KPI` object — mrr, arr, renewal_rate, churn_flag_count, delinquency_count, cohort_retention series

### Changed — Framework
- `FRAMEWORK.md §18` — 4 new CRM_PAGE keys registered: `user-management-crm`, `invoices`, `subscriptions-detail`, `subscriptions-dashboard`
- `crm-custom.css` — 2 new DataTable alignment rules: `#dt_UMgmt`, `#dt_Invoices`
- `DESIGN-SPEC.md` — A-06/B-09/C-09/G-02 status updated from ⬜ to ⏳

### Status
- **Built total:** 32 of 75 custom pages
- **All Cat 1 pages complete** — 0 Cat 1 unbuilt pages remain
- **Remaining:** 43 pages (15 Cat 1 unbuilt, 28 Cat 2 — no backend domain)

---

## [0.28.0] — 2026-05-28 — b9-p Alignment + 75-Page Mapping Analysis

### Changed — b9-p Spec Alignment (8 specs updated)
- `b9-p02-list-queue.md` — Lead.stage canonical enum added; FollowupTask.escalation_level vocabulary corrected (Soft/Medium/Strict → none/reminder/warning/escalated/reassigned); field names corrected (enforcement_level → escalation_level, attempt_count → attempts_count, status → state); Invoice.amount_due corrected (was total_amount)
- `b9-p04-support-console.md` — CaseStatus enum added (OPEN/ASSIGNED/IN_PROGRESS/WAITING_ON_CUSTOMER/RESOLVED/ESCALATED/CLOSED); sla_state derivation documented; cases-domain.md referenced as entity contract
- `b9-p06-entity-detail.md` — Case Detail: full CaseStatus state machine + header button state gates from cases-domain.md; Subscription Detail: Subscription.status enum (draft/trialing/active/past_due/paused/cancelled/expired) + state-gated buttons from payments-revenue.md
- `b9-p09-settings-admin.md` — G-02/G-03 route conflict resolved (separate pages); G-07 feature flag rule_type enum + change approval process; G-09 territory contract updated to territory-management.md; G-01/G-04/G-06/G-08 added (were missing); sections renumbered 2.1–2.14
- `b9-p10-reporting-analytics.md` — Full restructure: H-01–H-07 now explicitly defined anchored to kpi-data-pipelines.md; original enterprise surfaces (Predictive Forecasting, AI Scoring, Usage Billing) retained as Phase 6 addenda
- `b9-p11-form-wizard.md` — I-01/I-02/I-03/I-04/I-06 simple entity creation forms added (§2.1–§2.6); original 6 enterprise wizards renumbered §2.7–§2.12
- `b9-p12-audit-compliance.md` — J-01 route fixed (/app/audit); J-02 Compliance Report + J-04 RBAC Audit + J-05 Consent & Privacy Manager added
- `b9-p13-inbox-communication.md` — shared-inbox.md entities integrated (InboxQueue, AgentPresence, ConversationHandoff); L-02 route unified to /app/inbox/:thread_id; L-03 Routing Configuration added

### Changed — DESIGN-SPEC.md
- Header updated: last updated date, build state, ⏳ status added to legend
- A-01, B-01, B-02, B-03, B-08, C-01, I-01 updated to ⏳ with protocol audit gap notes
- Archetype section headers: C/G/H/I/J/L updated with b9-p fix notes
- §5 Archetype Quick Reference updated with one-line change summaries

### Added — 75-Page Backend Mapping Analysis
- `backend/FRONTEND-BACKEND-MAPPING.md` Section 7: fresh 75-page 3-category analysis
  - Category 1 (both sides exist): 25 pages
  - Category 2 (frontend spec, little/no backend): 42 pages — 23 have zero gateway domain
  - Category 3 (backend richer than spec): 8 pages
- Confirmed: 23 gateway route files exist; no routes for cases/marketing/workflows/territories/partners/knowledge/AI/inbox

### Changed — Tracking Docs
- `SYSTEM-SNAPSHOT.md` — full refresh: date, refresh trigger, frontend state, archetype table, immediate next step
- `REBUILD-PLAN.md` — resume point updated
- `PROGRESS.md` — Phase 5 table updated with protocol audit findings per page
- `PENDING.md` — Phase 5 section rewritten; DOC-BLOCKED REGISTRY updated with correct block reasons (b9-p blocks lifted where fixed; no-backend-domain added as primary blocker for 23 pages)

### Protocol Audit Findings (10 built pages)
- T1 failures: I-01 (crm-custom.css missing)
- T2 failures: A-01 (posture strip + KPI h2 hardcoded), B-01/B-02/B-03/B-08 (delta text hardcoded), B-02 (chart data hardcoded), C-01 (activity timeline partial), I-01 (stage vocabulary stale)
- T3 failures: B-01/B-02/B-03 (DataTable Place 3 CSS missing for dt_Followups/dt_ScrollVertical/dt_Contacts)
- T4 failures: B-01 (level filter Soft/Medium/Strict), B-02 (stage filter Contacted/Engaged), B-08 (status filter vocabulary)
- C-04/D-01/A-04 T2 unverified — AI self-certified in previous session

---

## [0.27.0] — 2026-05-27 — Phase 2 Visual QC + 3 Pages Browser-Locked

### Locked
- `sales-cockpit.html` (D-01) — browser-approved 2026-05-27
- `opportunities-detail.html` (C-04) — browser-approved 2026-05-27
- `sales-dashboard.html` (A-04) — browser-approved 2026-05-27

### Fixed — Frontend
- `sales-cockpit.html` + `crm-sales-cockpit.js` + `crm-custom.css` — `dt_Pipeline` all-column centre alignment (3-place fix: dt-head-center on all th, dt-body-center on all JS column defs, `!important` CSS rule)
- `sales-cockpit.html` — right rail `align-self-start` added to prevent footer cut-off caused by Bootstrap stretch on h-100 sibling column
- `sales-dashboard.html` — `mb-3` added to all 3 content rows (posture, execution queue, stage velocity); rows were flush/merged without it

### Fixed — Docs
- `PROGRESS.md` — D-01/C-04/A-04 updated ⏳ → ✓
- `DESIGN-SPEC.md` — D-01/C-04/A-04 updated ⬜ → ✓
- `SCREEN-ARTEFACTS.md` — sign-offs for D-01/C-04 updated; A-04 full record added; ToC updated to 10 pages
- `SYSTEM-SNAPSHOT.md` — phase state and next steps updated
- `DOC-CATALOGUE.md` — SCREEN-ARTEFACTS/PROGRESS/CHANGELOG entries updated
- `PENDING.md` — Build Phase 1 note updated; C-06/I-05/A-02/I-03 next steps added

---

## [0.26.0] — 2026-05-27 — Phase M Bidirectional Alignment: 27 gaps closed

### Fixed — Backend Gateway Routes

- `backend/gateway/routes/v1-opportunities.routes.js` — `account_name` added to POST body destructure, in-memory entity object, and downstream repo call; removed "not stored" limitation
- `backend/gateway/routes/v1-contacts.routes.js` — downstream schema contract comment added: documents required response fields (`contact_id`, `display_name`, `phone_e164`, `email`, `account_id`, `account_name`, `completeness_score`, `created_at`, `open_cases`, `idle`, `tags`, `last_touchpoint`)
- `backend/gateway/routes/v1-tasks.routes.js` — downstream schema contract comment added: documents required response fields (`task_id`, `title`, `status`, `due_at`, `owner_id`, `entity_type`, `entity_id`, `priority`)
- `backend/gateway/routes/v1-forecasts.routes.js` — `GET /forecasts` inline handler added; response shape: `{ period, generated_at, weighted_value, by_category: { pipeline, best_case, commit, closed — each with count + total_value }, stage_breakdown[] }`; replaces flat shape that had no `by_category` structure
- `backend/gateway/routes/v1-collections.routes.js` — reminder endpoint `POST /collections/invoices/:invoice_id/reminders` added; in-memory invoice PK corrected `invoice_summary_id` → `invoice_id`; fields added: `account_name`, `account_tier`, `is_overdue` (computed at GET time), `last_reminder_at`; reconcile handler stale field reference fixed

### Fixed — Frontend JS Drivers

- `frontend/src/assets/js/app/crm-dummy.js` — FORECASTS constant rewritten to `by_category` shape with real PKR values; COLLECTIONS records: `inv_id` → `invoice_id`, `amount` → `amount_due`, added `invoice_number` + `last_reminder_at` ISO timestamps; PRICE_BOOKS constant added (2 price books with products arrays, `page`/`page_size` pagination); QUOTES constant added (3 quotes with `opportunity_id` field); return block updated to expose `priceBooks` and `quotes` namespaces
- `frontend/src/assets/js/app/crm-api.js` — `priceBooks.list()` wired to `d().priceBooks` (was returning empty stub); `quotes` namespace added (list/get/create); collections `recordPayment` + `sendReminder` dummy responses corrected: `inv_id` → `invoice_id`
- `frontend/src/assets/js/app/crm-leads-detail.js` — `STAGE_ORDER` aligned to backend: `['new','qualifying','nurturing','proposal','negotiation','won']`; `STAGE_CFG` keys aligned: removed `contacted/engaged/qualified/converted`, added `qualifying/nurturing/won/lost/disqualified`; `LEVEL_CFG` keys aligned to backend enum: `none/reminder/warning/escalated/reassigned` (was `soft/medium/strict`)
- `frontend/src/assets/js/app/crm-collections.js` — DataTable column 0: `data:'inv_id'` → `data:'invoice_number'`; column 2: `data:'amount'` → `data:'amount_due'`; column 5 `last_reminder_at`: render function added (formats ISO timestamp to relative time)
- `frontend/src/assets/js/app/crm-sales-dashboard.js` — `d.forecasts.current_month` → `d.forecasts`; all KPI reads updated: `fc.weighted_pipeline` → `fc.weighted_value`; `fc.closed.*` → `fc.by_category.closed.*`; `fc.commit.*` → `fc.by_category.commit.*`; `fc.best_case.*` → `fc.by_category.best_case.*`
- `frontend/src/assets/js/app/crm-sales-cockpit.js` — same forecasts shape fix as sales-dashboard; priority badge map corrected: `{urgent:'danger',high:'warning',medium:'primary',low:'secondary'}` → `{hot:'danger',warm:'warning',cold:'secondary'}` (2 occurrences)
- `frontend/src/assets/js/app/crm-opportunities-detail.js` — priority badge map corrected: `{urgent:'danger',high:'warning',medium:'primary',low:'secondary'}` → `{hot:'danger',warm:'warning',cold:'secondary'}`
- `frontend/src/assets/js/app/crm-quote-builder.js` — hardcoded `PRICE_BOOK` array replaced with `d.priceBooks.data[0].products` lookup

### Tracking Docs Updated

- `backend/FRONTEND-BACKEND-MAPPING.md` — header updated (27 gaps, 0 deferred); Sec 1.2 account_name in opp entity; Sec 1.4 collections invoice schema corrected + reminder endpoint added; Sec 1.8 forecasts GET endpoint + by_category shape documented; Sec 4 all page gap entries updated to ✅; Sec 5 archetypes A/B/C/D/K → 🟢 Ready; gap closure table replaced with full 27-gap record
- `PENDING.md` — bidirectional alignment task added as complete under Build Phase 1
- `SYSTEM-SNAPSHOT.md` — refresh trigger + phase table updated
- `DOC-CATALOGUE.md` — 5 entries updated (header, PENDING.md, SYSTEM-SNAPSHOT.md, MAPPING-TRACKER.md, FRONTEND-BACKEND-MAPPING.md)

### State after this version

- All 8 Build Phase 1 pages fully aligned (dummy data ↔ backend contracts bidirectionally verified)
- 27 gaps closed, 0 deferred
- DUMMY_MODE: true — no live wiring yet; wiring sprint gated on Build Phase 1 review lock
- Build Phase 2 (7 Finance & Support pages) gated on user review and approval of Build Phase 1

---

## [0.25.0] — 2026-05-25 — Phase 4 Stage 3: Code Overlay Round 1

### Added
- `backend/docs/phase4-gap-register.md` — living gap register; 28 gaps catalogued across Groups A–E (persistence, security, domain APIs, API standards, observability/CI)
- `backend/alembic/versions/0002_followup_states_leads_idempotency.py` — migration: `snoozed`+`failed` followup states, `leads.closure_reason`, FK `followup_tasks→leads`, `idempotency_records` table
- `backend/alembic/versions/0003_collections_conversations.py` — migration: `invoices`, `payments`, `reconciliation_cases`, `conversations`, `conversation_messages` tables
- `backend/services/db/models/collections.py` — `Invoice`, `Payment`, `ReconciliationCase` ORM models
- `backend/services/db/models/conversations.py` — `Conversation`, `ConversationMessage` ORM models
- `backend/services/db/models/idempotency.py` — `IdempotencyRecord` ORM model (4-tuple key, state: in_flight/complete/conflict)

### Fixed — Security / Auth
- `services/auth/jwt_deps.py` (B-001) — `TokenClaims` extended from 4 → 9 claims: added `role_ids`, `scopes`, `aud`, `iss`, `territory_ids`; conditional aud/iss verification from env vars

### Fixed — API Correctness
- `gateway/routes/v1-leads.routes.js` (D-001) — `VALID_STAGES` aligned to DB + spec: `qualifying, nurturing, won, lost, disqualified` (was `new, contacted, qualified, proposal, negotiation, closed_won, closed_lost`)

### Fixed — State Machines
- Migration 0002 (D-002) — `followup_tasks.state` CHECK extended to include `snoozed` + `failed` states
- Migration 0002 (D-010) — `leads.closure_reason TEXT NULL` column + FK `followup_tasks → leads`

### Fixed — Bugs
- `services/activity/engine.py` — `_parse_rfc3339`: `.replace("Z", "+00:00")` → `.rstrip("Z")` — prevented double-offset `+00:00+00:00` crash (`ValueError: Invalid isoformat string`)
- `services/dashboard/owner/service.py` — `_parse_dt`: same double-offset fix
- `adapters/pakistan/payments/jazzcash.py` — `normalize_transaction`: only divide by 100 for `pp_Amount` (native JazzCash paise format); `amount` fallback key is already PKR
- `services/collections/service.py` — `_payments` dict added; fixes `AttributeError` from dashboard service

### Fixed — Infrastructure
- `src/event_bus/catalog_schema.py` — path updated for Stage 2E subdirectory restructure
- `src/event_bus/catalog_events.py` — 9 missing events added: `lead.conversion.failed.v1`, 2 `case.sla.*`, 6 `partner.*` events
- `scripts/self_qc_event_bus.py`, `self_qc_execution_hardening.py`, `self_qc_final_supervisor.py` — all doc paths updated for Stage 2E 9-subdir structure

### Verified
- 314/314 tests passing (was 308 before Stage 3)
- 96/96 library pages HTTP 200

---

## [0.24.0] — 2026-05-25 — Phase 4 Stage 2: Doc Fix + Restructure

### Changed
- All 71 flat `backend/docs/*.md` files reorganised into 9 subdirectories (Diátaxis + DDD taxonomy): `architecture/`, `security/`, `domain/`, `infrastructure/`, `adapters/`, `product/`, `ui/`, `_b9/`, `_qc/`
- Ownership blocks (PRIMARY / Defers to / Do not re-define) added to all 51 core spec files (Stage 2A)
- 6 gap fills added to owning spec files (Stage 2B): `territory_ids` JWT claim, EmployeePerformanceRM, TerritoryPerformanceRM, TenantUsageMetric, deny-by-default, tone tiers
- 6 inconsistencies resolved — canonical values locked, non-PRIMARY files updated (Stage 2C)
- 14 duplicate definitions replaced with cross-reference pointers; 4 misplaced content blocks moved (Stage 2D)
- All cross-references + `DOC-CATALOGUE.md` paths updated for new subdirectory structure (Stage 2E)
- `DOC-CATALOGUE.md` — 103 active docs catalogued (75 backend + others)

### Verified
- 308/308 tests passing
- 96/96 library pages HTTP 200

---

## [0.23.1] — 2026-05-18 — Pre-Phase-4 Audit: 9 Fixes

### Fixed — Critical / High
- `src/ticket_management/entities.py` — added `Literal` to typing import; `pytest` from backend/ root no longer aborts on collection (was hidden by collection error)
- `services/app.py` — lifespan now wires public router singletons in production (`PYTEST_CURRENT_TEST` gate preserves test isolation); activity + collections public routers share same in-memory instance as internal routers

### Fixed — Security / Auth
- `services/followup/http/public.py` — `POST /api/v1/followups/{id}/escalate` now requires `manager` or `admin` role; `sales_rep` returns 403; `_require_manager()` helper added; `client_manager` test fixture added

### Fixed — Business Logic
- `services/followup/overdue.py` (new) — `scan_overdue_tasks(db)` scans for pending tasks past `due_at` and marks them `overdue`
- `services/app.py` — asyncio background task `_overdue_scanner` runs every 60 s in production; starts in lifespan, cancelled cleanly on shutdown

### Fixed — API Correctness
- `services/followup/http/public.py` — `list_followups` double-query replaced with single `SELECT COUNT(*)` via `func.count()`
- `services/collections/http/public.py` — `POST /api/v1/invoices/{id}/send` endpoint added; returns scheduled WhatsApp reminder dates
- `services/conversation/http/public.py` — `GET /api/v1/conversations/{id}` detail endpoint added; returns conversation + full message thread

### Fixed — Data Correctness
- `services/collections/entities.py` — `tenant_id: str = ""` field added to `Invoice`; stamped from `claims.tenant_id` on creation; `list_invoices` now filters by tenant

### Fixed — Code Quality
- `services/activity/entities.py`, `services/collections/entities.py` — `datetime.utcnow()` replaced with `datetime.now(timezone.utc)`

### Tests
- `tests/followup/test_overdue_scanner.py` (new) — 4 tests for overdue scanner
- `tests/followup/test_public_api.py` — updated escalation tests to use `client_manager`; +1 test (`test_sales_rep_cannot_escalate`)
- `tests/coll/test_collections_public.py` — +3 tests (`TestSendInvoice`) + 2 tests (`TestTenantIsolation`)
- `tests/conversation/test_whatsapp_public.py` — +4 tests (`TestGetConversation`)

### Verified
- 308/308 tests passing (93 original Phase 2+3 + 14 new from audit fixes + 201 legacy src/ tests now visible after P3-A fix)
- 96/96 library pages HTTP 200

---

## [0.23.0] — 2026-05-18 — Phase 3: 5 Engines — Public API Layer

### Added — Sprint 1: WhatsApp Engine
- `backend/services/conversation/http/public.py` — `POST /api/v1/webhooks/whatsapp` (API-key auth) + `GET /api/v1/conversations` (JWT)
- Intent classification via keyword rules (payment_query > follow_up_response > lead_inquiry > support_request)
- Anti-lead-loss guarantee: every inbound message creates/updates a conversation record
- `backend/tests/conversation/test_whatsapp_public.py` — 12 tests

### Added — Sprint 2: Collections Engine
- `backend/services/collections/http/public.py` — `POST/GET /api/v1/invoices` (JWT) + `POST /api/v1/payments/callback/{provider}` (API-key auth)
- JazzCash/Easypaisa payment callback → auto-reconciliation against open invoices
- `backend/tests/coll/test_collections_public.py` — 11 tests

### Added — Sprint 3: Activity Control Engine
- `backend/services/activity/http/public.py` — `POST /api/v1/activities` + `GET /api/v1/activities` + `GET /api/v1/activities/chain-integrity` (JWT)
- Immutable audit hash chain exposed via public endpoint
- `backend/tests/activity/test_activity_public.py` — 10 tests

### Added — Sprint 4: Activation Engine
- `backend/services/activation/http/__init__.py` + `public.py` — `POST /api/v1/activation/start` + `/whatsapp-sim` + `/move-deal` + `GET /api/v1/activation/status` (JWT)
- <10-minute activation path: seed 5 contacts + 4 deals + pipeline; Aha triggered by first inbound + deal move
- `backend/tests/activation/test_activation_public.py` — 10 tests

### Added — Sprint 5: Execution Control Plane (DLQ Operator API)
- `backend/services/core/execution/http/__init__.py` + `public.py` — `GET /api/v1/admin/dead-letters` + `POST /{id}/retry` + `POST /{id}/requeue` (JWT, admin role)
- `backend/tests/execution/test_dlq_public.py` — 10 tests

### Changed
- `backend/services/app.py` — mounted all 5 new public routers

### Verified
- 93/93 tests passing (38 Phase 2 + 55 Phase 3)
- 96/96 library pages HTTP 200

---

## [0.22.0] — 2026-05-18 — Phase 2: Follow-up Engine

### Added
- `backend/services/db/base.py` — SQLAlchemy declarative base
- `backend/services/db/__init__.py` — lazy session factory (no import-time Postgres connection)
- `backend/services/db/models/followup.py` — `FollowupTask` + `FollowupEscalation` ORM models
- `backend/services/db/models/lead.py` — `Lead` ORM model
- `backend/services/db/models/activity.py` — `Activity` ORM model
- `backend/alembic/versions/0001_followup_schema.py` — first real schema migration
- `backend/services/auth/jwt_deps.py` — `get_current_user` FastAPI dependency (JWT Bearer validation)
- `backend/services/followup/http/public.py` — public REST router: 5 endpoints at `/api/v1/followups`
- `backend/tests/followup/test_enforcement.py` — 18 unit tests (timers, escalation ladder, closure gate)
- `backend/tests/followup/test_public_api.py` — 20 integration tests (all endpoints, happy path + error states)
- `pytest`, `httpx`, `python-jose[cryptography]` added to `requirements.txt`

### Changed
- `backend/alembic/env.py` — wired to `Base.metadata` (autogenerate-ready)
- `backend/services/app.py` — public followup router mounted at `/api/v1/followups`

### Verified
- 38/38 tests passing
- 96/96 library pages HTTP 200

---

## [0.21.0] — 2026-05-18 — Phase 1: Foundation Seal

### Added
- `README.md` (root) — GitHub landing page with quick start, architecture diagram, doc index
- `CHANGELOG.md` — this file
- `CONTRIBUTING.md` — branch naming, commit format, PR process
- `Makefile` — make dev, make test, make migrate, make lint
- `.pre-commit-config.yaml` — ruff + black enforced on every commit
- `backend/docs/adr/ADR-001.md` — DDD + microservices architecture decision
- `backend/docs/adr/ADR-002.md` — Adapter pattern for Pakistan isolation
- `backend/docs/adr/ADR-003.md` — WhatsApp-first interaction model
- Alembic migration framework — configured in `backend/alembic/`
- `REBUILD-PLAN.md` — 5-phase 10/10 roadmap
- `PENDING.md` (root) — 155-task rebuild checklist

---

## [0.20.0] — 2026-05-18 — Infrastructure Seal

### Added
- Python 3.12.10 runtime at `D:\Python` — zero C: leakage
- Python venv at `D:\CRM\backend\.venv` — fastapi 0.115.0, uvicorn 0.30.6, pydantic 2.8.2 installed
- `frontend/.npmrc` — npm cache locked to `D:\CRM\.npm-cache`
- `C:\Users\Admin\AppData\Roaming\pip\pip.ini` — pip cache locked to `D:\CRM\.pip-cache`
- `backend/.gitignore` — full Python ignore rules added
- `.gitignore` (root) — cache and runtime dirs locked to D:\CRM

### Changed
- Dev server path confirmed: `npm run serve` from `D:\CRM\frontend` — port 3001

### Fixed
- All 96 library pages verified HTTP 200 after folder restructure

---

## [0.19.0] — 2026-05-17 — Doc Production Readiness

### Changed
- 93 production-readiness gaps fixed across 26 backend docs
- 11 linkage/cross-reference issues resolved across all docs
- Naming normalisation: ALL-CAPS authority files, kebab-case QC/domain docs
- `DOC-CATALOGUE.md` overhauled as ground-truth document index

---

## [0.18.0] — 2026-05-17 — Workspace Restructure

### Changed
- Folder restructure: `V4_extracted/CRM-main` → `backend/`; nexlink triple-wrap → `frontend/`
- All internal paths updated across all docs

---

## [0.17.0] — 2026-05-15 — Library Phase Complete

### Added
- Session 17: AI section pages (investment, new-chat, new-project, plans, search-chat, search-image, your-chat, search-apps, search-apps-details) — self-contained pages with own aside + header, no crm-shell.js

### Changed
- All 96/96 NexLink library pages complete — all browser-approved

---

## [0.10.0–0.16.0] — 2026-05-12 to 2026-05-15 — Library Build Phase

### Added
- 96 NexLink library pages built across 17 batches
- crm-shell.js, crm-api.js (DUMMY_MODE), crm-dummy.js
- All authentication, error, chart, map, icon, component, form pages complete

---

## [0.1.0] — Project Initialisation

### Added
- Pakistan CRM OS project initialised
- DDD microservices backend architecture designed
- 47 domain spec documents written
- 13-archetype UI spec system (b9-p series)
- Pakistan adapter architecture (JazzCash, Easypaisa, WhatsApp)
- Database schemas for all core domains
