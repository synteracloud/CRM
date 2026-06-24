Status: Active
Authority Level: High
Date: 2026-06-21
Scope: Phase 1 Governance Documents
Auditor: AI (independent consistency check)

---

# GOVERNANCE CONSISTENCY AUDIT — Pakistan CRM OS

## Documents Audited

### Primary (7 governance documents)
1. `docs/00_authority/PROJECT_CHARTER.md`
2. `docs/00_authority/FEATURE_SCOPE.md`
3. `docs/00_authority/DOMAIN_MODEL.md`
4. `docs/00_authority/PRODUCT_WORKFLOWS.md`
5. `docs/00_authority/FULLSTACK_STITCHING_CONTRACT.md`
6. `docs/07_governance/AI_OPERATING_CONTEXT.md`
7. `docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md`

### Cross-Reference (U1 ground truth)
- `docs/reports/u-series/AUTHORITY_RECONSTRUCTION_REPORT.md`
- `docs/reports/u-series/API_INVENTORY.md`
- `docs/reports/u-series/ENTITY_INVENTORY.md`
- `docs/reports/u-series/ROLE_PERMISSION_INVENTORY.md`
- `docs/reports/u-series/WORKFLOW_INVENTORY.md`
- `COMMERCIALISATION-PLAN.md`

---

## Executive Summary

**Total issues found: 22**
- Critical: 0
- High: 4
- Medium: 10
- Low: 8

**Recommendation:** Six of seven documents are ready to move from Draft → Active. FULLSTACK_STITCHING_CONTRACT.md requires resolution of 2 High issues before promotion. All seven documents are internally coherent on the major architectural claims and are consistent with U1 ground truth on core facts (tech stack, entity structure, role count, workflow count, phase status).

---

## Critical Issues

No critical issues found. The seven documents do not contradict each other on any fact that would cause a security breach, data loss, or architectural reversal.

---

## High Issues

### H-001 — Gateway Count Discrepancy: 42 vs 43 vs 44 Route Groups

**Issue ID:** H-001
**Documents affected:** FULLSTACK_STITCHING_CONTRACT.md (implicit via source), PROJECT_CHARTER.md, AI_OPERATING_CONTEXT.md, ADR-001_PROJECT_FOUNDATION.md, COMMERCIALISATION-PLAN.md, AUTHORITY_RECONSTRUCTION_REPORT.md, API_INVENTORY.md

**Claim in PROJECT_CHARTER.md (§5 Current Status):**
> "Gateway API routes: 44 route groups, 228 endpoints"

**Claim in AI_OPERATING_CONTEXT.md (CURRENT_PHASE):**
> "44 gateway route groups (228 API endpoints) built"

**Claim in ADR-001_PROJECT_FOUNDATION.md (§2 Current Architecture):**
> "API Gateway (Node.js Express — 44 route groups, 228 endpoints)"

**Claim in COMMERCIALISATION-PLAN.md (Build Phase Carry-Forward State):**
> "Gateway routes: 42 inline routes under `/api/v1/`"

**Claim in AUTHORITY_RECONSTRUCTION_REPORT.md (header note):**
> "Gateway (Node.js Express — 44 API route groups) [corrected from 43 by U10 remediation 2026-06-21]"

**Claim in API_INVENTORY.md (footer):**
> "Current status of all 43 gateway route files: Implemented"

**Analysis:** Three different counts appear across documents — 42 (COMMERCIALISATION-PLAN.md, the oldest reference reflecting pre-U10 state), 43 (API_INVENTORY.md footer, which was not updated after U10 note in its header), and 44 (PROJECT_CHARTER.md, AI_OPERATING_CONTEXT.md, ADR-001, AUTHORITY_RECONSTRUCTION_REPORT.md header). The 44-count appears in the three documents most recently updated (all 2026-06-21) and aligns with the U10 correction note. The 43 in API_INVENTORY.md footer is a stale reference that was not updated when the U10 correction was applied. The 42 in COMMERCIALISATION-PLAN.md reflects the pre-C1 in-memory state from build phase carry-forward.

**Recommended resolution:** The authoritative count is 44 (confirmed in AUTHORITY_RECONSTRUCTION_REPORT.md header, PROJECT_CHARTER.md, and AI_OPERATING_CONTEXT.md). Update API_INVENTORY.md footer from "43" to "44". Note that COMMERCIALISATION-PLAN.md "42" is a historical carry-forward and does not require update — but a footnote clarifying it refers to the pre-C1 baseline would reduce confusion.

---

### H-002 — FULLSTACK_STITCHING_CONTRACT.md: contacts.delete Permission Not in 91-Scope List

**Issue ID:** H-002
**Document A:** FULLSTACK_STITCHING_CONTRACT.md §1 Contact Creation and Management
**Document B:** ROLE_PERMISSION_INVENTORY.md (U1 ground truth)
**Specific claim in A:**
> "contacts.delete — TBD – REQUIRES VERIFICATION (not found in 91-scope list)"

**Specific claim in B (ROLE_PERMISSION_INVENTORY.md):**
> The scope list does not include `contacts.delete` — the contacts section lists only: contacts.read, contacts.create, contacts.update

**However, API_INVENTORY.md §CONTACTS confirms:**
> "DELETE /contacts/:contact_id | JWT | contacts.delete | Hard delete (in-memory path)"

**Analysis:** The API endpoint DELETE /contacts/:id requires `contacts.delete` scope at the gateway level (confirmed in API_INVENTORY.md), but this scope is absent from the 91-scope RBAC definition in ROLE_PERMISSION_INVENTORY.md. This is a genuine gap: either the scope exists in rbac-scopes.js and was missed in the inventory, or the route is currently un-gated (which would be a security gap). The TBD marker in FULLSTACK_STITCHING_CONTRACT.md correctly flags this but the issue remains unresolved. This is the only instance where a required API scope is not in the 91-scope inventory.

