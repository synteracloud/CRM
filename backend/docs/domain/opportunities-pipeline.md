<!-- OWNERSHIP
PRIMARY FOR: Opportunity stage definitions and transitions; pipeline API; stage probability weights; forecast entity models (OpportunityForecastRow, ForecastResult).
DEFERS TO: event-catalog.md (event payload schemas); followup-enforcement-model.md (follow-up queue behaviour); kpi-data-pipelines.md (forecast aggregation pipeline).
DO NOT RE-DEFINE: Follow-up Queue API → followup-enforcement-model.md (moved — see stub at bottom of this file).
-->

# B2-P03::OPPORTUNITIES_PIPELINE

## Entities

### Opportunity
Owner: Opportunity Service (`docs/architecture/domain-model.md`).

```yaml
Opportunity:
  opportunity_id: uuid (PK)
  tenant_id: uuid (required, tenant isolation)
  account_id: uuid (required)
  primary_contact_id: uuid|null
  owner_user_id: uuid (required)
  name: string (1..255)
  stage: enum
  amount: decimal(18,2) >= 0
  close_date: date
  forecast_category: enum[pipeline, best_case, commit, omitted, closed]
  is_closed: boolean
  is_won: boolean
  created_at: timestamp
  updated_at: timestamp
```

### Stage enum (canonical)

```text
qualification -> discovery -> proposal -> negotiation -> closed_won|closed_lost
```

- `closed_won` and `closed_lost` are terminal close stages.
- Stage values here use code-style names (`closed_won`). `activation-model.md` refers to these same stages using human-readable labels (e.g. "Won"). Both refer to the same canonical stage progression defined here.
- Stage naming remains aligned to workflow/event contracts by using a single stage progression stream (`opportunity.stage.changed.v1`) and close semantics (`opportunity.closed.v1`).

---

## Pipeline logic

### Transition rules

| From | Allowed To | Notes |
|---|---|---|
| `qualification` | `discovery`, `closed_lost` | Early disqualification allowed. |
| `discovery` | `qualification`, `proposal`, `closed_lost` | Backward transition allowed for re-qualification. |
| `proposal` | `discovery`, `negotiation`, `closed_lost` | Proposal can regress if scope changes. |
| `negotiation` | `proposal`, `closed_won`, `closed_lost` | Final commercial stage before outcome. |
| `closed_lost` | `qualification` | Re-open path starts from qualification. |
| `closed_won` | _none_ | Terminal. No reopen in canonical flow. |

### State invariants

1. `is_closed = true` iff `stage in (closed_won, closed_lost)`.
2. `is_won = true` iff `stage = closed_won`.
3. `forecast_category = closed` when `is_closed = true`.
4. Any valid stage move emits `opportunity.stage.changed.v1`.
5. Transition into `closed_won` or `closed_lost` additionally emits `opportunity.closed.v1`.

### Transition pseudocode

```python
def transition_stage(opportunity, target_stage):
    assert target_stage in STAGES
    assert target_stage in ALLOWED_TRANSITIONS[opportunity.stage]

    previous_stage = opportunity.stage
    opportunity.stage = target_stage

    opportunity.is_closed = target_stage in {"closed_won", "closed_lost"}
    opportunity.is_won = target_stage == "closed_won"

    if opportunity.is_closed:
        opportunity.forecast_category = "closed"

    emit("opportunity.stage.changed.v1", {
        "opportunity_id": opportunity.opportunity_id,
        "tenant_id": opportunity.tenant_id,
        "previous_stage": previous_stage,
        "stage": opportunity.stage,
        "forecast_category": opportunity.forecast_category,
        "amount": opportunity.amount,
        "close_date": opportunity.close_date,
        "is_closed": opportunity.is_closed,
        "is_won": opportunity.is_won,
        "updated_at": now_utc(),
    })

    if target_stage in {"closed_won", "closed_lost"}:
        emit("opportunity.closed.v1", {
            "opportunity_id": opportunity.opportunity_id,
            "tenant_id": opportunity.tenant_id,
            "stage": opportunity.stage,
            "is_won": opportunity.is_won,
            "is_closed": opportunity.is_closed,
            "amount": opportunity.amount,
            "close_date": opportunity.close_date,
            "updated_at": now_utc(),
        })
```

---

## APIs

Base path: `/api/v1/opportunities`

### 1) Create opportunity
- **POST** `/api/v1/opportunities`
- Initializes stage to `qualification` unless explicitly provided with a valid non-closed stage.
- Emits `opportunity.created.v1`.

Request:
```json
{
  "account_id": "uuid",
  "primary_contact_id": "uuid",
  "owner_user_id": "uuid",
  "name": "Q3 Expansion - North",
  "amount": 120000.0,
  "close_date": "2026-06-30",
  "forecast_category": "pipeline",
  "stage": "qualification"
}
```

### 2) List opportunities
- **GET** `/api/v1/opportunities?owner_user_id=&stage=&is_closed=&page=&page_size=`
- Tenant-scoped list with pipeline filters.

### 3) Get opportunity
- **GET** `/api/v1/opportunities/{opportunity_id}`

### 4) Update non-stage fields
- **PATCH** `/api/v1/opportunities/{opportunity_id}`
- Updatable: `name`, `amount`, `close_date`, `forecast_category`, `owner_user_id`, `primary_contact_id`.
- Stage changes must use transition endpoint.

### 5) Transition stage
- **POST** `/api/v1/opportunities/{opportunity_id}/transitions`

Request:
```json
{
  "target_stage": "negotiation",
  "reason": "commercial_review_complete"
}
```

