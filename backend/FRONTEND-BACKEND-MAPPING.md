# Frontend ↔ Backend Mapping

**Purpose:** Authoritative reference for wiring NexLink template pages to the live backend API.
**Template:** NexLink v1.3.0 — `D:\CRM\frontend\src\`
**Backend base:** `http://localhost:3000/api/v1/` (gateway — `gateway/routes/index.js`)
**Last updated:** 2026-05-26 (Stage 4 complete — D-005 error envelope, D-006 pagination fields, B-007 auth endpoints, B-002 territory_ids, E-002 traceparent)

---

## How to Use This File

- **Status column:** `DIRECT` = template page maps cleanly to existing API. `EXTEND` = template page exists but needs custom components or extra API calls wired in. `BUILD` = no template page — build from scratch using archetype rules.
- **Auth header on every request:** `Authorization: Bearer <jwt>` — from JWT auth layer (`gateway/middleware/auth-rbac.js`).
- **Response envelope:** all endpoints return `{ data, meta }` — see `docs/api-standards.md`.
- **PKR default:** all monetary fields default to `currency: "PKR"` unless tenant overrides.
- **Tenant isolation:** every API call is scoped by `tenant_id` extracted from the JWT — no manual tenant param needed in frontend calls.

---

## Section 1 — Dashboard Pages

### 1.1 Main Owner Dashboard

| | |
|---|---|
| **Template file** | `src/app/dashboard.html` |
| **Our route** | `/app/sales/dashboard` (maps to spec `b9-p01-dashboard-kpi.md` §2.5 — Opportunity Pipeline) |
| **Status** | `BUILT — PENDING REVIEW` — `crm-dashboard.js` operative with full dummy data |
| **Backend calls** | |

| Widget | API Endpoint | Method | Key response fields |
|---|---|---|---|
| Total Contacts KPI | `GET /api/v1/contacts?limit=1` | GET | `meta.total` |
| Lead Analytics KPI | `GET /api/v1/leads?limit=1` | GET | `meta.total`, filter by `status=open` |
| Active Deals KPI | `GET /api/v1/opportunities?limit=1` | GET | `meta.total` |
| Tasks Overview chart | `GET /api/v1/tasks?limit=200` | GET | group by status client-side |
| Revenue chart (today/week/month) | `GET /api/v1/invoice-summaries` | GET | `period`, `total_revenue` |
| Follow-up overdue strip | `GET /api/v1/followups?state=overdue&limit=5` | GET | `data[].lead_id`, `data[].due_at` |
| Idle leads posture bar | `GET /api/v1/leads?status=open&limit=1` | GET | cross-ref `updated_at` age client-side |
| Recent activities feed | `GET /api/v1/activities?limit=10` | GET | `data[].activity_type`, `occurred_at` |

**Custom components to add:**
- Follow-up enforcement posture strip (red/amber/green) — no template equivalent
- `Today New Leads` header badge → wire to `GET /api/v1/leads?created_after=<today>` count

---

### 1.2 Lead Funnel Dashboard

| | |
|---|---|
| **Template file** | `src/leads.html` (top KPI section) |
| **Our route** | `/app/sales/leads/dashboard` |
| **Status** | `DIRECT` |
| **Backend calls** | |

| Widget | API Endpoint | Key response fields |
|---|---|---|
| Total Leads card | `GET /api/v1/leads?limit=1` | `meta.total` |
| New Leads This Week | `GET /api/v1/leads?created_after=<week_start>&limit=1` | `meta.total` |
| Qualified Leads | `GET /api/v1/leads?stage=qualified&limit=1` | `meta.total` |
| Opportunities Created | `GET /api/v1/opportunities?limit=1` | `meta.total` |
| Opportunities Won | `GET /api/v1/opportunities?stage=closed_won&limit=1` | `meta.total` |
| Total Opportunity Value | `GET /api/v1/forecasts` | `weighted_pipeline` |
| Leads by Source donut | `GET /api/v1/leads?limit=200` | group by `source` client-side |

---

## Section 2 — Lead Management

### 2.1 Lead Queue / List

| | |
|---|---|
| **Template file** | `src/app/leads.html` |
| **Our route** | `/app/leads` |
| **Status** | `BUILT — PENDING REVIEW` — `crm-leads.js` operative with full dummy data |
| **Backend endpoint** | `GET /api/v1/leads` |

