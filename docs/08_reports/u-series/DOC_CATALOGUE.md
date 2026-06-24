# DOC_CATALOGUE.md — Pakistan CRM OS

> **See also:** [DOCUMENT_INVENTORY.md](../../08_reports/DOCUMENT_INVENTORY.md) (docs/08_reports/, 2026-06-22) for full classification with authority levels across all ~195 project documents. This catalogue has historical detail about when documents were added and why; the 08_reports version adds authority level, information domain, and governance layer columns. Both are useful; neither fully replaces the other.
> Cross-reference added: 2026-06-21 (Documentation Normalization Phase — DUP-008 resolution)

**Generated:** 2026-06-20 (U2 — Documentation Catalogue)
**Scope:** All project-owned .md files. Third-party library docs in `backend/.venv/`, `backend/gateway/node_modules/`, `frontend/node_modules/`, and `bin/pgsql/` are excluded as they are not project documentation.
**Total project .md files catalogued:** 167 (130 at U2 generation + 11 added by U5/U6/U7 + 26 added by U10 remediation 2026-06-21: 6 root U-series prompts + 3 U8 sealing outputs + 5 U9 test planning outputs + 6 U10 forensic audit outputs + 6 U10 remediation outputs) [U5 and U8 execution reports now at docs/reports/u-series/ — paths corrected from root]
**Method:** Every file read before cataloguing.

---

## How to read this catalogue

| Column | Meaning |
|---|---|
| Class | Authority / Reference / Report / Historical / Archive / Obsolete |
| Level | AUTHORITY / REFERENCE / REPORT / HISTORICAL / ARCHIVE / OBSOLETE |
| Status | Active / Complete / Stale / Superseded / Draft |
| Owner | Who maintains this document |

---

## §A — Root (D:\SaaS\CRM\)

### Authority / Governance Files

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `CLAUDE.md` | CLAUDE.md | Authority | AUTHORITY | Active | Project Lead | Mandatory session enforcement rules for Claude: 5-step pre-build reading sequence, scope gate (never touch out-of-phase pages), seed audit protocol, path translation rules, and build checklist (4 recurring bug rules: crm-custom.css, footer ownership, DataTable 3-place alignment, filter chips). Loaded automatically every session. |
| `DESIGN-SPEC.md` | DESIGN-SPEC.md | Authority | AUTHORITY | Active | Project Lead | Master screen inventory: 75 custom pages across 13 archetypes A–M, design constraints, §4 build phase plan, §5 archetype quick reference, §6 file naming, §7 blocked surfaces. Gates the entire custom design phase. |
| `FRAMEWORK.md` | FRAMEWORK.md | Authority | AUTHORITY | Active | Developer | Complete technical build reference §0–§32 (3401 lines): HTML template, script load order, CRM_PAGE registry, 96-page seed table, chart/DataTable configs, design-phase build methodology, QC protocol T1–T4, NexLink component catalogue, §31 Frontend Build Protocol, §32 Seed-to-Archetype Normalisation Protocol. |
| `PAGE-BUILD-PROTOCOL.md` | PAGE-BUILD-PROTOCOL.md | Authority | AUTHORITY | Active | Claude/AI | Mandatory read before every page build: archetype-driven build rule, Phase 0 page selection, accuracy validation. Compiled from FRAMEWORK.md §0/§9/§16/§17/§24/§31, DESIGN-SPEC.md, CLAUDE.md, read-models.md. |
| `COMMERCIALISATION-PLAN.md` | COMMERCIALISATION-PLAN.md | Authority | AUTHORITY | Active | Project Lead | Active anchor from 2026-05-31. C0–C6 phase gates (Environment Seal → Commercial Launch). RESUME POINT table, session open/close protocol, non-negotiable rules for all commercialisation phases. REBUILD-PLAN.md is now closed; this file governs all current work. |
| `U0 — REPOSITORY REALITY DISCOVERY.md` | U0 — REPOSITORY REALITY DISCOVERY.md | Authority | AUTHORITY | Active | Project Lead | Process prompt: scan entire repository, identify all actual implemented components, produce 4 discovery docs. |
| `U1 — AUTHORITY RECONSTRUCTION.md` | U1 — AUTHORITY RECONSTRUCTION.md | Authority | AUTHORITY | Active | Project Lead | Process prompt: reconstruct project authority from repo evidence, produce 7 inventory docs. |
| `U2 — DOCUMENTATION CATALOGUE.md` | U2 — DOCUMENTATION CATALOGUE.md | Authority | AUTHORITY | Active | Project Lead | Process prompt: catalogue every .md file, produce 3 catalogue docs. |

### Reference Files

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `README.md` | README.md | Reference | REFERENCE | Active | Developer | GitHub landing page: what the project is, architecture diagram, quick start, project structure, documentation index, key constraints. |
| `PRODUCT-SPEC.md` | PRODUCT-SPEC.md | Reference | REFERENCE | Active | Project Lead | Consolidated product specification (1022 lines): §1 System Architecture & Execution Model (16 sections), §2 Pakistan Behavioral Layer (15 sections), §3 Market Intelligence (competitor landscape, pricing, gap analysis, SWOT). |
| `CONTRIBUTING.md` | CONTRIBUTING.md | Reference | REFERENCE | Active | Developer | Contribution rules: branch naming, commit format, PR process, non-negotiables, local dev setup, code standards (ruff/black/ESLint). |
| `DOC-CATALOGUE.md` | DOC-CATALOGUE.md | Reference | REFERENCE | Active | Claude/AI | Master document index (105+ active docs catalogued). How-to-use guide, §A–§M sections matching directory structure. Updated each session. Pre-existing catalogue; U2 produces DOC_CATALOGUE.md as the authoritative replacement. |
| `MAPPING-TRACKER.md` | MAPPING-TRACKER.md | Reference | REFERENCE | Complete | Claude/AI | Frontend ↔ Backend mapping rework tracker. All 22 backend route files inventoried. Outputs: FRONTEND-BACKEND-MAPPING.md ✓, PAGE-BUILD-PROTOCOL.md ✓. Phase M COMPLETE 2026-05-27. |
| `RENDER-DEPLOY.md` | RENDER-DEPLOY.md | Reference | REFERENCE | Active | DevOps | Render.com deployment guide (C4): Blueprint deploy, 5 services, Alembic migration steps, seed SQL, GitHub Actions variables. |
| `DOC-READ-LOG.md` | DOC-READ-LOG.md | Reference | REFERENCE | Active | Claude/AI | Durable line-by-line read checklist for all 109 project .md files. 105 ✓ / 4 W / 0 ⬜. Updated each session to prove every catalogue entry was verified against actual file content. |

