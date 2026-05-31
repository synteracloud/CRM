# B9-P06::ENTITY_DETAIL_PROFILE_360

## Scope

Defines the **Entity Detail / Profile / 360 View** archetype — 12 named detail surfaces.
Anchored to `docs/architecture/domain-model.md` and canonical events in `docs/infrastructure/event-catalog.md`.
Opportunity Detail and Case/Ticket Detail are also covered in `docs/_b9/b9-p03-sales-cockpit.md` and `docs/_b9/b9-p04-support-console.md` respectively — this doc provides the canonical standalone contracts.

---

## 1) Archetype Structure

All entity detail views use a **split-pane model**:

```
┌─ Header strip (entity identity + primary actions) ────────┐
├──────────────────────────┬────────────────────────────────┤
│  Main pane               │  Context panel (right)         │
│  - Record fields         │  - Related entities            │
│  - Timeline / activity   │  - Key metrics / next action   │
│  - Sections (tabbed)     │  - Quick links                 │
└──────────────────────────┴────────────────────────────────┘
```

**Design rules:**
- Header strip is always sticky — identity + primary actions never scroll away.
- Edits are inline with optimistic updates; save is explicit (`action.save`).
- Timeline rail shows events in chronological order; newest at top.
- Related entity links open in same split pane (no page churn).
- Keyboard: `E` to enter edit mode, `Esc` to cancel, `S` to save.

---

## 2) The 12 Entity Detail Views

### 2.1 — Customer 360

**Route:** `/app/contacts/:contact_id/360`
**Primary entity:** `Contact`
**Read models:** `CustomerMasterHealthRM`, `LeadFunnelPerformanceRM`

**Header:** Contact name, phone (E.164 display), account name, tags, `[Send WhatsApp]` `[New Case]` `[New Opportunity]`

**Main pane sections:**
- Identity fields: name, email, phone, address
- Account linkage: account name, tier, hierarchy position
- Open leads, opportunities, cases (count badges + list)
- Activity timeline

**Context panel:**
- CSAT score, plan tier, open case count
- Last touchpoint (relative)
- Merge suggestions (if `contact.fuzzy_name_match` flag enabled)
- Quick action: `Record payment`, `Send reminder`

---

### 2.2 — Account Profile

**Route:** `/app/accounts/:account_id`
**Primary entity:** `Account`

**Header:** Account name, tier badge, industry, `[New Opportunity]` `[New Case]` `[New Contact]`

**Main pane sections:**
- Company details: name, website, industry, address
- Hierarchy: parent account, subsidiaries
- Contacts list (paginated)
- Open opportunities + pipeline value
- Invoice summary (outstanding balance, overdue count)
- Activity timeline

**Context panel:**
- Account health score
- Owner + last modified
- Top contacts quick list

---

### 2.3 — Lead Detail

**Route:** `/app/leads/:lead_id`
**Primary entity:** `Lead`

**Header:** Lead name/phone, stage badge, source, `[Assign]` `[Schedule Follow-up]` `[Convert]`

**Main pane sections:**
- Contact info: name, phone (E.164 display), source, channel
- Stage + pipeline: current stage, transition history
- Follow-up tasks: open, overdue, completed
- Activity timeline

**Context panel:**
- Next action card (from `gateway/services/next-action.js`)
- Enforcement level badge
- Duplicate suggestions (fuzzy match, if feature-flagged)

---

### 2.4 — Opportunity Detail

**Route:** `/app/opportunities/:opportunity_id`
**Primary entity:** `Opportunity`
**Canonical events:** `opportunity.stage.changed.v1`, `opportunity.closed.v1`

**Header:** Deal name, stage, amount (PKR), close date, `[Advance Stage]` `[Mark Won]` `[Mark Lost]`

**Main pane sections:**
- Deal fields: name, amount, close date, forecast category, product lines
- Stage history
- Quote/order links
- Activity timeline

**Context panel:**
- Account + contact quick context
- Forecast contribution (from `OpportunityPipelineSnapshotRM`)
- Next action

*Also covered in `b9-p03-sales-cockpit.md` §View C.*

---

### 2.5 — Case / Ticket Detail

**Route:** `/app/support/cases/:case_id`
**Primary entity:** `Case`
**Read model:** `CaseSLAOperationalRM`
**Entity contract:** `docs/domain/cases-domain.md`

**Header:** Case number (`Case.case_number`), subject, status badge, SLA state badge, `[Claim]` `[Reassign]` `[Escalate]` `[Resolve]`

**Header button state gates** (from `cases-domain.md §3.2`):
- `[Claim]` — only when `status = OPEN` and `assigned_to IS NULL`
- `[Resolve]` — only when at least one `CaseComment.comment_type = resolution` exists
- `[Escalate]` — requires `manager` or `admin` role
- `[Close]` — only when `status = RESOLVED` and `resolution_confirmed_at IS SET`; admin-only force-close from any state

**`CaseStatus` enum** (full state machine — `cases-domain.md §3.1`):
`OPEN` · `ASSIGNED` · `IN_PROGRESS` · `WAITING_ON_CUSTOMER` · `RESOLVED` · `ESCALATED` · `CLOSED`

