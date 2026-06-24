Status: Active
Authority Level: Medium
Generated: 2026-06-22
Owner: AI (Claude Sonnet 4.6 — Documentation Normalization session)

---

# DUPLICATION ANALYSIS REPORT — Pakistan CRM OS

## Purpose

Identifies every case where the same information is defined or described in multiple documents. The goal is to establish exactly one authoritative source per claim, and either retire or redirect the duplicates.

**Supersedes:** `docs/reports/u-series/DOC_DUPLICATION_REGISTER.md` (U3 — covered pre-governance 130 docs)

---

## How to Read This Report

| Column | Meaning |
|---|---|
| ID | Duplication identifier (DUP-xxx) |
| Doc A | Primary document — recommended authority |
| Doc B | Secondary document — overlapping content |
| Overlap | What content is duplicated or near-duplicated |
| Severity | High (active confusion risk), Medium (potential confusion), Low (intentional or acceptable overlap) |
| Recommended Action | What to do |

---

## DUP-001 — Entity Definitions: DOMAIN_MODEL.md vs ENTITY_INVENTORY.md vs backend/docs/architecture/domain-model.md

| Field | Value |
|---|---|
| **Doc A (Authority)** | `docs/00_authority/DOMAIN_MODEL.md` |
| **Doc B** | `docs/reports/u-series/ENTITY_INVENTORY.md` |
| **Doc C** | `backend/docs/architecture/domain-model.md` |
| **Overlap** | All three describe entities (User, Lead, Contact, Account, etc.) with fields and relationships. DOMAIN_MODEL.md is the most complete and curated. ENTITY_INVENTORY.md was generated from code evidence and provides more raw field detail. backend/docs/architecture/domain-model.md is a higher-level narrative description. |
| **Severity** | Medium — not actively causing confusion since authority is clear; but three different levels of detail for the same entities creates ambiguity about which to update when entities change. |
| **Recommended Action** | **Designate DOMAIN_MODEL.md as authority. Cross-reference.** ENTITY_INVENTORY.md should add header: "Supporting Reference — for authority, see docs/00_authority/DOMAIN_MODEL.md. This document provides raw code-derived field evidence." backend/docs/architecture/domain-model.md defers to DOMAIN_MODEL.md per its OWNERSHIP comment — add cross-reference in header. When entity changes occur, DOMAIN_MODEL.md must be updated first. |

---

## DUP-002 — API Endpoint Lists: API_INVENTORY.md vs FULLSTACK_STITCHING_CONTRACT.md vs individual backend API spec docs

| Field | Value |
|---|---|
| **Doc A (Authority)** | `docs/reports/u-series/API_INVENTORY.md` — for complete listing |
| **Doc B** | `docs/00_authority/FULLSTACK_STITCHING_CONTRACT.md` — API tables per feature section |
| **Doc C** | `backend/docs/infrastructure/integration-contracts.md` — integration-level API contracts |
| **Overlap** | All three list API endpoints. API_INVENTORY.md has all 228. FULLSTACK_STITCHING_CONTRACT.md lists endpoints per feature (10 primary workflows). integration-contracts.md covers adapter/webhook interfaces. |
| **Severity** | Low — scope is different at each level; this is an intentional depth hierarchy, not true duplication. |
| **Recommended Action** | **Keep all three with clear cross-references.** Document the relationship: API_INVENTORY.md is the flat complete listing; FULLSTACK_STITCHING_CONTRACT.md is the feature-aligned traceability view; integration-contracts.md is the adapter-level interface spec. Each serves a different reader. No content to merge. |

---

## DUP-003 — Workflow Descriptions: PRODUCT_WORKFLOWS.md vs WORKFLOW_INVENTORY.md vs backend/docs/domain/*.md

| Field | Value |
|---|---|
| **Doc A (Authority — Business Workflows)** | `docs/00_authority/PRODUCT_WORKFLOWS.md` — WF-A through WF-E |
| **Doc B (Authority — System Workflows)** | `docs/reports/u-series/WORKFLOW_INVENTORY.md` — WF-001 through WF-005 |
| **Doc C** | `backend/docs/domain/followup-enforcement-model.md`, `backend/docs/domain/collections-engine-model.md`, etc. |
| **Overlap** | WF-001 (Lead Follow-up) is described in PRODUCT_WORKFLOWS.md, WORKFLOW_INVENTORY.md, and followup-enforcement-model.md. WF-002 (Collections) appears in PRODUCT_WORKFLOWS.md, WORKFLOW_INVENTORY.md, and collections-engine-model.md. The descriptions are at different levels of detail. |
| **Severity** | Medium — same workflow described from three angles. Risk: a step count or event name could diverge across documents. |
| **Recommended Action** | **Designate by level.** WORKFLOW_INVENTORY.md governs system workflow (WF-001 through WF-005) technical specs (trigger events, steps DSL, retry policy). PRODUCT_WORKFLOWS.md governs business journey descriptions (WF-A through WF-E end-to-end). Domain docs (followup-enforcement-model.md, etc.) govern domain-specific behavior depth. Add cross-references between levels. On workflow changes: update WORKFLOW_INVENTORY.md (system) or PRODUCT_WORKFLOWS.md (business) first; domain docs can reference either. |

