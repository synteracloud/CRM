# CRM Capability Matrix

This matrix maps each CRM feature to its owning/internal participating services and explicit service dependencies.

Coverage rules applied:
- No orphan features: every listed feature is mapped to one or more services.
- Full coverage: features span all canonical CRM domains from the service map/workflow catalog.

| Feature | Owning / Participating Services | Dependencies |
|---|---|---|
| Tenant provisioning & entitlement | Organization & Tenant Service; Feature Flag Service; Identity & Access Service; Workflow Automation Service; Analytics & Reporting Service; Audit & Compliance Service; Search Index Service | Billing & Subscription Service; Event Bus; Job Scheduler |
| Identity & access lifecycle | Identity & Access Service; Notification Orchestrator; Feature Flag Service; Analytics & Reporting Service; Audit & Compliance Service | Template Service; Email Delivery Provider; SMS Delivery Provider |
| Lead intake, assignment, conversion | Lead Management Service; Territory & Assignment Service; Data Quality Service; Activity Timeline Service; Notification Orchestrator; Contact Service; Account Service; Opportunity Service; Workflow Automation Service; Analytics & Reporting Service; Search Index Service | Contact Service; Account Service; Opportunity Service; Event Bus; Job Scheduler; Email Delivery Provider; SMS Delivery Provider |
| Contact management & deduplication | Contact Service; Data Quality Service; Activity Timeline Service; Search Index Service; Analytics & Reporting Service; Audit & Compliance Service | Data Quality Service; Activity Timeline Service; Event Bus; Job Scheduler |
| Account management & hierarchy | Account Service; Territory & Assignment Service; Data Quality Service; Activity Timeline Service; Search Index Service; Analytics & Reporting Service | Data Quality Service; Territory & Assignment Service; Event Bus; Job Scheduler |
| Opportunity pipeline & close outcomes | Opportunity Service; Activity Timeline Service; Territory & Assignment Service; Workflow Automation Service; Notification Orchestrator; Analytics & Reporting Service | Product Catalog Service; Quote Service; Event Bus; Job Scheduler; Template Service |
| Quote, approval, acceptance | Quote Service; Approval Service; Notification Orchestrator; Activity Timeline Service; Workflow Automation Service; Analytics & Reporting Service; Audit & Compliance Service; Billing & Subscription Service; Opportunity Service | Product Catalog Service; Approval Service; Billing & Subscription Service; Identity & Access Service; Template Service; Email Delivery Provider; SMS Delivery Provider |
| Subscription, invoicing, payments | Billing & Subscription Service; Organization & Tenant Service; Notification Orchestrator; Workflow Automation Service; Analytics & Reporting Service; Search Index Service; Audit & Compliance Service | Payment Gateway (External); Organization & Tenant Service; Event Bus; Job Scheduler; Template Service |
| Case management & SLA | Case Management Service; Notification Orchestrator; Activity Timeline Service; Search Index Service; Workflow Automation Service; Analytics & Reporting Service; Knowledge Base Service; Audit & Compliance Service | Knowledge Base Service; Activity Timeline Service; Event Bus; Job Scheduler; Template Service |
| Knowledge base authoring & retrieval | Knowledge Base Service; Search Index Service; Analytics & Reporting Service | Search Index Service; Event Bus; Job Scheduler |
| Communication tracking (email/call/message) | Communication Service; Activity Timeline Service; Notification Orchestrator; Analytics & Reporting Service | Email Delivery Provider; Telephony Provider; Activity Timeline Service; Event Bus; Template Service |
| Notifications & templating | Notification Orchestrator; Template Service; Communication Service | Template Service; Email Delivery Provider; SMS Delivery Provider |
| Product catalog & pricing context | Product Catalog Service; Quote Service; Opportunity Service; Approval Service | Approval Service |
| Territory & ownership assignment | Territory & Assignment Service; Lead Management Service; Account Service; Opportunity Service | Lead Management Service; Account Service; Opportunity Service |
| Workflow automation & scheduled jobs | Workflow Automation Service; Job Scheduler; Event Bus | Event Bus; Notification Orchestrator; Job Scheduler; Schema Registry |
| Search & discovery | Search Index Service; Lead Management Service; Contact Service; Account Service; Case Management Service; Knowledge Base Service; Billing & Subscription Service | Event Bus; Job Scheduler |
| Analytics, dashboards, and BI | Analytics & Reporting Service; Data Warehouse | Event Bus; Data Warehouse |
| Audit, compliance, and governance | Audit & Compliance Service; Identity & Access Service; Approval Service; Billing & Subscription Service | Identity & Access Service; Event Bus |

## Coverage Checklist

- Identity/security: covered (`Identity & access lifecycle`, `Audit, compliance, and governance`).
- Tenant/configuration: covered (`Tenant provisioning & entitlement`).
- Lead-to-revenue: covered (`Lead intake...`, `Opportunity...`, `Quote...`, `Subscription...`).
- Customer master data: covered (`Contact management...`, `Account management...`).
- Support: covered (`Case management & SLA`, `Knowledge base...`).
- Communications: covered (`Communication tracking`, `Notifications & templating`).
- Platform capabilities: covered (`Workflow automation...`, `Search & discovery`, `Analytics...`).