**Query params for filters:**
```
stage=<new|contacted|qualified|proposal|negotiation|closed_won|closed_lost>
owner_id=<user_id>
status=<open|contacted|working|closed>
priority=<low|medium|high|urgent>
source=<web|whatsapp|referral|cold_call|event|import|other>
limit=25&offset=0
```

**DataTable column → API field mapping:**

| Column shown | API field | Notes |
|---|---|---|
| Lead name | `contact_name` | Fall back to `contact_phone_e164` if null |
| Phone | `contact_phone_e164` | E.164 format — display with Pakistan prefix |
| Stage | `stage` | Render as colour-coded badge (custom component) |
| Source | `source` | Channel chip |
| Owner | `owner_id` | Resolve display name via `GET /api/v1/users/:id` |
| Priority | `priority` | Badge: urgent=danger, high=warning, medium=info, low=secondary |
| Follow-up due | fetch from `GET /api/v1/followups?lead_id=X` | Show red when `state=overdue` |
| Value | `estimated_value` + `currency` | Format as PKR amount |
| Created | `created_at` | Relative time (use Flatpickr for date range filter) |

**Row quick actions → API calls:**

| Action | API call |
|---|---|
| Assign | `PATCH /api/v1/leads/:lead_id` body: `{ owner_id }` |
| Stage change | `PATCH /api/v1/leads/:lead_id` body: `{ stage }` — triggers atomic history write |
| Next action | `GET /api/v1/leads/:lead_id/next-action` |
| Delete | `DELETE /api/v1/leads/:lead_id` (soft delete) |

**Custom enforcement badge to add:** If `followup.state === 'overdue'`, show red "OVERDUE" chip on row. Non-negotiable — see `docs/followup-enforcement-model.md`.

---

### 2.2 Lead Detail (360 View)

| | |
|---|---|
| **Template file** | `src/app/leads-detail.html` |
| **Our route** | `/app/leads/:lead_id` |
| **Status** | `BUILT — PENDING REVIEW` — `crm-leads.js` (leads-detail mode) operative with full dummy data |
| **Backend calls** | |

| Panel | API Endpoint |
|---|---|
| Lead header | `GET /api/v1/leads/:lead_id` |
| Follow-up enforcement state | `GET /api/v1/followups?lead_id=:lead_id` |
| Next suggested action | `GET /api/v1/leads/:lead_id/next-action` |
| Activity timeline | `GET /api/v1/activities?lead_id=:lead_id` |
| Tasks | `GET /api/v1/tasks?lead_id=:lead_id` |
| Related opportunities | `GET /api/v1/opportunities?contact_id=:contact_id` |

---

## Section 3 — Contact / Customer Management

### 3.1 Contact List

| | |
|---|---|
| **Template file** | `src/customers.html` |
| **Our route** | `/app/contacts` |
| **Status** | `DIRECT` |
| **Backend endpoint** | `GET /api/v1/contacts` |

**DataTable column → API field mapping:**

| Column | API field |
|---|---|
| Name | `display_name` |
| Phone | `phone_e164` |
| Email | `email` |
| Account | `account_id` → resolve via `GET /api/v1/accounts/:id` |
| Completeness score | `completeness_score` — render progress bar |
| Created | `created_at` |

**Row actions:** View detail, Edit (`PATCH /api/v1/contacts/:id`), Delete (`DELETE /api/v1/contacts/:id`)

**Add contact:** `POST /api/v1/contacts` — use `src/form-layout.html` modal pattern

---

### 3.2 Contact Detail

| | |
|---|---|
| **Template file** | `src/profile.html` (adapt) |
| **Our route** | `/app/contacts/:contact_id` |
| **Status** | `EXTEND` |
| **Backend calls** | `GET /api/v1/contacts/:id`, `GET /api/v1/leads?contact_id=:id`, `GET /api/v1/activities?contact_id=:id` |

---

## Section 4 — Opportunity / Pipeline Management

### 4.1 Opportunities List (Table view)

| | |
|---|---|
| **Template file** | `src/deals.html` |
| **Our route** | `/app/opportunities` |
| **Status** | `DIRECT` |
| **Backend endpoint** | `GET /api/v1/opportunities` |

**Query params for filters:**
```
stage=<qualification|discovery|proposal|negotiation|closed_won|closed_lost>
owner_id=<user_id>
forecast_category=<pipeline|best_case|commit|closed|omitted>
limit=25&offset=0
```