---

## DUP-004 — Permission Definitions: ROLE_PERMISSION_INVENTORY.md vs backend/docs/security/identity-auth-rbac.md vs DOMAIN_MODEL.md §Permission entity

| Field | Value |
|---|---|
| **Doc A (Authority)** | `backend/docs/security/identity-auth-rbac.md` — RBAC design authority |
| **Doc B** | `docs/reports/u-series/ROLE_PERMISSION_INVENTORY.md` — code-derived scope listing |
| **Doc C** | `docs/00_authority/DOMAIN_MODEL.md` §Permission entity — entity-level description |
| **Overlap** | All three describe roles and scopes. identity-auth-rbac.md governs the design model. ROLE_PERMISSION_INVENTORY.md lists what is actually in rbac-scopes.js. DOMAIN_MODEL.md describes Permission as a domain entity. |
| **Severity** | Low — different levels of abstraction; not causing active confusion. |
| **Recommended Action** | **Keep all three.** Each serves a different purpose: design model vs implementation list vs entity model. No action needed beyond ensuring cross-references are present. When scope changes occur: update rbac-scopes.js (code), then ROLE_PERMISSION_INVENTORY.md (documentation), then DOMAIN_MODEL.md §Permission if entity-level change. |

---

## DUP-005 — Module Descriptions: MODULE_INVENTORY.md vs AUTHORITY_RECONSTRUCTION_REPORT.md §2 vs backend/docs/ individual domain files

| Field | Value |
|---|---|
| **Doc A** | `docs/reports/u-series/MODULE_INVENTORY.md` — module inventory with status |
| **Doc B** | `docs/reports/u-series/AUTHORITY_RECONSTRUCTION_REPORT.md` §2 — module table with gateway/backend evidence |
| **Doc C** | `backend/docs/domain/*.md` — individual domain deep-dives |
| **Overlap** | MODULE_INVENTORY.md and AUTHORITY_RECONSTRUCTION_REPORT.md §2 both list all modules with similar columns (frontend pages, backend module, gateway routes, status). Individual domain docs cover each module in greater depth. |
| **Severity** | Low — MODULE_INVENTORY.md and AUTHORITY_RECONSTRUCTION_REPORT.md §2 are redundant at the summary level. Different age/purpose (AUTHORITY_RECONSTRUCTION_REPORT is the definitive U1 output; MODULE_INVENTORY.md is the extracted tracking table). |
| **Recommended Action** | **Designate MODULE_INVENTORY.md as the living module status document.** AUTHORITY_RECONSTRUCTION_REPORT.md §2 is the historical U1 source; it should not be updated. MODULE_INVENTORY.md should be updated when module status changes. Add header note to AUTHORITY_RECONSTRUCTION_REPORT.md: "Module status table superseded by MODULE_INVENTORY.md for live tracking." |

---

## DUP-006 — Architecture Overview: ADR-001_PROJECT_FOUNDATION.md vs AUTHORITY_RECONSTRUCTION_REPORT.md vs WORKSPACE_BASELINE_AUDIT.md vs backend/docs/architecture/architecture-overview.md

| Field | Value |
|---|---|
| **Doc A (Authority)** | `docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md` |
| **Doc B** | `docs/reports/u-series/AUTHORITY_RECONSTRUCTION_REPORT.md` §1 |
| **Doc C** | `docs/reports/u-series/WORKSPACE_BASELINE_AUDIT.md` |
| **Doc D** | `backend/docs/architecture/architecture-overview.md` |
| **Overlap** | The 3-tier architecture diagram (Frontend → Gateway → Services → DB+Redis), tech stack table, and deployment model appear in all four documents. |
| **Severity** | Medium — four places describing the same architecture. If technology changes (e.g., gateway framework), all four would need updating. |
| **Recommended Action** | **Designate ADR-001_PROJECT_FOUNDATION.md as the architecture authority.** Other documents should use it as the reference. When architecture changes: update ADR-001_PROJECT_FOUNDATION.md first; AUTHORITY_RECONSTRUCTION_REPORT.md and WORKSPACE_BASELINE_AUDIT.md are historical snapshots (do not update). backend/docs/architecture/architecture-overview.md defers to ADR-001 for decisions (it is the narrative; ADR is the decisions). Add cross-reference in architecture-overview.md OWNERSHIP comment. |

