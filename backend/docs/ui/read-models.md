<!-- OWNERSHIP
PRIMARY FOR: Full read model catalog — every *RM entity name, source entities, refresh trigger, and consumer API.
DEFERS TO: domain-model.md (base entity fields); kpi-data-pipelines.md (aggregation pipeline topology); employee-performance.md (KPI formulas); territory-management.md (territory entity definitions).
DO NOT RE-DEFINE: Write-side entity schemas; KPI formula definitions; dashboard routing rules.
-->

# CRM Read / Query Models

Read/query models are denormalized, query-optimized projections used by reporting dashboards and reporting APIs. They are built from canonical source entities and derived event streams, and are optimized for low-latency reads without coupling consumers to write-model schemas.

## Read Model Catalog

| Name | Source entities | Transformations | Usage (dashboard/API) |
|---|---|---|---|
| TenantEntitlementOverviewRM | `Tenant`, `TenantEntitlement`, `FeatureFlag` | Flatten tenant plan and effective entitlements; compute enabled feature counts, utilization against limits, and entitlement timeline snapshots. | Tenant administration dashboard; **computed client-side** from `GET /api/v1/tenants/current` (to create — `v1-tenants.routes.js`) + `GET /api/v1/users` (exists) + `GET /api/v1/feature-flags` (to create — `v1-feature-flags-mgmt.routes.js`). No `/reporting` endpoint exists or is needed. |
| IdentityAccessPostureRM | `User`, `Role`, `Permission`, `UserRole`, `RolePermission`, `SessionToken` | Join RBAC graph and session lifecycle; derive active-user counts, privileged-access distribution, dormant accounts, and active-session risk indicators. | Identity and security dashboard; `GET /api/v1/reporting/identity/posture` |
| LeadFunnelPerformanceRM | `Lead`, `LeadAssignment`, `Contact`, `Account`, `Opportunity` | Normalize lead lifecycle stages (new, assigned, qualified, converted); compute assignment latency, stage conversion rates, and source/channel performance. | Sales development dashboard; `GET /api/v1/reporting/leads/funnel` |
| CustomerMasterHealthRM | `Contact`, `Account`, `AccountHierarchy` | Build customer master projection across people/companies; calculate duplicate/merge survivorship, completeness scores, and hierarchy rollups. | Data quality dashboard; **computed client-side** from `GET /api/v1/contacts?limit=500` (exists inline in `v1-contacts.routes.js`). Metrics computed in JS driver: completeness mean, phone-exact dupe count, account-linked rate. No `/reporting` endpoint exists or is needed. |
| OpportunityPipelineSnapshotRM | `Opportunity`, `OpportunityLineItem`, `Account`, `Contact` | Snapshot pipeline by stage and period; compute weighted pipeline, forecast totals, stage velocity, cycle time, and aging buckets. | Pipeline and forecasting dashboard; `GET /api/v1/reporting/opportunities/pipeline` |
| QuoteApprovalCycleRM | `Quote`, `QuoteLineItem`, `ApprovalRequest`, `Opportunity` | Correlate quote lifecycle with approval decisions; compute approval turnaround, discount-band behavior, reject/approve ratios, and quote acceptance performance. | Revenue operations dashboard; `GET /api/v1/reporting/quotes/approval-cycle` |
| SubscriptionRevenueRetentionRM | `Subscription`, `InvoiceSummary`, `PaymentEvent`, `Account` | Build recurring-revenue time series; compute MRR/ARR, renewal cohorts, churn/expansion flags, delinquency rates, and collections performance. | Subscription and finance dashboard; `GET /api/v1/reporting/subscriptions/revenue-retention` |
| CaseSLAOperationalRM | `Case`, `CaseComment`, `Contact`, `Account` | Aggregate support workload and SLA outcomes; compute first-response time, resolution time, backlog, SLA breach rates, and channel/priority performance. | Support operations dashboard; `GET /api/v1/reporting/cases/sla` |
| CommunicationEngagementRM | `MessageThread`, `Message`, `Notification` | Unify conversation and notification delivery state; derive delivery/open/click/reply rates, campaign engagement, and trend windows by channel. | Engagement dashboard; `GET /api/v1/reporting/communications/engagement` |
| KnowledgeEffectivenessRM | `KnowledgeArticle`, `Case` | Relate knowledge publication and freshness to support outcomes; compute article adoption, case deflection indicators, and assisted-resolution impact. | Knowledge effectiveness dashboard; `GET /api/v1/reporting/knowledge/effectiveness` |
| WorkflowAutomationOutcomeRM | `WorkflowDefinition`, `WorkflowExecution` | Aggregate automation runtime outcomes; compute execution volume, success/failure rates, duration percentiles, retry behavior, and escalation counts. | Automation reliability dashboard; `GET /api/v1/reporting/workflows/outcomes` |
| SearchObservabilityRM | `SearchDocument` | Track search index health; compute freshness lag, entity coverage, indexing throughput, and stale-document ratios over time. | Search operations dashboard; `GET /api/v1/reporting/search/observability` |
| PlatformReliabilityAuditRM | `AuditLog` | Produce governance and platform slices; compute sensitive-action volume, actor/resource heatmaps, policy result distributions, and anomaly buckets. | Compliance and reliability dashboard; **computed client-side** from `GET /api/v1/audits/events` (exists in `v1-audit.routes.js`). Metrics computed in JS driver: deny rate, sensitive action count, actor heatmap grouping. No `/reporting` endpoint exists or is needed. |
| ActivityTaskOperationalRM | `Task`, `ActivityEvent`, `User` | Aggregate task workload by owner; compute overdue-task counts, due-today queues, no-next-action gaps, and completion rate trends. | Sales cockpit next-actions panel; `GET /api/v1/reporting/tasks/operational` |
| EmployeePerformanceRM | `ActivityEvent`, `Lead`, `Opportunity`, `FollowUp`, `User` | Project per-rep KPI scores (P-01 through P-08); compute call volume, lead conversion rate, follow-up completion rate, deals won, avg response time, and activity streak. See `employee-performance.md` for formula definitions. | Employee performance dashboard; `GET /api/v1/reporting/employees/performance` |
| TerritoryPerformanceRM | `TerritoryAssignment`, `Lead`, `Opportunity`, `ActivityEvent`, `User` | Aggregate per-territory pipeline value, lead count, conversion rate, and rep activity distribution. Used for territory health and rebalancing decisions. See `territory-management.md` for territory entity definitions. | Territory management dashboard; `GET /api/v1/reporting/territories/performance` |
| PartnerPerformanceRM | `Partner`, `DealRegistration`, `Opportunity`, `PartnerCommission` | Aggregate partner channel metrics: attributed opportunity count and total value by partner and tier; commission due vs paid; deal registration approval rates; tier distribution. See `partners.md` for entity definitions. | Partner list + partner detail dashboards; `GET /api/v1/reporting/partners/performance` |
| PredictiveInsightRM | `LeadScore`, `ChurnPrediction`, `CLVEstimate`, `Lead`, `Account` | Aggregate AI model outputs across the tenant: avg win probability (derived from lead score bands), churn risk account count by band, avg CLV estimate, model accuracy (static from model registry), score distribution histograms for win probability distribution chart. See `ai-predictive-models.md` for model definitions. | AI Insights Dashboard (M-02); `GET /api/v1/reporting/ai/insights` |

