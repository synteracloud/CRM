---
Status: Active
Authority Level: Critical
Created: 2026-06-23
Derived From: API_CONTRACT.md (228 endpoints, 44 gateway route groups), FULLSTACK_STITCHING_CONTRACT.md, DESIGN-SPEC.md
---

# FRONTEND API DEPENDENCY MAP — Pakistan CRM OS

228 API endpoints mapped to their frontend consumers. Grouped by module/domain.

**Auth pattern:** All protected endpoints require `Authorization: Bearer {accessToken}` header.
**Tenant pattern:** `x-tenant-id` extracted from JWT by gateway — frontend never sets manually.
**Idempotency:** Frontend MUST generate `Idempotency-Key` header on all POST/PUT/PATCH requests.
**Base path:** /api/v1/
**Gateway route groups:** 44 total

---

## Module 1: Authentication (Public — No Auth Required)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| POST | /auth/login | login-basic.html (library) | Email+password login → access_token + refresh cookie | No | None |
| POST | /auth/register | register-basic.html (library) | Tenant + user registration → JWT | No | None |
| POST | /auth/refresh | All pages (silent renewal) | Refresh access token via HttpOnly cookie | No (uses cookie) | None |
| DELETE | /auth/sessions/current | All pages (logout) | Logout; revoke JTI in Redis blocklist | Yes | None |
| POST | /auth/forgot-password | forgot-password-basic.html (library) | Generate 6-digit OTP via SendGrid | No | None |
| POST | /auth/reset-password | new-password-basic.html (library) | Reset password with OTP | No | None |
| POST | /auth/sessions | N/A | Legacy IdP token exchange (returns 501) | No | None |

---

## Module 2: Lead Management (v1-leads.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /leads | leads.html (B-02), leads-dashboard.html (A-02), dashboard.html (A-01), sales-cockpit.html (D-01) | List leads with filters (stage, priority, status, owner_id) | Yes | leads.read |
| POST | /leads | lead-new.html (I-01) | Create lead; emits lead.created.v1 | Yes | leads.create |
| GET | /leads/:id | leads-detail.html (C-01) | Lead detail with full fields | Yes | leads.read |
| PATCH | /leads/:id | leads-detail.html (C-01) | Update stage, priority, owner, fields | Yes | leads.update |
| DELETE | /leads/:id | leads-detail.html (C-01) | Soft delete (sets deleted_at) | Yes | leads.delete |
| GET | /leads/export | leads.html (B-02) | CSV export of lead list | Yes | leads.export |
| POST | /leads/import | leads.html (B-02) | Bulk CSV/JSON import with phone dedup | Yes | leads.import |
| GET | /leads/:id/next-action | leads-detail.html (C-01), ai-copilot.html (M-01) | AI next-action suggestion (proxies to followup service) | Yes | ai.view_scores |

---

## Module 3: Follow-up Tasks (v1-followups.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /followups | followups.html (B-01), dashboard.html (A-01) | List follow-up tasks with filters | Yes | tasks.read |
| POST | /followups | leads-detail.html (C-01) | Create follow-up task | Yes | tasks.create |
| GET | /followups/:task_id | followups.html (B-01) | Follow-up task detail | Yes | tasks.read |
| POST | /followups/:id/complete | followups.html (B-01) | Mark follow-up complete | Yes | tasks.complete |
| POST | /followups/:id/snooze | followups.html (B-01) | Snooze follow-up (sets new due_at) | Yes | tasks.update |
| GET | /followups/lead/:id/canonical | leads-detail.html (C-01) | Get canonical pending task for a lead | Yes | tasks.read |

---

## Module 4: Contacts (v1-contacts.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /contacts | contacts.html (B-03), contacts-health.html (A-03), cases-detail.html (C-05) live search | List contacts with health indicators | Yes | contacts.read |
| POST | /contacts | contact-new.html (I-02) | Create contact | Yes | contacts.create |
| GET | /contacts/:id | contacts-detail.html (C-02), cases-detail.html linked | Contact detail | Yes | contacts.read |
| PATCH | /contacts/:id | contacts-detail.html (C-02) | Update contact fields, tags | Yes | contacts.update |
| DELETE | /contacts/:id | contacts-detail.html (C-02) | Delete contact (SD-001: hidden — scope absent H-002) | Yes | contacts.delete (BROKEN — see H-002) |
| GET | /contacts/export | contacts.html (B-03) | CSV export | Yes | contacts.export |
| POST | /contacts/import | contacts.html (B-03) | Bulk CSV import with phone dedup | Yes | contacts.import |

