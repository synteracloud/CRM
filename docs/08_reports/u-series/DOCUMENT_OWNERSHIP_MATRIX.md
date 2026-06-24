> **SEE ALSO:** [DOCUMENT_INVENTORY.md](../../08_reports/DOCUMENT_INVENTORY.md) (docs/08_reports/, 2026-06-22) for owner classification across all ~195 project documents, including the governance layer added in Governance Phase 1. This file covers 130 pre-governance documents (U2 output) and contains useful ownership history; the 08_reports version adds authority level and information domain columns.
> Updated: 2026-06-21 (Documentation Normalization Phase — DUP-008/Tier 2 redirect)

# DOCUMENT_OWNERSHIP_MATRIX.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U2 — Documentation Catalogue)
**Total project .md files:** 130
**Owner classification:** based on document content, intent, and update pattern.

---

## Ownership Summary

| Owner | Count | Description |
|---|---|---|
| Project Lead | 10 | Strategic docs, phase gates, product decisions |
| Developer | 57 | Technical specs, domain models, API contracts, ADRs |
| Claude/AI | 42 | Generated reports, trackers, inventories, audit outputs |
| QA/Claude | 9 | QC records, test docs, self-qc logs |
| DevOps | 5 | Deployment, infrastructure, CI/CD docs |
| **Total** | **123** | (130 - 7 archive/third-party excluded from ownership breakdown) |

---

## Project Lead-Owned (10)

Strategic documents: design decisions, product specs, phase gates, process directives.

| Path | Class | Status | Purpose |
|---|---|---|---|
| `CLAUDE.md` | Authority | Active | Session enforcement rules — defines how Claude must work on this project |
| `DESIGN-SPEC.md` | Authority | Active | Screen inventory and build phase gates — approved by Project Lead per phase |
| `COMMERCIALISATION-PLAN.md` | Authority | Active | Active anchor C0–C6 — governs all current commercialisation work |
| `PRODUCT-SPEC.md` | Reference | Active | Product and market specification — defines system identity and Pakistan fit |
| `U0 — REPOSITORY REALITY DISCOVERY.md` | Authority | Active | Process directive prompt |
| `U1 — AUTHORITY RECONSTRUCTION.md` | Authority | Active | Process directive prompt |
| `U2 — DOCUMENTATION CATALOGUE.md` | Authority | Active | Process directive prompt |
| `backend/CONSTRAINTS.md` | Authority | Active | 17 non-negotiable build constraints |
| `backend/docs/product/pricing-plans.md` | Reference | Active | PKR pricing tiers and market positioning |
| `backend/docs/product/adoption-ux.md` | Reference | Active | 4-tier progressive disclosure and adoption model |

---

## Developer-Owned (57)

Technical specs, domain models, API contracts, ADRs, and infrastructure rules.

### Core Build Docs (3)
| Path | Status | Purpose |
|---|---|---|
| `README.md` | Active | Project landing page and architecture overview |
| `CONTRIBUTING.md` | Active | Branch naming, commit format, PR process |
| `RENDER-DEPLOY.md` | Active | Render.com deployment guide (C4) |

### Framework and Protocol Docs (2)
| Path | Status | Purpose |
|---|---|---|
| `FRAMEWORK.md` | Active | Complete technical build reference §0–§32 |
| `PAGE-BUILD-PROTOCOL.md` | Active | Mandatory pre-build protocol |

### Backend Core (2)
| Path | Status | Purpose |
|---|---|---|
| `backend/README.md` | Active | Backend system identity and design principles |
| `backend/db/transaction_db/transaction-policies.md` | Active | Transaction ACID policies |

### DB Schema Docs (2)
| Path | Status | Purpose |
|---|---|---|
| `backend/db/activity_task_db/README.md` | Active | Activity/task DB scope |
| `backend/db/transaction_db/README.md` | Active | Transaction DB scope |

### API Gateway Doc (1)
| Path | Status | Purpose |
|---|---|---|
| `backend/gateway/README.md` | Active | Gateway structure: 42 routers, RBAC scopes, middleware |

### ADRs (3)
| Path | Status | Purpose |
|---|---|---|
| `backend/docs/adr/ADR-001.md` | Active | DDD + Microservices decision |
| `backend/docs/adr/ADR-002.md` | Active | Adapter pattern decision |
| `backend/docs/adr/ADR-003.md` | Active | WhatsApp-first decision |

### Architecture Docs (5)
| Path | Status | Purpose |
|---|---|---|
| `backend/docs/architecture/architecture-overview.md` | Active | System architecture narrative |
| `backend/docs/architecture/capability-matrix.md` | Active | Capability matrix with implementation status |
| `backend/docs/architecture/data-architecture.md` | Active | CQRS-lite data architecture |
| `backend/docs/architecture/domain-model.md` | Active | 79 canonical domain entities |
| `backend/docs/architecture/service-map.md` | Active | Service ownership map |