### Report Files (session tracking and audit)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `PROGRESS.md` | PROGRESS.md | Report | REPORT | Active | Claude/AI | Page-by-page build tracker. Last updated 2026-06-01: C3 Code Hardening COMPLETE. 761/761 pytest, 87% coverage, 63 API contracts, Playwright E2E, Locust p95=28ms, semgrep clean. |
| `PENDING.md` | PENDING.md | Report | REPORT | Active | Claude/AI | Task checklist with completion percentages. 176/176 build tasks done (100%). Commercialisation section is current active work. |
| `SESSION-HANDOFF.md` | SESSION-HANDOFF.md | Report | REPORT | Active | Claude/AI | Session handoff 2026-05-31: 75/75 pages live, 5 inline stub routes, 0 blocked. Resume instructions for next session. |
| `SYSTEM-SNAPSHOT.md` | SYSTEM-SNAPSHOT.md | Report | REPORT | Active | Claude/AI | 60-second bird's-eye view. Date 2026-06-01, grade 9.97/10. Phase completion table C0–C6, scores by area. Read first at every session start. |
| `CATALOGUE-MERGE-PLAN.md` | CATALOGUE-MERGE-PLAN.md | Report | REPORT | Complete | Claude/AI | Step-by-step plan for merging DOC-CATALOGUE-OPS.md + DOC-CATALOGUE-TECH.md into DOC-CATALOGUE.md. All 7 steps COMPLETE 2026-05-22. Sub-catalogues deleted. |

### Historical Files

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `CHANGELOG.md` | CHANGELOG.md | Historical | HISTORICAL | Active | Claude/AI | Version history from v0.1.0 to v0.39.0. Covers all build sessions, features, fixes, test counts, wiring totals. Semantic versioning format. |
| `SCREEN-ARTEFACTS.md` | SCREEN-ARTEFACTS.md | Historical | HISTORICAL | Active | QA/Claude | QC records and browser sign-offs for all 75 custom pages. T1–T4 protocol status per page. Last updated 2026-05-31: all 75 pages T1–T4 ✓ and browser-approved. |
| `REBUILD-PLAN.md` | REBUILD-PLAN.md | Historical | HISTORICAL | Superseded | Claude/AI | 10/10 roadmap — 6 phases. CLOSED 2026-05-31. All phases complete. Historical record only; active work continues in COMMERCIALISATION-PLAN.md. |

### U0/U1 Report Files (discovery and inventory outputs)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `WORKSPACE_BASELINE_AUDIT.md` | WORKSPACE_BASELINE_AUDIT.md | Report | REPORT | Active | Claude/AI | U0 output: tech stack, page counts, CSS/JS assets, config files, docs, scripts, backend, tests, CI/CD, deployment. |
| `REPOSITORY_REALITY_REPORT.md` | REPOSITORY_REALITY_REPORT.md | Report | REPORT | Active | Claude/AI | U0 output: narrative of what the project is, module inventory, entity inventory, API inventory, integration inventory, test coverage, gaps. |
| `REPOSITORY_TREE_INVENTORY.md` | REPOSITORY_TREE_INVENTORY.md | Report | REPORT | Active | Claude/AI | U0 output: full directory tree of entire repository grouped by top-level folder. |
| `CURRENT_PROJECT_STATUS.md` | CURRENT_PROJECT_STATUS.md | Report | REPORT | Active | Claude/AI | U0 output: phase completion, page counts, known blockers, what is done vs what remains. |
| `AUTHORITY_RECONSTRUCTION_REPORT.md` | AUTHORITY_RECONSTRUCTION_REPORT.md | Report | REPORT | Active | Claude/AI | U1 output: full narrative — 28 modules, ~199 API endpoints, 35+ entities, 7 RBAC roles, 5 workflows, integrations, gaps. |
| `FEATURE_INVENTORY.md` | FEATURE_INVENTORY.md | Report | REPORT | Active | Claude/AI | U1 output: every user-facing feature per page with status (Built/Verified/Stub). |
| `MODULE_INVENTORY.md` | MODULE_INVENTORY.md | Report | REPORT | Active | Claude/AI | U1 output + U7 remediation: 29 modules (added Module 29 contract_lifecycle_management). Path fixes for Module 20 and daily summary. Scope count updated 63→91. |
| `ENTITY_INVENTORY.md` | ENTITY_INVENTORY.md | Report | REPORT | Active | Claude/AI | U1 output: 35+ entities with fields, relationships, CRUD coverage, file locations. |
| `WORKFLOW_INVENTORY.md` | WORKFLOW_INVENTORY.md | Report | REPORT | Active | Claude/AI | U1 output: 5 workflows with triggers, steps, entities, status. |
| `ROLE_PERMISSION_INVENTORY.md` | ROLE_PERMISSION_INVENTORY.md | Report | REPORT | Active | Claude/AI | U1 output + U7 remediation: 7 roles, 91 permission scopes (updated from stale 63 count), route restrictions. |
| `API_INVENTORY.md` | API_INVENTORY.md | Report | REPORT | Active | Claude/AI | U1 output + U7 remediation: 228 API endpoints (228 confirmed routes, fully enumerated for Collections/Campaigns/Territories/Partners/Webhooks). |

### U5 Report Files (workspace restructuring — moved to docs/reports/u-series/ by U10 2026-06-21)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `docs/reports/u-series/RESTRUCTURING_EXECUTION_REPORT.md` | RESTRUCTURING_EXECUTION_REPORT.md | Report | REPORT | Complete | Claude/AI | U5 output: execution log for workspace restructuring — 3 folders created, all 42 .md file moves tabulated, 0 errors. |
| `docs/reports/u-series/STALE_LINK_FIX_REPORT.md` | STALE_LINK_FIX_REPORT.md | Report | REPORT | Complete | Claude/AI | U5 output: 30 reference fixes (F-001 through F-030) across SYSTEM-SNAPSHOT.md, COMMERCIALISATION-PLAN.md, README.md, PROGRESS.md, CLAUDE.md, FRAMEWORK.md. |
| `docs/reports/u-series/POST_RESTRUCTURE_VALIDATION.md` | POST_RESTRUCTURE_VALIDATION.md | Report | REPORT | Complete | Claude/AI | U5 output: validation PASS — 9/9 protected files, 42/42 moved files, clean grep scan. 4 human follow-up items noted (H-001 through H-004). |

