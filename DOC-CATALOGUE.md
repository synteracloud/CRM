# Pakistan CRM — Document Catalogue

**Last updated:** 2026-05-19 (Full personal line-by-line read of all 90 docs verified; 23 description corrections total — 22 prior + 1 today (capability-matrix: 30→19 capabilities); stale content fixed in README.md, CHANGELOG.md, PROGRESS.md; §H Planned Docs added; phases restructured; 90 active + 9 planned + 3 archived)
**Scope:** All .md files in the project — 90 active + 9 planned (Sprint 0 — not yet written) + 3 archived — each with purpose and description.
**Purpose:** Ground-truth index built from an actual file system scan. Use this to find any document, understand its purpose, and know whether it is active or a QC record. Paths reflect current folder structure.
**Linkage audit:** 2026-05-17 — 11 issues resolved (3 broken refs, 5 stale refs, 3 notation mismatches). All cross-references verified clean.
**Production readiness audit:** 2026-05-17 — 93 gaps identified and fixed across 26 files. 16 critical, 29 high, 48 medium. All docs now at production-grade specification level.

---

## How to use

| I want to... | Go to |
|---|---|
| Start a new build session | §A — read CLAUDE.md, FRAMEWORK.md, DESIGN-SPEC.md |
| Build a custom page | DESIGN-SPEC.md → FRAMEWORK.md §25–26 → relevant b9-p spec in §F |
| Wire a page to the API | §B → FRONTEND-BACKEND-MAPPING.md |
| Check entity fields / states | §F → domain-model.md or the relevant domain spec |
| Understand what's already built | §A → PROGRESS.md + SCREEN-ARTEFACTS.md |
| Check build constraints | §B → CONSTRAINTS.md |
| Check blocked items | §B → PENDING.md |
| Review Pakistan market context | §A → PRODUCT-SPEC.md |
| Review QC records for a built page | §A → SCREEN-ARTEFACTS.md |
| Review backend QC pass | §B → BACKEND-QC.md |
| Check gap registers (code audit, product spec, market research) | §B → product-spec-gap-register.md · market-research-gap-register.md · PENDING.md §Phase 4 |
| Find planned but not-yet-written docs | §H — 9 planned docs, all PLANNED status |

---

## §A — D:\CRM\ root (12 active + 1 archived)

Build authority files. Claude reads these first every session.

| File | Purpose | Status |
|---|---|---|
| `CLAUDE.md` | Session enforcement rules — seed audit protocol, current build phase, path translation rules. Auto-loaded by Claude. | Active |
| `FRAMEWORK.md` | Complete technical build reference §0–§32 — mandatory pre-build 10-step checklist (§0, foundational), HTML template skeleton, UI framework architecture (6 core JS files), 13 dashboard archetype specifications (5 zones), seed-to-page normalisation, script load order protocol, component catalogue, QC tiers T1–T4. | Active |
| `FRAMEWORK-GAPS.md` | Library phase gap register — GAP-001 to GAP-006 resolved; open seed bugs (GAP-008/018/019) already noted inline in FRAMEWORK.md. | **Archived → D:\CRM\_archive\** |
| `DESIGN-SPEC.md` | Master screen inventory — 75 custom pages, 13 archetypes A–M, 8 build phases, design constraints C-001 to C-010. Gates the custom design phase. | Active |
| `PRODUCT-SPEC.md` | Product specification — what the CRM is, Pakistan behavioural layer, market intelligence. Consolidated from 5 source files (all deleted). | Active |
| `SCREEN-ARTEFACTS.md` | QC artefact records for 4 built custom pages (dashboard, leads, followups, contacts). 7-step audit protocol per page: L0 Seed Audit Card, L2 Behaviour Contract, L2.5 Wireframe, L4.5 Data Contract, L9 Assembly Spec, L8 Component Check, T1–T4 QC record (structure/data/visual/behaviour). Includes detailed gap-fix logs with failure counts and resolutions per page. Browser sign-offs pending. | Active |
| `DOC-CATALOGUE.md` | This file. Index of all .md documents in the project. | Active |
| `PROGRESS.md` | Frontend page progress tracker — 96/96 library pages complete, custom phase queue defined. Rebuild plan reference added. | Active |
| `REBUILD-PLAN.md` | 10/10 rebuild roadmap — 6 phases, ~21 weeks. Phases 1–3 COMPLETE ✓. Phase 4 = Backend Hardening + Missing Docs (gates Phase 5). Phase 5 = Frontend 75 pages. Phase 6 = Market Research features. Includes tri-register gap audit state and sequencing rationale. | Active |
| `PENDING.md` | Rebuild task checklist — 229 tasks across 6 phases. 71 done (31%). Phase 4 includes all 44 code audit gaps (C-01→L-06) + 10 Sprint-0 doc tasks (PS-001→PS-010). Updated as each task completes. | Active |
| `README.md` | Root GitHub landing page — architecture diagram, quick start, doc index, key constraints. | Active |
| `CHANGELOG.md` | Version history — sessions 0.1.0 through 0.23.1 (23+ entries). Per-version: feature additions, bug fixes, test counts, library page HTTP 200 verifications. Phases: Infrastructure Seal (0.20), Foundation Seal (0.21), Phase 2 Follow-up Engine (0.22), Phase 3 5-Engines (0.23.0), Pre-Phase-4 Audit (0.23.1). | Active |
| `CONTRIBUTING.md` | Branch naming, commit format, PR process, non-negotiable rules for all contributors. | Active |