### Page Archetype Specs (15)
| Path | Status | Purpose |
|---|---|---|
| `backend/docs/_b9/b9-p01-dashboard-kpi.md` | Active | Dashboard/KPI archetype (A-pages) |
| `backend/docs/_b9/b9-p02-list-queue.md` | Active | List/Queue archetype (B-pages) |
| `backend/docs/_b9/b9-p03-sales-cockpit.md` | Active | Sales Cockpit archetype (D-01) |
| `backend/docs/_b9/b9-p04-support-console.md` | Active | Support Console archetype (E-01) |
| `backend/docs/_b9/b9-p05-marketing-workspace.md` | Active | Marketing Workspace archetype (F-01) |
| `backend/docs/_b9/b9-p06-entity-detail.md` | Active | Entity Detail archetype (C-pages) |
| `backend/docs/_b9/b9-p07-workflow-visual-ui.md` | Active | Workflow Builder archetype (K-01) |
| `backend/docs/_b9/b9-p08-builder-extensions.md` | Active | Builder/Extensions archetype (K-02/K-03/K-04) |
| `backend/docs/_b9/b9-p08-mobile-responsiveness-system.md` | Active | Mobile responsiveness spec |
| `backend/docs/_b9/b9-p09-settings-admin.md` | Active | Settings/Admin archetype (G-pages) |
| `backend/docs/_b9/b9-p10-reporting-analytics.md` | Active | Reporting/Analytics archetype (H-pages) |
| `backend/docs/_b9/b9-p11-form-wizard.md` | Active | Form/Wizard archetype (I-pages) |
| `backend/docs/_b9/b9-p12-audit-compliance.md` | Active | Audit/Compliance archetype (J-pages) |
| `backend/docs/_b9/b9-p13-inbox-communication.md` | Active | Inbox/Communication archetype (L-pages) |
| `backend/docs/_b9/b9-p14-ai-copilot.md` | Active | AI Copilot archetype (M-pages) |

### Domain Specs (21)
| Path | Status | Purpose |
|---|---|---|
| `backend/docs/domain/activities-tasks.md` | Active | Activity and task domain |
| `backend/docs/domain/activity-control-model.md` | Active | Activity Control Engine |
| `backend/docs/domain/ai-predictive-models.md` | Active | AI predictive models (Sprint 5B-7) |
| `backend/docs/domain/cases-domain.md` | Active | Cases/Support (Sprint 5B-1) |
| `backend/docs/domain/collections-engine-model.md` | Active | Collections Engine |
| `backend/docs/domain/contract-lifecycle-management.md` | Active | Contract lifecycle |
| `backend/docs/domain/cpq-quotes-orders.md` | Active | CPQ quotes and orders |
| `backend/docs/domain/custom-object-framework.md` | Active | Custom object builder |
| `backend/docs/domain/data-governance-layer.md` | Active | Data governance |
| `backend/docs/domain/data-governance-ownership.md` | Active | Data governance ownership |
| `backend/docs/domain/employee-performance.md` | Active | Employee performance |
| `backend/docs/domain/enterprise-depth.md` | Active | Enterprise depth requirements |
| `backend/docs/domain/followup-enforcement-model.md` | Active | Follow-up Engine |
| `backend/docs/domain/marketing-campaigns.md` | Active | Campaigns (Sprint 5B-4) |
| `backend/docs/domain/opportunities-pipeline.md` | Active | Opportunities pipeline |
| `backend/docs/domain/owner-dashboard.md` | Active | Owner dashboard |
| `backend/docs/domain/partner-channel-management.md` | Active | Partner channel management |
| `backend/docs/domain/partners.md` | Active | Partners (Sprint 5B-5) |
| `backend/docs/domain/payments-revenue.md` | Active | Payments and revenue |
| `backend/docs/domain/shared-inbox.md` | Active | Shared Inbox (Sprint 5B-2) |
| `backend/docs/domain/territory-management.md` | Active | Territory management (Sprint 5B-3) |

