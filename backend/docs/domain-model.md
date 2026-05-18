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
| FollowUp | Lead Management Service | Follow-up task enforcement record — tracks due date, escalation level, and rule type for every active lead. |
| Team | Identity & Access Service | Named group of users for routing, assignment, and visibility scoping. |
| TeamMembership | Identity & Access Service | User membership record within a team with role context. |
| Contact | Contact Service | Person-level customer record. |
| Account | Account Service | Company/customer account record. |
| AccountHierarchy | Account Service | Parent-child account linkage. |
| Partner | Partner Management Service | External organization participating in referral/resell/channel motions. |
| PartnerRelationship | Partner Management Service | Linkage between partner and account/opportunity with attribution scope. |
| PartnerAttribution | Partner Management Service | Time-bounded source-of-truth attribution for referred/sourced deals. |
| PartnerCommission | Partner Management Service | Commission ledger entry tied to closed-won attributed revenue. |
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
| UnifiedCustomerProfile | Customer 360 CDP Service | Cross-entity CDP aggregation linking all Lead/Contact/Account records for one real-world customer. |
| UnifiedIdentity | Customer 360 CDP Service | Identity resolution record — primary + all known emails/phones for a unified profile. |
| Territory | Territory & Assignment Service | Named geographic/logical territory with parent hierarchy and status. |
| TerritoryRule | Territory & Assignment Service | Assignment rule mapping subject criteria to an owner within a territory. |
| TerritoryAssignment | Territory & Assignment Service | Resolved ownership assignment for a subject (lead, account, user, team) within a territory. |
| Campaign | Campaign Service | Marketing campaign lifecycle record (draft → active → completed). |
| SegmentDefinition | Campaign Service | Rules-based audience segment over Lead or Contact entities. |
| SegmentRule | Campaign Service | Single field/operator/value clause within a segment definition. |
| CampaignLeadLink | Campaign Service | Membership link between a campaign and a lead. |
| CampaignContactLink | Campaign Service | Membership link between a campaign and a contact. |
| JourneyDefinition | Automation Journey Service | Multi-step automation journey triggered by a platform event. |
| JourneyStep | Automation Journey Service | Single action step within a journey (email, update, assign, delay). |
| JourneyInstance | Automation Journey Service | Runtime execution instance of a journey for a specific trigger event. |

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

### Team
- **Owner service:** Identity & Access Service
- **Fields:** `team_id (PK)`, `tenant_id (FK->Tenant)`, `name`, `description`, `owner_user_id (FK->User)`, `status`, `created_at`, `updated_at`
- **status values:** `active | inactive`
- **Relationships:**
  - `Team` N-N `User` (via `TeamMembership`)
  - `RoutingDecision` N-1 `Team` (optional routing target)
- **Tenant isolation fields:** `tenant_id`

### TeamMembership
- **Owner service:** Identity & Access Service
- **Fields:** `team_membership_id (PK)`, `tenant_id (FK->Tenant)`, `team_id (FK->Team)`, `user_id (FK->User)`, `role`, `joined_at`
- **role values:** `member | lead`
- **Relationships:** bridge table for `Team` N-N `User`
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
- **Status values:** `new | qualifying | nurturing | proposal | negotiation | won | lost | disqualified`
- **Status transition policy:**
  - Forward: `new → qualifying → nurturing → proposal → negotiation → won`
  - Early exit: any status → `lost | disqualified`
  - Terminal: `won`, `lost`, `disqualified` — no automatic reactivation (manual only with audit record)
  - Idle threshold breach: system marks lead `at_risk` and creates escalation task (does not change status)
  - See `docs/followup-enforcement-model.md` for enforcement rules per status.
- **Tenant isolation fields:** `tenant_id`

### LeadAssignment
- **Owner service:** Territory & Assignment Service
- **Fields:** `lead_assignment_id (PK)`, `tenant_id (FK->Tenant)`, `lead_id (FK->Lead, UNIQUE)`, `assigned_user_id (FK->User)`, `assignment_rule`, `assigned_at`
- **Relationships:** `Lead` 1-1 `LeadAssignment`, `User` 1-N `LeadAssignment`
- **Tenant isolation fields:** `tenant_id`