### U6 Report Files (doc-to-code delta analysis — docs/reports/u-series/)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `docs/reports/u-series/DOC_CODE_DELTA_REPORT.md` | DOC_CODE_DELTA_REPORT.md | Report | REPORT | Complete | Claude/AI | U6 output: full comparison of documentation inventories against actual codebase across routes, RBAC scopes, modules, entities, workflows, frontend pages. |
| `docs/reports/u-series/UNDOCUMENTED_CODE_REGISTER.md` | UNDOCUMENTED_CODE_REGISTER.md | Report | REPORT | Complete | Claude/AI | U6 output: 11 underdocumented or undocumented code items (UC-001 through UC-011): contract_lifecycle_management, WhatsApp webhook paths, payment webhook paths, RBAC scope count, entity DB attributions, and more. |
| `docs/reports/u-series/STALE_DOC_CLAIMS_REGISTER.md` | STALE_DOC_CLAIMS_REGISTER.md | Report | REPORT | Complete | Claude/AI | U6 output: 15 stale documentation claims (SC-001 through SC-015): route counts, scope counts, module paths, API totals. |
| `docs/reports/u-series/DELTA_SUMMARY_REPORT.md` | DELTA_SUMMARY_REPORT.md | Report | REPORT | Complete | Claude/AI | U6 output: executive delta summary, P1/P2/P3 priority action list. |

### U7 Report Files (delta remediation — docs/reports/u-series/)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `docs/reports/u-series/DOC_CODE_REMEDIATION_REPORT.md` | DOC_CODE_REMEDIATION_REPORT.md | Report | REPORT | Complete | Claude/AI | U7 output: itemised log of all documentation fixes applied — which files, which claims, what evidence, what was changed. |
| `docs/reports/u-series/BACKEND_DOC_ALIGNMENT_STATUS.md` | BACKEND_DOC_ALIGNMENT_STATUS.md | Report | REPORT | Complete | Claude/AI | U7 output: per-domain alignment status table — Aligned / Partially-Aligned / Misaligned / Human-Decision-Required. |

---

## §B — _archive/

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `_archive/README.md` | README.md | Reference | REFERENCE | Active | Claude/AI | Redirect notice: "Contents moved to docs/archive/ (2026-06-20 restructuring)". Installed at _archive/ root to explain the empty directory post-migration. |
| `_archive/deployment-pipelines.md` | deployment-pipelines.md | Archive | ARCHIVE | Superseded | DevOps | B1-P05 CI/CD deployment pipeline spec (3 pipelines: runtime packaging, infra tooling, environment deployment flow). Superseded by `backend/docs/infrastructure/runtime-deployment.md`. |
| `_archive/FRAMEWORK-GAPS.md` | FRAMEWORK-GAPS.md | Archive | ARCHIVE | Superseded | Claude/AI | Library phase gap register GAP-001 to GAP-006. Superseded by inline annotations in FRAMEWORK.md. |
| `_archive/gap-register.md` | gap-register.md | Archive | ARCHIVE | Superseded | Claude/AI | Docs vs code gap register generated 2026-04-02. Superseded by `backend/docs/phase4-gap-register.md` and BACKEND-QC.md. |

---

## §C — backend/ root

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/README.md` | README.md | Reference | REFERENCE | Active | Developer | Backend system identity: system name, market positioning, design principles, architecture layers, 6 core engines (Follow-up, Collections, WhatsApp, Activity Control, Activation, Execution Control). Module map. |
| `backend/BACKEND-QC.md` | BACKEND-QC.md | Report | REPORT | Active | QA/Claude | Consolidated backend QC log from 11 source files. §1–§8 covering Foundation QC, security/auth, tenant isolation, production hardening, integration, intelligence/data. |
| `backend/CONSTRAINTS.md` | CONSTRAINTS.md | Authority | AUTHORITY | Active | Developer | 17 build constraints. C-001 RTL CRITICAL; C-002 feature visibility; C-007 DUMMY_MODE via crm-api.js; C-009 JAZZCASH_STUB_MODE=true. Updated 2026-04-09. |
| `backend/FRONTEND-BACKEND-MAPPING.md` | FRONTEND-BACKEND-MAPPING.md | Reference | REFERENCE | Active | Claude/AI | Frontend ↔ Backend mapping (42 route files, 75 pages). Section 1: domain inventory; Sections 2–7: page-by-page mapping. Note: treat as reference only, not ground truth. |
| `backend/PENDING.md` | PENDING.md | Report | REPORT | Active | Claude/AI | Blocked items register (Groups 1–9). P-016: JazzCash/Easypaisa credentials BLOCKED. P-017: Urdu native speaker review BLOCKED. Updated 2026-04-09. |
| `backend/market-research-gap-register.md` | market-research-gap-register.md | Report | REPORT | Active | Claude/AI | Market research gaps (MR-001 to MR-007): Facebook/Instagram lead capture, WhatsApp invoice, voice transcription, daily summary (DONE MR-004), Excel import/export (DONE MR-005), geo-tagging, Kuickpay. |
| `backend/product-spec-gap-register.md` | product-spec-gap-register.md | Report | REPORT | Active | Claude/AI | PRODUCT-SPEC.md overlay against all 81 active docs. Coverage map (well-covered areas) and gap table (items needing docs). Dated 2026-05-18. |
| `backend/docs/phase4-gap-register.md` | phase4-gap-register.md | Report | REPORT | Complete | Claude/AI | Phase 4 Stage 3 code overlay gap register. Groups A–E (persistence, security, domain APIs, API standards, observability/CI). 28 gaps fixed, 2 OPEN (A-006 Redis rate-limit, A-007 FeatureFlag Redis). |

---

## §D — backend/db/

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/db/activity_task_db/README.md` | README.md | Reference | REFERENCE | Active | Developer | Activity/task DB schema scope (B2-P04): activity timeline, tasks, task_schedule. |
| `backend/db/activity_task_db/self-qc.md` | self-qc.md | Report | REPORT | Complete | QA | Activity/task DB QC: task-entity link validation, no orphan activities, scheduling constraint checks. All pass. |
| `backend/db/transaction_db/README.md` | README.md | Reference | REFERENCE | Active | Developer | Transaction DB scope: billing/subscription (B1-P05), payments/revenue (B2-P08), transaction integrity (B7-P01). 3-migration setup. |
| `backend/db/transaction_db/self-qc.md` | self-qc.md | Report | REPORT | Complete | QA | Payments/revenue QC: payment aggregate, status history, revenue ledger, API endpoints listed. |
| `backend/db/transaction_db/transaction-policies.md` | transaction-policies.md | Authority | AUTHORITY | Active | Developer | B7-P01 Transaction Policies: 5 boundary rules, ACID-safe handling, Unit-of-Work policy. Governs all writes to transaction_db. |