### Infrastructure Specs (9)
| Path | Status | Purpose |
|---|---|---|
| `backend/docs/infrastructure/api-standards.md` | Active | API design standards |
| `backend/docs/infrastructure/concurrency-control.md` | Active | OCC and row-level locking |
| `backend/docs/infrastructure/distributed-lock-strategy.md` | Active | Redis-based distributed locking |
| `backend/docs/infrastructure/event-catalog.md` | Active | All system events |
| `backend/docs/infrastructure/execution-hardening.md` | Active | Idempotency, retry, DLQ |
| `backend/docs/infrastructure/feature-flags-config.md` | Active | Feature flag system |
| `backend/docs/infrastructure/global-idempotency.md` | Active | Idempotency table and protocol |
| `backend/docs/infrastructure/integration-contracts.md` | Active | Provider allowlist and contract shapes |
| `backend/docs/infrastructure/kpi-data-pipelines.md` | Active | KPI data pipelines |
| `backend/docs/infrastructure/observability-audit.md` | Active | Logging, tracing, alerting |
| `backend/docs/infrastructure/offline-sync.md` | Active | Offline queue and sync |
| `backend/docs/infrastructure/scheduler-jobs.md` | Active | Background job definitions |
| `backend/docs/infrastructure/workflow-catalog.md` | Active | 5 named workflow definitions |
| `backend/docs/infrastructure/workflow-dsl.md` | Active | Workflow DSL grammar |

### Security Specs (3)
| Path | Status | Purpose |
|---|---|---|
| `backend/docs/security/identity-auth-rbac.md` | Active | JWT, RBAC, 7 roles, 63 scopes |
| `backend/docs/security/org-multi-tenancy.md` | Active | Tenant isolation rules |
| `backend/docs/security/security-model.md` | Active | Overall security model |

### UI Specs (3)
| Path | Status | Purpose |
|---|---|---|
| `backend/docs/ui/read-models.md` | Active | 15+ read model shapes |
| `backend/docs/ui/ui-foundations.md` | Active | Design system basics |
| `backend/docs/ui/ui-system.md` | Active | Component rules, DataTable, filter chips |

### Pakistan Adapter Docs (5)
| Path | Status | Purpose |
|---|---|---|
| `backend/docs/adapters/compliance-adapter.md` | Active | Compliance adapter (PTA, FBR) |
| `backend/docs/adapters/conversational-action-spec.md` | Active | Conversational action spec |
| `backend/docs/adapters/integration-flow-traces.md` | Active | Integration flow traces |
| `backend/docs/adapters/pakistan-adapter-architecture.md` | Active | Pakistan adapter L1/L2/L3 model |
| `backend/docs/adapters/whatsapp-execution-model.md` | Active | WhatsApp execution model |

### Product Docs (2)
| Path | Status | Purpose |
|---|---|---|
| `backend/docs/product/activation-model.md` | Active | Activation Engine spec |
| `backend/docs/product/localization.md` | Active | Localization: PKR, EN/UR |

---

## Claude/AI-Owned (42)

Generated reports, trackers, inventories, audit outputs, and session logs. These files are written and maintained by Claude during build sessions.

### Root Session and Status Docs (8)
| Path | Class | Status |
|---|---|---|
| `CHANGELOG.md` | Historical | Active |
| `PROGRESS.md` | Report | Active |
| `PENDING.md` | Report | Active |
| `SESSION-HANDOFF.md` | Report | Active |
| `SYSTEM-SNAPSHOT.md` | Report | Active |
| `CATALOGUE-MERGE-PLAN.md` | Report | Complete |
| `MAPPING-TRACKER.md` | Reference | Complete |
| `DOC-CATALOGUE.md` | Reference | Active |
| `DOC-READ-LOG.md` | Reference | Active |
| `REBUILD-PLAN.md` | Historical | Superseded |

### U0 Discovery Outputs (4)
| Path | Class | Status |
|---|---|---|
| `WORKSPACE_BASELINE_AUDIT.md` | Report | Active |
| `REPOSITORY_REALITY_REPORT.md` | Report | Active |
| `REPOSITORY_TREE_INVENTORY.md` | Report | Active |
| `CURRENT_PROJECT_STATUS.md` | Report | Active |

### U1 Authority Outputs (7)
| Path | Class | Status |
|---|---|---|
| `AUTHORITY_RECONSTRUCTION_REPORT.md` | Report | Active |
| `FEATURE_INVENTORY.md` | Report | Active |
| `MODULE_INVENTORY.md` | Report | Active |
| `ENTITY_INVENTORY.md` | Report | Active |
| `WORKFLOW_INVENTORY.md` | Report | Active |
| `ROLE_PERMISSION_INVENTORY.md` | Report | Active |
| `API_INVENTORY.md` | Report | Active |

### U2 Catalogue Outputs (3)
| Path | Class | Status |
|---|---|---|
| `DOC_CATALOGUE.md` | Reference | Active |
| `DOCUMENT_CLASSIFICATION_MATRIX.md` | Reference | Active |
| `DOCUMENT_OWNERSHIP_MATRIX.md` | Reference | Active |

