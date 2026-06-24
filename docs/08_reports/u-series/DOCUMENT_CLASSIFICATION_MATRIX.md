> **SUPERSEDED** — This document has been superseded by [DOCUMENT_CLASSIFICATION_MATRIX.md](../../08_reports/DOCUMENT_CLASSIFICATION_MATRIX.md) (docs/08_reports/, 2026-06-22 — covers ~195 docs with 9 classes vs 130 docs with 6 classes).
> Content preserved for historical reference. Do not update this document.
> Retired: 2026-06-21 (Documentation Normalization Phase — DUP-009 resolution)

# DOCUMENT_CLASSIFICATION_MATRIX.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U2 — Documentation Catalogue)
**Total project .md files:** 130
**Scope:** Project-owned docs only. Third-party library docs excluded.

---

## Classification Summary

| Class | Count | Description |
|---|---|---|
| Authority | 22 | Documents that govern how work is done |
| Reference | 63 | Factual specs, inventories, and catalogues used for lookup |
| Report | 36 | Audit outputs, discovery outputs, status reports |
| Historical | 5 | Records of past state (version history, QC records, closed plans) |
| Archive | 3 | Superseded content retained as audit record |
| Obsolete | 0 | None identified |
| **Total** | **129** | (SKIP-BACKLOG.md = Report; DOC_CATALOGUE.md itself not self-counted) |

---

## Authority Documents (22)

Documents that govern how work is done. Rules, constraints, protocols, process directives.

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `CLAUDE.md` | Project Lead | Active | Mandatory session enforcement rules: 5-step reading sequence, scope gate, seed audit protocol, 4 build checklist rules |
| `DESIGN-SPEC.md` | Project Lead | Active | Master screen inventory: 75 custom pages, 13 archetypes, build phases, blocked surfaces |
| `FRAMEWORK.md` | Developer | Active | Complete technical build reference §0–§32: HTML template, QC protocol T1–T4, NexLink catalogue, §31 build protocol, §32 normalisation formula |
| `PAGE-BUILD-PROTOCOL.md` | Claude/AI | Active | Mandatory pre-build read: archetype-driven build rule, phase gate, accuracy validation steps |
| `COMMERCIALISATION-PLAN.md` | Project Lead | Active | Active anchor C0–C6 (Environment Seal → Commercial Launch): RESUME POINT, session protocol, non-negotiable rules |
| `U0 — REPOSITORY REALITY DISCOVERY.md` | Project Lead | Active | Process directive: scan entire repo, produce 4 discovery docs |
| `U1 — AUTHORITY RECONSTRUCTION.md` | Project Lead | Active | Process directive: reconstruct project authority, produce 7 inventory docs |
| `U2 — DOCUMENTATION CATALOGUE.md` | Project Lead | Active | Process directive: catalogue every .md file, produce 3 catalogue docs |
| `backend/CONSTRAINTS.md` | Developer | Active | 17 non-negotiable build constraints (C-001 RTL CRITICAL, C-007 DUMMY_MODE, C-009 JAZZCASH_STUB_MODE) |
| `backend/db/transaction_db/transaction-policies.md` | Developer | Active | B7-P01 Transaction Policies: 5 boundary rules, ACID-safe handling, Unit-of-Work policy |
| `backend/docs/infrastructure/api-standards.md` | Developer | Active | API design standards: REST conventions, response envelope, error codes, pagination |
| `backend/docs/infrastructure/concurrency-control.md` | Developer | Active | OCC, row-level locking rules, partners/AI sections |
| `backend/docs/infrastructure/distributed-lock-strategy.md` | Developer | Active | Redis-based locking patterns, deadlock prevention |
| `backend/docs/infrastructure/execution-hardening.md` | Developer | Active | Idempotency, retry/backoff, DLQ, Redis rate-limiting, transactional safety |
| `backend/docs/infrastructure/global-idempotency.md` | Developer | Active | 4-tuple idempotency key, PostgreSQL idempotency_records table, states |
| `backend/docs/infrastructure/workflow-dsl.md` | Developer | Active | Workflow DSL grammar: trigger/condition/action, validation rules, workflow_key uniqueness |
| `backend/docs/security/identity-auth-rbac.md` | Developer | Active | JWT 9-claim TokenClaims, 7 roles, 63 permission scopes, RBAC enforcement |
| `backend/docs/security/org-multi-tenancy.md` | Developer | Active | Tenant isolation: x-tenant-id header, tenant_id FK constraints, enforcement rules |
| `backend/docs/security/security-model.md` | Developer | Active | Deny-by-default, bearer token auth, scope enforcement, audit trail immutability |

