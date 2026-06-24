# ENTITY_INVENTORY.md
> Generated: 2026-06-20 — U1 Authority Reconstruction — evidence from db/*/schema.sql, gateway/routes/v1-*.routes.js, src/*/entities.py, crm-dummy.js

> **Supporting Reference** — For entity authority, see [DOMAIN_MODEL.md](../../docs/00_authority/DOMAIN_MODEL.md) (docs/00_authority/). This document provides raw code-derived field evidence (30 entities confirmed from schema.sql); DOMAIN_MODEL.md is the curated canonical source. When entity definitions conflict, DOMAIN_MODEL.md governs. When entities change, update DOMAIN_MODEL.md first; then update this inventory to reflect implementation evidence.
> Cross-reference added: 2026-06-21 (Documentation Normalization Phase — DUP-001 resolution)

---

## Identity & Auth Domain

### User
**Source:** `db/identity_auth_db/schema.sql`, `gateway/routes/v1-auth.routes.js`
**Fields:** user_id (UUID PK), tenant_id (UUID FK), email (TEXT UNIQUE per tenant), password_hash (TEXT nullable — NULL for SSO), full_name (TEXT), status (active/suspended/deactivated), last_login_at (TIMESTAMPTZ nullable), created_at, updated_at
**Relationships:** belongs to Tenant; has many Roles via user_roles; has many Sessions; has many RefreshTokens
**CRUD:** C (register), R (list/get via /users), U (PATCH /users/:id), D (not explicitly — status→deactivated)

### Role
**Source:** `db/identity_auth_db/schema.sql`, `gateway/routes/v1-roles.routes.js`
**Fields:** role_id (UUID PK), tenant_id (UUID FK), name (TEXT UNIQUE per tenant), label (TEXT), description (TEXT), is_system (BOOL), active_user_count (int, in-memory), created_at
**Relationships:** has many Permissions via role_permissions; has many Users via user_roles
**CRUD:** C (POST /roles), R (GET /roles), U (PATCH /roles/:id), D (DELETE /roles/:id — non-system only)

### Permission (Scope)
**Source:** `db/identity_auth_db/schema.sql`, `gateway/config/rbac-scopes.js`
**Fields:** permission_id (UUID PK), scope (TEXT UNIQUE e.g. "leads.read"), description (TEXT), created_at
**Relationships:** belongs to many Roles via role_permissions
**CRUD:** R (defined at config time — not user-mutable via API)

### Session
**Source:** `db/identity_auth_db/schema.sql`
**Fields:** session_id (UUID PK), user_id (UUID FK), tenant_id (UUID FK), token_hash (TEXT UNIQUE), ip_address (TEXT), user_agent (TEXT), expires_at (TIMESTAMPTZ), revoked_at (TIMESTAMPTZ nullable), created_at
**Relationships:** belongs to User, belongs to Tenant
**CRUD:** C (login → creates session), D (logout → revokes via JTI blocklist in Redis)

### RefreshToken
**Source:** `db/identity_auth_db/schema.sql`, `gateway/routes/v1-auth.routes.js`
**Fields:** token_id (UUID PK), user_id (UUID FK), tenant_id (UUID FK), token_hash (TEXT UNIQUE), expires_at (TIMESTAMPTZ), rotated_at (TIMESTAMPTZ nullable), revoked_at (TIMESTAMPTZ nullable), created_at
**Relationships:** belongs to User
**CRUD:** C (login/register), R (POST /auth/refresh validates), D (rotated on use — single-use)

---

## Tenant Domain

### Tenant
**Source:** `db/org_tenant_db/schema.sql`, `gateway/routes/v1-auth.routes.js` (register endpoint)
**Fields:** tenant_id (UUID PK), name (TEXT), slug (TEXT UNIQUE), status (active), plan (starter/…), region (pk-south/…), created_at, updated_at
**Relationships:** has many Users; has many Leads; has all domain data
**CRUD:** C (POST /auth/register), R (GET /admin/tenants — admin only), U (PATCH /admin/tenants/:id), D (status flag)

---

## Lead Domain

