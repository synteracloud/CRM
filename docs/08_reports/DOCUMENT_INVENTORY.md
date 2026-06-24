Status: Active
Authority Level: Medium
Generated: 2026-06-22
Owner: AI (Claude Sonnet 4.6 — Documentation Normalization session)

---

# DOCUMENT INVENTORY — Pakistan CRM OS

## Purpose

Complete inventory of all project-owned .md files. Third-party library documentation in `frontend/node_modules/`, `backend/.venv/`, and `bin/pgsql/` is excluded — these are dependency artefacts, not project documentation.

**Total project .md files inventoried: 195**
- Layer A (Governance Phase 1): 14
- Layer B (Backend authority): 80
- Layer C (U-series outputs): 68
- Layer D (Session/operational): 7
- Layer E (Archive): 11
- Layer F (Root authority docs): 10
- Layer G (U-series prompt files at root): 6
- Layer H (Reference): 1
- Layer I (Other): 4 (README.md variants, misc)

---

## Layer A — Governance (Phase 1)

Path prefix: `docs/00_authority/`, `docs/06_decisions/`, `docs/07_governance/`, `docs/08_reports/`

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| docs/00_authority/PROJECT_CHARTER.md | PROJECT_CHARTER.md | A | Authority Document | Critical | Draft | Human | Project Purpose |
| docs/00_authority/FEATURE_SCOPE.md | FEATURE_SCOPE.md | A | Authority Document | Critical | Draft | Human | Product Scope |
| docs/00_authority/DOMAIN_MODEL.md | DOMAIN_MODEL.md | A | Authority Document | Critical | Draft | Shared | Domain Model |
| docs/00_authority/PRODUCT_WORKFLOWS.md | PRODUCT_WORKFLOWS.md | A | Authority Document | Critical | Draft | Shared | Workflows |
| docs/00_authority/FULLSTACK_STITCHING_CONTRACT.md | FULLSTACK_STITCHING_CONTRACT.md | A | Authority Document | Critical | Draft | Shared | Fullstack Contracts |
| docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md | ADR-001_PROJECT_FOUNDATION.md | A | Authority Document | High | Draft | Human | Architecture / Decision Records |
| docs/07_governance/AI_OPERATING_CONTEXT.md | AI_OPERATING_CONTEXT.md | A | Authority Document | Critical | Draft | AI | AI Operating Context |
| docs/07_governance/DECISION_ESCALATION_MATRIX.md | DECISION_ESCALATION_MATRIX.md | A | Authority Document | High | Draft | Shared | Governance |
| docs/08_reports/GOVERNANCE_IMPLEMENTATION_REPORT.md | GOVERNANCE_IMPLEMENTATION_REPORT.md | A | Generated Report | Medium | Active | AI | Governance |
| docs/08_reports/DOCUMENTATION_COVERAGE_MATRIX.md | DOCUMENTATION_COVERAGE_MATRIX.md | A | Generated Report | Medium | Draft | Shared | Testing / Documentation |
| docs/08_reports/ARCHITECTURAL_GAP_REGISTER.md | ARCHITECTURAL_GAP_REGISTER.md | A | Generated Report | Medium | Draft | Shared | Architecture |
| docs/08_reports/RECOMMENDED_ADR_ROADMAP.md | RECOMMENDED_ADR_ROADMAP.md | A | Generated Report | Low | Draft | Human | Decision Records |
| docs/08_reports/GOVERNANCE_CONSISTENCY_AUDIT.md | GOVERNANCE_CONSISTENCY_AUDIT.md | A | Generated Report | High | Active | AI | Governance |
| docs/08_reports/REMEDIATION_REPORT.md | REMEDIATION_REPORT.md | A | Generated Report | High | Active | AI | Governance |

---

## Layer B — Backend Authority

Path prefix: `backend/docs/`, `backend/db/`, `backend/` root

