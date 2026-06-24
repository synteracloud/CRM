# STALE_DOC_CLAIMS_REGISTER.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U6 — Doc to Code Delta Analysis)
**Scope:** Documentation claims that do not match actual code state.

---

## SC-001 — API_INVENTORY.md: Total Route Count Claim

| Field | Value |
|---|---|
| **ID** | SC-001 |
| **Source Doc** | `docs/reports/u-series/API_INVENTORY.md` |
| **Stale Claim** | "~198" total routes |
| **Actual State** | 228 routes across 44 route files |
| **Delta** | +30 routes undocumented |
| **Root Cause** | Two route files use non-standard sub-router naming (`casesRouter`, `supportRouter`, `partnersRouter`, `dealRegistrationsRouter`) which caused the original counting to read 0 routes for v1-cases and v1-partners. Also, several domains grew significantly post-inventory (territories, campaigns, collections). |
| **Fix** | Update summary table in API_INVENTORY.md to reflect actual per-domain counts. |

---

## SC-002 — API_INVENTORY.md: Collections Domain Count

| Field | Value |
|---|---|
| **ID** | SC-002 |
| **Source Doc** | `docs/reports/u-series/API_INVENTORY.md` |
| **Stale Claim** | "Collections: ~4 endpoints" |
| **Actual State** | 11 endpoints in v1-collections.routes.js |
| **Delta** | +7 — nearly 3x documented count |
| **Root Cause** | Sprint 5B collections work expanded the API significantly beyond the original ~4 basic CRUD endpoints. Documentation not updated. |
| **Fix** | Read v1-collections.routes.js and enumerate all 11 endpoints in API_INVENTORY.md. |

---

## SC-003 — API_INVENTORY.md: Partners Domain Count

| Field | Value |
|---|---|
| **ID** | SC-003 |
| **Source Doc** | `docs/reports/u-series/API_INVENTORY.md` |
| **Stale Claim** | "Partners: ~5 endpoints" |
| **Actual State** | 13 endpoints in v1-partners.routes.js (using named sub-routers) |
| **Delta** | +8 — more than 2x documented count |
| **Root Cause** | Named sub-router pattern not detected by original inventory sweep. Partners module has deal registrations as a sub-resource (additional 5+ routes beyond core CRUD). |
| **Fix** | Re-enumerate v1-partners.routes.js and add deal registrations sub-resource routes. |

---

## SC-004 — API_INVENTORY.md: Territories Domain Count

| Field | Value |
|---|---|
| **ID** | SC-004 |
| **Source Doc** | `docs/reports/u-series/API_INVENTORY.md` |
| **Stale Claim** | "Territories: ~5 endpoints" |
| **Actual State** | 11 endpoints in v1-territories.routes.js |
| **Delta** | +6 — more than 2x documented count |
| **Root Cause** | Territory management includes territory rules CRUD, manual assignment, performance views, and assignment history — all added in Sprint 5B but not reflected in inventory count. |
| **Fix** | Read and enumerate all 11 endpoints. |

---

## SC-005 — API_INVENTORY.md: Campaigns Domain Count

| Field | Value |
|---|---|
| **ID** | SC-005 |
| **Source Doc** | `docs/reports/u-series/API_INVENTORY.md` |
| **Stale Claim** | "Campaigns: ~5 endpoints" |
| **Actual State** | 10 endpoints in v1-campaigns.routes.js |
| **Delta** | +5 — 2x documented count |
| **Root Cause** | Sprint 5B campaigns included segment management, template linking, and activation endpoints beyond basic CRUD. |
| **Fix** | Read and enumerate all 10 endpoints. |

---

## SC-006 — API_INVENTORY.md: WhatsApp Webhooks Count

| Field | Value |
|---|---|
| **ID** | SC-006 |
| **Source Doc** | `docs/reports/u-series/API_INVENTORY.md` |
| **Stale Claim** | "WhatsApp Webhooks: 1 endpoint" |
| **Actual State** | 6 endpoints in v1-whatsapp-webhooks.routes.js |
| **Delta** | +5 — 6x documented count |
| **Root Cause** | The WhatsApp platform requires multiple webhook paths: verification challenge (GET), incoming messages (POST), message status updates (POST), delivery reports, etc. The original inventory counted 1 (likely just the main POST handler). |
| **Fix** | Enumerate all 6 webhook paths and their event types. |

