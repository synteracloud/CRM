---
Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: AI
Phase: 3.25
---

# DECISION COLLAPSE REGISTER — Phase 3.25

> Full register of every item reviewed during Phase 3.25 Autonomous Gap Elimination.
> Every open TBD, unresolved gap, and owner-required item is listed here with its collapse outcome.

---

## Register

| Item ID | Source | Description | Collapse Rule Applied | Evidence | Resolution | Final Status |
|---------|--------|-------------|----------------------|----------|------------|--------------|
| D-002 | UNRESOLVABLE_ITEMS_REGISTER.md | Custom objects module product scope in C6 — is K-02 advisory or live? | B — Documentation evidence | FEATURE_SCOPE.md §22: Feature 129 "Custom object builder" Status = Built. DESIGN-SPEC.md line 204: K-02 Browser-approved. | K-02 is a C6 built advisory shell. No gateway route needed. D-002 CLOSED. | CLOSED |
| OA-003 | UNRESOLVABLE_ITEMS_REGISTER.md | JazzCash/Easypaisa live payment credentials | None applicable | render.yaml STUB flags, adapter code, no credentials anywhere in repo | Vendor merchant account application required. Cannot be resolved from code. | UNRESOLVABLE — Commercial |
| G-MED-005 | UNRESOLVABLE_ITEMS_REGISTER.md | Urdu WhatsApp template approval (P-017) | None applicable | Urdu strings exist in code with UR_TODO markers; no native speaker review found | Human Urdu native speaker review required. Cannot be automated. | UNRESOLVABLE — Linguistic/Compliance |
| O-TBD-001 | TBD_RESOLUTION_REGISTER.md | EmailStr vs plain str in FastAPI models | A — Code evidence | grep -r "EmailStr" backend/src/ = no matches; customer_360_cdp/entities.py uses email: str | Email is plain str type. No EmailStr. No format validation in Python layer. | RESOLVED — Updated VALIDATION_RULES.md |
| O-TBD-002 | TBD_RESOLUTION_REGISTER.md | Phone number validation regex in Pydantic | A — Code evidence | No phone regex in backend/src/ or backend/gateway/. Dedup is string equality. No validator function found. | No phone regex validator exists. E.164 is convention + DB uniqueness only. | RESOLVED — Updated VALIDATION_RULES.md |
| O-TBD-003 | TBD_RESOLUTION_REGISTER.md | CNIC/NTN/STRN database fields | A — Code evidence | grep backend/db/ returns no matches. Only in jazzcash.py metadata dict (pp_CNIC). | Not DB fields. Optional JazzCash payment metadata only. | RESOLVED — Updated VALIDATION_RULES.md |
| O-TBD-004 | TBD_RESOLUTION_REGISTER.md | UUID type in FastAPI Pydantic models | A — Code evidence | backend/src/support_console entities: Optional[uuid.UUID] in BaseModel. uuid4() used for generation. | UUID fields use uuid.UUID type in Pydantic; generated with uuid4(). | RESOLVED — Updated VALIDATION_RULES.md |
| O-TBD-005 | TBD_RESOLUTION_REGISTER.md | Event schema for 6 events (opp.stage.changed, opp.closed, lead.idle, lead.created, invoice.overdue, case.sla.breached) | B — Documentation evidence | backend/docs/infrastructure/event-catalog.md: full payload schemas for all 6 events documented. | All 6 event schemas resolved from event catalog. | RESOLVED — Updated CONTRACT_VERSION_REGISTRY.md |
| O-TBD-006 | TBD_RESOLUTION_REGISTER.md | Route deprecation strategy | F — Only rational interpretation | No deprecation headers in any route file. Single v1 prefix. No v2 planned for C6. | No deprecation strategy implemented. Needed when v2 planned (C7+). TBD converted to confirmed state. | RESOLVED — Updated CONTRACT_VERSION_REGISTRY.md |
| O-TBD-007 | TBD_RESOLUTION_REGISTER.md | Dev token endpoint active in production | A — Code already verified | Already closed as G-MED-003 in BACKEND_GAP_REGISTER.md (JWT_SECRET in render.yaml). | Confirmed closed. Dev endpoint always inactive in production. | CONFIRMED CLOSED (prior phase) |
| O-TBD-008 | TBD_RESOLUTION_REGISTER.md | SLA breach background scanner | A — Code already verified | Already closed as G-MED-002 in BACKEND_GAP_REGISTER.md (emitted from services/cases/service.py). | Confirmed closed. SLA breach events emitted. | CONFIRMED CLOSED (prior phase) |
| P-TBD-001 | TBD_RESOLUTION_REGISTER.md | JTI blocklist in-memory → Redis (owner decision) | SAFE-DEFAULT already applied | OA-002 classified as SAFE-DEFAULT in FINAL_CLASSIFIED_REGISTER.md | Accept for C6; Redis migration in Post-C6 Auth Sprint. | SAFE-DEFAULT (no change needed) |
| P-TBD-002 | TBD_RESOLUTION_REGISTER.md | Refresh token revocation on logout (owner decision) | SAFE-DEFAULT already applied | OA-009 classified as SAFE-DEFAULT. v1-auth.routes.js confirmed behavior. | Accept for C6; bundle fix with OA-002 post-C6. | SAFE-DEFAULT (no change needed) |
| P-TBD-003 | TBD_RESOLUTION_REGISTER.md | Frontend scope-based UI gating | B — Documentation evidence | docs/03_frontend_authority/FRONTEND_PERMISSION_MATRIX.md exists and defines scope gating for all 75 pages. | Frontend scope gating IS defined in FRONTEND_PERMISSION_MATRIX.md. TBD obsolete. | RESOLVED — Updated USER_ROLES_AND_PERMISSIONS.md |
| P-TBD-004 | TBD_RESOLUTION_REGISTER.md | contacts.delete scope in RBAC | SAFE-DEFAULT already applied | OA-001 SAFE-DEFAULT: grant to tenant_admin + super_admin. Pattern from 6 other delete scope examples. | SAFE-DEFAULT documented. Implementation pending owner sign-off on code change. | SAFE-DEFAULT (no change needed) |
| EVENT_BUS_TBD | EVENT_AND_QUEUE_ARCHITECTURE.md | Event dispatch mechanism — in-process or polling? | A — Code evidence | backend/src/event_bus/core.py: InMemoryEventBus class. src/event_bus/__init__.py exports it. Confirmed in-process pub/sub with retry + dead-letter. | Events dispatched in-process via InMemoryEventBus. | RESOLVED — Updated EVENT_AND_QUEUE_ARCHITECTURE.md |
| OUTBOX_TBD | EVENT_AND_QUEUE_ARCHITECTURE.md | Outbox publisher — confirmed absent? | A — Code evidence | grep -r "outbox" backend/src/ = no matches. Outbox table defined in DB but no publisher code found. | Outbox publisher CONFIRMED ABSENT. G-HIGH-004 SAFE-DEFAULT applies. | RESOLVED — Updated EVENT_AND_QUEUE_ARCHITECTURE.md |
| CASE_SLA_SCANNER_TBD | EVENT_AND_QUEUE_ARCHITECTURE.md | SLA scanner implementation verification | A — Code already verified | G-MED-002 CLOSED: services/cases/service.py emits case.sla.*.v1 events. | SLA events confirmed emitted. | CONFIRMED CLOSED (prior phase) |
| FSC_TEST_TBD_1 | FULLSTACK_STITCHING_CONTRACT.md | Backend tests for customer_360_cdp | A — Code evidence | backend/tests/test_customer_360_cdp.py confirmed present. | Specific test file confirmed. | RESOLVED — Updated FULLSTACK_STITCHING_CONTRACT.md |
| FSC_TEST_TBD_2 | FULLSTACK_STITCHING_CONTRACT.md | Backend tests for lead_management | A — Code evidence | backend/tests/test_lead_management.py confirmed present. | Specific test file confirmed. | RESOLVED — Updated FULLSTACK_STITCHING_CONTRACT.md |
| FSC_TEST_TBD_3 | FULLSTACK_STITCHING_CONTRACT.md | Backend tests for sales_cockpit | A — Code evidence | backend/tests/test_sales_cockpit_workspace.py confirmed present. | Specific test file confirmed. | RESOLVED — Updated FULLSTACK_STITCHING_CONTRACT.md |
| FSC_TEST_TBD_4 | FULLSTACK_STITCHING_CONTRACT.md | Backend tests for subscription/billing | A — Code evidence | backend/tests/test_revenue_recognition.py, test_subscription_billing.py, test_usage_billing.py confirmed. | 3 specific test files confirmed. | RESOLVED — Updated FULLSTACK_STITCHING_CONTRACT.md |
| FSC_TEST_TBD_5 | FULLSTACK_STITCHING_CONTRACT.md | Backend tests for omnichannel_inbox | A — Code evidence | backend/tests/test_omnichannel_inbox.py confirmed present. | Specific test file confirmed. | RESOLVED — Updated FULLSTACK_STITCHING_CONTRACT.md |
| FSC_CUSTOM_OBJ | FULLSTACK_STITCHING_CONTRACT.md | Custom objects routing mechanism TBD | B — Documentation (via D-002 closure) | FEATURE_SCOPE.md + DESIGN-SPEC.md confirm K-02 advisory shell in C6. No gateway route needed. | K-02 is advisory shell. Routing TBD is moot. | RESOLVED — Updated FULLSTACK_STITCHING_CONTRACT.md |
| OA-001 | RESIDUAL_OWNER_DECISION_REGISTER.md | contacts.delete RBAC scope missing | SAFE-DEFAULT already applied | SD-001: deterministic from 6 existing delete scope examples in rbac-scopes.js. | SAFE-DEFAULT applies. Code change documented. Frontend: hide delete button per scope. | SAFE-DEFAULT (verified, no change) |
| OA-002 | RESIDUAL_OWNER_DECISION_REGISTER.md | JTI blocklist in-memory | SAFE-DEFAULT already applied | SD-002: single-instance C6 launch. | Accept for C6; Redis migration post-launch. | SAFE-DEFAULT (verified, no change) |
| OA-009 | RESIDUAL_OWNER_DECISION_REGISTER.md | Refresh token not revoked on logout | SAFE-DEFAULT already applied | SD-002: bundle with OA-002 in auth sprint. | Accept for C6; fix post-launch. | SAFE-DEFAULT (verified, no change) |
| OA-004 | RESIDUAL_OWNER_DECISION_REGISTER.md | AI inference model selection | AUTO-CLOSED (prior phase) | Rule-based IS the C6 design. LLM is C7 additive. | AUTO-CLOSED. No C6 decision needed. | CONFIRMED CLOSED (prior phase) |
| OA-005 | RESIDUAL_OWNER_DECISION_REGISTER.md | contracts gateway route | AUTO-CLOSED (prior phase) | DESIGN-SPEC.md: no contracts page in C6 scope. Module ready for C7. | AUTO-CLOSED. No C6 action. | CONFIRMED CLOSED (prior phase) |
| G-HIGH-005 | BACKEND_GAP_REGISTER.md | leads.delete scope gap | CLOSED (prior phase) | LEADS_DELETE: 'leads.delete' IS present in rbac-scopes.js line 21. | Not a gap. Confirmed closed. | CONFIRMED CLOSED (prior phase) |

---

## Collapse Rule Reference

| Rule | Description |
|------|-------------|
| A | Answer derivable from code (grep, read, pattern match) |
| B | Answer derivable from documentation |
| C | Answer derivable from CI/CD workflows |
| D | Answer derivable from architecture patterns |
| E | Answer derivable from existing code patterns |
| F | Only one rational interpretation exists |
| SAFE-DEFAULT | Deterministic default documented in prior phase; no new decision needed |

---

*End DECISION_COLLAPSE_REGISTER.md*