---

## DUP-007 — Project Purpose: PROJECT_CHARTER.md vs README.md vs COMMERCIALISATION-PLAN.md §intro vs backend/README.md

| Field | Value |
|---|---|
| **Doc A (Authority)** | `docs/00_authority/PROJECT_CHARTER.md` |
| **Doc B** | `README.md` (root) |
| **Doc C** | `COMMERCIALISATION-PLAN.md` (intro section) |
| **Doc D** | `backend/README.md` |
| **Overlap** | All describe the Pakistan CRM, its market (Pakistani SMBs), key differentiators (WhatsApp-first, PKR, JazzCash/Easypaisa), and architecture overview. README.md and backend/README.md are shorter summaries for GitHub visitors. COMMERCIALISATION-PLAN.md has an intro that repeats the purpose. |
| **Severity** | Low — different audience/scope at each level; intentional redundancy is acceptable. |
| **Recommended Action** | **Keep all four with explicit deference to PROJECT_CHARTER.md.** README.md and backend/README.md are audience-appropriate summaries (GitHub landing page, backend developer). COMMERCIALISATION-PLAN.md intro is a phase anchor, not a primary purpose statement. Action: Add note in COMMERCIALISATION-PLAN.md pointing to PROJECT_CHARTER.md for the definitive purpose statement. |

---

## DUP-008 — Document Catalogues: DOC_CATALOGUE.md (u-series) vs DOCUMENT_INVENTORY.md (this session)

| Field | Value |
|---|---|
| **Doc A (Authority)** | `docs/08_reports/DOCUMENT_INVENTORY.md` (this session, 2026-06-22) |
| **Doc B** | `docs/reports/u-series/DOC_CATALOGUE.md` (U2 output, updated through U10 — 167 entries) |
| **Overlap** | Both serve as the master document index. DOC_CATALOGUE.md is the living U-series catalogue (manual update history). DOCUMENT_INVENTORY.md is this session's comprehensive inventory. |
| **Severity** | Medium — two competing master indexes will diverge. |
| **Recommended Action** | **Keep both with clear role separation.** DOC_CATALOGUE.md has historical detail about when documents were added and why. DOCUMENT_INVENTORY.md has classification, authority level, and information domain columns. Neither fully replaces the other. Add header to DOC_CATALOGUE.md: "See also docs/08_reports/DOCUMENT_INVENTORY.md for full classification with authority levels (2026-06-22 normalization session)." |

---

## DUP-009 — Document Classification Matrices: DOCUMENT_CLASSIFICATION_MATRIX.md (u-series) vs DOCUMENT_CLASSIFICATION_MATRIX.md (08_reports)

| Field | Value |
|---|---|
| **Doc A (Authority)** | `docs/08_reports/DOCUMENT_CLASSIFICATION_MATRIX.md` (this session, 2026-06-22) |
| **Doc B** | `docs/reports/u-series/DOCUMENT_CLASSIFICATION_MATRIX.md` (U2, 130 docs) |
| **Overlap** | Both classify project documents by type. U2 version covers 130 pre-governance docs with 6 classes. This session's version covers ~195 docs with 9 classes and includes the governance layer. |
| **Severity** | High — having two classification matrices is confusing; this is a direct duplication of purpose. |
| **Recommended Action** | **Retire U2 version; this session's version is authoritative.** Add SUPERSEDED banner to `docs/reports/u-series/DOCUMENT_CLASSIFICATION_MATRIX.md` pointing to `docs/08_reports/DOCUMENT_CLASSIFICATION_MATRIX.md`. |

---

## DUP-010 — Conflict Registers: DOC_CONFLICT_REGISTER.md (u-series) vs CONFLICT_ANALYSIS_REPORT.md (this session)

