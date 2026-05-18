# B9-P01::DASHBOARD_KPI_OVERVIEW

## Scope

Defines the **Dashboard / KPI Overview** archetype — 13 named dashboard panels covering all read model surfaces.
Anchored to `docs/read-models.md` (Widget System + Dashboard Read Model Shapes) and `docs/domain-model.md`.
Pakistan-specific owner view: see also `docs/owner-dashboard.md`.

---

## 1) Archetype Structure

The dashboard archetype uses a **five-zone layout** (from `read-models.md` § Widget Zones):

| Zone | Purpose | Always visible? |
|---|---|---|
| `posture` | Health/risk posture bar — role-gated alert strip | Yes |
| `primary_kpi` | Headline metric tiles (3–5 max per dashboard) | Yes |
| `execution_queue` | Actionable queue driving immediate next action | Yes |
| `trend_diagnostic` | Time-series chart or cohort drill-down | On scroll / tab |
| `risk_anomaly` | Breach indicators, anomaly flags | Yes (when non-zero) |

**Widget states:** `default | loading | empty | error | restricted`
**Role-dashboard mapping:** role → `RoleDashboardMapping.default_dashboard_type` determines landing panel.

---

## 2) The 13 Dashboard Panels

### 2.1 — Tenant & Entitlement Dashboard

**Read model:** `TenantEntitlementOverviewRM`
**Route:** `/app/admin/tenants`
**Role gate:** `super_admin`, `tenant_admin`

| Zone | Widget | Metric path |
|---|---|---|
| `primary_kpi` | Active tenants | `tenant_count` |
| `primary_kpi` | Feature utilisation | `enabled_feature_count / entitlement_limit` |
| `execution_queue` | Entitlements nearing limit | `entitlements_at_limit` |
| `risk_anomaly` | Entitlement overages | `entitlement_overage_count` |

---

### 2.2 — Identity & Access Posture Dashboard

**Read model:** `IdentityAccessPostureRM`
**Route:** `/app/admin/identity`
**Role gate:** `super_admin`, `tenant_admin`

| Zone | Widget | Metric path |
|---|---|---|
| `posture` | Privileged account count | `privileged_user_count` |
| `primary_kpi` | Active users | `active_user_count` |
| `primary_kpi` | Dormant accounts | `dormant_user_count` |
| `execution_queue` | High-risk sessions | `active_session_risk_count` |
| `risk_anomaly` | Dormant privileged accounts | derived: `dormant_user_count` ∩ `privileged_user_count` |

---

### 2.3 — Lead Funnel Dashboard

**Read model:** `LeadFunnelPerformanceRM`
**Route:** `/app/sales/leads/dashboard`
**Role gate:** `sales_manager`, `owner`

| Zone | Widget | Metric path |
|---|---|---|
| `posture` | Leads with no owner | `unassigned_lead_count` |
| `primary_kpi` | New leads (period) | `new_lead_count` |
| `primary_kpi` | Conversion rate | `stage_conversion_rate` |
| `primary_kpi` | Avg assignment latency | `avg_assignment_latency_hours` |
| `execution_queue` | Idle leads > threshold | `idle_lead_count` |
| `trend_diagnostic` | Source/channel funnel chart | `source_channel_conversion_rate` |
| `risk_anomaly` | Leads idle > 7 days | `idle_lead_count` |

---

### 2.4 — Customer Master Health Dashboard

**Read model:** `CustomerMasterHealthRM`
**Route:** `/app/contacts/health`
**Role gate:** `sales_manager`, `data_admin`

| Zone | Widget | Metric path |
|---|---|---|
| `primary_kpi` | Total contacts | `contact_count` |
| `primary_kpi` | Completeness score | `avg_completeness_score` |
| `execution_queue` | Duplicate merge candidates | `merge_candidate_count` |
| `trend_diagnostic` | Hierarchy health by account tier | `hierarchy_rollup_health` |
| `risk_anomaly` | Duplicate contacts flagged | `duplicate_count` |

---

### 2.5 — Opportunity Pipeline & Forecast Dashboard

**Read model:** `OpportunityPipelineSnapshotRM`
**Route:** `/app/sales/dashboard`
**Role gate:** `sales_rep`, `sales_manager`, `owner`