## Reporting Coverage (No Duplicates)

| Reporting need | Model |
|---|---|
| Tenant provisioning and entitlement visibility | `TenantEntitlementOverviewRM` |
| Identity, RBAC, and session posture | `IdentityAccessPostureRM` |
| Lead intake-to-conversion performance | `LeadFunnelPerformanceRM` |
| Contact/account master-data quality and hierarchy health | `CustomerMasterHealthRM` |
| Opportunity pipeline, forecast, and close progression | `OpportunityPipelineSnapshotRM` |
| Quote pricing, approval, and acceptance cycle | `QuoteApprovalCycleRM` |
| Subscription lifecycle, recurring revenue, invoicing, and payments | `SubscriptionRevenueRetentionRM` |
| Case throughput and SLA compliance | `CaseSLAOperationalRM` |
| Message/notification engagement outcomes | `CommunicationEngagementRM` |
| Knowledge publication and case-deflection impact | `KnowledgeEffectivenessRM` |
| Workflow runtime reliability and automation outcomes | `WorkflowAutomationOutcomeRM` |
| Search indexing freshness and coverage | `SearchObservabilityRM` |
| Audit, governance, and platform reliability insights | `PlatformReliabilityAuditRM` |
| Task workload and overdue queue by owner | `ActivityTaskOperationalRM` |
| Per-rep KPI performance (calls, conversions, follow-ups, deals) | `EmployeePerformanceRM` |
| Territory pipeline health and rep distribution | `TerritoryPerformanceRM` |
| Partner attribution, deal registration, and commission ledger | `PartnerPerformanceRM` |
| AI lead scores, churn predictions, CLV estimates, and model accuracy | `PredictiveInsightRM` |