### Lead
**Source:** `db/lead_management_db/schema.sql`, `src/lead_management/entities.py`, `gateway/routes/v1-leads.routes.js`
**Fields (DB):** lead_id (UUID PK), tenant_id (UUID FK NOT NULL), contact_id (UUID NOT NULL), owner_id (UUID NOT NULL — mandatory), stage (new/qualifying/nurturing/proposal/negotiation/won/lost/disqualified), status (open/working/idle/closed), priority (hot/warm/cold), source (whatsapp/web/import/manual/referral/campaign), campaign_id (UUID nullable), last_activity_at (TIMESTAMPTZ), version_no (INTEGER), created_at, updated_at
**Fields (Gateway extra):** title (TEXT), contact_name (TEXT), contact_phone_e164 (E.164), contact_email (TEXT), estimated_value (NUMERIC), currency (PKR default), notes (TEXT), metadata (JSONB)
**Fields (Python entity):** lead_id, tenant_id, owner_user_id, source, status, score (int), email, phone, company_name, created_at, converted_at
**Relationships:** belongs to Tenant; belongs to Contact (contact_id); owned by User (owner_id); has many LeadAssignments; has many LeadHistory; has many FollowupTasks; optionally belongs to Campaign
**CRUD:** C (POST /leads), R (GET /leads, GET /leads/:id, GET /leads/export), U (PATCH /leads/:id), D (DELETE /leads/:id — soft delete via repo.softDelete)

### LeadAssignment
**Source:** `db/lead_management_db/schema.sql`
**Fields:** assignment_id (UUID PK), lead_id (UUID FK CASCADE), tenant_id (UUID FK), owner_id (UUID NOT NULL), assigned_by (UUID nullable — NULL=system), reason (TEXT), assigned_at (TIMESTAMPTZ)
**Relationships:** belongs to Lead
**CRUD:** C (created internally on lead.assign), R (implicit — part of lead history)

### LeadHistory
**Source:** `db/lead_management_db/schema.sql`
**Fields:** history_id (UUID PK), lead_id (UUID FK CASCADE), tenant_id (UUID FK), field_name (TEXT), old_value (TEXT), new_value (TEXT), changed_by (UUID NOT NULL), changed_at (TIMESTAMPTZ)
**Relationships:** belongs to Lead
**CRUD:** C (created automatically on lead field changes — immutable audit trail), R (via lead detail)

---

## Contact Domain

### Contact
**Source:** `gateway/routes/v1-contacts.routes.js`, `db/contact_account_db/schema.sql`
**Fields:** contact_id (UUID PK), display_name (TEXT), phone_e164 (E.164), email (TEXT nullable), account_id (UUID nullable FK), account_name (TEXT), tags (TEXT[]), open_cases (INT), idle (INT), completeness_score (INT 0–100), source (whatsapp/web/import/manual), last_touchpoint (DATE), created_at
**Patchable fields:** display_name, phone_e164, email, account_id, tags, source
**Relationships:** belongs to Account (optional); has many Cases (via contact_id); has many Leads (via contact_id)
**CRUD:** C (POST /contacts, POST /contacts/import), R (GET /contacts, GET /contacts/:id, GET /contacts/export), U (PATCH /contacts/:id), D (DELETE /contacts/:id)

### Account
**Source:** `db/contact_account_db/schema.sql`, crm-dummy.js
**Fields:** account_id (UUID PK), tenant_id (UUID FK), name (TEXT), tier (TEXT), industry (TEXT), balance (NUMERIC PKR), created_at, updated_at
**Relationships:** has many Contacts; has many Opportunities; has many Cases; has AI ChurnPrediction; has AI CLVEstimate
**CRUD:** C (POST /accounts), R (GET /accounts, GET /accounts/:id), U (PATCH /accounts/:id)

---

## Opportunity / Sales Domain

### Opportunity
**Source:** `gateway/routes/v1-opportunities.routes.js`, `db/opportunity_db/schema.sql`
**Fields:** opportunity_id (UUID PK), tenant_id (UUID FK), owner_id (UUID NOT NULL), name (TEXT), account_id (UUID nullable), account_name (TEXT), contact_id (UUID nullable), amount (NUMERIC nullable), currency (PKR default), close_date (DATE nullable), stage (qualification/discovery/proposal/negotiation/closed_won/closed_lost), probability (INT 0–100), forecast_category (pipeline/best_case/commit/closed/omitted), version_no (INT), closed_at (TIMESTAMPTZ nullable), close_reason (TEXT nullable), created_at, updated_at
**Relationships:** belongs to Account; belongs to Contact; owned by User; has many OpportunityLineItems; emits events on stage change
**CRUD:** C (POST /opportunities), R (GET /opportunities, GET /opportunities/:id), U (PATCH /opportunities/:id — atomic stage transition), D (not exposed — use closed_lost)