**DataTable column → API field mapping:**

| Column | API field | Notes |
|---|---|---|
| Name | `name` | |
| Account | `account_id` | Resolve name |
| Stage | `stage` | Badge — terminal stages (closed_won/closed_lost) greyed |
| Amount | `amount` + `currency` | PKR formatted |
| Forecast | `forecast_category` | Badge |
| Close date | `close_date` | Red if past + not closed |
| Owner | `owner_id` | Resolve display name |
| Probability | `probability` | Progress bar |

**Stage transition:** `PATCH /api/v1/opportunities/:opp_id` body `{ stage }` — backend handles event emission + history automatically.

**Closed opportunity lock:** if `stage ∈ {closed_won, closed_lost}` — disable edit actions on row (backend returns 409 on attempt).

---

### 4.2 Sales Cockpit — Kanban View

| | |
|---|---|
| **Template file** | **BUILD** — no kanban in template |
| **Our route** | `/app/sales/cockpit` |
| **Status** | `BUILD` using Sortable.js (already bundled in `libs/sortable/`) |
| **Spec** | `docs/b9-p03-sales-cockpit.md` |
| **Backend endpoint** | `GET /api/v1/opportunities` (all stages) + `GET /api/v1/forecasts` |

**Kanban columns:** qualification → discovery → proposal → negotiation → closed_won
**Card drag = stage transition:** `PATCH /api/v1/opportunities/:opp_id` body `{ stage: <target_column> }`
**Forecast rail:** `GET /api/v1/forecasts?period=current_month` → show commit / best_case / pipeline totals above kanban

---

## Section 5 — Follow-up Enforcement

### 5.1 Follow-up Queue

| | |
|---|---|
| **Template file** | `src/app/followups.html` |
| **Our route** | `/app/followups` |
| **Status** | `BUILT — PENDING REVIEW` — `crm-followups.js` operative with full dummy data |
| **Backend endpoint** | `GET /api/v1/followups` |

**Query params:**
```
state=<pending|overdue|completed>
owner_id=<user_id>
escalation_level=<soft|medium|strict>
limit=25&offset=0
```

**Column → API field mapping:**

| Column | API field | Notes |
|---|---|---|
| Lead | `lead_id` → resolve name | Link to lead detail |
| State | `state` | `overdue` = danger badge, `pending` = warning, `completed` = success |
| Escalation | `escalation_level` | `strict` = red, `medium` = amber, `soft` = grey |
| Due | `due_at` | Red when past |
| Owner | `owner_id` | |
| Rule | `rule_type` | |

**Actions:** Mark complete → `PATCH /api/v1/followups/:followup_id` body `{ state: 'completed' }`, Reschedule → `POST /api/v1/tasks/:task_id/reschedule`

---

## Section 6 — Sales & Revenue Analytics

### 6.1 Sales Analytics

| | |
|---|---|
| **Template file** | `src/sales.html` |
| **Our route** | `/app/analytics/sales` |
| **Status** | `DIRECT` |
| **Backend calls** | |

| Chart/Widget | API Endpoint | Notes |
|---|---|---|
| Revenue chart | `GET /api/v1/invoice-summaries?period=month` | Wire to ApexCharts |
| Pipeline by stage | `GET /api/v1/opportunities` group by stage | Bar chart |
| Forecast vs actual | `GET /api/v1/forecasts` | Commit/best_case/actual bars |
| Win rate | `GET /api/v1/opportunities?stage=closed_won` vs total | Calculated client-side |
| Top deals | `GET /api/v1/opportunities?limit=5` sort by `amount DESC` | Table |

---

### 6.2 Finance Page

| | |
|---|---|
| **Template file** | `src/finance.html` |
| **Our route** | `/app/finance` |
| **Status** | `EXTEND` |
| **Backend calls** | |

| Widget | API Endpoint | Notes |
|---|---|---|
| Total Revenue | `GET /api/v1/invoice-summaries` | `total_revenue` |
| Total Expenses | not in current backend — placeholder | Leave as static until expense tracking built |
| Net Profit | derived from revenue − expenses | |
| Pending Invoices | `GET /api/v1/invoice-summaries?status=pending` | `meta.total` |
| Revenue vs Expenses chart | `GET /api/v1/invoice-summaries?group_by=month` | ApexCharts bar |
| Payment list | `GET /api/v1/payments` | Status badges: initiated/captured/settled/refunded |
| Collections queue | `GET /api/v1/collections` | Overdue receivables |

