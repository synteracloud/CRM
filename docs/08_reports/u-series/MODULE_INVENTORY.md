# MODULE_INVENTORY.md
> Generated: 2026-06-20 — U1 Authority Reconstruction — evidence from backend/src/, backend/gateway/routes/, frontend/src/app/

---

## Module Status Key
- **Frontend-built** — HTML page exists in app/; uses crm-dummy.js data (DUMMY_MODE: true)
- **Backend-built** — Python src/ module and/or gateway route file confirmed
- **Integrated** — Frontend page has DUMMY_MODE: false and calls live API
- **Verified** — Full live-API end-to-end test passed

---

## 1. Lead Management
**Frontend pages:** followups.html (B-01), leads.html (B-02), leads-detail.html (C-01), lead-new.html (I-01), leads-dashboard.html (A-02)
**Backend module:** `src/lead_management/` (api.py, entities.py, services.py, events.py, workflow_mapping.py)
**Gateway route:** `gateway/routes/v1-leads.routes.js`, `v1-followups.routes.js`
**Entities:** Lead, LeadAssignment, LeadHistory, FollowupTask
**Status:** Frontend-built, Backend-built
**Notes:** Full CRUD + stage transitions + CSV export/import + next-action endpoint. Followup enforcement engine wired (POST /internal/leads/:id/register). T-level audit issues on B-01, B-02.

---

## 2. Contacts
**Frontend pages:** contacts.html (B-03), contacts-detail.html (C-02), contact-new.html (I-02), contacts-health.html (A-03)
**Backend module:** `src/customer_360_cdp/` (api.py, entities.py, services.py)
**Gateway route:** `gateway/routes/v1-contacts.routes.js`
**Entities:** Contact
**Status:** Frontend-built, Backend-built
**Notes:** Full CRUD + CSV export/import. T-level audit issues on B-03.

---

## 3. Accounts
**Frontend pages:** accounts.html (B-04), accounts-detail.html (C-03)
**Backend module:** `src/customer_360_cdp/` (shared with Contacts)
**Gateway route:** `gateway/routes/v1-accounts.routes.js`
**Entities:** Account
**Status:** Frontend-built, Backend-built

---

## 4. Sales / Opportunities
**Frontend pages:** opportunities-detail.html (C-04), sales-cockpit.html (D-01), sales-dashboard.html (A-04), opportunity-new.html (I-03)
**Backend module:** `src/sales_cockpit/` (api.py, workspace.py)
**Gateway route:** `gateway/routes/v1-opportunities.routes.js`
**Entities:** Opportunity, OpportunityLineItem
**Status:** Frontend-built, Backend-built
**Notes:** Stage transitions emit events to workflow engine. Line items sub-resource.

---

## 5. CPQ / Quotes & Orders
**Frontend pages:** quotes-detail.html (C-06), quote-builder.html (I-05), quotes-dashboard.html (A-05)
**Backend module:** `src/rule_engine/` (api.py, cpq_api.py, cpq_rules.py, entities.py, services.py)
**Gateway route:** `gateway/routes/v1-quotes.routes.js`, `v1-orders.routes.js`
**Entities:** Quote, Order
**Status:** Frontend-built, Backend-built
**Notes:** Discount > 10% auto-triggers approval workflow. Order is immutable post-fulfilment (rule_engine enforces). CPQ rules engine is a separate sub-module.

---

## 6. Finance / Collections
**Frontend pages:** invoices.html (B-09), invoices-detail.html (C-08), collections.html (B-08), finance-analytics.html (H-04)
**Backend module:** `src/revenue_recognition/`, `src/usage_billing/`, `src/subscription_billing/`
**Gateway route:** `gateway/routes/v1-invoice-summaries.routes.js`, `v1-collections.routes.js`, `v1-payments.routes.js`, `v1-payment-webhooks.routes.js`
**Entities:** Invoice, Collection, Payment
**Status:** Frontend-built, Backend-built
**Blockers:** JazzCash/Easypaisa in stub_mode=True (P-016)

---

## 7. Subscriptions / Billing
**Frontend pages:** subscriptions-dashboard.html (A-06), subscriptions-detail.html (C-09), billing-settings.html (G-04)
**Backend module:** `src/subscription_billing/` (api.py, entities.py, services.py, workflow_mapping.py)
**Gateway route:** `gateway/routes/v1-subscriptions.routes.js`, `v1-billing.routes.js`
**Entities:** Subscription
**Status:** Frontend-built, Backend-built
**Blockers:** G-04 billing-settings.html payment section is static stub (P-016)

---

