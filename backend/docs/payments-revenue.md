# B2-P08::PAYMENTS_REVENUE

## Entities

### Payment

- `payment_id (PK)`
- `tenant_id (FK->TenantRef)`
- `subscription_id (FK->Subscription, nullable)`
- `invoice_summary_id (FK->InvoiceSummary, nullable)`
- `external_payment_ref`
- `payment_method_type` (`card|bank_transfer|wallet|ach|other`)
- `amount`
- `currency`
- `status` (`initiated|authorized|captured|settled|failed|canceled|partially_refunded|refunded|chargeback`)
- lifecycle timestamps (`initiated_at`, `authorized_at`, etc.)
- `created_at`, `updated_at`

### PaymentStatusHistory

- immutable status transition records per payment:
  - `from_status`, `to_status`, `reason`, `changed_at`, `changed_by_user_id`

### RevenueLedger

- revenue delta entries linked to payment:
  - `entry_type` (`recognition|refund|chargeback_adjustment`)
  - `amount_delta`
  - `currency`
  - `recognized_at`

## APIs

- `GET /api/v1/payments`
- `POST /api/v1/payments`
- `POST /api/v1/payments/:payment_id/status`
- `GET /api/v1/payments/revenue/summary?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD`

## Status flow

- `initiated -> authorized | failed | canceled`
- `authorized -> captured | failed | canceled`
- `captured -> settled | partially_refunded | refunded | chargeback`
- `settled -> partially_refunded | refunded | chargeback`
- `partially_refunded -> refunded | chargeback`
- terminal: `failed`, `canceled`, `refunded`, `chargeback`

Transition enforcement:

- DB helper: `is_valid_payment_status_transition`
- DB mutator: `apply_payment_status_transition`
- API guard in `v1-payments.routes.js`

**Invalid transition error response:**
```json
{
  "error": "INVALID_STATE_TRANSITION",
  "message": "Payment cannot transition from '{current_status}' to '{requested_status}'",
  "current_status": "<current>",
  "requested_status": "<requested>",
  "allowed_transitions": ["<list of valid next states>"],
  "meta": { "request_id": "req_..." }
}
```
HTTP status: `409 Conflict`.

## Revenue tracking behavior

- On `settled`, add positive recognition entry.
- On `partially_refunded`/`refunded`, add negative refund entry.
- On `chargeback`, add negative chargeback adjustment entry.

---

## Subscription Lifecycle

*Added from src/subscription_billing overlay — 2026-04-02*

### Subscription Status States

`draft → trialing → active → past_due → paused → canceled | expired`

| Status | Meaning |
|---|---|
| `draft` | Created but not yet activated |
| `trialing` | Free trial period active |
| `active` | Paid and current |
| `past_due` | Payment failed; grace period active |
| `paused` | Voluntarily paused; not billed |
| `canceled` | Terminated by customer or admin |
| `expired` | End date passed without renewal |

### PlanChange Entity

Records upgrade/downgrade requests with proration control.

| Field | Notes |
|---|---|
| `plan_change_id` | PK |
| `subscription_id` | FK→Subscription |
| `from_plan_code` | Previous plan |
| `to_plan_code` | Target plan |
| `change_kind` | `upgrade \| downgrade` |
| `requested_at` | When change was requested |
| `effective_at` | When change takes effect |
| `apply_on_renewal` | If true, change waits until next renewal cycle |

**Plan change cancellation rules:**

- If `apply_on_renewal = false` and `effective_at` has not yet passed: plan change can be cancelled via `DELETE /api/v1/subscriptions/{id}/plan-changes/{plan_change_id}`. Cancellation emits `subscription.plan_change.cancelled.v1`.
- If `apply_on_renewal = true` and the renewal cycle has not begun: plan change can be cancelled via the same endpoint.
- If `effective_at` has already passed or renewal cycle has begun: plan change cannot be cancelled — a reverse change request must be submitted.
- If the subscription is cancelled before the plan change takes effect: the plan change is automatically voided. No proration is applied for the unrealized change.

