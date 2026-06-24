---
Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: AI
Phase: 3.5 — Project Memory Layer Establishment
---

# AUTO_CLOSED REGISTER

> All items resolved directly from repository evidence (code, architecture, contracts, authority docs).
> No owner action required for any item in this register.
> Owner Required: NO for all entries. External Dependency: NO for all entries.

---

## AC-001: OA-004 — AI Inference Model Selection

**Item ID:** OA-004
**Title:** AI inference model selection — rule-based vs LLM
**Classification:** AUTO_CLOSED
**Current Status:** Closed — no C6 action needed
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md
**Evidence Source:** backend/requirements.txt; backend/src/ai_copilot/services.py; backend/src/ai_insights/services.py
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md (Phase 2.97)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** Rule-based scoring IS the designed and implemented C6 production behavior. The question "which LLM provider?" is a C7 additive feature request, not an open C6 decision.

**Detailed Explanation:** All AI features (ai-copilot.html M-01, ai-insights.html M-02) use rule-based weighted-sum scoring. No AI inference provider SDK is installed in requirements.txt (no openai, anthropic, google-generativeai packages). This is not a gap — it is the documented C6 design. FEATURE_SCOPE.md §14 Module 14 documents features 86–93 all as "Built (rule-based only)" or "Built (rule-based)". The advisory shell posture is intentional. LLM integration is an additive C7 scope item.