---

## §B — backend/ root (7 active + 1 archived)

Backend project authority files.

| File | Purpose | Status |
|---|---|---|
| `README.md` | System identity — "Execution-First CRM OS", platform overview, module structure. Python env setup: Python 3.12.10 at `D:\Python`, venv at `D:\CRM\backend\.venv`, fastapi/uvicorn/pydantic installed. | Active |
| `BACKEND-QC.md` | Consolidated backend QC log — 11 sections all 10/10 or RESOLVED: Foundation, Execution Hardening, Integration E2E, Enterprise Depth, System Hardening, UI Experience, Final Supervisor, Behaviour Gaps (15 items), Consistency Pass (4 items), src/ Gap Register (37 items), Build Progress (Groups 1–9). 308/308 tests passing, 96/96 pages HTTP 200, P-016/P-017 intentionally blocked. Consolidated from 11 source files (all deleted). | Active |
| `CONSTRAINTS.md` | 17 build constraints register — architectural decisions with trade-offs, CRITICAL flags for rework risk. Read before starting any new build layer. | Active |
| `PENDING.md` | Pending work register — P-001 to P-034 organised in 9 groups + 5 build layers. Includes build sequence diagram, cluster dependency map, per-item file locations and dependencies, completion checklist (23 items done, P-016/P-017 blocked pending external resources). Groups 1–9 complete. | Active |
| `gap-register.md` | Docs vs code gap register — 20 gaps, all resolved. | **Archived → D:\CRM\_archive\** |
| `market-research-gap-register.md` | Pakistan market research gaps from Manus AI report (P-034, 2026-04-09) — MR-001 to MR-007: Facebook/Instagram lead capture, one-click WhatsApp invoice+payment, voice note transcription, daily WhatsApp manager summary, Excel import/export, geo-tagging, Kuickpay adapter. MR-004 and MR-005 buildable; rest blocked. Phase 6 scope. | Active |
| `product-spec-gap-register.md` | PRODUCT-SPEC.md overlay against all 81 repo .md files (2026-05-18) — 10 new gaps (PS-001–PS-010) + 7 MR gaps confirmed. 3 Phase-5 build blockers: PS-001 (Cases domain spec), PS-005 (Localization/i18n), PS-008 (Territory management). 4 architecture gaps; 3 feature gaps. All PS items tracked as Sprint-0 tasks in PENDING.md Phase 4. | Active |
| `FRONTEND-BACKEND-MAPPING.md` | NexLink page → live API endpoint wiring — 21 sections covering 15+ built pages and 16 pages to BUILD from scratch. Per-page: endpoint mapping, DataTable column-to-field, row action calls, status (DIRECT/EXTEND/BUILD). Includes custom component specs, RTL implementation pattern, blocked surfaces (P-016/P-017/MR-001–007), and 5-phase frontend build order. | Active |

---

