# CRM Domain Model

## Modeling Conventions (Deterministic Naming)

- Entity names use **PascalCase singular** (e.g., `Lead`, `Opportunity`).
- Field names use **snake_case**.
- Primary keys are `*_id` as UUIDs.
- Foreign keys use referenced entity name + `_id`.
- Tenant isolation is enforced with required `tenant_id` on all internal business entities (except explicit system-global reference entities where noted).

## Cross-Domain Entity Catalog

| Entity | Owner Service | Purpose |
|---|---|---|
| Tenant | Organization & Tenant Service | Top-level tenant/account container and settings. |
| TenantEntitlement | Organization & Tenant Service | Plan/feature entitlement state per tenant. |
| User | Identity & Access Service | Human identity record. |
| Role | Identity & Access Service | RBAC role definition. |
| Permission | Identity & Access Service | Fine-grained action/resource permission. |
| UserRole | Identity & Access Service | User-to-role mapping. |
| RolePermission | Identity & Access Service | Role-to-permission mapping. |
| SessionToken | Identity & Access Service | Access/refresh token lifecycle record. |
| Lead | Lead Management Service | Prospect prior to conversion. |
| LeadAssignment | Territory & Assignment Service | Current lead ownership assignment. |
| Contact | Contact Service | Person-level customer record. |
| Account | Account Service | Company/customer account record. |
| AccountHierarchy | Account Service | Parent-child account linkage. |
| Opportunity | Opportunity Service | Revenue opportunity in pipeline. |
| OpportunityLineItem | Opportunity Service | Product line details on opportunity. |
| Quote | Quote Service | Commercial quote and approval state. |
| QuoteLineItem | Quote Service | Product line details on quote. |
| Order | Order Service | Commercial order created from accepted quote. |
| Product | Product Catalog Service | Sellable product/SKU metadata. |
| PriceBook | Product Catalog Service | Named pricing context/book. |
| PriceBookEntry | Product Catalog Service | Product price in a given price book. |
| ApprovalRequest | Approval Service | Policy-based approval workflow state. |
| ActivityEvent | Activity Timeline Service | Immutable timeline event. |
| MessageThread | Communication Service | Conversation container for messages/calls. |
| Message | Communication Service | Individual outbound/inbound communication event. |
| Case | Case Management Service | Support case lifecycle record. |
| CaseComment | Case Management Service | Case discussion and internal/external notes. |
| KnowledgeArticle | Knowledge Base Service | Support knowledge content item. |
| Subscription | Billing & Subscription Service | Customer subscription context in CRM. |
| InvoiceSummary | Billing & Subscription Service | Invoice mirror/status snapshot. |
| PaymentEvent | Billing & Subscription Service | Payment lifecycle event mirror. |
| WorkflowDefinition | Workflow Automation Service | Declarative automation definition. |
| WorkflowExecution | Workflow Automation Service | Runtime execution instance. |
| NotificationTemplate | Template Service | Versioned template for notifications/docs. |
| Notification | Notification Orchestrator | Notification dispatch record and status. |
| FeatureFlag | Feature Flag Service | Runtime feature toggle definition. |
| FeatureFlagRule | Feature Flag Service | Targeting rule per feature flag. |
| AuditLog | Audit & Compliance Service | Immutable security/compliance log entry. |
| SearchDocument | Search Index Service | Indexed entity/document projection. |

---

## Entity Definitions

### Tenant
- **Owner service:** Organization & Tenant Service
- **Fields:** `tenant_id (PK)`, `name`, `status`, `region`, `timezone`, `default_locale`, `created_at`, `updated_at`
- **Relationships:**
  - `Tenant` 1-N `TenantEntitlement`
  - `Tenant` 1-N `User`
  - `Tenant` 1-N all tenant-scoped business entities
- **Tenant isolation fields:** `tenant_id` (self PK/root scope)

### TenantEntitlement
- **Owner service:** Organization & Tenant Service
- **Fields:** `entitlement_id (PK)`, `tenant_id (FK->Tenant)`, `plan_code`, `feature_code`, `limit_value`, `effective_from`, `effective_to`, `created_at`
- **Relationships:** `Tenant` 1-N `TenantEntitlement`
- **Tenant isolation fields:** `tenant_id`