---

## SC-007 — API_INVENTORY.md: Communications Domain Count

| Field | Value |
|---|---|
| **ID** | SC-007 |
| **Source Doc** | `docs/reports/u-series/API_INVENTORY.md` |
| **Stale Claim** | "Communications: ~3 endpoints" |
| **Actual State** | 1 endpoint in v1-communications.routes.js |
| **Delta** | -2 — overdocumented |
| **Root Cause** | Communications module may have been planned with more endpoints but only 1 was implemented. Or documentation counted communications functionality spread across WhatsApp webhooks and inbox routes (which are separate files). |
| **Fix** | Verify whether the 2 missing endpoints were merged into another route file or deferred. Update claim to "1 endpoint". |

---

## SC-008 — API_INVENTORY.md: Tenants Domain Count

| Field | Value |
|---|---|
| **ID** | SC-008 |
| **Source Doc** | `docs/reports/u-series/API_INVENTORY.md` |
| **Stale Claim** | "Tenants: ~4 endpoints" |
| **Actual State** | 1 endpoint in v1-tenants.routes.js |
| **Delta** | -3 — significantly overdocumented |
| **Root Cause** | Tenant management is mostly internal (registration via /auth/register, admin operations handled separately). The public tenant API may have been planned with 4 routes but only 1 exists. |
| **Fix** | Verify intended vs implemented. Update claim to "1 endpoint". |

---

## SC-009 — ROLE_PERMISSION_INVENTORY.md: Scope Count Header

| Field | Value |
|---|---|
| **ID** | SC-009 |
| **Source Doc** | `docs/reports/u-series/ROLE_PERMISSION_INVENTORY.md` |
| **Stale Claim** | "63 scopes from rbac-scopes.js" (line: "Complete Scope Inventory (63 scopes)") |
| **Actual State** | 91 unique scope constants in SCOPES object |
| **Delta** | +28 scopes — documentation count not updated after Sprint 5B additions |
| **Root Cause** | Sprint 5B added scopes for: emails, forecasts, pricing, billing, reports, integrations, compliance, privacy, marketing, audit.logs, users.manage_roles, orders.create, quotes.accept, invoices.create. |
| **Fix** | Update ROLE_PERMISSION_INVENTORY.md section header from "63 scopes" to "91 scopes". The scope list itself appears complete. |

---

## SC-010 — MODULE_INVENTORY.md: Module 19 Claims 63 Scopes

| Field | Value |
|---|---|
| **ID** | SC-010 |
| **Source Doc** | `docs/reports/u-series/MODULE_INVENTORY.md` |
| **Stale Claim** | Module 19 (Identity & Access Management) notes: "Full RBAC system (7 canonical roles, 63 scopes)." |
| **Actual State** | 91 scopes |
| **Fix** | Update Module 19 notes to "91 scopes". |

---

## SC-011 — MODULE_INVENTORY.md: Module 20 Path Format Inconsistency

| Field | Value |
|---|---|
| **ID** | SC-011 |
| **Source Doc** | `docs/reports/u-series/MODULE_INVENTORY.md` |
| **Stale Claim** | Module 20 (Activity/Task Tracking): "Backend module: services/activity.py, services/followup.py" (bare file paths) |
| **Actual State** | Code is in `backend/services/activity/` (directory with multiple .py files), `backend/services/followup/` (directory). All other modules use `src/` paths. |
| **Delta** | Path format inconsistency — all other modules use `src/module_name/`, this one uses `services/filename.py` format |
| **Fix** | Update Module 20 to: "Backend module: `backend/services/activity/` (engine.py, entities.py, __init__.py), `backend/services/followup/` (engine.py, entities.py, scheduler.py, overdue.py, __init__.py)" |

---

## SC-012 — ENTITY_INVENTORY.md: Undocumented DB Source Databases