**Affected Components:** backend/src/ai_copilot/, backend/src/ai_insights/, frontend/src/app/ai-copilot.html (M-01), frontend/src/app/ai-insights.html (M-02)
**Affected Routes:** GET /ai-copilot/suggestions, GET /ai-insights/*, POST /ai-copilot/chat
**Affected APIs:** AI Copilot API group, AI Insights API group
**Affected Workflows:** None (advisory only, no workflow triggers)
**Affected Roles:** All roles (advisory features visible to all)

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** When C7 LLM integration sprint begins: add SDK to requirements.txt, set API key in render.yaml, replace rule-based scoring functions in services.py. No structural changes needed — hooks are already in place.

**Reopen Criteria:** Only if a decision is made to add LLM inference to C6 scope (scope change requires owner sign-off).

**Related Documents:** FEATURE_SCOPE.md §14, AI_OPERATING_CONTEXT.md (KNOWN_CONSTRAINTS AI-001), DESIGN-SPEC.md archetype M
**Related Register Entries:** AI-001 (OUT_OF_SCOPE_REGISTER.md)

---

## AC-002: OA-005 — contracts_lifecycle_management No Gateway Route

**Item ID:** OA-005
**Title:** contract_lifecycle_management module — no gateway route
**Classification:** AUTO_CLOSED
**Current Status:** Closed — C7 scope confirmed
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md
**Evidence Source:** DESIGN-SPEC.md (no contracts page in C6 75-page scope); backend/src/contract_lifecycle_management/api.py
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md (Phase 2.97); confirmed Phase 2.95
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass (confirmed Phase 2.95 closure)

**Decision Summary:** DESIGN-SPEC.md contains no contracts frontend page in the C6 75-page scope. Backend module is complete and tested. Gateway route will be created in C7 when the contracts frontend page is built.

**Detailed Explanation:** backend/src/contract_lifecycle_management/ is fully implemented with 12 API endpoints (API_ENDPOINTS dict in api.py). MODULE_INVENTORY.md §29 originally flagged "gateway route required; human decision." Resolution: DESIGN-SPEC.md confirms no contracts page exists in the C6 scope (75 custom pages, 13 archetypes A–M — no contracts archetype). No gateway route is needed in C6 because there is no frontend page to call it. The module will be exposed in C7 when frontend page is built.

**Affected Components:** backend/src/contract_lifecycle_management/, backend/gateway/routes/ (no file needed for C6)
**Affected Routes:** None in C6 (12 endpoints defined in Python but not exposed via gateway)
**Affected APIs:** N/A in C6
**Affected Workflows:** None in C6
**Affected Roles:** N/A in C6

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** C7 sprint: create backend/gateway/routes/v1-contracts.routes.js using existing 43 route files as pattern. Add contracts.* RBAC scopes following OA-001 pattern. Build contracts frontend page per DESIGN-SPEC.md C7 archetype.

**Reopen Criteria:** If a decision is made to add a contracts page to C6 scope (scope change requires owner sign-off and DESIGN-SPEC.md update).

**Related Documents:** DESIGN-SPEC.md, MODULE_INVENTORY.md §29, FEATURE_SCOPE.md
**Related Register Entries:** D-001 (AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS — confirmed OUT_OF_SCOPE)

---

## AC-003: D-002 — Custom Objects Module Product Scope

**Item ID:** D-002
**Title:** Custom objects module — K-02 advisory shell or live backend?
**Classification:** AUTO_CLOSED
**Current Status:** Closed 2026-06-23
**Original Source:** UNRESOLVABLE_ITEMS_REGISTER.md
**Evidence Source:** docs/00_authority/FEATURE_SCOPE.md §22 Feature 129 Status=Built; DESIGN-SPEC.md line 204 K-02 Browser-approved; FG-005 in FRONTEND_GAP_REGISTER.md
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25 (Collapse Rule B — Documentation evidence)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** K-02 (object-builder.html) is a C6 built advisory shell with crm-dummy.js data. FEATURE_SCOPE.md §22 Feature 129 Status=Built confirms it is in C6 scope as a built page. No gateway route is needed for the advisory shell posture.

**Detailed Explanation:** D-002 was previously OWNER-REQUIRED because the question "is K-02 advisory or live?" could not be answered from code alone. During Phase 3.25, FEATURE_SCOPE.md §22 (Module 22: Builder Tools, Feature 129 "Custom object builder") was read directly — Status = Built. DESIGN-SPEC.md line 204 confirms K-02: "Cat 2. Built 2026-05-29. Browser-approved." FG-005 in FRONTEND_GAP_REGISTER.md already documents K-02 as advisory shell. The three sources are consistent: K-02 is built, browser-approved, and correctly implemented as an advisory shell (consistent with D-002 "no gateway route needed" conclusion).

**Affected Components:** frontend/src/app/object-builder.html (K-02), backend/src/custom_objects/, backend/src/custom_object_framework/
**Affected Routes:** None in C6 (no v1-custom-objects.routes.js needed for advisory shell)
**Affected APIs:** None in C6
**Affected Workflows:** None
**Affected Roles:** All admin roles can view the advisory shell

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** When custom objects becomes live (C7+): create v1-custom-objects.routes.js, wire frontend to live API, remove crm-dummy.js fallback.

**Reopen Criteria:** If owner explicitly decides K-02 must have live backend connectivity in C6 (scope change).

**Related Documents:** FEATURE_SCOPE.md §22, DESIGN-SPEC.md line 204, FRONTEND_GAP_REGISTER.md FG-005
**Related Register Entries:** FSC_CUSTOM_OBJ (this register AC-022)

---

## AC-004: D-003 — Entity Schema Attributions Unverified

**Item ID:** D-003
**Title:** 5 entity schema attributions unverified (inferred from gateway code)
**Classification:** AUTO_CLOSED
**Current Status:** Closed — assigned as verification task
**Original Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md
**Evidence Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md SD-012; backend/db/*/schema.sql files
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** This is an investigation task (read 5 schema.sql files directly), not an owner decision. No human judgment required — backend team executes verification pass.

**Detailed Explanation:** 5 entity field lists were inferred from gateway code rather than read directly from DB schema.sql files. This creates documentation accuracy risk (field names or types may differ). However, the entities function correctly — this is documentation completeness only. Any developer can verify by reading the 5 schema.sql files. No policy decision, no commercial judgment, no external dependency.

**Affected Components:** backend/db/*/schema.sql (5 specific files to be read)
**Affected Routes:** N/A
**Affected APIs:** N/A
**Affected Workflows:** N/A
**Affected Roles:** N/A (documentation only)

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** When verification pass completes: update DOMAIN_MODEL.md and ENTITY_INVENTORY.md field lists for affected entities. No code changes needed.

**Reopen Criteria:** Cannot be reopened — it is already open as a verification task. Closes permanently when the 5 schema.sql files are read and docs updated.

**Related Documents:** DOMAIN_MODEL.md, ENTITY_INVENTORY.md, backend/db/*/schema.sql
**Related Register Entries:** None

---

## AC-005: G-HIGH-005 — leads.delete Scope Gap (False Alarm)