Each reporting need maps to exactly one read model, ensuring full reporting coverage with no duplicate models.

## Read Model Field Addenda

### SubscriptionRevenueRetentionRM — field schema
*Added 2026-05-28 — required before A-06 subscriptions-dashboard.html and C-09 subscriptions-detail.html can pass 4-source check.*

| Field | Type | Description |
|---|---|---|
| `mrr` | decimal | Monthly Recurring Revenue — current period |
| `arr` | decimal | Annual Recurring Revenue (MRR × 12) |
| `new_mrr` | decimal | MRR from new subscriptions this period |
| `expansion_mrr` | decimal | MRR from upgrades/plan changes |
| `contraction_mrr` | decimal | MRR lost from downgrades |
| `churn_mrr` | decimal | MRR lost from cancellations |
| `net_new_mrr` | decimal | new + expansion − contraction − churn |
| `churn_rate` | decimal | Percentage of subscriptions cancelled (period) |
| `renewal_rate` | decimal | Percentage of due renewals that renewed |
| `active_subscription_count` | integer | Subscriptions in `active` state |
| `past_due_count` | integer | Subscriptions in `past_due` state |
| `delinquency_rate` | decimal | past_due / total active subscriptions |
| `collections_performance` | object | `{ collected_amount, outstanding_amount, overdue_amount, collection_rate_pct }` |
| `monthly_trend` | array | 6-month trailing monthly_trend array (see §monthly_trend computation) |

**API response:** `GET /api/v1/reporting/subscriptions/revenue-retention`

---

### ActivityTaskOperationalRM — field schema
*Added 2026-05-28 — required before D-01 sales-cockpit.html (next-actions panel) and B-07 tasks.html can pass 4-source check.*

| Field | Type | Description |
|---|---|---|
| `overdue_task_count` | integer | Tasks with `state = overdue` |
| `due_today_count` | integer | Tasks with `due_at` date = today |
| `no_next_action_count` | integer | Leads with no pending FollowUp task |
| `completion_rate_pct` | decimal | Completed tasks / total tasks (rolling 7 days) |
| `by_owner` | array | Per-user breakdown: `{ owner_id, overdue, due_today, completion_rate }` |
| `by_entity_type` | object | Task counts grouped by entity_type (`lead / opportunity / contact / null`) |
| `monthly_trend` | array | 6-month trailing completion rate trend |

**API response:** `GET /api/v1/reporting/tasks/operational`

---