### FollowUp
- **Owner service:** Lead Management Service
- **Fields:** `followup_id (PK)`, `tenant_id (FK->Tenant)`, `lead_id (FK->Lead)`, `task_id (FK->Task, nullable)`, `owner_user_id (FK->User)`, `state`, `rule_type`, `escalation_level`, `generated_by`, `due_at`, `completed_at (nullable)`, `snoozed_until (nullable)`, `created_at`, `updated_at`
- **state values:** `pending | overdue | completed | snoozed | failed`
- **rule_type values:** `time_based | activity_based | inactivity_based`
- **escalation_level values:** `none | reminder | warning | escalated | reassigned`
- **generated_by values:** `scheduler | escalation_engine | system_repair`
- **Relationships:**
  - `Lead` 1-N `FollowUp`
  - `FollowUp` 0..1-1 `Task` (optional linked action task)
  - `User` 1-N `FollowUp` (owner)
- **Tenant isolation fields:** `tenant_id`
- **Note:** Managed exclusively by the Follow-Up Engine. Manual deletion is blocked; state transitions are system-enforced. See `docs/followup-enforcement-model.md`.

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

### Partner
- **Owner service:** Partner Management Service
- **Fields:** `partner_id (PK)`, `tenant_id (FK->Tenant)`, `partner_account_id (FK->Account, nullable)`, `partner_code`, `name`, `partner_type`, `status`, `tier`, `payout_terms`, `default_commission_plan_code`, `owner_user_id (FK->User)`, `created_at`, `updated_at`
- **Relationships:**
  - `Partner` 0..1-1 `Account` (partner has optional account master record)
  - `Partner` 1-N `PartnerRelationship`
  - `Partner` 1-N `PartnerAttribution`
  - `Partner` 1-N `PartnerCommission`
- **Tenant isolation fields:** `tenant_id`

### PartnerRelationship
- **Owner service:** Partner Management Service
- **Fields:** `partner_relationship_id (PK)`, `tenant_id (FK->Tenant)`, `partner_id (FK->Partner)`, `account_id (FK->Account, nullable)`, `opportunity_id (FK->Opportunity, nullable)`, `relationship_type`, `source_channel`, `effective_from`, `effective_to`, `status`, `created_by_user_id (FK->User)`, `created_at`, `updated_at`
- **Relationships:**
  - `Partner` 1-N `PartnerRelationship`
  - `Account` 0..N-1 `PartnerRelationship`
  - `Opportunity` 0..N-1 `PartnerRelationship`
- **Tenant isolation fields:** `tenant_id`

### PartnerAttribution
- **Owner service:** Partner Management Service
- **Fields:** `partner_attribution_id (PK)`, `tenant_id (FK->Tenant)`, `partner_id (FK->Partner)`, `opportunity_id (FK->Opportunity)`, `account_id (FK->Account)`, `attribution_type`, `attribution_model`, `attribution_weight`, `attribution_status`, `originated_lead_id (FK->Lead, nullable)`, `attributed_amount`, `currency`, `locked_at`, `created_at`, `updated_at`
- **Relationships:**
  - `Partner` 1-N `PartnerAttribution`
  - `Opportunity` 1-N `PartnerAttribution`
  - `Account` 1-N `PartnerAttribution`
  - `Lead` 0..N-1 `PartnerAttribution`
- **Tenant isolation fields:** `tenant_id`

### PartnerCommission
- **Owner service:** Partner Management Service
- **Fields:** `partner_commission_id (PK)`, `tenant_id (FK->Tenant)`, `partner_id (FK->Partner)`, `partner_attribution_id (FK->PartnerAttribution)`, `opportunity_id (FK->Opportunity)`, `order_id (FK->Order, nullable)`, `commission_plan_code`, `commission_rate`, `commission_base_amount`, `commission_amount`, `currency`, `status`, `eligible_at`, `approved_at`, `paid_at`, `created_at`, `updated_at`
- **Relationships:**
  - `Partner` 1-N `PartnerCommission`
  - `PartnerAttribution` 1-N `PartnerCommission` (adjustments/reversals preserve history)
  - `Opportunity` 1-N `PartnerCommission`
  - `Order` 0..N-1 `PartnerCommission`
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
- **channel_type values:** `whatsapp | email | sms | in_app | voice`
- **status values:** `open | active | pending_customer | resolved | closed | archived`
- **Relationships:**
  - `MessageThread` 1-N `Message`
  - `MessageThread` 1-N `RoutingDecision`
  - `Contact` 1-N `MessageThread`
  - `Account` 1-N `MessageThread`
- **Tenant isolation fields:** `tenant_id`