### OpportunityLineItem
**Source:** `gateway/routes/v1-opportunities.routes.js`
**Fields:** line_item_id (UUID PK), opportunity_id (UUID FK), tenant_id (UUID FK), product_id (UUID NOT NULL), quantity (INT default 1), unit_price (NUMERIC NOT NULL), currency (PKR default), discount_pct (NUMERIC default 0)
**Relationships:** belongs to Opportunity
**CRUD:** C (POST /opportunities/:id/line-items), R (GET /opportunities/:id/line-items)

---

## Follow-up Domain

### FollowupTask
**Source:** `gateway/routes/v1-followups.routes.js`, `db/activity_task_db/schema.sql`
**Fields:** task_id (UUID PK), tenant_id (UUID FK), lead_id (UUID NOT NULL FK), owner_id (UUID NOT NULL), state (pending/overdue/completed), due_at (TIMESTAMPTZ NOT NULL), rule_type (TimeBased/ActivityBased/InactivityBased), escalation_level (none/reminder/warning/escalated/reassigned), generated_by (Scheduler/…), is_canonical (BOOL — exactly one canonical pending task per lead), action_type (Call/WhatsApp/Reminder/null), attempts_count (INT), completed_at (TIMESTAMPTZ nullable), created_at, updated_at
**Relationships:** belongs to Lead; belongs to User (owner)
**CRUD:** C (POST /followups), R (GET /followups, GET /followups/:id, GET /followups/lead/:id/canonical), U (POST /followups/:id/complete, POST /followups/:id/snooze)
**Invariant:** Exactly one canonical pending task per lead (enforced by DB unique constraint)

---

## Case / Support Domain

### Case
**Source:** `gateway/routes/v1-cases.routes.js`, `db/case_ticket_db/schema.sql`
**Fields:** case_id (UUID PK), tenant_id (UUID FK), case_number (TEXT e.g. CAS-2026-000001), subject (TEXT), description (TEXT nullable), status (OPEN/ASSIGNED/IN_PROGRESS/WAITING_ON_CUSTOMER/RESOLVED/ESCALATED/CLOSED), priority (critical/high/medium/low), source (whatsapp/web_form/email/phone/internal), category (TEXT nullable), contact_id (UUID nullable FK), account_id (UUID nullable FK), lead_id (UUID nullable FK), assigned_to (UUID nullable), assigned_team_id (UUID nullable), queue_id (UUID nullable), sla_tier (tier_1_critical/tier_2_high/tier_3_standard/tier_4_low), sla_first_response_due_at (TIMESTAMPTZ), sla_resolution_due_at (TIMESTAMPTZ), first_responded_at (TIMESTAMPTZ nullable), resolved_at (TIMESTAMPTZ nullable), resolution_confirmed_at (TIMESTAMPTZ nullable), closed_at (TIMESTAMPTZ nullable), reopened_at (TIMESTAMPTZ nullable), reopen_count (INT), escalation_level (INT 0–3), tags (TEXT[]), custom_fields (JSONB), version_no (INT), created_at, updated_at, created_by (UUID), updated_by (UUID), knowledge_article_ids (UUID[] optional)
**State machine:** OPEN→ASSIGNED|CLOSED; ASSIGNED→IN_PROGRESS|OPEN|ESCALATED; IN_PROGRESS→WAITING_ON_CUSTOMER|RESOLVED|ESCALATED; WAITING_ON_CUSTOMER→IN_PROGRESS|RESOLVED|CLOSED; RESOLVED→CLOSED|IN_PROGRESS; ESCALATED→ASSIGNED|IN_PROGRESS; CLOSED→OPEN (14-day reopen window)
**SLA defaults:** tier_1_critical: 1h response/8h resolution; tier_2_high: 4h/24h; tier_3_standard: 8h/72h; tier_4_low: 24h/168h
**CRUD:** C (POST /cases), R (GET /cases, GET /cases/:id), U (PATCH /cases/:id), D (none — use CLOSED status)