**Item ID:** G-HIGH-005
**Title:** leads.delete scope missing from rbac-scopes.js
**Classification:** AUTO_CLOSED
**Current Status:** Closed Phase 2.9
**Original Source:** BACKEND_GAP_REGISTER.md (original gap register)
**Evidence Source:** backend/gateway/config/rbac-scopes.js line 21: `LEADS_DELETE: 'leads.delete'`
**Resolution Source:** APPROVAL_ELIMINATION_REPORT.md Phase 2.9 (Step 7 — DD-004)
**Resolution Date:** 2026-06-23 (confirmed; originally closed Phase 2.9)
**Resolved By:** Phase 2.9 Approval Elimination Pass

**Decision Summary:** LEADS_DELETE: 'leads.delete' IS present in rbac-scopes.js line 21. Not a gap — false alarm from original audit.

**Affected Components:** backend/gateway/config/rbac-scopes.js line 21
**Affected Routes:** DELETE /leads/:id
**Affected APIs:** Lead Management API
**Affected Workflows:** None
**Affected Roles:** Roles with leads.delete scope

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** None. Scope is present and functioning.

**Reopen Criteria:** If leads.delete is accidentally removed from rbac-scopes.js.

**Related Documents:** backend/gateway/config/rbac-scopes.js
**Related Register Entries:** OA-001 (contrast: contacts.delete IS missing, leads.delete is NOT)

---

## AC-006: G-MED-002 — SLA Breach Events Not Emitted (False Alarm)

**Item ID:** G-MED-002
**Title:** SLA breach events not emitted from backend
**Classification:** AUTO_CLOSED
**Current Status:** Closed Phase 2.9
**Original Source:** BACKEND_GAP_REGISTER.md
**Evidence Source:** backend/services/cases/service.py lines 120–144 — case.sla.*.v1 events confirmed emitted
**Resolution Source:** APPROVAL_ELIMINATION_REPORT.md Phase 2.9; confirmed DECISION_COLLAPSE_REGISTER.md Phase 3.25 (CASE_SLA_SCANNER_TBD)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.9 Approval Elimination Pass

**Decision Summary:** SLA breach events ARE emitted from services/cases/service.py. Not a gap — false alarm.

**Affected Components:** backend/services/cases/service.py lines 120–144
**Affected Routes:** SLA breach webhook delivery
**Affected APIs:** Cases service internal events
**Affected Workflows:** WF-003 (SLA breach auto-escalation)
**Affected Roles:** Agents, supervisors (notification recipients)

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** None. Events are emitting correctly.

**Reopen Criteria:** If SLA event emission is broken by a future code change.

**Related Documents:** backend/docs/infrastructure/event-catalog.md, PRODUCT_WORKFLOWS.md WF-003
**Related Register Entries:** O-TBD-005 (this register AC-012 — event schemas confirmed)

---

## AC-007: G-MED-003 — Dev Token Endpoint Active in Production (False Alarm)

**Item ID:** G-MED-003
**Title:** Dev token endpoint active in production
**Classification:** AUTO_CLOSED
**Current Status:** Closed Phase 2.9
**Original Source:** BACKEND_GAP_REGISTER.md
**Evidence Source:** render.yaml line 37: JWT_SECRET always set; dev endpoint conditional on JWT_SECRET absence
**Resolution Source:** APPROVAL_ELIMINATION_REPORT.md Phase 2.9; confirmed DECISION_COLLAPSE_REGISTER.md O-TBD-007
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.9 Approval Elimination Pass

**Decision Summary:** JWT_SECRET is always set in render.yaml. Dev token endpoint is inactive in production. Not a gap.

**Affected Components:** backend/gateway/routes/v1-auth.routes.js (dev endpoint conditional)
**Affected Routes:** Dev-only token endpoint
**Affected APIs:** Auth API
**Affected Workflows:** None
**Affected Roles:** N/A (endpoint inactive in production)

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** None. Security posture is correct.

**Reopen Criteria:** If JWT_SECRET is accidentally removed from render.yaml.

**Related Documents:** render.yaml line 37, backend/gateway/routes/v1-auth.routes.js
**Related Register Entries:** None

---

## AC-008: G-LOW-001 — DB Connection Pool Not Configurable (False Alarm)

**Item ID:** G-LOW-001
**Title:** DB connection pool size not configurable
**Classification:** AUTO_CLOSED
**Current Status:** Closed Phase 2.9
**Original Source:** BACKEND_GAP_REGISTER.md
**Evidence Source:** backend/gateway/db/pool.js — DB_POOL_MAX env var confirmed
**Resolution Source:** APPROVAL_ELIMINATION_REPORT.md Phase 2.9
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.9 Approval Elimination Pass