---

## Module 5: Accounts (v1-accounts.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /accounts | accounts.html (B-04), accounts-detail.html sub-resources | List accounts with tier/industry filters | Yes | accounts.read |
| POST | /accounts | accounts.html (B-04) — inline create | Create account | Yes | accounts.create |
| GET | /accounts/:id | accounts-detail.html (C-03) | Account detail | Yes | accounts.read |
| PATCH | /accounts/:id | accounts-detail.html (C-03) | Update account fields | Yes | accounts.update |
| DELETE | /accounts/:id | accounts-detail.html (C-03) | Delete account | Yes | accounts.delete |

---

## Module 6: Opportunities (v1-opportunities.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /opportunities | sales-cockpit.html (D-01), sales-dashboard.html (A-04), accounts-detail.html (C-03) tab | List opportunities | Yes | opportunities.read |
| POST | /opportunities | opportunity-new.html (I-03) | Create opportunity | Yes | opportunities.create |
| GET | /opportunities/:id | opportunities-detail.html (C-04) | Opportunity detail | Yes | opportunities.read |
| PATCH | /opportunities/:id | opportunities-detail.html (C-04) | Stage transition; emits opportunity.stage.changed.v1 | Yes | opportunities.update |
| GET | /opportunities/:id/line-items | opportunities-detail.html (C-04) | Line items sub-resource | Yes | opportunities.read |
| POST | /opportunities/:id/line-items | opportunities-detail.html (C-04) | Add line item | Yes | opportunities.update |

---

## Module 7: CPQ — Quotes (v1-quotes.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /quotes | quotes-dashboard.html (A-05), approval-lanes.html (K-04), opportunities-detail.html (C-04) tab | List quotes | Yes | quotes.read |
| POST | /quotes | quote-builder.html (I-05) | Create quote | Yes | quotes.create |
| GET | /quotes/:id | quotes-detail.html (C-06) | Quote detail with line items and approval history | Yes | quotes.read |
| PATCH | /quotes/:id | quotes-detail.html (C-06) | Update/approve/reject quote | Yes | quotes.update / quotes.approve |
| POST | /quotes/:id/accept | quotes-detail.html (C-06) | Accept quote → creates Order | Yes | quotes.convert_to_order |

---

## Module 8: CPQ — Orders (v1-orders.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| POST | /orders | quotes-detail.html (C-06) — auto on acceptance | Create order from accepted quote | Yes | quotes.convert_to_order |
| GET | /orders/:id | orders-detail.html (C-07) | Order detail | Yes | orders.read |

---

## Module 9: Finance — Invoices (v1-invoice-summaries.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /invoice-summaries | invoices.html (B-09), accounts-detail.html (C-03) tab, finance-analytics.html (H-04) | List invoices | Yes | collections.read |
| POST | /invoice-summaries | invoices.html (B-09) | Create standalone invoice | Yes | invoices.create (collections.create_invoice per WF-B) |
| GET | /invoice-summaries/:id | invoices-detail.html (C-08) | Invoice detail | Yes | collections.read |
| PATCH | /invoice-summaries/:id | invoices-detail.html (C-08) | Update invoice status | Yes | collections.record_payment |

---

## Module 10: Finance — Collections (v1-collections.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /collections | collections.html (B-08), finance-analytics.html (H-04) | List collection records | Yes | collections.read |
| GET | /collections/invoices | invoices.html (B-09) | Collections invoice sub-resource | Yes | collections.read |
| POST | /collections/invoices | collections.html (B-08) | Create invoice via collections workflow | Yes | collections.create_invoice |
| POST | /collections/:id/reconcile | invoices-detail.html (C-08), collections.html (B-08) | Reconcile payment | Yes | collections.reconcile |

---