### CaseComment
**Source:** `gateway/routes/v1-cases.routes.js`
**Fields:** comment_id (UUID PK), case_id (UUID FK), tenant_id (UUID FK), comment_type (internal_note/customer_reply/resolution/status_change/escalation_note), body (TEXT), author_id (UUID), is_visible_to_customer (BOOL), attachment_urls (TEXT[]), created_at, updated_at
**Relationships:** belongs to Case
**CRUD:** C (POST /cases/:id/comments), R (embedded in GET /cases/:id)

### CaseEscalation
**Source:** `gateway/routes/v1-cases.routes.js`
**Fields:** escalation_id (UUID PK), case_id (UUID FK), tenant_id (UUID FK), escalation_level (INT), escalation_reason (sla_first_response_breach/sla_resolution_breach/customer_request/manager_override), escalated_by (UUID), escalated_to (UUID nullable), escalated_to_team (UUID nullable), note (TEXT nullable), triggered_at (TIMESTAMPTZ), resolved_at (TIMESTAMPTZ nullable)
**Relationships:** belongs to Case
**CRUD:** C (POST /cases/:id/escalate — CASES_ADMIN), R (embedded in GET /cases/:id)

### SupportQueue
**Source:** `gateway/routes/v1-cases.routes.js`
**Fields:** queue_id (UUID PK), name (TEXT), description (TEXT nullable), routing_strategy (round_robin/least_loaded/manual), sla_tier_default (tier_1_critical/…), skill_tags (TEXT[]), team_id (UUID nullable), is_active (BOOL), created_at, updated_at
**Relationships:** has many Cases (via queue_id)
**CRUD:** C (POST /support/queues — CASES_ADMIN), R (GET /support/queues), U (PATCH /support/queues/:id — CASES_ADMIN)

---

## Finance Domain

### Invoice
**Source:** `db/transaction_db/schema.sql`, crm-dummy.js
**Fields:** invoice_id (UUID PK), tenant_id (UUID FK), account_id (UUID FK), contact_id (UUID FK), total_amount (NUMERIC PKR), paid_amount (NUMERIC), balance_amount (NUMERIC), status (draft/sent/paid/overdue/partially_paid/cancelled), due_date (DATE), is_overdue (BOOL), created_at, updated_at
**Relationships:** belongs to Account; belongs to Contact; linked to Order (optionally)
**CRUD:** C (POST /invoices), R (GET /invoice-summaries), U (payment via /payments), D (status→cancelled)

### Subscription
**Source:** `db/transaction_db/schema.sql`, crm-dummy.js
**Fields:** subscription_id (UUID PK), tenant_id (UUID FK), account_id (UUID FK), plan_name (TEXT), status (draft/trialing/active/past_due/paused/cancelled/expired), mrr (NUMERIC PKR), arr (NUMERIC PKR), billing_cycle (monthly/annual), next_billing_date (DATE), trial_ends_at (DATE nullable), created_at, updated_at
**CRUD:** C (POST /subscriptions), R (GET /subscriptions, GET /subscriptions/:id), U (PATCH /subscriptions/:id)

### Quote
**Source:** `db/quote_order_db/schema.sql`, crm-dummy.js
**Fields:** quote_id (UUID PK), tenant_id (UUID FK), opportunity_id (UUID FK), contact_id, account_id, line_items (JSONB array), subtotal (NUMERIC PKR), discount_pct (NUMERIC), total (NUMERIC), status (draft/sent/approved/rejected/expired), approval_history (JSONB), requires_approval (BOOL — auto-set if discount_pct > 10%), created_at, updated_at
**CRUD:** C (POST /quotes), R (GET /quotes, GET /quotes/:id), U (PATCH /quotes/:id), D (status→expired)

### Order
**Source:** `db/quote_order_db/schema.sql`, crm-dummy.js
**Fields:** order_id (UUID PK), tenant_id (UUID FK), quote_id (UUID FK), account_id, total (NUMERIC PKR), status (processing/fulfilled/cancelled), fulfilled_at (TIMESTAMPTZ nullable), linked_invoice_id (UUID nullable), created_at
**Note:** Immutable post-fulfilment (enforced by rule_engine)
**CRUD:** C (POST /orders — from accepted quote), R (GET /orders, GET /orders/:id)