### backend/ root

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/CONSTRAINTS.md | CONSTRAINTS.md | B | Authority Document | Critical | Active | Developer | Architecture / Backend Structure |
| backend/README.md | README.md | B | Supporting Reference | Medium | Active | Developer | Project Purpose / Architecture |
| backend/FRONTEND-BACKEND-MAPPING.md | FRONTEND-BACKEND-MAPPING.md | B | Supporting Reference | Medium | Active | Developer | Fullstack Contracts |
| backend/BACKEND-QC.md | BACKEND-QC.md | B | Operational Artifact | Medium | Active | AI/QA | Testing |
| backend/PENDING.md | PENDING.md | B | Operational Artifact | Low | Active | Developer | Operations |
| backend/market-research-gap-register.md | market-research-gap-register.md | B | Supporting Reference | Low | Active | Human | Product Scope |
| backend/product-spec-gap-register.md | product-spec-gap-register.md | B | Supporting Reference | Low | Active | Human | Product Scope |

### backend/docs/adr/

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/docs/adr/ADR-001.md | ADR-001.md | B | Historical Record | Medium | Superseded (incorporated into docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md) | Developer | Architecture / Decision Records |
| backend/docs/adr/ADR-002.md | ADR-002.md | B | Historical Record | Medium | Superseded (incorporated into docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md) | Developer | Architecture / Decision Records |
| backend/docs/adr/ADR-003.md | ADR-003.md | B | Historical Record | Medium | Superseded (incorporated into docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md) | Developer | Architecture / Decision Records |

### backend/docs/architecture/

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/docs/architecture/architecture-overview.md | architecture-overview.md | B | Authority Document | High | Active | Developer | Architecture |
| backend/docs/architecture/capability-matrix.md | capability-matrix.md | B | Supporting Reference | Medium | Active | Developer | Product Scope |
| backend/docs/architecture/data-architecture.md | data-architecture.md | B | Authority Document | High | Active | Developer | Database / Domain Model |
| backend/docs/architecture/domain-model.md | domain-model.md | B | Supporting Reference | High | Active | Developer | Domain Model |
| backend/docs/architecture/service-map.md | service-map.md | B | Supporting Reference | Medium | Active | Developer | Architecture / Backend Structure |

### backend/docs/domain/

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/docs/domain/activities-tasks.md | activities-tasks.md | B | Authority Document | High | Active | Developer | Domain Model / Workflows |
| backend/docs/domain/activity-control-model.md | activity-control-model.md | B | Authority Document | High | Active | Developer | Domain Model / Workflows |
| backend/docs/domain/ai-predictive-models.md | ai-predictive-models.md | B | Supporting Reference | Medium | Active | Developer | Domain Model |
| backend/docs/domain/cases-domain.md | cases-domain.md | B | Authority Document | High | Active | Developer | Domain Model / Workflows |
| backend/docs/domain/collections-engine-model.md | collections-engine-model.md | B | Authority Document | High | Active | Developer | Domain Model / Workflows |
| backend/docs/domain/contract-lifecycle-management.md | contract-lifecycle-management.md | B | Supporting Reference | Medium | Active | Developer | Domain Model |
| backend/docs/domain/cpq-quotes-orders.md | cpq-quotes-orders.md | B | Authority Document | High | Active | Developer | Domain Model |
| backend/docs/domain/custom-object-framework.md | custom-object-framework.md | B | Supporting Reference | Medium | Active | Developer | Domain Model |
| backend/docs/domain/data-governance-layer.md | data-governance-layer.md | B | Supporting Reference | Medium | Active | Developer | Domain Model |
| backend/docs/domain/data-governance-ownership.md | data-governance-ownership.md | B | Supporting Reference | Medium | Active | Developer | Domain Model |
| backend/docs/domain/employee-performance.md | employee-performance.md | B | Supporting Reference | Low | Active | Developer | Domain Model |
| backend/docs/domain/enterprise-depth.md | enterprise-depth.md | B | Supporting Reference | Low | Active | Developer | Product Scope |
| backend/docs/domain/followup-enforcement-model.md | followup-enforcement-model.md | B | Authority Document | High | Active | Developer | Domain Model / Workflows |
| backend/docs/domain/marketing-campaigns.md | marketing-campaigns.md | B | Authority Document | High | Active | Developer | Domain Model |
| backend/docs/domain/opportunities-pipeline.md | opportunities-pipeline.md | B | Authority Document | High | Active | Developer | Domain Model |
| backend/docs/domain/owner-dashboard.md | owner-dashboard.md | B | Supporting Reference | Medium | Active | Developer | Frontend Build |
| backend/docs/domain/partner-channel-management.md | partner-channel-management.md | B | Supporting Reference | Medium | Active | Developer | Domain Model |
| backend/docs/domain/partners.md | partners.md | B | Supporting Reference | Medium | Active | Developer | Domain Model |
| backend/docs/domain/payments-revenue.md | payments-revenue.md | B | Authority Document | High | Active | Developer | Domain Model |
| backend/docs/domain/shared-inbox.md | shared-inbox.md | B | Authority Document | High | Active | Developer | Domain Model |
| backend/docs/domain/territory-management.md | territory-management.md | B | Supporting Reference | Medium | Active | Developer | Domain Model |