## Module 11: Finance — Payments (v1-payments.routes.js / webhooks)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| POST | /payments | invoices-detail.html (C-08) | Record payment (JazzCash/Easypaisa — STUB P-016) | Yes | collections.record_payment |
| POST | /payment-webhooks/jazzcash | N/A (webhook) | JazzCash payment webhook (HMAC auth) | No (HMAC) | None |
| POST | /payment-webhooks/easypaisa | N/A (webhook) | Easypaisa payment webhook (HMAC auth) | No (HMAC) | None |
| POST | /payment-webhooks/log | invoices-detail.html (C-08) proof tab | Payment proof logging | Yes | collections.record_payment |

---

## Module 12: Finance — Subscriptions (v1-subscriptions.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /subscriptions | subscriptions-dashboard.html (A-06) | List subscriptions | Yes | collections.read |
| GET | /subscriptions/:id | subscriptions-detail.html (C-09) | Subscription detail | Yes | collections.read |
| PATCH | /subscriptions/:id | subscriptions-detail.html (C-09) | Update subscription status (pause/cancel/reactivate) | Yes | admin.system_config |

---

## Module 13: Finance — Billing Settings (v1-billing.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /billing/subscription | billing-settings.html (G-04) | Get tenant billing plan/seats/renewal | Yes | admin.system_config |
| GET | /billing/invoices | billing-settings.html (G-04) | Tenant invoice history | Yes | admin.system_config |

---

## Module 14: Support — Cases (v1-cases.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /cases | cases.html (B-05), support-console.html (E-01), support-dashboard.html (A-07) | List cases with SLA status filters | Yes | cases.read |
| POST | /cases | case-new.html (I-04) | Create case; SLA timer set based on sla_tier | Yes | cases.create |
| GET | /cases/:id | cases-detail.html (C-05) | Case detail with full state | Yes | cases.read |
| PATCH | /cases/:id | cases-detail.html (C-05) | Update case fields | Yes | cases.update |
| POST | /cases/:id/assign | cases-detail.html (C-05), support-console.html (E-01) | Assign case to agent | Yes | cases.assign |
| POST | /cases/:id/comments | cases-detail.html (C-05) | Add comment (internal_note/customer_reply/resolution) | Yes | cases.update |
| POST | /cases/:id/resolve | cases-detail.html (C-05) | Resolve case (status → RESOLVED) | Yes | cases.close |
| POST | /cases/:id/close | cases-detail.html (C-05) | Force close (admin) | Yes | cases.close |
| POST | /cases/:id/reopen | cases-detail.html (C-05) | Reopen (14-day window) | Yes | cases.update |
| POST | /cases/:id/escalate | cases-detail.html (C-05), support-console.html (E-01) | Escalate case | Yes | cases.escalate |
| POST | /cases/:id/link-article | cases-detail.html (C-05) | Link knowledge article to case | Yes | cases.update |

---

## Module 15: Support — Queues (v1-support.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /support/queues | support-console.html (E-01), case-new.html (I-04) | List support queues | Yes | cases.read |
| POST | /support/queues | routing-config.html (L-03) | Create support queue | Yes | inbox.supervise |

---

## Module 16: Knowledge Base (v1-knowledge.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /knowledge | knowledge-dashboard.html (A-09) | List knowledge articles | Yes | knowledge.read |
| POST | /knowledge | knowledge-dashboard.html (A-09) | Create article (draft) | Yes | knowledge.create |
| GET | /knowledge/:id | knowledge-article.html (C-12) | Article detail with version history | Yes | knowledge.read |
| PATCH | /knowledge/:id | knowledge-article.html (C-12) | Update article content | Yes | knowledge.update |
| POST | /knowledge/:id/publish | knowledge-article.html (C-12) | Publish article (status → published) | Yes | knowledge.publish |

---

