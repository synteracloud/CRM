---
Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: AI
Phase: 3.5 — Project Memory Layer Establishment
---

# FINAL CLASSIFIED REGISTER — Project Memory Layer

> Single entry point for all classified items from all phases (U0 through Phase 3.5).
> Every item appears here exactly once. Future AI sessions load this first, then follow Register Links for full detail.
> Consolidated from: FINAL_CLASSIFIED_REGISTER.md (Phase 2.97), DECISION_COLLAPSE_REGISTER.md (Phase 3.25), OWNER_REQUIRED_COMPRESSION_REPORT.md (Phase 2.97), UNRESOLVABLE_ITEMS_REGISTER.md (Phase 3.25), APPROVAL_ELIMINATION_REPORT.md (Phase 2.9), RESIDUAL_OWNER_DECISION_REGISTER.md (Phase 2.9), OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md.

---

## How to Read This Register

| Column | Meaning |
|--------|---------|
| Item ID | Unique identifier carried across all phases |
| Title | Brief description of the item |
| Classification | Final category (see legend below) |
| Status | Current state at time of last review |
| Evidence Source | Document where the item originated |
| Resolution Source | Document where the item was resolved/classified |
| Current State | One-sentence operational state |
| Register Link | Which register file holds the full detail entry |

**Classification Legend:**
| Classification | Meaning |
|---------------|---------|
| AUTO_CLOSED | Resolved directly from repository evidence (code, architecture, contracts, authority docs). No action needed. |
| SAFE_DEFAULT | A deterministic default has been documented and accepted. Implementation proceeds on the default unless owner explicitly objects. |
| OWNER_DECISION | Genuinely requires human commercial / legal / credential / product-scope decision. |
| EXTERNAL_DEPENDENCY | Requires external provisioning (vendor credentials, government registration, third-party approval). |
| OUT_OF_SCOPE | Intentionally deferred to a future phase. Not a gap — a planned deferral. |

---

## Section 1: AUTO_CLOSED Items (19 items)

> All resolved from repository evidence. No action required. Full detail: AUTO_CLOSED_REGISTER.md