### Payment
**Source:** `db/transaction_db/schema.sql`, adapters/pakistan/payments/
**Fields:** payment_id (UUID PK), tenant_id (UUID FK), invoice_id (UUID FK), amount (NUMERIC PKR), method (jazzcash/easypaisa/bank_transfer), status (pending/completed/failed/reversed), stub_mode (BOOL), created_at
**Relationships:** belongs to Invoice
**CRUD:** C (POST /payments), R (GET /payments)
**Note:** JazzCash and Easypaisa adapters implemented but `stub_mode=True` in production config

### Collection
**Source:** crm-dummy.js, `gateway/routes/v1-collections.routes.js`
**Fields:** collection_id (UUID PK), tenant_id (UUID FK), contact_id (UUID FK), invoice_id (UUID FK), amount_due (NUMERIC PKR), days_overdue (INT), status (pending/contacted/promised/paid/escalated/written_off), last_contact_at (TIMESTAMPTZ nullable), next_action_at (TIMESTAMPTZ nullable), created_at, updated_at
**CRUD:** C, R (GET /collections, GET /collections/:id), U

---

## Inbox / Communication Domain

### Conversation
**Source:** `gateway/routes/v1-inbox.routes.js`, `db/messaging_db/schema.sql`
**Fields:** conversation_id (UUID PK), tenant_id (UUID FK), contact_name (TEXT), contact_phone (E.164), channel (whatsapp/email/sms), state (open/resolved/closed), assigned_agent_id (UUID nullable), assigned_at (TIMESTAMPTZ nullable), queue_id (UUID FK nullable), assignment_reason (auto_routed/claimed/handoff), handoff_count (INT), last_handoff_at (TIMESTAMPTZ nullable), unread_count (INT), intent (payment_query/follow_up_response/lead_inquiry/support_request), last_message_preview (TEXT), last_message_at (TIMESTAMPTZ)
**Relationships:** has many Messages; has many Handoffs; belongs to InboxQueue; optionally linked to Contact
**CRUD:** R (GET /inbox/conversations, GET /inbox/conversations/:id), U (claim/handoff/resolve via sub-actions)

### Message
**Source:** `gateway/routes/v1-inbox.routes.js`
**Fields:** message_id (UUID PK), conversation_id (UUID FK), tenant_id (UUID FK), direction (inbound/outbound), text (TEXT), occurred_at (TIMESTAMPTZ), sender_name/sender_id (TEXT/UUID), created_at
**CRUD:** C (POST /inbox/conversations/:id/messages), R (embedded in conversation detail)

### Handoff
**Source:** `gateway/routes/v1-inbox.routes.js`
**Fields:** handoff_id (UUID PK), conversation_id (UUID FK), tenant_id (UUID FK), from_agent_id (UUID nullable), to_agent_id (UUID nullable), handoff_reason (agent_unavailable/capacity_exceeded/skill_match/manual/escalation), note (TEXT nullable), initiated_by (UUID), created_at
**CRUD:** C (POST /inbox/conversations/:id/handoff)

### AgentPresence
**Source:** `gateway/routes/v1-inbox.routes.js`
**Fields:** agent_id (UUID PK), tenant_id (UUID FK), status (online/away/busy/offline), open_conversation_count (INT), max_concurrent (INT default 10), last_seen_at (TIMESTAMPTZ), updated_at (TIMESTAMPTZ)
**CRUD:** C/U (PATCH /inbox/presence), R (GET /inbox/presence — inbox.admin only)

### InboxQueue
**Source:** `gateway/routes/v1-inbox.routes.js`
**Fields:** queue_id (UUID PK), name (TEXT), routing_strategy (round_robin/least_loaded/claim_first/skill_based), auto_assign (BOOL), skill_tags (TEXT[]), team_id (UUID nullable), is_active (BOOL), created_at, updated_at
**CRUD:** C (POST /inbox/queues), R (GET /inbox/queues), U (PATCH /inbox/queues/:id), stats (GET /inbox/queues/:id/stats)

---

## Workflow Domain

