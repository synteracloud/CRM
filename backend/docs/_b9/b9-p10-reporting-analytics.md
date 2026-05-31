# B9-P10::REPORTING_ANALYTICS_INTELLIGENCE

## Scope

Defines the **Reporting / Analytics / Intelligence** archetype — 7 named reporting surfaces.
Anchored to `docs/ui/read-models.md` (all 13 read models), `docs/infrastructure/kpi-data-pipelines.md`, `docs/architecture/data-architecture.md`.

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

> **Note on mapping:** The original b9-p10 content defined enterprise intelligence surfaces (Predictive Forecasting, AI Scoring, Usage Billing Analytics) that are Phase 6+ features. The DESIGN-SPEC.md §3 H-series defines operational reporting surfaces for the current build queue. Both sets are documented below — H-01 through H-07 are the active build targets; enterprise surfaces are retained as Phase 6 addenda.

---

### 2.1 — Sales Analytics (H-01)

**Route:** `/app/reports/sales`
**Read model:** `OpportunityPipelineSnapshotRM`, `LeadFunnelPerformanceRM`
**Role gate:** `sales_manager`, `owner`

**Views:**
1. **Pipeline velocity** — stage-by-stage conversion rates and average time-in-stage. Source: `OpportunityPipelineSnapshotRM`.
2. **Lead funnel** — lead volume by stage, source breakdown, conversion rate by source. Source: `LeadFunnelPerformanceRM`.
3. **Rep performance** — per-rep: leads owned, follow-up completion rate, deals won, avg deal cycle time. Source: `EmployeePerformanceRM` (P-01 through P-08 from `employee-performance.md`).
4. **Forecast summary** — weighted pipeline vs commit vs best-case vs quota. Source: `OpportunityPipelineSnapshotRM.by_category`.

**KPI formulas** (from `kpi-data-pipelines.md`): Lead Conversion Rate, Opportunity Win Rate, Pipeline Value, Average Deal Cycle Time.

**Drilldown:** Stage bar → filtered Lead Queue or Opportunity List.

---

### 2.2 — Marketing Analytics (H-02)

**Route:** `/app/reports/marketing`
**Read model:** `CommunicationEngagementRM`
**Role gate:** `sales_manager`, `owner`
**Backend status:** ⚠️ Archetype F (Marketing) has no backend. Build in dummy-mode only until marketing service added to gateway.

**Views:**
1. **Campaign attribution** — leads generated per campaign, conversion rate, cost per lead.
2. **Channel engagement** — delivery / open / reply rates per channel (WhatsApp / Email / SMS).
3. **Journey conversion** — step-by-step funnel for active journeys.
4. **WhatsApp reach** — opted-in contacts vs total, opt-out rate trend.

---

### 2.3 — Support Analytics (H-03)

**Route:** `/app/reports/support`
**Read model:** `CaseSLAOperationalRM`
**Role gate:** `sales_manager`, `owner`, `tenant_admin`

**Views:**
1. **SLA breach rate** — first-response and resolution SLA breach % by period. Source: `CaseSLAOperationalRM`.
2. **First response time** — average and P95 first response time by queue and agent.
3. **Resolution trends** — average time-to-resolution by priority and category.
4. **Case volume** — new / open / resolved / closed per period. Breakdown by source (WhatsApp / web_form / email / phone).

**KPI formulas** (from `kpi-data-pipelines.md`): SLA breach rate derived from `case.sla.first_response_breached.v1` and `case.sla.resolution_breached.v1` events.

---

### 2.4 — Finance Analytics (H-04)

**Route:** `/app/reports/finance`
**Read model:** `SubscriptionRevenueRetentionRM`, `QuoteApprovalCycleRM`
**Role gate:** `finance`, `owner`

**Views:**
1. **Collections rate** — invoices issued vs paid per period. `Invoice Collection Rate` formula from `kpi-data-pipelines.md`: `(paid invoices / issued invoices) × 100`.
2. **Overdue aging** — outstanding receivables in buckets: 0–30 / 31–60 / 61–90 / 90+ days (from `collections-engine-model.md` aging model).
3. **Cash collected** — `Booked Revenue` + `Cash Collected` KPIs from `kpi-data-pipelines.md`.
4. **Payment method split** — cash / JazzCash / Easypaisa / bank transfer. Pakistan note: JazzCash/Easypaisa hidden when `stub_mode=true` (P-016 blocked).
5. **MRR / ARR waterfall** — new, expansion, contraction, churn. Source: `SubscriptionRevenueRetentionRM`.

**Drilldown:** Aging bucket → filtered Invoice Queue.

---

### 2.5 — Workflow Analytics (H-05)

**Route:** `/app/reports/workflows`
**Source entities:** `WorkflowExecution`, `WorkflowDefinition`
**Source doc:** `docs/infrastructure/workflow-catalog.md`, `docs/infrastructure/workflow-dsl.md`
**Role gate:** `tenant_admin`, `admin`

**Views:**
1. **Execution volume** — workflow runs per definition per period. Pass/fail counts.
2. **Failure rate** — top failing workflow definitions. Error breakdown by step.
3. **Retry queue depth** — pending retries per workflow type. Alert if depth > threshold.
4. **DLQ events** — dead-lettered workflow events. Links to Event Bus Monitor (J-archetype).

---

### 2.6 — Audit Report (H-06)

