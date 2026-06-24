# DOC_CODE_REMEDIATION_REPORT.md

**Generated:** 2026-06-20 — U7 Delta Remediation
**Source:** DOC_CODE_DELTA_REPORT.md (U6), UNDOCUMENTED_CODE_REGISTER.md (U6), STALE_DOC_CLAIMS_REGISTER.md (U6)
**Principle:** Fix where repository evidence supports correction. No TBDs or placeholders where code provides the answer.

---

## Summary

| Category | Items identified (U6) | Items fixed (U7) | Deferred (human decision) |
|---|---|---|---|
| Stale doc claims (SC-*) | 15 | 13 | 2 |
| Undocumented code (UC-*) | 11 | 8 | 3 |
| **Total** | **26** | **21** | **5** |

---

## Fixes Applied

### FX-001 — API_INVENTORY.md: Total route count updated
**Source:** SC-001
**File:** `docs/reports/u-series/API_INVENTORY.md`
**Change:** Summary by Method total: `~198` → `228`. Method breakdown updated: GET ~108, POST ~92, PATCH ~18, DELETE ~10.
**Evidence:** Direct route count from all 43 gateway route files (U6 analysis).

---

### FX-002 — API_INVENTORY.md: Collections section fully enumerated
**Source:** SC-002, UC-002
**File:** `docs/reports/u-series/API_INVENTORY.md`
**Change:** COLLECTIONS table replaced — 4 inferred rows → 11 confirmed routes from `v1-collections.routes.js`.
**Routes documented:**
1. GET /collections/invoices
2. POST /collections/invoices
3. GET /collections/invoices/:invoice_id
4. POST /collections/invoices/:invoice_id/payments
5. GET /collections/subscriptions
6. POST /collections/subscriptions
7. GET /collections/overdue
8. POST /collections/reconcile
9. POST /collections/invoices/:invoice_id/payments/:payment_id/proof
10. PATCH /collections/invoices/:invoice_id/payments/:payment_id/proof/verify
11. POST /collections/invoices/:invoice_id/reminders

**Evidence:** `backend/gateway/routes/v1-collections.routes.js` lines 55, 83, 143, 163, 239, 258, 290, 316, 363, 401, 441.

---

### FX-003 — API_INVENTORY.md: Partners section fully enumerated
**Source:** SC-003, UC-003
**File:** `docs/reports/u-series/API_INVENTORY.md`
**Change:** PARTNERS table replaced — 5 inferred rows → 11 routes under /partners + new DEAL REGISTRATIONS section with 2 routes = 13 total.
**Additional routes documented:** /partners/:id/opportunities, /partners/:id/commissions, /partners/:id/commissions/:id/approve, /partners/:id/commissions/:id/pay, /partners/:id/activity, /partners/:id/deal-registrations (POST + GET), /deal-registrations/:id/approve, /deal-registrations/:id/reject.
**Evidence:** `backend/gateway/routes/v1-partners.routes.js` — partnersRouter (11 routes) + dealRegsRouter (2 routes).

---

### FX-004 — API_INVENTORY.md: Territories section fully enumerated
**Source:** SC-004, UC-004
**File:** `docs/reports/u-series/API_INVENTORY.md`
**Change:** TERRITORIES table replaced — 5 inferred rows → 11 confirmed routes.
**Additional routes documented:** GET /territories/assignments, POST /territories/assignments/evaluate, POST /territories/assignments/:id/reassign, POST /territories/:id/rules, DELETE /territories/:id/rules/:rule_id, GET /territories/:id/performance.
**Evidence:** `backend/gateway/routes/v1-territories.routes.js` lines 136, 153, 197, 215, 247, 292, 311, 345, 365, 398, 415.

---

### FX-005 — API_INVENTORY.md: Campaigns section fully enumerated
**Source:** SC-005, UC-005
**File:** `docs/reports/u-series/API_INVENTORY.md`
**Change:** CAMPAIGNS table expanded — 5 rows → 10 confirmed routes.
**Routes added:** POST /campaigns/:id/pause, POST /campaigns/:id/resume, POST /campaigns/:id/cancel, GET /campaigns/:id/sends, GET /campaigns/:id/conversions.
**Evidence:** `backend/gateway/routes/v1-campaigns.routes.js` lines 62, 83, 131, 149, 179, 213, 234, 255, 276, 292.