### WorkflowDefinition
**Source:** `gateway/routes/v1-workflows.routes.js`, `db/workflow_db/schema.sql`
**Fields:** workflow_id (UUID PK), tenant_id (UUID FK), workflow_key (TEXT slug), name (TEXT), description (TEXT nullable), status (draft/active/paused/archived), trigger_events (TEXT[] e.g. ["lead.idle.v1"]), steps_dsl (JSONB array of {id, type, name, action/condition}), max_retries (INT default 3), retry_backoff_seconds (INT default 60), timeout_seconds (INT default 300), is_system (BOOL), version (INT), created_by (UUID), created_at, updated_at
**State machine:** draft→active|archived; active→paused|archived; paused→active|archived; archived→(terminal)
**CRUD:** C (POST /workflows), R (GET /workflows, GET /workflows/:id, GET /workflows/:id/stats), U (PATCH /workflows/:id), Publish (POST /workflows/:id/publish), Simulate (POST /workflows/:id/simulate)

### WorkflowExecution
**Source:** `gateway/routes/v1-workflows.routes.js`
**Fields:** execution_id (UUID PK), workflow_id (UUID FK), tenant_id (UUID FK), workflow_key (TEXT), workflow_name (TEXT), trigger_event (TEXT), trigger_payload (JSONB), status (running/succeeded/failed/retrying/cancelled), step_count (INT), current_step (INT), failed_step (TEXT nullable), error_message (TEXT nullable), retry_count (INT), parent_execution_id (UUID nullable — for retries), started_at (TIMESTAMPTZ), ended_at (TIMESTAMPTZ nullable), duration_ms (INT nullable), created_at
**CRUD:** R (GET /workflows/runs, GET /workflows/runs/:id), Retry (POST /workflows/runs/:id/retry), Cancel (POST /workflows/runs/:id/cancel)

### WorkflowStepRecord
**Source:** `gateway/routes/v1-workflows.routes.js`
**Fields:** step_record_id (UUID PK), execution_id (UUID FK), workflow_id (UUID FK), tenant_id (UUID FK), step_index (INT), step_name (TEXT), step_type (condition/action/notification), status (succeeded/failed), input_data (JSONB), output_data (JSONB nullable), error_message (TEXT nullable), duration_ms (INT), started_at, ended_at, created_at
**CRUD:** R (embedded in GET /workflows/runs/:id)

---

## AI / Intelligence Domain

### LeadScore
**Source:** `gateway/routes/v1-ai.routes.js`, `db/intelligence_db/schema.sql`
**Fields:** score_id (UUID PK), tenant_id (UUID FK), lead_id (UUID FK), model_id (TEXT), score (INT 0–100), score_band (hot/warm/cold/disqualified), trend (rising/stable/falling), trend_delta (INT), confidence_score (FLOAT 0–1), is_stale (BOOL), computed_at (TIMESTAMPTZ), top_drivers (JSONB array of {feature_key, feature_label, contribution, direction, value})
**CRUD:** R (GET /ai/scores/leads, GET /ai/scores/leads/:lead_id), Recompute (POST /ai/scores/leads/:lead_id/recompute)

### ChurnPrediction
**Source:** `gateway/routes/v1-ai.routes.js`
**Fields:** prediction_id (UUID PK), tenant_id (UUID FK), account_id (UUID FK), model_id (TEXT), churn_probability (FLOAT 0–1), risk_band (high/medium/low), confidence_score (FLOAT), evidence_anchor (TEXT), recommended_action (TEXT), is_stale (BOOL), computed_at (TIMESTAMPTZ), top_drivers (JSONB)
**CRUD:** R (GET /ai/predictions/churn, GET /ai/predictions/churn/:account_id)

### CLVEstimate
**Source:** `gateway/routes/v1-ai.routes.js`
**Fields:** estimate_id (UUID PK), tenant_id (UUID FK), account_id (UUID FK), model_id (TEXT), estimated_clv (NUMERIC PKR), clv_horizon_months (INT), confidence_score (FLOAT), evidence_anchor (TEXT), is_stale (BOOL), computed_at (TIMESTAMPTZ)
**CRUD:** R (GET /ai/estimates/clv, GET /ai/estimates/clv/:account_id)