### EmployeePerformanceRM — field schema
*Added 2026-05-28 — required before H-01 sales-analytics.html (rep performance section) can pass 4-source check. Full KPI formula definitions in `employee-performance.md`.*

| Field | Type | KPI | Description |
|---|---|---|---|
| `rep_id` | uuid | — | FK→User |
| `rep_name` | string | — | Display name |
| `leads_captured` | integer | P-01 | New leads assigned to rep this period |
| `followup_completion_rate` | decimal | P-02 | On-time follow-up completions / total due |
| `avg_first_response_hours` | decimal | P-03 | Average hours from lead creation to first contact |
| `lead_conversion_rate` | decimal | P-04 | Converted leads / total leads owned |
| `deals_won` | integer | P-05 | Opportunities closed_won this period |
| `daily_activity_count` | integer | P-06 | Activity events logged (excludes passive view) |
| `overdue_followup_count` | integer | P-07 | Open FollowUp tasks in `overdue` state |
| `avg_deal_cycle_days` | decimal | P-08 | Average days from qualification to close |
| `period` | string | — | `today / week / month / rolling_30` |
| `computed_at` | datetime | — | Last computation timestamp |

**API response:** `GET /api/v1/reporting/employees/performance?period=week`
**Note:** Refresh every 60 minutes per `EmployeePerformanceRM` refresh schedule.

---

### TenantEntitlementOverviewRM — additional fields

The following fields are available in `TenantEntitlementOverviewRM` beyond the catalog summary:

| Field | Type | Description |
|---|---|---|
| `entitlements_at_limit` | integer | Count of feature entitlements where current usage ≥ 90% of `limit_value` |
| `entitlement_overage_count` | integer | Count of entitlements where current usage exceeds `limit_value` |
| `utilization_by_feature` | object[] | Per-feature utilization percentage |

## Read Model Refresh Frequencies

| Read Model | Refresh mechanism | Target freshness | Stale-data fallback |
|---|---|---|---|
| TenantEntitlementOverviewRM | Event-driven (`tenant.entitlement.updated.v1`) | p95 < 5s | Show last-known values with "as of {timestamp}" indicator |
| IdentityAccessPostureRM | Event-driven (`identity.user.role.assigned.v1`) | p95 < 5s | Show cached posture with staleness warning |
| LeadFunnelPerformanceRM | Event-driven (`lead.created.v1`, `lead.converted.v1`) + hourly batch reconciliation | p95 < 10s | Show last batch values with staleness banner |
| CustomerMasterHealthRM | Event-driven (`contact.merged.v1`, `account.created.v1`) + daily quality scan | p95 < 30s | Show last-known health score with scan date |
| OpportunityPipelineSnapshotRM | Event-driven (`opportunity.stage.changed.v1`, `opportunity.closed.v1`) | p95 < 5s | Show cached pipeline with "last updated" timestamp |
| QuoteApprovalCycleRM | Event-driven (`approval.decided.v1`, `quote.accepted.v1`) | p95 < 10s | Show last cycle metrics with staleness indicator |
| SubscriptionRevenueRetentionRM | Event-driven (`subscription.status.changed.v1`, `payment.event.recorded.v1`) + hourly MRR recalc | p95 < 60s | Show last MRR calculation with timestamp |
| CaseSLAOperationalRM | Event-driven (`case.created.v1`, `case.sla.breached.v1`, `case.resolved.v1`) | p95 < 5s | Show last-known SLA counts with warning |
| CommunicationEngagementRM | Event-driven (`communication.message.engagement.updated.v1`) + 15-min batch aggregation | p95 < 15s | Show last batch engagement metrics |
| KnowledgeEffectivenessRM | Daily batch (article publication + case resolution correlation) | p95 < 24h | Show previous day's metrics |
| WorkflowAutomationOutcomeRM | Event-driven (`workflow.execution.completed.v1`, `workflow.execution.failed.v1`) | p95 < 10s | Show last-known outcome rates |
| SearchObservabilityRM | 15-minute batch (index health check) | p95 < 15 min | Show last health check with timestamp |
| PlatformReliabilityAuditRM | Event-driven (`audit.log.recorded.v1`) + hourly aggregation | p95 < 60s | Show last hour's audit metrics |
| ActivityTaskOperationalRM | Event-driven (task state changes) + 15-min sweep | p95 < 15s | Show last sweep results |
| EmployeePerformanceRM | Event-driven (`activity.logged.v1`, `lead.converted.v1`, `opportunity.closed.v1`, `followup.completed.v1`) + hourly KPI recalc | p95 < 60s | Show last hourly calculation with timestamp |
| TerritoryPerformanceRM | Event-driven (`lead.assignment.updated.v1`, `opportunity.closed.v1`) + daily batch | p95 < 24h | Show previous day's territory metrics |

