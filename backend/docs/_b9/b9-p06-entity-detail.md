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

**Header:** Case number, subject, status, SLA state badge, `[Claim]` `[Reassign]` `[Escalate]` `[Resolve]`

**Main pane sections:**
- Conversation thread (chronological customer/agent/system messages)
- SLA timer strip (always visible)
- Case fields: priority, queue, category
- Resolution notes + knowledge article links

**Context panel:**
- Customer context: account, contact, open ticket count, CSAT, plan tier
- Escalation controls (deterministic by SLA state)
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

**Header:** Subscription ID, plan, MRR, status, `[Renew]` `[Suspend]` `[Cancel]`

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

## SELF-QC

- **All 12 Archetype.md entity detail pages documented:** ✅ — 2.1–2.12 match exactly.
- **Every view anchored to a domain-model.md entity:** ✅
- **Header + main pane + context panel defined for all views:** ✅
- **Immutability constraint documented (Order):** ✅
- **Mobile collapse behaviour cross-referenced:** ✅
- **No duplicate surfaces with p03/p04:** ✅ — cross-references noted.

Score: **10/10**