## §B2 — Phase 3 Public API layer + Audit Fixes (11 files)

New service public-facing HTTP modules. All JWT-gated; webhook endpoints use X-Api-Key.
Updated during pre-Phase-4 audit: new endpoints, RBAC gates, tenant isolation, overdue scanner.

| File | Routes | Tests |
|---|---|---|
| `services/conversation/http/public.py` | `POST /api/v1/webhooks/whatsapp` · `GET /api/v1/conversations` · `GET /api/v1/conversations/{id}` | `tests/conversation/test_whatsapp_public.py` (16) |
| `services/collections/http/public.py` | `POST /api/v1/invoices` · `GET /api/v1/invoices` · `GET /api/v1/invoices/{id}` · `POST /api/v1/invoices/{id}/send` · `POST /api/v1/payments/callback/{provider}` | `tests/coll/test_collections_public.py` (16) |
| `services/activity/http/public.py` | `POST/GET /api/v1/activities` · `GET /api/v1/activities/chain-integrity` | `tests/activity/test_activity_public.py` (10) |
| `services/activation/http/public.py` | `POST /api/v1/activation/start` · `/whatsapp-sim` · `/move-deal` · `GET /api/v1/activation/status` | `tests/activation/test_activation_public.py` (10) |
| `services/core/execution/http/public.py` | `GET /api/v1/admin/dead-letters` · `POST /{id}/retry` · `POST /{id}/requeue` | `tests/execution/test_dlq_public.py` (10) |
| `services/followup/overdue.py` | — (background worker utility) | `tests/followup/test_overdue_scanner.py` (4) |

---

## §C — backend/db/ (5 files)

Database schema documentation.

| File | Purpose | Status |
|---|---|---|
| `activity_task_db/README.md` | Schema overview for activities/tasks database (B2-P04). | Active |
| `activity_task_db/self-qc.md` | QC record — activities/tasks DB validation pass. | QC record |
| `transaction_db/README.md` | Schema overview for transaction database — billing, subscriptions, payments (B1-P05, B2-P08, B7-P01). Covers migration setup, transaction handling, and cross-references transaction-policies.md. | Active |
| `transaction_db/self-qc.md` | QC record — two sections: (B2-P08) payments/revenue DB validation (payment aggregate, status history, revenue ledger, 10/10); (B7-P01) transaction integrity validation (UoW functions, policy documentation, 10/10). | QC record |
| `transaction_db/transaction-policies.md` | Transaction boundary policies for billing service — write rules, rollback policies, idempotency. | Active |

---

## §D — backend/gateway/ (2 files)

API gateway documentation.

| File | Purpose | Status |
|---|---|---|
| `README.md` | API gateway structure (B1-P03) — middleware list (request-id, request-validation, response-wrapper, rate-limit-hook), CPQ quote/order APIs, standard response wrapper, forecasting APIs (B2-P06), and audit APIs. | Active |
| `self-qc.md` | Gateway QC record — two sections: (B2-P02) accounts/contacts standards conformance (REST endpoints, payload conventions, tenant isolation, Account-Contact relationship, B2-P07 domain alignment, 10/10); activities/tasks resource patterns and scheduling validation. | QC record |

---

## §E — backend/docs/ — Frontend Page Specs (15 files)

B9-series UI specs. Each spec defines scope, layout, components, and backend wiring for one page archetype. Read the relevant spec before building any custom page.