**Payment status badge mapping:**

| `status` field | Badge style |
|---|---|
| `initiated` | info |
| `authorized` | primary |
| `captured` | success subtle |
| `settled` | success |
| `failed` | danger |
| `canceled` | secondary |
| `refunded` | warning |
| `chargeback` | danger outline |

**Note:** `stub_mode=True` on all payment adapters — never show "Pay now" buttons until P-016 unblocked.

---

## Section 7 — Activities & Tasks

### 7.1 Activities Feed

| | |
|---|---|
| **Template file** | `src/activities.html` |
| **Our route** | `/app/activities` |
| **Status** | `DIRECT` |
| **Backend endpoint** | `GET /api/v1/activities` |

| Column | API field |
|---|---|
| Activity type | `activity_type` — icon mapped per type |
| Description | `description` |
| Entity | `entity_type` + `entity_id` — link to relevant detail page |
| Performed by | `performed_by` — resolve user display name |
| Time | `occurred_at` — relative time |

---

### 7.2 Task Management

| | |
|---|---|
| **Template file** | `src/task-management.html` |
| **Our route** | `/app/tasks` |
| **Status** | `DIRECT` |
| **Backend endpoints** | `GET /api/v1/tasks`, `POST /api/v1/tasks`, `POST /api/v1/tasks/:task_id/reschedule` |

| Column | API field |
|---|---|
| Title | `title` |
| Status | `status` — badge |
| Due | `due_at` — red when overdue |
| Owner | `owner_id` |
| Related entity | `entity_type` / `entity_id` — link |

**Create task:** use `src/form-layout.html` modal → `POST /api/v1/tasks`
**Reschedule:** `POST /api/v1/tasks/:task_id/reschedule` body `{ new_due_at }`

---

### 7.3 Calendar

| | |
|---|---|
| **Template file** | `src/calendar.html` — FullCalendar already wired |
| **Our route** | `/app/calendar` |
| **Status** | `EXTEND` |
| **Backend calls** | `GET /api/v1/tasks?limit=200`, `GET /api/v1/followups?limit=200` |

**Event sources for FullCalendar:**
- Tasks: `due_at` → calendar event, colour by `priority`
- Follow-ups: `due_at` → calendar event, colour red when `state=overdue`
- Click event → open task/lead detail in offcanvas

---

## Section 8 — Communication

### 8.1 WhatsApp / Chat Inbox

| | |
|---|---|
| **Template file** | `src/chat.html` (extend — does not have WhatsApp-specific layout) |
| **Our route** | `/app/inbox/whatsapp` |
| **Status** | `EXTEND` |
| **Spec** | `docs/b9-p13-inbox-communication.md`, `docs/whatsapp-execution-model.md` |
| **Backend endpoints** | `GET /api/v1/webhooks/whatsapp`, `GET /api/v1/leads?source=whatsapp` |

**Extensions needed on top of chat.html:**
- WhatsApp-style bubble layout (right=outbound, left=inbound)
- Offline compose queue (messages composed offline, sent on reconnect)
- Intent detection label on messages (show detected intent from backend)
- RTL layout when `locale=ur` — swap `dir` + load `styles-rtl.css`
- Lead creation from WhatsApp message (quick action → `POST /api/v1/leads`)

---

### 8.2 Email Inbox

| | |
|---|---|
| **Template file** | `src/inbox.html`, `src/read-email.html`, `src/compose.html` |
| **Our route** | `/app/inbox/email` |
| **Status** | `DIRECT` |
| **Backend endpoint** | `GET /api/v1/emails`, `POST /api/v1/emails` |

---

## Section 9 — Marketing

### 9.1 Marketing Workspace

| | |
|---|---|
| **Template file** | `src/marketing.html` |
| **Our route** | `/app/marketing` |
| **Status** | `EXTEND` |
| **Spec** | `docs/b9-p05-marketing-workspace.md` |
| **Backend calls** | `GET /api/v1/leads?source=campaign`, `GET /api/v1/activities?activity_type=campaign` |

**MR-001 hook point:** When Facebook/Instagram lead capture is unblocked, wire `POST /api/v1/leads` with `source=facebook` or `source=instagram` from this page.

---

## Section 10 — Quotes, Orders & CPQ