## 8. Support / Cases
**Frontend pages:** cases.html (B-05), cases-detail.html (C-05), support-console.html (E-01), support-dashboard.html (A-07), case-new.html (I-04)
**Backend module:** `src/ticket_management/` (api.py, entities.py, services.py), `src/support_console/` (api.py, entities.py, services.py)
**Gateway route:** `gateway/routes/v1-cases.routes.js` (exports casesRouter + supportRouter)
**Entities:** Case, CaseComment, CaseEscalation, SupportQueue
**Status:** Frontend-built, Backend-built
**Notes:** Full SLA state machine (OPEN→ASSIGNED→IN_PROGRESS→WAITING_ON_CUSTOMER→RESOLVED→ESCALATED→CLOSED). 14-day reopen window. PKT business-hours SLA calculation in Python service.

---

## 9. Knowledge Base
**Frontend pages:** knowledge-article.html (C-12), knowledge-dashboard.html (A-09)
**Backend module:** `src/knowledge_base/` (api.py, entities.py, services.py)
**Gateway route:** `gateway/routes/v1-knowledge.routes.js`
**Entities:** KnowledgeArticle
**Status:** Frontend-built, Backend-built
**Notes:** State-gated (draft→review→published→archived). Linked to Cases via /cases/:id/link-article.

---

## 10. Omnichannel Inbox
**Frontend pages:** inbox.html (L-01), inbox-thread.html (L-02), engagement-dashboard.html (A-08)
**Backend module:** `src/omnichannel_inbox/` (api.py, entities.py, services.py)
**Gateway route:** `gateway/routes/v1-inbox.routes.js`
**Entities:** Conversation, Message, Handoff, AgentPresence, InboxQueue
**Status:** Frontend-built, Backend-built
**Notes:** A-08 confirmed wired to live API (2026-05-31). Claim-first atomic assignment. Supervisor-only handoff from other agents.

---

## 11. Routing / Inbox Config
**Frontend pages:** routing-config.html (L-03)
**Backend module:** `src/omnichannel_inbox/` (services.py handles routing strategies)
**Gateway route:** `gateway/routes/v1-inbox.routes.js` (/queues endpoints)
**Entities:** InboxQueue
**Status:** Frontend-built, Backend-built

---

## 12. Marketing / Campaigns
**Frontend pages:** marketing-workspace.html (F-01), campaign-new.html (I-06), marketing-analytics.html (H-02)
**Backend module:** `src/campaigns/` (api.py, entities.py, services.py, segmentation.py, workspace.py, workflow_mapping.py), `src/marketing_admin_workflow_ui/`
**Gateway route:** `gateway/routes/v1-campaigns.routes.js`, `v1-segments.routes.js`, `v1-emails.routes.js`, `v1-templates.routes.js`
**Entities:** Campaign, Segment
**Status:** Frontend-built, Backend-built
**Notes:** Automation journeys module (`src/automation_journeys/`) handles multi-step drip sequences.

---

## 13. Workflow Automation
**Frontend pages:** workflow-builder.html (K-01), workflow-run-detail.html (C-10), workflows-dashboard.html (A-10), workflow-analytics.html (H-05)
**Backend module:** `src/workflow_engine/` (api.py, catalog.py, entities.py, services.py)
**Gateway route:** `gateway/routes/v1-workflows.routes.js`
**Entities:** WorkflowDefinition, WorkflowExecution, WorkflowStepRecord
**Status:** Frontend-built, Backend-built
**Notes:** 5 system workflows seeded (see WORKFLOW_INVENTORY.md). Custom workflow create/publish/simulate supported.

---

## 14. AI / Copilot
**Frontend pages:** ai-copilot.html (M-01), ai-insights.html (M-02)
**Backend module:** `src/ai_copilot/` (api.py, entities.py, services.py), `src/ai_scoring/`, `src/predictive_models/`, `src/predictive_forecasting/`
**Gateway route:** `gateway/routes/v1-ai.routes.js`
**Entities:** LeadScore, ChurnPrediction, CLVEstimate, CopilotSuggestion, ScoringModel
**Status:** Frontend-built, Backend-built (rule-based only)
**Blockers (M-01):** AI inference model not selected; no AI provider SDK in requirements.txt; copilot is advisory-only shell. All models are rule_based (not ML inference).

---

## 15. Forecasting
**Frontend pages:** sales-dashboard.html (A-04) includes forecast panel
**Backend module:** `src/predictive_forecasting/` (api.py, entities.py, services.py)
**Gateway route:** `gateway/routes/v1-forecasts.routes.js`
**Entities:** Forecast (inferred from module)
**Status:** Frontend-built, Backend-built

---

## 16. Report Builder
**Frontend pages:** report-builder.html (H-07), sales-analytics.html (H-01), support-analytics.html (H-03), finance-analytics.html (H-04), workflow-analytics.html (H-05), audit-report.html (H-06)
**Backend module:** `src/reporting_dashboards/` (api.py, entities.py, services.py)
**Gateway route:** `gateway/routes/v1-reports.routes.js`
**Status:** Frontend-built, Backend-built
**Notes:** H-07 (report-builder) confirmed wired to live API (2026-05-31). POST /reports/execute + POST/GET /reports/definitions.

