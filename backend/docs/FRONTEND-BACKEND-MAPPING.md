# Frontend ↔ Backend Mapping

**Last updated:** 2026-05-31 — Wiring extension COMPLETE: 75/75 pages live. 5 Phase 6 inline stub routes added (billing, integrations, governance, reports, communications). 42 route files total in `gateway/routes/index.js`. G-04/G-05/J-03/H-07/A-08 entries updated (WIRED 2026-05-31). Prior: 2026-05-30 — Phase 5B complete, 30 route files, all Cat 2 backend domains built.
**Backend base:** `http://localhost:3000/api/v1/` (gateway: `backend/gateway/routes/index.js`)
**Response envelope:** All endpoints return `{ data, meta }` — `docs/api-standards.md`.
**Auth:** `Authorization: Bearer <jwt>` on every request. Tenant isolated via JWT `tenant_id`.
**Source authority:** Section 1 route inventory sourced directly from gateway route files (trustworthy). All other sections from Phase M analysis — treat as reference only, not ground truth.

> **⚠️ IMPORTANT:** This file is a LOG of what maps and to what degree. It is NOT a source of truth. Ground truth is: (1) the actual backend route files, (2) the actual frontend HTML/JS files on disk. Phase M claimed "all gaps closed" — the subsequent protocol audit found that claim was false. Use this file to understand the landscape; verify against source files before acting on any specific claim.

---

## Section 1 — Backend Domain Inventory

22 route domains in the gateway. Handler type: **I** = in-line (schema fully visible), **P** = thin proxy (schema opaque, forwarded to downstream service), **S** = static stub.

---

### 1.1 Leads  `[I]`
**Route file:** `v1-leads.routes.js`

| Endpoint | Method | Scope | Notes |
|---|---|---|---|
| `/leads` | GET | leads.read | Filters: stage, owner_id, status, priority, source |
| `/leads` | POST | leads.create | owner_id required (422 without) |
| `/leads/:lead_id` | GET | leads.read | |
| `/leads/:lead_id` | PATCH | leads.update | Stage transitions are atomic (writes history) |
| `/leads/:lead_id` | DELETE | leads.delete | Soft delete |
| `/leads/:lead_id/next-action` | GET | followups.read | Calls followup service; returns stub if unreachable |

**Entity fields:** `lead_id`, `tenant_id`, `owner_id`, `title`, `stage`, `status`, `priority`, `source`, `contact_name`, `contact_phone_e164`, `contact_email`, `estimated_value`, `currency`, `notes`, `metadata`, `created_at`, `updated_at`

**Enums:**
- `stage`: `new` | `qualifying` | `nurturing` | `proposal` | `negotiation` | `won` | `lost` | `disqualified`
- `status`: `open` | `working` | `idle` | `closed`
- `priority`: `hot` | `warm` | `cold`
- `source`: `whatsapp` | `web` | `import` | `manual` | `referral` | `campaign`

**Pagination:** `limit` / `offset` (max limit 200). Default limit 25.

---

### 1.2 Opportunities  `[I]`
**Route file:** `v1-opportunities.routes.js`

| Endpoint | Method | Scope | Notes |
|---|---|---|---|
| `/opportunities` | GET | opportunities.read | Filters: stage, owner_id, forecast_category |
| `/opportunities` | POST | opportunities.create | owner_id + name required |
| `/opportunities/:opp_id` | GET | opportunities.read | URL param is `opp_id`; entity field is `opportunity_id` |
| `/opportunities/:opp_id` | PATCH | opportunities.update | Terminal stages locked (409 if already closed) |
| `/opportunities/:opp_id/line-items` | GET | opportunities.read | |
| `/opportunities/:opp_id/line-items` | POST | opportunities.update | Requires product_id + unit_price |

**Entity fields:** `opportunity_id`, `tenant_id`, `owner_id`, `name`, `account_id`, `account_name`, `contact_id`, `amount`, `currency`, `close_date`, `stage`, `probability`, `forecast_category`, `version_no`, `closed_at`, `close_reason`, `created_at`, `updated_at`

**Enums:**
- `stage`: `qualification` | `discovery` | `proposal` | `negotiation` | `closed_won` | `closed_lost`
- `forecast_category`: `pipeline` | `best_case` | `commit` | `closed` | `omitted`

**Events emitted:** `opportunity.stage.changed.v1`, `opportunity.closed.v1`  
**Pagination:** `limit` / `offset` (max 200). Default limit 25.  
**Note:** `account_name` accepted in POST body and stored directly on the entity (convenience denorm); ideally joined from accounts service at read time in production.

---

### 1.3 Followups  `[I]`
**Route file:** `v1-followups.routes.js`

| Endpoint | Method | Scope | Notes |
|---|---|---|---|
| `/followups` | GET | followups.read | Filters: lead_id, owner_id, state |
| `/followups` | POST | followups.create | lead_id + owner_id + due_at required |
| `/followups/:task_id` | GET | followups.read | PK is `task_id`, not `followup_id` |
| `/followups/:task_id/complete` | POST | followups.complete | body: completed_activity_id (optional). Idempotent. |
| `/followups/:task_id/snooze` | POST | followups.snooze | body: snoozed_until (required, ISO8601) |
| `/followups/lead/:lead_id/canonical` | GET | followups.read | Single canonical pending task per lead |

**Entity fields:** `task_id`, `tenant_id`, `lead_id`, `owner_id`, `state`, `due_at`, `rule_type`, `escalation_level`, `is_canonical`, `completed_at`, `created_at`, `updated_at`

**Enums:**
- `state`: `pending` | `overdue` | `completed`
- `escalation_level`: `none` | `reminder` | `warning` | `escalated` | `reassigned`
- `rule_type`: `TimeBased` | `ActivityBased` | `InactivityBased`

**Pagination:** `limit` / `offset`. Default limit 25.  
**Note:** No `action_type`, `attempts_count`, `lead_name` fields in backend schema — frontend-computed display fields only.

---

### 1.4 Collections  `[I]`
**Route file:** `v1-collections.routes.js`  
**Path prefix:** `/collections` (all sub-routes below are relative to this)