### RoutingDecision
- **Owner service:** Communication Service
- **Purpose:** Records which agent/team was assigned to a thread and by which rule
- **Fields:** `tenant_id`, `message_thread_id (FK->MessageThread)`, `assigned_user_id (FK->User, nullable)`, `assigned_team_id (FK->Team, nullable)`, `rule_code`, `assigned_at`
- **Tenant isolation fields:** `tenant_id`

### Message
- **Owner service:** Communication Service
- **Fields:** `message_id (PK)`, `tenant_id (FK->Tenant)`, `message_thread_id (FK->MessageThread)`, `direction`, `provider_message_id`, `sender`, `recipient`, `status`, `sent_at`, `delivered_at`, `opened_at`, `clicked_at`
- **Relationships:** `MessageThread` 1-N `Message`
- **Tenant isolation fields:** `tenant_id`

### Case (impl: Ticket)
- **Owner service:** Case Management Service
- **Implementation alias:** `src/ticket_management/entities.py` uses `Ticket` — same entity, different naming layer
- **Fields:** `case_id (PK)`, `tenant_id (FK->Tenant)`, `account_id (FK->Account)`, `contact_id (FK->Contact, nullable)`, `owner_user_id (FK->User)`, `subject`, `description`, `priority`, `status`, `created_at`, `response_due_at`, `resolution_due_at`, `first_responded_at`, `resolved_at`, `closed_at`
- **Status sequence:** `open → in_progress → resolved → closed`
- **SLA state:** `healthy | at_risk | breached` — derived from `response_due_at`/`resolution_due_at` vs now; `at_risk` when ≤20% of SLA window remains
- **Relationships:**
  - `Account` 1-N `Case`
  - `Contact` 1-N `Case`
  - `Case` 1-N `CaseComment`
  - `Case` 1-N `EscalationAuditRecord`
- **Tenant isolation fields:** `tenant_id`

### EscalationRule
- **Owner service:** Case Management Service
- **Purpose:** Deterministic time/condition-based SLA escalation triggers
- **Fields:** `rule_id (PK)`, `tenant_id (FK->Tenant)`, `level` (int, escalation tier), `name`, `route_to` (user/team/queue), `trigger` (sla_breach|response_overdue|custom), `threshold_minutes`, `condition_field`, `condition_op`, `condition_value`, `active`
- **Escalation action types:** `reassign | raise_priority | page_on_call | request_manager_review`
- **Tenant isolation fields:** `tenant_id`

### EscalationAuditRecord
- **Owner service:** Case Management Service
- **Purpose:** Immutable audit record for every escalation decision (who, why, when)
- **Fields:** `audit_id (PK)`, `ticket_id (FK->Case)`, `tenant_id`, `event_type`, `details (jsonb)`, `created_at`
- **Tenant isolation fields:** `tenant_id`

### CaseComment
- **Owner service:** Case Management Service
- **Fields:** `case_comment_id (PK)`, `tenant_id (FK->Tenant)`, `case_id (FK->Case)`, `author_user_id (FK->User)`, `is_internal`, `body`, `created_at`
- **Relationships:** `Case` 1-N `CaseComment`
- **Tenant isolation fields:** `tenant_id`

### KnowledgeArticle
- **Owner service:** Knowledge Base Service
- **Fields:** `knowledge_article_id (PK)`, `tenant_id (FK->Tenant)`, `title`, `slug`, `body_markdown`, `status`, `version`, `published_at`, `updated_at`, `categories (tuple[str])`
- **ARTICLE_CATEGORIES:** `getting_started | billing | integrations | troubleshooting | security | account_management`
- **Relationships:** optionally linked to `Case` via references in `ActivityEvent`/automation context (no hard FK)
- **Tenant isolation fields:** `tenant_id`

### Subscription
- **Owner service:** Billing & Subscription Service
- **Fields:** `subscription_id (PK)`, `tenant_id (FK->Tenant)`, `account_id (FK->Account)`, `quote_id (FK->Quote, nullable)`, `external_subscription_ref`, `plan_code`, `status`, `start_date`, `end_date`, `renewal_date`, `created_at`
- **Status sequence:** `draft → trialing → active → past_due → paused → canceled | expired`
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

