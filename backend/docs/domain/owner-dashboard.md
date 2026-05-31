<!-- OWNERSHIP
PRIMARY FOR: Owner-role dashboard layout; KPI tile definitions; widget data sources for the owner view.
DEFERS TO: read-models.md (RM sources); kpi-data-pipelines.md (KPI formulas); ui-system.md (dashboard layout patterns); collections-engine-model.md (canonical aging buckets: 1–7/8–30/31–60/61+).
DO NOT RE-DEFINE: KPI formulas; RM schemas; UI component rules.
-->

# Owner Dashboard

## 1) Purpose

The Owner Dashboard is Domain Capability #6 from the system specification. It provides business owners with complete operational transparency across all revenue activities.

> **Design intent**: A business owner opening this dashboard must immediately see whether their team is executing, whether cash is moving, and whether there are any blocked items requiring attention — without drilling into individual records.

This is distinct from the Sales Cockpit (`b9-p03-sales-cockpit.md`), which is the rep-level execution surface. The Owner Dashboard is a cross-functional visibility layer for management.

---

## 2) Scope of Visibility

The Owner Dashboard aggregates across four operational domains:

| Domain | What the Owner Sees |
|---|---|
| **Leads** | Total leads, new leads today, leads with no follow-up scheduled, idle leads beyond threshold, conversion rate |
| **Deals** | Pipeline value by stage, deals at risk (idle/no activity), deal win rate, average time to close |
| **Revenue** | Booked revenue (this period vs last), cash collected, outstanding invoices by age bucket |
| **Collections** | Overdue invoices, DSO (days sales outstanding), reminders sent, escalations active |

---

## 3) Required Panels

**Read model alignment note (updated 2026-05-28):** This document was originally authored using non-canonical read model names. All panel read model references have been updated to use the canonical names from `read-models.md`. The original names (LeadOwnershipReadModel, InvoiceAgingReadModel, etc.) do not exist — they are replaced below with the canonical RM entries.

### 3.1 Execution Health Panel

Shows whether the team is executing correctly — not just activity volume.

| Metric | Canonical Read Model (read-models.md) | Alert Threshold |
|---|---|---|
| Leads with no owner / idle leads | `LeadFunnelPerformanceRM` — `avg_assignment_latency_hours`, `source_counts` | > 0 (always alert) |
| Open follow-ups overdue | `ActivityTaskOperationalRM` — `overdue_task_counts` | > 0 |
| Escalations not acknowledged | `ActivityTaskOperationalRM` — `no_next_action_gaps` | > 0 |
| Deals with no activity in 7 days | `OpportunityPipelineSnapshotRM` — `aging_buckets` | Configurable |

### 3.2 Revenue Pipeline Panel

| Metric | Canonical Read Model (read-models.md) |
|---|---|
| Total pipeline value (all stages) | `OpportunityPipelineSnapshotRM` — `total_pipeline_amount` (SalesDashboardReadModel shape) |
| Pipeline value by stage | `OpportunityPipelineSnapshotRM` — `stage_counts`, `weighted_pipeline_amount` |
| Booked revenue this period | `SubscriptionRevenueRetentionRM` — `monthly_trend.value` |
| Forecast (weighted by stage probability) | `OpportunityPipelineSnapshotRM` — `weighted_pipeline_amount` |
| Win rate (won / (won + lost)) | `OpportunityPipelineSnapshotRM` — computed from `won_opportunity_count` / `closed_opportunities` (see `kpi-data-pipelines.md §1.2`) |

### 3.3 Collections Panel

| Metric | Canonical Read Model (read-models.md) |
|---|---|
| Total outstanding (PKR) | `SubscriptionRevenueRetentionRM` — `delinquency_rates`, `collections_performance` |
| Overdue aging buckets (1–7 / 8–30 / 31–60 / 61+ days) | `SubscriptionRevenueRetentionRM` — collections component. Aging bucket definitions: 1–7 / 8–30 / 31–60 / 61+ days per `collections-engine-model.md` (canonical there). |
| Cash collected this period | `SubscriptionRevenueRetentionRM` — `monthly_trend` (collections component) |
| DSO (days sales outstanding) | Computed from `kpi-data-pipelines.md` formulas against Invoice + Payment events |
| Payment reminders sent this week | Direct from `Invoice.last_reminder_at` + `ReminderEvent` aggregate — not a named RM |