## Module 17: Omnichannel Inbox (v1-inbox.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /inbox/conversations | inbox.html (L-01) | List conversations | Yes | inbox.read |
| GET | /inbox/conversations/:id | inbox-thread.html (L-02) | Conversation thread with messages | Yes | inbox.read |
| POST | /inbox/conversations/:id/claim | inbox-thread.html (L-02) | Claim conversation (atomic; capacity check) | Yes | inbox.claim |
| POST | /inbox/conversations/:id/messages | inbox-thread.html (L-02) | Send outbound message | Yes | inbox.claim |
| POST | /inbox/conversations/:id/handoff | inbox-thread.html (L-02) | Transfer conversation to another agent | Yes | inbox.handoff |
| GET | /inbox/presence | routing-config.html (L-03), identity-dashboard.html (A-12) | Get agent presence statuses | Yes | inbox.supervise |
| PATCH | /inbox/presence | inbox.html (L-01) | Update own presence status | Yes | inbox.read |
| GET | /inbox/queues | routing-config.html (L-03), support-console.html (E-01) | List inbox queues | Yes | inbox.supervise |
| POST | /inbox/queues | routing-config.html (L-03) | Create inbox queue | Yes | inbox.supervise |

---

## Module 18: WhatsApp Webhooks (v1-whatsapp-webhooks.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /whatsapp-webhooks/meta | N/A (webhook) | Meta webhook verification (hub.challenge) | No | None |
| POST | /whatsapp-webhooks/meta | N/A (webhook) | Meta inbound message (HMAC signature auth) | No (HMAC) | None |
| POST | /whatsapp-webhooks/twilio | N/A (webhook) | Twilio inbound message | No | None |
| POST | /whatsapp-webhooks/360dialog | N/A (webhook) | 360dialog inbound message | No | None |
| POST | /whatsapp-webhooks/gupshup | N/A (webhook) | Gupshup inbound message | No | None |

---

## Module 19: Campaigns / Marketing (v1-campaigns.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /campaigns | marketing-workspace.html (F-01), engagement-dashboard.html (A-08), marketing-analytics.html (H-02) | List campaigns | Yes | campaigns.read |
| POST | /campaigns | campaign-new.html (I-06) | Create campaign | Yes | campaigns.create |
| GET | /campaigns/:id | marketing-workspace.html (F-01) | Campaign detail | Yes | campaigns.read |
| PATCH | /campaigns/:id | marketing-workspace.html (F-01) | Update campaign | Yes | campaigns.update |
| POST | /campaigns/:id/activate | campaign-new.html (I-06), marketing-workspace.html (F-01) | Activate campaign (status → active) | Yes | campaigns.activate |

---

## Module 20: Segments (v1-segments.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /segments | campaign-new.html (I-06) | List contact segments | Yes | campaigns.read |
| POST | /segments | campaign-new.html (I-06) | Create segment | Yes | campaigns.create |
| GET | /segments/:id | campaign-new.html (I-06) | Segment detail with criteria | Yes | campaigns.read |

---

## Module 21: Templates (v1-templates.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /templates | campaign-new.html (I-06) | List message templates | Yes | campaigns.read |
| POST | /templates | campaign-new.html (I-06) | Create template | Yes | campaigns.create |

---

## Module 22: Communications Engagement (v1-communications.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /communications/engagement | engagement-dashboard.html (A-08) | Delivery/open/reply rate KPIs | Yes | analytics.view_basic |

---

## Module 23: Workflows (v1-workflows.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /workflows | workflows-dashboard.html (A-10), workflow-builder.html (K-01) | List workflow definitions | Yes | workflows.read |
| POST | /workflows | workflow-builder.html (K-01) | Create workflow | Yes | workflows.create |
| GET | /workflows/:id | workflow-builder.html (K-01) | Workflow definition detail | Yes | workflows.read |
| PATCH | /workflows/:id | workflow-builder.html (K-01) | Update workflow (403 if is_system=true) | Yes | workflows.update |
| DELETE | /workflows/:id | workflow-builder.html (K-01) | Archive workflow | Yes | workflows.update |
| POST | /workflows/:id/publish | workflow-builder.html (K-01) | Publish workflow (status → active) | Yes | workflows.publish |
| POST | /workflows/:id/simulate | workflow-builder.html (K-01) | Dry-run simulate (no side effects) | Yes | workflows.read |
| POST | /workflows/:id/retry | workflow-run-detail.html (C-10) | Retry failed execution (creates child) | Yes | workflows.read |
| GET | /workflows/runs | workflows-dashboard.html (A-10), workflow-analytics.html (H-05) | List executions | Yes | workflows.read |
| GET | /workflows/runs/:id | workflow-run-detail.html (C-10) | Execution detail with step trace | Yes | workflows.read |