| Field | Value |
|---|---|
| **Doc A (Authority)** | `docs/08_reports/CONFLICT_ANALYSIS_REPORT.md` (this session, 2026-06-22) |
| **Doc B** | `docs/reports/u-series/DOC_CONFLICT_REGISTER.md` (U3, pre-governance) |
| **Overlap** | Both document conflicts between project documents. U3 register covered 7 conflicts in the pre-governance 130-doc corpus. This session covers the current state including post-governance conflicts. |
| **Severity** | Medium — pre-governance conflicts were mostly resolved by governance actions; the U3 register is therefore historically complete but no longer the active conflict tracker. |
| **Recommended Action** | **Retire U3 version as a historical record; this session's report is current.** Add note to `docs/reports/u-series/DOC_CONFLICT_REGISTER.md`: "Historical — covers pre-governance conflicts as of U3 (2026-06-20). See docs/08_reports/CONFLICT_ANALYSIS_REPORT.md for current conflict state." |

---

## DUP-011 — Phase Status: PROJECT_CHARTER.md §5 vs AI_OPERATING_CONTEXT.md CURRENT_PHASE vs COMMERCIALISATION-PLAN.md RESUME POINT vs CURRENT_PROJECT_STATUS.md

| Field | Value |
|---|---|
| **Doc A (Authority)** | `COMMERCIALISATION-PLAN.md` RESUME POINT table — operational anchor |
| **Doc B** | `docs/07_governance/AI_OPERATING_CONTEXT.md` CURRENT_PHASE section |
| **Doc C** | `docs/00_authority/PROJECT_CHARTER.md` §5 Current Status |
| **Doc D** | `docs/reports/u-series/CURRENT_PROJECT_STATUS.md` |
| **Overlap** | All four state the current phase (C6) and list what has been built. |
| **Severity** | Low — all four currently agree on C6. Risk is divergence when the phase changes. |
| **Recommended Action** | **COMMERCIALISATION-PLAN.md is the operational authority for phase status.** When phase changes: (1) Update COMMERCIALISATION-PLAN.md RESUME POINT first, (2) Update AI_OPERATING_CONTEXT.md CURRENT_PHASE to match, (3) Update PROJECT_CHARTER.md §5 in the same session. CURRENT_PROJECT_STATUS.md is a more granular status report; update it when detail changes. |

---

## Summary Table

| ID | Doc A | Doc B (+ C, D) | Overlap | Severity | Recommended Action |
|---|---|---|---|---|---|
| DUP-001 | DOMAIN_MODEL.md | ENTITY_INVENTORY.md, backend/docs/architecture/domain-model.md | Entity field definitions | Medium | Designate DOMAIN_MODEL.md as authority; others cross-reference |
| DUP-002 | API_INVENTORY.md | FULLSTACK_STITCHING_CONTRACT.md, integration-contracts.md | API endpoint lists | Low | Keep all — different depth levels; document hierarchy |
| DUP-003 | PRODUCT_WORKFLOWS.md | WORKFLOW_INVENTORY.md, domain docs | Workflow descriptions | Medium | Designate by level; add cross-references |
| DUP-004 | identity-auth-rbac.md | ROLE_PERMISSION_INVENTORY.md, DOMAIN_MODEL.md | Role/scope definitions | Low | Keep all — different abstraction levels |
| DUP-005 | MODULE_INVENTORY.md | AUTHORITY_RECONSTRUCTION_REPORT.md §2 | Module status table | Low | MODULE_INVENTORY.md is live tracker; ARR §2 is historical |
| DUP-006 | ADR-001_PROJECT_FOUNDATION.md | ARR §1, WORKSPACE_BASELINE_AUDIT.md, architecture-overview.md | Architecture overview | Medium | ADR-001 is authority; others are historical or narrative |
| DUP-007 | PROJECT_CHARTER.md | README.md, COMMERCIALISATION-PLAN.md intro, backend/README.md | Project purpose | Low | Keep all — different audiences; acceptable redundancy |
| DUP-008 | DOCUMENT_INVENTORY.md (08_reports) | DOC_CATALOGUE.md (u-series) | Master document index | Medium | Keep both — different columns; add cross-references |
| DUP-009 | DOCUMENT_CLASSIFICATION_MATRIX.md (08_reports) | DOCUMENT_CLASSIFICATION_MATRIX.md (u-series) | Document classification | High | Retire U2 version; add SUPERSEDED banner |
| DUP-010 | CONFLICT_ANALYSIS_REPORT.md (08_reports) | DOC_CONFLICT_REGISTER.md (u-series) | Conflict listing | Medium | Retire U3 version as historical record |
| DUP-011 | COMMERCIALISATION-PLAN.md | AI_OPERATING_CONTEXT.md, PROJECT_CHARTER.md §5, CURRENT_PROJECT_STATUS.md | Phase status | Low | COMMERCIALISATION-PLAN.md is operational authority; others sync to it |

---

*End DUPLICATION_ANALYSIS_REPORT.md*