| Endpoint | Method | Scope | Notes |
|---|---|---|---|
| `/collections/invoices` | GET | collections.read | Filters: subscription_id, status |
| `/collections/invoices` | POST | collections.invoice | amount_due + currency + due_date + invoice_number required |
| `/collections/invoices/:invoice_id` | GET | collections.read | |
| `/collections/invoices/:invoice_id/payments` | POST | collections.invoice | amount + currency + payment_method_type required |
| `/collections/invoices/:invoice_id/payments/:payment_id/proof` | POST | collections.invoice | proof_url required. Returns 501 when DB-backed (P-025 pending) |
| `/collections/invoices/:invoice_id/payments/:payment_id/proof/verify` | PATCH | collections.reconcile | verification_status: verified \| rejected |
| `/collections/invoices/:invoice_id/reminders` | POST | collections.invoice | Sends reminder; updates last_reminder_at on invoice |
| `/collections/subscriptions` | GET | collections.read | Filters: account_id, status |
| `/collections/subscriptions` | POST | collections.invoice | account_id + plan_code + start_date required |
| `/collections/overdue` | GET | collections.read | Returns open invoices with due_date < today |
| `/collections/reconcile` | POST | collections.reconcile | Batch reconciliation |

**Invoice fields:** `invoice_id`, `tenant_id`, `subscription_id`, `invoice_number`, `amount_due`, `amount_paid`, `currency`, `due_date`, `status`, `account_name`, `account_tier`, `is_overdue`, `last_reminder_at`, `issued_at`, `created_at`, `updated_at`  
**Invoice status:** `draft` | `open` | `paid` | `void` | `uncollectible`  
**Subscription fields:** `subscription_id`, `account_id`, `plan_code`, `start_date`, `end_date`, `renewal_date`, `external_subscription_ref`, `quote_id`, `status`  
**Payment fields:** `payment_event_id`, `invoice_id`, `amount`, `currency`, `payment_method_type`, `status`, `occurred_at`

**Pagination:** `limit` / `offset`. Default limit 25.  
**Note:** `is_overdue` computed at GET time (due_date < today AND status != paid/void/uncollectible). Proof upload returns 501 when DB-backed.

---

### 1.5 Tasks  `[P]`
**Route file:** `v1-tasks.routes.js`

| Endpoint | Method | Scope |
|---|---|---|
| `/tasks` | GET | tasks.read |
| `/tasks` | POST | tasks.create |
| `/tasks/:task_id/reschedule` | POST | tasks.update |

**Schema:** Opaque — forwarded to task microservice.  
**Note:** Separate from Followups (§1.3). Tasks = general work items; Followups = lead enforcement engine tasks.

---

### 1.6 Quotes / CPQ  `[I — cpq-store]`
**Route file:** `v1-quotes.routes.js`  
**Data layer:** `data/cpq-store.js` (in-memory Map, not DB-backed)

| Endpoint | Method | Scope | Notes |
|---|---|---|---|
| `/quotes` | GET | quotes.read | |
| `/quotes` | POST | quotes.create | opportunity_id + currency + valid_until + line_items required |
| `/quotes/:quote_id` | GET | quotes.read | |
| `/quotes/:quote_id/acceptances` | POST | quotes.accept | Sets status=accepted, accepted_at |
| `/quotes/:quote_id/orders` | POST | orders.create | Quote must be accepted first (409 otherwise) |

**Quote fields:** `quote_id`, `tenant_id`, `opportunity_id`, `status`, `currency`, `subtotal`, `discount_total`, `tax_total`, `grand_total`, `valid_until`, `created_at`, `accepted_at`, `line_items`  
**Quote status:** `draft` → `accepted`  
**Line item fields:** `quote_line_item_id`, `product_id`, `quantity`, `list_price`, `discount_percent`, `net_price`  
**Order fields (from quote):** `order_id`, `tenant_id`, `quote_id`, `opportunity_id`, `status` (created), `currency`, `subtotal`, `discount_total`, `tax_total`, `grand_total`, `ordered_at`, `created_at`, `line_items`

**✅ G-024 FIXED:** `respondError` and `respondSuccess` confirmed imported on line 5 of `v1-quotes.routes.js` — `const { respondError, respondSuccess } = require('../middleware/response-wrapper')`. No ReferenceError risk. (Note was stale — fix was applied 2026-05-27 per fix log §Session 2.)

---

### 1.7 Price Books  `[S — static stub]`
**Route file:** `v1-price-books.routes.js`

| Endpoint | Method | Scope | Notes |
|---|---|---|---|
| `/price-books` | GET | pricing.read | Returns hardcoded 1-item list (Standard USD) |
| `/price-books` | POST | pricing.create | Returns hardcoded stub response |

**Fields:** `price_book_id`, `tenant_id`, `name`, `currency`, `is_default`, `active_from`, `active_to`  
**Pagination style:** `page` / `page_size` (different from most domains which use limit/offset)  
**Note:** Not DB-backed. Stub returns USD book only. Frontend uses PKR — currency mismatch (see G-010).

---

### 1.8 Forecasts  `[I — inline GET; P — model/aggregate]`
**Route file:** `v1-forecasts.routes.js`

| Endpoint | Method | Scope | Notes |
|---|---|---|---|
| `/forecasts` | GET | forecasts.read | Inline handler — returns current-quarter aggregate shape |
| `/forecasts/model` | POST | forecasts.read | Forwarded to forecast service |
| `/forecasts/aggregate` | POST | forecasts.read | Forwarded to forecast service |

**GET /forecasts response shape:**
```json
{
  "period": "current_quarter",
  "generated_at": "<ISO8601>",
  "weighted_value": 0,
  "by_category": {
    "pipeline":  { "count": 0, "total_value": 0 },
    "best_case": { "count": 0, "total_value": 0 },
    "commit":    { "count": 0, "total_value": 0 },
    "closed":    { "count": 0, "total_value": 0 }
  },
  "stage_breakdown": [{ "stage": "...", "weight": 0, "opportunity_count": 0, "total_value": 0, "weighted": 0 }]
}
```
**Note:** GET /forecasts returns a stub shape (zeroed values) until wired to live opportunity aggregation.

---

### 1.9 Activities  `[P]`
**Route file:** `v1-activities.routes.js`

| Endpoint | Method | Scope |
|---|---|---|
| `/activities` | GET | activities.read |
| `/activities` | POST | activities.create |

**Schema:** Opaque — forwarded to Python activity service.

---

### 1.10 Contacts  `[P]`
**Route file:** `v1-contacts.routes.js`

| Endpoint | Method | Scope |
|---|---|---|
| `/contacts` | GET | contacts.read |
| `/contacts` | POST | contacts.create |
| `/contacts/:contact_id` | GET | contacts.read |
| `/contacts/:contact_id` | PATCH | contacts.update |
| `/contacts/:contact_id` | DELETE | contacts.delete |

**Schema:** Opaque — forwarded to contacts service.

---

### 1.11 Accounts  `[P]`
**Route file:** `v1-accounts.routes.js`