---

## Module 24: Partners (v1-partners.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /partners | partners.html (B-11) | List partners | Yes | partners.read |
| POST | /partners | partners.html (B-11) | Create partner | Yes | partners.create |
| GET | /partners/:id | partners-detail.html (C-11) | Partner detail | Yes | partners.read |
| PATCH | /partners/:id | partners-detail.html (C-11) | Update partner | Yes | partners.update |

---

## Module 25: Territories (v1-territories.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /territories | territories.html (G-09) | List territories | Yes | territories.read |
| POST | /territories | territories.html (G-09) | Create territory | Yes | territories.create |
| GET | /territories/:id | territories.html (G-09) | Territory detail with rules | Yes | territories.read |
| PATCH | /territories/:id | territories.html (G-09) | Update territory rules | Yes | territories.update |
| DELETE | /territories/:id | territories.html (G-09) | Delete territory | Yes | territories.delete |

---

## Module 26: Activities (v1-activities.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /activities | activity.html (B-06), leads-detail.html (C-01) timeline, contacts-detail.html (C-02) timeline | List activities | Yes | activities.read |
| POST | /activities | leads-detail.html (C-01), contacts-detail.html (C-02) | Log activity | Yes | activities.create |

---

## Module 27: Tasks (v1-tasks.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /tasks | tasks.html (B-07) | List tasks | Yes | tasks.read |
| POST | /tasks | tasks.html (B-07) | Create task | Yes | tasks.create |
| PATCH | /tasks/:id | tasks.html (B-07) | Update/complete/assign task | Yes | tasks.update |

---

## Module 28: AI — Lead Scores (v1-ai-scores.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /ai/scores/leads | ai-copilot.html (M-01), leads-detail.html (C-01), ai-insights.html (M-02) | List lead scores (sorted by score DESC) | Yes | ai.view_scores |
| GET | /ai/scores/leads/:id | leads-detail.html (C-01) | Lead score detail with top_drivers | Yes | ai.view_scores |
| POST | /ai/scores/leads/:id/recompute | leads-detail.html (C-01), ai-copilot.html (M-01) | Force recompute lead score | Yes | ai.score_leads |

---

## Module 29: AI — Predictions (v1-ai-predictions.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /ai/predictions/churn | ai-insights.html (M-02), accounts-detail.html (C-03) | Churn predictions (sorted by churn_probability DESC) | Yes | ai.view_scores |
| GET | /ai/predictions/churn/:account_id | accounts-detail.html (C-03) | Churn prediction for account | Yes | ai.view_scores |

---

## Module 30: AI — CLV Estimates (v1-ai-estimates.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /ai/estimates/clv | ai-insights.html (M-02) | CLV estimates (sorted by estimated_clv DESC) | Yes | ai.view_scores |
| GET | /ai/estimates/clv/:account_id | accounts-detail.html (C-03), ai-insights.html (M-02) | CLV estimate for account | Yes | ai.view_scores |

---

## Module 31: AI — Copilot (v1-ai-copilot.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /ai/copilot/suggestions | ai-copilot.html (M-01), dashboard.html (A-01) risk panel | Copilot suggestions (sorted by priority) | Yes | ai.view_scores |
| POST | /ai/copilot/suggestions/:id/dismiss | ai-copilot.html (M-01) | Dismiss suggestion | Yes | ai.view_scores |
| POST | /ai/copilot/suggestions/:id/action | ai-copilot.html (M-01) | Mark suggestion as actioned | Yes | ai.view_scores |
| POST | /ai/copilot/chat | ai-copilot.html (M-01) | Send NL query to copilot | Yes | ai.view_scores |

---

## Module 32: AI — Models (v1-ai-models.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /ai/models | ai-insights.html (M-02) | List AI model registry | Yes | ai.view_scores |
| POST | /ai/models/:key/retrain | ai-insights.html (M-02) | Trigger model retraining | Yes | ai.train_models |