| Item ID | Title | Classification | Status | Evidence Source | Resolution Source | Current State | Register Link |
|---------|-------|----------------|--------|-----------------|-------------------|---------------|---------------|
| OA-004 | AI inference model selection | AUTO_CLOSED | Closed | OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Rule-based scoring IS the designed C6 behavior. LLM integration is C7 additive scope. No C6 decision needed. | AUTO_CLOSED_REGISTER.md |
| OA-005 | contracts_lifecycle_management no gateway route | AUTO_CLOSED | Closed | OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | C7 scope confirmed by DESIGN-SPEC.md. No contracts frontend page in C6. Backend module awaits C7 gateway route. | AUTO_CLOSED_REGISTER.md |
| D-002 | Custom objects module product scope (C6 vs C7) | AUTO_CLOSED | Closed 2026-06-23 | UNRESOLVABLE_ITEMS_REGISTER.md | DECISION_COLLAPSE_REGISTER.md Phase 3.25 | K-02 is a C6 built advisory shell. FEATURE_SCOPE.md §22 Feature 129 Status=Built. No gateway route needed. | AUTO_CLOSED_REGISTER.md |
| D-003 | 5 entity schema attributions unverified | AUTO_CLOSED | Closed | OWNER_REQUIRED_COMPRESSION_REPORT.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Investigation task, not owner decision. Backend team reads 5 schema.sql files directly to verify. | AUTO_CLOSED_REGISTER.md |
| G-HIGH-005 | leads.delete scope gap | AUTO_CLOSED | Closed Phase 2.9 | BACKEND_GAP_REGISTER.md | APPROVAL_ELIMINATION_REPORT.md | LEADS_DELETE: 'leads.delete' IS present in rbac-scopes.js line 21. Not a gap. False alarm. | AUTO_CLOSED_REGISTER.md |
| G-MED-002 | SLA breach events not emitted | AUTO_CLOSED | Closed Phase 2.9 | BACKEND_GAP_REGISTER.md | APPROVAL_ELIMINATION_REPORT.md | Confirmed emitted from services/cases/service.py lines 120–144. Not a gap. | AUTO_CLOSED_REGISTER.md |
| G-MED-003 | Dev token endpoint active in production | AUTO_CLOSED | Closed Phase 2.9 | BACKEND_GAP_REGISTER.md | APPROVAL_ELIMINATION_REPORT.md | JWT_SECRET always set in render.yaml line 37; endpoint is inactive in production. | AUTO_CLOSED_REGISTER.md |
| G-LOW-001 | DB connection pool size not configurable | AUTO_CLOSED | Closed Phase 2.9 | BACKEND_GAP_REGISTER.md | APPROVAL_ELIMINATION_REPORT.md | Pool configurable via DB_POOL_MAX env var in gateway/db/pool.js. Not a gap. | AUTO_CLOSED_REGISTER.md |
| O-TBD-001 | EmailStr vs plain str in FastAPI models | AUTO_CLOSED | Resolved Phase 3.25 | TBD_RESOLUTION_REGISTER.md | DECISION_COLLAPSE_REGISTER.md | Email is plain str type. No EmailStr. Confirmed by grep. VALIDATION_RULES.md updated. | AUTO_CLOSED_REGISTER.md |
| O-TBD-002 | Phone number validation regex in Pydantic | AUTO_CLOSED | Resolved Phase 3.25 | TBD_RESOLUTION_REGISTER.md | DECISION_COLLAPSE_REGISTER.md | No phone regex validator exists. E.164 is convention + DB uniqueness only. VALIDATION_RULES.md updated. | AUTO_CLOSED_REGISTER.md |
| O-TBD-003 | CNIC/NTN/STRN database fields | AUTO_CLOSED | Resolved Phase 3.25 | TBD_RESOLUTION_REGISTER.md | DECISION_COLLAPSE_REGISTER.md | Not DB fields. Optional JazzCash payment metadata only (pp_CNIC in jazzcash.py). | AUTO_CLOSED_REGISTER.md |
| O-TBD-004 | UUID type in FastAPI Pydantic models | AUTO_CLOSED | Resolved Phase 3.25 | TBD_RESOLUTION_REGISTER.md | DECISION_COLLAPSE_REGISTER.md | UUID fields use uuid.UUID type in Pydantic; generated with uuid4(). Confirmed from support_console entities. | AUTO_CLOSED_REGISTER.md |
| O-TBD-005 | Event schemas for 6 core events | AUTO_CLOSED | Resolved Phase 3.25 | TBD_RESOLUTION_REGISTER.md | DECISION_COLLAPSE_REGISTER.md | All 6 event schemas documented in backend/docs/infrastructure/event-catalog.md. CONTRACT_VERSION_REGISTRY.md updated. | AUTO_CLOSED_REGISTER.md |
| O-TBD-006 | Route deprecation strategy | AUTO_CLOSED | Resolved Phase 3.25 | TBD_RESOLUTION_REGISTER.md | DECISION_COLLAPSE_REGISTER.md | No deprecation strategy implemented for C6. Single v1 prefix. Needed when v2 is planned (C7+). | AUTO_CLOSED_REGISTER.md |
| EVENT_BUS_TBD | Event dispatch mechanism (in-process or polling) | AUTO_CLOSED | Resolved Phase 3.25 | EVENT_AND_QUEUE_ARCHITECTURE.md | DECISION_COLLAPSE_REGISTER.md | Events dispatched in-process via InMemoryEventBus class. Confirmed from backend/src/event_bus/core.py. | AUTO_CLOSED_REGISTER.md |
| OUTBOX_TBD | Outbox publisher confirmed absent | AUTO_CLOSED | Resolved Phase 3.25 | EVENT_AND_QUEUE_ARCHITECTURE.md | DECISION_COLLAPSE_REGISTER.md | Outbox publisher CONFIRMED ABSENT. Outbox table exists in DB but no publisher code. G-HIGH-004 SAFE_DEFAULT applies. | AUTO_CLOSED_REGISTER.md |
| FSC_TEST_TBD_1 | Backend tests for customer_360_cdp | AUTO_CLOSED | Resolved Phase 3.25 | FULLSTACK_STITCHING_CONTRACT.md | DECISION_COLLAPSE_REGISTER.md | backend/tests/test_customer_360_cdp.py confirmed present. | AUTO_CLOSED_REGISTER.md |
| FSC_TEST_TBD_2 | Backend tests for lead_management | AUTO_CLOSED | Resolved Phase 3.25 | FULLSTACK_STITCHING_CONTRACT.md | DECISION_COLLAPSE_REGISTER.md | backend/tests/test_lead_management.py confirmed present. | AUTO_CLOSED_REGISTER.md |
| FSC_TEST_TBD_3 | Backend tests for sales_cockpit | AUTO_CLOSED | Resolved Phase 3.25 | FULLSTACK_STITCHING_CONTRACT.md | DECISION_COLLAPSE_REGISTER.md | backend/tests/test_sales_cockpit_workspace.py confirmed present. | AUTO_CLOSED_REGISTER.md |
| FSC_TEST_TBD_4 | Backend tests for subscription/billing | AUTO_CLOSED | Resolved Phase 3.25 | FULLSTACK_STITCHING_CONTRACT.md | DECISION_COLLAPSE_REGISTER.md | 3 test files confirmed: test_revenue_recognition.py, test_subscription_billing.py, test_usage_billing.py. | AUTO_CLOSED_REGISTER.md |
| FSC_TEST_TBD_5 | Backend tests for omnichannel_inbox | AUTO_CLOSED | Resolved Phase 3.25 | FULLSTACK_STITCHING_CONTRACT.md | DECISION_COLLAPSE_REGISTER.md | backend/tests/test_omnichannel_inbox.py confirmed present. | AUTO_CLOSED_REGISTER.md |
| FSC_CUSTOM_OBJ | Custom objects routing mechanism TBD | AUTO_CLOSED | Resolved Phase 3.25 | FULLSTACK_STITCHING_CONTRACT.md | DECISION_COLLAPSE_REGISTER.md | K-02 is advisory shell per FEATURE_SCOPE.md + DESIGN-SPEC.md. No gateway route needed. Routing TBD is moot. | AUTO_CLOSED_REGISTER.md |
| P-TBD-003 | Frontend scope-based UI gating | AUTO_CLOSED | Resolved Phase 3.25 | TBD_RESOLUTION_REGISTER.md | DECISION_COLLAPSE_REGISTER.md | Scope gating IS defined in docs/03_frontend_authority/FRONTEND_PERMISSION_MATRIX.md for all 75 pages. | AUTO_CLOSED_REGISTER.md |
| CRIT-002 | python-jose version drift | AUTO_CLOSED | Closed U10 | BACKEND_GAP_REGISTER.md | Phase U10 audit | venv has 3.5.0; pip-audit.json was stale. Not a real gap. | AUTO_CLOSED_REGISTER.md |