**Recommended resolution:** Verify rbac-scopes.js directly. If `contacts.delete` scope exists, add it to ROLE_PERMISSION_INVENTORY.md. If it does not exist, add it to rbac-scopes.js and document who has it (recommended: tenant_owner, tenant_admin only — consistent with leads.delete pattern).

---

### H-003 — PRODUCT_WORKFLOWS.md WF-005 References "Forecast" Entity Not in DOMAIN_MODEL.md

**Issue ID:** H-003
**Document A:** PRODUCT_WORKFLOWS.md WF-005 (Opportunity Stage Change Notification)
**Document B:** DOMAIN_MODEL.md

**Specific claim in A:**
> "Entities involved: Opportunity, User (team), Forecast"

**Claim in B (DOMAIN_MODEL.md):** No `Forecast` entity is defined anywhere in DOMAIN_MODEL.md. The AI domain defines LeadScore, ChurnPrediction, CLVEstimate, CopilotSuggestion, ScoringModel — but no Forecast entity.

**Cross-reference with WORKFLOW_INVENTORY.md (U1):**
> "Entities involved: Opportunity, User (team), Forecast" — same claim, unverified

**Cross-reference with API_INVENTORY.md:**
> `/forecasts` route exists: GET /forecasts (forecasts.read), POST /forecasts/refresh. This is a separate endpoint from the AI scoring routes.

**Analysis:** PRODUCT_WORKFLOWS.md and WORKFLOW_INVENTORY.md both reference a "Forecast" entity, and the API_INVENTORY.md confirms a /forecasts route exists. However, DOMAIN_MODEL.md does not define a Forecast entity — not even as an inferred/partial entity. The `predictive_forecasting` module is referenced in ADR-001 and the stitching contract but no Forecast entity is modelled. This is a gap in DOMAIN_MODEL.md rather than a contradiction, but it means the domain model is incomplete for the WF-005 workflow.

**Recommended resolution:** Add a `Forecast` entity to DOMAIN_MODEL.md under the AI/Intelligence domain or as a separate Forecasting domain, with fields inferred from v1-forecasts.routes.js and the predictive_forecasting module.

---

### H-004 — FULLSTACK_STITCHING_CONTRACT.md Only Covers 10 Features; 21+ Modules Are Undocumented in Stitch Form

**Issue ID:** H-004
**Document A:** FULLSTACK_STITCHING_CONTRACT.md
**Document B:** FEATURE_SCOPE.md (22 modules, 131+ features)

**Specific claim in A (§Purpose):**
> "This document traces each major feature through every layer of the stack"

**Reality check against FEATURE_SCOPE.md:** FEATURE_SCOPE.md defines 22 modules. FULLSTACK_STITCHING_CONTRACT.md covers only 10 of them (Contact, Lead, Deal Pipeline, Invoice/Payment, Case, WhatsApp Conversation, AI, Auth, Multi-tenant, Workflow). The following 12+ modules have no stitch entry:
- Module 3 Contacts (partially covered via Contact Creation)
- Module 4 Accounts (no dedicated stitch entry)
- Module 10 Knowledge Base (no stitch entry)
- Module 12 Marketing/Campaigns (no stitch entry)
- Module 15 Report Builder (no stitch entry)
- Module 16 Territories (no stitch entry)
- Module 17 Partners (no stitch entry)
- Module 18 Identity/IAM (partially covered via Auth)
- Module 19 Audit & Compliance (no stitch entry)
- Module 20 Settings/Administration (no stitch entry)
- Module 22 Builder Tools (no stitch entry)
- Module 8 Subscriptions/Billing (partially covered under Invoice)

**Analysis:** The stitching contract covers the highest-traffic core workflows well but does not achieve the stated goal of tracing "each major feature." The gap is significant for compliance, audit, territory, campaign, and settings modules — all of which have confirmed API routes, entities, and frontend pages.

**Recommended resolution:** Add stitch entries for the missing modules, or explicitly state in the document's scope that it covers only the 10 primary workflows and that remaining modules are documented via API_INVENTORY.md + ENTITY_INVENTORY.md.

---

## Medium Issues

### M-001 — Leads API: FULLSTACK_STITCHING_CONTRACT.md Lists 13 Endpoints; API_INVENTORY.md Counts 8

**Issue ID:** M-001
**Document A:** FULLSTACK_STITCHING_CONTRACT.md §2 (Lead Capture and Qualification)
**Document B:** API_INVENTORY.md §LEADS and §FOLLOW-UPS

**Specific claim in A:** Lists the following as "Leads" endpoints: GET /leads, POST /leads, GET /leads/:id, PATCH /leads/:id, DELETE /leads/:id, GET /leads/export, POST /leads/import, GET /leads/:id/next-action, GET /followups, POST /followups, POST /followups/:id/complete, POST /followups/:id/snooze, GET /followups/lead/:id/canonical (13 routes total)

**Specific claim in B:** API_INVENTORY.md §LEADS lists 8 endpoints; §FOLLOW-UPS lists 6 separate endpoints.

**Analysis:** This is not a contradiction — FULLSTACK_STITCHING_CONTRACT.md legitimately groups follow-up endpoints under the Lead feature since they are part of the same workflow. However, the combined count (13) differs from either individual section count (8 leads + 6 followups = 14). The discrepancy of 1 is likely because `GET /followups/:task_id` (follow-up task detail) appears in API_INVENTORY.md but is not listed in the stitching contract. This is a minor gap in the stitching contract, not a factual error.

**Recommended resolution:** Add `GET /followups/:task_id` to the stitching contract endpoint list for completeness.

---

### M-002 — Invoice API Path Inconsistency: /invoices vs /invoice-summaries vs /collections/invoices

**Issue ID:** M-002
**Document A:** PRODUCT_WORKFLOWS.md WF-B (Deal-to-Invoice) and WF-E (Payment Collection)
**Document B:** API_INVENTORY.md §COLLECTIONS and §INVOICE-SUMMARIES
**Document C:** FULLSTACK_STITCHING_CONTRACT.md §4

**Claim in PRODUCT_WORKFLOWS.md WF-B:**
> "POST /invoices creates Invoice linked to Account" and "GET /invoice-summaries"