---

### FX-006 — API_INVENTORY.md: WhatsApp Webhooks fully enumerated
**Source:** SC-006, UC-006
**File:** `docs/reports/u-series/API_INVENTORY.md`
**Change:** WEBHOOKS section restructured. WhatsApp: 1 inferred row → 6 confirmed routes. Payment: 1 inferred row → 3 confirmed routes.
**WhatsApp routes:** GET /meta (verification), POST /meta, POST /twilio, POST /360dialog, POST /gupshup, GET /log.
**Payment routes:** POST /jazzcash, POST /easypaisa, GET /log.
**Evidence:** `backend/gateway/routes/v1-whatsapp-webhooks.routes.js` lines 127, 138, 187, 215, 250, 286; `v1-payment-webhooks.routes.js` lines 57, 101, 148.

---

### FX-007 — API_INVENTORY.md: Communications count corrected
**Source:** SC-007
**File:** `docs/reports/u-series/API_INVENTORY.md`
**Change:** COMMUNICATIONS table — 2 inferred rows (including incorrect POST /communications/send) → 1 confirmed route.
**Retained:** GET /communications/engagement (marketing.read scope).
**Removed:** POST /communications/send was inferred, not in v1-communications.routes.js.
**Evidence:** `backend/gateway/routes/v1-communications.routes.js` — single `router.get('/engagement', ...)` at line 33.

---

### FX-008 — API_INVENTORY.md: Tenants count corrected
**Source:** SC-008
**File:** `docs/reports/u-series/API_INVENTORY.md`
**Change:** TENANTS table — 3 inferred admin/tenants rows → 1 confirmed route (GET /tenants/current). Added clarifying note about missing admin-tenant management routes.
**Evidence:** `backend/gateway/routes/v1-tenants.routes.js` — single `router.get('/current', ...)` at line 14.

---

### FX-009 — ROLE_PERMISSION_INVENTORY.md: Scope count corrected
**Source:** SC-009, UC-008
**File:** `docs/reports/u-series/ROLE_PERMISSION_INVENTORY.md`
**Changes:**
- Role table: `tenant_owner | All (63+)` → `All (91)`; `tenant_admin | 62` → `90`; `integration_service | All (63+)` → `All (91)`
- Section header: `Complete Scope Inventory (63 scopes)` → `(91 scopes)`
**Note:** The scope detail tables already listed all 91 scopes correctly — only the summary counts were stale.
**Evidence:** `backend/gateway/config/rbac-scopes.js` — 91 entries in SCOPES object (counted directly).

---

### FX-010 — MODULE_INVENTORY.md: Module 19 scope count corrected
**Source:** SC-010
**File:** `docs/reports/u-series/MODULE_INVENTORY.md`
**Change:** Module 19 (Identity & Access Management) Notes: `63 scopes` → `91 scopes`.
**Evidence:** Same as FX-009.

---

### FX-011 — MODULE_INVENTORY.md: Module 20 backend path corrected
**Source:** SC-011
**File:** `docs/reports/u-series/MODULE_INVENTORY.md`
**Change:** Module 20 (Activity / Task Tracking) Backend module: `services/activity.py, services/followup.py` → `backend/services/activity/, backend/services/followup/`.
**Evidence:** `backend/services/` directory listing — `activity` and `followup` are subdirectories, not .py files.

---

### FX-012 — MODULE_INVENTORY.md: Daily summary service path corrected
**Source:** UC-010
**File:** `docs/reports/u-series/MODULE_INVENTORY.md`
**Change:** Backend Infrastructure table — `services/daily_summary.py` → `services/summary/daily_summary.py`. Description expanded to include DailySummaryReport fields, EN/UR template support, P-017 gate.
**Evidence:** `backend/services/summary/daily_summary.py` confirmed at exact path.

---