---

## Section 2: SAFE_DEFAULT Items (12 items)

> All resolved via deterministic safe defaults. Implementation proceeds on the default. Full detail: SAFE_DEFAULT_REGISTER.md

| Item ID | Title | Classification | Status | Evidence Source | Resolution Source | Current State | Register Link |
|---------|-------|----------------|--------|-----------------|-------------------|---------------|---------------|
| OA-001 (SD-001) | contacts.delete RBAC scope missing | SAFE_DEFAULT | Pending code fix | OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Default: grant CONTACTS_DELETE to tenant_admin + super_admin. Frontend hides delete button for all other roles. 2-line code change pending. | SAFE_DEFAULT_REGISTER.md |
| OA-002 (SD-002) | JTI blocklist in-memory only | SAFE_DEFAULT | Accepted for C6 | OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Accept in-process Set() for C6 single instance. Redis migration in Post-C6 Auth Sprint bundled with OA-009. | SAFE_DEFAULT_REGISTER.md |
| OA-009 (SD-002) | Refresh token not revoked on logout | SAFE_DEFAULT | Accepted for C6 | OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Accept for C6. Bundle Redis del(rt:{token}) fix with OA-002 in Post-C6 Auth Sprint. | SAFE_DEFAULT_REGISTER.md |
| OA-006 (SD-003) | Security test artifacts disposition | SAFE_DEFAULT | Pending hygiene pass | OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Move tests/security/*.json to docs/reports/security/ as compliance evidence. | SAFE_DEFAULT_REGISTER.md |
| OA-007 (SD-004) | Load test reports disposition | SAFE_DEFAULT | Pending hygiene pass | OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Move c5-prod-*.html to docs/reports/load/. Gitignore non-production reports. | SAFE_DEFAULT_REGISTER.md |
| OA-008 (SD-005) | Password hashing SHA-256 not bcrypt | SAFE_DEFAULT | Accepted for C6 | OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Accept SHA-256 for C6. Plan transparent re-hash-on-login (bcrypt) for C7 Security Sprint. | SAFE_DEFAULT_REGISTER.md |
| G-HIGH-003 (SD-006) | No message broker | SAFE_DEFAULT | Accepted for C6 | BACKEND_GAP_REGISTER.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Accept in-process events for C6 single instance. Evaluate broker at multi-instance scale (C7). | SAFE_DEFAULT_REGISTER.md |
| G-HIGH-004 (SD-007) | Outbox publisher not implemented | SAFE_DEFAULT | Accepted for C6 | BACKEND_GAP_REGISTER.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Accept for C6 (payment domain in stub mode). Implement outbox publisher when OA-003 payment credentials activate. | SAFE_DEFAULT_REGISTER.md |
| G-MED-001 (SD-008) | No external task scheduler | SAFE_DEFAULT | Accepted for C6 | BACKEND_GAP_REGISTER.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Accept for C6. task_schedule table unused. Implement Celery Beat or APScheduler in C7. | SAFE_DEFAULT_REGISTER.md |
| D-005 (SD-009) | 4 backend archive docs in wrong location | SAFE_DEFAULT | Pending hygiene pass | OWNER_REQUIRED_COMPRESSION_REPORT.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Move backend/docs/phase4-gap-register.md and 3 others to docs/08_reports/ via SAFE_REPOSITORY_HYGIENE. | SAFE_DEFAULT_REGISTER.md |
| G-LOW-003 (SD-010) | Rate limit fails open on Redis outage | SAFE_DEFAULT | Accepted for C6 | BACKEND_GAP_REGISTER.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Accept fail-open pattern for C6. Render.com managed Redis has high uptime. Note for C7 hardening. | SAFE_DEFAULT_REGISTER.md |
| G-LOW-004 (SD-011) | No PostgreSQL RLS | SAFE_DEFAULT | Permanent | BACKEND_GAP_REGISTER.md | OWNER_REQUIRED_COMPRESSION_REPORT.md | Accepted architecture trade-off. Application-layer isolation enforced by semgrep CI. No change planned. | SAFE_DEFAULT_REGISTER.md |

---

## Section 3: OWNER_DECISION Items (2 items)

> Genuine product/business decisions that require owner input. Full detail: OWNER_DECISION_REGISTER.md

| Item ID | Title | Classification | Status | Evidence Source | Resolution Source | Current State | Register Link |
|---------|-------|----------------|--------|-----------------|-------------------|---------------|---------------|
| OA-001 | contacts.delete RBAC scope — who gets it | OWNER_DECISION | Awaiting owner | OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md | RESIDUAL_OWNER_DECISION_REGISTER.md | SAFE_DEFAULT documents tenant_admin + super_admin. Owner must approve the 2-line code change to rbac-scopes.js (TIER 2). | OWNER_DECISION_REGISTER.md |

*Note: OA-001 appears in SAFE_DEFAULT (what to do) and OWNER_DECISION (code change approval required for rbac-scopes.js per governance TIER 2 rule). The safe default is fully documented; only the TIER 2 code-change approval is pending.*

---

## Section 4: EXTERNAL_DEPENDENCY Items (5 items)

> Items requiring external provisioning. Development is NOT blocked. Full detail: EXTERNAL_DEPENDENCY_REGISTER.md

| Item ID | Title | Classification | Status | Evidence Source | Resolution Source | Current State | Register Link |
|---------|-------|----------------|--------|-----------------|-------------------|---------------|---------------|
| OA-003 | JazzCash live payment credentials | EXTERNAL_DEPENDENCY | Unresolved | UNRESOLVABLE_ITEMS_REGISTER.md | Phase 3.25 confirms unresolvable from code | Payment adapters in stub mode (JAZZCASH_STUB_MODE=true). Revenue collection blocked. Free-tier CRM launch viable. | EXTERNAL_DEPENDENCY_REGISTER.md |
| OA-003b | Easypaisa live payment credentials | EXTERNAL_DEPENDENCY | Unresolved | UNRESOLVABLE_ITEMS_REGISTER.md | Phase 3.25 confirms unresolvable from code | Easypaisa adapter in stub mode (EASYPAISA_STUB_MODE=true). Bundled with JazzCash merchant account application. | EXTERNAL_DEPENDENCY_REGISTER.md |
| G-MED-005 | Urdu WhatsApp template approval | EXTERNAL_DEPENDENCY | Unresolved | UNRESOLVABLE_ITEMS_REGISTER.md | Phase 3.25 confirms unresolvable from code | Urdu strings exist with UR_TODO markers. Native Urdu speaker review required. English campaigns unaffected. | EXTERNAL_DEPENDENCY_REGISTER.md |
| MR-001 | Facebook/Instagram lead capture | EXTERNAL_DEPENDENCY | Blocked | AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS | AI_OPERATING_CONTEXT.md | Not rendered in UI (hidden div data-unblock=MR-001). Requires Meta Business Manager account + API approval. | EXTERNAL_DEPENDENCY_REGISTER.md |
| MR-003 | Voice note transcription | EXTERNAL_DEPENDENCY | Blocked | AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS | AI_OPERATING_CONTEXT.md | Microphone icon disabled in UI. Requires transcription provider selection + credentials. | EXTERNAL_DEPENDENCY_REGISTER.md |

---

## Section 5: OUT_OF_SCOPE Items (8 items)

> Intentionally deferred. Not gaps — planned deferrals with documented future phase. Full detail: OUT_OF_SCOPE_REGISTER.md

| Item ID | Title | Classification | Status | Evidence Source | Resolution Source | Current State | Register Link |
|---------|-------|----------------|--------|-----------------|-------------------|---------------|---------------|
| OA-005 | contracts_lifecycle_management gateway route | OUT_OF_SCOPE | Deferred to C7 | OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md | DESIGN-SPEC.md | Backend module complete (12 endpoints). No C6 frontend page. Gateway route to be created in C7 when contracts page is built. | OUT_OF_SCOPE_REGISTER.md |
| AI-001 | AI inference model / LLM provider selection | OUT_OF_SCOPE | Deferred to C7 | AI_OPERATING_CONTEXT.md | FEATURE_SCOPE.md | Rule-based scoring IS the C6 production model. LLM integration is C7 additive scope. Constraint AI-001 remains. | OUT_OF_SCOPE_REGISTER.md |
| MR-007 | Kuickpay adapter | OUT_OF_SCOPE | Blocked / Deferred | AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS | AI_OPERATING_CONTEXT.md | Not rendered in UI. Requires Kuickpay API credentials. Post-C6 activation. | OUT_OF_SCOPE_REGISTER.md |
| AUTH-C7 | Bcrypt password migration (re-hash on login) | OUT_OF_SCOPE | Deferred to C7 | OWNER_REQUIRED_COMPRESSION_REPORT.md SD-005 | OWNER_REQUIRED_COMPRESSION_REPORT.md | SHA-256 accepted for C6. Transparent bcrypt re-hash-on-login planned for C7 Security Sprint. | OUT_OF_SCOPE_REGISTER.md |
| AUTH-C7b | Redis JTI blocklist + refresh token revocation | OUT_OF_SCOPE | Deferred Post-C6 | OWNER_REQUIRED_COMPRESSION_REPORT.md SD-002 | OWNER_REQUIRED_COMPRESSION_REPORT.md | Both OA-002 and OA-009 bundled into Post-C6 Auth Sprint. Redis migration path fully documented. | OUT_OF_SCOPE_REGISTER.md |
| BROKER-C7 | Message broker (Celery / RabbitMQ / Redis Streams) | OUT_OF_SCOPE | Deferred to C7 | OWNER_REQUIRED_COMPRESSION_REPORT.md SD-006 | OWNER_REQUIRED_COMPRESSION_REPORT.md | In-process InMemoryEventBus accepted for C6. Broker evaluation at multi-instance scale. | OUT_OF_SCOPE_REGISTER.md |
| SCHED-C7 | External task scheduler (Celery Beat / APScheduler) | OUT_OF_SCOPE | Deferred to C7 | OWNER_REQUIRED_COMPRESSION_REPORT.md SD-008 | OWNER_REQUIRED_COMPRESSION_REPORT.md | task_schedule table exists but unused. Scheduler implementation deferred to C7. | OUT_OF_SCOPE_REGISTER.md |
| FBR-COMP | FBR invoice formatting compliance | OUT_OF_SCOPE | Pending legal review | AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS | AI_OPERATING_CONTEXT.md | Invoice formatting requirements not verified. FBR NTN/STRN field requirements pending legal review. | OUT_OF_SCOPE_REGISTER.md |

---

## Summary Counts

| Classification | Count | Register File |
|---------------|-------|---------------|
| AUTO_CLOSED | 24 | AUTO_CLOSED_REGISTER.md |
| SAFE_DEFAULT | 12 | SAFE_DEFAULT_REGISTER.md |
| OWNER_DECISION | 1 | OWNER_DECISION_REGISTER.md |
| EXTERNAL_DEPENDENCY | 5 | EXTERNAL_DEPENDENCY_REGISTER.md |
| OUT_OF_SCOPE | 8 | OUT_OF_SCOPE_REGISTER.md |
| **TOTAL** | **50** | — |

---

## Quick Reference: Active Blockers

**Commercial launch blockers (must resolve before revenue):**
- OA-003 / OA-003b: JazzCash + Easypaisa merchant account applications

**Code fix pending owner approval:**
- OA-001: contacts.delete scope — 2-line rbac-scopes.js change (TIER 2)

**Feature activation blockers (non-blocking for launch):**
- G-MED-005: Urdu WhatsApp templates — native speaker review
- MR-001: Facebook/Instagram — Meta Business Manager
- MR-003: Voice transcription — provider selection
- AI-001: LLM inference — deferred to C7

**Everything else: resolved, defaulted, or deferred with documented plans.**

---

*End FINAL_CLASSIFIED_REGISTER.md — Phase 3.5 (2026-06-23)*