**Claim in API_INVENTORY.md §COLLECTIONS:**
> POST /collections/invoices (scope: collections.invoice); GET /collections/invoices; GET /collections/invoices/:invoice_id

**Claim in API_INVENTORY.md §INVOICE-SUMMARIES:**
> GET /invoice-summaries; GET /invoice-summaries/:invoice_id; POST /invoice-summaries (scope: invoices.create)

**Claim in FULLSTACK_STITCHING_CONTRACT.md §4:**
> Lists `POST /invoices` as an endpoint but also references `/invoice-summaries` and `/collections`

**Analysis:** Three separate route patterns exist for invoice-related operations: `/invoices` (referenced in PRODUCT_WORKFLOWS.md and PROJECT_CHARTER.md), `/invoice-summaries` (in API_INVENTORY.md), and `/collections/invoices` (in API_INVENTORY.md as the collections sub-path). It is unclear from the governance documents which path is canonical for invoice creation. API_INVENTORY.md shows both `/invoice-summaries` (POST creates invoice) and `/collections/invoices` (POST creates invoice via collections scope) as active routes. PRODUCT_WORKFLOWS.md uses `/invoices` which does not appear as a distinct route in API_INVENTORY.md. FULLSTACK_STITCHING_CONTRACT.md uses all three.

**Recommended resolution:** Clarify in PRODUCT_WORKFLOWS.md whether `POST /invoices` is an alias for `POST /invoice-summaries` or whether it refers to the `/collections/invoices` path. The distinction matters because the two paths use different permission scopes (`invoices.create` vs `collections.invoice`).

---

### M-003 — ADR-001 References "ADR-002 (governance)" and "ADR-003 (governance)" But These Share Numbers with Original ADRs

**Issue ID:** M-003
**Document:** ADR-001_PROJECT_FOUNDATION.md §8 (Relationship to Other ADRs)

**Specific claim:**
> "ADR-002 (governance): Multi-tenancy isolation strategy — Recommended"
> "ADR-003 (governance): AI inference model selection — Recommended"
> "ADR-002 (original): Adapter Pattern — Accepted"
> "ADR-003 (original): WhatsApp-First Model — Accepted"

**Analysis:** ADR-001_PROJECT_FOUNDATION.md incorporates the original ADR-001, ADR-002, and ADR-003 from `backend/docs/adr/`. It then refers to new governance ADRs also numbered ADR-002 and ADR-003. This creates a numbering collision: "ADR-002" simultaneously means "Adapter Pattern (original, Accepted)" and "Multi-tenancy isolation strategy (governance, Recommended)." The RECOMMENDED_ADR_ROADMAP.md (confirmed to exist in docs/08_reports/) presumably documents the new ADR numbering, but the collision within this single document creates ambiguity.

**Recommended resolution:** Renumber the governance-recommended ADRs as ADR-006, ADR-007, ADR-008, ADR-009 (continuing from the last original ADR) rather than reusing ADR-002/ADR-003 designations. Update the §8 table accordingly.

---

### M-004 — PRODUCT_WORKFLOWS.md WF-D Lists /whatsapp-webhooks/dialog360 But API_INVENTORY.md Uses /whatsapp-webhooks/360dialog

**Issue ID:** M-004
**Document A:** PRODUCT_WORKFLOWS.md WF-D (WhatsApp Conversation Workflow)
**Document B:** API_INVENTORY.md §WhatsApp Webhooks

**Specific claim in A:**
> "POST /whatsapp-webhooks/dialog360"

**Specific claim in B:**
> "POST /whatsapp-webhooks/360dialog | Webhook signature | 360dialog inbound WhatsApp messages"

**Analysis:** PRODUCT_WORKFLOWS.md consistently uses `dialog360` as the path segment while API_INVENTORY.md uses `360dialog`. These are slightly different strings (`dialog360` vs `360dialog`) and at least one is incorrect. The provider is known as "360dialog" (the company name); `360dialog` in the API path matches the provider brand convention. The gateway adapter is named `dialog360_adapter.py` (reversed) in the code. ADR-001 lists it as "360dialog" in the adapter table.