---

## §E — backend/gateway/

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/gateway/README.md` | README.md | Reference | REFERENCE | Active | Developer | API Gateway structure: 42 routers mounted under /api/v1, full router directory listing, RBAC scope definitions, middleware chain. |
| `backend/gateway/self-qc.md` | self-qc.md | Report | REPORT | Complete | QA | Gateway QC (B2-P02 Accounts/Contacts): standards conformance, tenant isolation, relationship API, service layer centralization. All pass. |

---

## §F — backend/docs/_b9/ (Page Archetype Specs)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/docs/_b9/b9-p01-dashboard-kpi.md` | b9-p01-dashboard-kpi.md | Reference | REFERENCE | Active | Developer | Dashboard/KPI archetype spec: 5-zone layout, 13 named panels, read model shapes, API routes. Updated 2026-05-31 (A-03/A-11/A-13/A-08 routes added). |
| `backend/docs/_b9/b9-p02-list-queue.md` | b9-p02-list-queue.md | Reference | REFERENCE | Active | Developer | List/Queue archetype spec: Lead/FollowupTask/Invoice stage enums corrected, field contracts, DataTable requirements. Updated 2026-05-28. |
| `backend/docs/_b9/b9-p03-sales-cockpit.md` | b9-p03-sales-cockpit.md | Reference | REFERENCE | Active | Developer | Sales Cockpit archetype spec (D-01): 3-pane layout (pipeline rail, kanban, deal pane), forecast strip, next-actions. |
| `backend/docs/_b9/b9-p04-support-console.md` | b9-p04-support-console.md | Reference | REFERENCE | Active | Developer | Support Console archetype spec (E-01): 3-pane layout, SLA timer header, CaseStatus state machine, click-to-select thread. |
| `backend/docs/_b9/b9-p05-marketing-workspace.md` | b9-p05-marketing-workspace.md | Reference | REFERENCE | Active | Developer | Marketing Workspace archetype spec (F-01): campaign DataTable, status chips, CommunicationEngagementRM. Updated 2026-05-29. |
| `backend/docs/_b9/b9-p06-entity-detail.md` | b9-p06-entity-detail.md | Reference | REFERENCE | Active | Developer | Entity Detail archetype spec: all C-page contracts, state-gated buttons, tab panes. Updated 2026-05-31 (C-08 Invoice Detail added). |
| `backend/docs/_b9/b9-p07-workflow-visual-ui.md` | b9-p07-workflow-visual-ui.md | Reference | REFERENCE | Active | Developer | Workflow Builder archetype spec (K-01): 3-pane layout (palette/canvas/inspector), DSL, validate/simulate/save/publish. |
| `backend/docs/_b9/b9-p08-builder-extensions.md` | b9-p08-builder-extensions.md | Reference | REFERENCE | Active | Developer | Builder/Extensions archetype spec (K-02/K-03/K-04): object builder, rule builder, approval lanes kanban. |
| `backend/docs/_b9/b9-p08-mobile-responsiveness-system.md` | b9-p08-mobile-responsiveness-system.md | Reference | REFERENCE | Active | Developer | Mobile responsiveness system spec: breakpoints, offline queue, lightweight interaction requirements. |
| `backend/docs/_b9/b9-p09-settings-admin.md` | b9-p09-settings-admin.md | Reference | REFERENCE | Active | Developer | Settings/Admin archetype spec: G-01 through G-09 + J-05 contracts, API routes, role/flag/compliance UI rules. Updated 2026-05-31. |
| `backend/docs/_b9/b9-p10-reporting-analytics.md` | b9-p10-reporting-analytics.md | Reference | REFERENCE | Active | Developer | Reporting/Analytics archetype spec: H-01 through H-07, KPI data pipeline anchors, report builder wizard. Updated 2026-05-31. |
| `backend/docs/_b9/b9-p11-form-wizard.md` | b9-p11-form-wizard.md | Reference | REFERENCE | Active | Developer | Form/Wizard archetype spec: I-01 through I-06 (simple forms) + I-07 through I-12 (enterprise wizards). Updated 2026-05-28. |
| `backend/docs/_b9/b9-p12-audit-compliance.md` | b9-p12-audit-compliance.md | Reference | REFERENCE | Active | Developer | Audit/Compliance archetype spec: J-01 through J-05, API routes, consent/DSR/RBAC contracts. Updated 2026-05-31. |
| `backend/docs/_b9/b9-p13-inbox-communication.md` | b9-p13-inbox-communication.md | Reference | REFERENCE | Active | Developer | Inbox/Communication archetype spec: L-01 through L-03, InboxQueue/AgentPresence/ConversationHandoff entities, routing config. Updated 2026-05-31. |
| `backend/docs/_b9/b9-p14-ai-copilot.md` | b9-p14-ai-copilot.md | Reference | REFERENCE | Active | Developer | AI Copilot archetype spec (M-01/M-02): advisory-only architecture, PredictiveInsightRM, copilot query API. Updated 2026-05-29. |

---

