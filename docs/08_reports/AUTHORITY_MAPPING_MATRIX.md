Status: Active
Authority Level: High
Generated: 2026-06-22
Owner: AI (Claude Sonnet 4.6 — Documentation Normalization session)

---

# AUTHORITY MAPPING MATRIX — Pakistan CRM OS

## Purpose

For each information domain, this matrix identifies exactly one authoritative document, lists supporting documents and legacy/competing documents, and notes any unresolved conflicts.

**Principle:** The governance foundation (docs/00_authority/, docs/06_decisions/, docs/07_governance/) and the backend authority documents (backend/docs/) are the PRIMARY sources of truth. Everything else must either support them, reference them, or be retired.

**Authority levels:**
- Critical: Must be read and followed. Contradiction is a blocker.
- High: Governs the domain. Competing claims require resolution.
- Medium: Supplements but does not govern.

---

## 1. Project Purpose

*What the SaaS is, who it serves, why it exists.*

| Field | Document |
|---|---|
| **Authority Document** | `docs/00_authority/PROJECT_CHARTER.md` (Critical) |
| **Supporting Documents** | `README.md` (root), `backend/README.md`, `backend/docs/product/activation-model.md` |
| **Legacy / Competing** | `COMMERCIALISATION-PLAN.md` §1 (purpose narrative overlaps PROJECT_CHARTER.md §1–§3; COMMERCIALISATION-PLAN.md is authority for Operations, not Purpose) |
| **Conflict Notes** | No substantive conflict. README.md and backend/README.md are intentionally shorter versions of the purpose statement for different audiences. PROJECT_CHARTER.md is the complete record. |

---

## 2. Product Scope

*What features are in / out of scope for v1.*

| Field | Document |
|---|---|
| **Authority Document** | `docs/00_authority/FEATURE_SCOPE.md` (Critical) |
| **Supporting Documents** | `DESIGN-SPEC.md` (frontend scope), `docs/reports/u-series/FEATURE_INVENTORY.md`, `backend/docs/architecture/capability-matrix.md`, `backend/market-research-gap-register.md`, `backend/product-spec-gap-register.md`, `PRODUCT-SPEC.md` |
| **Legacy / Competing** | `docs/00_authority/PROJECT_CHARTER.md` §4 (product scope summary), `COMMERCIALISATION-PLAN.md` (references blocked features); these are subordinate; FEATURE_SCOPE.md is the definitive list |
| **Conflict Notes** | PROJECT_CHARTER.md §4 states "91 scopes" for IAM feature. The H-002 finding in REMEDIATION_REPORT.md documents that contacts.delete scope is missing, making the effective reachable scope count 91 but the DELETE /contacts endpoint inaccessible. This is a code gap, not a scope conflict. |

---

## 3. Architecture

*Overall system architecture decisions, layer model, deployment topology.*

| Field | Document |
|---|---|
| **Authority Document** | `docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md` (High) — consolidates original ADR-001, ADR-002, ADR-003 |
| **Supporting Documents** | `backend/docs/architecture/architecture-overview.md`, `backend/docs/architecture/service-map.md`, `backend/docs/adapters/pakistan-adapter-architecture.md`, `backend/CONSTRAINTS.md`, `docs/reports/u-series/WORKSPACE_BASELINE_AUDIT.md`, `docs/reports/u-series/AUTHORITY_RECONSTRUCTION_REPORT.md` |
| **Legacy / Competing** | `backend/docs/adr/ADR-001.md`, `backend/docs/adr/ADR-002.md`, `backend/docs/adr/ADR-003.md` — original ADRs; now incorporated into ADR-001_PROJECT_FOUNDATION.md; original files are Historical Records |
| **Conflict Notes** | Gateway route count: PROJECT_CHARTER.md and AI_OPERATING_CONTEXT.md now both say 44 route groups (corrected by U10 REMEDIATION_REPORT.md). No remaining architectural conflicts. |

---

## 4. Domain Model

*Entities, relationships, business rules, field definitions.*