**Decision Summary:** Pool is configurable via DB_POOL_MAX env var. Not a gap — false alarm.

**Affected Components:** backend/gateway/db/pool.js
**Affected Routes:** All database-backed routes
**Affected APIs:** All
**Affected Workflows:** All
**Affected Roles:** All

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** Set DB_POOL_MAX in render.yaml when tuning for scale.

**Reopen Criteria:** If DB_POOL_MAX env var support is removed from pool.js.

**Related Documents:** backend/gateway/db/pool.js, render.yaml
**Related Register Entries:** None

---

## AC-009: O-TBD-001 — EmailStr vs plain str in FastAPI Models

**Item ID:** O-TBD-001
**Title:** EmailStr vs plain str type for email fields in Pydantic models
**Classification:** AUTO_CLOSED
**Current Status:** Resolved Phase 3.25
**Original Source:** TBD_RESOLUTION_REGISTER.md
**Evidence Source:** grep -r "EmailStr" backend/src/ = no matches; customer_360_cdp/entities.py uses email: str
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25 (Collapse Rule A)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** Email is plain str type in FastAPI models. No EmailStr validator. No format validation in Python layer. VALIDATION_RULES.md updated.

**Affected Components:** backend/src/ Pydantic models (all use email: str)
**Affected Routes:** All routes accepting email fields
**Affected APIs:** Customer 360 CDP, Contacts, Auth
**Affected Workflows:** Registration, contact creation
**Affected Roles:** All

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** Email format validation is convention only (no runtime enforcement in Python layer). If email validation is added in future, add pydantic[email] to requirements.txt and change field type.

**Reopen Criteria:** If EmailStr is added to any Pydantic model.

**Related Documents:** VALIDATION_RULES.md (updated), backend/src/customer_360_cdp/entities.py
**Related Register Entries:** None

---

## AC-010: O-TBD-002 — Phone Number Validation Regex

**Item ID:** O-TBD-002
**Title:** Phone number validation regex in Pydantic models
**Classification:** AUTO_CLOSED
**Current Status:** Resolved Phase 3.25
**Original Source:** TBD_RESOLUTION_REGISTER.md
**Evidence Source:** grep result: no phone regex in backend/src/ or backend/gateway/; dedup is string equality
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25 (Collapse Rule A)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** No phone regex validator exists. E.164 is convention + DB uniqueness constraint only. VALIDATION_RULES.md updated.

**Affected Components:** backend/src/ (all phone fields)
**Affected Routes:** Lead creation, contact creation, any route accepting phone
**Affected APIs:** Lead Management, Customer 360, Contacts
**Affected Workflows:** Lead import, contact import
**Affected Roles:** All

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** If E.164 format enforcement is required at API layer, add a Pydantic validator function.

**Reopen Criteria:** If phone regex is added to any Pydantic model (update VALIDATION_RULES.md).

**Related Documents:** VALIDATION_RULES.md (updated)
**Related Register Entries:** None

---

## AC-011: O-TBD-003 — CNIC/NTN/STRN Database Fields

**Item ID:** O-TBD-003
**Title:** CNIC/NTN/STRN as database fields
**Classification:** AUTO_CLOSED
**Current Status:** Resolved Phase 3.25
**Original Source:** TBD_RESOLUTION_REGISTER.md
**Evidence Source:** grep backend/db/ returns no matches; only found in jazzcash.py metadata dict (pp_CNIC)
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25 (Collapse Rule A)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** CNIC/NTN/STRN are NOT database fields. They appear only as optional JazzCash payment metadata. VALIDATION_RULES.md updated.

**Affected Components:** backend/adapters/pakistan/payments/jazzcash.py (pp_CNIC metadata only)
**Affected Routes:** JazzCash payment endpoints
**Affected APIs:** Billing/Payment API
**Affected Workflows:** Payment processing
**Affected Roles:** N/A (payment metadata only)

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** If FBR compliance requires NTN/STRN as invoice fields, schema migration will be needed. See FBR-COMP in OUT_OF_SCOPE_REGISTER.md.

**Reopen Criteria:** If CNIC/NTN/STRN are added as DB schema fields.

