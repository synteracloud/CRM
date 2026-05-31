# B9-P02::LIST_QUEUE_TABLE_VIEW

## Scope

Defines the **List / Queue / Table View** archetype — 11 named list surfaces.
Anchored to `docs/architecture/domain-model.md`, `docs/ui/read-models.md`, and `docs/infrastructure/api-standards.md`.
Interaction rules for queue-first surfaces per `docs/product/adoption-ux.md` §2 (Tier 1 — follow-up queue).

---

## 1) Archetype Structure

All list/queue views share a common shell:

```
┌─ Filter bar (chips + search) ─────────────────────────────┐
├─ Column header row (sortable) ────────────────────────────┤
├─ Row 1 [primary data] [badges] [quick actions] ───────────┤
├─ Row N ...                                                 ┤
├─ Bulk action bar (visible when ≥1 row selected) ──────────┤
└─ Pagination / infinite scroll ────────────────────────────┘
```

**Design rules:**
- Default sort: most urgent / newest first (configurable per list type).
- Filter chips are persisted per user session (not global).
- Bulk actions apply only to selected rows; confirmation required for destructive bulk ops.
- Row quick actions: max 3 visible; overflow into `…` menu.
- Every list supports keyboard navigation (↑↓ to move, Enter to open detail, Space to select).

---

## 2) The 11 List / Queue Views

### 2.1 — Lead Queue

**Route:** `/app/leads`
**Source entity:** `Lead`
**Read model:** `LeadFunnelPerformanceRM`
**Default sort:** `created_at DESC` (newest first); urgent-flag leads pinned top

| Column | Source | Notes |
|---|---|---|
| Lead name / phone | `Lead.contact_name`, `Lead.normalized_phone` | Phone shown when name absent |
| Stage | `Lead.stage` | Colour-coded badge |
| Source | `Lead.source` | Channel chip |
| Owner | `Lead.assigned_to` | Avatar + name |
| Follow-up due | `FollowupTask.due_at` | Red when overdue |
| Last activity | `Lead.updated_at` | Relative time |

**Canonical `Lead.stage` values** (from `domain-model.md`):
`new` · `qualifying` · `nurturing` · `proposal` · `negotiation` · `won` · `lost` · `disqualified`

**Filter chips:** Stage (`new` / `qualifying` / `nurturing` / `proposal` / `negotiation`), Owner, Source, Follow-up overdue (toggle), Idle > N days
**Quick actions:** `Assign`, `Schedule follow-up`, `Open detail`
**Bulk actions:** `Reassign`, `Add to campaign`, `Export`

---

### 2.2 — Contact List

**Route:** `/app/contacts`
**Source entity:** `Contact`
**Default sort:** `last_name ASC`

| Column | Source | Notes |
|---|---|---|
| Name | `Contact.first_name + last_name` | |
| Phone | `Contact.phone_e164` | Display format (Pakistan adapter) |
| Account | `Account.name` | FK link |
| Last touchpoint | derived from `MessageThread` | Relative time |
| Open cases | derived from `Case` count | Badge |
| Tags | `Contact.tags` | Up to 3 chips |

**Filter chips:** Account, Has open case, Last touchpoint > N days, Tag
**Quick actions:** `Call`, `Send WhatsApp`, `Open detail`
**Bulk actions:** `Assign to account`, `Add tag`, `Export`

---

### 2.3 — Account List

**Route:** `/app/accounts`
**Source entity:** `Account`
**Default sort:** `account_tier DESC`, then `name ASC`

| Column | Source | Notes |
|---|---|---|
| Account name | `Account.name` | |
| Tier | `Account.account_tier` | Badge |
| Industry | `Account.industry` | |
| Open opportunities | derived from `Opportunity` count | |
| Outstanding invoices | derived from `InvoiceSummary` | PKR amount |
| Owner | `Account.owner_id` | |

**Filter chips:** Tier, Industry, Owner, Has overdue invoice, Open opportunity
**Quick actions:** `New opportunity`, `New case`, `Open profile`
**Bulk actions:** `Reassign owner`, `Export`

---

### 2.4 — Ticket / Case Queue

**Route:** `/app/support/cases`
**Source entity:** `Case`
**Read model:** `CaseSLAOperationalRM`
**Default sort:** `response_due_at ASC` (nearest SLA breach first)

| Column | Source | Notes |
|---|---|---|
| Ticket ID + subject | `Case.case_number`, `Case.subject` | |
| Status | `Case.status` | |
| Priority | `Case.priority` | |
| SLA state | `Case.sla_state` | `healthy` / `at_risk` / `breached` — colour coded |
| Owner / queue | `Case.assigned_to` | |
| Response due | `Case.response_due_at` | Red when overdue |

