# CRM Read / Query Models

Read/query models are denormalized, query-optimized projections used by reporting dashboards and reporting APIs. They are built from canonical source entities and derived event streams, and are optimized for low-latency reads without coupling consumers to write-model schemas.

## Read Model Catalog

| Name | Source entities | Transformations | Usage (dashboard/API) |
|---|---|---|---|
| TenantEntitlementOverviewRM | `Tenant`, `TenantEntitlement`, `FeatureFlag` | Flatten tenant plan and effective entitlements; compute enabled feature counts, utilization against limits, and entitlement timeline snapshots. | Tenant administration dashboard; `GET /api/v1/reporting/tenants/{tenant_id}/entitlements` |
| IdentityAccessPostureRM | `User`, `Role`, `Permission`, `UserRole`, `RolePermission`, `SessionToken` | Join RBAC graph and session lifecycle; derive active-user counts, privileged-access distribution, dormant accounts, and active-session risk indicators. | Identity and security dashboard; `GET /api/v1/reporting/identity/posture` |
| LeadFunnelPerformanceRM | `Lead`, `LeadAssignment`, `Contact`, `Account`, `Opportunity` | Normalize lead lifecycle stages (new, assigned, qualified, converted); compute assignment latency, stage conversion rates, and source/channel performance. | Sales development dashboard; `GET /api/v1/reporting/leads/funnel` |
| CustomerMasterHealthRM | `Contact`, `Account`, `AccountHierarchy` | Build customer master projection across people/companies; calculate duplicate/merge survivorship, completeness scores, and hierarchy rollups. | Data quality dashboard; `GET /api/v1/reporting/customers/master-health` |
| OpportunityPipelineSnapshotRM | `Opportunity`, `OpportunityLineItem`, `Account`, `Contact` | Snapshot pipeline by stage and period; compute weighted pipeline, forecast totals, stage velocity, cycle time, and aging buckets. | Pipeline and forecasting dashboard; `GET /api/v1/reporting/opportunities/pipeline` |
| QuoteApprovalCycleRM | `Quote`, `QuoteLineItem`, `ApprovalRequest`, `Opportunity` | Correlate quote lifecycle with approval decisions; compute approval turnaround, discount-band behavior, reject/approve ratios, and quote acceptance performance. | Revenue operations dashboard; `GET /api/v1/reporting/quotes/approval-cycle` |
| SubscriptionRevenueRetentionRM | `Subscription`, `InvoiceSummary`, `PaymentEvent`, `Account` | Build recurring-revenue time series; compute MRR/ARR, renewal cohorts, churn/expansion flags, delinquency rates, and collections performance. | Subscription and finance dashboard; `GET /api/v1/reporting/subscriptions/revenue-retention` |
| CaseSLAOperationalRM | `Case`, `CaseComment`, `Contact`, `Account` | Aggregate support workload and SLA outcomes; compute first-response time, resolution time, backlog, SLA breach rates, and channel/priority performance. | Support operations dashboard; `GET /api/v1/reporting/cases/sla` |
| CommunicationEngagementRM | `MessageThread`, `Message`, `Notification` | Unify conversation and notification delivery state; derive delivery/open/click/reply rates, campaign engagement, and trend windows by channel. | Engagement dashboard; `GET /api/v1/reporting/communications/engagement` |
| KnowledgeEffectivenessRM | `KnowledgeArticle`, `Case` | Relate knowledge publication and freshness to support outcomes; compute article adoption, case deflection indicators, and assisted-resolution impact. | Knowledge effectiveness dashboard; `GET /api/v1/reporting/knowledge/effectiveness` |
| WorkflowAutomationOutcomeRM | `WorkflowDefinition`, `WorkflowExecution` | Aggregate automation runtime outcomes; compute execution volume, success/failure rates, duration percentiles, retry behavior, and escalation counts. | Automation reliability dashboard; `GET /api/v1/reporting/workflows/outcomes` |
| SearchObservabilityRM | `SearchDocument` | Track search index health; compute freshness lag, entity coverage, indexing throughput, and stale-document ratios over time. | Search operations dashboard; `GET /api/v1/reporting/search/observability` |
| PlatformReliabilityAuditRM | `AuditLog` | Produce governance and platform slices; compute sensitive-action volume, actor/resource heatmaps, policy result distributions, and anomaly buckets. | Compliance and reliability dashboard; `GET /api/v1/reporting/platform/audit` |

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

Each reporting need maps to exactly one read model, ensuring full reporting coverage with no duplicate models.