### backend/docs/infrastructure/

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/docs/infrastructure/api-standards.md | api-standards.md | B | Authority Document | High | Active | Developer | API Contracts |
| backend/docs/infrastructure/concurrency-control.md | concurrency-control.md | B | Authority Document | High | Active | Developer | Architecture |
| backend/docs/infrastructure/distributed-lock-strategy.md | distributed-lock-strategy.md | B | Supporting Reference | Medium | Active | Developer | Architecture |
| backend/docs/infrastructure/event-catalog.md | event-catalog.md | B | Authority Document | High | Active | Developer | Workflows |
| backend/docs/infrastructure/execution-hardening.md | execution-hardening.md | B | Authority Document | High | Active | Developer | Architecture |
| backend/docs/infrastructure/feature-flags-config.md | feature-flags-config.md | B | Authority Document | High | Active | Developer | Domain Model |
| backend/docs/infrastructure/global-idempotency.md | global-idempotency.md | B | Authority Document | High | Active | Developer | Architecture |
| backend/docs/infrastructure/integration-contracts.md | integration-contracts.md | B | Authority Document | High | Active | Developer | API Contracts |
| backend/docs/infrastructure/kpi-data-pipelines.md | kpi-data-pipelines.md | B | Supporting Reference | Medium | Active | Developer | Architecture |
| backend/docs/infrastructure/observability-audit.md | observability-audit.md | B | Authority Document | High | Active | Developer | Deployment |
| backend/docs/infrastructure/offline-sync.md | offline-sync.md | B | Supporting Reference | Medium | Active | Developer | Architecture |
| backend/docs/infrastructure/runtime-deployment.md | runtime-deployment.md | B | Authority Document | High | Active | Developer | Deployment |
| backend/docs/infrastructure/scheduler-jobs.md | scheduler-jobs.md | B | Supporting Reference | Medium | Active | Developer | Architecture |
| backend/docs/infrastructure/workflow-catalog.md | workflow-catalog.md | B | Supporting Reference | Medium | Active | Developer | Workflows |
| backend/docs/infrastructure/workflow-dsl.md | workflow-dsl.md | B | Authority Document | High | Active | Developer | Workflows |

### backend/docs/security/

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/docs/security/identity-auth-rbac.md | identity-auth-rbac.md | B | Authority Document | Critical | Active | Developer | Permissions / RBAC |
| backend/docs/security/org-multi-tenancy.md | org-multi-tenancy.md | B | Authority Document | Critical | Active | Developer | Architecture / Permissions |
| backend/docs/security/security-model.md | security-model.md | B | Authority Document | High | Active | Developer | Risk / Security |

### backend/docs/product/

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/docs/product/activation-model.md | activation-model.md | B | Authority Document | High | Active | Developer | Operations / Product Scope |
| backend/docs/product/adoption-ux.md | adoption-ux.md | B | Supporting Reference | Medium | Active | Developer | Frontend Build |
| backend/docs/product/localization.md | localization.md | B | Supporting Reference | Medium | Active | Developer | Architecture |
| backend/docs/product/pricing-plans.md | pricing-plans.md | B | Supporting Reference | Medium | Active | Developer | Operations |

### backend/docs/adapters/

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/docs/adapters/compliance-adapter.md | compliance-adapter.md | B | Supporting Reference | Medium | Active | Developer | Risk / Security |
| backend/docs/adapters/conversational-action-spec.md | conversational-action-spec.md | B | Supporting Reference | Medium | Active | Developer | Workflows |
| backend/docs/adapters/integration-flow-traces.md | integration-flow-traces.md | B | Supporting Reference | Medium | Active | Developer | API Contracts |
| backend/docs/adapters/pakistan-adapter-architecture.md | pakistan-adapter-architecture.md | B | Authority Document | High | Active | Developer | Architecture |
| backend/docs/adapters/whatsapp-execution-model.md | whatsapp-execution-model.md | B | Authority Document | High | Active | Developer | Workflows / Domain Model |