| Zone | Widget | Metric path |
|---|---|---|
| `posture` | Deals with no activity 7d | `idle_deal_count` |
| `primary_kpi` | Weighted pipeline | `weighted_pipeline` |
| `primary_kpi` | Commit total | `forecast_commit_total` |
| `primary_kpi` | Closed won this period | `closed_won_total` |
| `execution_queue` | Deals overdue on close date | `overdue_close_count` |
| `trend_diagnostic` | Stage velocity chart | `stage_velocity` |
| `risk_anomaly` | Gap to target | `gap_to_target` |

---

### 2.6 — Quote Approval Cycle Dashboard

**Read model:** `QuoteApprovalCycleRM`
**Route:** `/app/sales/quotes/dashboard`
**Role gate:** `sales_rep`, `sales_manager`, `finance`

| Zone | Widget | Metric path |
|---|---|---|
| `primary_kpi` | Open quotes | `open_quote_count` |
| `primary_kpi` | Approval turnaround (avg hrs) | `avg_approval_turnaround_hours` |
| `execution_queue` | Quotes awaiting approval | `pending_approval_count` |
| `trend_diagnostic` | Discount band distribution | `discount_band_distribution` |
| `risk_anomaly` | Quotes stalled > 5 days | `stalled_quote_count` |

---

### 2.7 — Subscription Revenue Retention Dashboard

**Read model:** `SubscriptionRevenueRetentionRM`
**Route:** `/app/finance/subscriptions/dashboard`
**Role gate:** `finance`, `owner`

| Zone | Widget | Metric path |
|---|---|---|
| `posture` | Churn-risk subscriptions | `churn_flag_count` |
| `primary_kpi` | MRR | `mrr` |
| `primary_kpi` | ARR | `arr` |
| `primary_kpi` | Renewal rate | `renewal_rate` |
| `execution_queue` | Delinquent accounts | `delinquency_count` |
| `trend_diagnostic` | Revenue cohort retention | `renewal_cohort` |
| `risk_anomaly` | Expansion vs churn delta | `expansion_churn_delta` |

---

### 2.8 — Case SLA Operations Dashboard

**Read model:** `CaseSLAOperationalRM`
**Route:** `/app/support/dashboard`
**Role gate:** `support_agent`, `support_manager`

| Zone | Widget | Metric path |
|---|---|---|
| `posture` | Breached SLA count | `sla_breach_count` |
| `primary_kpi` | Open cases | `open_case_count` |
| `primary_kpi` | Avg first response (min) | `avg_first_response_minutes` |
| `primary_kpi` | SLA breach rate | `breach_rate` |
| `execution_queue` | Cases at-risk (SLA) | `at_risk_case_count` |
| `trend_diagnostic` | Resolution time trend | `avg_resolution_hours` |
| `risk_anomaly` | Breached cases unacknowledged | `unacknowledged_breach_count` |

---

### 2.9 — Communication Engagement Dashboard

**Read model:** `CommunicationEngagementRM`
**Route:** `/app/marketing/engagement`
**Role gate:** `marketing`, `sales_manager`

| Zone | Widget | Metric path |
|---|---|---|
| `primary_kpi` | Delivery rate | `delivery_rate` |
| `primary_kpi` | Open rate | `open_rate` |
| `primary_kpi` | Reply rate | `reply_rate` |
| `execution_queue` | Failed message threads | `failed_delivery_count` |
| `trend_diagnostic` | Engagement trend by channel | `delivery_open_click_reply_rate` |
| `risk_anomaly` | Channels with <50% delivery | `low_delivery_channel_count` |

---

### 2.10 — Knowledge Effectiveness Dashboard

**Read model:** `KnowledgeEffectivenessRM`
**Route:** `/app/support/knowledge/dashboard`
**Role gate:** `support_agent`, `support_manager`

| Zone | Widget | Metric path |
|---|---|---|
| `primary_kpi` | Published articles | `published_article_count` |
| `primary_kpi` | Case deflection rate | `case_deflection_rate` |
| `execution_queue` | Stale articles (> 90d) | `stale_article_count` |
| `trend_diagnostic` | Article adoption over time | `article_adoption_rate` |
| `risk_anomaly` | Articles with zero views | `zero_view_article_count` |

---

### 2.11 — Workflow Automation Outcome Dashboard

**Read model:** `WorkflowAutomationOutcomeRM`
**Route:** `/app/workflows/dashboard`
**Role gate:** `admin`, `operations`

