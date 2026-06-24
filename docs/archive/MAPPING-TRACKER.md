> **RETIRED** — This document has been superseded by [DOCUMENT_OWNERSHIP_MATRIX.md](../reports/u-series/DOCUMENT_OWNERSHIP_MATRIX.md) for ownership tracking, and [backend/FRONTEND-BACKEND-MAPPING.md](../../backend/FRONTEND-BACKEND-MAPPING.md) for frontend-backend mapping.
> Content preserved for historical reference. Do not update this document.
> Retired: 2026-06-21 (Documentation Normalization Phase)

# Frontend ↔ Backend Mapping — Rework Tracker

**Objective:** Reconcile frontend UI, backend routes, and spec docs into a single code-anchored
mapping file. No deletions — fill gaps by building what's missing on whichever side needs it.

**Outputs:**
1. `backend/FRONTEND-BACKEND-MAPPING.md` — complete rewrite, 6 sections ✅ DONE 2026-05-27
2. Backend gap builds — new endpoints / fields as identified (B9a — pending)
3. Frontend gap builds — new pages / wiring as identified (B9b — pending)
4. `PAGE-BUILD-PROTOCOL.md` — archetype list updated to match reality (B9c — pending)

---

## Read Inventory — ALL COMPLETE ✅

### Backend route files  22/22

| File | Status |
|---|---|
| v1-leads.routes.js | ✓ done |
| v1-opportunities.routes.js | ✓ done |
| v1-tasks.routes.js | ✓ done |
| v1-quotes.routes.js | ✓ done |
| v1-price-books.routes.js | ✓ done |
| v1-forecasts.routes.js | ✓ done |
| v1-followups.routes.js | ✓ done |
| v1-collections.routes.js | ✓ done |
| v1-activities.routes.js | ✓ partial (thin proxy) |
| v1-contacts.routes.js | ✓ done |
| v1-accounts.routes.js | ✓ done |
| v1-users.routes.js | ✓ done |
| v1-auth.routes.js | ✓ done |
| v1-emails.routes.js | ✓ done |
| v1-audit.routes.js | ✓ done |
| v1-orders.routes.js | ✓ done |
| v1-payments.routes.js | ✓ done |
| v1-subscriptions.routes.js | ✓ done |
| v1-invoice-summaries.routes.js | ✓ done |
| v1-payment-webhooks.routes.js | ✓ done |
| v1-sync.routes.js | ✓ done |
| v1-whatsapp-webhooks.routes.js | ✓ done |

### Frontend JS drivers  14/14

| File | Status |
|---|---|
| crm-followups.js | ✓ done |
| crm-collections.js | ✓ done |
| crm-sales-cockpit.js | ✓ done |
| crm-opportunities-detail.js | ✓ done |
| crm-sales-dashboard.js | ✓ done |
| crm-leads-detail.js | ✓ done |
| crm-quote-builder.js | ✓ done |
| crm-quotes-detail.js | ✓ done |
| crm-leads.js | ✓ done |
| crm-contacts.js | ✓ done |
| crm-dashboard.js | ✓ done |
| crm-lead-new.js | ✓ done |
| crm-dummy.js | ✓ done |
| crm-api.js | ✓ done |

### Spec / protocol docs

| File | Status |
|---|---|
| PAGE-BUILD-PROTOCOL.md | ✓ done |
| DESIGN-SPEC.md §3 (archetype list A–M) | ✓ done |

---

## Execution Batches

```
B0   Foundation reads ─────────────────────────────────────────────  ✅ done 2026-05-27
       PAGE-BUILD-PROTOCOL.md
       DESIGN-SPEC.md §3

B1a  Backend routes — core CRM ───────────────────────────────────  ✅ done 2026-05-27
       contacts, accounts, users, auth

B1b  Backend routes — revenue ────────────────────────────────────  ✅ done 2026-05-27
       orders, payments, subscriptions, invoice-summaries

B1c  Backend routes — comms + infra ──────────────────────────────  ✅ done 2026-05-27
       emails, audit, sync, whatsapp-webhooks, payment-webhooks

B2   Frontend drivers — remaining ───────────────────────────────  ✅ done 2026-05-27
       crm-leads, crm-contacts, crm-dashboard, crm-lead-new
       crm-dummy, crm-api

B3   Write Sec 1 — Backend Domain Inventory ─────────────────────  ✅ done 2026-05-27
       22 domains: endpoints, fields, enums, constraints

B4   Write Sec 4 — Frontend Page Inventory ──────────────────────  ✅ done 2026-05-27
       12 built pages: consumes / needs / gaps

B5   Write Sec 2 — Fresh Archetype Extraction ───────────────────  ✅ done 2026-05-27
       Per backend domain: what UI archetype(s) it supports

B6   Write Sec 3 — Existing Archetype Overlay ───────────────────  ✅ done 2026-05-27
       A–M vs fresh extraction → gaps in both directions

B7   Write Sec 5 — Canonical Archetype List ─────────────────────  ✅ done 2026-05-27
       Supported by BOTH backend AND protocol

B8   Write Sec 6 — Gap Register ─────────────────────────────────  ✅ done 2026-05-27
       24 gaps G-001 through G-024
       14 breaking · 10 mapping

B9a  Gap closure — backend ───────────────────────────────────────  ☐ pending scope
       G-002: Build GET /forecasts endpoint
       G-004: Add action_type + attempts_count to followup schema
       G-020: Build POST /collections/invoices/:id/reminders
       G-024: Fix respondError/respondSuccess import in v1-quotes.routes.js

B9b  Gap closure — frontend ──────────────────────────────────────  ☐ pending scope
       G-001/G-015: Align lead stage + priority vocab (crm-dummy + crm-leads)
       G-003/G-023: Rename opp_id → opportunity_id in CRM_DUMMY
       G-005: Align followup escalation_level (crm-dummy + crm-followups)
       G-006: Align collections status vocab (crm-dummy + crm-collections)
       G-008: Remove lead.followup_enforcement; derive from canonical task
       G-009/G-021: Fix collections paths in crm-api.js
       G-010: Wire GET /price-books in quote builder
       G-011: Fix followups.complete method + path in crm-api.js
       G-012: Fix auth endpoint URL in crm-api.js
       G-013/G-019: Rename user_id→id and followup_id→task_id in CRM_DUMMY + drivers
       G-014: Fix lead source values in crm-leads.js
       G-016: Rewrite crm-dashboard.js to read from CRM_DUMMY
       G-022: Fix price-books pagination to use page/page_size

B9c  Gap closure — docs ──────────────────────────────────────────  ☐ pending scope
       Update PAGE-BUILD-PROTOCOL.md archetype list to canonical (Sec 5)
       Note archetypes E, F, M as backend-incomplete in DESIGN-SPEC commentary
```