## §G — backend/docs/_qc/

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/docs/_qc/phase4-stage1-read-log.md` | phase4-stage1-read-log.md | Report | REPORT | Complete | Claude/AI | Phase 4 Stage 1 doc normalisation read log. 51/51 files read. Stage 1 COMPLETE 2026-05-23. |
| `backend/docs/_qc/qc-integration.md` | qc-integration.md | Report | REPORT | Complete | QA/Claude | B5-QC01 Integration QC: 10-check validation matrix. Inputs: external_apis_webhooks, communication_integrations. All checks pass. |
| `backend/docs/_qc/qc-intelligence-data.md` | qc-intelligence-data.md | Report | REPORT | Complete | QA/Claude | B4-QC01 Intelligence/Data QC: covers reporting_dashboards, workflow_engine, rule_engine, ai_scoring, predictive_models, customer_360_cdp, event_bus. |

---

## §H — backend/docs/adapters/

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/docs/adapters/compliance-adapter.md` | compliance-adapter.md | Reference | REFERENCE | Active | Developer | Pakistan compliance adapter: PTA, FBR requirements, compliance interface contract. |
| `backend/docs/adapters/conversational-action-spec.md` | conversational-action-spec.md | Reference | REFERENCE | Active | Developer | Conversational action spec: intent classification, action execution via WhatsApp conversation context. |
| `backend/docs/adapters/integration-flow-traces.md` | integration-flow-traces.md | Reference | REFERENCE | Active | Developer | Integration flow traces: end-to-end flow diagrams for WhatsApp→Lead, Lead→Invoice→Payment, Follow-up→Escalation, Offline→Sync. |
| `backend/docs/adapters/pakistan-adapter-architecture.md` | pakistan-adapter-architecture.md | Reference | REFERENCE | Active | Developer | Pakistan adapter L1/L2/L3 model: JazzCash, Easypaisa, 360dialog, Gupshup. Adapter isolation rules. |
| `backend/docs/adapters/whatsapp-execution-model.md` | whatsapp-execution-model.md | Reference | REFERENCE | Active | Developer | WhatsApp execution model: inbound message handling, intent classification (4 classes), conversation threading, contact mapping, anti-lead-loss guarantee. |

---

## §I — backend/docs/adr/

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/docs/adr/ADR-001.md` | ADR-001.md | Reference | REFERENCE | Active | Developer | ADR: DDD + Microservices Architecture. Context, decision (L1/L2/L3 layers), consequences. Status: Accepted 2026-05-18. |
| `backend/docs/adr/ADR-002.md` | ADR-002.md | Reference | REFERENCE | Active | Developer | ADR: Adapter Pattern for Pakistan Market Isolation. JazzCash, Easypaisa, 360dialog, Gupshup isolated behind interfaces. Status: Accepted 2026-05-18. |
| `backend/docs/adr/ADR-003.md` | ADR-003.md | Reference | REFERENCE | Active | Developer | ADR: WhatsApp-First Interaction Model. WhatsApp is the primary operating surface, not an integration. Status: Accepted 2026-05-18. |

---

## §J — backend/docs/architecture/

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/docs/architecture/architecture-overview.md` | architecture-overview.md | Reference | REFERENCE | Active | Developer | System architecture overview: layered+engine-driven+adapter-based pattern, L1/L2/L3 layer model, 6 platform engines, 40 domain services, non-functional requirements. Updated 2026-05-30 (service count 39→40). |
| `backend/docs/architecture/capability-matrix.md` | capability-matrix.md | Reference | REFERENCE | Active | Developer | Capability matrix: all system capabilities with implementation status. AI scoring/copilot row added 2026-05-30. |
| `backend/docs/architecture/data-architecture.md` | data-architecture.md | Reference | REFERENCE | Active | Developer | CQRS-lite data architecture: write model (PostgreSQL), read model (15+ named read models), event sourcing patterns. |
| `backend/docs/architecture/domain-model.md` | domain-model.md | Reference | REFERENCE | Active | Developer | 79 canonical domain entities (added 12 Phase 5B entities 2026-05-30): all fields, relationships, state machines. PRIMARY for entity definitions. |
| `backend/docs/architecture/service-map.md` | service-map.md | Reference | REFERENCE | Active | Developer | Service ownership map: which service owns which domain. AI & Predictive Models Service row added 2026-05-30. |

---

## §K — backend/docs/domain/ (21 files)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/docs/domain/activities-tasks.md` | activities-tasks.md | Reference | REFERENCE | Active | Developer | Activity and task domain spec: entity schemas, lifecycle, linkage rules. |
| `backend/docs/domain/activity-control-model.md` | activity-control-model.md | Reference | REFERENCE | Active | Developer | Activity Control Engine spec: immutable audit hash chain, ownership tracking, append-only log. |
| `backend/docs/domain/ai-predictive-models.md` | ai-predictive-models.md | Reference | REFERENCE | Active | Developer | AI/Predictive Models domain spec (Sprint 5B-7): advisory-only architecture, 3 rule-based v1 models (lead_score_v1, churn_predict_v1, clv_estimate_v1), CopilotSuggestion, 5-class intent classifier. Written 2026-05-29. |
| `backend/docs/domain/cases-domain.md` | cases-domain.md | Reference | REFERENCE | Active | Developer | Cases/Support Tickets domain spec (Sprint 5B-1): Case 33-field entity, SLA timers, state machine, CaseComment/CaseEscalation/SupportQueue/SLAPolicy/KnowledgeArticle. |
| `backend/docs/domain/collections-engine-model.md` | collections-engine-model.md | Reference | REFERENCE | Active | Developer | Collections Engine spec: invoice lifecycle, payment tracking, reconciliation, reminder automation, JazzCash/Easypaisa callback handling. |
| `backend/docs/domain/contract-lifecycle-management.md` | contract-lifecycle-management.md | Reference | REFERENCE | Active | Developer | Contract lifecycle management domain spec: contract states, approval gates, renewal tracking. |
| `backend/docs/domain/cpq-quotes-orders.md` | cpq-quotes-orders.md | Reference | REFERENCE | Active | Developer | CPQ (Configure-Price-Quote) domain spec: quote builder, price books, discount approval routing (>10%), order lifecycle. |
| `backend/docs/domain/custom-object-framework.md` | custom-object-framework.md | Reference | REFERENCE | Active | Developer | Custom object framework spec: object builder, field types, layout canvas, relationship engine. |
| `backend/docs/domain/data-governance-layer.md` | data-governance-layer.md | Reference | REFERENCE | Active | Developer | Data governance domain spec: classification map, retention schedule, SAR (Subject Access Request) handling, consent management. |
| `backend/docs/domain/data-governance-ownership.md` | data-governance-ownership.md | Reference | REFERENCE | Active | Developer | Data governance ownership model: who owns what data, access controls, break-glass log. |
| `backend/docs/domain/employee-performance.md` | employee-performance.md | Reference | REFERENCE | Active | Developer | Employee performance domain spec: activity metrics, KPI tracking, performance dashboards. |
| `backend/docs/domain/enterprise-depth.md` | enterprise-depth.md | Reference | REFERENCE | Active | Developer | Enterprise depth spec: multi-tenant, multi-territory, multi-currency, partner channel management depth requirements. |
| `backend/docs/domain/followup-enforcement-model.md` | followup-enforcement-model.md | Reference | REFERENCE | Active | Developer | Follow-up Engine spec: T+0/+2h/+24h/+48h escalation ladder, enforcement rules (inactivity/time/activity precedence), state machine (none/reminder/warning/escalated/reassigned). |
| `backend/docs/domain/marketing-campaigns.md` | marketing-campaigns.md | Reference | REFERENCE | Active | Developer | Marketing/Campaigns domain spec (Sprint 5B-4): campaign lifecycle, CampaignSegment rule engine, MessageTemplate, dispatch pipeline (80 msg/min rate limit), P-017 Urdu gate, 30-day attribution window. Written 2026-05-29. |
| `backend/docs/domain/opportunities-pipeline.md` | opportunities-pipeline.md | Reference | REFERENCE | Active | Developer | Opportunities/Pipeline domain spec: opportunity lifecycle, stage transitions, pipeline value calculations, `attributed_partner_id` added 2026-05-29. |
| `backend/docs/domain/owner-dashboard.md` | owner-dashboard.md | Reference | REFERENCE | Active | Developer | Owner dashboard domain spec: Pakistan-specific owner view, business health KPIs, lead/revenue/collections visibility. |
| `backend/docs/domain/partner-channel-management.md` | partner-channel-management.md | Reference | REFERENCE | Active | Developer | Partner channel management domain spec: partner tiers, deal registration, channel rules. |
| `backend/docs/domain/partners.md` | partners.md | Reference | REFERENCE | Active | Developer | Partners domain spec (Sprint 5B-5): tier system (Platinum 15%/Gold 10%/Silver 5%), DealRegistration protection windows, PartnerCommission lifecycle (paid=immutable). Written 2026-05-29. |
| `backend/docs/domain/payments-revenue.md` | payments-revenue.md | Reference | REFERENCE | Active | Developer | Payments/Revenue domain spec: payment aggregate, status transitions, revenue ledger, JazzCash/Easypaisa integration, Subscription.status enum. |
| `backend/docs/domain/shared-inbox.md` | shared-inbox.md | Reference | REFERENCE | Active | Developer | Shared Inbox domain spec (Sprint 5B-2): InboxQueue, AgentPresence, ConversationHandoff, auto-assign (round_robin/least_loaded), claim race-condition guard. |
| `backend/docs/domain/territory-management.md` | territory-management.md | Reference | REFERENCE | Active | Developer | Territory Management domain spec (Sprint 5B-3): Territory, TerritoryRule (9 rule types), TerritoryAssignment, dry-run evaluate, conflict resolution (priority→rule_count→uuid). |