### User
- **Owner service:** Identity & Access Service
- **Fields:** `user_id (PK)`, `tenant_id (FK->Tenant)`, `email`, `display_name`, `status`, `last_login_at`, `created_at`, `updated_at`
- **Relationships:**
  - `Tenant` 1-N `User`
  - `User` N-N `Role` (via `UserRole`)
  - `User` 1-N `SessionToken`
- **Tenant isolation fields:** `tenant_id`

### Role
- **Owner service:** Identity & Access Service
- **Fields:** `role_id (PK)`, `tenant_id (FK->Tenant)`, `name`, `description`, `is_system`, `created_at`
- **Relationships:**
  - `Role` N-N `Permission` (via `RolePermission`)
  - `User` N-N `Role` (via `UserRole`)
- **Tenant isolation fields:** `tenant_id`

### Permission
- **Owner service:** Identity & Access Service
- **Fields:** `permission_id (PK)`, `tenant_id (FK->Tenant)`, `resource`, `action`, `description`, `created_at`
- **Relationships:** `Role` N-N `Permission` (via `RolePermission`)
- **Tenant isolation fields:** `tenant_id`

### UserRole
- **Owner service:** Identity & Access Service
- **Fields:** `user_role_id (PK)`, `tenant_id (FK->Tenant)`, `user_id (FK->User)`, `role_id (FK->Role)`, `assigned_at`, `assigned_by_user_id (FK->User)`
- **Relationships:** bridge table for `User` N-N `Role`
- **Tenant isolation fields:** `tenant_id`

### RolePermission
- **Owner service:** Identity & Access Service
- **Fields:** `role_permission_id (PK)`, `tenant_id (FK->Tenant)`, `role_id (FK->Role)`, `permission_id (FK->Permission)`, `granted_at`
- **Relationships:** bridge table for `Role` N-N `Permission`
- **Tenant isolation fields:** `tenant_id`

### SessionToken
- **Owner service:** Identity & Access Service
- **Fields:** `session_token_id (PK)`, `tenant_id (FK->Tenant)`, `user_id (FK->User)`, `token_type`, `issued_at`, `expires_at`, `revoked_at`, `client_ip`, `user_agent`
- **Relationships:** `User` 1-N `SessionToken`
- **Tenant isolation fields:** `tenant_id`

### Lead
- **Owner service:** Lead Management Service
- **Fields:** `lead_id (PK)`, `tenant_id (FK->Tenant)`, `owner_user_id (FK->User)`, `source`, `status`, `score`, `email`, `phone`, `company_name`, `created_at`, `converted_at`
- **Relationships:**
  - `Lead` 1-1 `LeadAssignment` (current assignment)
  - `Lead` N-1 `User` (owner)
  - `Lead` 0..1-1 `Contact` (post-conversion)
  - `Lead` 0..1-1 `Account` (post-conversion)
  - `Lead` 0..1-1 `Opportunity` (optional conversion output)
- **Tenant isolation fields:** `tenant_id`

### LeadAssignment
- **Owner service:** Territory & Assignment Service
- **Fields:** `lead_assignment_id (PK)`, `tenant_id (FK->Tenant)`, `lead_id (FK->Lead, UNIQUE)`, `assigned_user_id (FK->User)`, `assignment_rule`, `assigned_at`
- **Relationships:** `Lead` 1-1 `LeadAssignment`, `User` 1-N `LeadAssignment`
- **Tenant isolation fields:** `tenant_id`

### Contact
- **Owner service:** Contact Service
- **Fields:** `contact_id (PK)`, `tenant_id (FK->Tenant)`, `account_id (FK->Account, nullable)`, `owner_user_id (FK->User)`, `first_name`, `last_name`, `email`, `phone`, `lifecycle_status`, `created_at`, `updated_at`
- **Relationships:**
  - `Account` 1-N `Contact`
  - `Contact` 1-N `Opportunity` (buyer/contact role, optional)
  - `Contact` 1-N `Case`