### backend/docs/ui/

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/docs/ui/read-models.md | read-models.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/ui/ui-foundations.md | ui-foundations.md | B | Supporting Reference | Medium | Active | Developer | Frontend Build |
| backend/docs/ui/ui-system.md | ui-system.md | B | Authority Document | High | Active | Developer | Frontend Build |

### backend/docs/_b9/ (page spec docs)

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/docs/_b9/b9-p01-dashboard-kpi.md | b9-p01-dashboard-kpi.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p02-list-queue.md | b9-p02-list-queue.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p03-sales-cockpit.md | b9-p03-sales-cockpit.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p04-support-console.md | b9-p04-support-console.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p05-marketing-workspace.md | b9-p05-marketing-workspace.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p06-entity-detail.md | b9-p06-entity-detail.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p07-workflow-visual-ui.md | b9-p07-workflow-visual-ui.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p08-builder-extensions.md | b9-p08-builder-extensions.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p08-mobile-responsiveness-system.md | b9-p08-mobile-responsiveness-system.md | B | Supporting Reference | Medium | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p09-settings-admin.md | b9-p09-settings-admin.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p10-reporting-analytics.md | b9-p10-reporting-analytics.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p11-form-wizard.md | b9-p11-form-wizard.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p12-audit-compliance.md | b9-p12-audit-compliance.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p13-inbox-communication.md | b9-p13-inbox-communication.md | B | Authority Document | High | Active | Developer | Frontend Build |
| backend/docs/_b9/b9-p14-ai-copilot.md | b9-p14-ai-copilot.md | B | Authority Document | High | Active | Developer | Frontend Build |

### backend/docs/_qc/

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/docs/_qc/phase4-stage1-read-log.md | phase4-stage1-read-log.md | B | Historical Record | Low | Complete | AI | Operations |
| backend/docs/_qc/qc-integration.md | qc-integration.md | B | Supporting Reference | Medium | Active | AI/QA | Testing |
| backend/docs/_qc/qc-intelligence-data.md | qc-intelligence-data.md | B | Supporting Reference | Medium | Active | AI/QA | Testing |

### backend/docs/ root

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/docs/phase4-gap-register.md | phase4-gap-register.md | B | Historical Record | Low | Stale | Developer | Architecture |

### backend/db/

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/db/activity_task_db/self-qc.md | self-qc.md | B | Historical Record | Low | Complete | AI/QA | Database |
| backend/db/activity_task_db/README.md | README.md | B | Supporting Reference | Low | Active | Developer | Database |
| backend/db/transaction_db/self-qc.md | self-qc.md | B | Historical Record | Low | Complete | AI/QA | Database |
| backend/db/transaction_db/README.md | README.md | B | Supporting Reference | Low | Active | Developer | Database |
| backend/db/transaction_db/transaction-policies.md | transaction-policies.md | B | Authority Document | High | Active | Developer | Database |

### backend/gateway/

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| backend/gateway/README.md | README.md | B | Supporting Reference | Medium | Active | Developer | API Contracts / Architecture |
| backend/gateway/self-qc.md | self-qc.md | B | Historical Record | Low | Complete | AI/QA | Architecture |

---

## Layer C — U-Series Outputs