---

## §L — backend/docs/infrastructure/ (13 files)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/docs/infrastructure/api-standards.md` | api-standards.md | Authority | AUTHORITY | Active | Developer | API design standards: REST conventions, response envelope `{data, meta}`, error codes, pagination, versioning. Read before writing any endpoint. |
| `backend/docs/infrastructure/concurrency-control.md` | concurrency-control.md | Authority | AUTHORITY | Active | Developer | Concurrency control spec: OCC (Optimistic Concurrency Control), row-level locking rules. Sections E (Partners) and F (AI) added 2026-05-30. |
| `backend/docs/infrastructure/distributed-lock-strategy.md` | distributed-lock-strategy.md | Authority | AUTHORITY | Active | Developer | Distributed lock strategy: Redis-based locking, lock acquisition/release patterns, deadlock prevention. |
| `backend/docs/infrastructure/event-catalog.md` | event-catalog.md | Reference | REFERENCE | Active | Developer | All system events and payloads: 21 campaign/partner/AI events added 2026-05-29. Event names, versions, schemas. |
| `backend/docs/infrastructure/execution-hardening.md` | execution-hardening.md | Authority | AUTHORITY | Active | Developer | Execution hardening spec: idempotency, retry with backoff, DLQ, rate limiting (Redis-backed), transactional safety. |
| `backend/docs/infrastructure/feature-flags-config.md` | feature-flags-config.md | Reference | REFERENCE | Active | Developer | Feature flag system: flag registry, 2-person approval rule, Redis cache (A-007 OPEN), evaluation rules. |
| `backend/docs/infrastructure/global-idempotency.md` | global-idempotency.md | Authority | AUTHORITY | Active | Developer | Global idempotency spec: 4-tuple idempotency key, `idempotency_records` PostgreSQL table, in-flight/complete/conflict states. |
| `backend/docs/infrastructure/integration-contracts.md` | integration-contracts.md | Reference | REFERENCE | Active | Developer | Integration contracts: provider allowlist, API contract shapes for WhatsApp/email/SMS/payment providers. |
| `backend/docs/infrastructure/kpi-data-pipelines.md` | kpi-data-pipelines.md | Reference | REFERENCE | Active | Developer | KPI data pipeline spec: 8 canonical KPIs, named read model shapes, aggregation rules. |
| `backend/docs/infrastructure/observability-audit.md` | observability-audit.md | Reference | REFERENCE | Active | Developer | Observability spec: structured logging, tracing, alerting rules, audit log requirements. |
| `backend/docs/infrastructure/offline-sync.md` | offline-sync.md | Reference | REFERENCE | Active | Developer | Offline sync spec: local queue, sync-on-reconnect, conflict resolution strategy. |
| `backend/docs/infrastructure/runtime-deployment.md` | runtime-deployment.md | Reference | REFERENCE | Active | DevOps | Runtime deployment model: Docker Compose (dev), Render.com (prod), 5 services, progressive rollout. Supersedes `_archive/deployment-pipelines.md`. |
| `backend/docs/infrastructure/scheduler-jobs.md` | scheduler-jobs.md | Reference | REFERENCE | Active | Developer | Scheduler jobs spec: background job definitions, cron schedules, retry rules. |
| `backend/docs/infrastructure/workflow-catalog.md` | workflow-catalog.md | Reference | REFERENCE | Active | Developer | Workflow catalog: 5 named workflow definitions, DSL triggers, action types. |
| `backend/docs/infrastructure/workflow-dsl.md` | workflow-dsl.md | Authority | AUTHORITY | Active | Developer | Workflow DSL spec: trigger/condition/action grammar, validation rules, workflow_key uniqueness constraint. |

---