### RecurringInvoiceHook

Scheduled triggers for automatic invoice generation events.

| Field | Notes |
|---|---|
| `trigger_type` | `activation \| renewal \| plan_change` |
| `invoice_reason` | `initial \| recurring \| proration` |
| `run_at` | Scheduled execution time |

---

## Revenue Recognition

*Added from src/revenue_recognition overlay — 2026-04-02*

Revenue is recognised on a **deterministic schedule** — not on cash receipt. Revenue is earned over the service period, not when invoiced or collected.

### Recognition Rule

Defines how revenue for a contract is distributed over time.

| Field | Notes |
|---|---|
| `contract_id` | Links to Order/Subscription |
| `revenue_type` | `one_time \| recurring` |
| `amount` | Total contract value |
| `service_period_start/end` | When service is delivered |
| `recognized_at` | Set when fully recognised; null = in-progress |

### Billing Event Types

`invoice_posted \| payment_settled \| payment_refunded \| chargeback`

### Revenue Schedule

Generated from recognition rules — a set of `RevenueScheduleLine` entries, one per recognition date, each with `amount`, `currency`, `revenue_type`, and `trace_event_ids` (audit trail).

### Revenue Position

Point-in-time snapshot for a contract as of a given date:

| Field | Meaning |
|---|---|
| `billed_amount` | Total invoiced to date |
| `collected_amount` | Total cash received |
| `earned_amount` | Revenue earned through service delivery |
| `deferred_amount` | Billed but not yet earned (liability) |
| `scheduled_through_as_of` | Revenue scheduled up to as-of date |

**Rule:** `earned + deferred = billed` at any point in time.

---

## Usage Billing

*Added from src/usage_billing overlay — 2026-04-02*

Usage billing meters platform events into billable quantities and rates them against a customer's plan.

### Tracked Billable Events

| Event name | What it meters |
|---|---|
| `communication.message.sent.v1` | Outbound messages |
| `communication.message.engagement.updated.v1` | Message opens/clicks |
| `workflow.execution.completed.v1` | Workflow runs |
| `notification.dispatched.v1` | Notifications sent |
| `search.document.upserted.v1` | Search index writes |
| `job.succeeded.v1` | Background job completions |

### Usage Billing Flow

```
Platform event emitted
    ↓
BillableEventRule matches event_name → meter_code + quantity_field
    ↓
UsageRecord created (dedupe_key prevents double-counting)
    ↓
UsageAggregate built per meter/period
    ↓
MeterRateCard applied (flat or tiered pricing)
    ↓
RatedUsageLine generated
    ↓
InvoiceInput assembled → sent to subscription billing
```

### MeterRateCard

| Field | Notes |
|---|---|
| `meter_code` | Unique meter identifier |
| `billing_model` | `flat \| tiered \| volume` |
| `unit_price` | Used for flat billing |
| `tiers` | `TierPrice[]` — `up_to` (null = infinity) + `unit_price` per tier |

**Billing model semantics:**

| Model | Calculation |
|---|---|
| `flat` | `unit_price × total_units` |
| `tiered` (graduated) | Each tier applies only to units within that tier's range. Example: tiers `[0-500 @ $0.01, 501-1000 @ $0.005]` for 700 units = `(500 × $0.01) + (200 × $0.005) = $6.00` |
| `volume` | All units priced at the rate of the highest reached tier. Example: same tiers for 700 units = `700 × $0.005 = $3.50` |

Tier `up_to: null` means "infinity" (catch-all final tier). Tiers are non-overlapping and must cover all quantity ranges without gaps.

### DB schema needed

`db/transaction_db/` extension — tables: `usage_events`, `usage_aggregates`, `billing_meters`, `meter_rate_cards`, `recognition_rules`, `revenue_schedule_lines` (pending P-030)