Path prefix: `docs/reports/u-series/`

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| docs/reports/u-series/U0 — REPOSITORY REALITY DISCOVERY.md | U0 — REPOSITORY REALITY DISCOVERY.md | C | Historical Record | Low | Complete | AI | Architecture |
| docs/reports/u-series/U1 — AUTHORITY RECONSTRUCTION.md | U1 — AUTHORITY RECONSTRUCTION.md | C | Historical Record | Low | Complete | AI | Architecture |
| docs/reports/u-series/U2 — DOCUMENTATION CATALOGUE.md | U2 — DOCUMENTATION CATALOGUE.md | C | Historical Record | Low | Complete | AI | Operations |
| docs/reports/u-series/U3 — DOCUMENTATION NORMALIZATION.md | U3 — DOCUMENTATION NORMALIZATION.md | C | Historical Record | Low | Complete | AI | Operations |
| docs/reports/u-series/U4 — WORKSPACE RESTRUCTURING PLAN.md | U4 — WORKSPACE RESTRUCTURING PLAN.md | C | Historical Record | Low | Complete | AI | Operations |
| docs/reports/u-series/REPOSITORY_TREE_INVENTORY.md | REPOSITORY_TREE_INVENTORY.md | C | Generated Report | Low | Stale | AI | Architecture |
| docs/reports/u-series/REPOSITORY_REALITY_REPORT.md | REPOSITORY_REALITY_REPORT.md | C | Generated Report | Medium | Active | AI | Architecture |
| docs/reports/u-series/WORKFLOW_INVENTORY.md | WORKFLOW_INVENTORY.md | C | Supporting Reference | High | Active | AI | Workflows |
| docs/reports/u-series/FEATURE_INVENTORY.md | FEATURE_INVENTORY.md | C | Supporting Reference | Medium | Active | AI | Product Scope |
| docs/reports/u-series/DOCUMENT_CLASSIFICATION_MATRIX.md | DOCUMENT_CLASSIFICATION_MATRIX.md | C | Generated Report | Medium | Stale (130 docs; this report supersedes) | AI | Operations |
| docs/reports/u-series/DOCUMENT_OWNERSHIP_MATRIX.md | DOCUMENT_OWNERSHIP_MATRIX.md | C | Generated Report | Medium | Stale (130 docs; this report supersedes) | AI | Operations |
| docs/reports/u-series/DOC_NORMALIZATION_REPORT.md | DOC_NORMALIZATION_REPORT.md | C | Generated Report | Medium | Stale (this report supersedes) | AI | Operations |
| docs/reports/u-series/DOC_CONFLICT_REGISTER.md | DOC_CONFLICT_REGISTER.md | C | Generated Report | Medium | Stale (this report supersedes) | AI | Operations |
| docs/reports/u-series/DOC_DUPLICATION_REGISTER.md | DOC_DUPLICATION_REGISTER.md | C | Generated Report | Medium | Stale (this report supersedes) | AI | Operations |
| docs/reports/u-series/DOC_STALE_REFERENCE_REPORT.md | DOC_STALE_REFERENCE_REPORT.md | C | Generated Report | Low | Stale | AI | Operations |
| docs/reports/u-series/DOC_CATALOGUE.md | DOC_CATALOGUE.md | C | Supporting Reference | Medium | Active | AI | Operations |
| docs/reports/u-series/WORKSPACE_RESTRUCTURING_PLAN.md | WORKSPACE_RESTRUCTURING_PLAN.md | C | Historical Record | Low | Complete | AI | Operations |
| docs/reports/u-series/FILE_RELOCATION_MATRIX.md | FILE_RELOCATION_MATRIX.md | C | Historical Record | Low | Complete | AI | Operations |
| docs/reports/u-series/FOLDER_PURPOSE_MATRIX.md | FOLDER_PURPOSE_MATRIX.md | C | Supporting Reference | Low | Active | AI | Operations |
| docs/reports/u-series/BREAKAGE_RISK_REPORT.md | BREAKAGE_RISK_REPORT.md | C | Historical Record | Low | Complete | AI | Operations |
| docs/reports/u-series/RESTRUCTURING_EXECUTION_REPORT.md | RESTRUCTURING_EXECUTION_REPORT.md | C | Historical Record | Low | Complete | AI | Operations |
| docs/reports/u-series/STALE_LINK_FIX_REPORT.md | STALE_LINK_FIX_REPORT.md | C | Historical Record | Low | Complete | AI | Operations |
| docs/reports/u-series/POST_RESTRUCTURE_VALIDATION.md | POST_RESTRUCTURE_VALIDATION.md | C | Historical Record | Low | Complete | AI | Operations |
| docs/reports/u-series/DOC_CODE_DELTA_REPORT.md | DOC_CODE_DELTA_REPORT.md | C | Generated Report | Medium | Active | AI | Fullstack Contracts |
| docs/reports/u-series/UNDOCUMENTED_CODE_REGISTER.md | UNDOCUMENTED_CODE_REGISTER.md | C | Generated Report | Medium | Active | AI | Backend Structure |
| docs/reports/u-series/STALE_DOC_CLAIMS_REGISTER.md | STALE_DOC_CLAIMS_REGISTER.md | C | Generated Report | Medium | Active | AI | Operations |
| docs/reports/u-series/DELTA_SUMMARY_REPORT.md | DELTA_SUMMARY_REPORT.md | C | Generated Report | Medium | Active | AI | Fullstack Contracts |
| docs/reports/u-series/MODULE_INVENTORY.md | MODULE_INVENTORY.md | C | Supporting Reference | High | Active | AI | Backend Structure |
| docs/reports/u-series/DOC_CODE_REMEDIATION_REPORT.md | DOC_CODE_REMEDIATION_REPORT.md | C | Generated Report | Low | Complete | AI | Operations |
| docs/reports/u-series/BACKEND_DOC_ALIGNMENT_STATUS.md | BACKEND_DOC_ALIGNMENT_STATUS.md | C | Generated Report | Medium | Active | AI | Backend Structure |
| docs/reports/u-series/WORKSPACE_SEALING_REPORT.md | WORKSPACE_SEALING_REPORT.md | C | Historical Record | Low | Complete | AI | Deployment |
| docs/reports/u-series/C_DRIVE_LEAKAGE_AUDIT.md | C_DRIVE_LEAKAGE_AUDIT.md | C | Historical Record | Low | Complete | AI | Deployment |
| docs/reports/u-series/SEALED_WORKSPACE_VALIDATION.md | SEALED_WORKSPACE_VALIDATION.md | C | Historical Record | Low | Complete | AI | Deployment |
| docs/reports/u-series/LOAD_TEST_PLAN.md | LOAD_TEST_PLAN.md | C | Supporting Reference | Medium | Active | AI | Testing |
| docs/reports/u-series/VALIDATION_COMMANDS.md | VALIDATION_COMMANDS.md | C | Supporting Reference | Medium | Active | AI | Testing |
| docs/reports/u-series/U0_U9_FORENSIC_AUDIT_REPORT.md | U0_U9_FORENSIC_AUDIT_REPORT.md | C | Generated Report | Medium | Complete | AI | Operations |
| docs/reports/u-series/U0_U9_FINDINGS_REGISTER.md | U0_U9_FINDINGS_REGISTER.md | C | Generated Report | Medium | Complete | AI | Operations |
| docs/reports/u-series/U0_U9_CONTRADICTION_REGISTER.md | U0_U9_CONTRADICTION_REGISTER.md | C | Generated Report | Medium | Complete | AI | Operations |
| docs/reports/u-series/U0_U9_MISSED_ITEMS_REGISTER.md | U0_U9_MISSED_ITEMS_REGISTER.md | C | Generated Report | Low | Complete | AI | Operations |
| docs/reports/u-series/U0_U9_COMPLETENESS_SCORECARD.md | U0_U9_COMPLETENESS_SCORECARD.md | C | Generated Report | Low | Complete | AI | Operations |
| docs/reports/u-series/U0_U9_FINAL_STATUS.md | U0_U9_FINAL_STATUS.md | C | Generated Report | Medium | Complete | AI | Operations |
| docs/reports/u-series/WORKSPACE_BASELINE_AUDIT.md | WORKSPACE_BASELINE_AUDIT.md | C | Generated Report | Medium | Active | AI | Architecture |
| docs/reports/u-series/CURRENT_PROJECT_STATUS.md | CURRENT_PROJECT_STATUS.md | C | Generated Report | High | Active | AI | Operations |
| docs/reports/u-series/TEST_SUITE_PLAN.md | TEST_SUITE_PLAN.md | C | Supporting Reference | High | Active | AI | Testing |
| docs/reports/u-series/SECURITY_TEST_PLAN.md | SECURITY_TEST_PLAN.md | C | Supporting Reference | High | Active | AI | Risk / Security |
| docs/reports/u-series/HARDENING_PLAN.md | HARDENING_PLAN.md | C | Supporting Reference | High | Active | AI | Risk / Security |
| docs/reports/u-series/AUTHORITY_RECONSTRUCTION_REPORT.md | AUTHORITY_RECONSTRUCTION_REPORT.md | C | Generated Report | High | Active | AI | Architecture |
| docs/reports/u-series/U10_AUDIT_REMEDIATION_REPORT.md | U10_AUDIT_REMEDIATION_REPORT.md | C | Generated Report | Medium | Complete | AI | Operations |
| docs/reports/u-series/U10_FINDINGS_RESOLUTION_MATRIX.md | U10_FINDINGS_RESOLUTION_MATRIX.md | C | Generated Report | Medium | Complete | AI | Operations |
| docs/reports/u-series/U10_REPOSITORY_ALIGNMENT_REPORT.md | U10_REPOSITORY_ALIGNMENT_REPORT.md | C | Generated Report | Medium | Complete | AI | Operations |
| docs/reports/u-series/U10_AUTHORITY_ALIGNMENT_REPORT.md | U10_AUTHORITY_ALIGNMENT_REPORT.md | C | Generated Report | Medium | Complete | AI | Operations |
| docs/reports/u-series/U10_ENVIRONMENT_ALIGNMENT_REPORT.md | U10_ENVIRONMENT_ALIGNMENT_REPORT.md | C | Generated Report | Medium | Complete | AI | Deployment |
| docs/reports/u-series/U10_FINAL_STATUS.md | U10_FINAL_STATUS.md | C | Generated Report | Medium | Complete | AI | Operations |
| docs/reports/u-series/API_INVENTORY.md | API_INVENTORY.md | C | Supporting Reference | High | Active | AI | API Contracts |
| docs/reports/u-series/ROLE_PERMISSION_INVENTORY.md | ROLE_PERMISSION_INVENTORY.md | C | Supporting Reference | High | Active | AI | Permissions / RBAC |
| docs/reports/u-series/ENTITY_INVENTORY.md | ENTITY_INVENTORY.md | C | Supporting Reference | High | Active | AI | Domain Model |