- **Tenant isolation fields:** `tenant_id`

### Account
- **Owner service:** Account Service
- **Fields:** `account_id (PK)`, `tenant_id (FK->Tenant)`, `owner_user_id (FK->User)`, `name`, `industry`, `segment`, `status`, `billing_address`, `created_at`, `updated_at`
- **Relationships:**
  - `Account` 1-N `Contact`
  - `Account` 1-N `Opportunity`
  - `Account` 1-N `Case`
  - `Account` 1-N `Subscription`
  - `Account` N-N `Account` (via `AccountHierarchy`)
- **Tenant isolation fields:** `tenant_id`

### AccountHierarchy
- **Owner service:** Account Service
- **Fields:** `account_hierarchy_id (PK)`, `tenant_id (FK->Tenant)`, `parent_account_id (FK->Account)`, `child_account_id (FK->Account)`, `relationship_type`, `created_at`
- **Relationships:** bridge for `Account` N-N `Account` hierarchy
- **Tenant isolation fields:** `tenant_id`

### Opportunity
- **Owner service:** Opportunity Service
- **Fields:** `opportunity_id (PK)`, `tenant_id (FK->Tenant)`, `account_id (FK->Account)`, `primary_contact_id (FK->Contact, nullable)`, `owner_user_id (FK->User)`, `name`, `stage`, `amount`, `close_date`, `forecast_category`, `is_closed`, `is_won`, `created_at`, `updated_at`
- **Relationships:**
  - `Account` 1-N `Opportunity`
  - `Contact` 1-N `Opportunity` (optional primary contact)
  - `Opportunity` 1-N `OpportunityLineItem`
  - `Opportunity` 1-N `Quote`
- **Tenant isolation fields:** `tenant_id`

### OpportunityLineItem
- **Owner service:** Opportunity Service
- **Fields:** `opportunity_line_item_id (PK)`, `tenant_id (FK->Tenant)`, `opportunity_id (FK->Opportunity)`, `product_id (FK->Product)`, `quantity`, `unit_price`, `discount_percent`, `total_price`
- **Relationships:** `Opportunity` 1-N `OpportunityLineItem`, `Product` 1-N `OpportunityLineItem`
- **Tenant isolation fields:** `tenant_id`

### Quote
- **Owner service:** Quote Service
- **Fields:** `quote_id (PK)`, `tenant_id (FK->Tenant)`, `opportunity_id (FK->Opportunity)`, `status`, `currency`, `subtotal`, `discount_total`, `tax_total`, `grand_total`, `valid_until`, `created_at`, `accepted_at`
- **Relationships:**
  - `Opportunity` 1-N `Quote`
  - `Quote` 1-N `QuoteLineItem`
  - `Quote` 0..N-1 `ApprovalRequest`
  - `Quote` 0..1-1 `Subscription` (on acceptance)
- **Tenant isolation fields:** `tenant_id`

### QuoteLineItem
- **Owner service:** Quote Service
- **Fields:** `quote_line_item_id (PK)`, `tenant_id (FK->Tenant)`, `quote_id (FK->Quote)`, `product_id (FK->Product)`, `quantity`, `list_price`, `discount_percent`, `net_price`
- **Relationships:** `Quote` 1-N `QuoteLineItem`, `Product` 1-N `QuoteLineItem`
- **Tenant isolation fields:** `tenant_id`

### Order
- **Owner service:** Order Service
- **Fields:** `order_id (PK)`, `tenant_id (FK->Tenant)`, `quote_id (FK->Quote)`, `opportunity_id (FK->Opportunity)`, `status`, `currency`, `subtotal`, `discount_total`, `tax_total`, `grand_total`, `ordered_at`, `created_at`
- **Relationships:**
  - `Quote` 0..1-1 `Order`
  - `Opportunity` 1-N `Order`
- **Tenant isolation fields:** `tenant_id`