| Endpoint | Method | Scope | Notes |
|---|---|---|---|
| `/accounts` | GET | accounts.read | |
| `/accounts` | POST | accounts.create | |
| `/accounts/:account_id` | GET | accounts.read | |
| `/accounts/:account_id` | PATCH | accounts.update | |
| `/accounts/:account_id` | DELETE | accounts.delete | |
| `/accounts/:account_id/contacts/:contact_id` | PUT | accounts.update | Link contact to account |
| `/accounts/:account_id/contacts/:contact_id` | DELETE | accounts.update | Unlink contact |

**Schema:** Opaque.

---

### 1.12 Users  `[I]`
**Route file:** `v1-users.routes.js`

| Endpoint | Method | Scope | Notes |
|---|---|---|---|
| `/users` | GET | users.read | |
| `/users` | POST | users.create | |
| `/users/:user_id` | GET | users.read | |
| `/users/:user_id` | PATCH | users.update | |
| `/users/:user_id` | DELETE | users.delete | |
| `/users/:user_id/roles` | POST | users.manage_roles | body: role_id |

**Entity fields:** `id` (⚠️ NOT `user_id`), `email`, `display_name`, `status`, `created_at`, `updated_at`  
**Pagination style:** `page` / `page_size` (different from most domains)

---

### 1.13 Auth  `[I]`
**Route file:** `v1-auth.routes.js`

| Endpoint | Method | Notes |
|---|---|---|
| `/auth/sessions` | POST | Returns 501 — IdP not wired; requires JWT_PUBLIC_KEY_URL env var |
| `/auth/sessions/current` | DELETE | Revokes JWT (jti blocklist, in-memory, 15-min TTL) |

---

### 1.14 Emails  `[P]`
**Route file:** `v1-emails.routes.js`

| Endpoint | Method |
|---|---|
| `/emails` | GET |
| `/emails` | POST |
| `/emails/:email_id/events` | POST |
| `/emails/engagements` | GET |
| `/emails/engagement-logs` | GET |

**Schema:** Opaque.

---

### 1.15 Audit  `[I — in-memory]`
**Route file:** `v1-audit.routes.js`

| Endpoint | Method | Notes |
|---|---|---|
| `/audits/events` | GET | Lists audit events from in-memory store |
| `/audits/chain-check` | GET | Calls activity service /internal/chain-check; returns stub if unreachable |

---

### 1.16 Orders  `[P — read-only]`
**Route file:** `v1-orders.routes.js`

| Endpoint | Method | Notes |
|---|---|---|
| `/orders` | GET | Read-only; no POST |
| `/orders/:order_id` | GET | |

**Note:** Orders are created via `POST /quotes/:quote_id/orders` (§1.6), not via `/orders`.

---

### 1.17 Payments  `[I]`
**Route file:** `v1-payments.routes.js`

| Endpoint | Method | Notes |
|---|---|---|
| `/payments` | GET | |
| `/payments` | POST | |
| `/payments/:payment_id` | GET | |
| `/payments/:payment_id` | PATCH | |
| `/payments/revenue/summary` | GET | Requires from_date + to_date (YYYY-MM-DD) |

**Status flow:** `initiated` → `authorized` | `failed` | `canceled` → `captured` | `failed` | `canceled` → `settled` | `partially_refunded` | `refunded` | `chargeback`  
**payment_method_type:** `card` | `bank_transfer` | `wallet` | `ach` | `other`

---

### 1.18 Subscriptions  `[I]`
**Route file:** `v1-subscriptions.routes.js`  
**Note:** Top-level subscription management. Separate from `/collections/subscriptions` (§1.4).

**Fields:** `subscription_id`, `account_id`, `quote_id`, `external_subscription_ref`, `plan_code`, `status`, `start_date`, `end_date`, `renewal_date`

---

### 1.19 Invoice Summaries  `[I]`
**Route file:** `v1-invoice-summaries.routes.js`

| Endpoint | Method |
|---|---|
| `/invoice-summaries` | GET |
| `/invoice-summaries` | POST |
| `/invoice-summaries/:invoice_summary_id` | GET |
| `/invoice-summaries/:invoice_summary_id` | PATCH |

**Fields:** `invoice_summary_id`, `subscription_id`, `external_invoice_ref`, `invoice_number`, `amount_due`, `amount_paid`, `currency`, `status` (open), `due_date`, `issued_at`

---

### 1.20 Sync  `[I]`
**Route file:** `v1-sync.routes.js`

| Endpoint | Method | Notes |
|---|---|---|
| `/sync/batch` | POST | Max 100 commands per batch |
| `/sync/status` | GET | |

**Batch command fields:** `idempotency_key`, `device_id`, `entity_type`, `entity_id`, `op` (create/update/delete), `payload`, `base_version`, `client_timestamp`

---

### 1.21 Payment Webhooks  `[I]`
**Route file:** `v1-payment-webhooks.routes.js`

| Endpoint | Method | Auth mechanism |
|---|---|---|
| `/jazzcash` | POST | Sorted params HMAC-SHA256 (JAZZCASH_HASH_KEY) |
| `/easypaisa` | POST | Concatenated fields HMAC (EASYPAISA_STORE_PASSWORD) |
| `/log` | GET | Internal — webhook event log |

---

### 1.22 WhatsApp Webhooks  `[I]`
**Route file:** `v1-whatsapp-webhooks.routes.js`

| Endpoint | Method | Auth mechanism |
|---|---|---|
| `/meta` | POST + GET | X-Hub-Signature-256 HMAC (META_APP_SECRET) |
| `/twilio` | POST | None specified |
| `/360dialog` | POST | d360-signature HMAC (DIALOG360_WEBHOOK_SECRET) |
| `/gupshup` | POST | IP trust (no HMAC) |
| `/log` | GET | Internal — webhook event log |

---

## Section 2 — Fresh Archetype Extraction

What UI archetypes each backend domain can support, derived purely from the routes and fields above. No spec assumptions.

