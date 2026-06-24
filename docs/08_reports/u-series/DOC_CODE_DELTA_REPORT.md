# DOC_CODE_DELTA_REPORT.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U6 — Doc to Code Delta Analysis)
**Method:** Compared docs/reports/u-series/API_INVENTORY.md, ENTITY_INVENTORY.md, MODULE_INVENTORY.md, ROLE_PERMISSION_INVENTORY.md, WORKFLOW_INVENTORY.md, FEATURE_INVENTORY.md against actual code in backend/gateway/routes/, backend/src/, backend/services/, backend/db/, frontend/src/app/
**Status:** Analysis only — no files modified.

---

## 1. API Routes Delta

### Summary

| Metric | Documented | Actual in Code | Delta |
|---|---|---|---|
| Total route count | ~198 | 228 | **+30 underdocumented** |
| Route domain files | 44 | 44 | 0 |
| Route counting method | Approximate (`~`) | Exact (router.*() calls) | — |

### Per-Domain Route Count Comparison

| Domain | Doc Claims | Actual | Delta | Assessment |
|---|---|---|---|---|
| Auth | 7 | 7 | 0 | MATCH |
| Leads | 8 | 8 | 0 | MATCH |
| Contacts | 7 | 7 | 0 | MATCH |
| Accounts | ~4 | 4 | 0 | MATCH |
| Opportunities | 6 | 6 | 0 | MATCH |
| Follow-ups | 6 | 6 | 0 | MATCH |
| Cases | 13 | 14 | +1 | NEAR MATCH |
| Inbox | 11 | 11 | 0 | MATCH |
| Workflows | 11 | 11 | 0 | MATCH |
| AI | 13 | 13 | 0 | MATCH |
| Knowledge | ~5 | 5 | 0 | MATCH |
| Quotes | ~5 | 5 | 0 | MATCH |
| Governance | ~4 | 4 | 0 | MATCH |
| Compliance Settings | ~2 | 2 | 0 | MATCH |
| Roles | 4 | 4 | 0 | MATCH |
| Sync | ~2 | 2 | 0 | MATCH |
| Forecasts | ~3 | 3 | 0 | MATCH |
| Templates | ~4 | 4 | 0 | MATCH |
| Invoice Summaries | ~3 | 3 | 0 | MATCH |
| **Collections** | ~4 | **11** | **+7** | **STALE — severely underdocumented** |
| **Partners** | ~5 | **13** | **+8** | **STALE — severely underdocumented** |
| **Territories** | ~5 | **11** | **+6** | **STALE — severely underdocumented** |
| **Campaigns** | ~5 | **10** | **+5** | **STALE — significantly underdocumented** |
| **WhatsApp Webhooks** | 1 | **6** | **+5** | **STALE — severely underdocumented** |
| **Billing** | ~4 | **6** | **+2** | **STALE** |
| **Privacy** | ~3 | **5** | **+2** | **STALE** |
| **Payment Webhooks** | 1 | **3** | **+2** | **STALE** |
| Emails | ~4 | 5 | +1 | minor underdocument |
| Segments | ~4 | 5 | +1 | minor underdocument |
| Payments | ~3 | 4 | +1 | minor underdocument |
| **Communications** | ~3 | **1** | **-2** | **STALE — overdocumented** |
| **Tenants** | ~4 | **1** | **-3** | **STALE — overdocumented** |
| Activities | ~4 | 2 | -2 | overdocumented |
| Subscriptions | ~4 | 2 | -2 | overdocumented |
| Users | ~5 | 3 | -2 | overdocumented |
| Price Books | ~4 | 2 | -2 | overdocumented |
| Tasks | ~4 | 3 | -1 | minor overdocument |
| Orders | ~3 | 2 | -1 | minor overdocument |
| Reports | ~4 | 3 | -1 | minor overdocument |
| Audit | ~3 | 2 | -1 | minor overdocument |
| Org Settings | ~3 | 2 | -1 | minor overdocument |
| Integrations | ~4 | 3 | -1 | minor overdocument |
| Feature Flags | ~3 | 2 | -1 | minor overdocument |
| Notifications | ~3 | 2 | -1 | minor overdocument |

### Route Counting Note

The API_INVENTORY.md stated "~198" routes using approximate (~) notation. The actual count is 228. Two route files use named sub-routers (`casesRouter` + `supportRouter` in v1-cases.routes.js; `partnersRouter` + `dealRegistrationsRouter` in v1-partners.routes.js) instead of the standard `router.` prefix. These were originally counted as 0 in the first pass and corrected on re-analysis.

---

## 2. RBAC Permissions Delta

### Summary

| Metric | Documented | Actual in Code | Delta |
|---|---|---|---|
| SCOPES count | 63 | 91 | **+28** |
| Roles | 7 | 7 | 0 |
| Auth algorithm | HS256 | HS256 | MATCH |
| Token expiry | 15min/7d | 15min/7d | MATCH |

### Scope Count Explanation