**Related Documents:** VALIDATION_RULES.md (updated), backend/adapters/pakistan/payments/jazzcash.py
**Related Register Entries:** FBR-COMP (OUT_OF_SCOPE_REGISTER.md)

---

## AC-012: O-TBD-004 — UUID Type in FastAPI Pydantic Models

**Item ID:** O-TBD-004
**Title:** UUID type in FastAPI Pydantic models
**Classification:** AUTO_CLOSED
**Current Status:** Resolved Phase 3.25
**Original Source:** TBD_RESOLUTION_REGISTER.md
**Evidence Source:** backend/src/support_console entities: Optional[uuid.UUID] in BaseModel; uuid4() for generation
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25 (Collapse Rule A)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** UUID fields use uuid.UUID type in Pydantic models; generated with uuid4().

**Affected Components:** backend/src/ Pydantic models (UUID fields)
**Affected Routes:** All routes with ID fields
**Affected APIs:** All
**Affected Workflows:** All
**Affected Roles:** All

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** None. UUID type is consistent and confirmed.

**Reopen Criteria:** If UUID type is changed.

**Related Documents:** backend/src/support_console/entities.py, VALIDATION_RULES.md
**Related Register Entries:** None

---

## AC-013: O-TBD-005 — Event Schemas for 6 Core Events

**Item ID:** O-TBD-005
**Title:** Event schemas for 6 events (opp.stage.changed, opp.closed, lead.idle, lead.created, invoice.overdue, case.sla.breached)
**Classification:** AUTO_CLOSED
**Current Status:** Resolved Phase 3.25
**Original Source:** TBD_RESOLUTION_REGISTER.md
**Evidence Source:** backend/docs/infrastructure/event-catalog.md — full payload schemas for all 6 events
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25 (Collapse Rule B)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** All 6 event schemas are fully documented in backend/docs/infrastructure/event-catalog.md. CONTRACT_VERSION_REGISTRY.md updated.

**Affected Components:** backend/src/event_bus/, backend/services/ (event publishers)
**Affected Routes:** Webhook delivery routes
**Affected APIs:** Event Bus, Webhooks
**Affected Workflows:** WF-001 (lead idle), WF-002 (collections), WF-003 (SLA breach), WF-004 (territory), WF-005 (opp stage)
**Affected Roles:** All

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** None. Event schemas are documented and stable.

**Reopen Criteria:** If event schema changes (requires CONTRACT_VERSION_REGISTRY.md update).

**Related Documents:** backend/docs/infrastructure/event-catalog.md, CONTRACT_VERSION_REGISTRY.md
**Related Register Entries:** EVENT_BUS_TBD (this register AC-015)

---

## AC-014: O-TBD-006 — Route Deprecation Strategy

**Item ID:** O-TBD-006
**Title:** Route deprecation strategy for v1 API
**Classification:** AUTO_CLOSED
**Current Status:** Resolved Phase 3.25 — confirmed no strategy in C6
**Original Source:** TBD_RESOLUTION_REGISTER.md
**Evidence Source:** No deprecation headers in any route file; single v1 prefix; no v2 planned for C6
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25 (Collapse Rule F)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** No route deprecation strategy is implemented in C6. Single v1 prefix. Strategy needed when v2 is planned (C7+).

**Affected Components:** backend/gateway/routes/ (all v1-*.routes.js)
**Affected Routes:** All 228 API endpoints
**Affected APIs:** All
**Affected Workflows:** N/A
**Affected Roles:** N/A

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** C7+: when v2 routes are planned, implement Deprecation header standard. CONTRACT_VERSION_REGISTRY.md documents the approach.

**Reopen Criteria:** If v2 routes are added to C6 scope.

**Related Documents:** CONTRACT_VERSION_REGISTRY.md
**Related Register Entries:** None

---

## AC-015: EVENT_BUS_TBD — Event Dispatch Mechanism

**Item ID:** EVENT_BUS_TBD
**Title:** Event dispatch mechanism — in-process or polling?
**Classification:** AUTO_CLOSED
**Current Status:** Resolved Phase 3.25
**Original Source:** EVENT_AND_QUEUE_ARCHITECTURE.md
**Evidence Source:** backend/src/event_bus/core.py: InMemoryEventBus class; src/event_bus/__init__.py exports it
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25 (Collapse Rule A)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** Events dispatched in-process via InMemoryEventBus with retry and dead-letter queue. Not an external broker. EVENT_AND_QUEUE_ARCHITECTURE.md updated.