---

## 17. Territories
**Frontend pages:** territories.html (G-09)
**Backend module:** `src/territory_management/` (api.py, entities.py, services.py)
**Gateway route:** `gateway/routes/v1-territories.routes.js`
**Entities:** Territory, TerritoryRule
**Status:** Frontend-built, Backend-built
**Notes:** WF-004 (lead_assignment) calls territory evaluation on lead.created.v1.

---

## 18. Partners / Channel
**Frontend pages:** partners.html (B-11), partners-detail.html (C-11)
**Backend module:** `src/partner_channel_management/` (api.py, entities.py, services.py)
**Gateway route:** `gateway/routes/v1-partners.routes.js`
**Entities:** Partner
**Status:** Frontend-built, Backend-built
**Notes:** Commission ledger, deal registration, tier management.

---

## 19. Identity & Access Management
**Frontend pages:** users.html (B-10), user-management-crm.html (G-02), roles.html (G-03), identity-dashboard.html (A-12)
**Backend module:** `src/role_based_ui/` (api.py, entities.py, services.py)
**Gateway route:** `gateway/routes/v1-users.routes.js`, `v1-roles.routes.js`
**Entities:** User, Role, Permission
**Status:** Frontend-built, Backend-built
**Notes:** Full RBAC system (7 canonical roles, 91 scopes). JWT + Redis-based auth.

---

## 20. Activity / Task Tracking
**Frontend pages:** activity.html (B-06), tasks.html (B-07)
**Backend module:** `backend/services/activity/`, `backend/services/followup/`
**Gateway route:** `gateway/routes/v1-activities.routes.js`, `v1-tasks.routes.js`
**Entities:** Activity, Task (general), FollowupTask
**Status:** Frontend-built, Backend-built

---

## 21. Audit & Compliance
**Frontend pages:** audit-log.html (J-01), compliance-report.html (J-02), data-governance.html (J-03), rbac-audit.html (J-04), privacy.html (J-05), audit-dashboard.html (A-13)
**Backend module:** `src/admin_control_center/`
**Gateway route:** `gateway/routes/v1-audit.routes.js`, `v1-governance.routes.js`, `v1-compliance-settings.routes.js`, `v1-privacy.routes.js`
**Entities:** AuditLog
**Status:** Frontend-built, Backend-built
**Notes:** J-03 (data-governance) confirmed wired to live API (2026-05-31). Hash-chain audit log. Signed CSV export. GDPR/PDPA SAR workflow (governance/sar endpoint).

---

## 22. Settings / Administration
**Frontend pages:** org-settings.html (G-01), billing-settings.html (G-04), integrations.html (G-05), notifications.html (G-06), feature-flags.html (G-07), compliance.html (G-08)
**Backend module:** `src/design_system/`, `src/admin_control_center/`
**Gateway route:** `gateway/routes/v1-org-settings.routes.js`, `v1-integrations.routes.js`, `v1-feature-flags-mgmt.routes.js`, `v1-notification-preferences.routes.js`
**Entities:** FeatureFlag, OrgSettings (inferred)
**Status:** Frontend-built, Backend-built
**Notes:** G-05 (integrations) confirmed wired (2026-05-31). G-06 blocked on P-017 (Urdu strings). G-04 blocked on P-016 (payment credentials).

---

## 23. Custom Objects / Object Builder
**Frontend pages:** object-builder.html (K-02)
**Backend module:** `src/custom_object_framework/` (api.py, entities.py, services.py, layout.py), `src/custom_objects/` (api.py, entities.py, services.py)
**Gateway route:** (inferred — gateway route for custom objects not found in route list; likely proxied via catch-all or not yet surfaced)
**Status:** Frontend-built, Backend-built
**Notes:** Full custom object framework with layout management.

---

## 24. Rule Builder
**Frontend pages:** rule-builder.html (K-03), approval-lanes.html (K-04)
**Backend module:** `src/rule_engine/` (api.py, cpq_api.py, cpq_rules.py, entities.py, services.py)
**Gateway route:** (CPQ rules via /quotes, /orders; rule builder UI → separate endpoint)
**Status:** Frontend-built, Backend-built
**Notes:** CPQ discount routing (>10% requires approval). Approval lanes define multi-level approval chains.

---

## 25. Communication Integrations
**Frontend pages:** integrations.html (G-05)
**Backend module:** `src/communication_integrations/` (api.py, entities.py, services.py)
**Adapters:** `adapters/pakistan/messaging/` (meta_api, gupshup, dialog360, twilio), `adapters/pakistan/payments/` (jazzcash, easypaisa)
**Gateway route:** `gateway/routes/v1-communications.routes.js`, `v1-whatsapp-webhooks.routes.js`
**Status:** Frontend-built, Backend-built
**Notes:** 4 WhatsApp adapters implemented. Payment adapters in stub mode.