### UnifiedCustomerProfile
- **Owner service:** Customer 360 CDP Service
- **Purpose:** CDP-level aggregation of all CRM records for a single real-world customer. One profile may span multiple Lead, Contact, and Account records created over time.
- **Fields:** `profile_id (PK)`, `tenant_id`, `merge_strategy`, `profile_version`, `lead_ids (array)`, `contact_ids (array)`, `account_ids (array)`, `activity_ids (array)`, `identity (embedded UnifiedIdentity)`
- **merge_strategy values:** `email_match | phone_match | manual | rule_based`
- **Relationships:**
  - `UnifiedCustomerProfile` N-N `Lead` (via lead_ids)
  - `UnifiedCustomerProfile` N-N `Contact` (via contact_ids)
  - `UnifiedCustomerProfile` N-N `Account` (via account_ids)
- **Tenant isolation fields:** `tenant_id`
- **Note:** Not stored as a traditional row — built as a materialised read model from identity resolution rules. `profile_version` increments on each re-merge.

### UnifiedIdentity
- **Owner service:** Customer 360 CDP Service
- **Purpose:** Identity resolution record — all known contact vectors for a unified profile, used to detect and link duplicate records
- **Fields:** `primary_email`, `primary_phone`, `all_emails (array)`, `all_phones (array)`
- **Embedded in:** `UnifiedCustomerProfile.identity`
- **Dedup link:** Works alongside `src/data_deduplication_engine/` — identity match triggers a `DuplicateCandidate` and ultimately a `MergeWorkflow` if auto_merge_safe

### Territory

*Added from src/territory_management overlay — 2026-04-02*

- **Owner service:** Territory & Assignment Service
- **Status values:** `active | inactive`
- **Fields:** `territory_id (PK)`, `tenant_id (FK->Tenant)`, `name`, `code`, `parent_territory_id (nullable FK->Territory)`, `level (int)`, `status`
- **Relationships:** `Territory` 1-N `Territory` (parent-child hierarchy); `Territory` 1-N `TerritoryRule`; `Territory` 1-N `TerritoryAssignment`
- **Tenant isolation fields:** `tenant_id`

### TerritoryRule

- **Owner service:** Territory & Assignment Service
- **SubjectType values:** `user | team | account | lead`
- **OwnerType values:** `user | team`
- **Fields:** `rule_id (PK)`, `tenant_id`, `territory_id (FK->Territory)`, `subject_type (SubjectType)`, `priority (int)`, `criteria (dict)`, `owner_type (OwnerType)`, `owner_id`
- **Tenant isolation fields:** `tenant_id`

### TerritoryAssignment

- **Owner service:** Territory & Assignment Service
- **Fields:** `assignment_id (PK)`, `tenant_id`, `subject_type (SubjectType)`, `subject_id`, `territory_id (FK->Territory)`, `owner_type (OwnerType)`, `owner_id`, `assignment_rule`, `assigned_at`
- **Tenant isolation fields:** `tenant_id`

---

### Campaign

*Added from src/campaigns overlay — 2026-04-02*

- **Owner service:** Campaign Service
- **Status values:** `draft | active | completed`
- **Fields:** `campaign_id (PK)`, `tenant_id (FK->Tenant)`, `owner_user_id (FK->User)`, `name`, `description`, `status (CampaignStatus)`, `segment_id (FK->SegmentDefinition)`, `starts_at`, `ends_at`, `created_at`, `updated_at`, `activated_at (nullable)`, `completed_at (nullable)`
- **Relationships:**
  - `Campaign` N-N `Lead` (via `CampaignLeadLink`)
  - `Campaign` N-N `Contact` (via `CampaignContactLink`)
  - `Campaign` 1-1 `SegmentDefinition`
- **Tenant isolation fields:** `tenant_id`

### SegmentDefinition

*Added from src/campaigns overlay — 2026-04-02*

- **Owner service:** Campaign Service
- **entity_type values:** `lead | contact`
- **Fields:** `segment_id (PK)`, `tenant_id (FK->Tenant)`, `name`, `description`, `entity_type (SegmentEntityType)`, `rules (SegmentRule[])`, `created_at`, `updated_at`
- **Relationships:** `SegmentDefinition` 1-N `SegmentRule` (embedded tuple)
- **Tenant isolation fields:** `tenant_id`

### SegmentRule

- **Embedded in:** `SegmentDefinition.rules`
- **Fields:** `field`, `operator`, `value` (str | int | float | bool)
- Represents a single AND-clause filter. Multiple rules are evaluated together to produce the audience set.

### CampaignLeadLink / CampaignContactLink

- **Purpose:** Membership link recording when a Lead or Contact was added to a campaign.
- **Fields:** `*_link_id (PK)`, `tenant_id`, `campaign_id (FK->Campaign)`, `lead_id / contact_id`, `membership_status`, `linked_at`
- **Tenant isolation fields:** `tenant_id`

