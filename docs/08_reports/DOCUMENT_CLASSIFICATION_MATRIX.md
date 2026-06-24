Status: Active
Authority Level: Medium
Generated: 2026-06-22
Owner: AI (Claude Sonnet 4.6 — Documentation Normalization session)

---

# DOCUMENT CLASSIFICATION MATRIX — Pakistan CRM OS

## Purpose

Every project-owned document classified into exactly one class. Third-party library docs excluded.
Source: DOCUMENT_INVENTORY.md (this session).

---

## Classification Definitions

| Class | Definition |
|---|---|
| Authority Document | Single source of truth for an information domain; governs decisions; others must defer to it |
| Supporting Reference | Supplements an authority; lookup material, detailed specs, inventories; does not govern |
| Operational Artifact | Tracks ongoing work — progress logs, session handoffs, changelogs, pending task lists |
| Historical Record | Documents past state; no longer current; retained for audit trail |
| Generated Report | Output of an automated or semi-automated analysis process |
| Working Draft | In-progress; not yet authoritative |
| Retired Document | Explicitly superseded; kept for record only |
| Duplicate Document | Same content as another doc; candidate for consolidation |
| Obsolete Document | No longer relevant; content superseded by code or governance changes |

---

## Authority Documents

Documents that govern how work is done. No other document may contradict these.

| Path | Owner | Authority Level | Information Domain |
|---|---|---|---|
| docs/00_authority/PROJECT_CHARTER.md | Human | Critical | Project Purpose, Product Scope |
| docs/00_authority/FEATURE_SCOPE.md | Human | Critical | Product Scope |
| docs/00_authority/DOMAIN_MODEL.md | Shared | Critical | Domain Model |
| docs/00_authority/PRODUCT_WORKFLOWS.md | Shared | Critical | Workflows |
| docs/00_authority/FULLSTACK_STITCHING_CONTRACT.md | Shared | Critical | Fullstack Contracts |
| docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md | Human | High | Architecture, Decision Records |
| docs/07_governance/AI_OPERATING_CONTEXT.md | AI | Critical | AI Operating Context |
| docs/07_governance/DECISION_ESCALATION_MATRIX.md | Shared | High | Governance |
| CLAUDE.md | Human | Critical | AI Operating Context, Frontend Build |
| DESIGN-SPEC.md | Human | Critical | Product Scope, Frontend Build |
| FRAMEWORK.md | Developer | Critical | Frontend Build |
| COMMERCIALISATION-PLAN.md | Human | Critical | Operations |
| PAGE-BUILD-PROTOCOL.md | AI | High | Frontend Build |
| backend/CONSTRAINTS.md | Developer | Critical | Architecture, Backend Structure |
| backend/docs/architecture/architecture-overview.md | Developer | High | Architecture |
| backend/docs/architecture/data-architecture.md | Developer | High | Database, Domain Model |
| backend/docs/security/identity-auth-rbac.md | Developer | Critical | Permissions / RBAC |
| backend/docs/security/org-multi-tenancy.md | Developer | Critical | Architecture, Permissions |
| backend/docs/security/security-model.md | Developer | High | Risk / Security |
| backend/docs/infrastructure/api-standards.md | Developer | High | API Contracts |
| backend/docs/infrastructure/integration-contracts.md | Developer | High | API Contracts |
| backend/docs/infrastructure/workflow-dsl.md | Developer | High | Workflows |
| backend/docs/infrastructure/event-catalog.md | Developer | High | Workflows |
| backend/docs/infrastructure/execution-hardening.md | Developer | High | Architecture |
| backend/docs/infrastructure/global-idempotency.md | Developer | High | Architecture |
| backend/docs/infrastructure/concurrency-control.md | Developer | High | Architecture |
| backend/docs/infrastructure/feature-flags-config.md | Developer | High | Domain Model |
| backend/docs/infrastructure/observability-audit.md | Developer | High | Deployment |
| backend/docs/infrastructure/runtime-deployment.md | Developer | High | Deployment |
| backend/docs/adapters/pakistan-adapter-architecture.md | Developer | High | Architecture |
| backend/docs/adapters/whatsapp-execution-model.md | Developer | High | Workflows, Domain Model |
| backend/docs/ui/read-models.md | Developer | High | Frontend Build |
| backend/docs/ui/ui-system.md | Developer | High | Frontend Build |
| backend/docs/domain/activities-tasks.md | Developer | High | Domain Model, Workflows |
| backend/docs/domain/activity-control-model.md | Developer | High | Domain Model, Workflows |
| backend/docs/domain/cases-domain.md | Developer | High | Domain Model, Workflows |
| backend/docs/domain/collections-engine-model.md | Developer | High | Domain Model, Workflows |
| backend/docs/domain/cpq-quotes-orders.md | Developer | High | Domain Model |
| backend/docs/domain/followup-enforcement-model.md | Developer | High | Domain Model, Workflows |
| backend/docs/domain/marketing-campaigns.md | Developer | High | Domain Model |
| backend/docs/domain/opportunities-pipeline.md | Developer | High | Domain Model |
| backend/docs/domain/payments-revenue.md | Developer | High | Domain Model |
| backend/docs/domain/shared-inbox.md | Developer | High | Domain Model |
| backend/docs/product/activation-model.md | Developer | High | Operations, Product Scope |
| backend/docs/_b9/b9-p01-dashboard-kpi.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p02-list-queue.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p03-sales-cockpit.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p04-support-console.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p05-marketing-workspace.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p06-entity-detail.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p07-workflow-visual-ui.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p08-builder-extensions.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p09-settings-admin.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p10-reporting-analytics.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p11-form-wizard.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p12-audit-compliance.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p13-inbox-communication.md | Developer | High | Frontend Build |
| backend/docs/_b9/b9-p14-ai-copilot.md | Developer | High | Frontend Build |
| backend/db/transaction_db/transaction-policies.md | Developer | High | Database |

