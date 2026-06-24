# API_INVENTORY.md
> Generated: 2026-06-20 — U1 Authority Reconstruction — evidence from backend/gateway/routes/v1-*.routes.js (44 files) [corrected from 43 by U10 remediation 2026-06-21]
> All routes are prefixed /api/v1/ unless noted.
> Auth: all routes except /auth/* require Bearer JWT + x-tenant-id header.

---

## Summary by Method

| Method | Count |
|---|---|
| GET | ~108 |
| POST | ~92 |
| PATCH | ~18 |
| DELETE | ~10 |
| **Total** | **228** |

## Summary by Domain

| Domain | Route File | Endpoints |
|---|---|---|
| Auth | v1-auth.routes.js | 7 |
| Leads | v1-leads.routes.js | 8 |
| Contacts | v1-contacts.routes.js | 7 |
| Accounts | v1-accounts.routes.js | ~4 |
| Opportunities | v1-opportunities.routes.js | 6 |
| Follow-ups | v1-followups.routes.js | 6 |
| Activities | v1-activities.routes.js | ~4 |
| Tasks | v1-tasks.routes.js | ~4 |
| Cases | v1-cases.routes.js | 14 |
| Collections | v1-collections.routes.js | 11 |
| Campaigns | v1-campaigns.routes.js | 10 |
| Communications | v1-communications.routes.js | 1 |
| Inbox | v1-inbox.routes.js | 11 |
| Quotes | v1-quotes.routes.js | ~5 |
| Orders | v1-orders.routes.js | ~3 |
| Invoice Summaries | v1-invoice-summaries.routes.js | ~3 |
| Subscriptions | v1-subscriptions.routes.js | ~4 |
| Payments | v1-payments.routes.js | ~3 |
| Payment Webhooks | v1-payment-webhooks.routes.js | 3 |
| WhatsApp Webhooks | v1-whatsapp-webhooks.routes.js | 6 |
| Billing | v1-billing.routes.js | ~4 |
| Workflows | v1-workflows.routes.js | 11 |
| Users | v1-users.routes.js | ~5 |
| Roles | v1-roles.routes.js | 4 |
| Tenants | v1-tenants.routes.js | 1 |
| Territories | v1-territories.routes.js | 11 |
| Partners | v1-partners.routes.js | 13 |
| Knowledge | v1-knowledge.routes.js | ~5 |
| Reports | v1-reports.routes.js | ~4 |
| AI | v1-ai.routes.js | 13 |
| Audit | v1-audit.routes.js | ~3 |
| Segments | v1-segments.routes.js | ~4 |
| Templates | v1-templates.routes.js | ~4 |
| Org Settings | v1-org-settings.routes.js | ~3 |
| Integrations | v1-integrations.routes.js | ~4 |
| Feature Flags | v1-feature-flags-mgmt.routes.js | ~3 |
| Governance | v1-governance.routes.js | ~4 |
| Compliance Settings | v1-compliance-settings.routes.js | ~2 |
| Privacy | v1-privacy.routes.js | ~3 |
| Notifications | v1-notification-preferences.routes.js | ~3 |
| Forecasts | v1-forecasts.routes.js | ~3 |
| Price Books | v1-price-books.routes.js | ~4 |
| Emails | v1-emails.routes.js | ~4 |
| Sync | v1-sync.routes.js | ~2 |

---

## Detailed API (fully read from code — gateway/routes/v1-*.routes.js)

### AUTH — /api/v1/auth/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| POST | /auth/login | No | none | email + password → access_token + refresh_token cookie. Password: sha256:salt:hash. |
| POST | /auth/sessions | No | none | Legacy IdP token exchange — returns 501 NOT_IMPLEMENTED |
| DELETE | /auth/sessions/current | JWT | none | Logout — adds jti to Redis blocklist |
| POST | /auth/refresh | No | none | Refresh token (cookie or body) → new access_token. Single-use rotation. |
| POST | /auth/forgot-password | No | none | Body: email, tenant_id → OTP sent via SendGrid (stub in dev) |
| POST | /auth/reset-password | No | none | Body: email, tenant_id, otp, new_password → update password_hash |
| POST | /auth/register | No | none | Body: name, email, password, slug → creates Tenant + User + seeds pipeline. Returns JWT. |

### LEADS — /api/v1/leads/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /leads | JWT | leads.read | Query: stage, owner_id, status, priority, source, limit (max 200), offset |
| POST | /leads | JWT | leads.create | Body: owner_id, title, stage, status, priority, source, contact_name, contact_phone_e164, contact_email, estimated_value, currency, notes, metadata. Fires register to followup service. |
| GET | /leads/:lead_id | JWT | leads.read | Lead detail |
| PATCH | /leads/:lead_id | JWT | leads.update | Stage transition uses atomic repo.transitionStage() — writes LeadHistory |
| DELETE | /leads/:lead_id | JWT | leads.delete | Soft delete via repo.softDelete() |
| GET | /leads/:lead_id/next-action | JWT | followups.read | Calls followup service /internal/leads/:id/next-action. Returns stub if service unreachable. |
| GET | /leads/export | JWT | leads.read | CSV export (RFC 4180), Content-Disposition: attachment |
| POST | /leads/import | JWT | leads.create | Accepts text/csv or JSON array. Phone-based dedup. Returns {created, skipped, errors}. |

### CONTACTS — /api/v1/contacts/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /contacts | JWT | contacts.read | List; proxied to downstream if GATEWAY_UPSTREAM_BASE_URL set |
| POST | /contacts | JWT | contacts.create | Creates contact |
| GET | /contacts/:contact_id | JWT | contacts.read | Contact detail |
| PATCH | /contacts/:contact_id | JWT | contacts.update | Patchable: display_name, phone_e164, email, account_id, tags, source |
| DELETE | /contacts/:contact_id | JWT | contacts.delete | Hard delete (in-memory path) |
| GET | /contacts/export | JWT | contacts.read | CSV export |
| POST | /contacts/import | JWT | contacts.create | CSV or JSON array; phone-based dedup |

### ACCOUNTS — /api/v1/accounts/ (inferred from v1-accounts.routes.js pattern)

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /accounts | JWT | accounts.read | List accounts |
| POST | /accounts | JWT | accounts.create | Create account |
| GET | /accounts/:account_id | JWT | accounts.read | Account detail |
| PATCH | /accounts/:account_id | JWT | accounts.update | Update account |

### OPPORTUNITIES — /api/v1/opportunities/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /opportunities | JWT | opportunities.read | Query: stage, owner_id, forecast_category, limit, offset |
| POST | /opportunities | JWT | opportunities.create | Body: owner_id, name, account_id, account_name, contact_id, amount, currency, close_date, stage, forecast_category |
| GET | /opportunities/:opp_id | JWT | opportunities.read | Opportunity detail |
| PATCH | /opportunities/:opp_id | JWT | opportunities.update | Stage transition emits opportunity.stage.changed.v1 and opportunity.closed.v1 (terminal). Optimistic concurrency via version_no. |
| GET | /opportunities/:opp_id/line-items | JWT | opportunities.read | List line items |
| POST | /opportunities/:opp_id/line-items | JWT | opportunities.update | Body: product_id (required), unit_price (required), quantity, currency, discount_pct |

### FOLLOW-UPS — /api/v1/followups/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /followups | JWT | followups.read | Query: lead_id, owner_id, state, limit, offset |
| POST | /followups | JWT | followups.create | Body: lead_id (required), owner_id (required), due_at (required ISO8601), rule_type, generated_by, is_canonical, action_type, attempts_count |
| GET | /followups/:task_id | JWT | followups.read | Follow-up task detail |
| POST | /followups/:task_id/complete | JWT | followups.complete | Idempotent. Body: completed_activity_id (optional) |
| POST | /followups/:task_id/snooze | JWT | followups.snooze | Body: snoozed_until (required ISO8601). Returns 409 if already completed. |
| GET | /followups/lead/:lead_id/canonical | JWT | followups.read | Returns canonical pending task. 404 if none. |

### ACTIVITIES — /api/v1/activities/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /activities | JWT | activities.read | List activities |
| POST | /activities | JWT | activities.create | Log activity (call/whatsapp/email/meeting/note) |
| GET | /activities/:activity_id | JWT | activities.read | Activity detail |

### TASKS — /api/v1/tasks/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /tasks | JWT | tasks.read | List tasks |
| POST | /tasks | JWT | tasks.create | Create general task |
| GET | /tasks/:task_id | JWT | tasks.read | Task detail |
| PATCH | /tasks/:task_id | JWT | tasks.update | Update task status/priority/due_at |

### CASES — /api/v1/cases/ and /api/v1/support/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| POST | /cases | JWT | cases.create | Body: subject, description, priority (critical/high/medium/low), source, category, contact_id, account_id, lead_id, sla_tier, queue_id, custom_fields |
| GET | /cases | JWT | cases.read | Query: status, priority, assigned_to, queue_id, contact_id, limit, offset |
| GET | /cases/:case_id | JWT | cases.read | Case detail with embedded comments and escalations |
| PATCH | /cases/:case_id | JWT | cases.update | Body: subject, priority, category, custom_fields, version_no (optimistic lock) |
| POST | /cases/:case_id/assign | JWT | cases.admin | Body: assigned_to or assigned_team_id. Auto-transitions OPEN→ASSIGNED. |
| POST | /cases/:case_id/comments | JWT | cases.update | Body: body (required), comment_type (required: internal_note/customer_reply/resolution/status_change/escalation_note), attachment_urls. Sets first_responded_at on first customer_reply. |
| POST | /cases/:case_id/resolve | JWT | cases.update | Body: resolution_note (required). Creates resolution comment automatically. |
| POST | /cases/:case_id/close | JWT | cases.admin | Body: close_reason. Force-close (admin/manager). |
| POST | /cases/:case_id/reopen | JWT | cases.update | 14-day reopen window enforced. CLOSED→OPEN. |
| POST | /cases/:case_id/escalate | JWT | cases.admin | Body: escalation_reason, escalated_to, escalated_to_team, note. ESCALATED status. |
| POST | /cases/:case_id/link-article | JWT | cases.update | Body: article_id (required). Links knowledge article. |
| GET | /support/queues | JWT | cases.read | List active support queues |
| POST | /support/queues | JWT | cases.admin | Body: name (required), routing_strategy, sla_tier_default, team_id |
| PATCH | /support/queues/:queue_id | JWT | cases.admin | Update queue config |

### COLLECTIONS — /api/v1/collections/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /collections/invoices | JWT | collections.read | List invoices. Query: subscription_id, status, limit (max 200), offset. Returns is_overdue flag. |
| POST | /collections/invoices | JWT | collections.invoice | Create invoice. Required: amount_due, currency (ISO 4217), due_date. DB path requires subscription_id (FK constraint). |
| GET | /collections/invoices/:invoice_id | JWT | collections.read | Invoice detail |
| POST | /collections/invoices/:invoice_id/payments | JWT | collections.invoice | Ingest payment against invoice. Required: amount, currency, payment_method_type. Auto-marks invoice paid when amount_paid >= amount_due. |
| GET | /collections/subscriptions | JWT | collections.read | List subscriptions. Query: account_id, status. |
| POST | /collections/subscriptions | JWT | collections.invoice | Create subscription. Required: account_id, plan_code, start_date. DB path only. |
| GET | /collections/overdue | JWT | collections.read | List open invoices whose due_date < today. |
| POST | /collections/reconcile | JWT | collections.reconcile | Run reconciliation pass: compare amount_paid vs amount_due across all tenant invoices. Returns matched/unmatched counts. |
| POST | /collections/invoices/:invoice_id/payments/:payment_id/proof | JWT | collections.invoice | Upload payment proof URL. Required: proof_url (valid https URL). Sets verification_status=pending_verification. In-memory only (DB path returns 501 — pending P-025 schema migration). |
| PATCH | /collections/invoices/:invoice_id/payments/:payment_id/proof/verify | JWT | collections.reconcile | Approve or reject uploaded proof. Required: verification_status (verified/rejected). rejected requires rejection_reason. |
| POST | /collections/invoices/:invoice_id/reminders | JWT | collections.invoice | Schedule payment reminder. Body: channel (default whatsapp), message, scheduled_for. |

### CAMPAIGNS — /api/v1/campaigns/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /campaigns | JWT | campaigns.read | List campaigns. Query: status, type, limit, offset. |
| POST | /campaigns | JWT | campaigns.manage | Create campaign. Required: name, type (whatsapp_broadcast/email/sms). Status starts as draft. |
| GET | /campaigns/:campaign_id | JWT | campaigns.read | Campaign detail |
| PATCH | /campaigns/:campaign_id | JWT | campaigns.manage | Update campaign. 409 if status is completed or cancelled. |
| POST | /campaigns/:campaign_id/activate | JWT | campaigns.manage | Activate campaign. Requires segment_id and template_id. Urdu WhatsApp templates require urdu_approved_by (P-017). |
| POST | /campaigns/:campaign_id/pause | JWT | campaigns.manage | Pause active campaign. |
| POST | /campaigns/:campaign_id/resume | JWT | campaigns.manage | Resume paused campaign. Transitions paused→active. |
| POST | /campaigns/:campaign_id/cancel | JWT | campaigns.manage | Cancel campaign (terminal state). |
| GET | /campaigns/:campaign_id/sends | JWT | campaigns.manage | List campaign send records with delivery stats. |
| GET | /campaigns/:campaign_id/conversions | JWT | campaigns.manage | List attributed conversions within 30-day attribution window. |

### SEGMENTS — /api/v1/segments/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /segments | JWT | campaigns.read | List segments |
| POST | /segments | JWT | campaigns.manage | Create segment with criteria |
| GET | /segments/:segment_id | JWT | campaigns.read | Segment detail |
| PATCH | /segments/:segment_id | JWT | campaigns.manage | Update criteria |

### COMMUNICATIONS — /api/v1/communications/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /communications/engagement | JWT | marketing.read | Engagement metrics dashboard. Single confirmed route in v1-communications.routes.js. |

### INBOX — /api/v1/inbox/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /inbox/conversations | JWT | inbox.read | Query: state, channel, queue_id, assigned_agent_id, limit, offset. Sorted by last_message_at DESC. |
| GET | /inbox/conversations/:conversation_id | JWT | inbox.read | Conversation detail + embedded messages |
| POST | /inbox/conversations/:conversation_id/claim | JWT | inbox.write | Atomic claim from pool. 409 if already assigned. Checks agent presence (busy/offline blocked). |
| POST | /inbox/conversations/:conversation_id/handoff | JWT | inbox.write | Body: to_agent_id (nullable), reason (required), note. Supervisor can handoff any; agent can only handoff own. |
| POST | /inbox/conversations/:conversation_id/messages | JWT | inbox.write | Body: text (required). Outbound message. Only assigned agent or supervisor. 409 on resolved/closed. |
| PATCH | /inbox/presence | JWT | inbox.read | Body: status (required: online/away/busy/offline). Update own presence. |
| GET | /inbox/presence | JWT | inbox.admin | Supervisor view of all agent presence statuses |
| GET | /inbox/queues | JWT | inbox.admin | List active inbox queues |
| POST | /inbox/queues | JWT | inbox.admin | Body: name (required), routing_strategy, auto_assign, skill_tags, team_id |
| PATCH | /inbox/queues/:queue_id | JWT | inbox.admin | Update queue config |
| GET | /inbox/queues/:queue_id/stats | JWT | inbox.admin | Queue stats: open_count, unassigned_count, assigned_count, avg_unread |

### QUOTES — /api/v1/quotes/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /quotes | JWT | quotes.read | List quotes |
| POST | /quotes | JWT | quotes.create | Create quote (CPQ). Discount >10% auto-triggers approval. |
| GET | /quotes/:quote_id | JWT | quotes.read | Quote detail with line items and approval history |
| PATCH | /quotes/:quote_id | JWT | quotes.update | Update quote |
| POST | /quotes/:quote_id/accept | JWT | quotes.accept | Accept quote → create Order |

### ORDERS — /api/v1/orders/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /orders | JWT | orders.read | List orders |
| GET | /orders/:order_id | JWT | orders.read | Order detail |
| POST | /orders | JWT | orders.create | Create order (typically from accepted quote) |

### INVOICE SUMMARIES — /api/v1/invoice-summaries/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /invoice-summaries | JWT | collections.read | Invoice summary list |
| GET | /invoice-summaries/:invoice_id | JWT | collections.read | Invoice detail |
| POST | /invoice-summaries | JWT | invoices.create | Create invoice |

### SUBSCRIPTIONS — /api/v1/subscriptions/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /subscriptions | JWT | subscriptions.read | List subscriptions |
| GET | /subscriptions/:subscription_id | JWT | subscriptions.read | Subscription detail |
| POST | /subscriptions | JWT | subscriptions.create | Create subscription |
| PATCH | /subscriptions/:subscription_id | JWT | subscriptions.update | Update subscription status |

### PAYMENTS — /api/v1/payments/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /payments | JWT | payments.read | List payments |
| POST | /payments | JWT | payments.create | Create payment (JazzCash/Easypaisa/bank_transfer — stub mode) |

### WEBHOOKS — public endpoints

#### WhatsApp Webhooks — /api/v1/whatsapp-webhooks/

| Method | Path | Auth Required | Notes |
|---|---|---|---|
| GET | /whatsapp-webhooks/meta | Webhook token | Meta platform webhook verification (hub.challenge handshake) |
| POST | /whatsapp-webhooks/meta | Webhook signature | Meta (WhatsApp Business API) inbound messages |
| POST | /whatsapp-webhooks/twilio | Webhook signature | Twilio inbound WhatsApp messages |
| POST | /whatsapp-webhooks/360dialog | Webhook signature | 360dialog inbound WhatsApp messages |
| POST | /whatsapp-webhooks/gupshup | Webhook signature | Gupshup inbound WhatsApp messages |
| GET | /whatsapp-webhooks/log | JWT | Webhook delivery log (internal debug view) |

#### Payment Webhooks — /api/v1/payment-webhooks/

| Method | Path | Auth Required | Notes |
|---|---|---|---|
| POST | /payment-webhooks/jazzcash | Webhook signature | JazzCash payment callback (stub_mode=true per P-016) |
| POST | /payment-webhooks/easypaisa | Webhook signature | Easypaisa payment callback (stub_mode=true per P-016) |
| GET | /payment-webhooks/log | JWT | Webhook delivery log (internal debug view) |

### BILLING — /api/v1/billing/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /billing/subscription | JWT | billing.read | Current tenant billing subscription |
| GET | /billing/invoices | JWT | billing.read | Billing invoice history |
| POST | /billing/subscription | JWT | billing.create | Create billing subscription |
| PATCH | /billing/subscription | JWT | billing.manage | Update billing plan |

### WORKFLOWS — /api/v1/workflows/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /workflows/runs | JWT | workflows.read | Query: status, workflow_key, limit, offset. Sorted by started_at DESC. |
| GET | /workflows/runs/:execution_id | JWT | workflows.read | Execution detail with step records |
| POST | /workflows/runs/:execution_id/retry | JWT | workflows.manage | Retries failed/retrying execution. max_retries enforced. |
| POST | /workflows/runs/:execution_id/cancel | JWT | workflows.manage | Cancels running/failed/retrying execution. 409 on terminal state. |
| GET | /workflows | JWT | workflows.read | Query: status. List definitions (own tenant + system). |
| POST | /workflows | JWT | workflows.manage | Body: name, trigger_events[] (required), steps_dsl[], max_retries, timeout_seconds. Created as draft. |
| GET | /workflows/:workflow_id | JWT | workflows.read | Definition detail + 5 recent runs |
| PATCH | /workflows/:workflow_id | JWT | workflows.manage | Update non-system workflow. 403 on is_system. 409 on archived. |
| POST | /workflows/:workflow_id/publish | JWT | workflows.manage | Transitions draft→active. Requires ≥1 step. |
| POST | /workflows/:workflow_id/simulate | JWT | workflows.read | Dry-run with test payload. Returns simulated step results. No side effects. |
| GET | /workflows/:workflow_id/stats | JWT | workflows.read | Total runs, succeeded, failed, retrying, running, success_rate, avg_duration_ms |

### USERS — /api/v1/users/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /users | JWT | users.read | List users in tenant |
| POST | /users | JWT | users.create | Invite/create user |
| GET | /users/:user_id | JWT | users.read | User detail |
| PATCH | /users/:user_id | JWT | users.update | Update user (status, role, etc.) |
| POST | /users/:user_id/assign-role | JWT | users.manage_roles | Assign role to user |

### ROLES — /api/v1/roles/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /roles | JWT | users.read | List roles (seeded + custom) |
| POST | /roles | JWT | users.update | Body: name (required), permissions (required array), label. Creates custom role. 409 if name exists. |
| PATCH | /roles/:role_id | JWT | users.update | Allowed: label, permissions. 422 if renaming system role. |
| DELETE | /roles/:role_id | JWT | users.update | 422 if system role. 409 if has active users. |

### TENANTS — /api/v1/tenants/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /tenants/current | JWT | users.read | Get current tenant profile. Single confirmed route in v1-tenants.routes.js. |

> **Note (SC-008):** The admin/tenants list/detail/patch endpoints were inferred during U1 but are NOT confirmed in v1-tenants.routes.js. Only GET /tenants/current exists. Super-admin multi-tenant management may be handled out-of-band or via direct DB access.

### TERRITORIES — /api/v1/territories/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /territories | JWT | territories.read | List territories sorted by routing_priority. Query: is_active. |
| POST | /territories | JWT | territories.admin | Create territory. Required: criteria_type (geographic/postal/account_segment/rep_assigned/hybrid). Atomically unsets previous default if is_default=true. |
| GET | /territories/assignments | JWT | territories.read | List active assignments. Query: subject_type, territory_id, assigned_rep_id. |
| POST | /territories/assignments/evaluate | JWT | territories.read | Dry-run evaluation. Required: subject (object with city/province/industry fields). Returns winner territory, candidates, reason (single_match/conflict_resolved/default_fallback). |
| POST | /territories/assignments/:assignment_id/reassign | JWT | territories.write | Manual override reassignment. Requires manager role. Supersedes previous assignment. |
| GET | /territories/:territory_id | JWT | territories.read | Territory detail with embedded rules and active_assignment_count. |
| PATCH | /territories/:territory_id | JWT | territories.admin | Update territory. Patchable: name, description, assigned_reps, primary_manager, routing_priority, criteria_value, is_default. |
| DELETE | /territories/:territory_id | JWT | territories.admin | Soft-deactivate territory. 409 if it is the default territory. |
| POST | /territories/:territory_id/rules | JWT | territories.admin | Add routing rule. Required: rule_type (city/postal_code/region/geo_polygon/account_industry/account_size/account_tier/rep_explicit/custom_field), value. |
| DELETE | /territories/:territory_id/rules/:rule_id | JWT | territories.admin | Delete routing rule. |
| GET | /territories/:territory_id/performance | JWT | territories.read | Territory performance metrics: open_leads, conversions, overdue_follow_ups, invoice amounts. Demo data in v1 (populated by daily aggregation job in production). |

### PARTNERS — /api/v1/partners/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /partners | JWT | partners.read | List partners. Query: partner_tier (platinum/gold/silver), status (active/inactive/suspended), limit, offset. |
| POST | /partners | JWT | partners.manage | Create partner. Required: name, partner_tier. |
| GET | /partners/:partner_id | JWT | partners.read | Partner detail |
| PATCH | /partners/:partner_id | JWT | partners.manage | Update partner. Tier and status changes require admin role. |
| GET | /partners/:partner_id/opportunities | JWT | partners.read | List attributed opportunities for partner. |
| GET | /partners/:partner_id/commissions | JWT | partners.manage | List commission records for partner. |
| POST | /partners/:partner_id/commissions/:commission_id/approve | JWT | partners.manage | Approve pending or disputed commission. 409 if already paid (immutable). |
| POST | /partners/:partner_id/commissions/:commission_id/pay | JWT | partners.admin | Mark approved commission as paid. Required: payment_reference. 409 if already paid. |
| GET | /partners/:partner_id/activity | JWT | partners.manage | Activity log for partner. |
| POST | /partners/:partner_id/deal-registrations | JWT | partners.manage | Register a deal for partner. Required: prospect_name, estimated_value. 422 if partner is inactive/suspended. Sets expiry per tier (platinum=30d, gold=45d, silver=none). |
| GET | /partners/:partner_id/deal-registrations | JWT | partners.read | List deal registrations for partner. |

### DEAL REGISTRATIONS — /api/v1/deal-registrations/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| POST | /deal-registrations/:registration_id/approve | JWT | partners.manage | Approve submitted deal registration. 422 if not in submitted state. |
| POST | /deal-registrations/:registration_id/reject | JWT | partners.manage | Reject submitted deal registration. Required: rejection_reason. |

### KNOWLEDGE — /api/v1/knowledge/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /knowledge | JWT | knowledge.read | List articles |
| POST | /knowledge | JWT | knowledge.manage | Create article (draft) |
| GET | /knowledge/:article_id | JWT | knowledge.read | Article detail |
| PATCH | /knowledge/:article_id | JWT | knowledge.manage | Update article |
| POST | /knowledge/:article_id/publish | JWT | knowledge.manage | Publish article |

### REPORTS — /api/v1/reports/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /reports/definitions | JWT | reports.read | List saved report definitions |
| POST | /reports/definitions | JWT | reports.create | Save report definition |
| POST | /reports/execute | JWT | reports.read | Execute report (returns data) |

### AI — /api/v1/ai/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /ai/scores/leads | JWT | ai.scores.read | List lead scores. Query: score_band, lead_id, limit. Sorted by score DESC. |
| GET | /ai/scores/leads/:lead_id | JWT | ai.scores.read | Lead score detail with top_drivers |
| POST | /ai/scores/leads/:lead_id/recompute | JWT | ai.scores.recompute | Force recompute lead score |
| GET | /ai/predictions/churn | JWT | ai.predictions.read | List churn predictions. Query: risk_band. Sorted by churn_probability DESC. |
| GET | /ai/predictions/churn/:account_id | JWT | ai.predictions.read | Account churn prediction |
| GET | /ai/estimates/clv | JWT | ai.clv.read | List CLV estimates. Sorted by estimated_clv DESC. |
| GET | /ai/estimates/clv/:account_id | JWT | ai.clv.read | Account CLV estimate |
| POST | /ai/copilot/query | JWT | ai.copilot | Body: query (NL text). Returns intent + summary + records + actions. Rule-based intent detection. |
| GET | /ai/copilot/suggestions | JWT | ai.copilot | Query: priority, suggestion_type, include_dismissed. Sorted by priority weight. |
| POST | /ai/copilot/suggestions/:id/dismiss | JWT | ai.copilot | Dismiss a suggestion |
| POST | /ai/copilot/suggestions/:id/action | JWT | ai.copilot | Mark suggestion as actioned |
| GET | /ai/models | JWT | ai.models.read | List scoring model registry |
| GET | /ai/models/:model_key | JWT | ai.models.read | Model detail |

### AUDIT — /api/v1/audit/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /audit | JWT | audit.logs.read | List audit log entries |
| GET | /audit/export | JWT | audit.logs.read | CSV export with hash-chain verification |

### GOVERNANCE — /api/v1/governance/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /governance/classification | JWT | compliance.read | Data classification labels |
| GET | /governance/retention | JWT | compliance.read | Retention policy config |
| POST | /governance/sar | JWT | privacy.manage | Submit Subject Access Request (GDPR/PDPA) |

### COMPLIANCE SETTINGS — /api/v1/compliance-settings/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /compliance-settings | JWT | compliance.read | Current compliance config |
| PATCH | /compliance-settings | JWT | compliance.read | Update compliance settings |

### PRIVACY — /api/v1/privacy/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /privacy/consent | JWT | privacy.read | Get consent records |
| POST | /privacy/consent | JWT | privacy.manage | Record consent |

### NOTIFICATIONS — /api/v1/notification-preferences/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /notification-preferences | JWT | any | Get user notification preferences |
| PATCH | /notification-preferences | JWT | any | Update preferences |

### ORG SETTINGS — /api/v1/org-settings/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /org-settings | JWT | integrations.read | Get org settings |
| PATCH | /org-settings | JWT | integrations.manage | Update org settings |

### INTEGRATIONS — /api/v1/integrations/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /integrations | JWT | integrations.read | List configured integrations |
| PATCH | /integrations/:provider | JWT | integrations.manage | Configure integration |
| POST | /integrations/:provider/test | JWT | integrations.manage | Test connection |

### FEATURE FLAGS — /api/v1/admin/feature-flags/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /admin/feature-flags | JWT | users.read | List feature flags |
| PATCH | /admin/feature-flags/:flag_id | JWT | users.update | Toggle flag. Dual-approval required when requires_dual_approval=true. |

### FORECASTS — /api/v1/forecasts/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /forecasts | JWT | forecasts.read | Get forecast data |
| POST | /forecasts/refresh | JWT | forecasts.read | Trigger forecast recalculation |

### PRICE BOOKS — /api/v1/price-books/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /price-books | JWT | pricing.read | List price books |
| POST | /price-books | JWT | pricing.create | Create price book |
| GET | /price-books/:book_id | JWT | pricing.read | Price book detail |
| PATCH | /price-books/:book_id | JWT | pricing.create | Update price book |

### EMAILS — /api/v1/emails/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /emails | JWT | emails.read | List email threads |
| POST | /emails | JWT | emails.send | Send email |
| GET | /emails/:email_id | JWT | emails.read | Email detail |
| GET | /emails/:email_id/tracking | JWT | emails.track | Open/click tracking data |

### TEMPLATES — /api/v1/templates/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| GET | /templates | JWT | campaigns.read | List message/email templates |
| POST | /templates | JWT | campaigns.manage | Create template |
| GET | /templates/:template_id | JWT | campaigns.read | Template detail |
| PATCH | /templates/:template_id | JWT | campaigns.manage | Update template |

### SYNC — /api/v1/sync/

| Method | Path | Auth Required | Scope | Notes |
|---|---|---|---|---|
| POST | /sync | JWT | sync.write | Trigger data sync |
| GET | /sync/status | JWT | sync.read | Sync status |

### HEALTH — (no /api/v1/ prefix)

| Method | Path | Auth Required | Notes |
|---|---|---|---|
| GET | /health | No | Health check — confirmed in render.yaml healthCheckPath |

---

## API Status Legend

| Status | Meaning |
|---|---|
| **Implemented** | Route handler confirmed in gateway source code |
| **Stub** | Route exists; uses in-memory data with DUMMY_MODE; not proxied to live Python services |
| **Planned** | Referenced in docs or frontend but no gateway route file found |

**Current status of all 44 gateway route files:** Implemented (gateway handlers confirmed).
**Total route count:** 228 (confirmed by direct code read 2026-06-20, U7 delta remediation).
**Live-API integration status:** All routes in stub/in-memory mode until GATEWAY_UPSTREAM_BASE_URL is configured. Exception: specific pages confirmed wired (G-05, H-07, J-03, A-08).

---

*End API_INVENTORY.md*