| File | Page / Archetype | Purpose |
|---|---|---|
| `b9-p01-dashboard-kpi.md` | Dashboard / KPI overview | Owner dashboard spec — KPI cards, charts, enforcement strip. Includes error states (401/403/404/429/503), gap-to-target metric configuration. |
| `b9-p02-list-queue.md` | List / queue / table view | DataTable list pages — leads, contacts, tasks, followups. Includes error states (401/403/404/422/429/503) for all list surfaces. |
| `b9-p03-sales-cockpit.md` | Sales cockpit | Multi-view sales workspace — deal list (execution table), kanban board (stage columns, drag-to-transition), deal detail pane, forecast context rail, next-actions panel. Views A–E with workspace model, stage transitions, and forecast binding. |
| `b9-p04-support-console.md` | Support console | Ticket workspace — ticket list, thread view, resolution flow |
| `b9-p05-marketing-workspace.md` | Marketing workspace | Campaign lifecycle (draft→active→completed), 5 named views (campaign list, segment builder, funnel/attribution, journey status, performance drill-down), read-model bindings and interaction patterns. UI Config Model with nodes, edges, panes. |
| `b9-p06-entity-detail.md` | Entity detail / 360 profile | Lead detail, contact detail — timeline, panels, related entities |
| `b9-p07-workflow-visual-ui.md` | Workflow visual builder | Node-canvas workflow editor |
| `b9-p08-builder-extensions.md` | Builder / visual canvas | Custom object builder + CPQ logic + CPQ approval lane |
| `b9-p08-mobile-responsiveness-system.md` | Mobile responsiveness | Responsive behaviour rules across all pages |
| `b9-p09-settings-admin.md` | Settings / admin / config | RBAC, tenant config, feature flags, locale toggle |
| `b9-p10-reporting-analytics.md` | Reporting / analytics | Charts, KPI pipelines, intelligence dashboards |
| `b9-p11-form-wizard.md` | Form wizard / CPQ configurator | 6 wizard/form surfaces: CPQ Quote Configurator (4 steps), Lead Conversion Wizard (3 steps), Contract Lifecycle Form (3 steps), Subscription Setup Wizard (3 steps), Custom Object Record Form, Tenant Activation Onboarding Wizard (5 steps). ≤2-steps rule enforced; inline validation, back-preserves-state, autosave. |
| `b9-p12-audit-compliance.md` | Audit / compliance | Immutable audit log, hash-chain integrity badge |
| `b9-p13-inbox-communication.md` | Inbox / communication thread | WhatsApp inbox, email inbox, omnichannel thread |
| `b9-p14-ai-copilot.md` | AI copilot | Advisory-only suggestion panel — never autonomous actions |

---

## §F — backend/docs/ — Domain & Architecture Specs (47 files)

Authoritative backend domain documentation. These define entity fields, states, service boundaries, and system behaviour. Frontend must not drift from these.

### Core architecture

| File | Purpose |
|---|---|
| `architecture-overview.md` | System architecture style — layered (L1 Core/L2 Interfaces/L3 Adapters) + engine-driven + adapter-based. DDD with bounded contexts, six platform-owned engines (WhatsApp, Follow-up, Collections, Activity Control, Activation, Execution Control Plane), 39 services in three tiers, CQRS-lite data flow, multi-tenancy model, critical end-to-end flows. |
| `domain-model.md` | CRM domain model — all entities, naming conventions, relationships. Includes FollowUp entity, Team/TeamMembership entities, Lead state machine, FK cascade rules, soft-delete semantics, TerritoryRule criteria schema. |
| `service-map.md` | All services, ownership, inter-service dependencies. Includes Partner Management Service. |
| `capability-matrix.md` | Feature → owning service → dependencies — the master capability map. 19 CRM capabilities mapped with owning + participating services and dependency lists. Note: partner management capabilities are not independently itemised as rows; partner service is referenced in service-map.md. |
| `data-architecture.md` | Data architecture goals, DB-per-service rules, constraints. Includes hot tenant overflow strategy, event schema versioning consumer guidance, cache invalidation on permission changes, implementation phasing criteria. |
| `read-models.md` | Read/query models — denormalised projections for dashboards and APIs. Includes refresh frequencies, stale-data fallbacks, monthly_trend computation, null-vs-zero empty state guidance, TenantEntitlementOverviewRM field addenda. |
| `api-standards.md` | Mandatory API standards — response envelope, error format, pagination, date format |
| `event-catalog.md` | Canonical system events exchanged across all services. Includes 6 partner channel management events (partner.created.v1 → partner.commission.approved.v1). |

### Identity, security, tenancy

| File | Purpose |
|---|---|
| `identity-auth-rbac.md` | Identity, auth, RBAC — JWT structure, roles, token handling. Includes IdP token validation rules, permission cache TTL (60s), conflict resolution (deny-overrides-allow). |
| `org-multi-tenancy.md` | Org / multi-tenancy model — tenant scoping, isolation rules |
| `security-model.md` | Auth model, RBAC permissions, tenant isolation, API security controls. Includes rate limiting thresholds (10k/min per-tenant), break-glass workflow (4hr TTL, dual-approve, auto-revoke), token TTL table (15m access / 7d refresh), session revocation via Redis, cache permission context hash. |