### CopilotSuggestion
**Source:** `gateway/routes/v1-ai.routes.js`
**Fields:** suggestion_id (UUID PK), tenant_id (UUID FK), target_user_id (UUID FK), suggestion_type (follow_up_overdue/deal_nudge/risk_flag/next_action/stale_deal/sla_breach_alert), priority (urgent/high/medium/low), title (TEXT), body (TEXT), action_label (TEXT), action_href (TEXT), evidence_anchor (TEXT), entity_type (lead/account/case), entity_id (UUID), confidence_score (FLOAT), is_dismissed (BOOL), dismissed_at (TIMESTAMPTZ nullable), is_actioned (BOOL), actioned_at (TIMESTAMPTZ nullable), expires_at (TIMESTAMPTZ nullable), created_at, updated_at
**CRUD:** R (GET /ai/copilot/suggestions), U (POST /ai/copilot/suggestions/:id/dismiss, POST /ai/copilot/suggestions/:id/action), Query (POST /ai/copilot/query)

### ScoringModel
**Source:** `gateway/routes/v1-ai.routes.js`
**Fields:** model_key (TEXT PK), model_type (lead_score/churn_predict/clv_estimate), version (TEXT), algorithm (rule_based/ml), recompute_interval_hours (INT), is_active (BOOL), description (TEXT)
**Current models:** lead_score_v1, churn_predict_v1, clv_estimate_v1 (all rule_based)
**CRUD:** R only (GET /ai/models, GET /ai/models/:model_key)
**Note:** No AI inference provider SDK in requirements.txt — models are rule-based computations

---

## Campaign / Marketing Domain

### Campaign
**Source:** `db/campaign_db/schema.sql`, crm-dummy.js
**Fields:** campaign_id (UUID PK), tenant_id (UUID FK), name (TEXT), type (whatsapp_blast/email/sms), status (draft/scheduled/running/paused/completed/cancelled), segment_id (UUID FK nullable), target_count (INT), sent_count (INT), open_rate (FLOAT), click_rate (FLOAT), conversion_rate (FLOAT), scheduled_at (TIMESTAMPTZ nullable), started_at (TIMESTAMPTZ nullable), ended_at (TIMESTAMPTZ nullable), created_at, updated_at
**CRUD:** C (POST /campaigns), R (GET /campaigns, GET /campaigns/:id), U (PATCH /campaigns/:id)

### Segment
**Source:** `gateway/routes/v1-segments.routes.js`, `db/campaign_db/schema.sql`
**Fields:** segment_id (UUID PK), tenant_id (UUID FK), name (TEXT), criteria (JSONB), member_count (INT), created_at, updated_at
**CRUD:** C/R/U (via /segments)

---

## Knowledge Domain

### KnowledgeArticle
**Source:** `db/knowledge_db/schema.sql`, crm-dummy.js
**Fields:** article_id (UUID PK), tenant_id (UUID FK), title (TEXT), body (TEXT), status (draft/review/published/archived), category (TEXT), tags (TEXT[]), view_count (INT), helpful_count (INT), version (INT), published_at (TIMESTAMPTZ nullable), created_by (UUID FK), updated_by (UUID FK), created_at, updated_at
**State gate:** draft→review→published (2-step approval), published→archived
**CRUD:** C/R/U (via /knowledge, /knowledge/:id), linked to Cases (POST /cases/:id/link-article)

---

## Territory Domain

### Territory
**Source:** `db/territory_db/schema.sql`, crm-dummy.js, gateway/routes/v1-territories.routes.js
**Fields:** territory_id (UUID PK), tenant_id (UUID FK), name (TEXT), criteria_type (geographic/postal/account_segment/rep_assigned/hybrid — runtime-enforced values from gateway; earlier documentation used geography/industry/account_size/custom), criteria (JSONB), owner_id (UUID FK nullable), status (active/inactive), created_at, updated_at
**Relationships:** has many TerritoryRules; has many Users (assigned); has many Leads (auto-assigned)
**CRUD:** C/R/U/D (via /territories, /territories/:id)

### TerritoryRule
**Source:** `db/territory_db/schema.sql`
**Fields:** rule_id (UUID PK), territory_id (UUID FK), criteria_field (TEXT), operator (TEXT), value (TEXT), priority (INT), created_at
**CRUD:** C/R/U/D (via /territories/:id/rules — inferred from territory management module)

