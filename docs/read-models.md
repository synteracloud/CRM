# CRM Read / Query Models

Read/query models are denormalized, query-optimized projections built from canonical domain entities and events. They are designed for low-latency dashboard rendering and stable API response contracts, without coupling consumers to write-model schemas.

## Read Model Catalog

| Name | Source entities | Transformations | Usage (dashboard/API) |
|---|---|---|---|
| TenantEntitlementOverviewRM | `Tenant`, `TenantEntitlement`, `FeatureFlag` | Flatten active plan + effective entitlements by tenant; compute enabled feature count and limits utilization snapshots. | Tenant admin dashboard; `GET /reporting/tenants/{tenant_id}/entitlements` |
| IdentityAccessPostureRM | `User`, `Role`, `Permission`, `UserRole`, `RolePermission`, `SessionToken` | Join user-role-permission graph; compute active users, privileged-user ratio, dormant users, active sessions by tenant. | Security posture dashboard; `GET /reporting/identity/posture` |
| LeadFunnelPerformanceRM | `Lead`, `LeadAssignment`, `Contact`, `Account`, `Opportunity` | Derive funnel stages (new, assigned, qualified, converted); compute assignment latency, conversion rate, source performance. | Sales development dashboard; `GET /reporting/leads/funnel` |
| CustomerMasterHealthRM | `Contact`, `Account`, `AccountHierarchy` | Normalize contact/account counts; compute duplicate/merge-adjusted survivorship metrics and hierarchy depth rollups. | Data quality dashboard; `GET /reporting/customers/master-health` |
| OpportunityPipelineSnapshotRM | `Opportunity`, `OpportunityLineItem`, `Account`, `Contact` | Build stage-based pipeline snapshots; calculate weighted pipeline, forecast totals, stage velocity, aging buckets. | Pipeline dashboard; `GET /reporting/opportunities/pipeline` |
| QuoteApprovalCycleRM | `Quote`, `QuoteLineItem`, `ApprovalRequest`, `Opportunity` | Join quote lifecycle with approval outcomes; calculate approval turnaround, discount bands, approve/reject ratio, quote acceptance rate. | Revenue operations dashboard; `GET /reporting/quotes/approval-cycle` |
| SubscriptionRevenueRetentionRM | `Subscription`, `InvoiceSummary`, `PaymentEvent`, `Account` | Compute MRR/ARR snapshots, renewal cohort status, churn/expansion flags, delinquency and collection effectiveness. | Subscription analytics dashboard; `GET /reporting/subscriptions/revenue-retention` |
| CaseSLAOperationalRM | `Case`, `CaseComment`, `Contact`, `Account` | Aggregate open/resolved queues; compute first-response time, resolution time, SLA breach rate by priority/owner/channel. | Support operations dashboard; `GET /reporting/cases/sla` |
| CommunicationEngagementRM | `MessageThread`, `Message`, `Notification` | Normalize message + notification delivery states; derive delivery/open/click/reply rates and engagement trend windows. | Engagement dashboard; `GET /reporting/communications/engagement` |
| KnowledgeEffectivenessRM | `KnowledgeArticle`, `Case` | Relate published knowledge coverage to case deflection and assisted-resolution indicators; compute article freshness/adoption metrics. | Support knowledge dashboard; `GET /reporting/knowledge/effectiveness` |
| WorkflowAutomationOutcomeRM | `WorkflowDefinition`, `WorkflowExecution` | Aggregate execution success/failure, runtime percentiles, retry/escalation counts by workflow and trigger domain. | Automation reliability dashboard; `GET /reporting/workflows/outcomes` |
| SearchObservabilityRM | `SearchDocument` | Compute index freshness lag, entity-type coverage, upsert volume, stale-document ratios. | Search health dashboard; `GET /reporting/search/observability` |
| PlatformReliabilityAuditRM | `AuditLog` | Build governance and reliability slices: sensitive-action volume, actor/resource heatmaps, policy result distributions, anomaly buckets. | Compliance dashboard; `GET /reporting/platform/audit` |

## Reporting Coverage Matrix

| Reporting need | Read model(s) |
|---|---|
| Tenant plan and entitlement visibility | `TenantEntitlementOverviewRM` |
| Identity, RBAC, and session risk posture | `IdentityAccessPostureRM` |
| Lead intake-to-conversion performance | `LeadFunnelPerformanceRM` |
| Customer/contact/account data quality and hierarchy reporting | `CustomerMasterHealthRM` |
| Opportunity pipeline, forecasting, and stage progression | `OpportunityPipelineSnapshotRM` |
| Quote approvals and quote-to-acceptance performance | `QuoteApprovalCycleRM` |
| Subscription lifecycle, revenue, collections, and retention | `SubscriptionRevenueRetentionRM` |
| Case SLA compliance and support throughput | `CaseSLAOperationalRM` |
| Cross-channel engagement and notification outcomes | `CommunicationEngagementRM` |
| Knowledge publication impact and deflection signals | `KnowledgeEffectivenessRM` |
| Workflow automation runtime reliability | `WorkflowAutomationOutcomeRM` |
| Search index freshness and coverage | `SearchObservabilityRM` |
| Audit/compliance and operational reliability governance | `PlatformReliabilityAuditRM` |

This catalog is intentionally non-duplicative: each read model owns a distinct analytical concern, while related domains are linked through the coverage matrix rather than duplicate projections.