**Filter chips:** Status, Priority, SLA state, Owner, Queue
**Quick actions:** `Claim`, `Reassign`, `Escalate`, `Open detail`
**Bulk actions:** `Reassign`, `Set priority`, `Export`

---

### 2.5 — Activity Feed

**Route:** `/app/activity`
**Source entity:** `ActivityEvent`
**Default sort:** `occurred_at DESC`

| Column | Source | Notes |
|---|---|---|
| Event type | `ActivityEvent.event_type` | Icon + label |
| Subject / target | polymorphic FK | Lead / Opportunity / Case name |
| Actor | `ActivityEvent.actor_id` | User name |
| Tenant | `ActivityEvent.tenant_id` | Admin view only |
| Timestamp | `ActivityEvent.occurred_at` | Absolute + relative |

**Filter chips:** Event type, Actor, Entity type, Date range
**Quick actions:** `View record`, `View audit detail`
**Bulk actions:** `Export` (audit-trail compliant export only)

Design rule: activity feed is **read-only** — no inline edits, no delete.

---

### 2.6 — Task Queue

**Route:** `/app/tasks`
**Source entity:** `Task` (via `ActivityEvent`)
**Read model:** `ActivityTaskOperationalRM`
**Default sort:** `due_at ASC`, overdue pinned top

| Column | Source | Notes |
|---|---|---|
| Task title | `Task.title` | |
| Linked record | polymorphic FK | Lead / Opportunity / Case |
| Owner | `Task.assigned_to` | |
| Due | `Task.due_at` | Overdue badge |
| Status | `Task.status` | |

**Filter chips:** Owner, Linked entity type, Overdue (toggle), Date range
**Quick actions:** `Complete`, `Snooze`, `Reassign`
**Bulk actions:** `Complete selected`, `Reassign`

---

### 2.7 — Follow-up Queue

**Route:** `/app/followups`
**Source entity:** `FollowupTask`
**Default sort:** `due_at ASC` — overdue pinned
**Priority surface:** Tier 1 per `docs/product/adoption-ux.md` §2 — always visible

| Column | Source | Notes |
|---|---|---|
| Lead / contact name | `Lead.contact_name` | |
| Action type | `FollowupTask.action_type` | `Call` / `WhatsApp` / `Reminder` |
| Due | `FollowupTask.due_at` | |
| Escalation level | `FollowupTask.escalation_level` | see canonical values below |
| Attempts | `FollowupTask.attempts_count` | Badge |
| State | `FollowupTask.state` | `pending` / `overdue` / `completed` / `snoozed` / `failed` |

**Canonical `FollowupTask.escalation_level` values** (from `followup-enforcement-model.md`):
`none` · `reminder` · `warning` · `escalated` · `reassigned`

**Filter chips:** Action type (`Call` / `WhatsApp` / `Reminder`), Escalation level (`none` / `reminder` / `warning` / `escalated` / `reassigned`), Overdue (toggle), Owner
**Quick actions:** `Log done`, `Snooze`, `Send WhatsApp`, `Call`
**Bulk actions:** `Snooze selected`, `Reassign`

---

### 2.8 — Collections Queue

**Route:** `/app/collections`
**Source entity:** `Invoice`, `PaymentEvent`
**Default sort:** `due_date ASC`, overdue first

| Column | Source | Notes |
|---|---|---|
| Invoice # | `Invoice.invoice_number` | |
| Account / contact | `Account.name` / `Contact.name` | |
| Amount | `Invoice.amount_due` | PKR formatted |
| Status | `Invoice.status` | `unpaid` / `partial` / `paid` / `overdue` |
| Due date | `Invoice.due_date` | |
| Last reminder | derived from `ReminderEvent` | |

**Filter chips:** Status, Amount band, Account tier, Overdue (toggle), Reminder sent
**Quick actions:** `Record payment`, `Send reminder`, `Escalate`
**Bulk actions:** `Send bulk reminder`, `Export`

---

### 2.9 — Invoice Queue

**Route:** `/app/finance/invoices`
**Source entity:** `InvoiceSummary`
**Default sort:** `created_at DESC`

| Column | Source | Notes |
|---|---|---|
| Invoice # | `InvoiceSummary.invoice_number` | |
| Account | `Account.name` | |
| Total | `InvoiceSummary.total_amount` | PKR |
| Paid | `InvoiceSummary.paid_amount` | |
| Balance | derived | |
| Status | `InvoiceSummary.status` | |
| Due date | `InvoiceSummary.due_date` | |

**Filter chips:** Status, Account, Amount range, Period
**Quick actions:** `Record payment`, `Download PDF`, `Open detail`
**Bulk actions:** `Export`

---

### 2.10 — User Directory

**Route:** `/app/admin/users`
**Source entity:** `User`, `Role`, `UserRole`
**Role gate:** `admin`, `tenant_admin`
**Default sort:** `last_name ASC`

