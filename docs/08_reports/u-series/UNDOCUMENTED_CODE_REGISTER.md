# UNDOCUMENTED_CODE_REGISTER.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U6 — Doc to Code Delta Analysis)
**Scope:** Code that exists in the repository but has no corresponding documentation entry in MODULE_INVENTORY.md, ENTITY_INVENTORY.md, API_INVENTORY.md, FEATURE_INVENTORY.md, or WORKFLOW_INVENTORY.md.

---

## UC-001 — Contract Lifecycle Management Module

| Field | Value |
|---|---|
| **ID** | UC-001 |
| **Type** | Backend Python module — complete domain module |
| **Code location** | `backend/src/contract_lifecycle_management/` |
| **Files** | api.py, entities.py, services.py, __init__.py |
| **Gateway route** | None found — no `v1-contracts.routes.js` exists |
| **Frontend page** | None found |
| **Missing from** | MODULE_INVENTORY.md, ENTITY_INVENTORY.md, FEATURE_INVENTORY.md |
| **Impact** | Module is built (4 files) but no gateway route exposes it. Either: (a) planned but not yet routed, (b) accessible via another route, or (c) abandoned after initial scaffold. |
| **Action** | Human review required: is this module active? If yes → add gateway route + document. If no → archive or delete. |

---

## UC-002 — Collections API: 7 Additional Undocumented Endpoints

| Field | Value |
|---|---|
| **ID** | UC-002 |
| **Type** | Gateway API endpoints |
| **Code location** | `backend/gateway/routes/v1-collections.routes.js` |
| **Documented count** | ~4 endpoints |
| **Actual count** | 11 endpoints |
| **Missing from** | API_INVENTORY.md (detailed endpoint table for Collections) |
| **Impact** | 7 live endpoints with no documentation. Callers using only the 4 documented endpoints may miss functionality like reconciliation detail, payment plan management, or advanced dispute handling. |
| **Action** | Read v1-collections.routes.js fully and add all 11 endpoints to API_INVENTORY.md under the Collections section. |

---

## UC-003 — Partners API: 8 Additional Undocumented Endpoints

| Field | Value |
|---|---|
| **ID** | UC-003 |
| **Type** | Gateway API endpoints |
| **Code location** | `backend/gateway/routes/v1-partners.routes.js` |
| **Documented count** | ~5 endpoints |
| **Actual count** | 13 endpoints |
| **Missing from** | API_INVENTORY.md (Partners section shows ~5) |
| **Note** | Partners uses a named sub-router pattern (`partnersRouter`, `dealRegistrationsRouter`) — this caused undercounting in the API_INVENTORY generation pass. |
| **Action** | Read v1-partners.routes.js fully and enumerate all 13 endpoints including deal registrations sub-resource. |

---

## UC-004 — Territories API: 6 Additional Undocumented Endpoints

| Field | Value |
|---|---|
| **ID** | UC-004 |
| **Type** | Gateway API endpoints |
| **Code location** | `backend/gateway/routes/v1-territories.routes.js` |
| **Documented count** | ~5 endpoints |
| **Actual count** | 11 endpoints |
| **Missing from** | API_INVENTORY.md (Territories section) |
| **Action** | Read v1-territories.routes.js and document all 11 endpoints (likely includes territory rules CRUD + manual reassignment + performance endpoints). |

---

## UC-005 — Campaigns API: 5 Additional Undocumented Endpoints

| Field | Value |
|---|---|
| **ID** | UC-005 |
| **Type** | Gateway API endpoints |
| **Code location** | `backend/gateway/routes/v1-campaigns.routes.js` |
| **Documented count** | ~5 endpoints |
| **Actual count** | 10 endpoints |
| **Missing from** | API_INVENTORY.md (Campaigns section) |
| **Action** | Read v1-campaigns.routes.js and document all 10 endpoints. |

---

## UC-006 — WhatsApp Webhooks: 5 Additional Undocumented Event Handlers

| Field | Value |
|---|---|
| **ID** | UC-006 |
| **Type** | Gateway webhook handlers |
| **Code location** | `backend/gateway/routes/v1-whatsapp-webhooks.routes.js` |
| **Documented count** | 1 endpoint ("webhook handler") |
| **Actual count** | 6 endpoints |
| **Missing from** | API_INVENTORY.md (WhatsApp Webhooks section) |
| **Note** | Likely includes: webhook verification (GET), incoming message (POST), status update (POST), delivery receipt (POST), read receipt (POST), error handler (POST). The WhatsApp platform sends distinct event types to distinct paths or the handler dispatches by event type. |
| **Action** | Read v1-whatsapp-webhooks.routes.js and document all 6 paths. |

---

## UC-007 — Payment Webhooks: 2 Additional Undocumented Handlers