---

## Layer D — Session/Operational

Path prefix: `docs/reports/session/`

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| docs/reports/session/SCREEN-ARTEFACTS.md | SCREEN-ARTEFACTS.md | D | Operational Artifact | Low | Active | AI/QA | Frontend Build |
| docs/reports/session/CHANGELOG.md | CHANGELOG.md | D | Operational Artifact | Low | Active | Developer | Operations |
| docs/reports/session/DOC-READ-LOG.md | DOC-READ-LOG.md | D | Operational Artifact | Low | Active | AI | Operations |
| docs/reports/session/SESSION-HANDOFF.md | SESSION-HANDOFF.md | D | Operational Artifact | Low | Stale (pre-governance) | AI | Operations |
| docs/reports/session/PENDING.md | PENDING.md | D | Operational Artifact | Low | Active | Developer | Operations |
| docs/reports/session/PROGRESS.md | PROGRESS.md | D | Operational Artifact | Low | Active | Developer | Operations |
| docs/reports/session/SYSTEM-SNAPSHOT.md | SYSTEM-SNAPSHOT.md | D | Operational Artifact | Medium | Stale (C2-era; says C3 is current) | AI | Operations |

---

## Layer E — Archive

Path prefix: `docs/archive/`, `_archive/`

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| docs/archive/deployment-pipelines.md | deployment-pipelines.md | E | Retired Document | Low | Archived | Developer | Deployment |
| docs/archive/gap-register.md | gap-register.md | E | Retired Document | Low | Archived | Developer | Architecture |
| docs/archive/FRAMEWORK-GAPS.md | FRAMEWORK-GAPS.md | E | Retired Document | Low | Archived | Developer | Frontend Build |
| docs/archive/CATALOGUE-MERGE-PLAN.md | CATALOGUE-MERGE-PLAN.md | E | Retired Document | Low | Archived | AI | Operations |
| docs/archive/MAPPING-TRACKER.md | MAPPING-TRACKER.md | E | Retired Document | Low | Archived | AI | Operations |
| docs/archive/DOC-CATALOGUE.md | DOC-CATALOGUE.md | E | Retired Document | Low | Superseded by docs/reports/u-series/DOC_CATALOGUE.md | AI | Operations |
| docs/archive/REBUILD-PLAN.md | REBUILD-PLAN.md | E | Retired Document | Low | Superseded by COMMERCIALISATION-PLAN.md | Developer | Operations |
| _archive/README.md | README.md | E | Historical Record | Low | Complete | Developer | Operations |