### 10.1 Quote List

| | |
|---|---|
| **Template file** | **BUILD** — no quote template page |
| **Our route** | `/app/quotes` |
| **Status** | `BUILD` — use `src/tables-datatable.html` as shell |
| **Spec** | `docs/b9-p11-form-wizard.md`, `docs/cpq-quotes-orders.md` |
| **Backend endpoint** | `GET /api/v1/quotes` |

| Column | API field |
|---|---|
| Quote ID | `quote_id` |
| Opportunity | `opportunity_id` → resolve name |
| Currency | `currency` |
| Total | line items sum |
| Valid until | `valid_until` — red if expired |
| Status | `status` |

**Create quote:** `POST /api/v1/quotes` requires `opportunity_id`, `currency`, `valid_until`, `line_items[]`, `tax_percent`
**Accept quote:** `POST /api/v1/quotes/:quote_id/accept` → creates order via unit-of-work

---

### 10.2 Orders

| | |
|---|---|
| **Template file** | **BUILD** — use DataTable shell |
| **Our route** | `/app/orders` |
| **Status** | `BUILD` |
| **Backend endpoint** | `GET /api/v1/orders` |

---

### 10.3 Price Books

| | |
|---|---|
| **Template file** | **BUILD** — use DataTable shell |
| **Our route** | `/app/price-books` |
| **Status** | `BUILD` |
| **Backend endpoint** | `GET /api/v1/price-books` |

---

## Section 11 — Users, Teams & RBAC

### 11.1 User Management

| | |
|---|---|
| **Template file** | `src/user-management.html` |
| **Our route** | `/app/admin/users` |
| **Status** | `DIRECT` |
| **Backend endpoint** | `GET /api/v1/users` |

| Column | API field |
|---|---|
| Name | `display_name` |
| Email | `email` |
| Status | `status` — active/inactive badge |
| Created | `created_at` |

**Pagination params:** `page`, `page_size`

---

### 11.2 Team / Employee View

| | |
|---|---|
| **Template file** | `src/employee.html` |
| **Our route** | `/app/admin/team` |
| **Status** | `DIRECT` |
| **Backend endpoint** | `GET /api/v1/users` (same endpoint, different presentation) |

---

## Section 12 — Audit & Compliance

### 12.1 Audit Log

| | |
|---|---|
| **Template file** | **BUILD** — no audit template. Use `src/tables-datatable.html` as shell. |
| **Our route** | `/app/admin/audit` |
| **Status** | `BUILD` |
| **Spec** | `docs/b9-p12-audit-compliance.md` |
| **Backend endpoints** | `GET /api/v1/audits/events`, `GET /api/v1/audits/chain-check` |

**Custom component required:** Immutable log indicator — no edit/delete icons on rows. Hash-chain integrity badge pulled from `GET /api/v1/audits/chain-check`. Green = chain intact, red = breach detected.

**Column → API field:**

| Column | API field |
|---|---|
| Event type | `event_type` |
| Actor | `actor_id` → resolve display name |
| Entity | `entity_type` + `entity_id` |
| Timestamp | `occurred_at` — immutable, no edit |
| Hash | `chain_hash` (if present) — truncated display |
| Tenant | `tenant_id` |

---

## Section 13 — Settings & Admin

### 13.1 Account Settings

| | |
|---|---|
| **Template file** | `src/settings.html` |
| **Our route** | `/app/settings` |
| **Status** | `EXTEND` |
| **Spec** | `docs/b9-p09-settings-admin.md` |

**Settings sections to wire:**
- Profile fields → `PATCH /api/v1/users/:user_id`
- Tenant feature flags → `GET /api/v1/accounts/:tenant_id` + feature flag endpoints
- Payment adapter status → read `stub_mode` from config — display "Payment integration pending" when `stub_mode=true`
- Locale toggle (EN/UR) → client-side `dir` attribute + CSS swap (no API call needed)

---

## Section 14 — Authentication

### 14.1 Auth Pages

| Template file | Our route | Backend |
|---|---|---|
| `src/app/login.html` ✓ BUILT | `/login` | `POST /api/v1/auth/sessions` → returns JWT (B-007) |
| `src/app/register.html` ✓ BUILT | `/register` | `POST /api/v1/auth/register` |
| `src/app/forgot-password.html` ✓ BUILT | `/forgot-password` | `POST /api/v1/auth/forgot-password` |
| `src/app/reset-password.html` ✓ BUILT | `/reset-password` | `POST /api/v1/auth/reset-password` |