---

## Reference Documents (63)

Factual inventories, specs, catalogues, and maps used for lookup. Not directives.

### Root Reference Docs (7)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `README.md` | Developer | Active | Project landing page: architecture, quick start, doc index |
| `PRODUCT-SPEC.md` | Project Lead | Active | System architecture + Pakistan behavioral layer + market intelligence (1022 lines) |
| `CONTRIBUTING.md` | Developer | Active | Branch naming, commit format, PR process, non-negotiables |
| `DOC-CATALOGUE.md` | Claude/AI | Active | Pre-existing master document index (105+ docs, §A–§M). Superseded by DOC_CATALOGUE.md (U2). |
| `MAPPING-TRACKER.md` | Claude/AI | Complete | Frontend ↔ Backend mapping rework tracker. Phase M COMPLETE. |
| `RENDER-DEPLOY.md` | DevOps | Active | Render.com deployment guide: Blueprint deploy, 5 services, migrations, seed |
| `DOC-READ-LOG.md` | Claude/AI | Active | Line-by-line read checklist for all 109 project .md files |

### Backend Reference Docs (4)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `backend/README.md` | Developer | Active | Backend system identity, design principles, 6 engines |
| `backend/FRONTEND-BACKEND-MAPPING.md` | Claude/AI | Active | 42 route files mapped to 75 pages. Reference only — not ground truth. |
| `backend/db/activity_task_db/README.md` | Developer | Active | Activity/task DB schema scope |
| `backend/db/transaction_db/README.md` | Developer | Active | Transaction DB scope (billing, payments, integrity) |
| `backend/gateway/README.md` | Developer | Active | API Gateway: 42 routers, RBAC scopes, middleware chain |

### Page Archetype Specs (15)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `backend/docs/_b9/b9-p01-dashboard-kpi.md` | Developer | Active | Dashboard/KPI archetype spec (A-pages) |
| `backend/docs/_b9/b9-p02-list-queue.md` | Developer | Active | List/Queue archetype spec (B-pages) |
| `backend/docs/_b9/b9-p03-sales-cockpit.md` | Developer | Active | Sales Cockpit archetype spec (D-01) |
| `backend/docs/_b9/b9-p04-support-console.md` | Developer | Active | Support Console archetype spec (E-01) |
| `backend/docs/_b9/b9-p05-marketing-workspace.md` | Developer | Active | Marketing Workspace archetype spec (F-01) |
| `backend/docs/_b9/b9-p06-entity-detail.md` | Developer | Active | Entity Detail archetype spec (C-pages) |
| `backend/docs/_b9/b9-p07-workflow-visual-ui.md` | Developer | Active | Workflow Builder archetype spec (K-01) |
| `backend/docs/_b9/b9-p08-builder-extensions.md` | Developer | Active | Builder/Extensions archetype spec (K-02/K-03/K-04) |
| `backend/docs/_b9/b9-p08-mobile-responsiveness-system.md` | Developer | Active | Mobile responsiveness system spec |
| `backend/docs/_b9/b9-p09-settings-admin.md` | Developer | Active | Settings/Admin archetype spec (G-pages) |
| `backend/docs/_b9/b9-p10-reporting-analytics.md` | Developer | Active | Reporting/Analytics archetype spec (H-pages) |
| `backend/docs/_b9/b9-p11-form-wizard.md` | Developer | Active | Form/Wizard archetype spec (I-pages) |
| `backend/docs/_b9/b9-p12-audit-compliance.md` | Developer | Active | Audit/Compliance archetype spec (J-pages) |
| `backend/docs/_b9/b9-p13-inbox-communication.md` | Developer | Active | Inbox/Communication archetype spec (L-pages) |
| `backend/docs/_b9/b9-p14-ai-copilot.md` | Developer | Active | AI Copilot archetype spec (M-pages) |