## §M — backend/docs/product/

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/docs/product/activation-model.md` | activation-model.md | Reference | REFERENCE | Active | Developer | Activation Engine spec: zero-setup onboarding, <10-minute time-to-value, seed 5 contacts+4 deals+pipeline, Aha moment trigger. |
| `backend/docs/product/adoption-ux.md` | adoption-ux.md | Reference | REFERENCE | Active | Developer | Adoption UX spec: 4-tier progressive disclosure model, feature visibility state machine, low-discipline environment handling. |
| `backend/docs/product/localization.md` | localization.md | Reference | REFERENCE | Active | Developer | Localization spec: PKR currency, EN/UR bilingual, local date formats, culturally appropriate tone, Urdu P-017 gate. |
| `backend/docs/product/pricing-plans.md` | pricing-plans.md | Reference | REFERENCE | Active | Developer | Pricing plans spec: PKR entry/mid/enterprise tier pricing, psychological thresholds, value demonstration requirements. |

---

## §N — backend/docs/security/

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/docs/security/identity-auth-rbac.md` | identity-auth-rbac.md | Authority | AUTHORITY | Active | Developer | Identity, Auth, and RBAC spec: JWT 9-claim TokenClaims, role_ids, scopes, aud/iss verification, 7 roles, 63 permission scopes. |
| `backend/docs/security/org-multi-tenancy.md` | org-multi-tenancy.md | Authority | AUTHORITY | Active | Developer | Organisation multi-tenancy spec: tenant isolation enforcement, `x-tenant-id` header, tenant_id FK constraints everywhere. |
| `backend/docs/security/security-model.md` | security-model.md | Authority | AUTHORITY | Active | Developer | Overall security model: deny-by-default, bearer token auth, scope enforcement, audit trail immutability, break-glass access. |

---

## §O — backend/docs/ui/

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `backend/docs/ui/read-models.md` | read-models.md | Reference | REFERENCE | Active | Developer | Read model catalogue: 15+ named read model shapes (OwnerDashboardRM, LeadFunnelKpiRM, PartnerPerformanceRM, PredictiveInsightRM, etc.), Widget System, Dashboard zones. |
| `backend/docs/ui/ui-foundations.md` | ui-foundations.md | Reference | REFERENCE | Active | Developer | UI foundations spec: design system basics, NexLink integration rules, component hierarchy. |
| `backend/docs/ui/ui-system.md` | ui-system.md | Reference | REFERENCE | Active | Developer | UI system spec: component library rules, NexLink card patterns, DataTable alignment protocol, filter chip conventions. |

---

## §P — tests/

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `tests/e2e/playwright/SKIP-BACKLOG.md` | SKIP-BACKLOG.md | Report | REPORT | Active | QA | Playwright E2E test skip backlog generated 2026-06-03. 3 design gaps (missing UI elements): followups level filter, quotes-dashboard filter chips, territories filter chips. 269 tests total, 0 hard failures. |

---

## §Q — Root U-Series Prompt Files (U6–U10, added by U10 remediation 2026-06-21)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `U6 — DOC TO CODE DELTA ANALYSIS.md` | U6 — DOC TO CODE DELTA ANALYSIS.md | Authority | AUTHORITY | Active | Project Lead | Process prompt: compare documentation inventories against live codebase, produce 4 delta analysis docs. |
| `U7 — DELTA REMEDIATION.md` | U7 — DELTA REMEDIATION.md | Authority | AUTHORITY | Active | Project Lead | Process prompt: apply all P1 and P2 delta remediations, produce 2 remediation docs. |
| `U8 — WORKSPACE SEALING.md` | U8 — WORKSPACE SEALING.md | Authority | AUTHORITY | Active | Project Lead | Process prompt: audit workspace for C: drive leakage, seal all tooling to D:, produce 3 sealing validation docs. |
| `U9 — TEST SUITE PLANNING.md` | U9 — TEST SUITE PLANNING.md | Authority | AUTHORITY | Active | Project Lead | Process prompt: inventory all test files, produce test suite plan, security plan, load plan, hardening plan, and validation commands. |
| `U0–U9 LEGACY MODERNIZATION AUDIT.md` | U0–U9 LEGACY MODERNIZATION AUDIT.md | Authority | AUTHORITY | Active | Project Lead | Process prompt: comprehensive forensic audit of all U0–U9 outputs — findings register, contradiction register, missed items register, completeness scorecard, final status. |
| `U10 — U0–U9 AUDIT REMEDIATION.md` | U10 — U0–U9 AUDIT REMEDIATION.md | Authority | AUTHORITY | Active | Project Lead | Process prompt: execute all remediations from U0–U9 audit — CRIT-001/CRIT-002, H-001 through H-004, M-001 through M-004. Produce 6 remediation output docs. |

---

## §R — docs/reports/u-series/ (U8 Workspace Sealing Outputs, added by U10 remediation 2026-06-21)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `docs/reports/u-series/WORKSPACE_SEALING_REPORT.md` | WORKSPACE_SEALING_REPORT.md | Report | REPORT | Complete | Claude/AI | U8 output: per-tool sealing findings (npm, node_modules, pnpm, Python/pip/venv, Playwright, env vars, Docker, CI/CD). Overall verdict: FULLY SEALED. 1 WARN (pip cache path inconsistency — both D:, non-critical). |
| `docs/reports/u-series/C_DRIVE_LEAKAGE_AUDIT.md` | C_DRIVE_LEAKAGE_AUDIT.md | Report | REPORT | Complete | Claude/AI | U8 output: audit table for every tool path — SEALED/LEAKING/RISK/NOT PRESENT. Zero C: leakage found. C: grep scan across all config files returned 0 hits. |
| `docs/reports/u-series/SEALED_WORKSPACE_VALIDATION.md` | SEALED_WORKSPACE_VALIDATION.md | Report | REPORT | Complete | Claude/AI | U8 output: 28-check validation checklist. 21 PASS / 1 WARN / 0 FAIL / 6 N/A. Overall verdict: PASS — workspace FULLY SEALED. |

---