---

## Module 33: Forecasts (v1-forecasts.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /forecasts | sales-dashboard.html (A-04), dashboard.html (A-01), ai-insights.html (M-02) | Get current quarter forecast | Yes | ai.view_forecasts |
| POST | /forecasts/model | sales-dashboard.html (A-04) | Trigger forecast model refresh | Yes | ai.generate_forecasts |
| POST | /forecasts/aggregate | sales-dashboard.html (A-04) | Aggregate forecast data | Yes | ai.generate_forecasts |

---

## Module 34: Reports (v1-reports.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| POST | /reports/execute | report-builder.html (H-07) | Execute custom report query → chart data | Yes | analytics.view_basic |
| POST | /reports/definitions | report-builder.html (H-07) | Save report definition | Yes | analytics.view_advanced |
| GET | /reports/definitions | report-builder.html (H-07) | Load saved report definitions | Yes | analytics.view_basic |

---

## Module 35: Admin — Users (v1-admin-users.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /admin/users | users.html (B-10), user-management-crm.html (G-02), identity-dashboard.html (A-12), rbac-audit.html (J-04) | List users with role badges | Yes | admin.manage_users |
| POST | /admin/users/invite | user-management-crm.html (G-02) | Invite user (2-step modal) | Yes | admin.manage_users |
| PATCH | /admin/users/:id | user-management-crm.html (G-02) | Update user (role, status) | Yes | admin.manage_users |
| POST | /admin/users/:id/reset-password | users.html (B-10), user-management-crm.html (G-02) | Reset user password | Yes | admin.manage_users |

---

## Module 36: Admin — Roles (v1-admin-roles.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /admin/roles | roles.html (G-03), rbac-audit.html (J-04) | List roles with scope arrays | Yes | admin.manage_roles |
| POST | /admin/roles | roles.html (G-03) | Create custom role | Yes | admin.manage_roles |
| PATCH | /admin/roles/:id | roles.html (G-03) | Update role permissions | Yes | admin.manage_roles |
| DELETE | /admin/roles/:id | roles.html (G-03) | Delete role (blocked if is_system=true or active users) | Yes | admin.manage_roles |

---

## Module 37: Admin — Audit Logs (v1-admin-audit.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /admin/audit-logs | audit-log.html (J-01), audit-dashboard.html (A-13), compliance-report.html (J-02), audit-report.html (H-06), identity-dashboard.html (A-12) | List audit log entries | Yes | admin.read_audit_logs |
| GET | /admin/audit-logs/export | audit-report.html (H-06) | Export signed CSV audit log | Yes | admin.export_compliance_data |

---

## Module 38: Admin — Settings (v1-admin-settings.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /admin/settings | org-settings.html (G-01), notifications.html (G-06) | Get tenant settings | Yes | admin.system_config |
| PATCH | /admin/settings | org-settings.html (G-01), notifications.html (G-06) | Update tenant settings | Yes | admin.system_config |

---

## Module 39: Admin — Tenants (v1-admin-tenants.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /admin/tenants | tenants-dashboard.html (A-11) | List all tenants (tenant_owner only) | Yes | admin.manage_tenants |
| GET | /admin/tenants/:id | tenants-dashboard.html (A-11) | Tenant detail | Yes | admin.manage_tenants |

---

## Module 40: Feature Flags (v1-feature-flags.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /feature-flags | feature-flags.html (G-07) | List feature flags | Yes | admin.manage_feature_flags |
| PATCH | /feature-flags/:id | feature-flags.html (G-07) | Toggle flag (dual-approval required if requires_dual_approval=true) | Yes | admin.manage_feature_flags |

---

## Module 41: Governance (v1-governance.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /governance/classification | data-governance.html (J-03) | Get data classification policies | Yes | admin.system_config |
| PATCH | /governance/classification | data-governance.html (J-03) | Update classification | Yes | admin.system_config |
| GET | /governance/retention | data-governance.html (J-03), compliance.html (G-08) | Get retention policies | Yes | admin.system_config |
| PATCH | /governance/retention | compliance.html (G-08) | Update retention policy | Yes | admin.system_config |
| GET | /governance/sar | data-governance.html (J-03), privacy.html (J-05) | List SAR records | Yes | admin.system_config |
| POST | /governance/sar | data-governance.html (J-03), privacy.html (J-05) | Create SAR (30-day SLA due date) | Yes | admin.system_config |