**Authority Document count: 57**

---

## Supporting Reference Documents

Supplements an authority; detailed lookup material, inventories, specifications. Does not govern.

| Path | Owner | Domain |
|---|---|---|
| README.md | Human | Project Purpose |
| PRODUCT-SPEC.md | Developer | Product Scope |
| CONTRIBUTING.md | Developer | Governance |
| backend/README.md | Developer | Project Purpose, Architecture |
| backend/FRONTEND-BACKEND-MAPPING.md | Developer | Fullstack Contracts |
| backend/market-research-gap-register.md | Human | Product Scope |
| backend/product-spec-gap-register.md | Human | Product Scope |
| backend/gateway/README.md | Developer | API Contracts |
| backend/docs/architecture/domain-model.md | Developer | Domain Model |
| backend/docs/architecture/capability-matrix.md | Developer | Product Scope |
| backend/docs/architecture/service-map.md | Developer | Architecture |
| backend/docs/domain/ai-predictive-models.md | Developer | Domain Model |
| backend/docs/domain/contract-lifecycle-management.md | Developer | Domain Model |
| backend/docs/domain/custom-object-framework.md | Developer | Domain Model |
| backend/docs/domain/data-governance-layer.md | Developer | Domain Model |
| backend/docs/domain/data-governance-ownership.md | Developer | Domain Model |
| backend/docs/domain/employee-performance.md | Developer | Domain Model |
| backend/docs/domain/enterprise-depth.md | Developer | Product Scope |
| backend/docs/domain/owner-dashboard.md | Developer | Frontend Build |
| backend/docs/domain/partner-channel-management.md | Developer | Domain Model |
| backend/docs/domain/partners.md | Developer | Domain Model |
| backend/docs/domain/territory-management.md | Developer | Domain Model |
| backend/docs/infrastructure/distributed-lock-strategy.md | Developer | Architecture |
| backend/docs/infrastructure/kpi-data-pipelines.md | Developer | Architecture |
| backend/docs/infrastructure/offline-sync.md | Developer | Architecture |
| backend/docs/infrastructure/scheduler-jobs.md | Developer | Architecture |
| backend/docs/infrastructure/workflow-catalog.md | Developer | Workflows |
| backend/docs/adapters/compliance-adapter.md | Developer | Risk / Security |
| backend/docs/adapters/conversational-action-spec.md | Developer | Workflows |
| backend/docs/adapters/integration-flow-traces.md | Developer | API Contracts |
| backend/docs/ui/ui-foundations.md | Developer | Frontend Build |
| backend/docs/_b9/b9-p08-mobile-responsiveness-system.md | Developer | Frontend Build |
| backend/docs/product/adoption-ux.md | Developer | Frontend Build |
| backend/docs/product/localization.md | Developer | Architecture |
| backend/docs/product/pricing-plans.md | Developer | Operations |
| backend/docs/_qc/qc-integration.md | AI/QA | Testing |
| backend/docs/_qc/qc-intelligence-data.md | AI/QA | Testing |
| backend/db/activity_task_db/README.md | Developer | Database |
| backend/db/transaction_db/README.md | Developer | Database |
| docs/reports/u-series/WORKFLOW_INVENTORY.md | AI | Workflows |
| docs/reports/u-series/FEATURE_INVENTORY.md | AI | Product Scope |
| docs/reports/u-series/DOC_CATALOGUE.md | AI | Operations |
| docs/reports/u-series/FOLDER_PURPOSE_MATRIX.md | AI | Operations |
| docs/reports/u-series/MODULE_INVENTORY.md | AI | Backend Structure |
| docs/reports/u-series/API_INVENTORY.md | AI | API Contracts |
| docs/reports/u-series/ROLE_PERMISSION_INVENTORY.md | AI | Permissions / RBAC |
| docs/reports/u-series/ENTITY_INVENTORY.md | AI | Domain Model |
| docs/reports/u-series/TEST_SUITE_PLAN.md | AI | Testing |
| docs/reports/u-series/SECURITY_TEST_PLAN.md | AI | Risk / Security |
| docs/reports/u-series/HARDENING_PLAN.md | AI | Risk / Security |
| docs/reports/u-series/LOAD_TEST_PLAN.md | AI | Testing |
| docs/reports/u-series/VALIDATION_COMMANDS.md | AI | Testing |
| docs/reference/RENDER-DEPLOY.md | DevOps | Deployment |
| PROMPT SEQUENCE.md | Human | Operations |

