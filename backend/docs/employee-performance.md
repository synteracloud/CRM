# Employee Performance Indicators Spec

## Purpose

This document defines per-employee performance KPI aggregation: which metrics constitute "performance indicators," how they are aggregated from raw activity events, the `EmployeePerformanceRM` read-model schema, refresh frequency, and RBAC visibility rules. The `activity-control-model.md` defines the raw event log; `owner-dashboard.md` defines the aggregate owner view. This doc fills the per-rep layer between those two.

---

## 1) Performance KPI Definitions

### 1.1 KPI Catalog

| KPI | Name | Formula | Source events |
|---|---|---|---|
| P-01 | Leads Captured | COUNT(leads WHERE assigned_rep_id = rep AND created_at WITHIN period) | `lead.created` |
| P-02 | Follow-up Completion Rate | COUNT(tasks completed on time) / COUNT(tasks assigned to rep) × 100 | `followup.completed`, `followup.created` |
| P-03 | Average First Response Time | AVG(first_responded_at - created_at) for leads owned by rep WHERE first_responded_at IS NOT NULL | `activity.logged` (type=call/message) vs `lead.created` |
| P-04 | Lead Conversion Rate | COUNT(leads converted to opportunity) / COUNT(leads assigned) × 100 | `lead.converted`, `lead.created` |
| P-05 | Deals Closed (Won) | COUNT(opportunities WHERE stage=WON AND closed_by=rep AND closed_at WITHIN period) | `opportunity.won` |
| P-06 | Daily Activity Count | COUNT(ActivityEvent WHERE actor_id=rep AND created_at WITHIN TODAY) | `activity.logged` (all types) |
| P-07 | Overdue Follow-up Count | COUNT(FollowupTask WHERE assigned_to=rep AND status=OVERDUE AND tenant_id=tenant) | `followup.overdue` |
| P-08 | Average Deal Cycle Time | AVG(opportunity.closed_at - opportunity.created_at) for rep's won deals in period | `opportunity.won`, `opportunity.created` |

### 1.2 KPI Periods

All KPIs are calculated for the following time windows:
- **Today** (00:00 PKT to now)
- **This week** (Monday 00:00 PKT to now)
- **This month** (1st of month 00:00 PKT to now)
- **Rolling 30 days** (now - 30 days to now)

P-02 (Completion Rate) and P-04 (Conversion Rate) use rolling 30-day as the primary period for meaningful sample size. Daily counts (P-01, P-06) primarily use Today.

---

## 2) Read Model Schema

### 2.1 EmployeePerformanceRM

```
EmployeePerformanceRM
├── rm_id                : UUID (PK)
├── tenant_id            : str (required)
├── rep_id               : UUID (FK → User)
├── period_type          : PeriodType enum (today | week | month | rolling_30)
├── period_start         : date
├── period_end           : date
├── leads_captured       : int (P-01)
├── followup_completion_rate : float (P-02 — 0.0 to 1.0)
├── avg_first_response_hours : float (P-03 — hours; null if no leads responded to)
├── lead_conversion_rate : float (P-04 — 0.0 to 1.0)
├── deals_won            : int (P-05)
├── daily_activity_count : int (P-06 — only meaningful for period_type=today)
├── overdue_followups    : int (P-07 — current count, not period-based)
├── avg_deal_cycle_days  : float (P-08 — null if no won deals)
├── computed_at          : datetime
└── is_current           : bool (true for the most recent computation for this rep+period_type)
```

**Partial unique index:** `UNIQUE (tenant_id, rep_id, period_type, period_start) WHERE is_current = true`. On recompute, the previous record is updated to `is_current = false` and a new record inserted.

### 2.2 EmployeePerformanceSummary (API response shape)

The API aggregates the four period rows into a single response:

```json
{
  "rep_id": "uuid",
  "rep_name": "string",
  "rep_avatar_url": "string | null",
  "today": { "leads_captured": 3, "daily_activity_count": 12, "overdue_followups": 1 },
  "this_week": { "leads_captured": 14, "deals_won": 2 },
  "this_month": { "leads_captured": 42, "deals_won": 8, "followup_completion_rate": 0.87 },
  "rolling_30": {
    "lead_conversion_rate": 0.34,
    "avg_first_response_hours": 1.8,
    "avg_deal_cycle_days": 12.4,
    "followup_completion_rate": 0.91
  },
  "computed_at": "ISO 8601 datetime"
}
```

---

## 3) Aggregation Source Rules

### 3.1 Event Sources

All KPI computation reads from:
1. **`ActivityEvent` table** — raw immutable event log; `actor_id` = the rep performing the action.
2. **`Lead` table** — `assigned_rep_id`, `created_at`, `stage`, `converted_at`.
3. **`FollowupTask` table** — `assigned_to`, `status`, `due_at`, `completed_at`.
4. **`Opportunity` table** — `owner_id`, `stage`, `created_at`, `closed_at`.

### 3.2 Aggregation Rules

