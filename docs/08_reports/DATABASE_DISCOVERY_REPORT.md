Status: Draft
Authority Level: High
Last Reviewed: 2026-06-22
Owner: Shared

# DATABASE_DISCOVERY_REPORT.md
> Database discovery findings from Phase 2 Backend Authority Capture

---

## 1. Discovery Summary

All 18 domain schema SQL files were read in full. No schemas were invented or inferred.

**Total schemas:** 18  
**Location:** `backend/db/`  
**PostgreSQL version:** 14 (from render.yaml)  
**Migration system:** Alembic (12 migrations applied)

---

## 2. Schema Inventory

| # | Schema name | Directory | Key tables | Notable patterns |
|---|---|---|---|---|
| 1 | identity_auth_db | identity_auth_db/ | tenant_ref, users, roles, permissions, role_permissions, user_roles, sessions, refresh_tokens | Password: sha256:salt:hash |
| 2 | org_tenant_db | org_tenant_db/ | tenants, tenant_entitlements, organizations, organization_memberships | Plans: starter/growth/enterprise |
| 3 | lead_management_db | lead_management_db/ | tenant_ref, leads, lead_assignments, lead_history | lead_history immutable; 4 indexes on leads |
| 4 | contact_account_db | contact_account_db/ | tenant_ref, contacts, accounts, account_hierarchy | UNIQUE(tenant_id, phone_e164) on contacts; account self-ref hierarchy |
| 5 | opportunity_db | opportunity_db/ | tenant_ref, opportunities, opportunity_line_items, forecast_records | GENERATED STORED total_price on line items |
| 6 | quote_order_db | quote_order_db/ | tenant_ref, quotes, quote_line_items, orders, order_line_items | Orders immutable; order_line_items denormalize product_name |
| 7 | transaction_db | transaction_db/ | tenant_ref, subscription, invoice_summary, payment_event, payment, payment_status_history, revenue_ledger, outbox_event, idempotency_key | FSM enforcement via DB functions; revenue_ledger auto-updated |
| 8 | case_ticket_db | case_ticket_db/ | tenant_ref, sla_policies, cases, case_assignments, case_history, sla_events, escalation_rules, escalation_actions, escalation_audit | case_history immutable; sla_state: healthy/at_risk/breached |
| 9 | messaging_db | messaging_db/ | contacts (TEXT PK), conversations, messages, message_events, message_idempotency, message_templates, sync_command_queue, webhook_dead_letter | TEXT PKs (not UUID); UNIQUE(tenant+provider+provider_message_id) |
| 10 | workflow_db | workflow_db/ | tenant_ref, workflow_definitions, workflow_executions, workflow_steps | trigger_event_id for dedup; UNIQUE(tenant+name+version) |
| 11 | intelligence_db | intelligence_db/ | tenant_ref, scoring_models, model_feature_weights, lead_scores, score_history, model_runs, forecast_snapshots | UNIQUE(tenant+entity_id) on lead_scores — one score per lead |
| 12 | campaign_db | campaign_db/ | tenant_ref, campaign_segments, campaigns, campaign_lead_links, campaign_contact_links, journey_definitions, journey_instances, journey_step_events | journey_step_events immutable; segments use rules JSONB |
| 13 | territory_db | territory_db/ | tenant_ref, territories, territory_rules, territory_assignments | Hierarchy via level INT; first-match wins on rules; NULL superseded_at = active assignment |
| 14 | activity_task_db | activity_task_db/ | tenant_ref, activity, task, task_schedule | activity immutable; entity_type: lead/contact/account/opportunity/case/message_thread |
| 15 | knowledge_db | knowledge_db/ | tenant_ref, knowledge_articles, article_versions, article_categories, article_feedback | UNIQUE(tenant+slug) on articles; article_versions immutable per publish |
| 16 | notification_db | notification_db/ | tenant_ref, notifications, notification_templates, delivery_log | NULL tenant_id = system template |
| 17 | audit_compliance_db | audit_compliance_db/ | tenant_ref, audit_log, compliance_events | APPEND-ONLY via PostgreSQL RULE; hash-chain with prev_hash; genesis='0' |
| 18 | feature_flag_db | feature_flag_db/ | feature_flags, flag_rules, flag_evaluations | Not tenant-scoped (global); safe-by-default=OFF; rule_types: tenant/role/percentage/always_on/always_off |