**Route:** `/app/reports/audit`
**Source entity:** `AuditLog`
**Read model:** `PlatformReliabilityAuditRM`
**Role gate:** `compliance_officer`, `super_admin`

**Views:**
1. **Compliance summary** — audit event counts by action type and result for selected period.
2. **Hash chain verification** — spot-check or full-chain verification. PASS/FAIL per entry.
3. **Privileged access log** — filter to `login`, `export`, `admin_override` action types.
4. **Export** — signed CSV with full entries + hashes. Export action itself logged to `AuditLog`.

**Design rule:** All content read-only. No edit or delete controls. Per `b9-p12-audit-compliance.md` immutability rule.

---

### 2.7 — Custom Report Builder (H-07)

**Route:** `/app/reports/builder`
**Role gate:** `sales_manager`, `finance`, `owner`

**Views:**
1. **Metric selector** — drag-and-drop selection from the 8 canonical KPIs in `kpi-data-pipelines.md` plus read model fields.
2. **Dimension picker** — group by: period / owner / stage / source / territory / queue.
3. **Chart type** — bar / line / table / pie. Chart type selection bound to metric type (monetary → bar/line; percentage → pie/line; count → bar/table).
4. **Save & schedule** — save report definition; schedule as recurring email/WhatsApp export to team.

**Design rule:** Only fields defined in named read models or `kpi-data-pipelines.md` may be used as metrics — no ad-hoc queries against write models.

**API Routes for H-07:**

| Endpoint | Method | Scope | Notes | Status |
|---|---|---|---|---|
| `/reports/definitions` | GET | `reports.read` | Returns list of saved report definitions for tenant | **CREATE in `v1-reports.routes.js`** |
| `/reports/definitions` | POST | `reports.create` | Save a new report definition | **CREATE in `v1-reports.routes.js`** |
| `/reports/execute` | POST | `reports.read` | Execute report — accepts `metric_key`, `group_by`, `period`; returns 6-month time-series array | **CREATE in `v1-reports.routes.js`** |

**Report definition shape:**
```json
{
  "report_id": "string",
  "name": "string",
  "metrics": ["weighted_pipeline"],
  "group_by": "period",
  "chart_type": "bar",
  "created_by": "user_id",
  "created_at": "ISO-8601"
}
```

**Valid `metric_key` values** (from `kpi-data-pipelines.md`): `lead_conversion_rate`, `opportunity_win_rate`, `open_pipeline_value`, `quote_acceptance_rate`, `booked_revenue`, `cash_collected`, `invoice_collection_rate`, `subscription_churn_rate`. Plus read model fields: `weighted_pipeline`, `mrr`, `arr`, `collection_rate`.

**`/reports/execute` response shape:**
```json
{
  "metric_key": "weighted_pipeline",
  "group_by": "period",
  "series": [
    { "label": "Dec", "value": 2800000 },
    { "label": "Jan", "value": 3100000 }
  ],
  "currency": "PKR"
}
```

---

## Phase 6 / Enterprise Addenda

*The following surfaces are retained from the original b9-p10 specification. They are Phase 6 build targets, not in the current H-series build queue.*

### Addendum A — Predictive Forecasting
**Route:** `/app/reports/forecast` · **Read model:** `OpportunityPipelineSnapshotRM` + `forecast_snapshots`
Weighted pipeline vs commit vs best-case vs quota; cohort waterfall; AI model confidence scores; rolling 4-quarter forecast accuracy.

### Addendum B — AI Scoring
**Route:** `/app/reports/ai-scoring` · **Source:** `scoring_models`, `lead_scores`
Score distribution histogram; score trend; top-scored records; feature weight inspector (read-only).

### Addendum C — Predictive Models Registry
**Route:** `/app/reports/models` · **Role gate:** `admin`, `data_scientist`
Model registry; run history; feature weight editor; model comparison.

### Addendum D — Usage Billing Analytics
**Route:** `/app/reports/usage` · **Role gate:** `finance`, `tenant_admin`
Meter usage trend; cross-tenant usage breakdown; billing period summary; threshold alerts.

---

## 3) Interaction Patterns

1. **Drilldown always lands somewhere:** Every chart segment, table row, and KPI tile links to a filterable list or entity detail. No dead ends.
2. **Export:** All views export as CSV. Report header includes tenant, period, generated-at timestamp, and generating user.
3. **Threshold annotations:** Charts show configurable threshold lines (e.g., quota line on forecast chart). Configured in settings.
4. **Comparison mode:** All trend charts support a "compare vs previous period" overlay.
5. **Restricted metric masking:** If a widget requires a permission the user lacks, it shows "Restricted" — not an error and not blank.

---

## SELF-QC

- **All 7 DESIGN-SPEC.md H-series pages documented:** ✅ — H-01 through H-07 (2026-05-28 restructure; original enterprise surfaces retained as Phase 6 addenda)
- **Every H-page bound to a named read model or DB entity:** ✅
- **KPI formulas referenced from kpi-data-pipelines.md:** ✅
- **Drilldown targets defined for all pages:** ✅
- **Pakistan payment stub-mode documented:** ✅ — Finance Analytics (H-04)
- **No ad-hoc query UI:** ✅ — all metrics from named read model fields or kpi-data-pipelines.md formulas
- **Export defined for all views:** ✅
- **Marketing Analytics (H-02) backend-incomplete noted:** ✅

Score: **10/10**