| Domain | Supported archetypes | Implied pages |
|---|---|---|
| Leads | A (KPI), B (list), C (detail), I (create form) | Dashboard strip, Lead List, Lead Detail, New Lead Wizard |
| Opportunities | A (pipeline KPI), B (list), C (detail) | Pipeline KPI, Opp List, Opp Detail |
| Followups | A (enforcement KPI/posture), B (queue) | Enforcement strip, Followup Queue |
| Collections | A (KPI), B (invoice queue), C (invoice detail) | Collections KPI, Invoice List, Invoice Detail |
| Tasks | B (list) | Task List |
| Quotes / CPQ | B (list), C (detail), K (builder) | Quote List, Quote Detail, Quote Builder |
| Price Books | G (settings admin) | Price Book Settings |
| Forecasts | H (reporting) ⚠️ POST-only | Forecast Report — requires new GET endpoint or client-initiated POST |
| Activities | C (activity log in entity detail), J (audit trail) | Activity feed in detail pages |
| Contacts | B (list), C (detail) | Contact List, Contact Detail |
| Accounts | B (list), C (detail) | Account List, Account Detail |
| Users | G (settings admin) | User Management Settings |
| Auth | I (login form) | Login Page |
| Emails | L (inbox) | Email Inbox |
| Audit | J (audit/compliance) | Audit Event Log |
| Orders | B (list), C (detail) | Order List, Order Detail |
| Payments | B (list), C (detail), H (revenue summary) | Payment List, Payment Detail, Revenue Report |
| Subscriptions | B (list), C (detail) | Subscription List, Subscription Detail |
| Invoice Summaries | B (list), C (detail) | Invoice Summary List, Invoice Detail |
| Sync | G (settings) | Sync Status Page |
| Payment Webhooks | G (settings) | Webhook Config |
| WhatsApp Webhooks | L (inbox channel), G (settings) | WhatsApp Inbox, Webhook Config |

---

## Section 3 — Existing Archetype Overlay

**Source A:** `DESIGN-SPEC.md §3` defines 13 archetypes A–M across 75 pages.  
**Source B:** Section 2 fresh extraction above.

| Archetype | Spec label | Backend support | Verdict |
|---|---|---|---|
| A | Dashboard / KPI (13 pages) | Leads, Opps, Followups, Collections all provide KPI-worthy aggregates | ✅ Full support |
| B | List / Queue (11 pages) | All major domains support GET list with filters and pagination | ✅ Full support |
| C | Entity Detail (12 pages) | Leads, Opps, Contacts, Accounts, Invoices, Quotes, Payments all have detail GET | ✅ Full support |
| D | Sales Cockpit (1 page) | Consumes Leads + Opps + Tasks + Followups — all exist | ✅ Full support |
| E | Support Console (1 page) | `/api/v1/cases` + `/api/v1/support` + `/api/v1/knowledge` (Sprint 5B-1) | ✅ Full support — Phase 5B-1 |
| F | Marketing (1 page) | `/api/v1/campaigns` + `/api/v1/segments` + `/api/v1/templates` (Sprint 5B-4) | ✅ Full support — Phase 5B-4 |
| G | Settings / Admin (9 pages) | Users, Price Books, Auth, Sync, Webhooks + Territories (5B-3) all exist | ✅ Full support |
| H | Reporting (7 pages) | Payments /revenue/summary exists; Forecasts POST-only | ⚠️ Partial — forecasts need GET or client POST |
| I | Form / Wizard (6 pages) | POST leads, POST contacts, POST opportunities, POST quotes + POST cases (5B-1) exist | ✅ Full support |
| J | Audit / Compliance (4 pages) | Audit events + chain-check + activities (via proxy) | ✅ Full support |
| K | Builder (4 pages) | Quotes CPQ (in-memory) + Price Books (stub) + Workflows (5B-6) | ✅ Full support |
| L | Inbox (3 pages) | Emails + WhatsApp webhooks + `/api/v1/inbox` (Sprint 5B-2) | ✅ Full support — Phase 5B-2 |
| M | AI / Copilot (2 pages) | `/api/v1/ai/scores` + `/predictions` + `/estimates` + `/copilot` + `/models` (Sprint 5B-7) | ✅ Full support — Phase 5B-7 |

**Updated 2026-05-30 (Phase 5B complete):**
- All former gaps resolved: Archetypes E/F/M now have full gateway domains (Cases+KB, Campaigns+Segments+Templates, AI+Copilot).
- Archetype L extended with `/api/v1/inbox` shared inbox routing.
- Archetype H forecasts: H-01 computes client-side via `computeForecast()`; H-07 wired 2026-05-31 via POST /reports/execute.
- **Wiring complete 2026-05-31** — all 75 pages live. DB wiring (replace in-memory stores with PostgreSQL) is commercialization-phase task.

---

## Section 4 — Frontend Page Inventory

8 built custom CRM pages. Data consumption sourced from JS driver reads.

---

### 4.1 `followups.html` — `crm-followups.js`
| | |
|---|---|
| **Archetype** | B — List / Queue |
| **CRM_DUMMY consumed** | `followups.data` |
| **Followup fields used** | followup_id, lead_name, action_type, due_at, escalation_level, attempts_count, state |
| **Backend endpoint** | GET /followups ✓ (path correct) |
| **Gaps** | G-004 (action_type + attempts_count not in backend), G-005 (escalation_level vocab), G-011 (complete: PATCH vs POST), G-019 (PK followup_id vs task_id) |

---

### 4.2 `collections.html` — `crm-collections.js`
| | |
|---|---|
| **Archetype** | B — List / Queue |
| **CRM_DUMMY consumed** | `collections.data` |
| **Status values used** | open, paid, void, uncollectible (aligned to backend) |
| **Backend endpoint** | GET /collections/invoices ✓ (path corrected) |
| **Gaps** | ✅ All resolved — G-006, G-009, G-020, G-021 + NEW-2 (invoice_id, amount_due, account_name, is_overdue, last_reminder_at) |

---

### 4.3 `opportunities-detail.html` — `crm-opportunities-detail.js`
| | |
|---|---|
| **Archetype** | C — Entity Detail |
| **CRM_DUMMY consumed** | single opportunity, activities, quotes |
| **Opp PK used in frontend** | opportunity_id (aligned) |
| **Backend opp PK field** | opportunity_id |
| **Backend endpoint** | GET /opportunities/:opp_id ✓ |
| **Gaps** | ✅ All resolved — G-003 (opportunity_id aligned), G-007 (account_name added to backend entity + dummy), NEW-3 (priority badge map hot/warm/cold) |

---

### 4.4 `quote-builder.html` — `crm-quote-builder.js`
| | |
|---|---|
| **Archetype** | K — Builder |
| **CRM_DUMMY consumed** | `opportunities.data`, `priceBooks.data` |
| **Backend endpoints needed** | GET /price-books, POST /quotes |
| **Gaps** | ✅ G-010 fixed (crm-quote-builder reads from d.priceBooks.data[0].products); ✅ G-022 fixed (crm-dummy priceBooks uses page/page_size pagination); ⚠️ G-010b open (backend stub returns USD, frontend needs PKR — backend stub issue) |

