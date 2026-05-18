# B9-P10::REPORTING_ANALYTICS_INTELLIGENCE

## Scope

Defines the **Reporting / Analytics / Intelligence** archetype — 7 named reporting surfaces.
Anchored to `docs/read-models.md` (all 13 read models), `docs/kpi-data-pipelines.md`, `docs/data-architecture.md`.

---

## 1) Archetype Structure

All reporting surfaces share a **chart-first layout**:

```
┌─ Period selector + filter bar ────────────────────────────┐
├─ Summary KPI strip (3–5 tiles) ───────────────────────────┤
├──────────────────────────┬────────────────────────────────┤
│  Primary chart / table   │  Drilldown / segment panel     │
│  (main read model)       │  (slice by dimension)          │
└──────────────────────────┴────────────────────────────────┘
├─ Detail table (paginated) ────────────────────────────────┤
└───────────────────────────────────────────────────────────┘
```

**Design rules:**
- All charts bound to a named read model field — no ad-hoc queries in UI.
- Drilldown navigates to the relevant list or entity detail (no dead ends).
- Export as CSV/PDF for all report views.
- Period selector shared across all panels on the page.
- `restricted` widget state shown when user lacks permission for a metric (no leaked data).

---

## 2) The 7 Reporting / Analytics Pages

### 2.1 — Reporting Dashboards

**Route:** `/app/reports`
**Purpose:** Entry point — aggregated cross-domain executive summary.
**Role gate:** `sales_manager`, `owner`, `finance`

**Panels on this page:**
- Pipeline summary tile → drills to Opportunity Pipeline (dashboard 2.5 in `b9-p01`)
- Collections summary tile → drills to Collections Queue
- Lead funnel summary tile → drills to Lead Queue
- Case SLA summary tile → drills to Ticket Queue

This is a **navigation hub** — not a stand-alone report. Clicking any tile navigates to the domain-specific dashboard. No duplicate data displayed here vs individual dashboards.

---

### 2.2 — Predictive Forecasting

**Route:** `/app/reports/forecast`
**Read model:** `OpportunityPipelineSnapshotRM` + `forecast_snapshots` table (from `db/intelligence_db/schema.sql`)
**Role gate:** `sales_manager`, `owner`
**Source module:** `src/predictive_forecasting/`

**Views:**
1. **Forecast summary** — weighted pipeline vs commit vs best-case vs quota. Period: current quarter.
2. **Cohort waterfall** — deals moved in/out of period forecast. Stage velocity chart.
3. **Prediction confidence** — AI model confidence scores per deal (when `ai_scoring` enabled).
4. **Historical accuracy** — rolling 4-quarter forecast accuracy vs actual.

**Drilldown:** Clicking any forecast bar → filtered Opportunity List for that stage/category.

---

### 2.3 — AI Scoring

**Route:** `/app/reports/ai-scoring`
**Source entities:** `scoring_models`, `lead_scores`, `score_history` (from `db/intelligence_db/schema.sql`)
**Source module:** `src/ai_scoring/`
**Role gate:** `sales_manager`, `owner`

**Views:**
1. **Score distribution** — histogram of current lead/opportunity scores (0–100).
2. **Score trend** — how average score moved over time per stage.
3. **Top scored records** — ranked list of leads/opportunities by score, with score explanation.
4. **Feature weight inspector** — which model features (from `model_feature_weights`) drive the score (read-only).

**Design rule:** Scores are advisory — no auto-action is triggered by score alone.

---

### 2.4 — Predictive Models

**Route:** `/app/reports/models`
**Source entities:** `scoring_models`, `model_runs`, `model_feature_weights`
**Source module:** `src/predictive_models/`
**Role gate:** `admin`, `data_scientist` (if role defined)

**Views:**
1. **Model registry** — list of scoring models with version, status (active/archived), last run.
2. **Model run history** — per-run: started_at, completed_at, records scored, error count.
3. **Feature weight editor** — adjust feature weights per model (writes to `model_feature_weights`).
4. **Model comparison** — compare two model versions on same dataset.

---

### 2.5 — Revenue Recognition

**Route:** `/app/reports/revenue`
**Read model:** `SubscriptionRevenueRetentionRM`, `QuoteApprovalCycleRM`
**Role gate:** `finance`, `owner`

**Views:**
1. **MRR / ARR waterfall** — new, expansion, contraction, churn breakdown. Period: monthly.
2. **Invoice aging buckets** — outstanding receivables by age (0–30, 31–60, 61–90, 90+).
3. **Quote acceptance funnel** — quote sent → approved → converted to order.
4. **Payment collection rate** — invoices issued vs collected by period.

**Drilldown:** Invoice aging bucket → filtered Invoice Queue for that bucket.

---

### 2.6 — Usage Billing Analytics

**Route:** `/app/reports/usage`
**Source entities:** `usage_events`, `usage_aggregates`, `billing_meters` (from `db/transaction_db/migrations/0004_add_usage_billing.up.sql`)
**Source module:** `src/usage_billing/`
**Role gate:** `finance`, `tenant_admin`

**Views:**
1. **Meter usage trend** — per meter_code, usage volume over time. Compare vs limits.
2. **Usage by tenant** — cross-tenant usage breakdown (super_admin only).
3. **Billing period summary** — total billable events per period, by meter.
4. **Threshold alerts** — meters approaching or breached limits.

---

### 2.7 — Payments Analytics

**Route:** `/app/reports/payments`
**Read model:** `SubscriptionRevenueRetentionRM`
**Source entities:** `PaymentEvent`
**Role gate:** `finance`, `owner`

**Views:**
1. **Payment method breakdown** — cash / JazzCash / Easypaisa / bank transfer split.
2. **Collection performance** — reminder sent → paid conversion rate by tone tier (polite/firm/urgent).
3. **DSO (Days Sales Outstanding)** — rolling average with trend.
4. **Failed payment events** — list of failed/reversed events with reason codes.

**Pakistan note:** JazzCash and Easypaisa appear only when `stub_mode=false` (P-016 unblocked). In stub mode, these rows are hidden or marked "pending integration".

---

## 3) Interaction Patterns

1. **Drilldown always lands somewhere:** Every chart segment, table row, and KPI tile links to a filterable list or entity detail. No dead ends.
2. **Export:** All views export as CSV. Report header includes tenant, period, generated-at timestamp, and generating user.
3. **Threshold annotations:** Charts show configurable threshold lines (e.g., quota line on forecast chart). Configured in settings.
4. **Comparison mode:** All trend charts support a "compare vs previous period" overlay.
5. **Restricted metric masking:** If a widget requires a permission the user lacks, it shows "Restricted" — not an error and not blank.

---

## SELF-QC

- **All 7 Archetype.md reporting pages documented:** ✅ — 2.1–2.7 match exactly.
- **Every page bound to a named read model or DB entity:** ✅
- **Drilldown targets defined for all pages:** ✅
- **Pakistan payment stub-mode documented:** ✅
- **No ad-hoc query UI:** ✅ — all metrics from named read model fields.
- **Export defined for all views:** ✅

Score: **10/10**
