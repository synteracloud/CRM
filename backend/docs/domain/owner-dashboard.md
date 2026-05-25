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

### 3.1 Execution Health Panel

Shows whether the team is executing correctly — not just activity volume.

| Metric | Source Read Model | Alert Threshold |
|---|---|---|
| Leads with no owner | `LeadOwnershipReadModel` | > 0 (always alert) |
| Leads idle > threshold | `LeadIdlenessReadModel` | > threshold per config |
| Open follow-ups overdue | `FollowUpStatusReadModel` | > 0 |
| Escalations not acknowledged | `EscalationReadModel` | > 0 |
| Deals with no activity in 7 days | `DealActivityReadModel` | Configurable |

### 3.2 Revenue Pipeline Panel

| Metric | Source Read Model |
|---|---|
| Total pipeline value (all stages) | `OpportunityPipelineReadModel` |
| Pipeline value by stage | `OpportunityPipelineReadModel` |
| Booked revenue this period | `RevenueReadModel` |
| Forecast (weighted by stage probability) | `ForecastReadModel` |
| Win rate (won / (won + lost)) | `KpiWinRateReadModel` |

### 3.3 Collections Panel

| Metric | Source Read Model |
|---|---|
| Total outstanding (PKR) | `InvoiceAgingReadModel` |
| Overdue 1–7 days | `InvoiceAgingReadModel` |
| Overdue 8–30 days | `InvoiceAgingReadModel` |
| Overdue 31–60 days | `InvoiceAgingReadModel` |
| Overdue 61+ days | `InvoiceAgingReadModel` |
| Cash collected this period | `CashCollectedReadModel` |
| DSO (days sales outstanding) | `DSOReadModel` |
| Payment reminders sent this week | `ReminderActivityReadModel` |

### 3.4 Employee Activity Panel

| Metric | Source Read Model |
|---|---|
| Activities logged per rep (today / this week) | `RepActivityReadModel` |
| Follow-ups completed vs assigned | `RepFollowUpReadModel` |
| Calls / messages initiated | `RepCommunicationReadModel` |
| Deals advanced this week | `RepDealProgressReadModel` |

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