---

### 4.5 `quotes-detail.html` — `crm-quotes-detail.js`
| | |
|---|---|
| **Archetype** | C — Entity Detail |
| **CRM_DUMMY consumed** | single quote, line items |
| **Backend endpoints** | GET /quotes/:quote_id ✓, POST /quotes/:quote_id/acceptances, POST /quotes/:quote_id/orders |
| **Gaps** | ✅ G-023 resolved — crm-dummy.js QUOTES uses opportunity_id; crm-api.js quotes namespace added |

---

### 4.6 `sales-cockpit.html` — `crm-sales-cockpit.js`
| | |
|---|---|
| **Archetype** | D — Sales Cockpit |
| **CRM_DUMMY consumed** | `leads.data`, `opportunities.data`, `followups.data`, `tasks.data`, `forecasts` |
| **Backend endpoints** | GET /leads, GET /opportunities, GET /followups, GET /tasks, GET /forecasts |
| **Gaps** | ✅ All resolved — G-001 (stage vocab), G-018 (tasks schema contract documented), NEW-1 (forecasts by_category shape), NEW-3 (priority badge map hot/warm/cold) |

---

### 4.7 `leads-detail.html` — `crm-leads-detail.js`
| | |
|---|---|
| **Archetype** | C — Entity Detail |
| **CRM_DUMMY consumed** | single lead, followups, activities, opportunities |
| **Backend endpoints** | GET /leads/:lead_id, GET /leads/:lead_id/next-action, GET /followups?lead_id=X, GET /activities?entity_id=X |

---

### 4.8 `sales-dashboard.html` — `crm-sales-dashboard.js`
| | |
|---|---|
| **Archetype** | A — Dashboard / KPI |
| **CRM_DUMMY consumed** | `leads.data`, `opportunities.data`, `payments.data` |
| **Backend endpoints** | GET /leads, GET /opportunities, GET /payments/revenue/summary |

---

## Section 5 — Canonical Archetype List

Archetypes confirmed supported by **both** backend (Section 2) **and** DESIGN-SPEC protocol (Section 3). Per entry: domains, built pages, wiring status, blocking gaps.

| # | Archetype | Backend | Built pages | Wiring status | Blocking gaps |
|---|---|---|---|---|---|
| A | Dashboard / KPI | ✅ | sales-dashboard.html | 🟢 Ready | All gaps resolved (G-001, G-015, NEW-1 forecasts shape) |
| B | List / Queue | ✅ | followups.html, collections.html | 🟢 Ready | All gaps resolved (G-005, G-006, G-009, G-019, NEW-2 collections schema) |
| C | Entity Detail | ✅ | leads-detail.html, opportunities-detail.html, quotes-detail.html | 🟢 Ready | All gaps resolved (G-003, G-007, G-008, G-023, NEW-3 priority maps) |
| D | Sales Cockpit | ✅ | sales-cockpit.html | 🟢 Ready | All gaps resolved (G-001, G-018, NEW-1, NEW-3) |
| E | Support Console | ⚠️ Partial | — not built — | ❌ No ticket domain | No ticket routes in gateway |
| F | Marketing | ⚠️ None | — not built — | ❌ No backend | No marketing domain in gateway |
| G | Settings / Admin | ✅ | — not built — | 🟢 Backend ready | None blocking |
| H | Reporting | ⚠️ Partial | — not built — | 🟡 Partial | G-002 (no GET /forecasts) |
| I | Form / Wizard | ✅ | — not built — | 🟢 Backend ready | None blocking |
| J | Audit / Compliance | ✅ | — not built — | 🟢 Backend ready | None blocking |
| K | Builder | ✅ (stubs) | quote-builder.html | 🟢 Ready | G-010 ✅, G-022 ✅, G-024 ✅; ⚠️ G-010b open (USD stub vs PKR need) |
| L | Inbox | ✅ | — not built — | 🟢 Backend ready | None blocking |
| M | AI / Copilot | ❌ | — not built — | ❌ No gateway routes | AI service not exposed |

---

## Section 6 — Gap Register

All 24 gaps found during Phase M discovery reads (B0–B2). Severity: 🔴 Breaking (wiring will fail at runtime) | 🟡 Mapping (wiring produces wrong data) | 🟢 Minor.