### JourneyDefinition

*Added from src/automation_journeys overlay — 2026-04-02*

- **Owner service:** Automation Journey Service
- **Fields:** `journey_id (PK)`, `tenant_id (FK->Tenant)`, `name`, `trigger_event` (platform event name), `steps (JourneyStep[])`, `is_active`
- **Relationships:** `JourneyDefinition` 1-N `JourneyInstance`; `JourneyDefinition` 1-N `JourneyStep` (embedded)
- **Tenant isolation fields:** `tenant_id`

### JourneyStep

- **Embedded in:** `JourneyDefinition.steps`
- **Fields:** `step_id`, `action (StepAction)`, `config (dict)`, `delay_seconds`
- **StepAction values:** `email | update | assign | delay`

### JourneyInstance

- **Owner service:** Automation Journey Service
- **Status values:** `running | waiting | completed | failed | stopped`
- **Fields:** `instance_id (PK)`, `tenant_id`, `journey_id (FK->JourneyDefinition)`, `trigger_event`, `trigger_event_id`, `status (InstanceStatus)`, `current_step_index`, `started_at`, `waiting_until (nullable)`, `completed_at (nullable)`, `error_message (nullable)`, `execution_log`
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
| Partner -> PartnerRelationship | 1-N | `PartnerRelationship.partner_id` |
| Opportunity -> PartnerRelationship | 1-N (optional) | `PartnerRelationship.opportunity_id` |
| Opportunity -> PartnerAttribution | 1-N (optional) | `PartnerAttribution.opportunity_id` |
| Partner -> PartnerCommission | 1-N | `PartnerCommission.partner_id` |
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
| Lead -> FollowUp | 1-N | `FollowUp.lead_id` |
| Team <-> User | N-N | `TeamMembership` |

## Tenant Isolation Enforcement

- Every tenant-scoped entity includes mandatory `tenant_id`.
- All unique constraints should be composite with `tenant_id` where business keys are tenant-local (e.g., `User(email, tenant_id)`, `Product(sku, tenant_id)`, `FeatureFlag(flag_key, tenant_id)`).
- Cross-tenant FKs are disallowed: all FK joins must match on `tenant_id` in application and database constraints.
- Query patterns must include `tenant_id` predicates on all reads/writes.

## FK Cascade and Deletion Semantics

### On-Delete Actions

| Relationship | On-Delete Action | Rationale |
|---|---|---|
| Tenant → all tenant-scoped entities | RESTRICT (blocked) | Tenant deletion requires explicit data export + purge workflow |
| Lead → LeadAssignment | CASCADE | Assignment is meaningless without the lead |
| Lead → FollowUp | CASCADE | Follow-ups are lead-scoped; auto-removed |
| Account → Contact | SET NULL (`account_id`) | Contacts survive account deletion as orphaned records |
| Account → Opportunity | RESTRICT | Opportunities must be closed before account deletion |
| Quote → QuoteLineItem | CASCADE | Line items are quote-scoped |
| Order → (no children with hard FK) | — | Order is immutable after creation |
| Case → CaseComment | CASCADE | Comments are case-scoped |
| WorkflowDefinition → WorkflowExecution | SET NULL or RESTRICT | Executions are historical record; definitions may be archived |
| FeatureFlag → FeatureFlagRule | CASCADE | Rules are flag-scoped |

### Soft-Delete Convention

Entities that support soft-delete carry `deleted_at (nullable timestamp)`. A non-null `deleted_at` means the record is logically deleted but retained for audit and legal hold purposes.

Soft-delete applies to: `Lead`, `Contact`, `Account`, `Opportunity`, `Quote`, `Order`, `Case`, `KnowledgeArticle`, `Subscription`.

Hard-delete is never applied directly — records transition through soft-delete and are subject to retention policy (see `docs/data-governance-layer.md §2.3`).

### TerritoryRule Criteria Schema

The `criteria (dict)` field on `TerritoryRule` uses a structured filter expression:

```json
{
  "field": "account.industry | lead.source | contact.region | geo.country_code",
  "operator": "eq | in | not_in | starts_with | gt | lt",
  "value": "<string | string[] | number>"
}
```

Multiple criteria entries are AND-joined. Example: `{"field": "lead.source", "operator": "in", "value": ["whatsapp", "web"]}`.