---

## Layer F — Root Authority Documents

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| CLAUDE.md | CLAUDE.md | F | Authority Document | Critical | Active | Human | AI Operating Context / Frontend Build |
| DESIGN-SPEC.md | DESIGN-SPEC.md | F | Authority Document | Critical | Active | Human | Product Scope / Frontend Build |
| FRAMEWORK.md | FRAMEWORK.md | F | Authority Document | Critical | Active | Developer | Frontend Build |
| COMMERCIALISATION-PLAN.md | COMMERCIALISATION-PLAN.md | F | Authority Document | Critical | Active | Human | Operations |
| README.md | README.md | F | Supporting Reference | Medium | Active | Human | Project Purpose |
| PAGE-BUILD-PROTOCOL.md | PAGE-BUILD-PROTOCOL.md | F | Authority Document | High | Active | AI | Frontend Build |
| DESIGN-SPEC.md | DESIGN-SPEC.md | F | Authority Document | Critical | Active | Human | Product Scope |
| PRODUCT-SPEC.md | PRODUCT-SPEC.md | F | Supporting Reference | Medium | Active | Developer | Product Scope |
| CONTRIBUTING.md | CONTRIBUTING.md | F | Supporting Reference | Low | Active | Developer | Governance |

---

## Layer G — U-Series Prompt Files (Root)