**Recommended resolution:** Standardize on the path `/whatsapp-webhooks/360dialog` (matching API_INVENTORY.md and ADR-001's adapter table) and correct PRODUCT_WORKFLOWS.md WF-D to use `360dialog`.

---

### M-005 — DOMAIN_MODEL.md Counts "37+" Entities But ENTITY_INVENTORY.md Counts "30 confirmed"

**Issue ID:** M-005
**Document A:** DOMAIN_MODEL.md (Overview)
**Document B:** ENTITY_INVENTORY.md (header) and AUTHORITY_RECONSTRUCTION_REPORT.md §3

**Specific claim in A:**
> "Pakistan CRM OS has 20 database domains (PostgreSQL schemas) containing 37+ confirmed entities."

**Specific claim in B (ENTITY_INVENTORY.md header):**
> (no explicit count stated in header — but AUTHORITY_RECONSTRUCTION_REPORT.md §3 states: "30 confirmed entities across 20 database domains")

**Analysis:** DOMAIN_MODEL.md claims "37+" entities while AUTHORITY_RECONSTRUCTION_REPORT.md §3 claims "30 confirmed entities." Counting entities in ENTITY_INVENTORY.md directly: User, Role, Permission, Session, RefreshToken (5), Tenant (1), Lead, LeadAssignment, LeadHistory (3), FollowupTask (1), Contact, Account (2), Opportunity, OpportunityLineItem (2), Quote, Order (2), Invoice, Subscription, Payment, Collection (4), Case, CaseComment, CaseEscalation, SupportQueue (4), Conversation, Message, Handoff, AgentPresence, InboxQueue (5), WorkflowDefinition, WorkflowExecution, WorkflowStepRecord (3), LeadScore, ChurnPrediction, CLVEstimate, CopilotSuggestion, ScoringModel (5), Campaign, Segment (2), KnowledgeArticle (1), Territory, TerritoryRule (2), Partner (1), AuditLog, FeatureFlag (2), Activity, Task (2) = 50 named entries. However, some of these (LeadScore, ChurnPrediction, CLVEstimate) appear both as direct AI domain entries and as Account child entities, causing double-counting. The "30 confirmed" in AUTHORITY_RECONSTRUCTION_REPORT.md likely reflects entities with confirmed DB schema evidence; the "37+" in DOMAIN_MODEL.md includes all entities including those inferred from gateway code. Neither count is wrong but they need reconciliation.

**Recommended resolution:** Update DOMAIN_MODEL.md to clarify: "37+ entities (30 with confirmed db/*/schema.sql evidence; 7+ inferred from gateway code — see D-003 in AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS)."

---

### M-006 — FEATURE_SCOPE.md "Total features inventoried: 131" But Lists Modules Non-Sequentially (Jumps from Module 6 to Module 18)

**Issue ID:** M-006
**Document:** FEATURE_SCOPE.md

**Specific claim in A:**
> "Total features inventoried: 131 (features 1–131 in FEATURE_INVENTORY.md + 15 undocumented features U-01–U-15)"

**Observation:** FEATURE_SCOPE.md lists modules 1–6 (Groups A's first six), then jumps to Module 18 (Identity & Access), Module 21 (Auth), Module 7 (Finance), Module 8 (Subscriptions), Module 9 (Support), Module 10 (Knowledge), Module 16 (Territories), Module 17 (Partners), then Group C (Modules 11–15), then Group D (Modules 19, 20, 22). Modules not explicitly listed include: Module 3 (Contacts — listed as features 17–22 under Group A), Module 4 (Accounts — listed as features 23–24). All 22 modules do appear to be covered by the feature numbering (1–131) but the grouping within FEATURE_SCOPE.md does not follow sequential module numbering, making it difficult to verify the 131-feature count from this document alone without access to FEATURE_INVENTORY.md.

**Specific concern:** FEATURE_SCOPE.md claims the feature count comes from "FEATURE_INVENTORY.md (U1)" but FEATURE_INVENTORY.md does not appear in the 13 cross-reference documents provided for this audit and was not read. The total cannot be independently verified.

**Recommended resolution:** Include a cross-reference table in FEATURE_SCOPE.md mapping the 131 feature numbers to module groups for independent verification. Alternatively, embed the full sequential feature list or confirm FEATURE_INVENTORY.md is accessible.

---

### M-007 — PRODUCT_WORKFLOWS.md Lists "5 system workflows" but WF-A through WF-E Are Business Workflows, Not System Workflows

**Issue ID:** M-007
**Document:** PRODUCT_WORKFLOWS.md

**Potential confusion:** PRODUCT_WORKFLOWS.md defines two distinct sets:
1. "Primary Business Workflows": WF-A (Lead-to-Deal), WF-B (Deal-to-Invoice), WF-C (Case Lifecycle), WF-D (WhatsApp Conversation), WF-E (Payment Collection) — these are end-to-end user journeys
2. "System Workflows": WF-001 through WF-005 (seeded, is_system=true, non-editable)

**Cross-reference concern:** PROJECT_CHARTER.md §4 (In-Scope) states:
> "Workflow automation engine (event-driven, 5 system workflows + custom)"

AI_OPERATING_CONTEXT.md ACTIVE_AUTHORITY_DOCS states:
> "PRODUCT_WORKFLOWS.md: 5 primary workflows, 5 system workflows, events"

The phrasing "5 primary workflows" (WF-A to WF-E) vs "5 system workflows" (WF-001 to WF-005) correctly distinguishes them, but PROJECT_CHARTER.md only references "5 system workflows" without mentioning the 5 business workflow archetypes, which might suggest the business workflows are not tracked there.

**This is not a factual error** — the numbers are consistent (both say 5 system workflows). However, the naming could mislead a reader into conflating the two sets.

**Recommended resolution:** PRODUCT_WORKFLOWS.md is clear in its structure. No document change required, but a note in PROJECT_CHARTER.md §4 distinguishing "5 system workflows (WF-001 to WF-005, is_system=true)" from "5 business workflow archetypes (WF-A to WF-E, documentation only)" would prevent ambiguity.

---

### M-008 — FULLSTACK_STITCHING_CONTRACT.md §8 Auth: Password Hashing Algorithm Marked TBD

**Issue ID:** M-008
**Document:** FULLSTACK_STITCHING_CONTRACT.md §8 (User Authentication and RBAC)

**Specific claim:**
> "Password: hashed (algorithm TBD – REQUIRES VERIFICATION from v1-auth.routes.js)"

**Cross-reference with API_INVENTORY.md §AUTH:**
> "Password: sha256:salt:hash" (stated as a fact, not TBD)

**Analysis:** API_INVENTORY.md (U1 ground truth) explicitly identifies the password hashing scheme as `sha256:salt:hash` based on direct code read. FULLSTACK_STITCHING_CONTRACT.md marks this as TBD. This is a stale TBD that was resolved in U1 but not propagated to the stitching contract.

**Recommended resolution:** Update FULLSTACK_STITCHING_CONTRACT.md §8 to state: "Password: sha256:salt:hash (confirmed from v1-auth.routes.js — see API_INVENTORY.md §AUTH)."

---

### M-009 — Territory Criteria Types Differ Between DOMAIN_MODEL.md and API_INVENTORY.md

**Issue ID:** M-009
**Document A:** DOMAIN_MODEL.md Territory entity
**Document B:** API_INVENTORY.md §TERRITORIES
**Document C:** ENTITY_INVENTORY.md Territory entity

**Specific claim in DOMAIN_MODEL.md:**
> "criteria_type (geography/industry/account_size/custom)"

**Specific claim in API_INVENTORY.md (POST /territories):**
> "Required: criteria_type (geographic/postal/account_segment/rep_assigned/hybrid)"

**Specific claim in ENTITY_INVENTORY.md:**
> "criteria_type (geography/industry/account_size/custom)"

**Analysis:** The allowed values for `criteria_type` differ:
- DOMAIN_MODEL.md and ENTITY_INVENTORY.md: geography, industry, account_size, custom
- API_INVENTORY.md (from gateway code): geographic, postal, account_segment, rep_assigned, hybrid

These are two different sets of enum values, neither of which is a subset of the other. The API_INVENTORY.md values are from direct gateway code read and are therefore more likely to be the runtime reality. The DOMAIN_MODEL.md values appear to be the conceptual design values.

**Recommended resolution:** Verify which values are enforced in the schema.sql for territory_db and update DOMAIN_MODEL.md and ENTITY_INVENTORY.md to match. The runtime-enforced values (from the gateway) are: geographic, postal, account_segment, rep_assigned, hybrid.

---

### M-010 — WF-002 (Collections Reminder) Entity List Omits WorkflowExecution in PRODUCT_WORKFLOWS.md

**Issue ID:** M-010
**Document A:** PRODUCT_WORKFLOWS.md §System Workflows WF-002
**Document B:** PRODUCT_WORKFLOWS.md WF-E (Payment Collection Workflow)

**Specific claim in WF-002 system workflow:**
> "Entities involved: Invoice, Contact, Payment"

**Specific claim in WF-E (which references WF-002):**
> "Entities involved: Invoice, Collection, Contact, Payment, WorkflowExecution, AuditLog"

**Analysis:** The system workflow definition (WF-002) omits WorkflowExecution and AuditLog from its entity list, while the business workflow (WF-E) that uses WF-002 includes them. Since every workflow execution creates a WorkflowExecution record (this is how the workflow engine works as described in DOMAIN_MODEL.md), the WF-002 entity list is incomplete. This is an internal inconsistency within PRODUCT_WORKFLOWS.md.

**Recommended resolution:** Update WF-002 system workflow entity list to add WorkflowExecution (and optionally AuditLog, since WF-003 explicitly includes AuditLog as part of its steps).

---

## Low Issues

### L-001 — PROJECT_CHARTER.md §7 Uses "TBD" for Platform Billing Model

**Issue ID:** L-001
**Document:** PROJECT_CHARTER.md §7 (Commercial Model)

**Specific claim:**
> "Payment collection from customers: TBD — JazzCash/Easypaisa adapters built for customer payment workflows; platform billing model TBD — REQUIRES VERIFICATION from pricing-plans.md"

**Analysis:** This is a correctly marked TBD, not a contradiction. It accurately reflects that the platform's own billing model (how the SaaS collects from its tenant customers) is separate from the in-app payment processing (how tenants collect from their customers). The distinction is appropriate and the TBD is intentional.

**Status:** No resolution required. TBD is legitimate and correctly scoped.

---

### L-002 — "5 pages confirmed wired" Stated in Three Documents with Slightly Different Lists

**Issue ID:** L-002
**Document A:** PROJECT_CHARTER.md §5
**Document B:** AI_OPERATING_CONTEXT.md (CURRENT_PHASE / DUMMY_MODE status)
**Document C:** FULLSTACK_STITCHING_CONTRACT.md (various sections)

**Claim in PROJECT_CHARTER.md §5:**
> "Frontend-to-API wiring: 5 pages confirmed wired; remainder use DUMMY_MODE graceful fallback"

**Claim in AI_OPERATING_CONTEXT.md (DUMMY_MODE section):**
> "Pages that confirmed wired to live API: integrations.html (G-05), report-builder.html (H-07), data-governance.html (J-03), engagement-dashboard.html (A-08), billing-settings.html (G-04 wired but content blocked by P-016)"

**Claim in FULLSTACK_STITCHING_CONTRACT.md §6:**
> "E2E: engagement-dashboard.html (A-08) is confirmed wired to live API"

**Analysis:** The list of 5 wired pages is consistent between PROJECT_CHARTER.md and AI_OPERATING_CONTEXT.md (5 pages named). FULLSTACK_STITCHING_CONTRACT.md mentions only A-08 explicitly in its test coverage section for WhatsApp Conversation, which is not inconsistent — it just doesn't repeat the full list. No contradiction exists, but the wired page list is only complete in AI_OPERATING_CONTEXT.md.

**Recommended resolution:** No change required. AI_OPERATING_CONTEXT.md is the canonical location for DUMMY_MODE status per its own CONTRACT_COMPATIBILITY_POLICY section.

---

### L-003 — ADR-001 §4 PTA/FBR Compliance Claims Marked TBD

**Issue ID:** L-003
**Document:** ADR-001_PROJECT_FOUNDATION.md §4 (Known Constraints)

**Specific claims:**
> "PTA compliance: Compliance adapter hooks are built but details pending legal review (TBD – REQUIRES VERIFICATION from backend/docs/adapters/compliance-adapter.md)"
> "FBR (tax) compliance: Federal Board of Revenue requirements for invoice formatting. Details pending verification (TBD – REQUIRES VERIFICATION)"

**Cross-reference:** Neither FEATURE_SCOPE.md nor DOMAIN_MODEL.md mentions PTA or FBR compliance as distinct features. AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS does not list PTA or FBR as active constraints (only P-016, P-017, MR-001, MR-003, MR-007, AI-001, D-001, D-002, D-003, starlette CVEs).

**Analysis:** PTA and FBR compliance are mentioned only in ADR-001 and are both marked TBD. They do not appear in the scope or constraint lists of any other governance document. This is a gap in scope coverage — if these are real regulatory requirements, they should appear in PROJECT_CHARTER.md (Out of Scope or Deferred) or AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS.

**Recommended resolution:** Either add PTA and FBR compliance as KNOWN_CONSTRAINTS in AI_OPERATING_CONTEXT.md, or confirm they are out of scope for v1 and document that decision in PROJECT_CHARTER.md §4 (Explicitly Out of Scope).

---

### L-004 — FEATURE_SCOPE.md Groups "Module 11: Omnichannel Inbox" Under "GROUP C — AI & Analytics" (Mislabeled Group)

**Issue ID:** L-004
**Document:** FEATURE_SCOPE.md

**Observation:** FEATURE_SCOPE.md places Module 11 (Omnichannel Inbox), Module 12 (Marketing/Campaigns), Module 13 (Workflow Automation), Module 14 (AI/Copilot), and Module 15 (Report Builder) under the heading "GROUP C — AI & Analytics." However, Omnichannel Inbox, Marketing/Campaigns, and Workflow Automation are not AI or analytics functions. They are operational CRM modules.

**Analysis:** This is a naming/organization issue rather than a factual error. No other document uses this grouping; it exists only in FEATURE_SCOPE.md for organizational purposes. The module-level content is correct.

**Recommended resolution:** Rename "GROUP C — AI & Analytics" to "GROUP C — Automation, Engagement & Intelligence" to accurately reflect its contents.

---

### L-005 — DOMAIN_MODEL.md Aggregate Boundaries Table Places ChurnPrediction Under Both Account and AI Aggregates

**Issue ID:** L-005
**Document:** DOMAIN_MODEL.md §Aggregate Boundaries

**Specific claim in Aggregate Boundaries table:**
> "Account | Account, ChurnPrediction, CLVEstimate"
> "AI | LeadScore, ChurnPrediction, CLVEstimate, CopilotSuggestion, ScoringModel"

**Analysis:** ChurnPrediction and CLVEstimate appear in both the Account aggregate and the AI aggregate. In DDD terms, an entity belongs to exactly one aggregate. This is a modelling inconsistency: ChurnPrediction and CLVEstimate are computed for an Account (Account is their natural root for lookup) but they are owned by the intelligence_db schema (suggesting AI is their physical aggregate root). The entity relationship map correctly shows them under both Account and AI domain, which is acceptable for a relationship map — but the aggregate table should reflect the authoritative boundary.

**Recommended resolution:** Clarify ownership: if ChurnPrediction and CLVEstimate are managed via /ai/predictions and /ai/estimates endpoints (confirmed in API_INVENTORY.md), their aggregate root is AI (intelligence_db). Remove them from the Account aggregate row and add a note: "Account→ChurnPrediction and Account→CLVEstimate are lookup relationships; AI is the owning aggregate."

---

### L-006 — PRODUCT_WORKFLOWS.md WF-B References POST /orders But API_INVENTORY.md Shows /orders as a Separate Route from /collections/invoices

**Issue ID:** L-006
**Document A:** PRODUCT_WORKFLOWS.md WF-B (Deal-to-Invoice) Step 1
**Document B:** API_INVENTORY.md §ORDERS

**Specific claim in A:**
> "POST /orders (from accepted Quote)"

**Cross-reference B:** API_INVENTORY.md §ORDERS shows POST /orders is a valid route with `orders.create` scope. This is consistent. However, PRODUCT_WORKFLOWS.md WF-B also references `POST /invoices` in step 2, which (as noted in M-002) may map to `/invoice-summaries` or `/collections/invoices`.

**Analysis:** The `/orders` reference is consistent. This issue is subsidiary to M-002 and documents that the WF-B invoice endpoint ambiguity affects step 2 only, not step 1.

**Status:** Subsidiary to M-002. Resolve M-002 to close this item.

---

### L-007 — AUTHORITY_RECONSTRUCTION_REPORT.md Module Count Differs from FEATURE_SCOPE.md

**Issue ID:** L-007
**Document A:** AUTHORITY_RECONSTRUCTION_REPORT.md §2 Module Inventory
**Document B:** FEATURE_SCOPE.md (22 modules)

**Claim in AUTHORITY_RECONSTRUCTION_REPORT.md §2:** Lists 30 rows in the module inventory table (including Email, Price Books, Tenants, Communication Integrations, External APIs, Event Bus, Auth as separate rows).

**Claim in FEATURE_SCOPE.md:** 22 explicitly numbered modules (Modules 1–22, with gaps in Module 13 labeling for Workflow Automation = Module 13, AI = Module 14, Reports = Module 15, Territories = Module 16, Partners = Module 17, IAM = Module 18, Audit = Module 19, Settings = Module 20, Auth = Module 21, Builder Tools = Module 22).

**Analysis:** The count difference is explained by AUTHORITY_RECONSTRUCTION_REPORT.md including backend-only modules (External APIs, Event Bus, Email, Price Books) that are not user-facing features and therefore not in FEATURE_SCOPE.md's 22-module count. This is not a contradiction but a scope difference: FEATURE_SCOPE.md counts user-facing product modules; AUTHORITY_RECONSTRUCTION_REPORT.md counts all backend modules including infrastructure modules.

**No resolution required.** A note in FEATURE_SCOPE.md clarifying "22 product feature modules; additional infrastructure modules (Email, Price Books, Event Bus, External APIs) are implementation-level and not counted in the feature scope" would prevent confusion.

---

### L-008 — AI_OPERATING_CONTEXT.md Lists 5 Render.com Services But ADR-001 and PROJECT_CHARTER.md List 3

**Issue ID:** L-008
**Document A:** AI_OPERATING_CONTEXT.md (CURRENT_PHASE — "5 services live on Render.com")
**Document B:** PROJECT_CHARTER.md §5 ("Deployment: Render.com — 3 services + PostgreSQL + Redis live")
**Document C:** ADR-001_PROJECT_FOUNDATION.md §2 ("3 services (gateway, services, frontend) + managed PostgreSQL + Redis")

**Specific claim in A:**
> "5 services live on Render.com (gateway + services + frontend + PostgreSQL + Redis)"

**Specific claim in B:**
> "3 services + PostgreSQL + Redis" (PROJECT_CHARTER.md)
> "3 services (gateway, services, frontend) + managed PostgreSQL + Redis" (ADR-001)

**Analysis:** This is a naming/counting difference, not a contradiction. AI_OPERATING_CONTEXT.md counts all 5 Render entities as "services" (including the managed PostgreSQL and Redis). PROJECT_CHARTER.md and ADR-001 distinguish between 3 application services (gateway, services, frontend) and 2 managed data services (PostgreSQL, Redis). Both descriptions are accurate; the difference is definitional.

**Recommended resolution:** Standardize language: "3 application services (gateway + services + frontend) + 2 managed data services (PostgreSQL + Redis) = 5 Render entities total." All three documents should use the same formulation.

---

## Documents Ready for Draft → Active

### PROJECT_CHARTER.md — READY FOR ACTIVE

**Justification:**
1. No critical or high issues affecting this document directly (H-001 touches it but the correct count is stated here)
2. All sections contain substantive content; no empty sections
3. Consistent with U1 ground truth on all verified claims: 7 roles, 91 scopes, 44 route groups (stated correctly), 228 endpoints, 34 FastAPI modules, 20 schemas, 75/75 pages, C6 phase
4. TBD items are explicitly marked (§7 commercial model, §8 success metrics)
5. Frozen decisions table matches AI_OPERATING_CONTEXT.md FROZEN_DECISIONS table

**Condition:** No conditions. Ready to promote.

---

### FEATURE_SCOPE.md — READY FOR ACTIVE (with minor annotation)

**Justification:**
1. No high issues affecting this document
2. Module list is consistent with AUTHORITY_RECONSTRUCTION_REPORT.md §2 (22 user-facing modules confirmed)
3. Phase gate mapping (C0–C6) is consistent with COMMERCIALISATION-PLAN.md phase table
4. Feature statuses (Built/Wired/Blocked) are consistent with U1 findings
5. Blocked items (P-016, P-017, MR-001, MR-003, MR-007) match PROJECT_CHARTER.md and AI_OPERATING_CONTEXT.md

**Condition:** Resolve L-004 (mislabeled group heading "GROUP C — AI & Analytics") before promotion. This is cosmetic but improves document authority.

---

### DOMAIN_MODEL.md — READY FOR ACTIVE (with one open item)

**Justification:**
1. No high issues directly affecting this document (H-003 is a gap, not an error in DOMAIN_MODEL.md itself)
2. Entity descriptions and field lists are consistent with ENTITY_INVENTORY.md for all 30 confirmed entities
3. Key business rules (OCC, soft delete, canonical follow-up, SLA tiers, 14-day reopen, dual approval) match code evidence in API_INVENTORY.md
4. Aggregate boundaries are internally consistent except for the ChurnPrediction/CLVEstimate overlap (L-005)
5. Naming conventions table is authoritative and complete

**Conditions:**
1. Resolve H-003: Add Forecast entity to the domain model
2. Resolve M-005: Clarify "37+ entities" vs "30 confirmed" with a parenthetical note
3. Resolve L-005: Fix aggregate boundary for ChurnPrediction/CLVEstimate
4. Resolve M-009: Update Territory criteria_type enum values to match runtime values

**Recommendation:** Promote after resolving H-003 and M-005 (the H-003 entity gap is the most substantive open item).

---

### PRODUCT_WORKFLOWS.md — READY FOR ACTIVE (with minor corrections)

**Justification:**
1. No high issues directly affecting this document
2. 5 system workflows (WF-001 to WF-005) are consistent with WORKFLOW_INVENTORY.md on all key fields: trigger events, workflow_keys, max_retries, entities involved
3. Business workflow archetypes (WF-A to WF-E) are consistent with FULLSTACK_STITCHING_CONTRACT.md workflows
4. System events catalog matches WORKFLOW_INVENTORY.md event catalog exactly
5. API endpoints cited in workflows match API_INVENTORY.md (with the exception of M-004 webhook path and M-002 invoice path)

**Conditions:**
1. Resolve M-004: Correct `/whatsapp-webhooks/dialog360` → `/whatsapp-webhooks/360dialog`
2. Resolve M-010: Add WorkflowExecution to WF-002 entity list

**Recommendation:** Promote after M-004 correction. These are cosmetic fixes.

---

### FULLSTACK_STITCHING_CONTRACT.md — NOT READY FOR ACTIVE

**Justification for holding:**
1. H-002 (contacts.delete scope gap) is unresolved and represents a potential security gap
2. H-004 (coverage gap — 12+ modules undocumented) means the document does not fulfill its stated purpose of tracing "each major feature"
3. Multiple TBD items remain open (M-008 password hash, backend test coverage for several modules)
4. While the 10 documented stitches are accurate, the incomplete coverage makes "Active" status premature for a document claiming comprehensive traceability

**Conditions to promote:**
1. Resolve H-002: Verify and document contacts.delete scope
2. Either resolve H-004 (add missing module stitches) OR update the document scope statement to explicitly limit coverage to "10 primary workflows"
3. Resolve M-008 (password hash TBD → sha256:salt:hash)
4. Resolve remaining TBD items or convert them to documented open questions

**Recommendation:** This document should remain Draft until H-002 and H-004 are resolved. Target: add at least the scope statement update (H-004 option B) and H-002 verification before promoting to Active.

---

### AI_OPERATING_CONTEXT.md — READY FOR ACTIVE

**Justification:**
1. No high issues directly affecting this document
2. FROZEN_DECISIONS table matches PROJECT_CHARTER.md §9 on all 13 frozen items
3. KNOWN_CONSTRAINTS match COMMERCIALISATION-PLAN.md Permanently Blocked Items and AI constraints (AI-001, D-001, D-002, D-003 are appropriately documented)
4. CURRENT_PHASE matches COMMERCIALISATION-PLAN.md RESUME POINT table (C6, dates consistent)
5. ACTIVE_AUTHORITY_DOCS list is complete and accurate for all 7 governance documents plus supporting references
6. DUMMY_MODE status (5 wired pages named) is consistent with PROJECT_CHARTER.md §5
7. REQUIRED_VALIDATIONS are actionable and reference real commands/thresholds

**Condition:** Resolve L-008 (3 vs 5 Render services language) — cosmetic. Ready to promote regardless.

---

### ADR-001_PROJECT_FOUNDATION.md — READY FOR ACTIVE (with ADR numbering fix)

**Justification:**
1. No high issues directly affecting this document
2. Technology choices (FastAPI/Express/PostgreSQL/Redis/NexLink/JWT/Render.com) are consistent with AI_OPERATING_CONTEXT.md FROZEN_DECISIONS and PROJECT_CHARTER.md §9
3. Adapter list (Meta, Gupshup, Dialog360, Twilio for WhatsApp; JazzCash, Easypaisa for payments) matches AUTHORITY_RECONSTRUCTION_REPORT.md §7
4. Application-level tenancy trade-off discussion is accurate and matches code evidence
5. Known risks (starlette CVEs, payment stub mode, no AI inference) match AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS

**Conditions:**
1. Resolve M-003: Renumber governance ADRs to avoid numbering collision with original ADRs

**Recommendation:** Promote after M-003 renumbering fix.

---

## TBD Items Inventory

All "TBD – REQUIRES VERIFICATION" markers found across the 7 governance documents:

| # | Document | Section | What Needs Verification |
|---|---|---|---|
| TBD-001 | FULLSTACK_STITCHING_CONTRACT.md | §1 Contact permissions | contacts.delete scope — verify it exists in rbac-scopes.js and document which roles have it |
| TBD-002 | FULLSTACK_STITCHING_CONTRACT.md | §1 Contact validation | Email format enforcement in gateway — verify if regex/format validation exists |
| TBD-003 | FULLSTACK_STITCHING_CONTRACT.md | §1 Test coverage | customer_360_cdp backend test files — verify specific test file names in 79-file suite |
| TBD-004 | FULLSTACK_STITCHING_CONTRACT.md | §2 Test coverage | lead_management specific test file names in backend suite |
| TBD-005 | FULLSTACK_STITCHING_CONTRACT.md | §3 Test coverage | sales_cockpit specific test file names in backend suite |
| TBD-006 | FULLSTACK_STITCHING_CONTRACT.md | §4 Test coverage | revenue_recognition, usage_billing, subscription_billing test files |
| TBD-007 | FULLSTACK_STITCHING_CONTRACT.md | §6 Test coverage | omnichannel_inbox test files in 79-file suite |
| TBD-008 | FULLSTACK_STITCHING_CONTRACT.md | §7 Test coverage | ai_copilot, ai_scoring test files |
| TBD-009 | FULLSTACK_STITCHING_CONTRACT.md | §8 Auth | Password hashing algorithm — now resolved by API_INVENTORY.md (sha256:salt:hash) |
| TBD-010 | FULLSTACK_STITCHING_CONTRACT.md | §10 Workflow | WF-001 through WF-005 test coverage verification |
| TBD-011 | PRODUCT_WORKFLOWS.md | Automation Journeys | automation_journeys/api.py and services.py — detail specification of multi-step marketing journeys |
| TBD-012 | PROJECT_CHARTER.md | §7 Commercial Model | Platform billing model — how Pakistan CRM OS bills its own tenant customers |
| TBD-013 | PROJECT_CHARTER.md | §8 Success Metrics | Additional commercial KPIs from pricing-plans.md |
| TBD-014 | ADR-001_PROJECT_FOUNDATION.md | §4 PTA Compliance | Pakistan Telecommunications Authority compliance details from compliance-adapter.md |
| TBD-015 | ADR-001_PROJECT_FOUNDATION.md | §4 FBR Compliance | Federal Board of Revenue invoice formatting requirements |

**Note on TBD-009:** This item is resolved — the password hash algorithm (sha256:salt:hash) is confirmed in API_INVENTORY.md §AUTH. The TBD marker in FULLSTACK_STITCHING_CONTRACT.md §8 should be updated to reflect this.

---

## Audit Verdict

**Overall governance consistency: MOSTLY CONSISTENT**

**Reasoning:**

The seven Phase 1 governance documents form a coherent, internally aligned set on all major claims:
- Technology stack (FastAPI + Express.js + PostgreSQL + Redis + NexLink) — unanimous across all 7 documents
- Current phase (C6 Commercial Launch) — unanimous across all 7 documents  
- 7 canonical roles and 91 scopes — unanimous and consistent with U1 ground truth
- 5 system workflows and their trigger events — unanimous and consistent with WORKFLOW_INVENTORY.md
- Entity structure (20 domains, 30+ entities) — consistent with ENTITY_INVENTORY.md (minor count discrepancy noted)
- Pakistan-specific technical requirements (PKR, E.164, WhatsApp-first, JazzCash/Easypaisa stub) — unanimous
- External blockers (P-016, P-017, MR-001, MR-003, MR-007) — unanimous

The "MOSTLY" qualifier reflects:
- 1 stale gateway route count in API_INVENTORY.md footer (43 vs 44)
- 1 unverified API scope (contacts.delete) that is a potential security gap
- 1 missing entity (Forecast) in DOMAIN_MODEL.md
- 1 incomplete document (FULLSTACK_STITCHING_CONTRACT.md covers only 10 of 22 modules)
- Minor path string inconsistencies (dialog360 vs 360dialog)
- Territory criteria_type enum values differ between conceptual and runtime definitions

None of the identified issues represent fundamental architectural contradictions or disputes about what the system is or does. All issues are resolvable through targeted document updates. The FULLSTACK_STITCHING_CONTRACT.md is the only document with issues that prevent immediate promotion to Active status.

**Readiness summary:**
| Document | Ready for Active? |
|---|---|
| PROJECT_CHARTER.md | YES — no conditions |
| FEATURE_SCOPE.md | YES — after L-004 cosmetic fix |
| DOMAIN_MODEL.md | YES — after H-003, M-005, L-005, M-009 (one session of updates) |
| PRODUCT_WORKFLOWS.md | YES — after M-004, M-010 (two line fixes) |
| FULLSTACK_STITCHING_CONTRACT.md | NO — H-002, H-004 must be resolved first |
| AI_OPERATING_CONTEXT.md | YES — no blocking conditions |
| ADR-001_PROJECT_FOUNDATION.md | YES — after M-003 ADR renumbering |

---

*End GOVERNANCE_CONSISTENCY_AUDIT.md*