### 3.4 Employee Activity Panel

| Metric | Canonical Read Model (read-models.md) |
|---|---|
| Activities logged per rep (today / this week) | `EmployeePerformanceRM` — `P-06 Daily Activity Count` |
| Follow-ups completed vs assigned | `EmployeePerformanceRM` — `P-02 Follow-up Completion Rate` |
| Calls / messages initiated | `EmployeePerformanceRM` — `P-01 Leads Captured` + activity breakdown |
| Deals advanced this week | `EmployeePerformanceRM` — `P-05 Deals Won` + `OpportunityPipelineSnapshotRM` stage transitions |

See `employee-performance.md` for P-01 through P-08 KPI formula definitions.

This panel surfaces execution discipline at individual level. It is not a punitive tool but a signal for coaching.

---

## 4) Access Control

- Role: `Tenant Owner` or `Manager` (see [`identity-auth-rbac.md`](../security/identity-auth-rbac.md))
- Scope: tenant-scoped; no cross-tenant visibility
- Data: read-only; no actions can be triggered from the Owner Dashboard
- Employee activity data visible to Tenant Owner and Manager roles only

---

## 5) Data Freshness

| Panel | Update Frequency | Source |
|---|---|---|
| Execution Health | Near-real-time (event-driven, <30s lag) | Domain events → Read Models |
| Revenue Pipeline | Near-real-time | Domain events → Read Models |
| Collections | Near-real-time | Domain events → Read Models |
| Employee Activity | Near-real-time | Activity Timeline events → Read Models |
| KPI aggregates (win rate, DSO) | Every 15 minutes (batch aggregation) | KPI pipeline (see [`kpi-data-pipelines.md`](../infrastructure/kpi-data-pipelines.md)) |

All data is tenant-scoped and derived from canonical domain events only.

---

## 6) Execution Rules (Build Specification §6 Alignment)

The dashboard enforces the following mandatory execution conditions by surfacing violations prominently:

| Condition | How Surfaced |
|---|---|
| Every lead must have an owner | Alert count in Execution Health panel; red badge on ownerless lead count |
| Every lead must have a follow-up schedule | Idle lead count surfaced; leads with no follow-up highlighted |
| No lead can remain idle beyond threshold | Idle leads count with threshold exceeded shown in red |
| Deals cannot be closed without execution history | Surfaced as "deals at risk" — deal with no activity before close attempt |
| Every action must be logged | Activity count per rep; missing activity surfaced as gap |

---

## 7) Mobile Behavior

The Owner Dashboard must be fully functional on mobile (phone and tablet). Per the mobile responsiveness system:
- All 5 panels are accessible on mobile
- Top 3 most critical KPIs (leads idle, collections overdue, pipeline value) are visible above the fold
- No horizontal scroll
- Tap targets ≥ 44px

See [`b9-p08-mobile-responsiveness-system.md`](../_b9/b9-p08-mobile-responsiveness-system.md).

---

## 8) Related Documents

- [`read-models.md`](../ui/read-models.md) — read model definitions powering dashboard panels
- [`kpi-data-pipelines.md`](../infrastructure/kpi-data-pipelines.md) — KPI computation logic
- [`activity-control-model.md`](activity-control-model.md) — employee activity data source
- [`followup-enforcement-model.md`](followup-enforcement-model.md) — follow-up enforcement rules
- [`collections-engine-model.md`](collections-engine-model.md) — collections data source
- [`b9-p03-sales-cockpit.md`](../_b9/b9-p03-sales-cockpit.md) — rep-level execution surface (distinct from Owner Dashboard)