### Pakistan-specific

| File | Purpose |
|---|---|
| `pakistan-adapter-architecture.md` | Pakistan adapter architecture — strict country isolation, JazzCash/Easypaisa/WhatsApp |
| `whatsapp-execution-model.md` | WhatsApp as primary interface — message flow, intent detection, lead capture |
| `adoption-ux.md` | Adoption UX + behavioural design — Pakistan first-session experience, gradual enforcement |
| `activation-model.md` | Activation engine — <10-minute first value delivery design. Includes sandbox-to-production WhatsApp transition spec, optimistic status definitions, sample data localisation. |

### Core domain specs

| File | Purpose |
|---|---|
| `followup-enforcement-model.md` | Follow-up enforcement — every lead must have a next action; no next action = system violation. Includes production timing values (T+0/+2h/+24h/+48h), rule precedence (inactivity > time > activity), reassignment configuration mechanism. |
| `activity-control-model.md` | Control-first activity architecture — ownership, visibility, immutable auditability |
| `activities-tasks.md` | Activities/tasks spec (B2-P04) — entities, states, timeline. Includes FollowUp entity relationship clarification. |
| `opportunities-pipeline.md` | Opportunities pipeline — entities, stage model, transitions (B2-P03). Includes follow-up queue API spec (GET /api/v1/followups). |
| `cpq-quotes-orders.md` | CPQ quotes/orders — entities, line items, accept flow (B2-P05) |
| `payments-revenue.md` | Payments/revenue (B2-P08) — Payment entity (8 status states), PaymentStatusHistory (immutable), RevenueLedger. Includes invalid transition error response (409), plan change cancellation rules. Also covers: Subscription Lifecycle overlay (draft→trialing→active→past_due→paused→canceled/expired), Revenue Recognition overlay (earned+deferred=billed rule), Usage Billing overlay (flat/tiered/volume billing model semantics, MeterRateCard). |
| `collections-engine-model.md` | Collections engine — overdue receivables automation. Includes confidence scoring thresholds (≥85 auto-match, 40–84 review), auto_verify configuration, customer opt-out mechanism (WhatsApp STOP). |
| `owner-dashboard.md` | Owner dashboard — domain model and data requirements |
| `data-governance-ownership.md` | Data governance spec — ownership model (single-writer authority, tenant boundaries, transfer workflows) + enforcement gates + no-uncontrolled-data guarantee. §2 retention and §3 quality rules are minimal cross-references only — substantive specs live in data-governance-layer.md. |
| `contract-lifecycle-management.md` | Contract lifecycle management spec |
| `data-governance-layer.md` | Data governance layer spec. Includes right-to-erasure workflow (GDPR/PDPA, 30-day SLA), legal hold workflow (request→activate→release), DataQualityRuleSet JSON schema, break-glass TTL/approver spec. |
| `partner-channel-management.md` | Partner/channel management spec (B8-P07) |
| `custom-object-framework.md` | Custom object framework — schema extensibility without domain conflicts |

### Infrastructure & reliability