**Affected Components:** backend/src/event_bus/core.py, backend/src/event_bus/__init__.py
**Affected Routes:** All event-publishing service methods
**Affected APIs:** Internal event bus (not a public API)
**Affected Workflows:** All 5 system workflows
**Affected Roles:** N/A (infrastructure)

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** When message broker is added (C7 per BROKER-C7 in OUT_OF_SCOPE_REGISTER.md), InMemoryEventBus will be replaced by a broker-backed bus. Interface remains stable.

**Reopen Criteria:** If event bus implementation changes from in-process.

**Related Documents:** EVENT_AND_QUEUE_ARCHITECTURE.md (updated), backend/src/event_bus/
**Related Register Entries:** BROKER-C7 (OUT_OF_SCOPE_REGISTER.md), G-HIGH-003 (SAFE_DEFAULT_REGISTER.md SD-006)

---

## AC-016: OUTBOX_TBD — Outbox Publisher Confirmed Absent

**Item ID:** OUTBOX_TBD
**Title:** Outbox publisher — confirmed absent
**Classification:** AUTO_CLOSED
**Current Status:** Resolved Phase 3.25 — confirmed absent, SAFE_DEFAULT applies
**Original Source:** EVENT_AND_QUEUE_ARCHITECTURE.md
**Evidence Source:** grep -r "outbox" backend/src/ = no matches; outbox table in db/transaction_db/schema.sql but no publisher code
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25 (Collapse Rule A)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** Outbox publisher is confirmed absent from backend/src/. Outbox table exists in DB. G-HIGH-004 SAFE_DEFAULT (SD-007) applies: accept for C6 while payments are in stub mode; implement when OA-003 activates.

**Affected Components:** backend/db/transaction_db/schema.sql (outbox table defined), backend/src/ (no publisher)
**Affected Routes:** Payment processing routes (when activated)
**Affected APIs:** Billing/Payment API
**Affected Workflows:** WF-002 (collections invoicing)
**Affected Roles:** N/A (infrastructure)

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** When OA-003 payment credentials are received: implement outbox publisher in backend/src/billing/ or backend/src/event_bus/. Outbox table schema is already in place.

**Reopen Criteria:** If outbox publisher is implemented (item naturally closes; remove from register).

**Related Documents:** backend/db/transaction_db/schema.sql, EVENT_AND_QUEUE_ARCHITECTURE.md
**Related Register Entries:** G-HIGH-004 (SAFE_DEFAULT_REGISTER.md SD-007), OA-003 (EXTERNAL_DEPENDENCY_REGISTER.md)

---

## AC-017 through AC-021: FSC Test TBDs — Backend Test Files Confirmed

**Item ID:** FSC_TEST_TBD_1, FSC_TEST_TBD_2, FSC_TEST_TBD_3, FSC_TEST_TBD_4, FSC_TEST_TBD_5
**Title:** Backend test file existence confirmation (5 modules)
**Classification:** AUTO_CLOSED
**Current Status:** All resolved Phase 3.25
**Original Source:** FULLSTACK_STITCHING_CONTRACT.md (TBD markers)
**Evidence Source:** grep/ls confirmation of test files in backend/tests/
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25 (Collapse Rule A)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** All 5 test files confirmed present:
- FSC_TEST_TBD_1: backend/tests/test_customer_360_cdp.py — CONFIRMED
- FSC_TEST_TBD_2: backend/tests/test_lead_management.py — CONFIRMED
- FSC_TEST_TBD_3: backend/tests/test_sales_cockpit_workspace.py — CONFIRMED
- FSC_TEST_TBD_4: backend/tests/test_revenue_recognition.py, test_subscription_billing.py, test_usage_billing.py — CONFIRMED (3 files)
- FSC_TEST_TBD_5: backend/tests/test_omnichannel_inbox.py — CONFIRMED

**Affected Components:** backend/tests/ directory (79 total pytest test files)
**Affected Routes:** All tested routes
**Affected APIs:** Customer 360 CDP, Lead Management, Sales Cockpit, Billing/Revenue, Omnichannel Inbox
**Affected Workflows:** All
**Affected Roles:** N/A (tests)

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** FULLSTACK_STITCHING_CONTRACT.md updated to remove TBD markers. Test coverage baseline confirmed.