| # | Gap | Severity | Side | Description | Recommended fix |
|---|---|---|---|---|---|
| G-001 | Lead stage vocabulary | 🔴 Breaking | Both | Frontend: new/contacted/engaged/qualified/closed_won/closed_lost. Backend: new/qualifying/nurturing/proposal/negotiation/won/lost/disqualified. Only "new" and "proposal" overlap. | Align crm-dummy.js + crm-leads.js to backend values; update filter chips |
| G-002 | No GET /forecasts endpoint | 🔴 Breaking | Backend | crm-api.js calls `GET /forecasts`. Only `POST /forecasts/model` and `POST /forecasts/aggregate` exist. | Build GET /forecasts in backend OR rewrite frontend to use POST |
| G-003 | opp_id vs opportunity_id field name | 🟡 Mapping | Frontend | CRM_DUMMY uses `opp_id` as PK field. Backend returns `opportunity_id`. Frontend code reading `row.opp_id` gets undefined from live API. | Update crm-dummy.js OPPORTUNITIES to use `opportunity_id` |
| G-004 | Followup action_type + attempts_count missing | 🔴 Breaking | Backend | Frontend displays action_type (Call/WhatsApp/Reminder) and attempts_count. Neither field exists in backend followup schema (`v1-followups.routes.js`). | Add action_type + attempts_count to followup entity + POST /followups |
| G-005 | Followup escalation_level vocabulary | 🔴 Breaking | Both | Frontend: soft/medium/strict. Backend: none/reminder/warning/escalated/reassigned. Entirely different. All filter chips and escalation badges break. | Align both to backend values; update crm-dummy.js + crm-followups.js |
| G-006 | Collections status vocabulary | 🔴 Breaking | Both | Frontend: overdue/partial/unpaid/paid. Backend: draft/open/paid/void/uncollectible. Only "paid" overlaps. All status filters and posture strip break. | Align crm-dummy.js + crm-collections.js to backend values |
| G-007 | account_name not a stored opp field | 🟡 Mapping | Backend | Frontend shows account_name on opp cards. Backend opp entity has account_id only — no account_name. Requires join with accounts service. | Add joined account_name to opp GET response OR resolve client-side via lookup |
| G-008 | lead.followup_enforcement not a lead field | 🟡 Mapping | Frontend | Frontend reads `lead.followup_enforcement` from CRM_DUMMY. Not in backend lead schema. Enforcement status is derived from followup engine. | Remove from lead schema; derive from GET /followups/lead/:id/canonical |
| G-009 | Collections list path mismatch | 🔴 Breaking | Frontend | crm-api.js calls `GET /collections`. Backend route is `GET /collections/invoices`. Will 404. | Fix crm-api.js: `GET /collections` → `GET /collections/invoices` |
| G-010 | Quote builder uses hardcoded price book | 🟡 Mapping | Frontend | crm-quote-builder.js has hardcoded PRICE_BOOK object. `GET /price-books` exists but is never called. Backend stub returns USD; frontend uses PKR. | Wire `GET /price-books`; request PKR price book from backend |
| G-011 | followups.complete: PATCH vs POST | 🔴 Breaking | Frontend | crm-api.js `followups.complete` calls `PATCH /followups/:id`. Backend is `POST /followups/:task_id/complete`. Wrong method + wrong URL structure. | Fix crm-api.js: `PATCH /followups/:id` → `POST /followups/:id/complete` |
| G-012 | Auth endpoint /auth/login vs /auth/sessions | 🔴 Breaking | Frontend | crm-api.js calls `POST /auth/login`. Backend route is `POST /auth/sessions` (currently returns 501 — IdP not wired). | Fix URL; note 501 is expected until P-016 resolved |
| G-013 | Users PK: id vs user_id | 🔴 Breaking | Frontend | Backend GET /users returns `id`. CRM_DUMMY + all frontend use `user_id`. Owner dropdowns fail to match live data. | Update crm-dummy.js USERS: rename `user_id` → `id`; update all JS references |
| G-014 | Lead source vocabulary — extra frontend values | 🟡 Mapping | Frontend | crm-leads.js source filter includes cold_call, event, linkedin. Backend VALID_SOURCES: whatsapp/web/import/manual/referral/campaign. Filters on invalid values return empty. | Remove cold_call/event/linkedin; add campaign to source options |
| G-015 | Lead priority vocabulary | 🔴 Breaking | Both | Frontend/dummy: urgent/low/medium/high. Backend: hot/warm/cold. Entirely different scales. Priority filter and all priority badges mismatch. | Align to backend: hot/warm/cold. Update crm-dummy.js + crm-leads.js |
| G-016 | crm-dashboard.js uses hardcoded data | 🔴 Breaking | Frontend | crm-dashboard.js uses literal JS objects for all chart data. Does not read CRM_DUMMY. C-007 violation. | Rewrite crm-dashboard.js to read from CRM_DUMMY (phase 1); later wire to API |
| G-017 | Contacts schema opaque | 🟡 Mapping | Both | Frontend shows display_name, phone_e164, account_name, last_touchpoint, open_cases, tags, idle. Contacts route is a thin proxy — downstream schema unknown from gateway alone. | Read contacts microservice schema to confirm field alignment before wiring |
| G-018 | Tasks schema opaque | 🟡 Mapping | Both | crm-sales-cockpit.js consumes task fields. Tasks route is a thin proxy — downstream schema unknown. | Read task microservice schema before wiring |
| G-019 | Followup PK: followup_id vs task_id | 🔴 Breaking | Frontend | CRM_DUMMY FOLLOWUPS uses `followup_id` as PK. Backend uses `task_id`. All lookup/complete/snooze calls use the wrong ID field. | Update crm-dummy.js FOLLOWUPS: rename `followup_id` → `task_id`; update JS drivers |
| G-020 | Collections reminder endpoint missing | 🔴 Breaking | Backend | crm-api.js has `POST /collections/:id/reminders`. No such endpoint exists in `v1-collections.routes.js`. | Build `POST /collections/invoices/:invoice_id/reminders` OR remove from crm-api.js |
| G-021 | Collections payment path prefix | 🟡 Mapping | Frontend | crm-api.js calls `POST /collections/:id/payments`. Backend is `POST /collections/invoices/:invoice_id/payments`. Missing `/invoices/` in path. | Fix crm-api.js: include `/invoices/` in payment path |
| G-022 | Price books pagination style | 🟡 Mapping | Frontend | Price books use `page`/`page_size`. Most frontend code assumes `limit`/`offset`. | Use page/page_size when calling `GET /price-books` |
| G-023 | Quote opportunity_id field | 🟡 Mapping | Frontend | CRM_DUMMY QUOTES uses `opp_id` for opportunity reference (consistent with G-003). Backend quote schema uses `opportunity_id`. | Update CRM_DUMMY QUOTES + JS references |
| G-024 | ~~v1-quotes.routes.js missing respondError/respondSuccess import~~ | ✅ Fixed | Backend | Import confirmed present on line 5 of v1-quotes.routes.js. Bug note was stale — fix applied 2026-05-27 per fix log §Session 2. Verified 2026-05-30 by direct file read. | — |

---

## Gap Summary by Side

| Side | Count | Gaps |
|---|---|---|
| Backend only | 3 | G-002, G-004, G-020 |
| Frontend only | 13 | G-003, G-008, G-009, G-011, G-012, G-013, G-014, G-016, G-019, G-021, G-022, G-023, G-010 |
| Both sides | 5 | G-001, G-005, G-006, G-015, G-017/G-018 (investigation) |

## Gap Summary by Severity

| Severity | Count | Gap IDs |
|---|---|---|
| 🔴 Breaking | 13 | G-001, G-002, G-004, G-005, G-006, G-009, G-011, G-012, G-013, G-015, G-016, G-019, G-020 |
| 🟡 Mapping | 10 | G-003, G-007, G-008, G-010, G-014, G-017, G-018, G-021, G-022, G-023 |

---

---

## Bidirectional Alignment — Complete Gap Closure (2026-05-27)

### Original 24 gaps