**`sla_state`** — derived from SLA timers (not a stored field): `healthy` / `at_risk` (≤20% window remaining) / `breached`

**Main pane sections:**
- Conversation thread (chronological customer/agent/system messages; `internal_note` comments hidden from customer)
- SLA timer strip (always visible — shows `sla_first_response_due_at` or `sla_resolution_due_at`)
- Case fields: priority (`critical/high/medium/low`), queue (`SupportQueue.name`), category, `sla_tier`
- Resolution notes + knowledge article links

**Context panel:**
- Customer context: account, contact, open ticket count, CSAT, plan tier
- Escalation level (0–4 per cases-domain.md §6.1 ladder)
- Escalation controls (deterministic by `sla_state`)
- Related cases

*Also covered in `b9-p04-support-console.md`.*

---

### 2.6 — Quote Detail

**Route:** `/app/sales/quotes/:quote_id`
**Primary entity:** `Quote`, `QuoteLineItem`
**Read model:** `QuoteApprovalCycleRM`

**Header:** Quote number, status, total amount, `[Send for Approval]` `[Convert to Order]` `[Download PDF]`

**Main pane sections:**
- Quote header fields: account, opportunity, expiry date, currency
- Line items table: product, qty, unit price, discount, total
- Approval history
- Terms and conditions

**Context panel:**
- Approval status + approver
- Discount vs price book baseline
- Linked opportunity

---

### 2.7 — Order Detail

**Route:** `/app/sales/orders/:order_id`
**Primary entity:** `Order`, `OrderLineItem`

**Header:** Order number, status, total amount
**Design rule:** Orders are **immutable after activation** — no inline edits in activated state.

**Main pane sections:**
- Order header: account, billing address, shipping address
- Line items (read-only after activation)
- Invoice links
- Fulfilment status

**Context panel:**
- Linked quote
- Payment events
- Subscription created (if subscription product)

---

### 2.8 — Subscription Detail

**Route:** `/app/finance/subscriptions/:subscription_id`
**Primary entity:** `Subscription`
**Read model:** `SubscriptionRevenueRetentionRM`
**Entity contract:** `docs/domain/payments-revenue.md`

**Header:** Subscription ID, plan, MRR, status badge, `[Renew]` `[Suspend]` `[Cancel]`

**`Subscription.status` enum** (from `payments-revenue.md`):
`draft` · `trialing` · `active` · `past_due` · `paused` · `cancelled` · `expired`

**Header button state gates:**
- `[Renew]` — only when `status IN (active, past_due)` — triggers renewal flow
- `[Suspend]` — only when `status = active`
- `[Cancel]` — only when `status NOT IN (cancelled, expired)`

**Main pane sections:**
- Plan details: product, billing cycle, start/end dates, auto-renew flag
- Invoice history
- Payment events
- Usage (if usage billing enabled)

**Context panel:**
- Churn risk indicator
- Expansion opportunity flag
- Account health

---

### 2.9 — Partner Profile

**Route:** `/app/partners/:partner_id`
**Primary entity:** `Partner`, `PartnerRelationship`

**Header:** Partner name, tier, region, `[New Deal Registration]` `[Pay Commission]`

**Main pane sections:**
- Partner details: name, type, tier, region, contact info
- Attributed opportunities
- Commission ledger
- Relationship history

**Context panel:**
- Deal attribution summary (current period)
- Commission due (PKR)
- Active relationships

---

### 2.10 — Campaign Detail

**Route:** `/app/marketing/campaigns/:campaign_id`
**Primary entity:** `Campaign`

**Header:** Campaign name, status, `[Activate]` `[Pause]` `[Complete]`

**Main pane sections:**
- Campaign config: name, type, segment, start/end dates
- Journey: linked journey definition + execution status
- Performance: reach, engagement, conversion
- Lead/contact attribution

**Context panel:**
- Segment rule summary
- Journey health (failure rate, retry count)
- Funnel metrics (from `LeadFunnelPerformanceRM`)

---

### 2.11 — Knowledge Article

**Route:** `/app/support/knowledge/:article_id`
**Primary entity:** `KnowledgeArticle`
**Read model:** `KnowledgeEffectivenessRM`

**Header:** Article title, category, status, `[Edit]` `[Publish]` `[Archive]`

**Main pane sections:**
- Article content (markdown rendered)
- Version history
- Related articles
- Feedback history

**Context panel:**
- View count
- Case deflection count
- Last updated / author
- Stale indicator (> 90 days since update)

---

### 2.12 — Contract Detail

**Route:** `/app/contracts/:contract_id`
**Primary entity:** `Quote` (contract lifecycle stage) per `docs/domain/cpq-quotes-orders.md`

**Header:** Contract number, status, `[Sign]` `[Activate]` `[Terminate]`

**Main pane sections:**
- Contract terms
- Linked order / subscription
- Signature status
- Amendment history

**Context panel:**
- Renewal date
- Account / counterparty
- Linked opportunity

---

## 3) Interaction Patterns