### Product
- **Owner service:** Product Catalog Service
- **Fields:** `product_id (PK)`, `tenant_id (FK->Tenant)`, `sku`, `name`, `description`, `status`, `billing_type`, `created_at`, `updated_at`
- **Relationships:**
  - `Product` N-N `PriceBook` (via `PriceBookEntry`)
  - `Product` 1-N `OpportunityLineItem`
  - `Product` 1-N `QuoteLineItem`
- **Tenant isolation fields:** `tenant_id`

### PriceBook
- **Owner service:** Product Catalog Service
- **Fields:** `price_book_id (PK)`, `tenant_id (FK->Tenant)`, `name`, `currency`, `is_default`, `active_from`, `active_to`
- **Relationships:** `Product` N-N `PriceBook` (via `PriceBookEntry`)
- **Tenant isolation fields:** `tenant_id`

### PriceBookEntry
- **Owner service:** Product Catalog Service
- **Fields:** `price_book_entry_id (PK)`, `tenant_id (FK->Tenant)`, `price_book_id (FK->PriceBook)`, `product_id (FK->Product)`, `unit_price`, `min_quantity`, `max_quantity`, `effective_from`, `effective_to`
- **Relationships:** bridge for `Product` N-N `PriceBook`
- **Tenant isolation fields:** `tenant_id`

### ApprovalRequest
- **Owner service:** Approval Service
- **Fields:** `approval_request_id (PK)`, `tenant_id (FK->Tenant)`, `resource_type`, `resource_id`, `requested_by_user_id (FK->User)`, `assigned_approver_user_id (FK->User, nullable)`, `status`, `policy_code`, `requested_at`, `decided_at`
- **Relationships:**
  - `Quote` 0..N-1 `ApprovalRequest` (when `resource_type='quote'`)
  - `User` 1-N `ApprovalRequest` (requester/approver)
- **Tenant isolation fields:** `tenant_id`

### ActivityEvent
- **Owner service:** Activity Timeline Service
- **Fields:** `activity_event_id (PK)`, `tenant_id (FK->Tenant)`, `actor_user_id (FK->User, nullable)`, `entity_type`, `entity_id`, `event_type`, `event_time`, `payload_json`, `source_service`
- **Relationships:** polymorphic N-1 to timeline-enabled entities (`Lead`, `Contact`, `Account`, `Opportunity`, `Case`, `MessageThread`)
- **Tenant isolation fields:** `tenant_id`

### MessageThread
- **Owner service:** Communication Service
- **Fields:** `message_thread_id (PK)`, `tenant_id (FK->Tenant)`, `account_id (FK->Account, nullable)`, `contact_id (FK->Contact, nullable)`, `channel_type`, `subject`, `status`, `created_at`, `updated_at`
- **Relationships:**
  - `MessageThread` 1-N `Message`
  - `Contact` 1-N `MessageThread`
  - `Account` 1-N `MessageThread`
- **Tenant isolation fields:** `tenant_id`

### Message
- **Owner service:** Communication Service
- **Fields:** `message_id (PK)`, `tenant_id (FK->Tenant)`, `message_thread_id (FK->MessageThread)`, `direction`, `provider_message_id`, `sender`, `recipient`, `status`, `sent_at`, `delivered_at`, `opened_at`, `clicked_at`
- **Relationships:** `MessageThread` 1-N `Message`
- **Tenant isolation fields:** `tenant_id`

### Case
- **Owner service:** Case Management Service
- **Fields:** `case_id (PK)`, `tenant_id (FK->Tenant)`, `account_id (FK->Account)`, `contact_id (FK->Contact, nullable)`, `owner_user_id (FK->User)`, `subject`, `description`, `priority`, `status`, `sla_due_at`, `created_at`, `resolved_at`
- **Relationships:**
  - `Account` 1-N `Case`
  - `Contact` 1-N `Case`
  - `Case` 1-N `CaseComment`
- **Tenant isolation fields:** `tenant_id`

### CaseComment
- **Owner service:** Case Management Service
- **Fields:** `case_comment_id (PK)`, `tenant_id (FK->Tenant)`, `case_id (FK->Case)`, `author_user_id (FK->User)`, `is_internal`, `body`, `created_at`
- **Relationships:** `Case` 1-N `CaseComment`
- **Tenant isolation fields:** `tenant_id`