**Supporting Reference count: 54**

---

## Operational Artifacts

Active tracking of current work state. Updated every session.

| Path | Owner | Domain |
|---|---|---|
| COMMERCIALISATION-PLAN.md | Human | Operations (NOTE: also classified Authority Document — primary class is Authority; Operational in its tracking role) |
| docs/reports/session/SCREEN-ARTEFACTS.md | AI/QA | Frontend Build |
| docs/reports/session/CHANGELOG.md | Developer | Operations |
| docs/reports/session/DOC-READ-LOG.md | AI | Operations |
| docs/reports/session/PENDING.md | Developer | Operations |
| docs/reports/session/PROGRESS.md | Developer | Operations |
| docs/reports/session/SESSION-HANDOFF.md | AI | Operations |
| backend/BACKEND-QC.md | AI/QA | Testing |
| backend/PENDING.md | Developer | Operations |
| tests/e2e/playwright/SKIP-BACKLOG.md | AI/QA | Testing |

**Operational Artifact count: 10**

---

## Historical Records

Documents past state; retained for audit; not current.

| Path | What It Records |
|---|---|
| docs/reports/u-series/U0 — REPOSITORY REALITY DISCOVERY.md | U0 session prompt log |
| docs/reports/u-series/U1 — AUTHORITY RECONSTRUCTION.md | U1 session prompt log |
| docs/reports/u-series/U2 — DOCUMENTATION CATALOGUE.md | U2 session prompt log |
| docs/reports/u-series/U3 — DOCUMENTATION NORMALIZATION.md | U3 session prompt log |
| docs/reports/u-series/U4 — WORKSPACE RESTRUCTURING PLAN.md | U4 session prompt log |
| docs/reports/u-series/WORKSPACE_RESTRUCTURING_PLAN.md | U4 restructuring plan (complete) |
| docs/reports/u-series/FILE_RELOCATION_MATRIX.md | U5 file move log (complete) |
| docs/reports/u-series/BREAKAGE_RISK_REPORT.md | U5 breakage risk assessment (complete) |
| docs/reports/u-series/RESTRUCTURING_EXECUTION_REPORT.md | U5 execution record (complete) |
| docs/reports/u-series/STALE_LINK_FIX_REPORT.md | U5 link fix record (complete) |
| docs/reports/u-series/POST_RESTRUCTURE_VALIDATION.md | U5 post-restructure check (complete) |
| docs/reports/u-series/DOC_CODE_REMEDIATION_REPORT.md | U7 remediation record (complete) |
| docs/reports/u-series/WORKSPACE_SEALING_REPORT.md | U8 workspace seal log (complete) |
| docs/reports/u-series/C_DRIVE_LEAKAGE_AUDIT.md | U8 C: drive audit (complete) |
| docs/reports/u-series/SEALED_WORKSPACE_VALIDATION.md | U8 seal validation (complete) |
| backend/docs/adr/ADR-001.md | Original DDD ADR (incorporated into ADR-001_PROJECT_FOUNDATION.md) |
| backend/docs/adr/ADR-002.md | Original Adapter ADR (incorporated) |
| backend/docs/adr/ADR-003.md | Original WhatsApp ADR (incorporated) |
| backend/docs/phase4-gap-register.md | Phase 4 gap register (stale; pre-governance) |
| backend/docs/_qc/phase4-stage1-read-log.md | Phase 4 read log (complete) |
| backend/db/activity_task_db/self-qc.md | DB QC record (complete) |
| backend/db/transaction_db/self-qc.md | DB QC record (complete) |
| backend/gateway/self-qc.md | Gateway QC record (complete) |
| _archive/README.md | Archive index note |
| docs/reports/session/SYSTEM-SNAPSHOT.md | C2-era system state (stale — says C3 is current; actual is C6) |
| docs/reports/session/SESSION-HANDOFF.md | Pre-governance session handoff (stale) |
| U0–U9 LEGACY MODERNIZATION AUDIT.md | U0–U9 series prompt |
| U10 — U0–U9 AUDIT REMEDIATION.md | U10 prompt |
| U5 — WORKSPACE RESTRUCTURING EXECUTION.md | U5 prompt |
| U6 — DOC TO CODE DELTA ANALYSIS.md | U6 prompt |
| U7 — DELTA REMEDIATION.md | U7 prompt |
| U8 — WORKSPACE SEALING.md | U8 prompt |
| U9 — TEST SUITE PLANNING.md | U9 prompt |
| GOVERNANCE IMPLEMENTATION PHASE 1.md | Governance Phase 1 prompt |
| PHASE 1 GOVERNANCE VALIDATION.md | Governance Phase 1 validation prompt |