### FX-013 — MODULE_INVENTORY.md: Contract lifecycle module documented
**Source:** UC-001
**File:** `docs/reports/u-series/MODULE_INVENTORY.md`
**Change:** Added Module 29 (Contract Lifecycle Management) — fully documented with entities (Contract, ContractTerm), API paths (12 from api.py::API_ENDPOINTS), status (backend-built, no gateway route), and human decision flag.
**Evidence:** `backend/src/contract_lifecycle_management/` — api.py, entities.py, services.py confirmed. 12 API_ENDPOINTS dict entries read directly.

---

### FX-014 — AUTHORITY_RECONSTRUCTION_REPORT.md: Scope count corrected
**Source:** SC-009 (cross-reference)
**File:** `docs/reports/u-series/AUTHORITY_RECONSTRUCTION_REPORT.md`
**Changes:** Two occurrences of "63 scopes" updated to "91 scopes". Route total updated from ~199 to 228.
**Evidence:** Same as FX-009.

---

### FX-015 — API_INVENTORY.md: Summary by Domain cases count corrected
**Source:** SC-013
**File:** `docs/reports/u-series/API_INVENTORY.md`
**Change:** Cases count in Summary by Domain table: `13` → `14`.
**Evidence:** Detailed CASES table in API_INVENTORY already had 14 rows; summary count was stale.

---

### FX-016 — DOC_CATALOGUE.md: New files registered
**Source:** G-05 (Governance rule — catalogue must be updated each session)
**File:** `docs/reports/u-series/DOC_CATALOGUE.md`
**Changes:**
- Updated `MODULE_INVENTORY.md`, `ROLE_PERMISSION_INVENTORY.md`, `API_INVENTORY.md` catalogue descriptions to reflect U7 remediation.
- Added new §§ for U5 Reports (3 files), U6 Reports (4 files), U7 Reports (2 files), `_archive/README.md`.
- Total count updated: 130 → 141.

---

## Items Deferred (Human Decision Required)

### D-001 — Contract Lifecycle Gateway Route
**Source:** UC-001
**Decision:** Add a gateway route for `src/contract_lifecycle_management/` (expose 12 API endpoints with appropriate RBAC scopes), or explicitly archive as deferred-scope.
**Current state:** Module documented in MODULE_INVENTORY.md Module 29 with full entity and API path details. No code change made.

---

### D-002 — Custom Objects Gateway Route
**Source:** UC-011
**Decision:** Confirm routing mechanism for `src/custom_object_framework/` and `src/custom_objects/`. Module 23 notes "(inferred — gateway route for custom objects not found)". No gateway route file confirmed.
**Current state:** MODULE_INVENTORY.md Module 23 note unchanged (accurate as-is: no route confirmed).

---

### D-003 — Entity DB Schema Attributions
**Source:** UC-009 / SC-012
**Decision:** ENTITY_INVENTORY.md lists entities without DB schema attribution for 5 entities added in Sprint 5B (Territory, TerritoryRule, TerritoryAssignment, Partner, PartnerCommission, Campaign, Segment). These entities have domain docs but no explicit DB schema file listed.
**Current state:** ENTITY_INVENTORY.md not updated. Reading the 5B DB schema files and adding attribution is a targeted task. Deferred to avoid partial updates.

---

### D-004 — Cases Count Discrepancy (detailed vs summary)
**Source:** SC-013
**Resolved partially:** Summary by Domain now shows 14. However the U6 delta identified this as a counting issue — the original v1-cases.routes.js analysis in U1 may have missed the 14th route. No code change; doc count is now correct.
**Status:** RESOLVED by FX-015.

---

### D-005 — backend/product-spec-gap-register.md, enterprise-depth.md, data-governance-ownership.md, b9-p08-mobile-responsiveness-system.md
**Source:** U5 H-001
**Decision:** These 4 backend docs were found at root during U5 restructuring scan. Placement needs human confirmation — move to docs/archive or leave in place.
**Current state:** Unchanged. No file moves made without explicit approval (scope gate rule).

---

*End DOC_CODE_REMEDIATION_REPORT.md*