---

## RM Catalog → Dashboard Read Model Shape Mapping

The Read Model Catalog (above) names the *aggregation stores*. The `Dashboard Read Model Shapes` section (below) defines the *API response shapes* returned to the frontend. Each shape is backed by the corresponding RM. This cross-reference was added 2026-05-28 to resolve the naming ambiguity.

| RM Catalog Entry | Dashboard Read Model Shape | Consumer API | Key frontend fields |
|---|---|---|---|
| `LeadFunnelPerformanceRM` | `MarketingDashboardReadModel` | `GET /api/v1/reporting/leads/funnel` | `lead_count`, `qualified_lead_count`, `converted_lead_count`, `conversion_rate`, `avg_assignment_latency_hours`, `source_counts`, `monthly_trend` |
| `OpportunityPipelineSnapshotRM` | `SalesDashboardReadModel` | `GET /api/v1/reporting/opportunities/pipeline` | `total_pipeline_amount`, `weighted_pipeline_amount`, `open_opportunity_count`, `won_opportunity_count`, `avg_sales_cycle_days`, `stage_counts`, `monthly_trend` |
| `SubscriptionRevenueRetentionRM` | (finance shape — not yet typed in this doc) | `GET /api/v1/reporting/subscriptions/revenue-retention` | MRR/ARR, churn rate, renewal cohorts, collections_performance |
| `CaseSLAOperationalRM` | `SupportDashboardReadModel` | `GET /api/v1/reporting/cases/sla` | `open_case_count`, `resolved_case_count`, `sla_breach_count`, `breach_rate`, `avg_first_response_minutes`, `avg_resolution_hours`, `priority_counts`, `monthly_trend` |
| `PlatformReliabilityAuditRM` | `AdminDashboardReadModel` | `GET /api/v1/audits/events` (**exists**; no `/reporting` endpoint needed — computed client-side) | `audit_entry_count`, `deny_rate`, `sensitive_action_volume`, `anomaly_bucket_count`, `actor_resource_heatmap`, `unreviewed_anomaly_count` |
| `ActivityTaskOperationalRM` | (operational shape — not yet typed) | `GET /api/v1/reporting/tasks/operational` | `overdue_task_counts`, `due_today_queues`, `no_next_action_gaps`, `completion_rate_trends` |
| `EmployeePerformanceRM` | (per-rep shape — see employee-performance.md) | `GET /api/v1/reporting/employees/performance` | P-01 through P-08 per-rep KPI scores |

**Note:** Shapes not yet typed in this file (`SubscriptionRevenueRetentionRM`, `ActivityTaskOperationalRM`, `EmployeePerformanceRM`) should have their field schemas added here before the corresponding pages are built. Adding them is Phase 5A doc-completion work.

---

## Dashboard Widget System

*Added from src/reporting_dashboards overlay — 2026-04-02*

### Widget States

Each widget progresses through a render lifecycle. `WIDGET_STATE`:

`default | loading | empty | error | restricted`

### Widget Zones