The ROLE_PERMISSION_INVENTORY.md claimed 63 scopes. The actual `rbac-scopes.js` SCOPES object contains 91 unique scope constants covering 35 categories. The 28-scope gap is explained by Sprint 5B additions that were wired into the code but the inventory count was not updated. The scope list in the inventory appears complete (covers all categories), but the header count "63" is stale.

### New Scopes in Code Not Reflected in Count (Sprint 5B additions)

Categories confirmed in code but count not updated in inventory:
- Email scopes: `emails.read`, `emails.send`, `emails.track` (3)
- Forecasting: `forecasts.read` (1)
- Pricing: `pricing.read`, `pricing.create` (2)
- Billing: `billing.read`, `billing.create`, `billing.manage` (3)
- Reports: `reports.read`, `reports.create` (2)
- Integrations: `integrations.read`, `integrations.manage` (2)
- Compliance: `compliance.read` (1)
- Privacy: `privacy.read`, `privacy.manage` (2)
- Marketing: `marketing.read` (1)
- Audit extended: `audit.logs.read` (1, separate from `audit.read`)
- Users extended: `users.manage_roles` (1)
- Orders extended: `orders.create` (1)
- Quotes extended: `quotes.accept` (1)
- Invoices: `invoices.create` (1)
- Activities: `activities.read`, `activities.create` (already in Sprint 5B areas)

**The scope list content in ROLE_PERMISSION_INVENTORY is accurate; only the "63" header count is stale. True count is 91.**

---

## 3. Python Service Modules Delta

### Architecture Clarification (Not in Documentation)

The backend has two Python layers, both present in code:
1. `backend/src/` — 34 business logic modules (153 .py files) — the domain layer
2. `backend/services/` — 22 FastAPI service modules — the HTTP layer (proxied by Node.js gateway)

The MODULE_INVENTORY.md references `src/` paths for most modules but `services/` paths for some (Module 20: Activity/Task Tracking). This inconsistency is a documentation accuracy issue.

### Module-to-Code Mapping Status

| Doc Module | Documented Path | Actual Code Path | Status |
|---|---|---|---|
| 1. Lead Management | `src/lead_management/` | `backend/src/lead_management/` ✓ + `backend/services/leads/` | MATCH |
| 2. Contacts | `src/customer_360_cdp/` | `backend/src/customer_360_cdp/` ✓ | MATCH |
| 3. Accounts | `src/customer_360_cdp/` (shared) | Same | MATCH |
| 4. Sales/Opportunities | `src/sales_cockpit/` | `backend/src/sales_cockpit/` ✓ + `backend/services/deals/` | MATCH |
| 5. CPQ | `src/rule_engine/` | `backend/src/rule_engine/` ✓ | MATCH |
| 6. Finance/Collections | `src/revenue_recognition/`, `src/usage_billing/`, `src/subscription_billing/` | All confirmed ✓ | MATCH |
| 7. Subscriptions | `src/subscription_billing/` | Confirmed ✓ | MATCH |
| 8. Support/Cases | `src/ticket_management/`, `src/support_console/` | Both confirmed ✓ | MATCH |
| 9. Knowledge Base | `src/knowledge_base/` | Confirmed ✓ | MATCH |
| 10. Omnichannel Inbox | `src/omnichannel_inbox/` | Confirmed ✓ + `backend/services/inbox/` | MATCH |
| 11. Routing/Inbox Config | `src/omnichannel_inbox/` | Same | MATCH |
| 12. Marketing/Campaigns | `src/campaigns/`, `src/marketing_admin_workflow_ui/` | Both confirmed ✓ | MATCH |
| 13. Workflow Automation | `src/workflow_engine/` | Confirmed ✓ + `backend/services/workflows/` | MATCH |
| 14. AI/Copilot | `src/ai_copilot/`, `src/ai_scoring/`, `src/predictive_models/`, `src/predictive_forecasting/` | All 4 confirmed ✓ | MATCH |
| 15. Forecasting | `src/predictive_forecasting/` | Confirmed ✓ | MATCH |
| 16. Report Builder | `src/reporting_dashboards/` | Confirmed ✓ | MATCH |
| 17. Territories | `src/territory_management/` | Confirmed ✓ + `backend/services/territories/` | MATCH |
| 18. Partners | `src/partner_channel_management/` | Confirmed ✓ + `backend/services/partners/` | MATCH |
| 19. Identity & Access | `src/role_based_ui/` | Confirmed ✓ | MATCH |
| 20. Activity/Task | `services/activity.py` | `backend/services/activity/` ✓ | MATCH (path format stale) |
| 21. Audit & Compliance | `src/admin_control_center/` | Confirmed ✓ | MATCH |
| 22. Settings/Admin | `src/design_system/`, `src/admin_control_center/` | Both confirmed ✓ | MATCH |
| 23. Custom Objects | `src/custom_object_framework/`, `src/custom_objects/` | Both confirmed ✓ | MATCH |
| 24. Rule Builder | `src/rule_engine/` | Confirmed ✓ | MATCH |
| 25. Communication Integrations | `src/communication_integrations/` | Confirmed ✓ | MATCH |
| 26. External APIs/Webhooks | `src/external_apis_webhooks/`, `src/plugin_framework/` | Both confirmed ✓ | MATCH |
| 27. Event Bus/Deduplication | `src/event_bus/`, `src/data_deduplication_engine/`, `src/execution_hardening/` | All 3 confirmed ✓ | MATCH |
| 28. Price Books | (inferred from route) | `gateway/routes/v1-price-books.routes.js` ✓ (no src/ module found) | PARTIAL — no src/ module |
| **—** | **NOT DOCUMENTED** | **`backend/src/contract_lifecycle_management/`** | **UNDOCUMENTED** |