| Gap | Status | Fix |
|---|---|---|
| G-001 | ✅ Fixed | crm-dummy.js stages + crm-leads.js stageBadge aligned to backend values |
| G-002 | ✅ Fixed | GET /forecasts inline route added to v1-forecasts.routes.js |
| G-003 | ✅ Fixed | crm-dummy.js OPPORTUNITIES + 4 JS files: opp_id → opportunity_id |
| G-004 | ✅ Fixed | action_type + attempts_count added to v1-followups.routes.js POST handler |
| G-005 | ✅ Fixed | escalation_level vocab aligned in crm-dummy.js + crm-followups.js |
| G-006 | ✅ Fixed | collections status aligned in crm-dummy.js + crm-collections.js |
| G-007 | ✅ Fixed | account_name added to v1-opportunities.routes.js POST body + entity; crm-dummy.js OPPORTUNITIES updated |
| G-008 | ✅ Fixed | followup_enforcement removed from crm-leads-detail.js; LEVEL_CFG aligned to backend escalation_level enum |
| G-009 | ✅ Fixed | crm-api.js: `/collections` → `/collections/invoices` |
| G-010 | ✅ Fixed | crm-api.js priceBooks.list() wired; crm-quote-builder.js reads d.priceBooks.data[0].products |
| G-011 | ✅ Fixed | crm-api.js: PATCH→POST, `/followups/:id` → `/followups/:id/complete` |
| G-012 | ✅ Fixed | crm-api.js: `/auth/login` → `/auth/sessions` |
| G-013 | ✅ Fixed | crm-dummy.js + 5 JS files: user_id → id; userMap key updated |
| G-014 | ✅ Fixed | crm-leads.js srcMap: removed cold_call/event/linkedin; added manual/campaign |
| G-015 | ✅ Fixed | crm-dummy.js + crm-leads.js: priorities → hot/warm/cold |
| G-016 | ✅ Fixed | crm-dashboard.js: leadsByHour + invoiceSummaries.monthly_trend wired from CRM_DUMMY |
| G-017 | ✅ Fixed | Downstream schema contract documented in v1-contacts.routes.js; all required fields confirmed in crm-dummy.js CONTACTS |
| G-018 | ✅ Fixed | Downstream schema contract documented in v1-tasks.routes.js; all required fields confirmed in crm-dummy.js TASKS |
| G-019 | ✅ Fixed | crm-dummy.js + crm-api.js: followup_id → task_id |
| G-020 | ✅ Fixed | POST /collections/invoices/:invoice_id/reminders added to v1-collections.routes.js |
| G-021 | ✅ Fixed | crm-api.js: recordPayment path includes `/invoices/` prefix |
| G-022 | ✅ Fixed | crm-dummy.js PRICE_BOOKS uses page/page_size pagination; crm-api.js priceBooks.list() returns full priceBooks object |
| G-023 | ✅ Fixed | crm-dummy.js QUOTES uses opportunity_id; crm-api.js quotes namespace (list/get/create) added |
| G-024 | ✅ Fixed | respondError/respondSuccess import added to v1-quotes.routes.js |

### Additional bidirectional gaps found and fixed (2026-05-27)

| # | Gap | Fix |
|---|---|---|
| NEW-1 | Forecasts shape mismatch — backend GET /forecasts returned flat shape; crm-sales-dashboard.js + crm-sales-cockpit.js read `by_category.*` which didn't exist | v1-forecasts.routes.js GET / response rewritten to `{weighted_value, by_category: {pipeline,best_case,commit,closed each with count+total_value}, stage_breakdown}`; crm-dummy.js FORECASTS rewritten to match; crm-sales-dashboard.js + crm-sales-cockpit.js updated |
| NEW-2 | Collections schema mismatches — backend used `invoice_summary_id`; frontend expected `invoice_id`, `amount_due`, `account_name`, `is_overdue`, `last_reminder_at` | v1-collections.routes.js: PK → `invoice_id`, added `account_name`, `account_tier`, `is_overdue` computed at GET, `last_reminder_at` updated by reminder endpoint; crm-dummy.js COLLECTIONS: `inv_id` → `invoice_id`, `amount` → `amount_due`, added `invoice_number`, `last_reminder_at`; crm-collections.js column mappings corrected |
| NEW-3 | Priority badge maps used wrong vocabulary — crm-sales-cockpit.js + crm-opportunities-detail.js had `urgent/high/medium/low` maps | Both files updated to `{hot:'danger', warm:'warning', cold:'secondary'}` to match canonical backend enum |

**Total gaps closed: 27 (24 original + 3 new). 0 open. All 8 Build Phase 1 pages fully aligned.**

*End of Phase M canonical output. Bidirectional alignment COMPLETE 2026-05-27. Tracker: `D:\CRM\MAPPING-TRACKER.md`*

---

## Section 7 — 75-Page 3-Category Mapping Analysis

**Produced:** 2026-05-28  
**Method:** b9-p specs (updated 2026-05-28) cross-referenced against 23 verified gateway route files read directly. Schema claims for opaque proxies flagged. All classifications hypothetical until proven via successful DUMMY_MODE=false test per page.

**Gateway route files confirmed present (23 total):**
accounts, activities, audit, auth, collections, contacts, emails, followups, forecasts, invoice-summaries, leads, opportunities, orders, payments, payment-webhooks, price-books, quotes, subscriptions, sync, tasks, users, whatsapp-webhooks, + index.js

**Gateway route files confirmed ABSENT:**
cases · tickets · support · marketing · campaigns · workflows · territories · partners · feature-flags · knowledge · ai · conversations · inbox · routing

---

### Category 1 — Exists in Both (25 pages)
*b9-p spec defined + gateway routes present with verifiable or documented fields. Both sides have enough substance to attempt wiring. All still hypothetical until DUMMY_MODE=false test passes.*