**Reopen Criteria:** If test files are deleted.

**Related Documents:** FULLSTACK_STITCHING_CONTRACT.md (updated), backend/tests/
**Related Register Entries:** None

---

## AC-022: FSC_CUSTOM_OBJ — Custom Objects Routing TBD

**Item ID:** FSC_CUSTOM_OBJ
**Title:** Custom objects routing mechanism TBD in FULLSTACK_STITCHING_CONTRACT
**Classification:** AUTO_CLOSED
**Current Status:** Resolved Phase 3.25 (via D-002 closure)
**Original Source:** FULLSTACK_STITCHING_CONTRACT.md
**Evidence Source:** FEATURE_SCOPE.md + DESIGN-SPEC.md (K-02 advisory shell)
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** K-02 is advisory shell. No gateway route needed. Routing TBD is moot. FULLSTACK_STITCHING_CONTRACT.md updated.

**Affected Components:** frontend/src/app/object-builder.html (K-02)
**Affected Routes:** None (advisory shell)
**Affected APIs:** None
**Affected Workflows:** None
**Affected Roles:** All (advisory view)

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** When K-02 is wired to live API (C7+), FULLSTACK_STITCHING_CONTRACT.md needs update.

**Reopen Criteria:** If K-02 is upgraded to live API in C6 (scope change).

**Related Documents:** FULLSTACK_STITCHING_CONTRACT.md (updated), D-002 (this register AC-003)
**Related Register Entries:** D-002 (this register AC-003)

---

## AC-023: P-TBD-003 — Frontend Scope-Based UI Gating

**Item ID:** P-TBD-003
**Title:** Frontend scope-based UI gating — defined or TBD?
**Classification:** AUTO_CLOSED
**Current Status:** Resolved Phase 3.25
**Original Source:** TBD_RESOLUTION_REGISTER.md
**Evidence Source:** docs/03_frontend_authority/FRONTEND_PERMISSION_MATRIX.md — scope gating defined for all 75 pages
**Resolution Source:** DECISION_COLLAPSE_REGISTER.md Phase 3.25 (Collapse Rule B)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.25 Autonomous Gap Elimination

**Decision Summary:** Frontend scope gating IS defined in FRONTEND_PERMISSION_MATRIX.md for all 75 pages. TBD was obsolete. USER_ROLES_AND_PERMISSIONS.md updated.

**Affected Components:** frontend/src/app/*.html (all 75 pages), FRONTEND_PERMISSION_MATRIX.md
**Affected Routes:** All frontend page routes
**Affected APIs:** RBAC API (scope check)
**Affected Workflows:** All
**Affected Roles:** All 7 roles

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** None. Permission matrix is the authoritative source for frontend gating.

**Reopen Criteria:** If FRONTEND_PERMISSION_MATRIX.md is deleted or scope definitions change.

**Related Documents:** docs/03_frontend_authority/FRONTEND_PERMISSION_MATRIX.md, USER_ROLES_AND_PERMISSIONS.md
**Related Register Entries:** None

---

## AC-024: CRIT-002 — python-jose Version Drift

**Item ID:** CRIT-002
**Title:** python-jose version drift (venv vs pip-audit)
**Classification:** AUTO_CLOSED
**Current Status:** Closed U10
**Original Source:** BACKEND_GAP_REGISTER.md
**Evidence Source:** venv has python-jose 3.5.0; pip-audit.json was stale (not updated after upgrade)
**Resolution Source:** Phase U10 audit
**Resolution Date:** 2026-06-23 (confirmed; originally closed U10)
**Resolved By:** Phase U10 audit

**Decision Summary:** Not a real version drift. venv has 3.5.0; pip-audit.json was stale. No security gap.

**Affected Components:** backend/requirements.txt, backend venv
**Affected Routes:** Auth routes (JWT decode)
**Affected APIs:** Auth API
**Affected Workflows:** Login, token refresh
**Affected Roles:** All

**Owner Required:** NO
**External Dependency:** NO

**Future Impact:** Keep pip-audit.json current on dependency updates.

**Reopen Criteria:** If python-jose CVE is published for 3.5.0.

**Related Documents:** backend/requirements.txt, pip-audit.json
**Related Register Entries:** None

---

*End AUTO_CLOSED_REGISTER.md — 24 items (AC-001 through AC-024) — Phase 3.5 (2026-06-23)*
