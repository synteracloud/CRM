Status: Draft
Authority Level: Medium
Last Reviewed: 2026-06-21
Owner: Shared

---

# DOCUMENTATION COVERAGE MATRIX — Pakistan CRM OS

## Purpose

This matrix shows the documentation coverage across all key system dimensions. Coverage is assessed against the U0–U10 inventory reports as the source of truth.

**Coverage key:**
- HIGH (>80%): Well documented, few gaps
- MEDIUM (50–80%): Core documented, gaps in edge cases or sub-resources
- LOW (<50%): Significant gaps
- BLOCKED: External dependency prevents completion

---

## Coverage Matrix

| Dimension | Coverage | Source Document(s) | Documented Items | Gaps |
|---|---|---|---|---|
| Backend Modules | HIGH (29/29) | MODULE_INVENTORY.md, AUTHORITY_RECONSTRUCTION_REPORT.md | All 29 modules named with backend paths, gateway routes, frontend pages, entities | 2 modules (contract_lifecycle_management, custom_objects) have no gateway route — human decision pending |
| Domain Entities | HIGH (37/37+) | ENTITY_INVENTORY.md, DOMAIN_MODEL.md | 37 entities with fields, relationships, business rules, CRUD | 5 entities have fields inferred from gateway code, not directly from schema.sql (D-003) |
| API Endpoints | MEDIUM (228/228 total, 20/44 route groups fully detailed) | API_INVENTORY.md, BACKEND_DOC_ALIGNMENT_STATUS.md, FULLSTACK_STITCHING_CONTRACT.md | 228 endpoints counted; 20 route groups ALIGNED (code-verified); 18 PARTIALLY-ALIGNED (approximate counts, no wrong claims) | Detailed per-endpoint docs exist only for ALIGNED groups; PARTIALLY-ALIGNED groups have approximate counts |
| Workflows | HIGH (5/5 system + WF-A through WF-E) | WORKFLOW_INVENTORY.md, PRODUCT_WORKFLOWS.md | 5 system workflows with trigger events, steps, entities, retries; 5 primary business workflows with full stack chain | Automation journeys (src/automation_journeys/) specification is TBD |
| Roles & Permissions | HIGH (7/7 roles, 91/91 scopes) | ROLE_PERMISSION_INVENTORY.md, DOMAIN_MODEL.md | All 7 roles with scope counts; all 91 scopes with granted-to roles; route→scope mapping for ~50 key routes | Some route→scope mappings are not fully documented for PARTIALLY-ALIGNED routes |
| Frontend Pages | HIGH (75/75 custom + 96 NexLink) | CURRENT_PROJECT_STATUS.md, FEATURE_SCOPE.md | All 75 custom pages listed with phase, page ID, file name, build status, DUMMY_MODE | Live-API re-verification pending for 70/75 pages (5 confirmed wired) |
| Tests | MEDIUM (file counts confirmed, coverage not re-run) | TEST_SUITE_PLAN.md, CURRENT_PROJECT_STATUS.md | 79 backend pytest files, 23 Playwright E2E files, 8 API contract files, load + security tests | Individual test function coverage per module not documented; actual pass/fail not re-run during U-series |
| Deployment | HIGH (all layers documented) | CURRENT_PROJECT_STATUS.md, COMMERCIALISATION-PLAN.md §C4 | render.yaml (5 services), ci.yml (11 jobs), Dockerfiles, Alembic migrations | Render.com secrets configuration not in repository (correct — sensitive); deployment runbook exists in COMMERCIALISATION-PLAN.md |
| Integrations | MEDIUM | AUTHORITY_RECONSTRUCTION_REPORT.md §7, FULLSTACK_STITCHING_CONTRACT.md | 4 WhatsApp providers (adapter code confirmed); 2 payment adapters (stub); SendGrid (prod-only); PostgreSQL; Redis | AI inference provider: not selected (D-004); SMS gateway: not implemented; Kuickpay: not implemented (MR-007) |
| Security | MEDIUM | SECURITY_TEST_PLAN.md, HARDENING_PLAN.md | RBAC enforced; tenant isolation CI rule; python-jose 3.5.0 installed; starlette CVEs documented | 3 starlette CVEs accepted risk; no pen test yet; OWASP ZAP reports from C2e/C5 not in repository |
| Database Schemas | HIGH (20/20 domains) | ENTITY_INVENTORY.md, AUTHORITY_RECONSTRUCTION_REPORT.md §3 | All 20 domain schemas named; 12 Alembic migrations documented (0001→0012) | 5 entity schemas inferred from gateway code, not directly verified from schema.sql files |
| Authentication | HIGH (fully documented) | ROLE_PERMISSION_INVENTORY.md, FULLSTACK_STITCHING_CONTRACT.md §8 | JWT (HS256, 15-min/7-day); JTI blocklist in Redis; OTP via SendGrid; registration → tenant seed; scope enforcement | Password hashing algorithm not documented (TBD – REQUIRES VERIFICATION from v1-auth.routes.js) |
| CI/CD Pipeline | HIGH (fully documented) | COMMERCIALISATION-PLAN.md §C4 | 11 GitHub Actions jobs documented; deploy flow (PR→staging→tag→prod); Render deploy hooks | Render webhook secrets not documented (correct — stored in Render only) |
| Architecture Decisions | MEDIUM (3 original ADRs + 1 governance ADR) | backend/docs/adr/ADR-001.md, ADR-002.md, ADR-003.md, docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md | DDD + adapter pattern + WhatsApp-first documented | 5 recommended ADRs not yet written (ADR-002 through ADR-006 in governance numbering) |