| Field | Document |
|---|---|
| **Authority Document** | `docs/00_authority/DOMAIN_MODEL.md` (Critical) |
| **Supporting Documents** | `docs/reports/u-series/ENTITY_INVENTORY.md` (detailed field-level evidence from code), `backend/docs/architecture/domain-model.md` (higher-level domain description), `backend/docs/architecture/data-architecture.md` |
| **Legacy / Competing** | `backend/docs/architecture/domain-model.md` overlaps DOMAIN_MODEL.md at the entity level; backend version less detailed — DOMAIN_MODEL.md is authoritative. Individual domain docs (backend/docs/domain/*.md) are authoritative for domain-specific behavior patterns but defer to DOMAIN_MODEL.md for entity fields. |
| **Conflict Notes** | D-003 from AI_OPERATING_CONTEXT.md: 5 entity schemas partially inferred from gateway code, not directly read from schema.sql (Activities, Tasks, Accounts, Quotes, Orders). DOMAIN_MODEL.md notes this uncertainty. No direct conflict with other documents; these remain TBD – REQUIRES VERIFICATION items. |

---

## 5. API Contracts

*All API endpoints, methods, auth requirements, request/response shapes.*

| Field | Document |
|---|---|
| **Authority Document** | `backend/docs/infrastructure/api-standards.md` (High) — governs API design rules |
| **Authority Document (Inventory)** | `docs/reports/u-series/API_INVENTORY.md` (High) — the complete route listing (228 endpoints, 44 route groups) |
| **Supporting Documents** | `backend/docs/infrastructure/integration-contracts.md`, `backend/docs/adapters/integration-flow-traces.md`, `backend/gateway/README.md`, `docs/00_authority/FULLSTACK_STITCHING_CONTRACT.md` §API tables |
| **Legacy / Competing** | None. API_INVENTORY.md is the only complete endpoint registry. |
| **Conflict Notes** | H-001 (GOVERNANCE_CONSISTENCY_AUDIT.md): gateway count discrepancy "42 vs 43 vs 44" was present in pre-governance docs. REMEDIATION_REPORT.md confirms 44 is correct. All governance docs now consistent. CF-002 RESOLVED (2026-06-21): CURRENT_PROJECT_STATUS.md lines 9 and 156 corrected from 43 to 44 — see REMEDIATION_REPORT_2.md CF-002. |

---

## 6. Permissions / RBAC

*Roles, scopes, access control, who can do what.*

| Field | Document |
|---|---|
| **Authority Document** | `backend/docs/security/identity-auth-rbac.md` (Critical) — governs the security model design |
| **Authority Document (Implementation)** | `backend/gateway/config/rbac-scopes.js` — code source of truth for actual granted scopes (not a .md file but is the authoritative implementation reference) |
| **Supporting Documents** | `docs/reports/u-series/ROLE_PERMISSION_INVENTORY.md` (documents what rbac-scopes.js contains), `backend/docs/security/security-model.md`, `backend/docs/security/org-multi-tenancy.md`, `docs/00_authority/DOMAIN_MODEL.md` §Permission entity |
| **Legacy / Competing** | None. ROLE_PERMISSION_INVENTORY.md is a Supporting Reference derived from rbac-scopes.js; identity-auth-rbac.md governs the design model. |
| **Conflict Notes** | H-002 (REMEDIATION_REPORT.md): `contacts.delete` scope is absent from rbac-scopes.js. DOMAIN_MODEL.md §Contact notes this gap. This is a code gap, not a document conflict. The authority documents agree: 91 scopes defined in code; contacts.delete is not one of them; DELETE /contacts returns 403 for all roles. Requires human code fix. |

---

## 7. Workflows

*Business process flows, system workflow triggers, step definitions.*

| Field | Document |
|---|---|
| **Authority Document** | `docs/00_authority/PRODUCT_WORKFLOWS.md` (Critical) — WF-A through WF-E primary workflows |
| **Authority Document (System Workflows)** | `docs/reports/u-series/WORKFLOW_INVENTORY.md` (High) — WF-001 through WF-005 system workflow specs with code evidence |
| **Supporting Documents** | `backend/docs/infrastructure/workflow-dsl.md` (step DSL spec), `backend/docs/infrastructure/event-catalog.md` (events that trigger workflows), `backend/docs/infrastructure/workflow-catalog.md`, `backend/docs/adapters/conversational-action-spec.md` |
| **Legacy / Competing** | Individual domain workflow docs (e.g., `backend/docs/domain/followup-enforcement-model.md`, `backend/docs/domain/collections-engine-model.md`) define domain-specific behavior; they support but do not replace PRODUCT_WORKFLOWS.md. |
| **Conflict Notes** | PRODUCT_WORKFLOWS.md §WF-B previously referenced "POST /invoices" which does not exist as a standalone route (corrected in-document: use POST /invoice-summaries or POST /collections/invoices). This was fixed during U10 remediation. No remaining conflicts. |

---

## 8. Frontend Build

*HTML/CSS/JS build rules, page structure, NexLink patterns, QC tiers.*

| Field | Document |
|---|---|
| **Authority Document** | `FRAMEWORK.md` (Critical) — complete frontend build reference §0–§32 |
| **Authority Document (Session rules)** | `CLAUDE.md` (Critical) — session-level enforcement rules, build checklist, scope gate |
| **Supporting Documents** | `DESIGN-SPEC.md` (page scope), `PAGE-BUILD-PROTOCOL.md`, `backend/docs/ui/read-models.md`, `backend/docs/ui/ui-system.md`, `backend/docs/ui/ui-foundations.md`, `backend/docs/_b9/*.md` (per-archetype specs), `backend/docs/product/adoption-ux.md` |
| **Legacy / Competing** | `docs/archive/FRAMEWORK-GAPS.md` — resolved gaps; Retired. `docs/reports/session/SCREEN-ARTEFACTS.md` — QC records (Supporting); does not govern build rules. |
| **Conflict Notes** | No conflicts. FRAMEWORK.md and CLAUDE.md are complementary: FRAMEWORK.md governs technical build rules; CLAUDE.md governs session behavior rules. CLAUDE.md §MANDATORY references FRAMEWORK.md §31 as authoritative. |

---

## 9. Backend Structure

*Module organization, service patterns, Python/Gateway code layout.*

| Field | Document |
|---|---|
| **Authority Document** | `backend/CONSTRAINTS.md` (Critical) — 17 build constraints |
| **Supporting Documents** | `docs/reports/u-series/MODULE_INVENTORY.md`, `docs/reports/u-series/AUTHORITY_RECONSTRUCTION_REPORT.md` §2, `backend/docs/architecture/architecture-overview.md`, `backend/docs/architecture/service-map.md`, `backend/README.md` |
| **Legacy / Competing** | `docs/reports/u-series/UNDOCUMENTED_CODE_REGISTER.md` (U6 finding register — Supporting); `docs/reports/u-series/BACKEND_DOC_ALIGNMENT_STATUS.md` (tracks alignment status — Supporting) |
| **Conflict Notes** | Module count: FEATURE_SCOPE.md §Overview says "22 user-facing product modules"; AUTHORITY_RECONSTRUCTION_REPORT.md says "30+ backend modules" including infrastructure modules. This is not a conflict — different counting criteria are explained in FEATURE_SCOPE.md. TEST_SUITE_PLAN.md uses 29 modules (fixed by U10). |

---

## 10. Database

*Schema definitions, migration history, data model, naming conventions.*

| Field | Document |
|---|---|
| **Authority Document** | `backend/docs/architecture/data-architecture.md` (High) — CQRS-lite, tenant isolation at DB level, schema naming |
| **Authority Document (Schema inventory)** | `docs/reports/u-series/ENTITY_INVENTORY.md` (High) — 37 entities with fields from code evidence |
| **Supporting Documents** | `docs/00_authority/DOMAIN_MODEL.md` §naming conventions, `backend/db/transaction_db/transaction-policies.md`, `backend/db/*/README.md` |
| **Legacy / Competing** | `backend/docs/architecture/domain-model.md` — Higher-level domain description; defers to data-architecture.md for schema detail |
| **Conflict Notes** | No conflicts. data-architecture.md and DOMAIN_MODEL.md are complementary: data-architecture.md governs physical schema patterns; DOMAIN_MODEL.md governs business entity definitions. |

---

## 11. Testing

*Test strategy, coverage targets, test tooling, test file inventory.*

| Field | Document |
|---|---|
| **Authority Document** | `docs/reports/u-series/TEST_SUITE_PLAN.md` (High) — corrected to 79/23/8 test files by U10 |
| **Supporting Documents** | `docs/reports/u-series/SECURITY_TEST_PLAN.md`, `docs/reports/u-series/LOAD_TEST_PLAN.md`, `docs/reports/u-series/VALIDATION_COMMANDS.md`, `backend/docs/_qc/qc-integration.md`, `backend/docs/_qc/qc-intelligence-data.md`, `docs/08_reports/DOCUMENTATION_COVERAGE_MATRIX.md` |
| **Legacy / Competing** | `tests/e2e/playwright/SKIP-BACKLOG.md` (Operational — active skip list; does not govern strategy) |
| **Conflict Notes** | U0_U9 audit found test count at 54 (wrong); U10 corrected to 79 backend test files. TEST_SUITE_PLAN.md is now accurate. No remaining conflicts. |

---

## 12. Deployment

*Infrastructure, CI/CD, environment configuration, Render.com.*

| Field | Document |
|---|---|
| **Authority Document** | `backend/docs/infrastructure/runtime-deployment.md` (High) — runtime spec, health endpoints, QC gates |
| **Supporting Documents** | `docs/reference/RENDER-DEPLOY.md` (Render-specific how-to), `COMMERCIALISATION-PLAN.md` §C4/§C5 (deployment gate history), `backend/docs/infrastructure/observability-audit.md` |
| **Legacy / Competing** | `docs/archive/deployment-pipelines.md` — Retired; superseded by runtime-deployment.md |
| **Conflict Notes** | No conflicts. render.yaml (code, not a .md) is the implementation authority; runtime-deployment.md and RENDER-DEPLOY.md are the documentation authorities at different levels of detail. |

---

## 13. Governance

*How decisions are made, what requires human approval, what is prohibited.*

| Field | Document |
|---|---|
| **Authority Document** | `docs/07_governance/DECISION_ESCALATION_MATRIX.md` (High) — Tier 1/2/3 classification |
| **Supporting Documents** | `docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md` §7 (Architectural Principles), `CONTRIBUTING.md` |
| **Legacy / Competing** | None. This domain was vacant before Governance Phase 1. |
| **Conflict Notes** | No conflicts. Governance domain is newly established. |

---

## 14. AI Operating Context

*Rules for AI sessions working on this project, frozen decisions, known constraints.*

| Field | Document |
|---|---|
| **Authority Document** | `docs/07_governance/AI_OPERATING_CONTEXT.md` (Critical) |
| **Supporting Documents** | `CLAUDE.md` (session-level rules; subordinate to AI_OPERATING_CONTEXT.md for meta-governance; authority for frontend build), `PAGE-BUILD-PROTOCOL.md` |
| **Legacy / Competing** | `docs/reports/session/SYSTEM-SNAPSHOT.md` — was the pre-governance session orientation document; now stale (C2-era; says C3 is current). AI_OPERATING_CONTEXT.md replaces SYSTEM-SNAPSHOT.md as the authoritative session orientation. |
| **Conflict Notes** | CF-001 RESOLVED (2026-06-21): SYSTEM-SNAPSHOT.md has been updated to redirect to AI_OPERATING_CONTEXT.md and shows C6 as current. AI_OPERATING_CONTEXT.md governs. SESSION-HANDOFF.md has been updated (CF-003) to reference AI_OPERATING_CONTEXT.md as the session opener. |

---

## 15. Decision Records

*Architectural decision history, rationale for key choices.*

| Field | Document |
|---|---|
| **Authority Document** | `docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md` (High) — the single governance ADR |
| **Supporting Documents** | `docs/08_reports/RECOMMENDED_ADR_ROADMAP.md` (5 recommended future ADRs), `backend/docs/adr/ADR-001.md`, `backend/docs/adr/ADR-002.md`, `backend/docs/adr/ADR-003.md` (original source ADRs — now Historical Records) |
| **Legacy / Competing** | backend ADRs — incorporated into ADR-001_PROJECT_FOUNDATION.md; original files retained as Historical Records |
| **Conflict Notes** | No conflicts. ADR-001_PROJECT_FOUNDATION.md explicitly references and supersedes the three original backend ADRs. Recommended ADR-002 through ADR-006 (governance numbering) are not yet authored. |

---

## 16. Risk / Security

*Known risks, CVEs, hardening requirements, security controls.*

| Field | Document |
|---|---|
| **Authority Document** | `backend/docs/security/security-model.md` (High) — threat model, security principles, break-glass procedures |
| **Supporting Documents** | `backend/docs/security/identity-auth-rbac.md`, `backend/docs/security/org-multi-tenancy.md`, `docs/reports/u-series/HARDENING_PLAN.md`, `docs/reports/u-series/SECURITY_TEST_PLAN.md`, `docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md` §6 (Known Risks) |
| **Legacy / Competing** | `docs/archive/gap-register.md` — Retired; specific gaps now in ARCHITECTURAL_GAP_REGISTER.md |
| **Conflict Notes** | H-002 security gap (contacts.delete scope missing) is documented in REMEDIATION_REPORT.md and DOMAIN_MODEL.md. Requires human code fix. HARDENING_PLAN.md documents starlette CVEs as accepted risk. No cross-document conflicts — all documents agree on current risk state. |

---

## 17. Operations

*Commercialisation phases, current project status, session management.*

| Field | Document |
|---|---|
| **Authority Document** | `COMMERCIALISATION-PLAN.md` (Critical) — C0–C6 phase gates; RESUME POINT; session close protocol |
| **Supporting Documents** | `docs/reports/u-series/CURRENT_PROJECT_STATUS.md`, `docs/reports/session/PENDING.md`, `docs/reports/session/PROGRESS.md`, `docs/reports/session/CHANGELOG.md` |
| **Legacy / Competing** | `docs/reports/session/SYSTEM-SNAPSHOT.md` — stale; was pre-governance session anchor; says C3 current (should say C6). `docs/archive/REBUILD-PLAN.md` — Retired; COMMERCIALISATION-PLAN.md is the successor. `docs/reports/session/SESSION-HANDOFF.md` — stale. |
| **Conflict Notes** | CF-001 RESOLVED (2026-06-21): SYSTEM-SNAPSHOT.md has been updated — now shows C6 ← CURRENT, C3/C4/C5 COMPLETE, and redirects to AI_OPERATING_CONTEXT.md. COMMERCIALISATION-PLAN.md confirms C6. No remaining conflict. |

---

## 18. Fullstack Contracts

*Feature-to-code traceability — feature → entity → API → page → permission.*

| Field | Document |
|---|---|
| **Authority Document** | `docs/00_authority/FULLSTACK_STITCHING_CONTRACT.md` (Critical) |
| **Supporting Documents** | `backend/FRONTEND-BACKEND-MAPPING.md`, `docs/reports/u-series/API_INVENTORY.md`, `docs/reports/u-series/ENTITY_INVENTORY.md`, `docs/reports/u-series/MODULE_INVENTORY.md`, `docs/reports/u-series/DOC_CODE_DELTA_REPORT.md`, `docs/reports/u-series/DELTA_SUMMARY_REPORT.md` |
| **Legacy / Competing** | `docs/reports/u-series/BACKEND_DOC_ALIGNMENT_STATUS.md` — tracks alignment status at module level; Supporting, not governing |
| **Conflict Notes** | FULLSTACK_STITCHING_CONTRACT.md contains "TBD – REQUIRES VERIFICATION" sections as noted in GOVERNANCE_CONSISTENCY_AUDIT.md. These are known gaps, not conflicts. Sections 11–22 are lower-detail and defer to API_INVENTORY.md for complete endpoint lists. |

---

## Domain Coverage Assessment

| Domain | Authority Status | Gap |
|---|---|---|
| Project Purpose | CLEAR — PROJECT_CHARTER.md | None |
| Product Scope | CLEAR — FEATURE_SCOPE.md | None |
| Architecture | CLEAR — ADR-001_PROJECT_FOUNDATION.md | 5 recommended ADRs not yet written |
| Domain Model | CLEAR — DOMAIN_MODEL.md | D-003: 5 entity schemas partially unverified |
| API Contracts | SPLIT — api-standards.md (design) + API_INVENTORY.md (inventory) | Both needed; acceptable split |
| Permissions / RBAC | SPLIT — identity-auth-rbac.md (design) + rbac-scopes.js (implementation) | H-002: contacts.delete code gap |
| Workflows | SPLIT — PRODUCT_WORKFLOWS.md (business) + WORKFLOW_INVENTORY.md (system) | Acceptable split; complementary |
| Frontend Build | SPLIT — FRAMEWORK.md (rules) + CLAUDE.md (session) | Intentional split; complementary |
| Backend Structure | CLEAR — CONSTRAINTS.md | D-001/D-002: two modules without gateway routes |
| Database | SPLIT — data-architecture.md (design) + ENTITY_INVENTORY.md (inventory) | D-003: 5 entity schemas partially unverified |
| Testing | CLEAR — TEST_SUITE_PLAN.md | No per-function coverage map |
| Deployment | SPLIT — runtime-deployment.md (spec) + RENDER-DEPLOY.md (how-to) | Acceptable split |
| Governance | CLEAR — DECISION_ESCALATION_MATRIX.md | None |
| AI Operating Context | CLEAR — AI_OPERATING_CONTEXT.md | SYSTEM-SNAPSHOT.md updated 2026-06-21 (CF-001 fix) — now redirects to AI_OPERATING_CONTEXT.md and shows C6 as current |
| Decision Records | CLEAR — ADR-001_PROJECT_FOUNDATION.md | 5 recommended ADRs pending |
| Risk / Security | CLEAR — security-model.md | H-002: contacts.delete code gap |
| Operations | CLEAR — COMMERCIALISATION-PLAN.md | SYSTEM-SNAPSHOT.md updated 2026-06-21 (CF-001 fix) — gap resolved |
| Fullstack Contracts | CLEAR — FULLSTACK_STITCHING_CONTRACT.md | TBD sections for 12 of 22 modules |

---

*End AUTHORITY_MAPPING_MATRIX.md*
