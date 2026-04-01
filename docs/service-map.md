# CRM Service Map

## Scope and Design Rules

- This map covers all primary CRM domains: identity/access, customer master data, lead-to-opportunity pipeline, sales execution, customer support, communication, billing/subscription context, analytics/reporting, and platform operations.
- Responsibilities are intentionally **non-overlapping**: each capability has one owning service.
- Services are classified as:
  - **Core**: cross-domain, foundational business capabilities
  - **Domain**: domain-specific business logic
  - **Platform**: infrastructure and operational capabilities
- **Boundary** indicates whether a service is internal or external to the CRM system.
- Separation guardrails:
  - **Notification Orchestrator** is only for user-facing delivery orchestration; **Communication Service** is only for CRM conversation tracking.
  - **Workflow Automation Service** handles business-rule orchestration; **Job Scheduler** handles time-based execution mechanics.
  - **Analytics & Reporting Service** owns metric semantics and report APIs; **Data Warehouse** owns persisted analytical storage.
  - **Activity Timeline Service** is the canonical interaction log; producers publish events but do not own timeline persistence.

## Service Catalog

| Layer | Service Name | Boundary | Responsibility (Single Owner) | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|---|
| Core | API Gateway | Internal | Authenticate/authorize API calls, route requests to internal services, enforce rate limits. | HTTP/gRPC requests, access tokens, client metadata | Routed requests, standardized API responses, rejection events | Identity & Access Service, Audit & Compliance Service |
| Core | Identity & Access Service | Internal | Manage users, roles, permissions, session/token lifecycle. | User credentials, SSO assertions, RBAC policy updates | Access/refresh tokens, auth decisions, identity events | Audit & Compliance Service |
| Core | Organization & Tenant Service | Internal | Manage tenant/account-level configuration, plan entitlements, and regional settings. | Tenant provisioning requests, plan assignments, config updates | Tenant profiles, feature-flag context, entitlement events | Billing & Subscription Service, Feature Flag Service |
| Core | Workflow Automation Service | Internal | Execute declarative business workflows and rule-triggered automations (non-temporal business orchestration). | Domain events, workflow definitions, rule conditions | Task executions, webhook calls, automation outcome events | Event Bus, Notification Orchestrator, Job Scheduler |
| Core | Notification Orchestrator | Internal | Build and dispatch user-facing in-app/email/SMS notifications from canonical templates and events (not CRM conversation state). | Notification commands, event payloads, user preferences | Sent notifications, delivery status events, failure events | Template Service, Email Delivery Provider, SMS Delivery Provider |
| Domain | Lead Management Service | Internal | Own lead capture, qualification state machine, assignment, and conversion trigger. | Web form submissions, imports, campaign attribution, rep actions | Lead records, qualification events, lead-to-contact/account conversion commands | Contact Service, Account Service, Opportunity Service, Activity Timeline Service |
| Domain | Contact Service | Internal | Own person-level customer records, lifecycle status, preferences, and deduplication. | Contact CRUD requests, merge requests, import files | Canonical contact records, merge events, preference snapshots | Data Quality Service, Activity Timeline Service |
| Domain | Account Service | Internal | Own company/customer account records, hierarchy, segmentation, and ownership. | Account CRUD requests, enrichment updates, ownership changes | Canonical account records, account hierarchy events | Data Quality Service, Territory & Assignment Service |
| Domain | Opportunity Service | Internal | Own pipeline opportunities, stage progression, forecasting fields, and close outcomes. | Opportunity updates, pricing context, qualification signals | Stage-change events, forecast records, win/loss outcomes | Product Catalog Service, Quote Service, Activity Timeline Service |
| Domain | Quote Service | Internal | Generate and manage commercial quotes, discounts, and approval state. | Opportunity context, product selections, discount rules | Quote documents, approval requests, accepted quote events | Product Catalog Service, Approval Service, Billing & Subscription Service |
| Domain | Activity Timeline Service | Internal | Store and expose immutable timeline of customer-facing interactions and system actions as the single system of record for timeline history. | Calls, emails, meetings, notes, domain events | Ordered activity feed, engagement metrics events | Event Bus |
| Domain | Communication Service | Internal | Track CRM-originated emails/calls/messages and their interaction metadata/conversation threads (excluding notification dispatch ownership). | Outbound message requests, inbound webhook events, call logs | Message records, reply/open/click events, conversation thread state, timeline publication events | Email Delivery Provider, Telephony Provider, Activity Timeline Service |
| Domain | Case Management Service | Internal | Own support case intake, triage, SLA state, and resolution workflow. | Case submissions, channel messages, priority rules | Case records, SLA breach events, resolution events | Knowledge Base Service, Notification Orchestrator, Activity Timeline Service |
| Domain | Knowledge Base Service | Internal | Manage support articles, taxonomy, and retrieval for support workflows. | Article drafts, publication commands, search queries | Published articles, article metadata, relevance signals | Search Index Service |
| Domain | Product Catalog Service | Internal | Own sellable products, pricing books, and packaging metadata used in sales flows. | Product updates, pricing policy changes | Product/pricing snapshots, catalog change events | Approval Service |
| Domain | Billing & Subscription Service | Internal | Manage customer subscriptions, invoice state mirrors, and payment status for CRM context. | Accepted quote events, external billing webhooks, plan changes | Subscription status, invoice summaries, delinquency events | Payment Gateway (External), Organization & Tenant Service |
| Domain | Territory & Assignment Service | Internal | Compute and apply ownership/territory assignment for leads, accounts, and opportunities. | Routing rules, rep capacity, geo/account attributes | Ownership assignments, reassignment events | Lead Management Service, Account Service, Opportunity Service |
| Domain | Analytics & Reporting Service | Internal | Produce curated operational/business metrics, dashboards, and scheduled reports (semantic metrics/reporting layer). | Domain events, query requests, reporting definitions | KPI datasets, dashboards, exported reports | Data Warehouse, Event Bus |
| Platform | Event Bus | Internal | Provide asynchronous event transport with durable pub/sub semantics. | Domain events, integration events | Event streams, delivery acknowledgements, dead-letter events | Schema Registry |
| Platform | Job Scheduler | Internal | Run delayed, recurring, and retryable background jobs (time-based execution engine only). | Job definitions, cron schedules, retry policies | Job execution events, task completions/failures | Event Bus |
| Platform | Search Index Service | Internal | Index CRM entities/content and serve low-latency full-text/filter search. | Entity change events, indexing jobs, search queries | Search results, index health metrics | Event Bus, Job Scheduler |
| Platform | Data Quality Service | Internal | Execute validation, normalization, deduplication signals, and survivorship policies. | Contact/account/lead upserts, merge candidates | Quality scores, canonicalization suggestions, duplicate alerts | Contact Service, Account Service, Lead Management Service |
| Platform | Approval Service | Internal | Centralize policy-based approvals (discounts, exceptions, access-sensitive changes). | Approval requests, policy rules, approver actions | Approval decisions, escalation events | Identity & Access Service, Notification Orchestrator |
| Platform | Audit & Compliance Service | Internal | Persist immutable audit trail for user/admin/data-access actions and policy checks. | Security-sensitive actions, admin changes, access decisions | Audit logs, compliance exports, anomaly alerts | Identity & Access Service, Event Bus |
| Platform | Feature Flag Service | Internal | Control runtime feature exposure and typed runtime configuration by tenant, role, and environment. | Flag definitions, targeting rules, configuration updates, evaluation calls | Flag evaluations, resolved configuration, rollout events | Organization & Tenant Service, Audit & Compliance Service |
| Platform | Template Service | Internal | Manage reusable notification/document templates with versioning and localization. | Template CRUD, localization updates, render requests | Rendered content, template version events | Search Index Service |
| Platform | Data Warehouse | Internal | Store analytics-ready historical data models for reporting and BI workloads (persistence layer only). | ETL/ELT loads, event streams, snapshot tables | Queryable marts, aggregate tables | Event Bus, Job Scheduler |
| External | Email Delivery Provider | External | Deliver outbound emails and emit delivery/open/click/bounce webhooks. | Email payloads, templates, recipient metadata | Delivery status webhooks, provider message IDs | Notification Orchestrator, Communication Service |
| External | SMS Delivery Provider | External | Deliver outbound SMS and emit delivery/failure webhooks. | SMS payloads, recipient numbers | Delivery receipts, failure webhooks | Notification Orchestrator |
| External | Telephony Provider | External | Provide call placement/recording and call event webhooks. | Dial requests, call control commands | Call records, call state events, recordings metadata | Communication Service |
| External | Payment Gateway | External | Process charges/refunds and emit payment lifecycle events. | Payment intents, capture/refund commands | Payment outcomes, settlement events, dispute events | Billing & Subscription Service |

