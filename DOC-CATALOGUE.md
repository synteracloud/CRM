# Pakistan CRM — Document Catalogue

**Last updated:** 2026-05-18 (Phase 3 complete: 5 public API engines — WhatsApp, Collections, Activity, Activation, DLQ; 93/93 tests passing)
**Scope:** All .md files in the project — 81 active + 3 archived — each with purpose and description.
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

---

## §A — D:\CRM\ root (8 files)

Build authority files. Claude reads these first every session.

| File | Purpose | Status |
|---|---|---|
| `CLAUDE.md` | Session enforcement rules — seed audit protocol, current build phase, path translation rules. Auto-loaded by Claude. | Active |
| `FRAMEWORK.md` | Complete technical build reference §0–§32 — dev server, script load order, seed normalisation, build methodology, QC protocol, UI component catalogue. | Active |
| `FRAMEWORK-GAPS.md` | Library phase gap register — GAP-001 to GAP-006 resolved; open seed bugs (GAP-008/018/019) already noted inline in FRAMEWORK.md. | **Archived → D:\CRM\_archive\** |
| `DESIGN-SPEC.md` | Master screen inventory — 75 custom pages, 13 archetypes A–M, 8 build phases, design constraints C-001 to C-010. Gates the custom design phase. | Active |
| `PRODUCT-SPEC.md` | Product specification — what the CRM is, Pakistan behavioural layer, market intelligence. Consolidated from 5 source files (all deleted). | Active |
| `SCREEN-ARTEFACTS.md` | QC artefact records for all built custom pages — dashboard, leads, followups, contacts. Each has L0–L9 artefact set + T1–T4 QC record. Browser sign-offs pending. | Active |
| `DOC-CATALOGUE.md` | This file. Index of all .md documents in the project. | Active |
| `PROGRESS.md` | Frontend page progress tracker — 96/96 library pages complete, custom phase queue defined. Rebuild plan reference added. | Active |
| `REBUILD-PLAN.md` | 10/10 rebuild roadmap — 5 phases, ~15 weeks. Phase 1 COMPLETE. Current grades, phase deliverables, non-negotiable rules. | Active |
| `PENDING.md` | Rebuild task checklist — 155 tasks across 5 phases. Phase 1: 14/14 ✓. Updated as each task completes. | Active |
| `README.md` | Root GitHub landing page — architecture diagram, quick start, doc index, key constraints. | Active |
| `CHANGELOG.md` | Version history — sessions 0.1.0 through current. Updated each phase. | Active |
| `CONTRIBUTING.md` | Branch naming, commit format, PR process, non-negotiable rules for all contributors. | Active |

---

## §B — backend/ root (7 files)

Backend project authority files.

| File | Purpose | Status |
|---|---|---|
| `README.md` | System identity — "Execution-First CRM OS", platform overview, module structure. Python env setup: Python 3.12.10 at `D:\Python`, venv at `D:\CRM\backend\.venv`, fastapi/uvicorn/pydantic installed. | Active |
| `BACKEND-QC.md` | Consolidated backend QC log — 11 sections, all 10/10 pass. Consolidated from 11 source files (all deleted). Single authority for backend validation. | Active |
| `CONSTRAINTS.md` | 17 build constraints register — architectural decisions with trade-offs, CRITICAL flags for rework risk. Read before starting any new build layer. | Active |
| `PENDING.md` | Pending work register — P-items. P-016 (JazzCash/Easypaisa credentials) and P-017 (Urdu speaker) blocked. Groups 1–9 otherwise complete. | Active |
| `gap-register.md` | Docs vs code gap register — 20 gaps, all resolved. | **Archived → D:\CRM\_archive\** |
| `market-research-gap-register.md` | Pakistan market research gaps — MR-001 to MR-007 (Facebook leads, voice notes, Kuickpay, offline sync, collections, WhatsApp flows, territory). | Active |
| `FRONTEND-BACKEND-MAPPING.md` | NexLink page → live API endpoint wiring — every page mapped to its endpoint, column → API field, row action → API call, status (DIRECT/EXTEND/BUILD). | Active |

---

## §B2 — Phase 3 Public API layer (10 files)

New service public-facing HTTP modules. All JWT-gated; webhook endpoints use X-Api-Key.

| File | Routes | Tests |
|---|---|---|
| `services/conversation/http/public.py` | `POST /api/v1/webhooks/whatsapp` · `GET /api/v1/conversations` | `tests/conversation/test_whatsapp_public.py` (12) |
| `services/collections/http/public.py` | `POST/GET /api/v1/invoices` · `POST /api/v1/payments/callback/{provider}` | `tests/coll/test_collections_public.py` (11) |
| `services/activity/http/public.py` | `POST/GET /api/v1/activities` · `GET /api/v1/activities/chain-integrity` | `tests/activity/test_activity_public.py` (10) |
| `services/activation/http/public.py` | `POST /api/v1/activation/start` · `/whatsapp-sim` · `/move-deal` · `GET /api/v1/activation/status` | `tests/activation/test_activation_public.py` (10) |
| `services/core/execution/http/public.py` | `GET /api/v1/admin/dead-letters` · `POST /{id}/retry` · `POST /{id}/requeue` | `tests/execution/test_dlq_public.py` (10) |