---

## Module 42: Privacy / Consent (v1-privacy.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /privacy/consent | data-governance.html (J-03), privacy.html (J-05) | List consent records from contacts | Yes | admin.system_config |
| PATCH | /privacy/consent/:id | privacy.html (J-05) | Update consent record | Yes | admin.system_config |

---

## Module 43: Integrations (v1-integrations.routes.js)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /integrations | integrations.html (G-05) | List integration provider status | Yes | admin.system_config |
| PATCH | /integrations/:provider | integrations.html (G-05) | Update integration config | Yes | admin.system_config |
| POST | /integrations/:provider/test | integrations.html (G-05) | Test integration connection | Yes | admin.system_config |

---

## Module 44: Health / Ready (Unversioned)

| Method | Endpoint | Frontend Screen(s) | Purpose | Auth Required | Permission |
|---|---|---|---|---|---|
| GET | /health | CI/CD, monitoring | Liveness probe | No | None |
| GET | /ready | CI/CD, monitoring | DB readiness check | No | None |
| GET | /dev-token | Development only | Dev JWT generation (non-production) | No | None |

---

## API Coverage Summary

| Domain | Endpoints | Primary Frontend Consumers |
|---|---|---|
| Auth | 7 | Login/register/refresh/logout pages |
| Lead Management | 8 | B-02, C-01, I-01, A-02 |
| Follow-up Tasks | 6 | B-01, C-01 |
| Contacts | 7 | B-03, C-02, I-02, A-03 |
| Accounts | 5 | B-04, C-03 |
| Opportunities | 6 | C-04, D-01, I-03, A-04 |
| CPQ Quotes | 5 | A-05, I-05, C-06, K-04 |
| CPQ Orders | 2 | C-07 |
| Finance Invoices | 4 | B-09, C-08 |
| Collections | 4 | B-08, C-08 |
| Payments | 4 | C-08 (3 STUB) |
| Subscriptions | 3 | A-06, C-09 |
| Billing Settings | 2 | G-04 |
| Support Cases | 11 | B-05, C-05, I-04, E-01 |
| Support Queues | 2 | E-01, I-04 |
| Knowledge Base | 5 | A-09, C-12 |
| Inbox | 9 | L-01, L-02, L-03 |
| WhatsApp Webhooks | 5 | N/A (server-side) |
| Campaigns | 5 | F-01, I-06, A-08, H-02 |
| Segments | 3 | I-06 |
| Templates | 2 | I-06 |
| Communications | 1 | A-08 |
| Workflows | 10 | A-10, K-01, C-10, H-05 |
| Partners | 4 | B-11, C-11 |
| Territories | 5 | G-09 |
| Activities | 2 | B-06, C-01, C-02 |
| Tasks | 3 | B-07 |
| AI Scores | 3 | M-01, C-01, M-02 |
| AI Predictions | 2 | M-02, C-03 |
| AI Estimates | 2 | M-02, C-03 |
| AI Copilot | 4 | M-01, A-01 |
| AI Models | 2 | M-02 |
| Forecasts | 3 | A-04, A-01, M-02 |
| Reports | 3 | H-07 |
| Admin Users | 4 | B-10, G-02, A-12 |
| Admin Roles | 4 | G-03, J-04 |
| Admin Audit | 2 | J-01, A-13, H-06 |
| Admin Settings | 2 | G-01, G-06 |
| Admin Tenants | 2 | A-11 |
| Feature Flags | 2 | G-07 |
| Governance | 6 | J-03, G-08 |
| Privacy/Consent | 2 | J-03, J-05 |
| Integrations | 3 | G-05 |
| Health/Ready | 3 | CI/CD |
| **TOTAL** | **228** | |

---

*End FRONTEND_API_DEPENDENCY_MAP.md*
*228 API endpoints across 44 gateway route groups*
*Pakistan CRM OS — Phase C6 — 2026-06-23*