**Historical Record count: 35**

---

## Generated Reports

Output of automated or semi-automated analysis. Snapshot in time; may become stale.

| Path | Generated By | Status |
|---|---|---|
| docs/reports/u-series/REPOSITORY_TREE_INVENTORY.md | U0 | Stale |
| docs/reports/u-series/REPOSITORY_REALITY_REPORT.md | U0 | Active |
| docs/reports/u-series/DOCUMENT_CLASSIFICATION_MATRIX.md | U2 | Superseded by this document |
| docs/reports/u-series/DOCUMENT_OWNERSHIP_MATRIX.md | U2 | Superseded by this document |
| docs/reports/u-series/DOC_NORMALIZATION_REPORT.md | U3 | Superseded by this session's report |
| docs/reports/u-series/DOC_CONFLICT_REGISTER.md | U3 | Superseded by this session's report |
| docs/reports/u-series/DOC_DUPLICATION_REGISTER.md | U3 | Superseded by this session's report |
| docs/reports/u-series/DOC_STALE_REFERENCE_REPORT.md | U3 | Stale |
| docs/reports/u-series/DOC_CODE_DELTA_REPORT.md | U6 | Active |
| docs/reports/u-series/UNDOCUMENTED_CODE_REGISTER.md | U6 | Active |
| docs/reports/u-series/STALE_DOC_CLAIMS_REGISTER.md | U6 | Active |
| docs/reports/u-series/DELTA_SUMMARY_REPORT.md | U6/U7 | Active |
| docs/reports/u-series/BACKEND_DOC_ALIGNMENT_STATUS.md | U6 | Active |
| docs/reports/u-series/U0_U9_FORENSIC_AUDIT_REPORT.md | U10 | Complete |
| docs/reports/u-series/U0_U9_FINDINGS_REGISTER.md | U10 | Complete |
| docs/reports/u-series/U0_U9_CONTRADICTION_REGISTER.md | U10 | Complete |
| docs/reports/u-series/U0_U9_MISSED_ITEMS_REGISTER.md | U10 | Complete |
| docs/reports/u-series/U0_U9_COMPLETENESS_SCORECARD.md | U10 | Complete |
| docs/reports/u-series/U0_U9_FINAL_STATUS.md | U10 | Complete |
| docs/reports/u-series/WORKSPACE_BASELINE_AUDIT.md | U0 | Active |
| docs/reports/u-series/CURRENT_PROJECT_STATUS.md | U0/updated | Active |
| docs/reports/u-series/U10_AUDIT_REMEDIATION_REPORT.md | U10 | Complete |
| docs/reports/u-series/U10_FINDINGS_RESOLUTION_MATRIX.md | U10 | Complete |
| docs/reports/u-series/U10_REPOSITORY_ALIGNMENT_REPORT.md | U10 | Complete |
| docs/reports/u-series/U10_AUTHORITY_ALIGNMENT_REPORT.md | U10 | Complete |
| docs/reports/u-series/U10_ENVIRONMENT_ALIGNMENT_REPORT.md | U10 | Complete |
| docs/reports/u-series/U10_FINAL_STATUS.md | U10 | Complete |
| docs/reports/u-series/AUTHORITY_RECONSTRUCTION_REPORT.md | U1 | Active |
| docs/08_reports/GOVERNANCE_IMPLEMENTATION_REPORT.md | Governance Phase 1 | Active |
| docs/08_reports/DOCUMENTATION_COVERAGE_MATRIX.md | Governance Phase 1 | Active |
| docs/08_reports/ARCHITECTURAL_GAP_REGISTER.md | Governance Phase 1 | Active |
| docs/08_reports/RECOMMENDED_ADR_ROADMAP.md | Governance Phase 1 | Active |
| docs/08_reports/GOVERNANCE_CONSISTENCY_AUDIT.md | Governance Phase 1 | Active |
| docs/08_reports/REMEDIATION_REPORT.md | Governance Phase 1 | Active |