Each dashboard is divided into five functional zones. Widgets are assigned to zones by `WidgetDefinition.zone`:

| Zone | Purpose |
|---|---|
| `posture` | High-level health/risk bar — always visible |
| `primary_kpi` | Core metric tiles — headline numbers |
| `execution_queue` | Actionable list or queue driving immediate work |
| `trend_diagnostic` | Time-series chart or cohort drill-down |
| `risk_anomaly` | Anomaly detection, alerts, breach indicators |

### Dashboard Types

`sales \| marketing \| support \| admin`

### WidgetDefinition

Config-driven widget mapped to a read-model metric path.

| Field | Notes |
|---|---|
| `widget_id` | Unique within dashboard |
| `title` | Display label |
| `widget_type` | Chart type / display hint |
| `metric_path` | Dot-path into the read model (`rm_field.sub_field`) |
| `zone` | One of the 5 zones above |
| `format_as` | `raw \| currency \| percent \| duration \| count` |
| `required_permissions` | Scopes needed to view this widget |
| `drilldown_route` | Optional route navigated on widget click |
| `empty_value` | Value to display when metric is null/zero |

**`empty_value` null vs zero distinction:**

| Scenario | Display behavior |
|---|---|
| Metric is `null` (data not yet available / pipeline not yet populated) | Show `—` (em dash) with tooltip "Data not yet available" |
| Metric is `0` (true zero — pipeline has run but result is zero) | Show `0` with appropriate unit |
| Metric is stale (freshness SLA breached) | Show last-known value with amber staleness badge |

Widget `empty_value` field specifies what to show for `null` only. Zero is always rendered as `0`.

### DashboardLayoutConfig

Config-driven layout composing a full dashboard from `WidgetDefinition` entries.

| Field | Notes |
|---|---|
| `dashboard_type` | One of the 4 dashboard types |
| `columns` | Grid column count |
| `widgets` | Ordered tuple of `WidgetDefinition` |

### RoleDashboardMapping

Controls which dashboards a role can access and what appears by default.

| Field | Notes |
|---|---|
| `role_id` | FK→Role |
| `dashboard_types` | Eligible dashboards for this role |
| `default_dashboard_type` | Shown on first login |

### Dashboard Read Model Shapes

Typed read models consumed by dashboard widgets:

| Read model class | Dashboard | Key metrics |
|---|---|---|
| `SalesDashboardReadModel` | Sales | `total_pipeline_amount`, `weighted_pipeline_amount`, `open_opportunity_count`, `won_opportunity_count`, `avg_sales_cycle_days`, `stage_counts`, `monthly_trend` |
| `MarketingDashboardReadModel` | Marketing | `lead_count`, `qualified_lead_count`, `converted_lead_count`, `conversion_rate`, `avg_assignment_latency_hours`, `source_counts`, `monthly_trend` |
| `SupportDashboardReadModel` | Support | `open_case_count`, `resolved_case_count`, `sla_breach_count`, `breach_rate`, `avg_first_response_minutes`, `avg_resolution_hours`, `priority_counts`, `monthly_trend` |
| `AdminDashboardReadModel` | Admin | `active_user_count`, `privileged_user_count`, `dormant_user_count`, `active_session_risk_count`, `entitlement_feature_count`, `audit_sensitive_action_count`, `monthly_audit_trend` |

**`monthly_trend` computation:**

`monthly_trend` is a 6-month trailing array of monthly aggregates, computed as:

```
monthly_trend[i] = {
  month: "YYYY-MM",
  value: <metric total for that calendar month>,
  delta_pct: <percentage change vs prior month>
}
```

- Window: last 6 complete calendar months (current partial month excluded).
- Aggregation: sum of the relevant metric (e.g., `won_opportunity_count` for sales trend).
- Computed via hourly batch job from the relevant read model's source events.
- Freshness: aligned to the parent read model's refresh frequency.