---

## 3. Universal Patterns

**Primary key strategy:** `gen_random_uuid()` (pgcrypto extension) on all tables — except `messaging_db` which uses TEXT PKs (provider-assigned IDs)

**Tenant isolation pattern:**
- Every domain table has `tenant_id UUID NOT NULL`
- Every schema has a `tenant_ref` local table FK target
- `REFERENCES tenant_ref(tenant_id)` — prevents orphaned tenant data
- Exception: `feature_flag_db.feature_flags` has no `tenant_id` (global flags)

**Optimistic concurrency:** `version_no INTEGER NOT NULL DEFAULT 1` on leads, contacts, accounts, opportunities, quotes, cases

**Soft delete:** Only on leads (`is_deleted BOOLEAN`, `deleted_at TIMESTAMPTZ`). Other entities use status flags (e.g. `status = 'cancelled'`).

**Immutable tables:** audit_log (PostgreSQL RULE blocks UPDATE/DELETE), lead_history, case_history, activity, article_versions, journey_step_events, score_history

**JSONB usage:** custom_fields on leads/contacts/accounts/opportunities, campaign segment rules, territory criteria, workflow steps_dsl, journey steps, notification template variables

**Generated columns:** `opportunity_line_items.total_price`, `quote_line_items.total_price` — GENERATED STORED

---

## 4. Key Constraints Found

### Cross-schema FK strategy
**Finding:** NO cross-schema foreign keys. All cross-domain references (e.g. `contact_id` on leads pointing to contacts table) are stored as bare UUID columns with no FK constraint. Application layer enforces these references.

**Reason:** PostgreSQL supports cross-schema FKs but the design choice was to avoid them for schema autonomy and potential multi-DB deployment.

### Audit log APPEND-ONLY rule
```sql
-- In audit_compliance_db
CREATE RULE no_update_audit_log AS ON UPDATE TO audit_log DO INSTEAD NOTHING;
CREATE RULE no_delete_audit_log AS ON DELETE TO audit_log DO INSTEAD NOTHING;
```
This is enforced at the DB level — cannot be bypassed by application code.

### Payment FSM functions
Two PostgreSQL functions in transaction_db enforce payment status transitions:
- `is_valid_payment_status_transition(from_status, to_status)` → boolean
- `apply_payment_status_transition(payment_id, new_status)` → updates payment + creates revenue_ledger entry

---

## 5. Alembic Migrations (12 confirmed)

| Migration | Name |
|---|---|
| 0001 | followup_schema |
| 0002 | followup_scheduler |
| 0003 | followup_metrics |
| 0004 | collections_schema |
| 0005 | payments_schema |
| 0006 | activity_schema |
| 0007 | notifications_schema |
| 0008 | conversations_schema |
| 0009 | inbox_schema |
| 0010 | cases_schema |
| 0011 | ai_scoring_schema |
| 0012 | lead_management_c1_columns |

**Migration trigger:** POST /internal/migrate → runs `alembic upgrade head`

---

## 6. Gaps and Uncertainties

| Gap | Detail |
|---|---|
| Single DB vs multiple | render.yaml suggests single DATABASE_URL; unclear if all 18 schemas share one DB |
| Connection pool size (gateway) | backend/gateway/db/pool.js not read; pool size unknown |
| PostgreSQL RLS | No RLS found in any schema — all tenant isolation is application-level |
| Partners table | No dedicated partners schema found; likely in contact_account_db or activity_task_db |
| Custom objects | No DB schema for custom objects found; custom_object_framework module exists in src/ without DB counterpart |

---

*End DATABASE_DISCOVERY_REPORT.md*