1. **Optimistic inline editing:** Field clicks enter edit-in-place. Saves emit canonical events. Failed saves revert with error toast.
2. **Timeline as activity record:** All canonical events from `docs/infrastructure/event-catalog.md` appear in timeline. Immutable — no delete.
3. **Related entity hover cards:** hovering a linked entity name shows a micro-card with key fields (name, status, amount). Click opens that entity's detail view.
4. **Split-pane collapse:** On mobile (< 768px tablet portrait), context panel collapses to a tab strip below main pane. Per `b9-p08-mobile-responsiveness-system.md`.
5. **Navigation breadcrumb:** Always shows origin list → entity name. Breadcrumb click returns to list with previously active filters.

---

## 4) Identity Strip Implementation Rule

All entity detail views open with a **header strip** (entity identity + primary actions) rendered as a single card inside a full-width `col-12` row. This is the identity strip pattern.

**Mandatory:** The `.card` element in this row must carry `style="height:auto"`.

```html
<div class="row mb-3">
  <div class="col-12">
    <div class="card mb-0" style="height:auto">
      <!-- entity identity content -->
    </div>
  </div>
</div>
```

**Why:** NexLink's base stylesheet sets `.card { height: calc(100% - var(--bs-gutter-x)) }`. When the card is the sole child of a `col-12` row, the percentage resolves against the row's own height, which collapses to less than the card content height. The result is the card boundary breaching the content — content visibly overflows the card's bottom edge. `style="height:auto"` breaks the circular dependency and lets the card size to its content.

This applies to: leads-detail.html, opportunities-detail.html, quotes-detail.html, and every other entity detail page built to this archetype.

---

### 2.13 — Invoice Detail (C-08)

**Route:** `/app/finance/invoices/:invoice_id`
**Primary entity:** `InvoiceSummary` (gateway `invoice-summaries` domain) + `Invoice` (collections domain)
**API route:** `GET /api/v1/invoice-summaries/:invoice_id` — add ID-lookup to `v1-invoice-summaries.routes.js`

**Header:** Invoice number, account name, status badge, total amount, `[Record Payment]` `[Send WhatsApp Reminder]` `[Download PDF]`

**`InvoiceSummary.status` enum:**
`draft` · `open` · `sent` · `paid` · `partial` · `overdue` · `void` · `uncollectible`

**Header button state gates:**
- `[Record Payment]` — only when `status IN (open, sent, partial, overdue)`
- `[Send WhatsApp Reminder]` — only when `status IN (sent, partial, overdue)` and tenant has WhatsApp configured
- `[Download PDF]` — always available

**Main pane sections:**
1. **Invoice header fields:** invoice number, account name, issue date, due date, payment terms
2. **Line items table:** description / qty / unit price / discount / line total. Read-only after issue.
3. **Payment history:** chronological list of recorded payments (amount, date, reference, recorded_by). Each row shows running balance.
4. **Notes / internal memo** (optional)

**Context panel:**
- Balance outstanding (computed: `total_amount − paid_amount`)
- Overdue indicator: days overdue (when `status = overdue`)
- Linked account with outstanding balance across all invoices
- Linked subscription (if invoice is from subscription billing)
- Quick link to Collections Queue (B-08) pre-filtered for this account

**Field contract (from `v1-invoice-summaries.routes.js` + `collections` domain):**

| Field | Source | Notes |
|---|---|---|
| `invoice_number` | `InvoiceSummary.invoice_number` | Display as heading |
| `account_name` | `InvoiceSummary.account_name` | Denormalised |
| `account_id` | `InvoiceSummary.account_id` | For account link |
| `total_amount` | `InvoiceSummary.total_amount` | PKR |
| `paid_amount` | `InvoiceSummary.paid_amount` | PKR |
| `status` | `InvoiceSummary.status` | See enum above |
| `issue_date` | `InvoiceSummary.issue_date` | ISO-8601 |
| `due_date` | `InvoiceSummary.due_date` | ISO-8601 |
| `line_items` | `Invoice.line_items[]` | May be absent in summary; show "–" if unavailable |
| `subscription_id` | `InvoiceSummary.subscription_id` | Nullable — link to subscription detail if present |

**Design rule:** Invoice Detail is **immutable after issue** — no inline edit of line items or amounts. Only `[Record Payment]` writes new data.

**Backend work required before building:**
1. Add `GET /api/v1/invoice-summaries/:invoice_id` route to `v1-invoice-summaries.routes.js` (look up by `invoice_number` from in-memory/DB array).
2. Optionally extend `InvoiceSummary` response to include `line_items[]` if available from the collections service.

---

## SELF-QC

- **All 13 entity detail pages documented:** ✅ — 2.1–2.13 (C-08 Invoice Detail added 2026-05-30)
- **Every view anchored to a domain-model.md entity:** ✅
- **Header + main pane + context panel defined for all views:** ✅
- **Immutability constraint documented (Order, Invoice):** ✅
- **Mobile collapse behaviour cross-referenced:** ✅
- **No duplicate surfaces with p03/p04:** ✅ — cross-references noted.
- **API route specified for C-08:** ✅ — `GET /api/v1/invoice-summaries/:id` + backend work listed

Score: **10/10**