### KnowledgeArticle
- **Owner service:** Knowledge Base Service
- **Fields:** `knowledge_article_id (PK)`, `tenant_id (FK->Tenant)`, `title`, `slug`, `body_markdown`, `status`, `version`, `published_at`, `updated_at`
- **Relationships:** optionally linked to `Case` via references in `ActivityEvent`/automation context (no hard FK)
- **Tenant isolation fields:** `tenant_id`

### Subscription
- **Owner service:** Billing & Subscription Service
- **Fields:** `subscription_id (PK)`, `tenant_id (FK->Tenant)`, `account_id (FK->Account)`, `quote_id (FK->Quote, nullable)`, `external_subscription_ref`, `plan_code`, `status`, `start_date`, `end_date`, `renewal_date`, `created_at`
- **Relationships:**
  - `Account` 1-N `Subscription`
  - `Quote` 0..1-1 `Subscription`
  - `Subscription` 1-N `InvoiceSummary`
  - `Subscription` 1-N `PaymentEvent`
- **Tenant isolation fields:** `tenant_id`

### InvoiceSummary
- **Owner service:** Billing & Subscription Service
- **Fields:** `invoice_summary_id (PK)`, `tenant_id (FK->Tenant)`, `subscription_id (FK->Subscription)`, `external_invoice_ref`, `invoice_number`, `amount_due`, `amount_paid`, `currency`, `status`, `due_date`, `issued_at`
- **Relationships:** `Subscription` 1-N `InvoiceSummary`
- **Tenant isolation fields:** `tenant_id`

### PaymentEvent
- **Owner service:** Billing & Subscription Service
- **Fields:** `payment_event_id (PK)`, `tenant_id (FK->Tenant)`, `subscription_id (FK->Subscription, nullable)`, `invoice_summary_id (FK->InvoiceSummary, nullable)`, `external_payment_ref`, `event_type`, `amount`, `currency`, `event_time`, `status`
- **Relationships:**
  - `Subscription` 1-N `PaymentEvent`
  - `InvoiceSummary` 1-N `PaymentEvent`
- **Tenant isolation fields:** `tenant_id`

### WorkflowDefinition
- **Owner service:** Workflow Automation Service
- **Fields:** `workflow_definition_id (PK)`, `tenant_id (FK->Tenant)`, `name`, `trigger_event`, `condition_expression`, `action_definition_json`, `status`, `version`, `created_at`
- **Relationships:** `WorkflowDefinition` 1-N `WorkflowExecution`
- **Tenant isolation fields:** `tenant_id`

### WorkflowExecution
- **Owner service:** Workflow Automation Service
- **Fields:** `workflow_execution_id (PK)`, `tenant_id (FK->Tenant)`, `workflow_definition_id (FK->WorkflowDefinition)`, `trigger_entity_type`, `trigger_entity_id`, `status`, `started_at`, `completed_at`, `error_message`
- **Relationships:** `WorkflowDefinition` 1-N `WorkflowExecution`
- **Tenant isolation fields:** `tenant_id`

### NotificationTemplate
- **Owner service:** Template Service
- **Fields:** `notification_template_id (PK)`, `tenant_id (FK->Tenant)`, `template_key`, `channel_type`, `locale`, `version`, `subject_template`, `body_template`, `is_active`, `created_at`
- **Relationships:** `NotificationTemplate` 1-N `Notification`
- **Tenant isolation fields:** `tenant_id`

### Notification
- **Owner service:** Notification Orchestrator
- **Fields:** `notification_id (PK)`, `tenant_id (FK->Tenant)`, `template_id (FK->NotificationTemplate)`, `recipient_user_id (FK->User, nullable)`, `channel_type`, `target_address`, `status`, `provider_ref`, `requested_at`, `sent_at`, `failed_at`
- **Relationships:**
  - `NotificationTemplate` 1-N `Notification`
  - `User` 1-N `Notification`
- **Tenant isolation fields:** `tenant_id`