## Capability Ownership Matrix (No Overlap)

| Capability | Single Owning Service |
|---|---|
| API ingress, routing, and rate-limiting | API Gateway |
| Authentication and authorization decisions | Identity & Access Service |
| Security/compliance audit evidence | Audit & Compliance Service |
| Tenant profile, entitlement, and regional config | Organization & Tenant Service |
| Runtime feature targeting and typed config evaluation | Feature Flag Service |
| Lead intake, qualification, and conversion trigger | Lead Management Service |
| Person/contact golden record lifecycle | Contact Service |
| Company/account golden record lifecycle and hierarchy | Account Service |
| Opportunity stage/forecast lifecycle | Opportunity Service |
| Quote construction, discounting, and quote approvals handoff | Quote Service |
| Territory and ownership assignment policy execution | Territory & Assignment Service |
| Support case intake, triage, SLA, resolution | Case Management Service |
| Support article authoring, publication, retrieval | Knowledge Base Service |
| Product/SKU and price-book definitions | Product Catalog Service |
| Subscription status and invoice/payment mirrors in CRM context | Billing & Subscription Service |
| CRM conversation threads and message interaction telemetry | Communication Service |
| Canonical customer activity timeline persistence/query | Activity Timeline Service |
| Cross-domain workflow/rule orchestration | Workflow Automation Service |
| User-facing notification dispatch orchestration | Notification Orchestrator |
| Async pub/sub transport semantics | Event Bus |
| Delayed/recurring/retryable execution mechanics | Job Scheduler |
| Entity/content full-text indexing and retrieval | Search Index Service |
| Validation/normalization/dedup quality scoring | Data Quality Service |
| Centralized policy-based approval workflow engine | Approval Service |
| Template versioning/localization/rendering | Template Service |
| Analytics storage marts and historical models | Data Warehouse |
| KPI semantics, dashboards, and report delivery | Analytics & Reporting Service |

## Boundary Summary

- **Internal services**: all Core, Domain, and Platform services except explicit provider integrations.
- **External services**: Email Delivery Provider, SMS Delivery Provider, Telephony Provider, Payment Gateway.