| File | Purpose |
|---|---|
| `execution-hardening.md` | Execution hardening — guarantees for critical flows (B0-P01). Includes retry backoff values (1s base, 2x multiplier, ±20% jitter, 60s max), OCC escalation thresholds (15% retry rate), checkpoint semantics, DLQ operator action API contract. |
| `global-idempotency.md` | Global idempotency model — deduplication across all write operations (B7-P02). Includes response_body_ref storage spec (inline ≤4KB / sha256 reference), financial mutation MUST-retain-7-days enforcement, in-flight duplicate guidance. |
| `concurrency-control.md` | Concurrency control — optimistic locking, conflict resolution (B7-P04). Includes child versioning guidance (strict vs summary), closed-opportunity edit override workflow. |
| `distributed-lock-strategy.md` | Distributed locks — Redis-based mutual exclusion (B7-P05). Includes force_expire auth model, p95 baseline tracking, Redis+DB token reconciliation semantics. |
| `offline-sync.md` | Offline sync layer — queue-first writes, reconnect replay. Includes duplicate CREATE_LEAD conflict handling, partial batch failure client guidance, schema backward compatibility for offline devices. |
| `scheduler-jobs.md` | Background scheduler — delayed, recurring, retryable jobs. Includes catch-up rate limiting (2hr window max), event transactionality via outbox, lease reclaim atomicity pattern. |
| `feature-flags-config.md` | Feature flags service + configuration APIs. Includes flag_rule schema, SHA-256 percentage rollout hash algorithm, expired flag behavior, change approval process (4hr timeout, 2-person). |
| `integration-contracts.md` | All approved integration contracts — external API boundaries. Includes JazzCash/Easypaisa authentication methods, WhatsApp dedup windows (24hr), 360dialog/Gupshup key rotation, GET /api/v1/forecasts spec. |
| `observability-audit.md` | Request logging (structured JSON envelope), immutable audit trails with hash-chain integrity, distributed tracing (W3C Trace Context). Mandatory event categories: authn, authz, admin actions, data mutations, break-glass, integrations, security signals. Critical action coverage matrix with CI enforcement. Redaction policies, severity/retention tiers, audit event schema, audit query/export/verify APIs. |
| `kpi-data-pipelines.md` | KPI data pipelines — 8 KPI metrics with explicit formulas: Lead Conversion Rate, Opportunity Win Rate, Pipeline Value, Quote Acceptance Rate, Booked Revenue, Cash Collected, Invoice Collection Rate, Subscription Churn Rate. 4-layer aggregation pipeline (ingestion/normalisation/state-build/aggregation — Bronze/Silver/Gold), incremental event-driven updates, late-event correction handling. |
| `runtime-deployment.md` | Runtime deployment spec (B0-P04). Includes rollback thresholds (2% error rate, +200ms p95), K8s resource sizing table, 15-min secret rotation overlap window, permitted writable volumes list. |
| `deployment-pipelines.md` | CI/CD pipeline reference — 37-line thin doc, content fully covered by runtime-deployment.md. | **Archived → D:\CRM\_archive\** |
| `workflow-catalog.md` | Canonical business workflows and execution sequences. Includes lead conversion atomicity contract (saga pattern, Account→Contact→Opportunity order, compensation on failure). |
| `workflow-dsl.md` | Workflow DSL — machine-readable workflow definition format |

### UI specs (backend-side)

| File | Purpose |
|---|---|
| `ui-foundations.md` | UI foundations spec — design system, component rules (B9-P01) |
| `ui-system.md` | UI system doc — design token and component system (B0-P03) |

### QC records

| File | Purpose |
|---|---|
| `qc-intelligence-data.md` | QC validation result (not a spec) — B4 intelligence/automation layer: reporting dashboards, workflow engine, rule engine, AI scoring, predictive models, customer 360 CDP, event bus. 10-check validation matrix, all PASS, 10/10. |
| `qc-integration.md` | QC validation result (not a spec) — B5 external APIs/webhooks and communication integrations. 10-check validation matrix, all PASS, 10/10. |
| `enterprise-depth.md` | Enterprise depth design artifact — NOT a QC file, NOT absorbed into BACKEND-QC.md |

---

## §G — backend/docs/adr/ (3 files)

Architectural Decision Records — immutable records of significant architecture choices. Each ADR is permanent; superseded decisions are marked Superseded, not deleted.

| File | Decision | Status |
|---|---|---|
| `ADR-001.md` | DDD + Microservices Architecture — domain-driven design with bounded contexts; microservices over monolith; service-per-domain ownership rules. | Accepted |
| `ADR-002.md` | Adapter Pattern for Pakistan Market Isolation — all country-specific logic in `adapters/pakistan/`; 5 L2 interface contracts (MessagingAdapter, PaymentAdapter, ComplianceAdapter, PhoneFormatter, LocaleAdapter) enforce core/adapter separation. core→pakistan imports blocked by ruff. JazzCash stub mode default (C-009). | Accepted |
| `ADR-003.md` | WhatsApp-First Interaction Model — WhatsApp is the primary execution surface, not an add-on channel; inbound messages trigger system actions; no core workflow requires the UI. | Accepted |