## §S — docs/reports/u-series/ (U9 Test Suite Planning Outputs, added by U10 remediation 2026-06-21)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `docs/reports/u-series/TEST_SUITE_PLAN.md` | TEST_SUITE_PLAN.md | Report | REPORT | Active | Claude/AI | U9 output: complete test suite plan — 79 backend test files, 23 E2E playwright, 8 API contract, 1 load, 1 security scan. CI gate: pytest --cov-fail-under=80. Corrected by U10 (was 54/25/6). |
| `docs/reports/u-series/SECURITY_TEST_PLAN.md` | SECURITY_TEST_PLAN.md | Report | REPORT | Active | Claude/AI | U9 output: security test plan — python-jose CVEs (3.5.0 installed, 3.3.0 in stale pip-audit.json), starlette CVEs (accepted risk), pip CVEs (4), semgrep config, OWASP test scope. |
| `docs/reports/u-series/LOAD_TEST_PLAN.md` | LOAD_TEST_PLAN.md | Report | REPORT | Active | Claude/AI | U9 output: Locust load test plan — 6 scenarios, p95 targets per tier, concurrency ramp profile, pass/fail gates. |
| `docs/reports/u-series/HARDENING_PLAN.md` | HARDENING_PLAN.md | Report | REPORT | Active | Claude/AI | U9 output: code hardening action list — Redis rate-limit (A-006), FeatureFlag Redis (A-007), JWT refresh, helmet/CORS, password reset OTP, PostgreSQL Windows stability. |
| `docs/reports/u-series/VALIDATION_COMMANDS.md` | VALIDATION_COMMANDS.md | Report | REPORT | Active | Claude/AI | U9 output: copy-paste command reference for all CI gate validations — pytest, playwright, locust, pip-audit, semgrep, npm audit. |

---

## §T — docs/reports/u-series/ (U10 Forensic Audit + Remediation Outputs, added 2026-06-21)

### Forensic Audit Outputs (U0–U9 audit findings)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `docs/reports/u-series/U0_U9_FORENSIC_AUDIT_REPORT.md` | U0_U9_FORENSIC_AUDIT_REPORT.md | Report | REPORT | Complete | Claude/AI | U10 forensic audit: phase-by-phase verification of all U0–U9 claims against live repository evidence. All claims fact-checked independently. |
| `docs/reports/u-series/U0_U9_FINDINGS_REGISTER.md` | U0_U9_FINDINGS_REGISTER.md | Report | REPORT | Complete | Claude/AI | U10 forensic audit: 22 findings (F-001 through F-022) classified by severity — 2 Critical, 4 High, 6 Medium, 4 Low, 6 Info. |
| `docs/reports/u-series/U0_U9_CONTRADICTION_REGISTER.md` | U0_U9_CONTRADICTION_REGISTER.md | Report | REPORT | Complete | Claude/AI | U10 forensic audit: 10 contradictions (CONT-001 through CONT-010) between phases or between phase outputs and live code. |
| `docs/reports/u-series/U0_U9_MISSED_ITEMS_REGISTER.md` | U0_U9_MISSED_ITEMS_REGISTER.md | Report | REPORT | Complete | Claude/AI | U10 forensic audit: 14 missed items (MI-001 through MI-014) — code/files present in repo but absent from U0–U9 outputs. |
| `docs/reports/u-series/U0_U9_FINAL_STATUS.md` | U0_U9_FINAL_STATUS.md | Report | REPORT | Complete | Claude/AI | U10 forensic audit: final status — PASS WITH FINDINGS. 2 Critical, 4 High, 6 Medium findings. Recommended next-action priority list (10 items). |
| `docs/reports/u-series/U0_U9_COMPLETENESS_SCORECARD.md` | U0_U9_COMPLETENESS_SCORECARD.md | Report | REPORT | Complete | Claude/AI | U10 forensic audit: phase-by-phase completeness scorecard with confidence ratings. |

### Remediation Outputs (U10 execution outputs)

| Path | Filename | Class | Level | Status | Owner | Purpose |
|---|---|---|---|---|---|---|
| `docs/reports/u-series/U10_AUDIT_REMEDIATION_REPORT.md` | U10_AUDIT_REMEDIATION_REPORT.md | Report | REPORT | Complete | Claude/AI | U10 remediation: per-finding log of all actions taken — CRIT-001/CRIT-002, H-001 through H-004, M-001 through M-004, before/after evidence. |
| `docs/reports/u-series/U10_FINDINGS_RESOLUTION_MATRIX.md` | U10_FINDINGS_RESOLUTION_MATRIX.md | Report | REPORT | Complete | Claude/AI | U10 remediation: 22-finding resolution matrix (F-001 through F-022) with RESOLVED/DEFERRED/ACCEPTABLE classification. |
| `docs/reports/u-series/U10_REPOSITORY_ALIGNMENT_REPORT.md` | U10_REPOSITORY_ALIGNMENT_REPORT.md | Report | REPORT | Complete | Claude/AI | U10 remediation: post-remediation repo state — root count 15, docs/ structure, 6 files moved confirmed. |
| `docs/reports/u-series/U10_AUTHORITY_ALIGNMENT_REPORT.md` | U10_AUTHORITY_ALIGNMENT_REPORT.md | Report | REPORT | Complete | Claude/AI | U10 remediation: post-remediation authority docs state — phase agreement, count accuracy, header accuracy. C-001/C-002/C-003 all resolved. |
| `docs/reports/u-series/U10_ENVIRONMENT_ALIGNMENT_REPORT.md` | U10_ENVIRONMENT_ALIGNMENT_REPORT.md | Report | REPORT | Complete | Claude/AI | U10 remediation: python-jose 3.5.0 confirmed installed; pip-audit.json stale; starlette CVEs accepted risk; workspace FULLY SEALED. |
| `docs/reports/u-series/U10_FINAL_STATUS.md` | U10_FINAL_STATUS.md | Report | REPORT | Complete | Claude/AI | U10 remediation: final verdict PASS — all Criticals and Highs resolved; governance framework ready. |

---

## Note on third-party .md files

The following directories contain .md files from installed packages — these are third-party library documentation, not project docs, and are excluded from this catalogue:

- `backend/.venv/Lib/site-packages/**` — Python package READMEs, LICENSE files (~25 files)
- `backend/gateway/node_modules/**` — Node.js package READMEs, CHANGELOGs, HISTORY files (~195 files)
- `frontend/node_modules/**` — Node.js package READMEs, CHANGELOGs (~100 files)
- `backend/.pytest_cache/README.md` — pytest cache marker
- `tests/e2e/playwright/.pytest_cache/README.md` — pytest cache marker
- `.pytest_cache/README.md` — pytest cache marker
- `bin/pgsql/doc/README-pldebugger.md` — PostgreSQL binary documentation