These are the original prompt files that drove the U0–U10 sessions. They are not authority documents — they are historical execution prompts.

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| U0–U9 LEGACY MODERNIZATION AUDIT.md | U0–U9 LEGACY MODERNIZATION AUDIT.md | G | Historical Record | Low | Complete | Human | Operations |
| U10 — U0–U9 AUDIT REMEDIATION.md | U10 — U0–U9 AUDIT REMEDIATION.md | G | Historical Record | Low | Complete | Human | Operations |
| U5 — WORKSPACE RESTRUCTURING EXECUTION.md | U5 — WORKSPACE RESTRUCTURING EXECUTION.md | G | Historical Record | Low | Complete | Human | Operations |
| U6 — DOC TO CODE DELTA ANALYSIS.md | U6 — DOC TO CODE DELTA ANALYSIS.md | G | Historical Record | Low | Complete | Human | Operations |
| U7 — DELTA REMEDIATION.md | U7 — DELTA REMEDIATION.md | G | Historical Record | Low | Complete | Human | Operations |
| U8 — WORKSPACE SEALING.md | U8 — WORKSPACE SEALING.md | G | Historical Record | Low | Complete | Human | Operations |
| U9 — TEST SUITE PLANNING.md | U9 — TEST SUITE PLANNING.md | G | Historical Record | Low | Complete | Human | Operations |

---

## Layer H — Reference

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| docs/reference/RENDER-DEPLOY.md | RENDER-DEPLOY.md | H | Supporting Reference | Medium | Active | DevOps | Deployment |

---

## Layer I — Other

| Path | Filename | Layer | Class | Authority Level | Status | Owner | Information Domain |
|---|---|---|---|---|---|---|---|
| AUDIT REMEDIATION.md | AUDIT REMEDIATION.md | I | Working Draft | Low | Draft (prompt file for this phase) | Human | Operations |
| DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md | DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md | I | Working Draft | Low | Draft (prompt for this task) | Human | Operations |
| GOVERNANCE IMPLEMENTATION PHASE 1.md | GOVERNANCE IMPLEMENTATION PHASE 1.md | I | Historical Record | Low | Complete | Human | Governance |
| PHASE 1 GOVERNANCE VALIDATION.md | PHASE 1 GOVERNANCE VALIDATION.md | I | Historical Record | Low | Complete | Human | Governance |
| PROMPT SEQUENCE.md | PROMPT SEQUENCE.md | I | Supporting Reference | Low | Active | Human | Operations |
| tests/e2e/playwright/SKIP-BACKLOG.md | SKIP-BACKLOG.md | I | Operational Artifact | Low | Active | AI/QA | Testing |
| backend/db/activity_task_db/README.md | README.md | I | Supporting Reference | Low | Active | Developer | Database |

---

*End DOCUMENT_INVENTORY.md*