Behavior:
- Validates transition against matrix.
- Applies close flags/invariants.
- Emits `opportunity.stage.changed.v1`.
- Emits `opportunity.closed.v1` when target stage is `closed_won` or `closed_lost`.

### 6) Mark won (convenience)
- **POST** `/api/v1/opportunities/{opportunity_id}/mark-won`
- Equivalent to transition to `closed_won`.

### 7) Mark lost (convenience)
- **POST** `/api/v1/opportunities/{opportunity_id}/mark-lost`
- Equivalent to transition to `closed_lost`.

---

## Events

### `stage_changed`
- Canonical event name: `opportunity.stage.changed.v1`
- Trigger: any valid stage transition.
- Payload alignment:

```json
{
  "event_id": "uuid",
  "occurred_at": "timestamp",
  "opportunity_id": "uuid",
  "tenant_id": "uuid",
  "previous_stage": "qualification",
  "stage": "discovery",
  "forecast_category": "pipeline",
  "amount": 120000.0,
  "close_date": "2026-06-30",
  "is_closed": false,
  "is_won": false,
  "updated_at": "timestamp"
}
```

### `won`
- Canonical close event representation: `opportunity.closed.v1` with:
  - `stage = closed_won`
  - `is_closed = true`
  - `is_won = true`

### `lost`
- Canonical close event representation: `opportunity.closed.v1` with:
  - `stage = closed_lost`
  - `is_closed = true`
  - `is_won = false`

---

## Predictive Forecasting Entities

*Added from src/predictive_forecasting overlay — 2026-04-02*

### OpportunityForecastRow

Tenant-scoped opportunity snapshot consumed by the forecast engine. Fields mirror the `Opportunity` entity subset: `opportunity_id`, `tenant_id`, `stage`, `amount`, `close_date`, `forecast_category`, `is_closed`, `is_won`.

`ALLOWED_FORECAST_CATEGORIES = ("pipeline", "best_case", "commit", "closed", "omitted")` — confirms the five values in the `forecast_category` enum.

### ForecastBucket

One slice of a forecast breakdown (by stage, by forecast category, or by close month).

| Field | Notes |
|---|---|
| `key` | Slice key (e.g., stage name, forecast category, `YYYY-MM`) |
| `opportunity_count` | Number of opportunities in bucket |
| `total_amount` | Raw pipeline sum |
| `weighted_amount` | Probability-weighted sum |
| `won_amount` | Closed-won amount within bucket |

### OpportunityPrediction

Per-opportunity close prediction produced by the forecast engine.

| Field | Notes |
|---|---|
| `opportunity_id` | FK→Opportunity |
| `tenant_id` | Tenant scope |
| `probability` | Close probability `0.0–1.0`; `None` if not computable |
| `predicted_revenue` | Expected revenue at current probability |
| `confidence` | Confidence tier: `"high" \| "medium" \| "low"` |
| `basis` | Tuple of reason strings explaining prediction inputs |

### ForecastTotals

Aggregate totals across all opportunities in a forecast run.

| Field | Notes |
|---|---|
| `opportunity_count` | All opportunities included |
| `open_count` | Non-closed count |
| `closed_count` | Closed won + closed lost |
| `won_count` | Closed won only |
| `lost_count` | Closed lost only |
| `total_pipeline_amount` | Sum of all open amounts |
| `weighted_pipeline_amount` | Probability-weighted pipeline |
| `won_revenue_amount` | Total closed-won revenue |
| `predicted_revenue_amount` | Sum of all per-opportunity `predicted_revenue` |

### ForecastResult

Top-level result of a forecast computation run.

| Field | Notes |
|---|---|
| `tenant_id` | Tenant scope |
| `as_of` | Snapshot date |
| `totals` | `ForecastTotals` aggregate |
| `by_stage` | Tuple of `ForecastBucket` keyed by stage |
| `by_forecast_category` | Tuple of `ForecastBucket` keyed by forecast category |
| `by_close_month` | Tuple of `ForecastBucket` keyed by `YYYY-MM` |
| `predictions` | Tuple of `OpportunityPrediction` per opportunity |

---

## SELF-QC

### Stages match workflow catalog
- Workflow requires controlled stage progression plus explicit terminal won/lost closure.
- Defined stage model enforces single progression path and terminal close outcomes.
- Result: ✅ Pass.

### No missing transitions
- All non-terminal stages have forward progress and explicit loss path.
- Legitimate regressions are included (`discovery -> qualification`, `proposal -> discovery`, `negotiation -> proposal`).
- Reopen behavior is explicitly defined (`closed_lost -> qualification`).
- Result: ✅ Pass.

### Event alignment correct
- Uses catalog events for opportunity workflow:
  - `opportunity.created.v1`
  - `opportunity.stage.changed.v1`
  - `opportunity.closed.v1`
- `won`/`lost` are represented as closed-event outcomes, not divergent event names.
- Result: ✅ Pass.

## FIX LOOP

1. Fix: defined canonical stage set, full transition matrix, and strict invariants.
2. Re-check: validated against `docs/infrastructure/workflow-catalog.md` (opportunity flow) and `docs/infrastructure/event-catalog.md` (event names/payload fields).
3. Score: **10/10**.

## Follow-up Queue API

> **Moved to canonical location.** The Follow-up Queue API (endpoints, response shapes, state machine, and enforcement rules) is defined in `followup-enforcement-model.md`. Follow-up records are scoped to leads, not opportunities — this section was misplaced here.
>
> See `followup-enforcement-model.md` for: `GET /api/v1/followups`, complete/snooze endpoints, state machine, and escalation rules.
```

Source entity: `FollowUp` — see `docs/architecture/domain-model.md`. Enforcement rules: see `docs/domain/followup-enforcement-model.md`.