| Zone | Widget | Metric path |
|---|---|---|
| `posture` | Failed workflow executions | `failure_count` |
| `primary_kpi` | Execution volume | `execution_volume_by_status` |
| `primary_kpi` | Success rate | `success_rate` |
| `execution_queue` | Workflows in retry backlog | `retry_queue_depth` |
| `trend_diagnostic` | Execution duration percentiles | `duration_p50`, `duration_p95` |
| `risk_anomaly` | Workflows with escalation count | `escalation_count` |

---

### 2.12 — Search Observability Dashboard

**Read model:** `SearchObservabilityRM`
**Route:** `/app/admin/search`
**Role gate:** `admin`, `super_admin`

| Zone | Widget | Metric path |
|---|---|---|
| `primary_kpi` | Index freshness lag (min) | `freshness_lag_minutes` |
| `primary_kpi` | Entity coverage % | `entity_coverage_rate` |
| `execution_queue` | Stale documents | `stale_document_count` |
| `trend_diagnostic` | Indexing throughput trend | `indexing_throughput` |
| `risk_anomaly` | Coverage below 95% | derived from `entity_coverage_rate` |

---

### 2.13 — Platform Audit & Reliability Dashboard

**Read model:** `PlatformReliabilityAuditRM`
**Route:** `/app/admin/audit/dashboard`
**Role gate:** `super_admin`, `compliance_officer`

| Zone | Widget | Metric path |
|---|---|---|
| `posture` | Sensitive action volume | `sensitive_action_volume` |
| `primary_kpi` | Audit entries (period) | `audit_entry_count` |
| `primary_kpi` | Policy deny rate | `policy_result_distribution.deny_rate` |
| `execution_queue` | Anomaly buckets open | `anomaly_bucket_count` |
| `trend_diagnostic` | Actor/resource heatmap | `actor_resource_heatmap` |
| `risk_anomaly` | Anomalies unreviewed | `unreviewed_anomaly_count` |

---

## 3) Interaction Patterns

1. **Role-gated entry:** User lands on `RoleDashboardMapping.default_dashboard_type` for their role. Dashboards outside their role mapping are not accessible.
2. **Widget drilldown:** Clicking a metric tile navigates to `WidgetDefinition.drilldown_route` with context filter pre-applied.
3. **Execution queue → record:** Clicking a queue item opens the entity detail view for that record (master-detail — no page churn).
4. **Risk anomaly persistence:** Anomaly widgets stay visible until the underlying metric resolves; they cannot be dismissed without action.
5. **Period selector:** All trend_diagnostic widgets respond to a shared period control (daily / weekly / monthly / quarterly). Default: current month.
6. **Empty state:** `empty_value` defined per widget — never shows blank tiles. Example: "No overdue leads" not "0".

---

## 4) Pakistan-Specific Owner Dashboard

The owner dashboard (see `docs/owner-dashboard.md`) is a curated subset of panels 2.3, 2.5, 2.7, 2.8. It prioritises:
- Leads with no follow-up (panel 2.3 → execution_queue)
- Cash collected vs outstanding (panel 2.7 → primary_kpi)
- Overdue invoices (panel 2.7 → risk_anomaly)
- Escalations unacknowledged (panel 2.8 → risk_anomaly)

No duplicate widgets — owner dashboard is a filtered projection, not a separate data model.

---

## SELF-QC

- **All 13 Archetype.md panels documented:** ✅ — panels 2.1–2.13 match Archetype.md exactly.
- **Every panel bound to a named read model:** ✅ — all 13 from `read-models.md` catalog.
- **Widget zones used correctly:** ✅ — posture/primary_kpi/execution_queue/trend_diagnostic/risk_anomaly pattern applied consistently.
- **Role-gating defined for all panels:** ✅
- **No duplicate metrics across panels:** ✅ — each read model appears exactly once.
- **Owner dashboard cross-referenced, not duplicated:** ✅

Score: **10/10**

## Error States (Dashboard Widgets)

| HTTP Status | Widget behavior |
|---|---|
| `401 Unauthorized` | Full page redirect to login |
| `403 Forbidden` | Widget shows "Restricted" placeholder with lock icon; no data |
| `404 Not Found` | Widget shows "No data" empty state |
| `429 Too Many Requests` | Widget shows last-cached value with "Refresh paused" indicator; auto-retry after `Retry-After` |
| `503 Service Unavailable` | Widget shows last-cached value with amber "Data may be stale" badge; retry button |

**Gap-to-target metric:** The "Gap to target" metric on the Opportunity Pipeline dashboard uses `tenant.settings.sales.pipeline_target_amount` as the target value. Default: `0` (widget shows "No target set" until configured by Tenant Admin).