---

## §H — backend/docs/ — Phase 4 Sprint 0: Planned Design Docs (9 files, not yet written)

These docs were identified by the product-spec-gap-register.md (PS-001–PS-010, 2026-05-18). None exist yet. Each must be created in Phase 4 Sprint 0 and added to this catalogue on the same day. Until a doc is created and catalogued, it cannot serve as an audit anchor for code review.

**Rule:** When any doc below is written, update its Status from PLANNED → Active and fill in the Purpose field fully.

| File | Gap ID | Purpose when written | Status | Phase-5 blocker? |
|---|---|---|---|---|
| `backend/docs/cases-domain.md` | PS-001 | Cases/support-tickets domain spec — entity model (`Case`, `CaseComment`, `CaseEscalation`), state machine (open→assigned→in_progress→resolved→closed), SLA tiers (first response time, resolution time), routing rules (skill/queue/round-robin), escalation rules, knowledge base article linking | PLANNED | Yes — gates B-05, C-05, E-01, A-07, I-04, C-12 |
| `backend/docs/shared-inbox.md` | PS-002 | Shared WhatsApp inbox spec — multi-agent assignment model (conversation→assigned_agent_id), unassigned pool queue, conversation handoff (re-assign between agents), agent-scoped vs supervisor inbox view, presence/availability status, concurrent assignment conflict rules | PLANNED | No |
| `backend/docs/compliance-adapter.md` | PS-003 | ComplianceAdapter interface contract — method signatures (`verify_consent()`, `anonymize_entity()`, `check_retention_policy()`, `audit_access()`), Pakistan PDPA implementation, call sites across services, `adapters/pakistan/compliance/` spec | PLANNED | No |
| `backend/docs/conversational-action-spec.md` | PS-004 | Conversational CRM action mapping — command dictionary (intent label → CRM mutation), entity context resolution (which lead/invoice/task is targeted), confirmation flow for destructive actions, error response for ambiguous context | PLANNED | No |
| `backend/docs/localization.md` | PS-005 | Localization / i18n spec — i18n framework choice, EN/UR key registry format, RTL rendering rules (CSS classes, direction toggle), Urdu font strategy, locale-aware date/currency format (PKR, DD/MM/YYYY), WhatsApp template locale variants, locale toggle UI and persistence | PLANNED | Yes — gates all 75 frontend pages (CONSTRAINTS.md C-001) |
| `backend/docs/employee-performance.md` | PS-006 | Employee performance indicators — per-rep KPI definitions (leads captured, follow-up completion rate, avg response time, conversion rate, daily activity count), read-model aggregation from activity events, refresh frequency, RBAC visibility (manager sees all reps; rep sees own only) | PLANNED | No |
| `backend/docs/territory-management.md` | PS-008 | Territory management spec — Territory entity model (territory_id, name, criteria_type, criteria_value, assigned_reps[], active), TerritoryRule criteria schema (full definition), lead/account auto-routing by territory, territory-scoped dashboard views, conflict resolution (lead matches multiple territories), territory performance reporting | PLANNED | Yes — gates G-09 territories.html |
| `backend/docs/pricing-plans.md` | PS-009 | Pricing plan spec — plan tier definitions (Starter/Growth/Business), PKR price per tier (aligned to PRODUCT-SPEC.md §3/§5 benchmarks), feature entitlements per plan, upgrade/downgrade flow (prorate billing), plan-gated feature enforcement in API, trial period model, metering model | PLANNED | No |
| `backend/docs/integration-flow-traces.md` | PS-010 | End-to-end integration flow traces — 4 cross-service flows with step-by-step trace, failure paths, and end-state assertions: (1) WhatsApp→Lead→Follow-up→Close, (2) Lead→Invoice→Payment→Reconciliation, (3) Follow-up→Escalation→Reassignment, (4) Offline Action→Sync→Consistent State | PLANNED | No |

**Note — PS-007:** No new file. Requires extending `backend/docs/collections-engine-model.md` with a new §N — Manual Payment Proof workflow (entity model, states, endpoints, RBAC). The existing §F catalogue entry for `collections-engine-model.md` should be updated when this section is added.