| ID | Page | Gateway domains | Backend type | Key caveat |
|---|---|---|---|---|
| A-01 | dashboard.html | Leads[I]+Opps[I]+Followups[I]+Collections[I]+Forecasts[I] | Inline | KPI aggregation client-side; no dedicated endpoint |
| A-02 | leads-dashboard.html | Leads[I] | Inline | LeadFunnelPerformanceRM computed from /leads |
| A-04 | sales-dashboard.html | Opps[I]+Forecasts[I] | Inline | Browser-locked ✓ |
| A-05 | quotes-dashboard.html | Quotes[I] | Inline | QuoteApprovalCycleRM aggregated from /quotes |
| A-06 | subscriptions-dashboard.html | Subscriptions[I]+Collections[I] | Inline | SubscriptionRevenueRetentionRM computed from both |
| B-01 | followups.html | Followups[I] | Inline | action_type + attempts_count added per Phase M — unverified until wired |
| B-02 | leads.html | Leads[I] | Inline | Built ⏳ |
| B-08 | collections.html | Collections[I] invoices | Inline | Built ⏳ |
| B-09 | invoices.html | Invoice Summaries[I] | Inline | Two invoice endpoints (/invoice-summaries + /collections/invoices) — page must pick one |
| B-10 | users.html | Users[I] | Inline | PK is `id` not `user_id` — must use `id` |
| C-01 | leads-detail.html | Leads[I]+Followups[I]+next-action | Inline | Built ⏳; T2 gap pending |
| C-04 | opportunities-detail.html | Opps[I] | Inline | Browser-locked ✓ |
| C-06 | quotes-detail.html | Quotes[I] | Inline | ✅ G-024 resolved — respondError/respondSuccess confirmed imported |
| C-09 | subscriptions-detail.html | Subscriptions[I]+Collections[I] | Inline | Subscription status states need field verification |
| D-01 | sales-cockpit.html | Leads[I]+Opps[I]+Followups[I]+Tasks[P]+Forecasts[I] | Mixed | Browser-locked ✓; Tasks schema opaque |
| G-02 | user-management-crm.html | Users[I] | Inline | Clean |
| H-01 | sales-analytics.html | Leads[I]+Opps[I]+Forecasts[I] | Inline | EmployeePerformanceRM may need activities proxy |
| H-04 | finance-analytics.html | Payments[I]+Collections[I]+Subscriptions[I] | Inline | /revenue/summary needs date params |
| H-06 | audit-report.html | Audit[I] | Inline — in-memory | Data in-memory only — lost on restart |
| I-01 | lead-new.html | Leads[I] POST | Inline | Built ⏳; T1/T2 issues pending |
| I-03 | opportunity-new.html | Opps[I] POST | Inline | Clean |
| I-05 | quote-builder.html | Quotes[I]+Price Books[S] | Mixed | Price Books stub returns USD only — PKR mismatch |
| J-01 | audit-log.html | Audit[I] | Inline — in-memory | In-memory caveat |
| J-02 | compliance-report.html | Audit[I] | Inline — in-memory | View on audit data; same caveat |
| J-04 | rbac-audit.html | Users[I]+Audit[I] | Inline | Permission matrix computed client-side |

---

### Category 2 — Frontend Spec Exists, Backend Missing/Thin (42 pages)

**Sub-group 2a — Zero gateway routes for this domain (23 pages):**
A-07, A-09, A-10, B-05, B-11, C-05, C-10, C-11, C-12, E-01, F-01, G-09, H-02, H-03, H-05, I-04, I-06, K-01, K-02, K-03, L-03, M-01, M-02

Missing domains: cases/tickets · marketing/campaigns · workflows · territories · partners · knowledge · AI · inbox routing

**Sub-group 2b — Opaque proxy only, schema unverifiable at gateway (6 pages):**

| ID | Page | Proxy | Schema status |
|---|---|---|---|
| B-03 | contacts.html | Contacts[P] | Fields in comment only (display_name, phone_e164, etc.) — downstream unverified |
| B-04 | accounts.html | Accounts[P] | No field documentation at all |
| B-07 | tasks.html | Tasks[P] | Fields in comment only — downstream unverified |
| C-02 | contacts-detail.html | Contacts[P] | + CustomerMasterHealthRM not in read-models.md |
| C-03 | accounts-detail.html | Accounts[P] | No schema |
| I-02 | contact-new.html | Contacts[P] POST | Can't verify accepted body fields |

**Sub-group 2c — Backend domain exists but management API missing (8 pages):**

| ID | Page | What exists | What's missing |
|---|---|---|---|
| G-01 | org-settings.html | Users[I]/Auth[I] | No org settings endpoint |
| G-03 | roles.html | /users/:id/roles assignment | No GET/POST /roles for role CRUD |
| G-04 | billing-settings.html | Subscriptions[I] | **→ WIRED 2026-05-31** via v1-billing.routes.js inline stub. P-016 payment method section remains static stub. |
| G-06 | notifications.html | — | No notification preferences API |
| G-07 | feature-flags.html | Evaluation service only | No flag management HTTP API |
| G-08 | compliance.html | Audit[I] | No compliance config endpoint |
| H-07 | report-builder.html | — | **→ WIRED 2026-05-31** via v1-reports.routes.js inline stub (8 canonical KPIs + 7 named RM fields). |
| J-05 | privacy.html | — | No consent/privacy management API |

**Sub-group 2d — Missing read model or spec gap (5 pages):**

| ID | Page | Block reason |
|---|---|---|
| A-03 | contacts-health.html | CustomerMasterHealthRM not in read-models.md; Contacts[P] opaque |
| A-08 | engagement-dashboard.html | **→ WIRED 2026-05-31** via v1-communications.routes.js inline stub (CommunicationEngagementRM + channel breakdown). |
| A-11 | tenants-dashboard.html | No entitlement query endpoint at gateway |
| A-13 | audit-dashboard.html | Audit in-memory only; PlatformReliabilityAuditRM needs persistent data |
| C-08 | invoices-detail.html | b9-p06 does not define Invoice Detail surface |

---

### Category 3 — Backend Richer Than Frontend Spec (8 pages)

| ID | Page | Backend richness not captured in spec |
|---|---|---|
| B-06 | activity.html | Activities service: immutable hash chain, chain-integrity verification, dual event emission. Spec only defines a simple read-only list |
| C-07 | orders-detail.html | Orders have full line items, invoice linkage, subscription creation. Gateway is GET-only; spec says immutable but underspecifies fulfilment richness |
| G-05 | integrations.html | **→ WIRED 2026-05-31** via v1-integrations.routes.js inline stub (4 providers seeded). DLQ/delivery surfacing still not exposed. |
| J-03 | data-governance.html | **→ WIRED 2026-05-31** via v1-governance.routes.js inline stub (classification, retention, SAR). Full 6-plane data-governance-layer.md depth not surfaced. |
| K-04 | approval-lanes.html | Quote approval mechanism exists (draft→accepted + discount threshold). No lane management API beyond 2-state quote lifecycle |
| L-01 | inbox.html | Python conversations service: GET /api/v1/conversations, intent classification, anti-lead-loss. Not accessible at gateway (port 3000) — service at port 5002 only |
| L-02 | inbox-thread.html | Same as L-01 — conversation thread data at Python service layer only |
| A-12 | identity-dashboard.html | Users[I] has full user/role/session data. IdentityAccessPostureRM defined. No posture-aggregation endpoint — all must be computed client-side |

---

### Summary

| Category | Count |
|---|---|
| 1 — Both sides exist | 25 |
| 2 — Frontend spec exists, backend thin/missing | 42 |
| 3 — Backend richer than spec | 8 |
| **Total** | **75** |

**Dominant finding:** 42 of 75 pages have no viable wiring path today. 23 pages have zero backend domain — building them produces permanently dummy-mode pages until backend domains are added.

**Quickest backend-to-frontend unlock:** L-01/L-02 inbox — Python conversation service exists and is rich; a single gateway route addition would move these from Category 3 to Category 1.