| Field | Value |
|---|---|
| **ID** | UC-007 |
| **Type** | Gateway webhook handlers |
| **Code location** | `backend/gateway/routes/v1-payment-webhooks.routes.js` |
| **Documented count** | 1 endpoint |
| **Actual count** | 3 endpoints |
| **Missing from** | API_INVENTORY.md (Payment Webhooks section) |
| **Note** | Likely: JazzCash webhook (POST), Easypaisa webhook (POST), generic payment status (GET or POST). |
| **Action** | Read v1-payment-webhooks.routes.js and document all 3 paths. |

---

## UC-008 — 28 Additional RBAC Scopes in Code

| Field | Value |
|---|---|
| **ID** | UC-008 |
| **Type** | Permission/RBAC scopes |
| **Code location** | `backend/gateway/config/rbac-scopes.js` |
| **Documented count** | 63 (per ROLE_PERMISSION_INVENTORY.md header) |
| **Actual count** | 91 unique scope constants |
| **Missing from** | ROLE_PERMISSION_INVENTORY.md header count (scope list appears complete) |
| **Note** | The scope list body in the inventory appears to cover all 91 scopes (organized by domain). The discrepancy is only in the header count "63" vs actual 91. |
| **Action** | Update ROLE_PERMISSION_INVENTORY.md header: change "63 scopes" to "91 scopes". No scope list changes needed. |

---

## UC-009 — 5 DB Schemas Not Explicitly Sourced in Entity Documentation

| Field | Value |
|---|---|
| **ID** | UC-009 |
| **Type** | Database schemas |
| **Code location** | `backend/db/` directories |
| **Undocumented DBs** | `intelligence_db/`, `notification_db/`, `activity_task_db/`, `feature_flag_db/`, `audit_compliance_db/` |
| **Note** | `activity_task_db/` has its own README.md and self-qc.md in `backend/db/activity_task_db/`. `intelligence_db/` likely holds AI scoring tables. Entities from these databases may be documented in ENTITY_INVENTORY but without explicit DB attribution. |
| **Action** | Add DB source attribution to ENTITY_INVENTORY for entities sourced from these 5 databases. |

---

## UC-010 — `backend/services/summary/` Daily Summary Service

| Field | Value |
|---|---|
| **ID** | UC-010 |
| **Type** | Python service module |
| **Code location** | `backend/services/summary/daily_summary.py` |
| **Missing from** | MODULE_INVENTORY.md (no module entry for daily summary service) |
| **Note** | PROGRESS.md references MR-004 as COMPLETE (2026-05-30): "Daily WhatsApp summary scheduler + 9 tests". This service powers that feature. It exists in code but is not inventoried as a module. |
| **Action** | Add entry to MODULE_INVENTORY.md: "Module 29 — Daily WhatsApp Summary" with reference to services/summary/daily_summary.py and its event trigger (scheduled job or cron). |

---

## UC-011 — Custom Object Framework: No Gateway Route

| Field | Value |
|---|---|
| **ID** | UC-011 |
| **Type** | Missing API surface |
| **Code location** | `backend/src/custom_object_framework/`, `backend/src/custom_objects/` (both confirmed) |
| **Gateway route** | None — no `v1-custom-objects.routes.js` found |
| **Frontend page** | `frontend/src/app/object-builder.html` (K-02) exists |
| **Missing from** | API_INVENTORY.md (note: MODULE_INVENTORY already flags "gateway route not found") |
| **Note** | MODULE_INVENTORY Module 23 already acknowledges "gateway route for custom objects not found in route list; likely proxied via catch-all or not yet surfaced." This confirms the finding. |
| **Action** | Clarify routing mechanism for custom objects. If there is a catch-all route, document it. If the feature is not API-accessible, mark object-builder.html as "frontend-only stub" in FEATURE_INVENTORY. |

---

## Register Summary

| ID | Category | Severity | Action Required |
|---|---|---|---|
| UC-001 | Undocumented module | HIGH | Human review — add route + docs or archive |
| UC-002 | Undocumented API endpoints | MEDIUM | Document 7 additional collections endpoints |
| UC-003 | Undocumented API endpoints | MEDIUM | Document 8 additional partners endpoints |
| UC-004 | Undocumented API endpoints | MEDIUM | Document 6 additional territories endpoints |
| UC-005 | Undocumented API endpoints | MEDIUM | Document 5 additional campaigns endpoints |
| UC-006 | Undocumented API endpoints | MEDIUM | Document 5 additional WhatsApp webhook paths |
| UC-007 | Undocumented API endpoints | LOW | Document 2 additional payment webhook paths |
| UC-008 | Wrong count in header | LOW | Update header count from 63 to 91 |
| UC-009 | Missing DB attribution | LOW | Add DB sources to ENTITY_INVENTORY |
| UC-010 | Undocumented service module | LOW | Add module entry to MODULE_INVENTORY |
| UC-011 | Missing gateway route | MEDIUM | Clarify routing mechanism for custom objects |