**Generated Report count: 34**

---

## Working Drafts

In-progress; not yet authoritative.

| Path | Notes |
|---|---|
| AUDIT REMEDIATION.md | Root prompt file for an audit remediation session — working instruction doc |
| DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md | Root prompt for this task — working instruction doc |

**Working Draft count: 2**

---

## Retired Documents

Explicitly superseded; kept for record only.

| Path | Superseded By |
|---|---|
| docs/archive/DOC-CATALOGUE.md | docs/reports/u-series/DOC_CATALOGUE.md |
| docs/archive/REBUILD-PLAN.md | COMMERCIALISATION-PLAN.md |
| docs/archive/deployment-pipelines.md | docs/reference/RENDER-DEPLOY.md + backend/docs/infrastructure/runtime-deployment.md |
| docs/archive/gap-register.md | docs/08_reports/ARCHITECTURAL_GAP_REGISTER.md |
| docs/archive/FRAMEWORK-GAPS.md | FRAMEWORK.md (gaps resolved) |
| docs/archive/CATALOGUE-MERGE-PLAN.md | docs/reports/u-series/DOC_CATALOGUE.md |
| docs/archive/MAPPING-TRACKER.md | docs/reports/u-series/DOCUMENT_OWNERSHIP_MATRIX.md |

**Retired Document count: 7**

---

## Duplicate Documents

Documents with substantially the same content as another document.

| Path | Duplicate Of | Notes |
|---|---|---|
| backend/docs/architecture/domain-model.md | docs/00_authority/DOMAIN_MODEL.md | backend/docs version is less detailed; governance version is authoritative |
| docs/reports/u-series/DOCUMENT_CLASSIFICATION_MATRIX.md | This document (docs/08_reports/DOCUMENT_CLASSIFICATION_MATRIX.md) | U2 version covers 130 docs; this version covers ~195 docs; this supersedes |
| docs/reports/u-series/DOC_CONFLICT_REGISTER.md | docs/08_reports/CONFLICT_ANALYSIS_REPORT.md (this session) | U3 version covers pre-governance state; this session's version is current |
| docs/reports/u-series/DOC_DUPLICATION_REGISTER.md | docs/08_reports/DUPLICATION_ANALYSIS_REPORT.md (this session) | U3 version; this session's version is current |

**Duplicate Document count: 4**

---

## Obsolete Documents

Content fully superseded by code reality or governance changes; no longer relevant.

None identified. All documents retained have some reference or historical value.

**Obsolete Document count: 0**

---

## Summary Count Table

| Class | Count |
|---|---|
| Authority Document | 57 |
| Supporting Reference | 54 |
| Operational Artifact | 10 |
| Historical Record | 35 |
| Generated Report | 34 |
| Working Draft | 2 |
| Retired Document | 7 |
| Duplicate Document | 4 |
| Obsolete Document | 0 |
| **Total** | **203** |

Note: Count exceeds DOCUMENT_INVENTORY.md total (195) due to 8 documents appearing in more than one classification (e.g., COMMERCIALISATION-PLAN.md is both Authority Document and Operational Artifact in different roles). The primary classification from DOCUMENT_INVENTORY.md governs.

---

*End DOCUMENT_CLASSIFICATION_MATRIX.md*
