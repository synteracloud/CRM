Status: Draft
Authority Level: Critical
Last Reviewed: 2026-06-21
Owner: Shared

---

# DOMAIN MODEL — Pakistan CRM OS

## Overview

Pakistan CRM OS has 20 database domains (PostgreSQL schemas) containing 37+ named entities (30 with confirmed db/*/schema.sql evidence; 7+ inferred from gateway code — see D-003 in AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS). The Forecast domain adds 1 computed entity (not persisted). All persistent entities are tenant-scoped — every row includes `tenant_id` as a foreign key, enforced at the gateway middleware layer.

Source: ENTITY_INVENTORY.md (U1), db/*/schema.sql, gateway/routes/v1-*.routes.js, src/*/entities.py

---

## Entity Relationship Map (Full)

```
Tenant (org_tenant_db)
  ├── Users (identity_auth_db)
  │     ├── → Roles (via user_roles)
  │     │     └── → Permissions/Scopes (via role_permissions)
  │     ├── → Sessions
  │     └── → RefreshTokens
  │
  ├── Leads (lead_management_db)
  │     ├── → LeadAssignments (every owner reassignment)
  │     ├── → LeadHistory (immutable field change log)
  │     ├── → FollowupTasks (exactly 1 canonical pending per lead)
  │     ├── belongs to → Contact
  │     └── optionally belongs to → Campaign
  │
  ├── Contacts (contact_account_db)
  │     └── optionally belongs to → Account
  │
  ├── Accounts (contact_account_db)
  │     ├── → ChurnPrediction (AI)
  │     └── → CLVEstimate (AI)
  │
  ├── Opportunities (opportunity_db)
  │     ├── → OpportunityLineItems
  │     ├── belongs to → Account (optional)
  │     └── belongs to → Contact (optional)
  │
  ├── Quotes (quote_order_db)
  │     └── accepted → Orders
  │           └── linked → Invoices
  │
  ├── Invoices (transaction_db)
  │     ├── → Payments
  │     └── → Collections
  │
  ├── Subscriptions (transaction_db)
  │     └── belongs to → Account
  │
  ├── Cases (case_ticket_db)
  │     ├── → CaseComments
  │     ├── → CaseEscalations
  │     ├── → linked KnowledgeArticles (cross-domain link)
  │     ├── belongs to → Contact (optional)
  │     ├── belongs to → Account (optional)
  │     ├── belongs to → Lead (optional)
  │     └── assigned to → SupportQueue
  │
  ├── Conversations (messaging_db)
  │     ├── → Messages
  │     ├── → Handoffs
  │     ├── assigned to → User (agent)
  │     └── belongs to → InboxQueue
  │
  ├── WorkflowDefinitions (workflow_db)
  │     └── → WorkflowExecutions
  │           └── → WorkflowStepRecords
  │
  ├── Forecast (computed from opportunity_db — not persisted)
  │     └── derived from → Opportunities (stage/forecast_category aggregation)
  │
  ├── Campaigns (campaign_db)
  │     └── → Segments (criteria-based contact lists)
  │
  ├── KnowledgeArticles (knowledge_db)
  │
  ├── Territories (territory_db)
  │     └── → TerritoryRules
  │
  ├── Partners (contact_account_db.partners)
  │     ├── → CommissionLedger entries
  │     └── → DealRegistrations
  │
  ├── AuditLog (audit_compliance_db) — IMMUTABLE hash-chain
  ├── FeatureFlags (feature_flag_db) — dual-approval toggle
  │
  ├── Activities (activity_task_db) — call/whatsapp/email/meeting/note
  ├── Tasks (activity_task_db) — general task entity
  │
  └── AI Domain (intelligence_db)
        ├── LeadScores
        ├── ChurnPredictions
        ├── CLVEstimates
        ├── CopilotSuggestions
        └── ScoringModels (read-only registry)
```

---

## Core Domain Entities

### Identity & Auth Domain (identity_auth_db)

**User**
- Description: A human or service account user within a tenant
- Key fields: user_id (UUID PK), tenant_id (UUID FK NOT NULL), email (TEXT UNIQUE per tenant), password_hash (TEXT nullable for SSO), full_name (TEXT), status (active/suspended/deactivated), last_login_at, created_at
- Relationships: belongs to Tenant; has many Roles; has many Sessions; has many RefreshTokens
- Key business rule: email is unique per tenant (not globally)

**Role**
- Description: A named set of permissions scoped to a tenant; system roles are predefined and not deletable
- Key fields: role_id (UUID PK), tenant_id (UUID FK), name (TEXT UNIQUE per tenant), is_system (BOOL)
- Relationships: has many Permissions via role_permissions; has many Users via user_roles
- Key business rule: system roles (is_system=true) cannot be deleted via DELETE /roles

**Permission (Scope)**
- Description: A capability string (e.g. "leads.read") — defined in code, not user-mutable
- Key fields: permission_id (UUID PK), scope (TEXT UNIQUE e.g. "leads.read")
- Key business rule: scope list is frozen at rbac-scopes.js; 91 scopes defined; new scopes require code change

**Session**
- Description: An active login session with IP tracking
- Key fields: session_id (UUID PK), user_id (FK), tenant_id (FK), token_hash (UNIQUE), ip_address, expires_at, revoked_at
- Key business rule: revocation writes to Redis JTI blocklist immediately; gateway checks blocklist on every request

**RefreshToken**
- Description: A rotating 7-day token for silent JWT renewal
- Key fields: token_id (UUID PK), token_hash (UNIQUE), expires_at, rotated_at, revoked_at
- Key business rule: single-use rotation — token is invalidated immediately on use and a new one is issued

---

### Tenant Domain (org_tenant_db)

**Tenant**
- Description: An isolated business workspace; the root of all domain data
- Key fields: tenant_id (UUID PK), name (TEXT), slug (TEXT UNIQUE), status (active), plan (starter/…), region (pk-south/…)
- Key business rule: created via POST /auth/register; triggers activation engine seed; cannot be deleted via API

---

### Lead Domain (lead_management_db)

**Lead**
- Description: A prospective customer or opportunity in the sales pipeline
- Key fields: lead_id (UUID PK), tenant_id (UUID FK NOT NULL), contact_id (UUID NOT NULL), owner_id (UUID NOT NULL — mandatory), stage (new/qualifying/nurturing/proposal/negotiation/won/lost/disqualified), status (open/working/idle/closed), priority (hot/warm/cold), source (whatsapp/web/import/manual/referral/campaign), version_no (INT)
- Relationships: belongs to Contact; owned by User; has many LeadAssignments, LeadHistory, FollowupTasks; optionally belongs to Campaign
- Key business rules: owner_id is mandatory (not nullable); soft-delete only (repo.softDelete sets deleted_at); version_no supports optimistic concurrency

**LeadAssignment**
- Description: Immutable record of every owner reassignment for a lead
- Key fields: assignment_id (UUID PK), lead_id (FK CASCADE), owner_id (UUID NOT NULL), assigned_by (UUID nullable — NULL=system), reason (TEXT), assigned_at
- Key business rule: created automatically; cannot be modified

**LeadHistory**
- Description: Immutable field-level change log for every Lead update
- Key fields: history_id (UUID PK), lead_id (FK CASCADE), field_name, old_value, new_value, changed_by (UUID NOT NULL), changed_at
- Key business rule: append-only; no UPDATE or DELETE allowed on this table

**FollowupTask**
- Description: A scheduled follow-up action for a lead with 4-level escalation
- Key fields: task_id (UUID PK), lead_id (UUID FK), owner_id (UUID), state (pending/overdue/completed), due_at (TIMESTAMPTZ NOT NULL), rule_type (TimeBased/ActivityBased/InactivityBased), escalation_level (none/reminder/warning/escalated/reassigned), is_canonical (BOOL), action_type (Call/WhatsApp/Reminder)
- Invariant: **Exactly one canonical pending task per lead** — enforced by DB unique constraint

---

### Contact Domain (contact_account_db)

**Contact**
- Description: A known person (customer, prospect, or partner contact)
- Key fields: contact_id (UUID PK), display_name (TEXT), phone_e164 (E.164 format), email (nullable), account_id (nullable FK), tags (TEXT[]), open_cases (INT), completeness_score (INT 0–100), source (whatsapp/web/import/manual), last_touchpoint (DATE)
- Key business rules: phone_e164 must be valid E.164 format (+923xx...); completeness_score drives health dashboard
- CRUD: C (POST /contacts, POST /contacts/import), R (GET /contacts, GET /contacts/:id, GET /contacts/export), U (PATCH /contacts/:id), D (DELETE /contacts/:id — SECURITY GAP: contacts.delete scope absent from rbac-scopes.js; endpoint inaccessible to all roles until scope is added — see H-002 in REMEDIATION_REPORT.md)

**Account**
- Description: A business entity (company); parent of Contacts and Opportunities
- Key fields: account_id (UUID PK), name (TEXT), tier (TEXT), industry (TEXT), balance (NUMERIC PKR)
- Relationships: has many Contacts; has many Opportunities; has AI ChurnPrediction; has AI CLVEstimate

---

### Opportunity / Sales Domain (opportunity_db)

**Opportunity**
- Description: A qualified sales deal with pipeline stage and financial value
- Key fields: opportunity_id (UUID PK), owner_id (UUID NOT NULL), amount (NUMERIC PKR nullable), stage (qualification/discovery/proposal/negotiation/closed_won/closed_lost), probability (INT 0–100), forecast_category (pipeline/best_case/commit/closed/omitted), version_no (INT)
- Relationships: belongs to Account; belongs to Contact; has many OpportunityLineItems
- Key business rules: stage transitions emit opportunity.stage.changed.v1 event; version_no enforces OCC; closed_lost is terminal (no DELETE exposed)

**OpportunityLineItem**
- Description: A product or service line added to an opportunity
- Key fields: line_item_id (UUID PK), opportunity_id (FK), product_id (UUID NOT NULL), quantity (INT), unit_price (NUMERIC PKR), discount_pct (NUMERIC)

---

### CPQ Domain (quote_order_db)

**Quote**
- Description: A priced proposal sent to an Account/Contact; may require approval
- Key fields: quote_id (UUID PK), opportunity_id (FK), line_items (JSONB array), discount_pct (NUMERIC), requires_approval (BOOL — auto-set if discount_pct > 10%), approval_history (JSONB), status (draft/sent/approved/rejected/expired)
- Key business rule: discount_pct > 10% triggers approval routing via rule_engine; acceptance creates an Order

**Order**
- Description: A confirmed sale created from an accepted Quote
- Key fields: order_id (UUID PK), quote_id (FK), total (NUMERIC PKR), status (processing/fulfilled/cancelled), linked_invoice_id (UUID nullable)
- Key business rule: immutable post-fulfilment (enforced by rule_engine)

---

### Finance Domain (transaction_db)

**Invoice**
- Description: A bill issued to an Account for payment
- Key fields: invoice_id (UUID PK), account_id (FK), contact_id (FK), total_amount (NUMERIC PKR), paid_amount, balance_amount, status (draft/sent/paid/overdue/partially_paid/cancelled), is_overdue (BOOL)

**Subscription**
- Description: A recurring billing relationship with an Account
- Key fields: subscription_id (UUID PK), account_id (FK), plan_name, status (draft/trialing/active/past_due/paused/cancelled/expired), mrr (NUMERIC PKR), arr (NUMERIC PKR), billing_cycle (monthly/annual), next_billing_date

**Payment**
- Description: A payment against an Invoice (JazzCash or Easypaisa)
- Key fields: payment_id (UUID PK), invoice_id (FK), amount (NUMERIC PKR), method (jazzcash/easypaisa/bank_transfer), status (pending/completed/failed/reversed), stub_mode (BOOL)
- Key business rule: JazzCash and Easypaisa adapters are in stub_mode=True until P-016 credentials received

**Collection**
- Description: An overdue invoice tracked for active collection outreach
- Key fields: collection_id (UUID PK), invoice_id (FK), amount_due (NUMERIC PKR), days_overdue (INT), status (pending/contacted/promised/paid/escalated/written_off)

---

### Support Domain (case_ticket_db)

**Case**
- Description: A customer support request with SLA tracking and full lifecycle management
- Key fields: case_id (UUID PK), case_number (TEXT e.g. CAS-2026-000001), status (OPEN/ASSIGNED/IN_PROGRESS/WAITING_ON_CUSTOMER/RESOLVED/ESCALATED/CLOSED), priority (critical/high/medium/low), sla_tier (tier_1_critical/tier_2_high/tier_3_standard/tier_4_low), version_no (INT), escalation_level (INT 0–3)
- SLA defaults: tier_1_critical: 1h response/8h resolution; tier_2_high: 4h/24h; tier_3_standard: 8h/72h; tier_4_low: 24h/168h
- State machine: OPEN→ASSIGNED|CLOSED; ASSIGNED→IN_PROGRESS|OPEN|ESCALATED; IN_PROGRESS→WAITING_ON_CUSTOMER|RESOLVED|ESCALATED; RESOLVED→CLOSED|IN_PROGRESS; CLOSED→OPEN (14-day window only)
- Key business rules: version_no enforces OCC (409 CONFLICT on stale); reopen blocked after 14 days; first customer_reply auto-transitions ASSIGNED→IN_PROGRESS

**CaseComment**
- Description: A message or note on a case (internal or customer-visible)
- Key fields: comment_id (UUID PK), case_id (FK), comment_type (internal_note/customer_reply/resolution/status_change/escalation_note), is_visible_to_customer (BOOL)

**CaseEscalation**
- Description: An immutable escalation event on a case
- Key fields: escalation_id (UUID PK), case_id (FK), escalation_level (INT), escalation_reason (sla_first_response_breach/sla_resolution_breach/customer_request/manager_override)

**SupportQueue**
- Description: A routing pool for case assignment
- Key fields: queue_id (UUID PK), name, routing_strategy (round_robin/least_loaded/manual), sla_tier_default, skill_tags (TEXT[]), is_active (BOOL)

---

### Inbox / Communication Domain (messaging_db)

**Conversation**
- Description: A WhatsApp or email conversation thread with a Contact
- Key fields: conversation_id (UUID PK), contact_phone (E.164), channel (whatsapp/email/sms), state (open/resolved/closed), assigned_agent_id (nullable), intent (payment_query/follow_up_response/lead_inquiry/support_request), unread_count (INT), handoff_count (INT)

**Message**
- Description: A single message in a Conversation
- Key fields: message_id (UUID PK), conversation_id (FK), direction (inbound/outbound), text (TEXT), occurred_at

**Handoff**
- Description: An immutable record of conversation transfer between agents
- Key fields: handoff_id (UUID PK), from_agent_id, to_agent_id, handoff_reason (agent_unavailable/capacity_exceeded/skill_match/manual/escalation), initiated_by

**AgentPresence**
- Description: Real-time agent availability status with capacity tracking
- Key fields: agent_id (UUID PK), status (online/away/busy/offline), open_conversation_count (INT), max_concurrent (INT default 10)
- Key business rule: claim fails if open_conversation_count >= max_concurrent

**InboxQueue**
- Description: A routing pool for conversations with configurable strategy
- Key fields: queue_id (UUID PK), routing_strategy (round_robin/least_loaded/claim_first/skill_based), auto_assign (BOOL), skill_tags (TEXT[])

---

### Workflow Domain (workflow_db)

**WorkflowDefinition**
- Description: A named event-triggered automation workflow with step DSL
- Key fields: workflow_id (UUID PK), workflow_key (TEXT slug), status (draft/active/paused/archived), trigger_events (TEXT[]), steps_dsl (JSONB array), max_retries (INT default 3), is_system (BOOL)
- Key business rule: is_system=true blocks PATCH (403 FORBIDDEN); archive is terminal

**WorkflowExecution**
- Description: A single run of a WorkflowDefinition triggered by an event
- Key fields: execution_id (UUID PK), workflow_id (FK), trigger_event (TEXT), status (running/succeeded/failed/retrying/cancelled), parent_execution_id (UUID nullable — for retries)
- Key business rule: retry creates a NEW execution (child); original marked 'retrying'

**WorkflowStepRecord**
- Description: Step-level execution trace with input/output data per step
- Key fields: step_record_id (UUID PK), execution_id (FK), step_index, step_type (condition/action/notification), status (succeeded/failed), input_data (JSONB), output_data (JSONB), duration_ms (INT)

---

### AI / Intelligence Domain (intelligence_db)

**LeadScore**
- Description: Rule-based lead quality score for a Lead
- Key fields: score (INT 0–100), score_band (hot/warm/cold/disqualified), trend (rising/stable/falling), confidence_score (FLOAT 0–1), top_drivers (JSONB), is_stale (BOOL)
- Note: model is rule_based — no ML inference provider

**ChurnPrediction**
- Description: Rule-based churn risk assessment for an Account
- Key fields: churn_probability (FLOAT 0–1), risk_band (high/medium/low), recommended_action (TEXT), is_stale (BOOL)

**CLVEstimate**
- Description: Customer Lifetime Value estimate for an Account over 24 months
- Key fields: estimated_clv (NUMERIC PKR), clv_horizon_months (INT), confidence_score (FLOAT), is_stale (BOOL)

**CopilotSuggestion**
- Description: An AI-generated advisory action item for a user
- Key fields: suggestion_type (follow_up_overdue/deal_nudge/risk_flag/next_action/stale_deal/sla_breach_alert), priority (urgent/high/medium/low), entity_type (lead/account/case), entity_id (UUID), is_dismissed (BOOL), is_actioned (BOOL)

**ScoringModel**
- Description: Registry of AI model definitions (read-only)
- Key fields: model_key (TEXT PK), algorithm (rule_based/ml), recompute_interval_hours (INT), is_active (BOOL)
- Current models: lead_score_v1, churn_predict_v1, clv_estimate_v1 (all rule_based)

---

### Forecasting Domain (computed from opportunity_db)

**Forecast**
- Description: A computed pipeline forecast aggregating Opportunity data by stage, forecast category, and close month. Not a persisted entity — generated at query time from current Opportunity records.
- Key fields (response shape): period (TEXT — "current_quarter"), generated_at (TIMESTAMPTZ), weighted_value (NUMERIC PKR), by_category (JSONB — pipeline/best_case/commit/closed totals), stage_breakdown (JSONB array — per-stage count/value/weighted)
- Source: `backend/gateway/routes/v1-forecasts.routes.js`, `backend/gateway/services/forecasting.js`
- Forecast category weights (from forecasting.js): pipeline=0.25, best_case=0.50, commit=0.75, closed=1.00, omitted=0.00
- Stage weights (from v1-forecasts.routes.js): qualification=0.10, discovery=0.20, proposal=0.40, negotiation=0.70, closed_won=1.00, closed_lost=0.00
- Relationships: derived from Opportunity (opportunity_db) — reads opportunity_id, tenant_id, stage, forecast_category, amount, close_date, is_closed, is_won
- CRUD: R (GET /forecasts — scope: forecasts.read); Refresh (POST /forecasts/model, POST /forecasts/aggregate — scope: forecasts.read — forwards to predictive_forecasting Python module)
- Key business rule: Forecast is tenant-scoped; weighted value = sum(amount × forecast_category_weight) across all open Opportunities in the tenant pipeline
- Backend module: `backend/src/predictive_forecasting/` (Python); gateway service: `backend/gateway/services/forecasting.js`
- Note: Referenced in WF-005 (opportunity_stage_notify) as a post-stage-change refresh target; not a standalone editable entity

---

### Campaign Domain (campaign_db)

**Campaign**
- Description: A marketing outreach effort targeting a Segment
- Key fields: campaign_id (UUID PK), type (whatsapp_blast/email/sms), status (draft/scheduled/running/paused/completed/cancelled), open_rate, click_rate, conversion_rate

**Segment**
- Description: A criteria-based list of Contacts for targeting
- Key fields: segment_id (UUID PK), name, criteria (JSONB), member_count (INT)

---

### Knowledge Domain (knowledge_db)

**KnowledgeArticle**
- Description: A support knowledge article with 2-step publication workflow
- Key fields: article_id (UUID PK), title, body (TEXT), status (draft/review/published/archived), category, tags (TEXT[]), view_count, helpful_count, version (INT)
- State gate: draft→review→published (2-step approval); published→archived

---

### Territory Domain (territory_db)

**Territory**
- Description: A sales assignment region defined by geography, postal code, account segment, rep assignment, or hybrid criteria
- Key fields: territory_id (UUID PK), criteria_type (geographic/postal/account_segment/rep_assigned/hybrid — from runtime API; conceptual model used geography/industry/account_size/custom), criteria (JSONB), owner_id (nullable), status (active/inactive)
- Note: Runtime-enforced values (from gateway v1-territories.routes.js) are: geographic, postal, account_segment, rep_assigned, hybrid. These supersede the conceptual values in earlier documentation.

**TerritoryRule**
- Description: A single matching rule within a Territory
- Key fields: rule_id (UUID PK), territory_id (FK), criteria_field, operator, value, priority (INT)

---

### Partner Domain (contact_account_db.partners)

**Partner**
- Description: A reseller or referral partner with commission tracking
- Key fields: partner_id (UUID PK), tier (Silver/Gold/Platinum), commission_rate (FLOAT), ytd_revenue (NUMERIC PKR), ytd_commission (NUMERIC PKR), contact_phone (E.164)

---

### Audit Domain (audit_compliance_db)

**AuditLog**
- Description: Immutable, hash-chain verified log of all significant system actions
- Key fields: log_id (UUID PK), actor_id (FK), action (TEXT e.g. "lead.stage.changed"), entity_type, entity_id, outcome (allow/deny), hash (TEXT — chain verification)
- Key business rule: no UPDATE or DELETE; hash-chain integrity check on every export; signed CSV export supported

**FeatureFlag**
- Description: A per-tenant boolean toggle with optional dual-approval requirement
- Key fields: flag_id (UUID PK), flag_key (TEXT UNIQUE per tenant), is_enabled (BOOL), requires_dual_approval (BOOL), approval_log (JSONB)
- Key business rule: toggle requires 2-person approval when requires_dual_approval=true

---

### Activity Domain (activity_task_db)

**Activity**
- Description: An immutable log entry for a CRM interaction (call, WhatsApp message, email, meeting, note)
- Key fields: activity_id (UUID PK), actor_id (FK), entity_type (lead/contact/account/opportunity/case), entity_id (UUID), activity_type (call/whatsapp/email/meeting/note), outcome, duration_seconds, occurred_at

**Task**
- Description: A general-purpose assignable task (distinct from FollowupTask)
- Key fields: task_id (UUID PK), owner_id (FK), entity_type (nullable), entity_id (nullable), title, due_at, status (open/in_progress/done/cancelled), priority (high/medium/low)

---

## Aggregate Boundaries

| Aggregate Root | Constituent Entities |
|---|---|
| Lead | Lead, LeadAssignment, LeadHistory, FollowupTask |
| Contact | Contact |
| Account | Account (ChurnPrediction and CLVEstimate are lookup relationships; AI is the owning aggregate — see note) |
| Opportunity | Opportunity, OpportunityLineItem |
| Case | Case, CaseComment, CaseEscalation |
| Conversation | Conversation, Message, Handoff, AgentPresence |
| Workflow | WorkflowDefinition, WorkflowExecution, WorkflowStepRecord |
| Quote→Order | Quote, Order (Quote accepted → Order created) |
| Invoice | Invoice, Payment, Collection |
| Campaign | Campaign, Segment |
| Tenant | Tenant, User, Role, Permission, Session, RefreshToken |
| AI | LeadScore, ChurnPrediction, CLVEstimate, CopilotSuggestion, ScoringModel |
| Forecast | Forecast (computed — not persisted; derived from Opportunity aggregate) |

**Note on Account↔AI aggregate boundary:** ChurnPrediction and CLVEstimate are managed via /ai/predictions and /ai/estimates endpoints (owned by intelligence_db), so their authoritative aggregate root is AI. Account→ChurnPrediction and Account→CLVEstimate are lookup relationships only (Account is the subject key, not the owning root).

---

## Key Business Rules (Cross-Entity)

1. **Tenant isolation:** Every entity row contains `tenant_id`; gateway middleware enforces x-tenant-id header matches JWT tenant_id on every request
2. **Mandatory lead ownership:** `lead.owner_id` is NOT NULL — every lead must have an owner
3. **Canonical follow-up constraint:** Exactly one pending FollowupTask per Lead (DB unique constraint)
4. **Soft delete only:** Leads use soft-delete (deleted_at); Cases use status=CLOSED; no hard deletes on core CRM entities
5. **Immutable audit trail:** LeadHistory and AuditLog are append-only; no updates or deletes permitted
6. **Optimistic concurrency:** Cases and Opportunities use version_no for OCC; stale version returns 409 CONFLICT
7. **Quote approval gate:** discount_pct > 10% automatically sets requires_approval=true
8. **Case reopen window:** Cases can only be reopened within 14 calendar days of closing
9. **Payment stub mode:** JazzCash and Easypaisa remain in stub_mode=True until P-016 credentials verified
10. **Feature flag dual approval:** Flags with requires_dual_approval=true need 2 approvals to toggle

---

## Naming Conventions

| Convention | Rule |
|---|---|
| Entity IDs | UUID v4; named `{entity_name}_id` (e.g. lead_id, case_id) |
| Tenant scoping | Every table has `tenant_id UUID NOT NULL` |
| Timestamps | `created_at`, `updated_at` on all mutable entities; `TIMESTAMPTZ` type |
| Status fields | Lowercase hyphenated strings (e.g. "open", "in_progress", "closed_won") |
| Currency fields | NUMERIC type; PKR always; no multi-currency |
| Phone numbers | E.164 format with +923xx prefix for Pakistan |
| Soft deletes | `deleted_at TIMESTAMPTZ NULL` (NULL = active) |
| Versioning | `version_no INTEGER` for OCC entities (Cases, Opportunities) |
| Boolean flags | Named `is_*` (is_system, is_active, is_canonical, is_dismissed) |
| JSON fields | JSONB type for flexible/schema-less data (metadata, criteria, steps_dsl) |

---

*End DOMAIN_MODEL.md*