---

## Mapping File — COMPLETE ✅

All 6 sections written to `backend/FRONTEND-BACKEND-MAPPING.md` (2026-05-27).

```
Section 1 — Backend Domain Inventory          ✅  22 domains
Section 2 — Fresh Archetype Extraction        ✅  22 domains → archetypes
Section 3 — Existing Archetype Overlay        ✅  A–M vs fresh, 3 partial/missing
Section 4 — Frontend Page Inventory           ✅  12 built pages
Section 5 — Canonical Archetype List          ✅  13 archetypes with wiring status
Section 6 — Gap Register                      ✅  24 gaps, G-001 to G-024
```

---

## Full Gap Register

| # | Gap | Severity | Side | B9 batch |
|---|---|---|---|---|
| G-001 | Lead stage vocabulary — 0 of 7 values overlap | 🔴 Breaking | Both | B9b |
| G-002 | No GET /forecasts endpoint | 🔴 Breaking | Backend | B9a |
| G-003 | `opp_id` vs `opportunity_id` — PK field name in response | 🟡 Mapping | Frontend | B9b |
| G-004 | Followup: `action_type`, `attempts_count` missing from backend | 🔴 Breaking | Backend | B9a |
| G-005 | Followup `escalation_level` values completely different | 🔴 Breaking | Both | B9b |
| G-006 | Collections status values don't match | 🔴 Breaking | Both | B9b |
| G-007 | `account_name` not on opp — requires join | 🟡 Mapping | Backend | B9a |
| G-008 | `lead.followup_enforcement` — not a backend lead field | 🟡 Mapping | Frontend | B9b |
| G-009 | Collections list path `/collections` vs `/collections/invoices` | 🔴 Breaking | Frontend | B9b |
| G-010 | Quote builder uses hardcoded price book, bypasses real endpoint | 🟡 Mapping | Frontend | B9b |
| G-011 | followups.complete: PATCH vs POST /:task_id/complete | 🔴 Breaking | Frontend | B9b |
| G-012 | Auth endpoint /auth/login vs /auth/sessions | 🔴 Breaking | Frontend | B9b |
| G-013 | Users backend returns `id` not `user_id` | 🔴 Breaking | Frontend | B9b |
| G-014 | Lead source includes cold_call/event/linkedin (not in backend) | 🟡 Mapping | Frontend | B9b |
| G-015 | Lead priority: urgent/low/medium/high vs hot/warm/cold | 🔴 Breaking | Both | B9b |
| G-016 | crm-dashboard.js hardcoded data (C-007 violation) | 🔴 Breaking | Frontend | B9b |
| G-017 | Contacts schema opaque — downstream alignment unknown | 🟡 Mapping | Both | investigate |
| G-018 | Tasks schema opaque — downstream alignment unknown | 🟡 Mapping | Both | investigate |
| G-019 | Followup PK `followup_id` vs `task_id` | 🔴 Breaking | Frontend | B9b |
| G-020 | Collections reminder endpoint missing from backend | 🔴 Breaking | Backend | B9a |
| G-021 | Collections payment path missing `/invoices/` prefix | 🟡 Mapping | Frontend | B9b |
| G-022 | Price books uses page/page_size not limit/offset | 🟡 Mapping | Frontend | B9b |
| G-023 | Quote uses `opp_id` vs `opportunity_id` | 🟡 Mapping | Frontend | B9b |
| G-024 | v1-quotes.routes.js missing respondError/respondSuccess import | 🔴 Breaking | Backend | B9a |

---

## Session Log

| Date | Batches run | Notes |
|---|---|---|
| 2026-05-27 | Pre-B1 reads | 9 backend routes + 8 JS drivers read. G-001–G-010 found. |
| 2026-05-27 | B0, B1a, B1b, B1c | All 22 backend routes read. |
| 2026-05-27 | B2 | All 14 frontend drivers read. G-011–G-017 found. |
| 2026-05-27 | B3–B8 | All 6 mapping sections written. 24 gaps catalogued. Phase M-2 complete. |