---

## Partner Domain

### Partner
**Source:** `db/contact_account_db/schema.sql` (partners table), crm-dummy.js
**Fields:** partner_id (UUID PK), tenant_id (UUID FK), name (TEXT), tier (Silver/Gold/Platinum), status (active/inactive), commission_rate (FLOAT), ytd_revenue (NUMERIC PKR), ytd_commission (NUMERIC PKR), contact_name (TEXT), contact_email (TEXT), contact_phone (E.164), created_at, updated_at
**Relationships:** has many DealRegistrations; has CommissionLedger entries; has AttributedLeads
**CRUD:** C/R/U (via /partners, /partners/:id)

---

## Audit / Compliance Domain

### AuditLog
**Source:** `db/audit_compliance_db/schema.sql`, crm-dummy.js
**Fields:** log_id (UUID PK), tenant_id (UUID FK), actor_id (UUID FK), action (TEXT e.g. "lead.stage.changed"), entity_type (TEXT), entity_id (UUID), outcome (allow/deny), ip_address (INET), user_agent (TEXT), metadata (JSONB), hash (TEXT — hash-chain verification), created_at
**Note:** Immutable; hash-chain verified; supports signed CSV export
**CRUD:** R only (GET /audit, GET /audit/export)

### FeatureFlag
**Source:** `db/feature_flag_db/schema.sql`, crm-dummy.js
**Fields:** flag_id (UUID PK), tenant_id (UUID FK), flag_key (TEXT UNIQUE per tenant), is_enabled (BOOL), description (TEXT), requires_dual_approval (BOOL), approval_log (JSONB), updated_by (UUID FK), updated_at
**Note:** Toggle requires 2-person approval when requires_dual_approval=true
**CRUD:** R (GET /admin/feature-flags), U (PATCH /admin/feature-flags/:id — dual approval enforced)

---

## Activity / Task Domain

### Activity
**Source:** `db/activity_task_db/schema.sql`
**Fields:** activity_id (UUID PK), tenant_id (UUID FK), actor_id (UUID FK), entity_type (lead/contact/account/opportunity/case), entity_id (UUID), activity_type (call/whatsapp/email/meeting/note), outcome (TEXT nullable), duration_seconds (INT nullable), notes (TEXT nullable), occurred_at (TIMESTAMPTZ), created_at
**CRUD:** C (POST /activities), R (GET /activities, GET /activities/:id)

### Task
**Source:** `db/activity_task_db/schema.sql`
**Fields:** task_id (UUID PK), tenant_id (UUID FK), owner_id (UUID FK), entity_type (TEXT nullable), entity_id (UUID nullable), title (TEXT), description (TEXT nullable), due_at (TIMESTAMPTZ), status (open/in_progress/done/cancelled), priority (high/medium/low), created_at, updated_at
**Note:** This is the general task entity (not the FollowupTask which has its own domain)
**CRUD:** C (POST /tasks), R (GET /tasks, GET /tasks/:id), U (PATCH /tasks/:id)

---

## Entity Relationship Map (text)

```
Tenant
  ├── Users → Roles → Permissions
  ├── Leads → LeadAssignments, LeadHistory, FollowupTasks
  │     └── belongs to Contact
  ├── Contacts → belongs to Account
  ├── Accounts → ChurnPrediction, CLVEstimate
  ├── Opportunities → OpportunityLineItems
  │     └── belongs to Account, Contact
  ├── Cases → CaseComments, CaseEscalations
  │     └── belongs to Contact, Account, Lead
  │     └── linked to KnowledgeArticles
  ├── Invoices → Payments, Collections
  ├── Quotes → Orders → Invoices
  ├── Subscriptions
  ├── Campaigns → Segments
  ├── Conversations → Messages, Handoffs
  │     └── assigned to Users (agents)
  ├── WorkflowDefinitions → WorkflowExecutions → WorkflowStepRecords
  ├── KnowledgeArticles
  ├── Territories → TerritoryRules
  ├── Partners
  ├── AuditLog
  ├── FeatureFlags
  ├── Activities, Tasks
  └── AI: LeadScores, ChurnPredictions, CLVEstimates, CopilotSuggestions
```

---

*End ENTITY_INVENTORY.md*