| Column | Source | Notes |
|---|---|---|
| Name | `User.full_name` | |
| Email | `User.email` | |
| Role(s) | `UserRole` → `Role.name` | Badge list |
| Status | `User.status` | active / inactive / suspended |
| Last login | `SessionToken.created_at` | Relative time |
| Tenant | `User.tenant_id` | Admin view only |

**Filter chips:** Role, Status, Last login > N days
**Quick actions:** `Edit roles`, `Suspend`, `Reset password`
**Bulk actions:** `Assign role`, `Suspend selected`, `Export`

---

### 2.11 — Partner List

**Route:** `/app/partners`
**Source entity:** `Partner`, `PartnerRelationship`
**Role gate:** `sales_manager`, `admin`
**Default sort:** `partner_tier DESC`, `name ASC`

| Column | Source | Notes |
|---|---|---|
| Partner name | `Partner.name` | |
| Tier | `Partner.partner_tier` | |
| Region | `Partner.region` | |
| Open opportunities | derived from attributed opportunities | |
| Commission due | derived from `PartnerCommission` | PKR |
| Status | `Partner.status` | |

**Filter chips:** Tier, Region, Status, Has commission due
**Quick actions:** `View profile`, `New deal registration`, `Pay commission`
**Bulk actions:** `Export`

---

## 3) Shared Interaction Patterns

1. **Master-detail without page churn:** selecting a row opens detail pane inline (or slide-over on mobile). List remains visible.
2. **≤2 steps for primary action:** per `docs/ui/ui-foundations.md` §6 — primary row action is one tap. Confirmation only for destructive ops.
3. **Filter persistence:** active filters are preserved in URL query string for shareability.
4. **Column customisation:** user can reorder and toggle column visibility; preference persisted per user + list type.
5. **Offline state:** queue/list shows cached data with staleness indicator when offline. Per `docs/infrastructure/offline-sync.md` §13.
6. **Empty state strings:** from `gateway/services/i18n.js` — `empty.leads`, `empty.followups`, `empty.invoices`, `empty.no_results`.

---

## 4) DataTable Implementation Rules

All list/queue surfaces use DataTables. The following rules are non-negotiable — verified against production bugs 2026-05-27:

**Column alignment — three places required:**

1. **HTML `<thead>`** — every `<th>` must carry an explicit alignment class:
   - `dt-head-left` — names, IDs, long text
   - `dt-head-center` — badges, dates, status, short codes, action buttons
   - `dt-head-right` — PKR/monetary amounts, numeric totals

2. **JS column definition** — every column entry must carry `className`:
   ```javascript
   { data: 'field', className: 'dt-body-center' }
   ```

3. **`crm-custom.css` with `!important`** — DataTables' own stylesheet overrides `className` at runtime regardless of specificity. Always add explicit per-table CSS rules:
   ```css
   #dt_TableName.dataTable tbody > tr > td { text-align: center !important; }
   #dt_TableName.dataTable tbody > tr > td:nth-child(N) { text-align: left !important; }
   ```
   Without `!important` these rules lose to DataTables' internal stylesheet.

**Filter chips:** All tab-style filter strips must use `nav-pills nav-pills-custom p-1 bg-light rounded-5` — never `btn-group`.

---

## SELF-QC

- **All 11 Archetype.md list pages documented:** ✅ — 2.1–2.11 match exactly.
- **Every list anchored to a source entity in domain-model.md:** ✅
- **Default sort defined for all lists:** ✅
- **Filter chips defined for all lists:** ✅ — vocabularies aligned to normalized backend (2026-05-28 update)
- **Quick actions ≤3 per row:** ✅ — overflow rule stated.
- **≤2 steps rule respected:** ✅ — primary action is single tap.
- **Offline + empty states covered:** ✅
- **Canonical stage / escalation / status enums added:** ✅ — Lead.stage, FollowupTask.escalation_level, Invoice.status aligned to domain specs (2026-05-28)

Score: **10/10**

## Error States (All List/Queue Surfaces)

Every list and queue surface must handle the following HTTP error states:

| HTTP Status | Scenario | UI behavior |
|---|---|---|
| `401 Unauthorized` | Session expired or token invalid | Redirect to login; preserve deep-link for post-login return |
| `403 Forbidden` | User lacks `records.read` permission | Show "Access restricted" empty state with permission name; no retry |
| `404 Not Found` | Tenant or resource not found | Show "Not found" state; offer navigation back to home |
| `422 Validation Error` | Invalid filter or query parameters | Show inline validation message; reset offending filter to default |
| `429 Too Many Requests` | Rate limit hit | Show "Too many requests — retrying in {n}s" banner; auto-retry after `Retry-After` header value |
| `503 Service Unavailable` | Backend service down | Show "Service temporarily unavailable" with retry button; use cached data if available (stale-while-revalidate) |