### Backend Gap and Tracking Docs (8)
| Path | Class | Status |
|---|---|---|
| `backend/FRONTEND-BACKEND-MAPPING.md` | Reference | Active |
| `backend/PENDING.md` | Report | Active |
| `backend/market-research-gap-register.md` | Report | Active |
| `backend/product-spec-gap-register.md` | Report | Active |
| `backend/docs/phase4-gap-register.md` | Report | Complete |
| `backend/docs/_qc/phase4-stage1-read-log.md` | Report | Complete |
| `_archive/FRAMEWORK-GAPS.md` | Archive | Superseded |
| `_archive/gap-register.md` | Archive | Superseded |

---

## QA/Claude-Owned (9)

QC records, self-qc logs, and test documentation.

| Path | Class | Status | Purpose |
|---|---|---|---|
| `SCREEN-ARTEFACTS.md` | Historical | Active | T1–T4 QC records and browser sign-offs for all 75 custom pages |
| `backend/BACKEND-QC.md` | Report | Active | Consolidated backend QC log |
| `backend/db/activity_task_db/self-qc.md` | Report | Complete | Activity/task DB QC |
| `backend/db/transaction_db/self-qc.md` | Report | Complete | Payments/revenue QC |
| `backend/gateway/self-qc.md` | Report | Complete | Gateway accounts/contacts QC |
| `backend/docs/_qc/qc-integration.md` | Report | Complete | B5-QC01 integration QC |
| `backend/docs/_qc/qc-intelligence-data.md` | Report | Complete | B4-QC01 intelligence/data QC |
| `tests/e2e/playwright/SKIP-BACKLOG.md` | Report | Active | Playwright skip backlog: 3 design gaps |

---

## DevOps-Owned (5)

Deployment, infrastructure, and CI/CD documentation.

| Path | Class | Status | Purpose |
|---|---|---|---|
| `RENDER-DEPLOY.md` | Reference | Active | Render.com deployment guide |
| `backend/docs/infrastructure/runtime-deployment.md` | Reference | Active | Runtime deployment model (Docker + Render) |
| `backend/docs/product/pricing-plans.md` | Reference | Active | Pricing tiers and infrastructure cost planning |
| `_archive/deployment-pipelines.md` | Archive | Superseded | Original CI/CD pipeline spec (superseded) |

---

## Flags: Duplicated, Conflicting, or Orphaned Documents

### Duplicated (same content in multiple files)

| Issue | Files | Notes |
|---|---|---|
| **Document catalogue duplication** | `DOC-CATALOGUE.md` (§A root) and `DOC_CATALOGUE.md` (U2 output) | DOC-CATALOGUE.md is the pre-existing manually-maintained index; DOC_CATALOGUE.md is the new U2-generated authoritative replacement. Recommend: deprecate DOC-CATALOGUE.md in favour of DOC_CATALOGUE.md. |
| **Ownership / identity claims** | `README.md` and `backend/README.md` both describe system identity | Partial duplication of system identity narrative. Acceptable — different audiences (GitHub vs backend dev). |

### Conflicting (contradictory information)

| Issue | Files | Notes |
|---|---|---|
| **REBUILD-PLAN.md vs COMMERCIALISATION-PLAN.md** | Both define RESUME POINT | REBUILD-PLAN.md is explicitly marked CLOSED; COMMERCIALISATION-PLAN.md supersedes it. No real conflict — but both files contain RESUME POINT headings which could confuse a first-time reader. REBUILD-PLAN.md resume point should be ignored. |
| **DOC-CATALOGUE.md doc count** | Claims "105 active + 0 planned + 3 archived" | U2 count is 130 project .md files. The pre-existing catalogue was not updated after U0/U1 outputs were added. |
| **SYSTEM-SNAPSHOT.md C4 status** | Claims "C4 COMPLETE 2026-06-01" | COMMERCIALISATION-PLAN.md says "C5 ⬜ pending". SYSTEM-SNAPSHOT.md needs updating to reflect C5/C6 status. |

### Orphaned (no references to or from other docs)

| File | Notes |
|---|---|
| `backend/docs/domain/enterprise-depth.md` | Not referenced from DOC-CATALOGUE.md §K. Cross-references to it from BACKEND-QC.md are generic. Confirm it is being actively used. |
| `backend/docs/domain/data-governance-ownership.md` | Separate from `data-governance-layer.md` — their relationship is not clearly cross-referenced. Consider merging or explicitly linking. |
| `backend/docs/_b9/b9-p08-mobile-responsiveness-system.md` | Does not correspond to any single archetype page. Confirm it is referenced from FRAMEWORK.md or a b9-p spec. |
| `CATALOGUE-MERGE-PLAN.md` | COMPLETE status — no longer referenced from SYSTEM-SNAPSHOT.md or PENDING.md. Safe to archive. |
| `backend/product-spec-gap-register.md` | Not referenced from SYSTEM-SNAPSHOT.md or PENDING.md. May be stale after Phase 4 completion. |