**P-01 (Leads Captured):**
- Source: `Lead WHERE created_by = rep_id` (not `assigned_rep_id` — captures leads the rep created/captured, not just assigned to them)
- Fallback: if `created_by` is a system user (auto-capture from WhatsApp), check `assigned_rep_id` instead.

**P-02 (Follow-up Completion Rate):**
- Numerator: `FollowupTask WHERE assigned_to = rep AND status = COMPLETED AND completed_at <= due_at` (on-time completions only)
- Denominator: `FollowupTask WHERE assigned_to = rep AND created_at WITHIN period AND status IN (COMPLETED, OVERDUE, FAILED)`
- Excludes tasks still in PENDING (not yet due).

**P-03 (Average First Response Time):**
- For each lead created by WhatsApp inbound (`Lead.source = whatsapp_inbound`) in the period, where the rep is `assigned_rep_id`:
- First response = first `ActivityEvent WHERE entity_ref = lead AND activity_type IN (call, message_sent, visit) AND actor_id = rep`
- Response time = `ActivityEvent.created_at - Lead.created_at` in hours.
- Average across all such leads in the period.

**P-06 (Daily Activity Count):**
- `COUNT(ActivityEvent WHERE actor_id = rep AND created_at >= today_start AND activity_type NOT IN (login, logout, view))`
- Excludes passive events (viewing records). Counts only productive actions: call, message_sent, visit, note_added, task_completed, deal_updated.

### 3.3 Anomaly Handling

- If `followup_completion_rate` denominator = 0: store `null` (not 0.0 — division by zero is not a zero rate).
- If `avg_first_response_hours` sample count < 3: store result but tag with `low_sample_warning = true` in the metadata field.
- If an ActivityEvent has no matching lead (orphaned event): skip from P-03 calculation.

---

## 4) Refresh Frequency

| Period type | Refresh schedule | Notes |
|---|---|---|
| `today` | Every 15 minutes during business hours (09:00–21:00 PKT) | Real-time-ish; frequent refresh for "today" dashboard view |
| `week` | Every 2 hours | Sufficient for weekly tracking |
| `month` | Every 4 hours | Sufficient for monthly tracking |
| `rolling_30` | Once daily at 01:00 PKT | Heavier computation; daily is sufficient |

Refresh is idempotent: the aggregation job queries from the source tables and writes the result to `EmployeePerformanceRM`. It does not accumulate incrementally — it recomputes from scratch each time. This keeps the aggregation simple and correct even after data corrections.

---

## 5) RBAC Visibility Rules

| Role | Visible data |
|---|---|
| `sales_rep` | Own performance data only (`rep_id = current_user.id`). Cannot see other reps' data. |
| `manager` | All reps in their teams (teams where user is `primary_manager` or has `manager` role). |
| `admin` | All reps in the tenant. |

**Enforcement:** Enforced at the service layer in `GET /api/v1/performance/employees`. The query is filtered by `rep_id` for `sales_rep` role, by `team_membership` for `manager` role, and unrestricted for `admin`.

**Dashboard drill-down:** Owner dashboard (`A-01 dashboard.html`) shows a team performance summary table. Clicking a rep row opens their individual performance page. This navigation is only available to `manager` and `admin` roles.

---

## 6) API Endpoints

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/performance/employees` | JWT | `manager`, `admin` | List all reps' performance summaries for the tenant (current period). |
| `GET` | `/api/v1/performance/employees/{rep_id}` | JWT | `sales_rep` (own), `manager`, `admin` | Single rep's full performance data across all periods. |
| `GET` | `/api/v1/performance/employees/me` | JWT | Any authenticated | Alias for current user's own performance data. |
| `GET` | `/api/v1/performance/teams/{team_id}` | JWT | `manager`, `admin` | Aggregate performance summary for a team (avg/total across reps). |

---

## 7) Events Emitted

| Event | Trigger |
|---|---|
| `performance.computed` | Aggregation job completes a refresh cycle. Includes `rep_count`, `period_type`, `tenant_id`. |
| `performance.overdue_threshold_exceeded` | Rep's `overdue_followups` > configurable threshold (default: 5). Alert emitted for manager. |

---

## 8) Implementation Acceptance Checklist

- [ ] `EmployeePerformanceRM` table created with all KPI fields and partial unique index.
- [ ] All 8 KPI formulas implemented as documented in §1.1.
- [ ] `today` refresh job runs every 15 minutes (business hours); `week` every 2 hours; `month` every 4 hours; `rolling_30` daily.
- [ ] Null handling: division-by-zero returns null, not 0.0.
- [ ] Low sample warning tag for P-03 when sample < 3.
- [ ] API enforces RBAC: `sales_rep` sees own data only; `manager` sees team data; `admin` sees all.
- [ ] `GET /api/v1/performance/employees/me` works for any authenticated user.
- [ ] `performance.overdue_threshold_exceeded` event emitted when rep overdue count > 5.
- [ ] All KPI computations use PKT timezone (UTC+5) for day/week/month boundaries.