### Architecture Reference Docs (5)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `backend/docs/architecture/architecture-overview.md` | Developer | Active | System architecture overview: layers, engines, 40 services |
| `backend/docs/architecture/capability-matrix.md` | Developer | Active | All system capabilities with implementation status |
| `backend/docs/architecture/data-architecture.md` | Developer | Active | CQRS-lite: write model (PostgreSQL), read model (15+) |
| `backend/docs/architecture/domain-model.md` | Developer | Active | 79 canonical domain entities with fields and relationships |
| `backend/docs/architecture/service-map.md` | Developer | Active | Service ownership: which service owns which domain |

### ADR Docs (3)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `backend/docs/adr/ADR-001.md` | Developer | Active | ADR: DDD + Microservices |
| `backend/docs/adr/ADR-002.md` | Developer | Active | ADR: Adapter Pattern for Pakistan |
| `backend/docs/adr/ADR-003.md` | Developer | Active | ADR: WhatsApp-First Interaction Model |

### Domain Spec Docs (21)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `backend/docs/domain/activities-tasks.md` | Developer | Active | Activity and task domain spec |
| `backend/docs/domain/activity-control-model.md` | Developer | Active | Activity Control Engine: immutable hash chain |
| `backend/docs/domain/ai-predictive-models.md` | Developer | Active | AI models (Sprint 5B-7): lead_score_v1, churn_predict_v1, clv_estimate_v1 |
| `backend/docs/domain/cases-domain.md` | Developer | Active | Cases/Support (Sprint 5B-1): Case 33 fields, SLA, state machine |
| `backend/docs/domain/collections-engine-model.md` | Developer | Active | Collections Engine: invoice lifecycle, reconciliation |
| `backend/docs/domain/contract-lifecycle-management.md` | Developer | Active | Contract lifecycle: states, approval, renewal |
| `backend/docs/domain/cpq-quotes-orders.md` | Developer | Active | CPQ: quote builder, price books, discount routing |
| `backend/docs/domain/custom-object-framework.md` | Developer | Active | Custom object builder: field types, layout canvas |
| `backend/docs/domain/data-governance-layer.md` | Developer | Active | Data governance: classification, retention, SAR, consent |
| `backend/docs/domain/data-governance-ownership.md` | Developer | Active | Data governance ownership: access controls, break-glass |
| `backend/docs/domain/employee-performance.md` | Developer | Active | Employee performance: activity metrics, KPIs |
| `backend/docs/domain/enterprise-depth.md` | Developer | Active | Enterprise depth: multi-tenant, multi-territory, multi-currency |
| `backend/docs/domain/followup-enforcement-model.md` | Developer | Active | Follow-up Engine: escalation ladder T+0/+2h/+24h/+48h |
| `backend/docs/domain/marketing-campaigns.md` | Developer | Active | Campaigns (Sprint 5B-4): lifecycle, segments, WhatsApp opt-in |
| `backend/docs/domain/opportunities-pipeline.md` | Developer | Active | Opportunities: pipeline, stage transitions, attributed_partner_id |
| `backend/docs/domain/owner-dashboard.md` | Developer | Active | Owner dashboard: Pakistan-specific KPIs |
| `backend/docs/domain/partner-channel-management.md` | Developer | Active | Partner channel: tiers, deal registration |
| `backend/docs/domain/partners.md` | Developer | Active | Partners (Sprint 5B-5): tier rates, DealRegistration, commission lifecycle |
| `backend/docs/domain/payments-revenue.md` | Developer | Active | Payments: aggregate, status transitions, revenue ledger |
| `backend/docs/domain/shared-inbox.md` | Developer | Active | Shared Inbox (Sprint 5B-2): InboxQueue, AgentPresence, claim guard |
| `backend/docs/domain/territory-management.md` | Developer | Active | Territories (Sprint 5B-3): 9 rule types, conflict resolution |