### FeatureFlag
- **Owner service:** Feature Flag Service
- **Fields:** `feature_flag_id (PK)`, `tenant_id (FK->Tenant)`, `flag_key`, `description`, `default_state`, `created_at`, `updated_at`
- **Relationships:** `FeatureFlag` 1-N `FeatureFlagRule`
- **Tenant isolation fields:** `tenant_id`

### FeatureFlagRule
- **Owner service:** Feature Flag Service
- **Fields:** `feature_flag_rule_id (PK)`, `tenant_id (FK->Tenant)`, `feature_flag_id (FK->FeatureFlag)`, `target_type`, `target_id`, `rule_expression`, `rollout_percentage`, `priority`, `created_at`
- **Relationships:** `FeatureFlag` 1-N `FeatureFlagRule`
- **Tenant isolation fields:** `tenant_id`

### AuditLog
- **Owner service:** Audit & Compliance Service
- **Fields:** `audit_log_id (PK)`, `tenant_id (FK->Tenant)`, `actor_user_id (FK->User, nullable)`, `action`, `resource_type`, `resource_id`, `result`, `ip_address`, `user_agent`, `occurred_at`, `metadata_json`
- **Relationships:** polymorphic N-1 to audited resources across all domains
- **Tenant isolation fields:** `tenant_id`

### SearchDocument
- **Owner service:** Search Index Service
- **Fields:** `search_document_id (PK)`, `tenant_id (FK->Tenant)`, `entity_type`, `entity_id`, `title`, `body_text`, `tags_json`, `indexed_at`, `last_source_update_at`
- **Relationships:** polymorphic projection of searchable entities (`Contact`, `Account`, `Lead`, `Opportunity`, `Case`, `KnowledgeArticle`, `MessageThread`)
- **Tenant isolation fields:** `tenant_id`

---

## Relationship Consistency Matrix

| Relationship | Cardinality | Enforced By |
|---|---|---|
| Tenant -> User | 1-N | `User.tenant_id` |
| User <-> Role | N-N | `UserRole` |
| Role <-> Permission | N-N | `RolePermission` |
| Lead -> LeadAssignment | 1-1 | `LeadAssignment.lead_id UNIQUE` |
| Account -> Contact | 1-N | `Contact.account_id` |
| Account -> Opportunity | 1-N | `Opportunity.account_id` |
| Opportunity -> OpportunityLineItem | 1-N | `OpportunityLineItem.opportunity_id` |
| Opportunity -> Quote | 1-N | `Quote.opportunity_id` |
| Quote -> QuoteLineItem | 1-N | `QuoteLineItem.quote_id` |
| Product <-> PriceBook | N-N | `PriceBookEntry` |
| Account <-> Account (hierarchy) | N-N | `AccountHierarchy` |
| Quote -> ApprovalRequest | 1-N (optional) | `ApprovalRequest.resource_type/resource_id` |
| MessageThread -> Message | 1-N | `Message.message_thread_id` |
| Case -> CaseComment | 1-N | `CaseComment.case_id` |
| Account -> Subscription | 1-N | `Subscription.account_id` |
| Subscription -> InvoiceSummary | 1-N | `InvoiceSummary.subscription_id` |
| Subscription -> PaymentEvent | 1-N | `PaymentEvent.subscription_id` |
| WorkflowDefinition -> WorkflowExecution | 1-N | `WorkflowExecution.workflow_definition_id` |
| NotificationTemplate -> Notification | 1-N | `Notification.template_id` |
| FeatureFlag -> FeatureFlagRule | 1-N | `FeatureFlagRule.feature_flag_id` |

## Tenant Isolation Enforcement

- Every tenant-scoped entity includes mandatory `tenant_id`.
- All unique constraints should be composite with `tenant_id` where business keys are tenant-local (e.g., `User(email, tenant_id)`, `Product(sku, tenant_id)`, `FeatureFlag(flag_key, tenant_id)`).
- Cross-tenant FKs are disallowed: all FK joins must match on `tenant_id` in application and database constraints.
- Query patterns must include `tenant_id` predicates on all reads/writes.