---

## Module-Level Coverage Detail

| Module | Backend Doc | Gateway Routes | Frontend Pages | Entities | Status |
|---|---|---|---|---|---|
| Lead Management | ALIGNED | v1-leads, v1-followups | B-01, B-02, C-01, I-01, A-02 | Lead, LeadAssignment, LeadHistory, FollowupTask | HIGH |
| Contacts | ALIGNED | v1-contacts | B-03, C-02, I-02, A-03 | Contact | HIGH |
| Accounts | PARTIALLY-ALIGNED | v1-accounts | B-04, C-03 | Account | MEDIUM |
| Sales / Opportunities | ALIGNED | v1-opportunities | C-04, D-01, A-04, I-03 | Opportunity, OpportunityLineItem | HIGH |
| CPQ / Quotes & Orders | PARTIALLY-ALIGNED | v1-quotes, v1-orders | C-06, I-05, A-05, C-07 | Quote, Order | MEDIUM |
| Finance / Collections | ALIGNED | v1-invoice-summaries, v1-collections, v1-payments, v1-payment-webhooks | B-08, B-09, C-08, H-04 | Invoice, Collection, Payment | HIGH |
| Subscriptions | PARTIALLY-ALIGNED | v1-subscriptions, v1-billing | A-06, C-09, G-04 | Subscription | MEDIUM |
| Support / Cases | ALIGNED | v1-cases | B-05, C-05, E-01, A-07, I-04 | Case, CaseComment, CaseEscalation, SupportQueue | HIGH |
| Knowledge Base | PARTIALLY-ALIGNED | v1-knowledge | C-12, A-09 | KnowledgeArticle | MEDIUM |
| Omnichannel Inbox | ALIGNED | v1-inbox, v1-whatsapp-webhooks | L-01, L-02, L-03, A-08 | Conversation, Message, Handoff, AgentPresence, InboxQueue | HIGH |
| Marketing / Campaigns | ALIGNED | v1-campaigns, v1-segments, v1-emails, v1-templates | F-01, I-06, H-02 | Campaign, Segment | HIGH |
| Workflow Automation | ALIGNED | v1-workflows | K-01, A-10, H-05 | WorkflowDefinition, WorkflowExecution, WorkflowStepRecord | HIGH |
| AI / Copilot | ALIGNED | v1-ai | M-01, M-02 | LeadScore, ChurnPrediction, CLVEstimate, CopilotSuggestion, ScoringModel | HIGH |
| Report Builder | PARTIALLY-ALIGNED | v1-reports | H-01 to H-07 | (none — report execution only) | MEDIUM |
| Territories | ALIGNED | v1-territories | G-09 | Territory, TerritoryRule | HIGH |
| Partners | ALIGNED | v1-partners | B-11, C-11 | Partner | HIGH |
| Identity & Access | ALIGNED | v1-users, v1-roles | B-10, G-02, G-03, A-12 | User, Role, Permission, Session, RefreshToken | HIGH |
| Audit & Compliance | PARTIALLY-ALIGNED | v1-audit, v1-governance, v1-compliance-settings, v1-privacy | J-01 to J-05, A-13 | AuditLog, FeatureFlag | HIGH |
| Settings / Admin | PARTIALLY-ALIGNED | v1-org-settings, v1-integrations, v1-feature-flags-mgmt, v1-notification-preferences | G-01, G-05 to G-08 | (config entities only) | MEDIUM |
| Auth | ALIGNED | v1-auth | authentication/ pages | (identity_auth_db entities) | HIGH |
| Custom Objects | HUMAN-DECISION-REQUIRED | (missing gateway route) | K-02 | (custom object framework entities) | LOW |
| Rule / Approval Builder | PARTIALLY-ALIGNED | (via quotes/orders routes) | K-03, K-04 | (rule_engine entities) | MEDIUM |
| Contract Lifecycle | HUMAN-DECISION-REQUIRED | (no gateway route) | (none) | (contract entities) | LOW |
| External APIs / Plugin | PARTIALLY-ALIGNED | v1-sync | (no UI) | (webhook entities) | LOW |
| Event Bus / Dedup | N/A (internal) | (internal) | (none) | (internal) | MEDIUM — documented in workflow catalog |

---

## Gap Summary

| Gap Category | Count | Severity |
|---|---|---|
| Routes with no gateway exposure (human decisions pending) | 2 (contract_lifecycle, custom_objects) | HIGH |
| Entities with fields inferred (not schema.sql verified) | 5 | MEDIUM |
| Route groups PARTIALLY-ALIGNED (approximate counts) | 18 | MEDIUM |
| AI inference provider not selected | 1 | HIGH |
| Blocked features (external credentials) | 5 (P-016, P-017, MR-001, MR-003, MR-007) | BLOCKED |
| Test pass/fail not re-validated during U-series | All 79+23+8 test files | MEDIUM |
| Security scan reports not in repository | C2e/C5 ZAP + semgrep reports | MEDIUM |
| Recommended ADRs not written | 5 | LOW |
| Password hashing algorithm not documented | 1 | LOW |
| Automation journeys specification incomplete | 1 | LOW |

---

*End DOCUMENTATION_COVERAGE_MATRIX.md*
