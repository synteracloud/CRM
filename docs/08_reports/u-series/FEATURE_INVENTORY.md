# FEATURE_INVENTORY.md
> Generated: 2026-06-20 — U1 Authority Reconstruction — evidence from frontend/src/app/*.html (75 custom pages), gateway/routes/v1-*.routes.js, src/*/entities.py

**Status key:**
- **Built** — HTML page exists; uses crm-dummy.js data (DUMMY_MODE: true)
- **Stub** — Backend route exists with in-memory fallback; not connected to Python services
- **Wired** — Page confirmed wired to live API (DUMMY_MODE: false)
- **Blocked** — Feature built but blocked by external dependency

---

## Module 1: Lead Management

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 1 | Lead list with DataTable (stage/priority/source filter chips) | leads.html | GET /leads | Built |
| 2 | Lead detail view (timeline, follow-up panel, score) | leads-detail.html | GET /leads/:id | Built |
| 3 | New lead form (stage, priority, source, phone E.164) | lead-new.html | POST /leads | Built |
| 4 | Lead stage transition (new→qualifying→proposal→negotiation→won/lost) | leads-detail.html | PATCH /leads/:id | Built |
| 5 | Lead priority toggle (hot/warm/cold) | leads-detail.html | PATCH /leads/:id | Built |
| 6 | Lead owner assignment | leads-detail.html | PATCH /leads/:id + leads.assign | Built |
| 7 | Lead CSV export | leads.html | GET /leads/export | Built |
| 8 | Lead CSV/JSON bulk import | leads.html | POST /leads/import | Built |
| 9 | Lead next-action suggestion (AI-powered advisory) | leads-detail.html | GET /leads/:id/next-action | Built |
| 10 | Lead funnel dashboard (KPI tiles, funnel chart) | leads-dashboard.html | GET /leads (aggregated) | Built |

## Module 2: Follow-up Enforcement

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 11 | Follow-up queue (overdue/pending filter, escalation badges) | followups.html | GET /followups | Built |
| 12 | Follow-up complete action | followups.html | POST /followups/:id/complete | Built |
| 13 | Follow-up snooze action | followups.html | POST /followups/:id/snooze | Built |
| 14 | Follow-up create (from lead detail) | leads-detail.html | POST /followups | Built |
| 15 | Canonical pending task indicator per lead | leads-detail.html | GET /followups/lead/:id/canonical | Built |
| 16 | Follow-up enforcement engine (auto-creates tasks on idle leads) | (background) | WF-001 + /internal/leads/:id/register | Built |

## Module 3: Contacts

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 17 | Contact list with health indicators (completeness score, open cases, idle flag) | contacts.html | GET /contacts | Built |
| 18 | Contact detail (touchpoint timeline, linked account, cases) | contacts-detail.html | GET /contacts/:id | Built |
| 19 | New contact form | contact-new.html | POST /contacts | Built |
| 20 | Contact health dashboard (KPI tiles, completeness distribution) | contacts-health.html | GET /contacts | Built |
| 21 | Contact CSV export/import | contacts.html | GET+POST /contacts/export+import | Built |
| 22 | Contact tag management | contacts-detail.html | PATCH /contacts/:id | Built |

## Module 4: Accounts

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 23 | Account list (tier/industry filter) | accounts.html | GET /accounts | Built |
| 24 | Account detail (contacts, opportunities, invoices, churn risk) | accounts-detail.html | GET /accounts/:id | Built |

