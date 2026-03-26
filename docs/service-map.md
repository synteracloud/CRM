# CRM Service Map

## Scope and Design Rules

- This map covers all primary CRM domains: identity/access, customer master data, lead-to-opportunity pipeline, sales execution, customer support, communication, billing/subscription context, analytics/reporting, and platform operations.
- Responsibilities are intentionally **non-overlapping**: each capability has one owning service.
- Services are classified as:
  - **Core**: cross-domain, foundational business capabilities
  - **Domain**: domain-specific business logic
  - **Platform**: infrastructure and operational capabilities
- **Boundary** indicates whether a service is internal or external to the CRM system.

## Service Catalog

| Layer | Service Name | Boundary | Responsibility (Single Owner) | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|---|
| Core | API Gateway | Internal | Authenticate/authorize API calls, route requests to internal services, enforce rate limits. | HTTP/gRPC requests, access tokens, client metadata | Routed requests, standardized API responses, rejection events | Identity & Access Service, Audit & Compliance Service, Notification Orchestrator |
| Core | Identity & Access Service | Internal | Manage users, roles, permissions, session/token lifecycle. | User credentials, SSO assertions, RBAC policy updates | Access/refresh tokens, auth decisions, identity events | Audit & Compliance Service |
| Core | Organization & Tenant Service | Internal | Manage tenant/account-level configuration, plan entitlements, and regional settings. | Tenant provisioning requests, plan assignments, config updates | Tenant profiles, feature-flag context, entitlement events | Billing & Subscription Service, Feature Flag Service |
| Core | Workflow Automation Service | Internal | Execute declarative business workflows and rule-triggered automations. | Domain events, workflow definitions, rule conditions | Task executions, webhook calls, automation outcome events | Event Bus, Notification Orchestrator, Job Scheduler |
| Core | Notification Orchestrator | Internal | Build and dispatch in-app/email/SMS notifications from canonical templates and events. | Notification commands, event payloads, user preferences | Sent notifications, delivery status events, failure events | Template Service, Email Delivery Provider, SMS Delivery Provider |
| Domain | Lead Management Service | Internal | Own lead capture, qualification state machine, assignment, and conversion trigger. | Web form submissions, imports, campaign attribution, rep actions | Lead records, qualification events, lead-to-contact/account conversion commands | Contact Service, Account Service, Opportunity Service, Activity Timeline Service |
| Domain | Contact Service | Internal | Own person-level customer records, lifecycle status, preferences, and deduplication. | Contact CRUD requests, merge requests, import files | Canonical contact records, merge events, preference snapshots | Data Quality Service, Activity Timeline Service |
| Domain | Account Service | Internal | Own company/customer account records, hierarchy, segmentation, and ownership. | Account CRUD requests, enrichment updates, ownership changes | Canonical account records, account hierarchy events | Data Quality Service, Territory & Assignment Service |
| Domain | Opportunity Service | Internal | Own pipeline opportunities, stage progression, forecasting fields, and close outcomes. | Opportunity updates, pricing context, qualification signals | Stage-change events, forecast records, win/loss outcomes | Product Catalog Service, Quote Service, Activity Timeline Service |
| Domain | Quote Service | Internal | Generate and manage commercial quotes, discounts, and approval state. | Opportunity context, product selections, discount rules | Quote documents, approval requests, accepted quote events | Product Catalog Service, Approval Service, Billing & Subscription Service |
| Domain | Activity Timeline Service | Internal | Store and expose immutable timeline of customer-facing interactions and system actions. | Calls, emails, meetings, notes, domain events | Ordered activity feed, engagement metrics events | Communication Service, Event Bus |
| Domain | Communication Service | Internal | Track CRM-originated emails/calls/messages and their interaction metadata. | Outbound message requests, inbound webhook events, call logs | Message records, reply/open/click events, conversation thread state | Email Delivery Provider, Telephony Provider, Activity Timeline Service |
| Domain | Case Management Service | Internal | Own support case intake, triage, SLA state, and resolution workflow. | Case submissions, channel messages, priority rules | Case records, SLA breach events, resolution events | Knowledge Base Service, Notification Orchestrator, Activity Timeline Service |
| Domain | Knowledge Base Service | Internal | Manage support articles, taxonomy, and retrieval for support workflows. | Article drafts, publication commands, search queries | Published articles, article metadata, relevance signals | Search Index Service |
| Domain | Product Catalog Service | Internal | Own sellable products, pricing books, and packaging metadata used in sales flows. | Product updates, pricing policy changes | Product/pricing snapshots, catalog change events | Approval Service |
| Domain | Billing & Subscription Service | Internal | Manage customer subscriptions, invoice state mirrors, and payment status for CRM context. | Accepted quote events, external billing webhooks, plan changes | Subscription status, invoice summaries, delinquency events | Payment Gateway (External), Organization & Tenant Service |
| Domain | Territory & Assignment Service | Internal | Compute and apply ownership/territory assignment for leads, accounts, and opportunities. | Routing rules, rep capacity, geo/account attributes | Ownership assignments, reassignment events | Lead Management Service, Account Service, Opportunity Service |
| Domain | Analytics & Reporting Service | Internal | Produce curated operational/business metrics, dashboards, and scheduled reports. | Domain events, query requests, reporting definitions | KPI datasets, dashboards, exported reports | Data Warehouse, Event Bus |
| Platform | Event Bus | Internal | Provide asynchronous event transport with durable pub/sub semantics. | Domain events, integration events | Event streams, delivery acknowledgements, dead-letter events | Schema Registry |
| Platform | Job Scheduler | Internal | Run delayed, recurring, and retryable background jobs. | Job definitions, cron schedules, retry policies | Job execution events, task completions/failures | Event Bus |
| Platform | Search Index Service | Internal | Index CRM entities/content and serve low-latency full-text/filter search. | Entity change events, indexing jobs, search queries | Search results, index health metrics | Event Bus, Job Scheduler |
| Platform | Data Quality Service | Internal | Execute validation, normalization, deduplication signals, and survivorship policies. | Contact/account/lead upserts, merge candidates | Quality scores, canonicalization suggestions, duplicate alerts | Contact Service, Account Service, Lead Management Service |
| Platform | Approval Service | Internal | Centralize policy-based approvals (discounts, exceptions, access-sensitive changes). | Approval requests, policy rules, approver actions | Approval decisions, escalation events | Identity & Access Service, Notification Orchestrator |
| Platform | Audit & Compliance Service | Internal | Persist immutable audit trail for user/admin/data-access actions and policy checks. | Security-sensitive actions, admin changes, access decisions | Audit logs, compliance exports, anomaly alerts | Identity & Access Service, Event Bus |
| Platform | Feature Flag Service | Internal | Control runtime feature exposure by tenant, role, and environment. | Flag definitions, targeting rules, evaluation calls | Flag evaluations, rollout events | Organization & Tenant Service |
| Platform | Template Service | Internal | Manage reusable notification/document templates with versioning and localization. | Template CRUD, localization updates, render requests | Rendered content, template version events | Search Index Service |
| Platform | Data Warehouse | Internal | Store analytics-ready historical data models for reporting and BI workloads. | ETL/ELT loads, event streams, snapshot tables | Queryable marts, aggregate tables | Event Bus, Analytics & Reporting Service |
| External | Email Delivery Provider | External | Deliver outbound emails and emit delivery/open/click/bounce webhooks. | Email payloads, templates, recipient metadata | Delivery status webhooks, provider message IDs | Notification Orchestrator, Communication Service |
| External | SMS Delivery Provider | External | Deliver outbound SMS and emit delivery/failure webhooks. | SMS payloads, recipient numbers | Delivery receipts, failure webhooks | Notification Orchestrator |
| External | Telephony Provider | External | Provide call placement/recording and call event webhooks. | Dial requests, call control commands | Call records, call state events, recordings metadata | Communication Service |
| External | Payment Gateway | External | Process charges/refunds and emit payment lifecycle events. | Payment intents, capture/refund commands | Payment outcomes, settlement events, dispute events | Billing & Subscription Service |

## Domain Coverage Matrix

| CRM Domain | Owning Service(s) |
|---|---|
| Identity, access, and security | Identity & Access Service; Audit & Compliance Service |
| Tenant and account configuration | Organization & Tenant Service; Feature Flag Service |
| Lead capture and qualification | Lead Management Service |
| Customer people records | Contact Service |
| Customer company records and hierarchy | Account Service |
| Pipeline and sales execution | Opportunity Service; Quote Service; Territory & Assignment Service |
| Customer interactions and engagement | Communication Service; Activity Timeline Service |
| Customer support operations | Case Management Service; Knowledge Base Service |
| Product and pricing context | Product Catalog Service |
| Subscription and billing context | Billing & Subscription Service |
| Analytics, BI, and reporting | Analytics & Reporting Service; Data Warehouse |
| Cross-service automation and orchestration | Workflow Automation Service; Job Scheduler; Event Bus |
| Search and retrieval | Search Index Service |
| Data quality and governance | Data Quality Service; Approval Service |

## Boundary Summary

- **Internal services**: all Core, Domain, and Platform services except explicit provider integrations.
- **External services**: Email Delivery Provider, SMS Delivery Provider, Telephony Provider, Payment Gateway.