---

## §C — backend/db/ (5 files)

Database schema documentation.

| File | Purpose | Status |
|---|---|---|
| `activity_task_db/README.md` | Schema overview for activities/tasks database (B2-P04). | Active |
| `activity_task_db/self-qc.md` | QC record — activities/tasks DB validation pass. | QC record |
| `transaction_db/README.md` | Schema overview for transaction database — billing, subscriptions, payments (B1-P05, B2-P08). | Active |
| `transaction_db/self-qc.md` | QC record — payments/revenue DB validation pass. | QC record |
| `transaction_db/transaction-policies.md` | Transaction boundary policies for billing service — write rules, rollback policies, idempotency. | Active |

---

## §D — backend/gateway/ (2 files)

API gateway documentation.

| File | Purpose | Status |
|---|---|---|
| `README.md` | API gateway structure — folder map, entry points, route organisation. | Active |
| `self-qc.md` | Gateway QC record — accounts/contacts standards conformance pass. | QC record |

---

## §E — backend/docs/ — Frontend Page Specs (15 files)

B9-series UI specs. Each spec defines scope, layout, components, and backend wiring for one page archetype. Read the relevant spec before building any custom page.

| File | Page / Archetype | Purpose |
|---|---|---|
| `b9-p01-dashboard-kpi.md` | Dashboard / KPI overview | Owner dashboard spec — KPI cards, charts, enforcement strip. Includes error states (401/403/404/429/503), gap-to-target metric configuration. |
| `b9-p02-list-queue.md` | List / queue / table view | DataTable list pages — leads, contacts, tasks, followups. Includes error states (401/403/404/422/429/503) for all list surfaces. |
| `b9-p03-sales-cockpit.md` | Sales cockpit | Kanban pipeline view — stage columns, drag-to-transition, forecast rail |
| `b9-p04-support-console.md` | Support console | Ticket workspace — ticket list, thread view, resolution flow |
| `b9-p05-marketing-workspace.md` | Marketing workspace | Campaign list, audience segmentation, MR-001 hook point |
| `b9-p06-entity-detail.md` | Entity detail / 360 profile | Lead detail, contact detail — timeline, panels, related entities |
| `b9-p07-workflow-visual-ui.md` | Workflow visual builder | Node-canvas workflow editor |
| `b9-p08-builder-extensions.md` | Builder / visual canvas | Custom object builder + CPQ logic + CPQ approval lane |
| `b9-p08-mobile-responsiveness-system.md` | Mobile responsiveness | Responsive behaviour rules across all pages |
| `b9-p09-settings-admin.md` | Settings / admin / config | RBAC, tenant config, feature flags, locale toggle |
| `b9-p10-reporting-analytics.md` | Reporting / analytics | Charts, KPI pipelines, intelligence dashboards |
| `b9-p11-form-wizard.md` | Form wizard / CPQ configurator | Multi-step forms, quote builder |
| `b9-p12-audit-compliance.md` | Audit / compliance | Immutable audit log, hash-chain integrity badge |
| `b9-p13-inbox-communication.md` | Inbox / communication thread | WhatsApp inbox, email inbox, omnichannel thread |
| `b9-p14-ai-copilot.md` | AI copilot | Advisory-only suggestion panel — never autonomous actions |

---

## §F — backend/docs/ — Domain & Architecture Specs (47 files)

Authoritative backend domain documentation. These define entity fields, states, service boundaries, and system behaviour. Frontend must not drift from these.

### Core architecture

| File | Purpose |
|---|---|
| `architecture-overview.md` | System architecture style — DDD, microservices, event-driven, service boundaries |
| `domain-model.md` | CRM domain model — all entities, naming conventions, relationships. Includes FollowUp entity, Team/TeamMembership entities, Lead state machine, FK cascade rules, soft-delete semantics, TerritoryRule criteria schema. |
| `service-map.md` | All services, ownership, inter-service dependencies. Includes Partner Management Service. |
| `capability-matrix.md` | Feature → owning service → dependencies — the master capability map |
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
| `payments-revenue.md` | Payments/revenue — entities, status flow, PKR ledger (B2-P08). Includes invalid transition error response, plan change cancellation rules, tiered/volume billing model semantics. |
| `collections-engine-model.md` | Collections engine — overdue receivables automation. Includes confidence scoring thresholds (≥85 auto-match, 40–84 review), auto_verify configuration, customer opt-out mechanism (WhatsApp STOP). |
| `owner-dashboard.md` | Owner dashboard — domain model and data requirements |
| `data-governance-ownership.md` | Data governance spec — ownership model + enforcement gates + no-uncontrolled-data guarantee. §2 retention and §3 quality rules → cross-reference data-governance-layer.md. |
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
| `observability-audit.md` | Request logging, immutable audit trails, distributed tracing |
| `kpi-data-pipelines.md` | KPI data pipelines — aggregation, projection, refresh |
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
| `qc-intelligence-data.md` | Intelligence data QC record |
| `qc-integration.md` | Integration QC record |
| `enterprise-depth.md` | Enterprise depth design artifact — NOT a QC file, NOT absorbed into BACKEND-QC.md |

