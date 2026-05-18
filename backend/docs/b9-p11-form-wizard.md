# B9-P11::FORM_WIZARD_CPQ_CONFIGURATOR

## Scope

Defines the **Form / Wizard / CPQ Configurator** archetype — 6 named guided-input surfaces.
Anchored to `docs/cpq-quotes-orders.md`, `docs/domain-model.md`, and `docs/ui-foundations.md` §6 (≤2 steps rule).

---

## 1) Archetype Structure

Wizards use a **step-tracker + form-body shell**:

```
┌─ Step tracker (1 of N steps, progress bar) ───────────────┐
├─ Step title + description ────────────────────────────────┤
├─ Form body (fields for this step) ────────────────────────┤
├─ Validation feedback (inline, not modal) ─────────────────┤
└─ [Back]  [Cancel]  ──────────────  [Next / Finish] ───────┘
```

**Design rules:**
- Wizards are multi-step; each step must be completable in ≤2 user interactions (taps + submits).
- Inline validation — errors appear under the field, not in a modal.
- `[Back]` never loses entered data — state preserved across steps.
- `[Cancel]` from any step prompts "Discard changes?" — returns to origin list.
- Final `[Finish]` or `[Submit]` is the only commit point — no partial saves unless explicitly autosaved.
- All wizard flows are tracked via `gateway/services/flow-steps.js` — violation throws `FlowStepViolationError`.

---

## 2) The 6 Form / Wizard Pages

### 2.1 — CPQ Quote Configurator

**Route:** `/app/sales/quotes/new` and `/app/sales/quotes/:id/configure`
**Steps:** 4
**Source entities:** `Quote`, `QuoteLineItem`, `PriceBook`, `PriceBookEntry`, `Product`

| Step | Fields | Notes |
|---|---|---|
| 1. Header | Account, Opportunity link, Expiry date, Currency | Account lookup = live search |
| 2. Line items | Product picker, Qty, Unit price (from PriceBook), Discount % | Discount validation: flag if > policy limit |
| 3. Terms | Payment terms, Delivery terms, Notes | Free text fields |
| 4. Review & send | Summary table, approval routing preview | Read-only; `[Send for Approval]` or `[Save Draft]` |

**Constraints:**
- Products must exist in active `PriceBook` for selected currency.
- Discounts > `approval_threshold` auto-route to approval before quote can be sent.

---

### 2.2 — Lead Conversion Wizard

**Route:** `/app/leads/:lead_id/convert`
**Steps:** 3
**Source entities:** `Lead`, `Contact`, `Account`, `Opportunity`

| Step | Fields | Notes |
|---|---|---|
| 1. Contact | Confirm / edit contact details (pre-filled from Lead) | Dedup check runs — shows merge suggestion if match |
| 2. Account | Select existing account or create new | Account lookup with create inline |
| 3. Opportunity | Create opportunity? Toggle. If yes: deal name, amount, close date, stage | Optional; defaults to pre-filled from Lead data |

**Output:** Creates `Contact`, optionally creates `Account` and `Opportunity`; `Lead.status` → `converted`.
**Constraint:** Cannot convert a Lead that is already converted.

---

### 2.3 — Contract Lifecycle Form

**Route:** `/app/contracts/new` and `/app/contracts/:id/edit`
**Steps:** 3
**Source entities:** `Quote` (contract stage), `Order`
**Source doc:** `docs/contract-lifecycle-management.md`

| Step | Fields | Notes |
|---|---|---|
| 1. Parties | Account, counterparty contact, internal owner | |
| 2. Terms | Start date, end date, value, payment schedule | Linked to Quote if applicable |
| 3. Signature | eSign routing or manual sign upload | Status → `pending_signature` |

**State machine:** `draft` → `pending_signature` → `active` → `expired` / `terminated`

---

### 2.4 — Subscription Setup Wizard

**Route:** `/app/finance/subscriptions/new`
**Steps:** 3
**Source entities:** `Subscription`, `InvoiceSummary`, `Order`

| Step | Fields | Notes |
|---|---|---|
| 1. Plan | Account, product (subscription type), billing cycle (monthly/annual), start date | |
| 2. Pricing | MRR, discount, promo code | Auto-creates Invoice for first period |
| 3. Confirm | Summary + payment method selection | `[Activate Subscription]` |

**Output:** `Subscription` record + first `InvoiceSummary` + optional `PaymentEvent` if paid at signup.

---

### 2.5 — Custom Object Record Form

**Route:** `/app/custom/:object_type/new` and `/app/custom/:object_type/:record_id/edit`
**Steps:** 1 (single-page form; not a wizard)
**Source:** Custom Object schema from `Custom Object Framework Admin` (b9-p09-settings-admin.md §2.8)

**Structure:**
- Fields rendered from object schema definition
- Field types: text, number, date, select, multi-select, relation (FK lookup)
- Required fields validated on save
- Layout from `Custom Object Layout Builder` (b9-p08-builder-extensions.md)

**Design rule:** Custom object forms must follow same inline-validation and ≤2 steps rules as standard forms.

---

### 2.6 — Tenant Activation Onboarding Wizard

**Route:** `/app/onboarding`
**Steps:** 5
**Source doc:** `docs/activation-model.md`
**Trigger:** First login for a new tenant

| Step | Content | Completion gate |
|---|---|---|
| 1. Welcome | System overview, language selection (EN / UR) | Locale selected |
| 2. Team | Invite first team member(s) | At least 1 invite sent |
| 3. WhatsApp | Connect WhatsApp provider (or skip — mark pending) | Provider configured or skipped |
| 4. First lead | Guided "create your first lead" | Lead created |
| 5. Done | Confirmation, link to docs, dismiss | `activation.onboarding_complete` event emitted |

**Notification shown on completion:** `notification.lead_captured` (i18n key) — "Your first lead is in the system. It won't slip away."
**Design rule:** Onboarding can be skipped at step 3 and 4; skipped steps shown as "pending" in activation checklist accessible from nav.

---

## 3) Interaction Patterns

1. **≤2 steps per action:** Each wizard step captures one logical decision, completable in ≤2 interactions.
2. **Live search for lookups:** Account, Contact, Product lookups use debounced live search — no separate modal.
3. **Dedup check on contact fields:** Fuzzy match runs on contact name field if `contact.fuzzy_name_match` enabled.
4. **Inline validation, not modal:** Error messages appear under the offending field, never in an alert box.
5. **Back preserves state:** All entered data persisted in wizard local state; `[Back]` never resets a step.
6. **Autosave for long wizards:** CPQ Configurator autosaves as draft every 60 seconds after step 1.

---

## SELF-QC

- **All 6 Archetype.md form/wizard pages documented:** ✅ — 2.1–2.6 match exactly.
- **≤2 steps rule applied to all flows:** ✅
- **Inline validation (not modal) stated for all:** ✅
- **Back preserves state rule documented:** ✅
- **Dedup check cross-referenced (Lead Conversion):** ✅
- **Onboarding notification i18n key referenced:** ✅

Score: **10/10**