### Infrastructure Reference Docs (8)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `backend/docs/infrastructure/event-catalog.md` | Developer | Active | All system events: 21 AI/campaign/partner events added 2026-05-29 |
| `backend/docs/infrastructure/feature-flags-config.md` | Developer | Active | Feature flag registry, 2-person approval, Redis cache |
| `backend/docs/infrastructure/integration-contracts.md` | Developer | Active | Provider allowlist, API contract shapes |
| `backend/docs/infrastructure/kpi-data-pipelines.md` | Developer | Active | 8 canonical KPIs, read model shapes, aggregation rules |
| `backend/docs/infrastructure/observability-audit.md` | Developer | Active | Structured logging, tracing, alerting, audit log |
| `backend/docs/infrastructure/offline-sync.md` | Developer | Active | Offline queue, sync-on-reconnect, conflict resolution |
| `backend/docs/infrastructure/runtime-deployment.md` | DevOps | Active | Docker Compose (dev), Render.com (prod), progressive rollout |
| `backend/docs/infrastructure/scheduler-jobs.md` | Developer | Active | Background job definitions, cron schedules |
| `backend/docs/infrastructure/workflow-catalog.md` | Developer | Active | 5 named workflow definitions, DSL triggers |

### Product Reference Docs (4)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `backend/docs/product/activation-model.md` | Developer | Active | Activation Engine: <10-minute time-to-value |
| `backend/docs/product/adoption-ux.md` | Developer | Active | 4-tier progressive disclosure, feature visibility |
| `backend/docs/product/localization.md` | Developer | Active | PKR, EN/UR bilingual, P-017 gate |
| `backend/docs/product/pricing-plans.md` | Developer | Active | PKR pricing tiers, willingness-to-pay |

### UI Reference Docs (3)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `backend/docs/ui/read-models.md` | Developer | Active | 15+ named read model shapes, Widget System, Dashboard zones |
| `backend/docs/ui/ui-foundations.md` | Developer | Active | Design system basics, NexLink integration rules |
| `backend/docs/ui/ui-system.md` | Developer | Active | Component library rules, DataTable alignment, filter chips |

---

## Report Documents (36)

Audit outputs, discovery outputs, and status reports — evidence-based records of what was found or done.

### Active Session Reports (5)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `PROGRESS.md` | Claude/AI | Active | Page-by-page build tracker. C3 COMPLETE 2026-06-01. |
| `PENDING.md` | Claude/AI | Active | Task checklist: 176/176 build tasks done; commercialisation is current. |
| `SESSION-HANDOFF.md` | Claude/AI | Active | Handoff 2026-05-31: 75/75 pages live, next = C3. |
| `SYSTEM-SNAPSHOT.md` | Claude/AI | Active | 60-second system state: 9.97/10, C3 current. |
| `CATALOGUE-MERGE-PLAN.md` | Claude/AI | Complete | Catalogue merge plan: all 7 steps complete 2026-05-22. |

### U0 Discovery Reports (4)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `WORKSPACE_BASELINE_AUDIT.md` | Claude/AI | Active | U0: tech stack, page counts, test counts, CI/CD |
| `REPOSITORY_REALITY_REPORT.md` | Claude/AI | Active | U0: narrative, module/entity/API/integration inventory |
| `REPOSITORY_TREE_INVENTORY.md` | Claude/AI | Active | U0: full directory tree |
| `CURRENT_PROJECT_STATUS.md` | Claude/AI | Active | U0: phase completion, blockers, gaps |