**Auth session management (B-007):**
- `POST /api/v1/auth/sessions` — login (returns JWT; IdP not yet wired → 501 until P-016/IdP resolved)
- `DELETE /api/v1/auth/sessions/current` — logout (revokes JWT jti in blocklist; returns `{revoked: true}`)
- `POST /api/v1/users/:user_id/roles` — assign role (requires `users.manage_roles` scope; returns `user_role_id`, `role_id`, `assigned_at`)

**JWT storage:** `localStorage.setItem('crm_token', jwt)` — attach as Bearer on every request.
**RBAC gate:** Check `user.role` from JWT claims before rendering role-gated sections. Roles: `super_admin`, `tenant_admin`, `sales_manager`, `sales_rep`, `finance`, `data_admin`.
**JWT claims (B-001/B-002):** Token contains `sub`, `tenant_id`, `role`, `role_ids`, `scopes`, `aud`, `iss`, `jti`, `territory_ids[]`. Frontend can read `territory_ids` to filter data to assigned territories.

---

## Section 15 — AI Copilot Panel

| | |
|---|---|
| **Template file** | `src/ai/` section (new-chat, search-apps, your-chat, etc.) |
| **Our route** | `/app/ai` |
| **Status** | `EXTEND` |
| **Spec** | `docs/b9-p14-ai-copilot.md` |
| **Backend** | `GET /api/v1/leads/:lead_id/next-action` (primary AI surface) |

**Advisory-only rule:** AI panel never takes autonomous actions. It displays suggestions from `next-action` endpoint. User must confirm before any write operation.

---

## Section 16 — Pages to BUILD from Scratch

These have no matching template page. Build using archetype rules from spec docs and Bootstrap 5 components already in the template.

| Page | Our route | Spec | Archetype base | Key backend |
|---|---|---|---|---|
| Sales Cockpit (Kanban) | `/app/sales/cockpit` | `b9-p03-sales-cockpit.md` | Sortable.js + card grid | `GET /api/v1/opportunities` + `GET /api/v1/forecasts` |
| Support Console | `/app/support` | `b9-p04-support-console.md` | `chat.html` + DataTable | `GET /api/v1/activities` + `GET /api/v1/tasks` |
| Workflow Builder | `/app/admin/workflows` | `b9-p07-workflow-visual-ui.md` | Custom visual canvas | — (spec-driven build) |
| Custom Object Builder | `/app/admin/objects` | `b9-p08-builder-extensions.md` | Form builder pattern | — |
| Quote Builder (CPQ) | `/app/quotes/new` | `b9-p11-form-wizard.md` | `form-layout.html` multi-step | `POST /api/v1/quotes` |
| Audit Log | `/app/admin/audit` | `b9-p12-audit-compliance.md` | DataTable (read-only) | `GET /api/v1/audits/events` |
| Follow-up Queue | `/app/followups` | `docs/adoption-ux.md` Tier 1 | `leads.html` DataTable shell | `GET /api/v1/followups` |

---

## Section 17 — Custom Components (Build Once, Use Everywhere)

These are reusable components not present in NexLink — build as standalone Bootstrap 5 partials and include via JS injection or HTML include.

| Component | Used on | Implementation |
|---|---|---|
| `followup-badge.html` | Lead row, Lead detail, Follow-up queue | Red/amber/grey badge showing `state` + `escalation_level` |
| `enforcement-strip.html` | All dashboards (posture zone) | Top-of-page alert bar: X overdue follow-ups, Y unassigned leads |
| `payment-status-badge.html` | Finance page, Order detail | Colour-coded per Section 6 status table |
| `whatsapp-bubble.html` | Chat / inbox | WhatsApp-style message bubble, RTL-safe |
| `rtl-locale-switcher.js` | Header (all pages) | Toggle `<html dir="rtl">` + swap `styles.css` ↔ `styles-rtl.css` |
| `audit-row.html` | Audit log | Read-only row, no edit/delete icons, hash truncation display |
| `kanban-card.html` | Sales cockpit | Bootstrap card + Sortable.js drag handle |

---

## Section 18 — RTL / Urdu Locale Wiring

The template ships with `src/index-rtl.html` as the RTL demo and `assets/css/styles-rtl.css` pre-built.