### Undocumented Python Module

**`backend/src/contract_lifecycle_management/`** — 4 .py files (api.py, entities.py, services.py, __init__.py) — full domain module with API, entities, and services. Not referenced in MODULE_INVENTORY.md, ENTITY_INVENTORY.md, or FEATURE_INVENTORY.md.

---

## 4. Entity Delta

### DB Databases: 18 Present vs Documentation

Databases confirmed in `backend/db/`:
`activity_task_db`, `audit_compliance_db`, `campaign_db`, `case_ticket_db`, `contact_account_db`, `feature_flag_db`, `identity_auth_db`, `intelligence_db`, `knowledge_db`, `lead_management_db`, `messaging_db`, `notification_db`, `opportunity_db`, `org_tenant_db`, `quote_order_db`, `territory_db`, `transaction_db`, `workflow_db`

ENTITY_INVENTORY.md sources confirmed:
- `db/identity_auth_db/schema.sql` — DOCUMENTED
- `db/lead_management_db/schema.sql` — DOCUMENTED
- `db/contact_account_db/schema.sql` — DOCUMENTED
- `db/org_tenant_db/schema.sql` — DOCUMENTED
- `db/opportunity_db/schema.sql` — DOCUMENTED
- `db/quote_order_db/schema.sql` — DOCUMENTED
- `db/transaction_db/schema.sql` — DOCUMENTED
- `db/workflow_db/schema.sql` — DOCUMENTED
- `db/campaign_db/schema.sql` — DOCUMENTED
- `db/case_ticket_db/schema.sql` — DOCUMENTED
- `db/knowledge_db/schema.sql` — DOCUMENTED
- `db/territory_db/schema.sql` — DOCUMENTED
- `db/messaging_db/schema.sql` — DOCUMENTED

Databases with no clear entity coverage in ENTITY_INVENTORY.md:
- `db/intelligence_db/` — likely AI/scoring entities; not explicitly documented as a separate database
- `db/notification_db/` — notification preferences DB; entities inferred but not explicitly documented
- `db/activity_task_db/` — activity and task entities; has its own README.md and self-qc.md in db/
- `db/feature_flag_db/` — feature flag entities; not explicitly referenced in ENTITY_INVENTORY

---

## 5. Workflow Delta

### Documented Workflows vs Code

From WORKFLOW_INVENTORY.md:
- WF-001 through WF-005 documented (5 system workflows)
- Custom workflow support documented

From gateway route seeds (`v1-workflows.routes.js`):
- Seeded workflow definitions confirmed at lines 45–49 of route file (WF-001 through WF-005)
- Status: MATCH — all 5 documented workflows confirmed seeded in code

Python services: `backend/services/workflows/service.py` and `backend/src/workflow_engine/` both confirmed present.

No additional undocumented workflows found in route seeds.

---

## 6. Frontend Pages Delta

| Metric | Documented | Actual | Delta |
|---|---|---|---|
| Library pages | 96 | ~94 (estimated) | possible -2 |
| Custom pages | 75 | 75 (estimated) | 0 |
| Total pages | 171 | 169 | **-2** |

The app/ directory has 169 HTML files. Documentation claims 96 library + 75 custom = 171. The -2 discrepancy may indicate 2 library pages removed or renamed. Exact pages cannot be identified without cross-referencing the full page list against the NexLink library manifest.

---

## 7. Integration Delta

### Documented Integrations
MODULE_INVENTORY Module 25 documents 4 WhatsApp adapters + 2 payment adapters. These are confirmed in `adapters/pakistan/`.

### Undocumented in API_INVENTORY
- WhatsApp webhook has 6 routes in code vs 1 documented. The additional 5 are event-type handlers (message status, delivery receipts, read receipts, etc.) that exist in code but are not explicitly enumerated in API_INVENTORY.

---

## 8. Summary Table

| Category | Documented | Actual | Verdict |
|---|---|---|---|
| Total API routes | ~198 | 228 | STALE — +30 undocumented |
| RBAC scope count | 63 | 91 | STALE — count is wrong; list is correct |
| Python src/ modules | 27 unique domains | 34 dirs (28 documented + 1 undocumented) | 1 UNDOCUMENTED |
| System workflows | 5 | 5 | MATCH |
| DB schemas | 13 explicitly documented | 18 present | 5 DBs not explicitly sourced in ENTITY_INVENTORY |
| Frontend pages | 171 | 169 | -2 pages (minor) |
| Gateway route files | 44 | 44 | MATCH |