## Module 5: Sales / Opportunities

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 25 | Opportunity detail (stage, forecast category, amount PKR, line items) | opportunities-detail.html | GET /opportunities/:id | Built |
| 26 | Opportunity stage transition | opportunities-detail.html | PATCH /opportunities/:id | Built |
| 27 | New opportunity form | opportunity-new.html | POST /opportunities | Built |
| 28 | Opportunity line item management | opportunities-detail.html | GET+POST /opportunities/:id/line-items | Built |
| 29 | Sales cockpit (pipeline overview, today's tasks, at-risk deals) | sales-cockpit.html | GET /opportunities | Built |
| 30 | Opportunity pipeline dashboard (funnel, forecast by category) | sales-dashboard.html | GET /opportunities | Built |

## Module 6: CPQ / Quotes & Orders

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 31 | CPQ quote builder (line items, discount, auto-approval trigger) | quote-builder.html | POST /quotes | Built |
| 32 | Quote detail (approval history, line items, status) | quotes-detail.html | GET /quotes/:id | Built |
| 33 | Quote approval dashboard (pending approvals queue) | quotes-dashboard.html | GET /quotes | Built |
| 34 | Quote accept → order creation | quotes-detail.html | POST /quotes/:id/accept | Built |
| 35 | Order detail (linked invoice, fulfilment status) | orders-detail.html | GET /orders/:id | Built |
| 36 | Discount >10% approval routing | quote-builder.html | Rule in rule_engine module | Built |

## Module 7: Finance / Collections

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 37 | Invoice queue (overdue flag, PKR amounts) | invoices.html | GET /invoice-summaries | Built |
| 38 | Invoice detail (payment history, balance) | invoices-detail.html | GET /invoice-summaries/:id | Built |
| 39 | Collections queue (days overdue, contact, next action) | collections.html | GET /collections | Built |
| 40 | Finance analytics (revenue trends, collections rate, PKR charts) | finance-analytics.html | GET /invoice-summaries + /collections | Built |
| 41 | JazzCash payment processing | billing-settings.html | POST /payments | Blocked (P-016) |
| 42 | Easypaisa payment processing | billing-settings.html | POST /payments | Blocked (P-016) |
| 43 | Payment webhook handler | (background) | POST /payment-webhooks | Built (stub) |

## Module 8: Subscriptions

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 44 | Subscription revenue dashboard (MRR/ARR, status breakdown) | subscriptions-dashboard.html | GET /subscriptions | Built |
| 45 | Subscription detail (billing cycle, status, renewal) | subscriptions-detail.html | GET /subscriptions/:id | Built |
| 46 | Billing settings (plan, payment methods) | billing-settings.html | GET /billing/subscription | Blocked (P-016) |

## Module 9: Support / Cases

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 47 | Case queue (SLA status, priority, queue assignment) | cases.html | GET /cases | Built |
| 48 | Case detail (SLA timers, comment thread, escalation history) | cases-detail.html | GET /cases/:id | Built |
| 49 | New case form (SLA tier, source, category, queue) | case-new.html | POST /cases | Built |
| 50 | Case assignment (to agent or team) | cases-detail.html | POST /cases/:id/assign | Built |
| 51 | Case comment (internal note, customer reply, resolution) | cases-detail.html | POST /cases/:id/comments | Built |
| 52 | Case resolve | cases-detail.html | POST /cases/:id/resolve | Built |
| 53 | Case force-close (admin) | cases-detail.html | POST /cases/:id/close | Built |
| 54 | Case reopen (14-day window) | cases-detail.html | POST /cases/:id/reopen | Built |
| 55 | Case escalation (SLA breach / manager override) | cases-detail.html | POST /cases/:id/escalate | Built |
| 56 | Link knowledge article to case | cases-detail.html | POST /cases/:id/link-article | Built |
| 57 | Support console (agent workspace with queue view) | support-console.html | GET /cases + /support/queues | Built |
| 58 | Support dashboard (SLA compliance, CSAT, queue depth) | support-dashboard.html | GET /cases (aggregated) | Built |
| 59 | SLA breach notification (auto-escalation workflow) | (background) | WF-003 | Built |

## Module 10: Knowledge Base

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 60 | Knowledge article view (rich content, version) | knowledge-article.html | GET /knowledge/:id | Built |
| 61 | Knowledge dashboard (effectiveness metrics) | knowledge-dashboard.html | GET /knowledge | Built |
| 62 | Article publish workflow (draft→review→published) | knowledge-article.html | POST /knowledge/:id/publish | Built |

## Module 11: Omnichannel Inbox

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 63 | Inbox conversation list (channel badges, unread count, intent tags) | inbox.html | GET /inbox/conversations | Built |
| 64 | Conversation thread view (message history, agent info) | inbox-thread.html | GET /inbox/conversations/:id | Built |
| 65 | Send message (WhatsApp/email outbound) | inbox-thread.html | POST /inbox/conversations/:id/messages | Built |
| 66 | Claim conversation from pool (atomic assignment) | inbox-thread.html | POST /inbox/conversations/:id/claim | Built |
| 67 | Handoff conversation to another agent | inbox-thread.html | POST /inbox/conversations/:id/handoff | Built |
| 68 | Agent presence status (online/away/busy/offline) | inbox.html | PATCH /inbox/presence | Built |
| 69 | Supervisor presence board | inbox.html | GET /inbox/presence | Built |
| 70 | Inbox queue management | routing-config.html | GET+POST /inbox/queues | Built |
| 71 | Engagement dashboard (WhatsApp metrics, channel breakdown) | engagement-dashboard.html | GET /communications/engagement | Wired (2026-05-31) |
| 72 | WhatsApp webhook receiver | (background) | POST /whatsapp-webhooks | Built |

## Module 12: Marketing / Campaigns

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 73 | Campaign builder (WhatsApp blast/email/SMS) | campaign-new.html | POST /campaigns | Built |
| 74 | Marketing workspace (active campaigns, performance) | marketing-workspace.html | GET /campaigns | Built |
| 75 | Marketing analytics (open rate, click rate, conversion) | marketing-analytics.html | GET /campaigns (aggregated) | Built |
| 76 | Segment management (criteria-based contact lists) | marketing-workspace.html | GET+POST /segments | Built |

## Module 13: Workflow Automation

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 77 | Workflow builder (canvas with trigger + step DSL) | workflow-builder.html | POST+PATCH /workflows | Built |
| 78 | Workflow publish/activate | workflow-builder.html | POST /workflows/:id/publish | Built |
| 79 | Workflow dry-run simulate | workflow-builder.html | POST /workflows/:id/simulate | Built |
| 80 | Workflow run detail (step-by-step execution trace) | workflow-run-detail.html | GET /workflows/runs/:id | Built |
| 81 | Workflow retry (failed execution) | workflow-run-detail.html | POST /workflows/runs/:id/retry | Built |
| 82 | Workflow cancel (running execution) | workflow-run-detail.html | POST /workflows/runs/:id/cancel | Built |
| 83 | Workflow dashboard (execution stats, success rate) | workflows-dashboard.html | GET /workflows/runs + /workflows/:id/stats | Built |
| 84 | Workflow analytics | workflow-analytics.html | GET /workflows (aggregated) | Built |
| 85 | 5 system workflows (lead idle, collections, SLA, territory, opp stage) | (background) | event-driven | Built |

## Module 14: AI / Copilot

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 86 | AI copilot chat (NL query → intent + records) | ai-copilot.html | POST /ai/copilot/query | Built (rule-based, no inference) |
| 87 | Copilot suggestions (overdue follow-ups, deal nudges, risk flags) | ai-copilot.html | GET /ai/copilot/suggestions | Built |
| 88 | Dismiss/action copilot suggestion | ai-copilot.html | POST /ai/copilot/suggestions/:id/dismiss+action | Built |
| 89 | Lead scoring (score 0–100, score_band, trend, top_drivers) | ai-insights.html + leads-detail.html | GET /ai/scores/leads | Built |
| 90 | Force recompute lead score | ai-insights.html | POST /ai/scores/leads/:id/recompute | Built |
| 91 | Churn prediction (risk_band, churn_probability, recommended_action) | ai-insights.html + accounts-detail.html | GET /ai/predictions/churn | Built |
| 92 | CLV estimate (PKR, 24-month horizon) | ai-insights.html + accounts-detail.html | GET /ai/estimates/clv | Built |
| 93 | AI model registry (rule_based models only) | ai-insights.html | GET /ai/models | Built |

## Module 15: Report Builder

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 94 | Report builder (custom query, field selection, visualisation) | report-builder.html | POST /reports/execute + /reports/definitions | Wired (2026-05-31) |
| 95 | Sales analytics (win rate, pipeline velocity, rep performance) | sales-analytics.html | GET /reports/execute | Built |
| 96 | Support analytics (CSAT, resolution time, escalation rate) | support-analytics.html | GET /reports/execute | Built |
| 97 | Finance analytics (revenue recognition, collections efficiency) | finance-analytics.html | GET /reports/execute | Built |
| 98 | Workflow analytics | workflow-analytics.html | GET /reports/execute | Built |
| 99 | Audit report | audit-report.html | GET /audit | Built |

## Module 16: Territories

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 100 | Territory list and configuration | territories.html | GET+POST /territories | Built |
| 101 | Territory rule management (geography/industry/account_size criteria) | territories.html | PATCH /territories/:id | Built |
| 102 | Auto-assignment of leads to territory owner (WF-004) | (background) | WF-004 (lead.created.v1) | Built |

## Module 17: Partners

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 103 | Partner list (tier, YTD revenue, commission) | partners.html | GET /partners | Built |
| 104 | Partner detail (deal registrations, commission ledger, attribution) | partners-detail.html | GET /partners/:id | Built |

## Module 18: Identity & Access Management

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 105 | User directory | users.html | GET /users | Built |
| 106 | User management (invite, status, role assignment) | user-management-crm.html | POST/PATCH /users | Built |
| 107 | Role editor (create custom roles, set permissions) | roles.html | GET+POST+PATCH+DELETE /roles | Built |
| 108 | Identity dashboard (role distribution, login heatmap) | identity-dashboard.html | GET /users (aggregated) | Built |
| 109 | RBAC audit (permission matrix view) | rbac-audit.html | GET /roles + /users | Wired (J-03 wired, J-04 adjacent) |

## Module 19: Audit & Compliance

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 110 | Audit log (hash-chain verified, actor/action/entity) | audit-log.html | GET /audit | Built |
| 111 | Audit log export (signed CSV) | audit-log.html | GET /audit/export | Built |
| 112 | Compliance report | compliance-report.html | GET /compliance-settings | Built |
| 113 | Data governance (classification, retention, SAR) | data-governance.html | GET /governance/* | Wired (2026-05-31) |
| 114 | Privacy consent management | privacy.html | GET+POST /privacy/consent | Built |
| 115 | Audit dashboard (platform health, event volume) | audit-dashboard.html | GET /audit (aggregated) | Built |

## Module 20: Settings / Administration

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 116 | Org settings (branding, timezone, currency PKR) | org-settings.html | GET+PATCH /org-settings | Built |
| 117 | Integration settings (WhatsApp, payment rails config) | integrations.html | GET+PATCH /integrations | Wired (2026-05-31) |
| 118 | Integration connection test | integrations.html | POST /integrations/:provider/test | Built |
| 119 | Notification preferences | notifications.html | GET+PATCH /notification-preferences | Built (EN only) |
| 120 | Notification preferences (Urdu) | notifications.html | — | Blocked (P-017) |
| 121 | Feature flag management (dual-approval toggle) | feature-flags.html | GET+PATCH /admin/feature-flags | Built |
| 122 | Tenant admin panel (entitlements, seat count) | tenants-dashboard.html | GET /admin/tenants | Built |

## Module 21: Auth & Registration

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 123 | Email + password login | (authentication/) | POST /auth/login | Built |
| 124 | Multi-tenant self-registration | (authentication/) | POST /auth/register | Built |
| 125 | JWT token refresh (silent renewal) | (crm-api.js) | POST /auth/refresh | Built |
| 126 | Logout (token revocation) | (crm-shell.js) | DELETE /auth/sessions/current | Built |
| 127 | Forgot password (6-digit OTP via email) | (authentication/) | POST /auth/forgot-password | Built |
| 128 | Reset password (OTP validation) | (authentication/) | POST /auth/reset-password | Built |

## Module 22: Builder Tools

| # | Feature | Page | API Endpoint | Status |
|---|---|---|---|---|
| 129 | Custom object builder (schema definition, layout) | object-builder.html | (custom_object_framework module) | Built |
| 130 | Rule builder (business rule canvas) | rule-builder.html | (rule_engine module) | Built |
| 131 | Approval lanes builder | approval-lanes.html | (rule_engine module) | Built |

---

## Undocumented Features Found in Code

(Present in code, not explicitly described in DESIGN-SPEC.md or product docs)

| # | Feature | Evidence Location | Notes |
|---|---|---|---|
| U-01 | SendGrid email integration (password reset OTP, welcome email) | v1-auth.routes.js:62–93 | Active in production when SENDGRID_API_KEY env var is set. U0 audit incorrectly stated "email provider not found". |
| U-02 | Lead next-action suggestion endpoint | v1-leads.routes.js:307–354 | GET /leads/:id/next-action — proxies to followup service FollowupEnforcementEngine.suggest_next_action() |
| U-03 | Leads soft delete | v1-leads.routes.js:287–305 | DELETE /leads/:id calls repo.softDelete() — soft delete, not hard |
| U-04 | Opportunity line items sub-resource | v1-opportunities.routes.js:247–292 | GET+POST /opportunities/:id/line-items |
| U-05 | Post-registration activation engine | v1-auth.routes.js:370–381 | POST /internal/activation/seed fires after register to seed default pipeline |
| U-06 | Lead stage history (immutable audit trail) | db/lead_management_db/schema.sql:59–70 | lead_history table captures every field change with old/new values |
| U-07 | Optimistic concurrency locking on Cases | v1-cases.routes.js:207–210 | version_no must match; 409 CONFLICT on stale |
| U-08 | Copilot suggestion dismiss/action tracking | v1-ai.routes.js:181–193 | actioned_at, dismissed_at timestamps tracked |
| U-09 | Agent max_concurrent capacity enforcement | v1-inbox.routes.js:146–150 | Claim fails if agent at max_concurrent conversations |
| U-10 | 14-day case reopen window | v1-cases.routes.js:411–415 | daysSinceClosed > 14 → 422 REOPEN_WINDOW_EXPIRED |
| U-11 | Workflow dry-run simulate (no side effects) | v1-workflows.routes.js:309–340 | POST /workflows/:id/simulate returns simulated step results without execution |
| U-12 | Workflow retry creates new child execution | v1-workflows.routes.js:127–162 | parent_execution_id links retry to original |
| U-13 | Followup canonical constraint (one pending per lead) | v1-followups.routes.js:231–248 | GET /followups/lead/:id/canonical — enforced uniqueness |
| U-14 | Case link-article cross-domain endpoint | v1-cases.routes.js:481–504 | POST /cases/:id/link-article links KnowledgeArticle to Case |
| U-15 | SLA auto-advance: ASSIGNED→IN_PROGRESS on first reply | v1-cases.routes.js:296–299 | Automatic state transition on first customer_reply comment |

---

*End FEATURE_INVENTORY.md*