### U1 Authority Reports (7)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `AUTHORITY_RECONSTRUCTION_REPORT.md` | Claude/AI | Active | U1: 28 modules, ~199 APIs, 35+ entities, 7 roles, 5 workflows |
| `FEATURE_INVENTORY.md` | Claude/AI | Active | U1: every user-facing feature with status |
| `MODULE_INVENTORY.md` | Claude/AI | Active | U1: 28 modules with router/entity/status mappings |
| `ENTITY_INVENTORY.md` | Claude/AI | Active | U1: 35+ entities with fields, relationships, CRUD |
| `WORKFLOW_INVENTORY.md` | Claude/AI | Active | U1: 5 workflows with triggers, steps, entities |
| `ROLE_PERMISSION_INVENTORY.md` | Claude/AI | Active | U1: 7 roles, 63 scopes, route restrictions |
| `API_INVENTORY.md` | Claude/AI | Active | U1: ~199 endpoints with method, path, auth, status |

### Backend QC and Gap Reports (8)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `backend/BACKEND-QC.md` | QA/Claude | Active | Consolidated backend QC log (§1–§8) |
| `backend/PENDING.md` | Claude/AI | Active | Blocked items: P-016 credentials, P-017 Urdu |
| `backend/market-research-gap-register.md` | Claude/AI | Active | MR-001 to MR-007: market research gaps (MR-004/005 DONE) |
| `backend/product-spec-gap-register.md` | Claude/AI | Active | Product spec coverage map and gaps |
| `backend/docs/phase4-gap-register.md` | Claude/AI | Complete | Phase 4 code overlay gaps: 26 FIXED, 2 OPEN (A-006/A-007) |
| `backend/db/activity_task_db/self-qc.md` | QA | Complete | Activity/task DB QC: all pass |
| `backend/db/transaction_db/self-qc.md` | QA | Complete | Payments/revenue QC: all pass |
| `backend/gateway/self-qc.md` | QA | Complete | Gateway accounts/contacts QC: all pass |

### QC Read Logs (3)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `backend/docs/_qc/phase4-stage1-read-log.md` | Claude/AI | Complete | Phase 4 Stage 1 read log: 51/51 files read |
| `backend/docs/_qc/qc-integration.md` | QA/Claude | Complete | B5-QC01 Integration QC: all 10 checks pass |
| `backend/docs/_qc/qc-intelligence-data.md` | QA/Claude | Complete | B4-QC01 Intelligence/Data QC |

### Test Reports (1)

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `tests/e2e/playwright/SKIP-BACKLOG.md` | QA | Active | Playwright skip backlog: 3 design gaps, 269 tests, 0 hard failures |

---

## Historical Documents (5)

Records of past state. Still valid for historical reference; not governing current work.

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `CHANGELOG.md` | Claude/AI | Active | Version history v0.1.0 → v0.39.0. All build sessions documented. |
| `SCREEN-ARTEFACTS.md` | QA/Claude | Active | QC records: T1–T4 status + browser sign-offs for all 75 custom pages. |
| `REBUILD-PLAN.md` | Claude/AI | Superseded | 6-phase 10/10 roadmap. CLOSED 2026-05-31. Historical record only. |
| `DOC-READ-LOG.md` | Claude/AI | Active | Cross-session read continuity log. 105 ✓ / 4 W / 0 ⬜ of 109 total. |
| `MAPPING-TRACKER.md` | Claude/AI | Complete | Phase M mapping rework tracker. COMPLETE 2026-05-27. |

---

## Archive Documents (3)

Superseded content retained for audit record. Do not rely on for current guidance.

| Path | Owner | Status | Purpose |
|---|---|---|---|
| `_archive/deployment-pipelines.md` | DevOps | Superseded | B1-P05 CI/CD pipeline spec. Superseded by runtime-deployment.md. |
| `_archive/FRAMEWORK-GAPS.md` | Claude/AI | Superseded | Library phase gap register. Superseded by inline FRAMEWORK.md annotations. |
| `_archive/gap-register.md` | Claude/AI | Superseded | Docs vs code gap register (2026-04-02). Superseded by BACKEND-QC.md and phase4-gap-register.md. |

---

## Obsolete Documents (0)

No documents identified as obsolete — archive folder is already used for superseded content.