**Implementation pattern (do once, apply globally):**

```javascript
// rtl-locale-switcher.js
function setLocale(locale) {
  const html = document.documentElement;
  const cssLink = document.getElementById('main-stylesheet');

  if (locale === 'ur') {
    html.setAttribute('dir', 'rtl');
    html.setAttribute('lang', 'ur');
    cssLink.href = 'assets/css/styles-rtl.css';
  } else {
    html.setAttribute('dir', 'ltr');
    html.setAttribute('lang', 'en');
    cssLink.href = 'assets/css/styles.css';
  }
  localStorage.setItem('crm_locale', locale);
}

// On page load
const saved = localStorage.getItem('crm_locale') || 'en';
setLocale(saved);
```

**Urdu string placeholder:** Until P-017 (native Urdu speaker sign-off) is unblocked, all Urdu strings are marked `/* UR_TODO */` in template comments. Do not ship Urdu strings without sign-off.

---

## Section 19 — API Response Shape Reference

All endpoints follow the envelope from `docs/api-standards.md`:

```json
{
  "data": { ... } | [ ... ],
  "meta": {
    "request_id": "uuid",
    "total_items": 840,
    "total_pages": 34,
    "limit": 25,
    "offset": 0
  }
}
```

**Note (D-006):** Pagination fields are `total_items` + `total_pages` — NOT `total`. Frontend code must use `meta.total_items` / `meta.total_pages`.

**Error envelope (D-005):**
```json
{
  "error": {
    "code": "not_found",
    "message": "human-readable message"
  },
  "meta": { "request_id": "uuid" }
}
```

Error codes map to HTTP status: `bad_request` (400), `unauthorized` (401), `forbidden` (403), `not_found` (404), `conflict` (409), `unprocessable_entity` (422), `internal_server_error` (500). All Python HTTPException errors flow through this envelope automatically (global handler in `services/app.py`).

**Date format:** All dates are ISO 8601 UTC — `2026-05-04T10:30:00Z`. Use Flatpickr for date inputs.

---

## Section 20 — Blocked / Deferred Surfaces

Do not build UI for these until external unblocks arrive:

| Surface | Blocked by | Action |
|---|---|---|
| JazzCash / Easypaisa payment button | P-016 — credentials | Show "Coming soon" badge, never render a real pay button |
| Easypaisa payment webhook status | P-016 | Read `stub_mode` flag — display stub notice |
| Urdu UI strings (beyond EN placeholders) | P-017 — native speaker | Mark all UR strings as `/* UR_TODO */` |
| Facebook/Instagram lead capture | MR-001 — Meta Business Manager | Wire hook point in marketing page, leave dormant |
| Voice note transcription | MR-003 — provider selection | Leave microphone icon as disabled in WhatsApp UI |
| Kuickpay adapter | MR-007 — P-016 first | Not applicable until P-016 resolved |

---

## Section 21 — Build Order (Frontend Priority)

Matches spec start point (`b9-p01-dashboard-kpi.md`) and adoption-ux.md Tier 1 priority:

```
Phase 1 — Core execution surfaces (build first):
  1. Auth pages (login/register/reset) — gates everything else
  2. Follow-up Queue (/app/followups) — Tier 1, highest business value
  3. Lead Queue (/app/leads) — core daily driver
  4. Lead Detail 360 view (/app/leads/:id)
  5. Owner Dashboard (/app/sales/dashboard)

Phase 2 — Pipeline & revenue:
  6. Opportunities list (/app/opportunities)
  7. Sales Cockpit kanban (/app/sales/cockpit)
  8. Contact list + detail (/app/contacts)
  9. Finance page (/app/finance)

Phase 3 — Communication & collaboration:
  10. WhatsApp inbox (/app/inbox/whatsapp)
  11. Task management (/app/tasks)
  12. Calendar (/app/calendar)
  13. Email inbox (/app/inbox/email)

Phase 4 — Analytics & reporting:
  14. Sales analytics (/app/analytics/sales)
  15. Marketing workspace (/app/marketing)
  16. Reporting pages (/app/reports)

Phase 5 — Admin & compliance:
  17. User management (/app/admin/users)
  18. Settings (/app/settings)
  19. Audit log (/app/admin/audit)
  20. Quote builder CPQ (/app/quotes/new)
  21. Workflow builder (/app/admin/workflows)
  22. AI copilot panel (/app/ai)
```