---

## 26. External APIs / Webhooks / Plugin Framework
**Frontend pages:** (no dedicated UI — backend-only)
**Backend module:** `src/external_apis_webhooks/` (api.py, auth.py, entities.py, mapping.py, public_api_sdk.py, self_qc.py, services.py), `src/plugin_framework/` (api.py, entities.py, services.py, self_qc.py)
**Gateway route:** `gateway/routes/v1-sync.routes.js`
**Status:** Backend-built
**Notes:** Public API SDK for third-party integrations. Plugin framework for extensibility. Self-QC modules for automated validation.

---

## 27. Event Bus / Data Deduplication
**Frontend pages:** (no dedicated UI — internal infrastructure)
**Backend module:** `src/event_bus/` (api.py, catalog_events.py, catalog_schema.py, core.py, handlers.py, interfaces.py, store.py), `src/data_deduplication_engine/` (entities.py, services.py — no api.py, internal only), `src/execution_hardening/` (concurrency.py)
**Status:** Backend-built (internal services, no public API surface)
**Notes:** Event bus powers WF-001 through WF-005 and all domain event integrations. Deduplication engine used for lead/contact import dedup. Execution hardening provides concurrency control.

---

## 28. Price Books
**Frontend pages:** (referenced in CPQ flows)
**Backend module:** (inferred from gateway route)
**Gateway route:** `gateway/routes/v1-price-books.routes.js`
**Entities:** PriceBook (inferred)
**Status:** Backend-built (gateway route confirmed)

---

## 29. Contract Lifecycle Management
**Frontend pages:** (none — backend-only; no gateway route registered)
**Backend module:** `src/contract_lifecycle_management/` (api.py, entities.py, services.py)
**Gateway route:** None. 12 API paths defined in `api.py::API_ENDPOINTS` dict but no corresponding gateway route file exists. Routes are defined as constants, not mounted handlers.
**Entities:** Contract (12 fields: contract_id, tenant_id, account_id, order_id, subscription_id, invoice_summary_id, owner_user_id, contract_number, title, status, currency, total_contract_value, term_start_at, term_end_at, renewal_alert_days, next_renewal_at), ContractTerm (10 fields)
**Status:** Backend-built (Python logic complete), no gateway exposure
**Domain spec:** `backend/docs/domain/contract-lifecycle-management.md`
**Contract states:** draft → review → approved → active → renewal_pending → terminated
**API paths (code-defined, not yet routed):** GET/POST /contracts, GET /contracts/{id}, POST /contracts/{id}/review, POST /contracts/{id}/approvals, POST /contracts/{id}/activations, POST /contracts/{id}/renewal-pending, POST /contracts/{id}/renewals, POST /contracts/{id}/terminations, POST /contracts/{id}/terms, PUT /contracts/{id}/links, GET /contracts/renewal-alerts
**Human decision required:** Add gateway route + RBAC scope to expose these endpoints, or archive as deferred scope.

---

## Backend Infrastructure Modules (no frontend pages)

| Module | Files | Purpose |
|---|---|---|
| `services/app.py` | FastAPI entrypoint | Main application bootstrap |
| `services/bootstrap.py` | Service bootstrap | Module registration |
| `services/jwt_deps.py` | Auth dependencies | JWT verification for Python services |
| `services/scheduler.py` | Task scheduler | Cron-like job execution (idle detection, SLA checks) |
| `services/summary/daily_summary.py` | Daily summary job | Generates owner daily WhatsApp briefings (MR-004). DailySummaryReport dataclass: leads_captured_today, followups_completed/missed, payments_recorded, escalations_active, pipeline_value. EN + UR templates (UR pending P-017 sign-off). |
| `services/recovery.py` | Failure recovery | Restart/retry failed service operations |
| `services/concurrency.py` | Concurrency control | Distributed locks for critical sections |
| `services/idempotency.py` | Idempotency keys | Prevents duplicate operations |
| `services/evaluator.py` | Rule evaluation | CPQ/territory rule evaluation engine |
| `services/fuzzy_match.py` | Fuzzy matching | Contact/lead deduplication matching |
| `services/parser.py` | Message parser | WhatsApp message intent parsing |
| `services/intent.py` | Intent classification | Conversation intent routing |
| `services/overdue.py` | Overdue detection | Leads/followups/invoices overdue scan |
| `services/reminders.py` | Reminder dispatch | Multi-channel reminder sending |
| `services/retry.py` | Retry logic | Exponential backoff retry handler |
| `middleware/execution_control.py` | Execution middleware | Request-level execution guards |

---

*End MODULE_INVENTORY.md*
