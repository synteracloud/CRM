Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: Human

# DATABASE_SCHEMA.md
> Source: backend/db/*/schema.sql (18 domain schema files), backend/alembic/versions/ (12 migrations), backend/services/db/models/

---

## 1. Multi-Tenancy Architecture

**Pattern:** Schema-per-domain with `tenant_id` column on every domain table.
**Isolation mechanism:** Every domain table has `tenant_id UUID NOT NULL` with a FK to a local `tenant_ref` table. Cross-tenant queries are prevented at the application layer (gateway auth middleware validates `x-tenant-id == JWT.tenant_id`).
**Cross-schema FKs:** Not used — cross-domain references (e.g. contact_id on leads, account_id on opportunities) are enforced by the application layer only, not by DB-level FK constraints. This allows each domain schema to operate independently.
**Tenant provisioning:** On `POST /auth/register`, the gateway inserts `tenant_ref` rows into 6 domain schemas in a single transaction: identity_auth_db, lead_management_db, contact_account_db, opportunity_db, transaction_db, activity_task_db.

---

## 2. Common Patterns Across All Tables

| Pattern | Implementation |
|---|---|
| Primary key strategy | UUID (`gen_random_uuid()` via pgcrypto extension) — all tables |
| Tenant isolation | `tenant_id UUID NOT NULL` on every domain table; FK to local `tenant_ref` |
| Soft delete | NOT universally applied. Leads use soft delete (`deleted_at` column added in gateway layer). Most entities use status fields (e.g. `status='deactivated'`, `status='cancelled'`). |
| Audit columns | `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()` on all tables. `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()` on mutable tables (via trigger). |
| Updated_at trigger | Each schema defines `set_updated_at()` trigger function; applied to all mutable tables. |
| Optimistic concurrency | `version_no INTEGER NOT NULL DEFAULT 1` on: leads, contacts, accounts, opportunities, quotes, cases |
| Enums | Text columns with CHECK constraints (not PostgreSQL ENUM type) |
| JSONB | Used for: flexible fields (metadata, tags, criteria, steps_dsl, factors, payload_json) |
| Immutable tables | audit_log (has `audit_log_no_update` and `audit_log_no_delete` rules), lead_history, case_history, score_history |

---

## 3. Database Schemas — Complete Table Inventory

### identity_auth_db
**Purpose:** Users, roles, permissions, sessions, refresh tokens. All authentication state.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), status TEXT, created_at | Local mirror of org_tenant_db tenants for FK integrity |
| users | user_id (PK UUID), tenant_id FK, email TEXT, password_hash TEXT nullable, full_name TEXT, status TEXT, last_login_at, created_at, updated_at | UNIQUE(tenant_id, email). password_hash NULL for SSO users. CHECK status IN (active, suspended, deactivated) |
| roles | role_id (PK UUID), tenant_id FK, name TEXT, description TEXT, is_system BOOL, created_at | UNIQUE(tenant_id, name). is_system=TRUE rows cannot be deleted |
| permissions | permission_id (PK UUID), scope TEXT UNIQUE, description TEXT, created_at | Global scope registry (not tenant-scoped) |
| role_permissions | (role_id, permission_id) composite PK, granted_at | Junction table — role to scope assignments |
| user_roles | (user_id, role_id) composite PK, tenant_id FK, granted_by UUID nullable, granted_at | Junction table — user to role assignments |
| sessions | session_id (PK UUID), user_id FK, tenant_id FK, token_hash TEXT UNIQUE, ip_address, user_agent, expires_at, revoked_at nullable, created_at | INDEX on (user_id, expires_at) |
| refresh_tokens | token_id (PK UUID), user_id FK, tenant_id FK, token_hash TEXT UNIQUE, expires_at, rotated_at nullable, revoked_at nullable, created_at | Single-use rotating tokens |

**Indexes:** sessions(user_id, expires_at)
**Soft delete:** Not present; status flag on users (deactivated), revoked_at on sessions/refresh_tokens

---

### org_tenant_db
**Purpose:** Tenant registry, entitlements, organizations, memberships.

| Table | Key Columns | Notes |
|---|---|---|
| tenants | tenant_id (PK UUID), name TEXT, slug TEXT UNIQUE, status TEXT, plan TEXT, region TEXT, created_at, updated_at | CHECK status IN (active, suspended, deactivated, trial). CHECK plan IN (starter, growth, enterprise) |
| tenant_entitlements | entitlement_id (PK UUID), tenant_id FK, feature TEXT, enabled BOOL, value_limit INT nullable, created_at, updated_at | UNIQUE(tenant_id, feature) — per-tenant feature gates |
| organizations | org_id (PK UUID), tenant_id FK, name TEXT, type TEXT, created_at, updated_at | Sub-units within tenant. type: team/division/region |
| organization_memberships | membership_id (PK UUID), org_id FK, tenant_id FK, user_id UUID (app-enforced FK), role TEXT, joined_at | UNIQUE(org_id, user_id). CHECK role IN (owner, admin, member, viewer) |

**No soft delete column.** Status flag on tenants.

---

### lead_management_db
**Purpose:** Leads, assignment history, immutable field-change audit.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| leads | lead_id (PK UUID), tenant_id FK, contact_id UUID NOT NULL (app FK), owner_id UUID NOT NULL, stage TEXT, status TEXT, priority TEXT, source TEXT, campaign_id UUID nullable, last_activity_at, version_no INT, created_at, updated_at | Stage CHECK: new/qualifying/nurturing/proposal/negotiation/won/lost/disqualified. Status CHECK: open/working/idle/closed. Priority CHECK: hot/warm/cold. Source CHECK: whatsapp/web/import/manual/referral/campaign |
| lead_assignments | assignment_id (PK UUID), lead_id FK CASCADE, tenant_id FK, owner_id UUID NOT NULL, assigned_by UUID nullable, reason TEXT, assigned_at | Historical assignment log. assigned_by NULL = system |
| lead_history | history_id (PK UUID), lead_id FK CASCADE, tenant_id FK, field_name TEXT, old_value TEXT, new_value TEXT, changed_by UUID NOT NULL, changed_at | Immutable field-level audit trail |

**Indexes:** leads(tenant_id, owner_id), leads(tenant_id, stage), leads(tenant_id, updated_at DESC), leads(tenant_id, contact_id)
**Soft delete:** Application-layer via deleted_at; DB schema stores version_no for optimistic concurrency

---

### contact_account_db
**Purpose:** Contacts (persons), accounts (companies), account hierarchy.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| contacts | contact_id (PK UUID), tenant_id FK, first_name TEXT nullable, last_name TEXT nullable, email TEXT nullable, phone_e164 TEXT NOT NULL, account_id UUID nullable, owner_id UUID nullable, status TEXT, lifecycle TEXT, tags JSONB, version_no INT, created_at, updated_at | UNIQUE(tenant_id, phone_e164) — primary dedup key. Status: active/inactive/blocked. Lifecycle: lead/prospect/customer/churned |
| accounts | account_id (PK UUID), tenant_id FK, name TEXT, domain TEXT nullable, industry TEXT nullable, size_band TEXT nullable, owner_id UUID nullable, parent_account_id UUID self-ref nullable, version_no INT, created_at, updated_at | Parent account hierarchy via self-reference |
| account_hierarchy | hierarchy_id (PK UUID), tenant_id FK, ancestor_id FK, descendant_id FK, depth INT, created_at | Materialized path for fast tree queries. UNIQUE(ancestor_id, descendant_id) |

**Indexes:** contacts(tenant_id, phone_e164), contacts(tenant_id, email) WHERE NOT NULL, contacts(tenant_id, account_id), accounts(tenant_id), accounts(parent_account_id)

---

### opportunity_db
**Purpose:** Pipeline opportunities, line items, forecast period snapshots.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| opportunities | opportunity_id (PK UUID), tenant_id FK, account_id UUID nullable, contact_id UUID nullable, owner_id UUID NOT NULL, name TEXT, stage TEXT, amount NUMERIC(18,2) nullable, currency TEXT, close_date DATE nullable, probability SMALLINT 0-100, forecast_category TEXT, close_reason TEXT nullable, version_no INT, created_at, updated_at, closed_at nullable | Stage: qualification/discovery/proposal/negotiation/closed_won/closed_lost. Forecast: pipeline/best_case/commit/closed/omitted |
| opportunity_line_items | line_item_id (PK UUID), opportunity_id FK CASCADE, tenant_id FK, product_id UUID NOT NULL, quantity NUMERIC(10,2), unit_price NUMERIC(18,2), currency TEXT, discount_pct NUMERIC(5,2), total_price NUMERIC GENERATED STORED, created_at | Computed column: quantity * unit_price * (1 - discount_pct/100) |
| forecast_records | forecast_id (PK UUID), opportunity_id FK CASCADE, tenant_id FK, owner_id UUID, forecast_category TEXT, amount NUMERIC(18,2), currency TEXT, period TEXT (e.g. "2026-Q2"), created_at | Period snapshots for forecasting |

**Indexes:** opportunities(tenant_id, owner_id), opportunities(tenant_id, stage), forecast_records(tenant_id, period)

---

### quote_order_db
**Purpose:** CPQ quotes, quote line items, orders, order line items (frozen at acceptance).

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| quotes | quote_id (PK UUID), tenant_id FK, opportunity_id UUID NOT NULL, owner_id UUID NOT NULL, status TEXT, valid_until DATE nullable, total_amount NUMERIC(18,2), currency TEXT, version_no INT, created_at, updated_at, accepted_at nullable | Status: draft/pending_approval/approved/accepted/rejected/expired |
| quote_line_items | line_item_id (PK UUID), quote_id FK CASCADE, tenant_id FK, product_id UUID, quantity, unit_price, discount_pct, total_price GENERATED STORED, created_at | |
| orders | order_id (PK UUID), tenant_id FK, quote_id FK, opportunity_id UUID, owner_id UUID, status TEXT, total_amount NUMERIC(18,2), currency TEXT, created_at, updated_at | Immutable post-creation. Status: pending_fulfillment/fulfilled/cancelled/refunded |
| order_line_items | line_item_id (PK UUID), order_id FK CASCADE, tenant_id FK, product_id UUID, product_name TEXT (denormalized snapshot), quantity, unit_price, currency, total_price, created_at | Denormalized snapshot of product name at order time |

---

### transaction_db
**Purpose:** Subscriptions, invoices, payments, payment events, revenue ledger, outbox events.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), tenant_name TEXT, status TEXT, created_at, updated_at | |
| subscription | subscription_id (PK UUID), tenant_id FK, account_id UUID NOT NULL, quote_id UUID nullable, plan_code TEXT, status TEXT, start_date DATE, end_date DATE nullable, renewal_date DATE nullable, external_subscription_ref TEXT, created_at, updated_at | Status: draft/trialing/active/paused/past_due/canceled/expired. UNIQUE(tenant_id, external_subscription_ref) |
| invoice_summary | invoice_summary_id (PK UUID), tenant_id, subscription_id FK, invoice_number TEXT, amount_due NUMERIC(18,2), amount_paid NUMERIC(18,2), currency CHAR(3), status TEXT, due_date DATE, issued_at, created_at, updated_at | Status: draft/open/paid/void/uncollectible. UNIQUE(tenant_id, invoice_number). Constraints: amount_paid <= amount_due |
| payment_event | payment_event_id (PK UUID), tenant_id, subscription_id nullable FK, invoice_summary_id nullable FK, event_type TEXT, amount NUMERIC(18,2), currency CHAR(3), event_time, status TEXT, external_payment_ref, created_at | Status: pending/succeeded/failed/refunded/reversed. Type: authorized/captured/settled/failed/refunded/chargeback |
| payment | payment_id (PK UUID), tenant_id, subscription_id nullable FK, invoice_summary_id nullable FK, payment_method_type TEXT, amount NUMERIC(18,2) CHECK >0, currency CHAR(3), status TEXT, initiated_at, authorized_at nullable, captured_at nullable, settled_at nullable, failed_at nullable, canceled_at nullable, refunded_at nullable, chargeback_at nullable, created_at, updated_at | Status: initiated/authorized/captured/settled/failed/canceled/partially_refunded/refunded/chargeback. Method: card/bank_transfer/wallet/ach/other |
| payment_status_history | payment_status_history_id (PK UUID), tenant_id, payment_id FK CASCADE, from_status nullable, to_status TEXT, reason TEXT, changed_at, changed_by_user_id nullable, created_at | Immutable status transition log |
| revenue_ledger | revenue_ledger_id (PK UUID), tenant_id, payment_id FK CASCADE, entry_type TEXT, amount_delta NUMERIC(18,2), currency CHAR(3), recognized_at, note TEXT, created_at | Entries created automatically on payment state transitions: settled→recognition; refunded→refund; chargeback→chargeback_adjustment |
| outbox_event | outbox_event_id (PK UUID), tenant_id FK, aggregate_type TEXT, aggregate_id UUID, event_type TEXT, event_version INT, payload_json JSONB, trace_id TEXT, correlation_id TEXT, occurred_at, recorded_at, published_at nullable, retry_count INT | Transactional outbox pattern. published_at NULL = unpublished |
| idempotency_key | idempotency_key_id (PK UUID), tenant_id FK, operation_name TEXT, idempotency_key TEXT, request_hash TEXT, response_json JSONB nullable, created_at, expires_at | UNIQUE(tenant_id, operation_name, idempotency_key) — for billing webhook dedup |

**DB Functions:** `is_valid_payment_status_transition()`, `apply_payment_status_transition()` — enforce FSM and write revenue_ledger entries atomically.

---

### case_ticket_db
**Purpose:** Support tickets (cases), SLA policies, escalation rules, assignments, history.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| sla_policies | policy_id (PK UUID), tenant_id FK, name TEXT, priority TEXT, response_minutes INT, resolution_minutes INT, business_hours_only BOOL, active BOOL, created_at, updated_at | UNIQUE(tenant_id, priority, active). Priority: low/medium/high/urgent |
| cases | ticket_id (PK UUID), tenant_id FK, account_id UUID nullable, contact_id UUID nullable, owner_user_id UUID NOT NULL, subject TEXT, description TEXT nullable, priority TEXT, status TEXT, sla_policy_id FK nullable, queue_name TEXT, sla_state TEXT, response_due_at nullable, resolution_due_at nullable, first_responded_at nullable, resolved_at nullable, closed_at nullable, version_no INT, created_at, updated_at | Status: open/in_progress/resolved/closed. SLA state: healthy/at_risk/breached |
| case_assignments | assignment_id (PK UUID), ticket_id FK CASCADE, tenant_id FK, owner_user_id UUID, assigned_by UUID nullable, reason TEXT, assigned_at | Historical assignment log |
| case_history | history_id (PK UUID), ticket_id FK CASCADE, tenant_id FK, changed_by UUID nullable, field_name TEXT, old_value TEXT, new_value TEXT, changed_at | Immutable field-change audit |
| sla_events | event_id (PK UUID), ticket_id FK CASCADE, tenant_id FK, event_type TEXT, old_sla_state TEXT, new_sla_state TEXT, occurred_at | Event types: response_due/resolution_due/state_change/breached |
| escalation_rules | rule_id (PK UUID), tenant_id FK, level INT, name TEXT, route_to TEXT, trigger TEXT, threshold_minutes INT, condition_field TEXT, condition_op TEXT, condition_value TEXT, action TEXT, active BOOL, created_at, updated_at | Action: reassign/raise_priority/page_on_call/request_manager_review |
| escalation_actions | action_id (PK UUID), ticket_id FK CASCADE, tenant_id FK, rule_id FK nullable, level INT, route_to TEXT, escalation_state TEXT, reason TEXT, escalated_at, resolved_at nullable | State: open/acknowledged/resolved |
| escalation_audit | audit_id (PK UUID), ticket_id FK CASCADE, tenant_id FK, event_type TEXT, details JSONB, created_at | Immutable escalation event log |

---

### messaging_db
**Purpose:** WhatsApp conversations, messages, message events, templates, sync queue, webhook dead-letter.

| Table | Key Columns | Notes |
|---|---|---|
| contacts | contact_id TEXT PK, tenant_id TEXT, normalized_phone TEXT, profile_name TEXT, locale TEXT, opt_in_whatsapp BOOL, tags JSONB, created_at, updated_at | UNIQUE(tenant_id, normalized_phone). Note: TEXT PKs (not UUID — provider-driven IDs) |
| conversations | conversation_id TEXT PK, tenant_id TEXT, channel TEXT, normalized_phone TEXT, contact_id FK, business_context TEXT, state TEXT, active_entity_type TEXT, active_entity_id TEXT, last_inbound_at, last_outbound_at, created_at, updated_at | UNIQUE(tenant_id, channel, normalized_phone, business_context) |
| messages | message_id TEXT PK, tenant_id TEXT, conversation_id FK, contact_id FK, direction TEXT (inbound/outbound), provider TEXT, provider_message_id TEXT, body TEXT, intent TEXT, status TEXT, payload_hash TEXT, retry_count INT, error_code TEXT, occurred_at, metadata JSONB, created_at | UNIQUE(tenant_id, provider, provider_message_id) — dedup |
| message_events | event_id TEXT PK, tenant_id TEXT, message_id FK, conversation_id FK, contact_id FK, event_type TEXT, status TEXT, provider TEXT, provider_message_id TEXT, payload_hash TEXT, error_code TEXT, details JSONB, occurred_at, created_at | |
| message_idempotency | (tenant_id, provider, event_scope, source_event_id) composite PK, processed_at | Dedup table for incoming webhooks |
| message_templates | template_id TEXT PK, tenant_id TEXT, provider TEXT, template_key TEXT, locale TEXT, category TEXT, body TEXT, params_schema JSONB, status TEXT, version INT, created_at, updated_at | UNIQUE(tenant_id, provider, template_key, locale, version) |
| sync_command_queue | command_id TEXT PK, tenant_id TEXT, device_id TEXT, idempotency_key TEXT, entity_type TEXT, entity_id TEXT, op TEXT (create/update/delete), payload JSONB, base_version INT, client_timestamp, status TEXT, retry_count INT, last_error TEXT, synced_at nullable, created_at | UNIQUE(tenant_id, idempotency_key). Status: pending/syncing/synced/failed/conflict/dead_letter |
| webhook_dead_letter | dead_letter_id TEXT PK, tenant_id TEXT nullable, provider TEXT, endpoint TEXT, payload JSONB, headers JSONB, failure_reason TEXT, attempt_count INT, first_failed_at, last_failed_at, resolved_at nullable, created_at | |

**Note:** messaging_db uses TEXT PKs (not UUID) — IDs are provider-assigned strings.

---

### workflow_db
**Purpose:** Workflow definitions (DSL), executions, step results.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| workflow_definitions | definition_id (PK UUID), tenant_id FK, name TEXT, trigger_type TEXT (event/schedule/manual/webhook), trigger_config JSONB, dsl_json JSONB, version INT, status TEXT, created_by UUID, created_at, updated_at | UNIQUE(tenant_id, name, version). Status: draft/active/paused/archived |
| workflow_executions | execution_id (PK UUID), tenant_id FK, definition_id FK, trigger_event_id TEXT nullable, entity_type TEXT, entity_id UUID, status TEXT, error_message TEXT, started_at, completed_at nullable | Status: running/completed/failed/cancelled/timed_out |
| workflow_steps | step_id (PK UUID), execution_id FK CASCADE, tenant_id FK, step_name TEXT, step_type TEXT (action/condition/wait/parallel), status TEXT, input_json JSONB, output_json JSONB, error_message TEXT, started_at nullable, completed_at nullable | Status: pending/running/completed/failed/skipped |

---

### intelligence_db
**Purpose:** AI scoring models, lead scores, score history, churn/CLV predictions, forecast snapshots.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| scoring_models | model_id (PK UUID), tenant_id FK, entity_type TEXT (lead/opportunity), version INT, status TEXT, created_at, updated_at | UNIQUE(tenant_id, entity_type, version). Status: active/deprecated/draft |
| model_feature_weights | weight_id (PK UUID), model_id FK CASCADE, tenant_id FK, factor_key TEXT, weight NUMERIC(8,4) CHECK >=0, created_at | UNIQUE(model_id, factor_key) |
| lead_scores | score_id (PK UUID), tenant_id FK, entity_id UUID NOT NULL (cross-schema lead_id), entity_type TEXT, model_id FK nullable, score INT CHECK 0-100, factors JSONB, scored_at | UNIQUE(tenant_id, entity_id) — one current score per lead |
| score_history | history_id (PK UUID), tenant_id FK, entity_id UUID, entity_type TEXT, model_id FK nullable, score INT, factors JSONB, scored_at | Immutable time-series of score changes |
| model_runs | run_id (PK UUID), tenant_id FK, model_id FK, entity_type TEXT, entities_scored INT, errors INT, status TEXT (running/completed/failed), started_at, completed_at nullable, error_detail TEXT | |
| forecast_snapshots | snapshot_id (PK UUID), tenant_id FK, period_start DATE, period_end DATE, entity_type TEXT, forecast_value NUMERIC(18,2), confidence NUMERIC(5,4) nullable, breakdown JSONB, model_run_id FK nullable, created_at | |

---

### campaign_db
**Purpose:** Campaigns, segments, campaign lead/contact links, journey definitions and instances.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| campaign_segments | segment_id (PK UUID), tenant_id FK, name TEXT, description TEXT, entity_type TEXT (lead/contact), rules JSONB array, created_at, updated_at | |
| campaigns | campaign_id (PK UUID), tenant_id FK, owner_user_id UUID, name TEXT, description TEXT, status TEXT (draft/active/completed), segment_id FK nullable, starts_at nullable, ends_at nullable, activated_at nullable, completed_at nullable, created_at, updated_at | |
| campaign_lead_links | campaign_lead_link_id (PK UUID), tenant_id FK, campaign_id FK CASCADE, lead_id UUID (app FK), membership_status TEXT, linked_at, updated_at | UNIQUE(campaign_id, lead_id). Status: pending/active/completed/removed |
| campaign_contact_links | campaign_contact_link_id (PK UUID), tenant_id FK, campaign_id FK CASCADE, contact_id UUID (app FK), membership_status TEXT, linked_at, updated_at | UNIQUE(campaign_id, contact_id) |
| journey_definitions | journey_id (PK UUID), tenant_id FK, name TEXT, trigger_event TEXT, steps JSONB array, is_active BOOL, created_at, updated_at | |
| journey_instances | instance_id (PK UUID), tenant_id FK, journey_id FK, trigger_event TEXT, trigger_event_id TEXT, status TEXT, current_step_index INT, started_at, waiting_until nullable, completed_at nullable, error_message TEXT, execution_log JSONB | Status: running/waiting/completed/failed/stopped |
| journey_step_events | step_event_id (PK UUID), instance_id FK CASCADE, tenant_id FK, step_id TEXT, action TEXT, outcome TEXT (success/failed/skipped), detail JSONB, executed_at | Immutable step execution records |

---

### territory_db
**Purpose:** Territory hierarchy, routing rules, subject assignments.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| territories | territory_id (PK UUID), tenant_id FK, name TEXT, code TEXT, parent_territory_id self-ref nullable, level INT (0=root), status TEXT (active/inactive), created_at, updated_at | UNIQUE(tenant_id, code) |
| territory_rules | rule_id (PK UUID), tenant_id FK, territory_id FK CASCADE, subject_type TEXT (user/team/account/lead), priority INT, criteria JSONB, owner_type TEXT (user/team), owner_id TEXT, active BOOL, created_at, updated_at | Rules evaluated in ascending priority; first match wins |
| territory_assignments | assignment_id (PK UUID), tenant_id FK, subject_type TEXT, subject_id UUID, territory_id FK, owner_type TEXT, owner_id TEXT, assignment_rule TEXT, assigned_at, superseded_at nullable | superseded_at NULL = current active assignment |

---

### activity_task_db
**Purpose:** Activity timeline records (immutable), general tasks, task schedules.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), tenant_name TEXT, status TEXT, created_at, updated_at | |
| activity | activity_id (PK UUID), tenant_id FK, actor_user_id UUID nullable, entity_type TEXT, entity_id UUID, event_type TEXT, event_time TIMESTAMPTZ, payload_json JSONB, source_service TEXT, created_at | Immutable. entity_type: lead/contact/account/opportunity/case/message_thread |
| task | task_id (PK UUID), tenant_id FK, entity_type TEXT, entity_id UUID, title TEXT, description TEXT, status TEXT, priority TEXT, assigned_user_id UUID nullable, created_by_user_id UUID, assignment_method TEXT, starts_at, due_at, completed_at nullable, created_at, updated_at | Status: open/in_progress/completed/canceled. Priority: low/normal/high/urgent. Assignment: explicit/entity_owner_fallback/least_loaded_candidate |
| task_schedule | task_schedule_id (PK UUID), tenant_id FK, name TEXT, schedule_type TEXT (immediate/delayed/recurring), cron TEXT nullable, timezone TEXT, run_at nullable, next_run_at nullable, enabled BOOL, concurrency_policy TEXT, misfire_policy TEXT, payload_template JSONB, last_run_at nullable, created_at, updated_at | UNIQUE(tenant_id, name). Shape constraint enforces cron/run_at/null based on type |

---

### knowledge_db
**Purpose:** Knowledge base articles, versions, categories, feedback.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| knowledge_articles | knowledge_article_id (PK UUID), tenant_id FK, title TEXT, slug TEXT, body_markdown TEXT, status TEXT (draft/published/archived), version INT, published_at nullable, created_at, updated_at | UNIQUE(tenant_id, slug) |
| article_versions | version_id (PK UUID), knowledge_article_id FK CASCADE, tenant_id FK, version INT, title TEXT, body_markdown TEXT, published_by UUID nullable, published_at | Immutable snapshot per publish. UNIQUE(knowledge_article_id, version) |
| article_categories | category_id (PK UUID), knowledge_article_id FK CASCADE, tenant_id FK, category TEXT, assigned_at | Many-to-many. Categories: getting_started/billing/integrations/troubleshooting/security/account_management. UNIQUE(knowledge_article_id, category) |
| article_feedback | feedback_id (PK UUID), knowledge_article_id FK CASCADE, tenant_id FK, user_id UUID nullable, helpful BOOL, comment TEXT, submitted_at | user_id NULL = anonymous |

---

### notification_db
**Purpose:** User-facing system notifications, templates, delivery log.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| notifications | notification_id (PK UUID), tenant_id FK, recipient_user_id UUID, type TEXT, channel TEXT (in_app/email/sms/push), status TEXT (pending/sent/delivered/read/failed), subject TEXT, body TEXT, metadata JSONB, sent_at nullable, delivered_at nullable, read_at nullable, created_at, updated_at | |
| notification_templates | template_id (PK UUID), tenant_id FK nullable (NULL=system template), key TEXT, locale TEXT, channel TEXT, subject TEXT, body TEXT (Handlebars/Jinja2), version INT, created_at, updated_at | UNIQUE(key, locale, channel, version) |
| delivery_log | log_id (PK UUID), notification_id FK CASCADE, tenant_id FK, provider TEXT (sendgrid/twilio/in_app), provider_message_id TEXT, status TEXT, error_code TEXT, attempted_at | |

---

### audit_compliance_db
**Purpose:** Immutable hash-chain audit log, compliance events.

| Table | Key Columns | Notes |
|---|---|---|
| tenant_ref | tenant_id (PK UUID), created_at | |
| audit_log | log_id (PK UUID), tenant_id FK, actor_user_id UUID nullable, action_type TEXT, entity_type TEXT, entity_id UUID, before_state JSONB, after_state JSONB, ip_address TEXT, user_agent TEXT, trace_id TEXT, source_service TEXT, hash TEXT (sha256), prev_hash TEXT (sha256 of previous; genesis='0'), occurred_at | **Append-only**: PostgreSQL RULE blocks UPDATE and DELETE. actor_user_id NULL = system entry |
| compliance_events | event_id (PK UUID), tenant_id FK, country TEXT (ISO-3166), action_type TEXT, entity_id UUID, payload JSONB, check_result TEXT (allowed/blocked), obligations TEXT[], report_ref TEXT, occurred_at | Country-specific regulatory obligation tracking |

---

### feature_flag_db
**Purpose:** Feature flags, targeting rules, evaluation log.

| Table | Key Columns | Notes |
|---|---|---|
| feature_flags | flag_id (PK UUID), key TEXT UNIQUE, name TEXT, description TEXT, default_value BOOL (FALSE=safe by default), status TEXT (active/archived), created_by UUID, created_at, updated_at | Global (not tenant-scoped) |
| flag_rules | rule_id (PK UUID), flag_id FK CASCADE, rule_type TEXT, condition_json JSONB, value BOOL, priority INT, created_at | rule_type: tenant/role/percentage/always_on/always_off. Evaluated in ascending priority order |
| flag_evaluations | eval_id (PK UUID), flag_id FK CASCADE, tenant_id UUID nullable, user_id UUID nullable, evaluated_value BOOL, rule_matched TEXT, evaluated_at | Sampled — not every evaluation |

---

## 4. Alembic Migrations (12 confirmed in alembic/versions/)

| Migration | File | Domain |
|---|---|---|
| 0001 | 0001_followup_schema.py | Follow-up tasks schema |
| 0002 | 0002_followup_states_leads_idempotency.py | Follow-up state machine, leads, idempotency |
| 0003 | 0003_collections_conversations.py | Collections + conversations |
| 0004 | 0004_cases_schema.py | Cases/tickets |
| 0005 | 0005_inbox_schema.py | Shared inbox |
| 0006 | 0006_territories_schema.py | Territory management |
| 0007 | 0007_campaigns_schema.py | Campaigns + segments |
| 0008 | 0008_partners_schema.py | Partner management |
| 0009 | 0009_workflows_schema.py | Workflow definitions + executions |
| 0010 | 0010_ai_scores_schema.py | AI scoring tables |
| 0011 | 0011_domain_schemas.py | Additional domain schemas |
| 0012 | 0012_lead_management_c1_columns.py | Lead management C1 column additions |

**Migration runner**: `POST /internal/migrate?secret=MIGRATE_SECRET` — runs `alembic upgrade head` via subprocess. Requires `MIGRATE_SECRET` env var.

---

## 5. Schema Coverage Analysis

| Pattern | Coverage |
|---|---|
| tenant_id on domain tables | 100% — all 18 schemas have tenant_id on every entity table |
| created_at audit column | 100% |
| updated_at audit column | ~85% — mutable tables have it; immutable tables (audit_log, activity, lead_history) intentionally omit it |
| updated_at trigger | 100% of tables with updated_at have the trigger |
| UUID primary key | ~95% — messaging_db uses TEXT PKs (provider-assigned IDs) |
| version_no (optimistic lock) | leads, contacts, accounts, opportunities, quotes, cases (6 entities) |
| Soft delete column | Not a universal pattern — most entities use status flags or dedicated closed/resolved states |

---

*End DATABASE_SCHEMA.md*