| Field | Value |
|---|---|
| **ID** | SC-012 |
| **Source Doc** | `docs/reports/u-series/ENTITY_INVENTORY.md` |
| **Stale Claim** | Entity inventory header sources only: `db/identity_auth_db`, `db/lead_management_db`, `db/contact_account_db`, `db/org_tenant_db`, `db/opportunity_db`, `db/quote_order_db`, `db/transaction_db`, `db/workflow_db`, `db/campaign_db`, `db/case_ticket_db`, `db/knowledge_db`, `db/territory_db`, `db/messaging_db` |
| **Actual State** | 5 additional databases present: `intelligence_db/`, `notification_db/`, `activity_task_db/`, `feature_flag_db/`, `audit_compliance_db/` |
| **Fix** | Review schema.sql files in these 5 databases and add their entities to ENTITY_INVENTORY.md with correct DB attribution. |

---

## SC-013 — API_INVENTORY.md: Cases Count Slightly Off

| Field | Value |
|---|---|
| **ID** | SC-013 |
| **Source Doc** | `docs/reports/u-series/API_INVENTORY.md` |
| **Stale Claim** | "Cases: 13 endpoints" |
| **Actual State** | 14 endpoints (casesRouter: 10 + supportRouter: 4 in v1-cases.routes.js) |
| **Delta** | +1 — near match; originally undercounted because casesRouter uses non-standard naming |
| **Fix** | Update count from 13 to 14. |

---

## SC-014 — MODULE_INVENTORY.md: No Entry for Contract Lifecycle Management

| Field | Value |
|---|---|
| **ID** | SC-014 |
| **Source Doc** | `docs/reports/u-series/MODULE_INVENTORY.md` |
| **Stale Claim** | No module entry for contract lifecycle management |
| **Actual State** | `backend/src/contract_lifecycle_management/` exists with api.py, entities.py, services.py, __init__.py |
| **Severity** | HIGH — module with full API, entity, and service layers exists with no documentation |
| **Fix** | Human decision: if active, add Module 29 (or appropriate number) to MODULE_INVENTORY. If not active, archive the module or mark as planned. |

---

## SC-015 — FEATURE_INVENTORY.md: Page Count vs Actual

| Field | Value |
|---|---|
| **ID** | SC-015 |
| **Source Doc** | `docs/reports/u-series/FEATURE_INVENTORY.md` and general documentation |
| **Stale Claim** | 75 custom pages + 96 library pages = 171 total pages |
| **Actual State** | 169 HTML files in `frontend/src/app/` |
| **Delta** | -2 pages |
| **Root Cause** | Unknown — 2 pages expected from the doc count are not present in app/. Possible causes: 2 pages were consolidated, renamed, or the library page count was miscounted. |
| **Fix** | Verify whether any pages were intentionally removed or consolidated. Update page count in documentation. |

---

## Register Summary

| ID | Source Doc | Severity | Type |
|---|---|---|---|
| SC-001 | API_INVENTORY.md | MEDIUM | Route total count wrong |
| SC-002 | API_INVENTORY.md | MEDIUM | Collections: 11 vs ~4 |
| SC-003 | API_INVENTORY.md | MEDIUM | Partners: 13 vs ~5 |
| SC-004 | API_INVENTORY.md | MEDIUM | Territories: 11 vs ~5 |
| SC-005 | API_INVENTORY.md | MEDIUM | Campaigns: 10 vs ~5 |
| SC-006 | API_INVENTORY.md | MEDIUM | WhatsApp webhooks: 6 vs 1 |
| SC-007 | API_INVENTORY.md | LOW | Communications: 1 vs ~3 |
| SC-008 | API_INVENTORY.md | LOW | Tenants: 1 vs ~4 |
| SC-009 | ROLE_PERMISSION_INVENTORY.md | LOW | Scope count: 91 vs 63 |
| SC-010 | MODULE_INVENTORY.md | LOW | Scope count repeated: 63 |
| SC-011 | MODULE_INVENTORY.md | LOW | Module 20 path format inconsistency |
| SC-012 | ENTITY_INVENTORY.md | LOW | 5 DB schemas not sourced |
| SC-013 | API_INVENTORY.md | LOW | Cases: 14 vs 13 |
| SC-014 | MODULE_INVENTORY.md | HIGH | Missing module entry |
| SC-015 | FEATURE_INVENTORY.md | LOW | Page count -2 |

**Total stale claims: 15 (2 HIGH, 6 MEDIUM, 7 LOW)**
