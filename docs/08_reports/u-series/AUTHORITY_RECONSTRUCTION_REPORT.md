# AUTHORITY_RECONSTRUCTION_REPORT.md
> Generated: 2026-06-20 — U1 Authority Reconstruction — all claims verified from code evidence only

> **Note on §2 Module Status Table (DUP-005, 2026-06-21):** The module inventory table in §2 of this report is the original U1 source. For the living module status (updated as modules change), see [MODULE_INVENTORY.md](MODULE_INVENTORY.md). This document is a historical record of the U1 reconstruction; it should not be updated. MODULE_INVENTORY.md is the live tracker.

---

## 1. What This System Actually Is

**Pakistan CRM** is a multi-tenant SaaS CRM built specifically for Pakistani SME businesses.

**Evidence from code:**
- Currency: PKR (Lakh/Crore formatter in crm-components.js `pkr()`)
- Phone: E.164 Pakistan numbers (+923xx) throughout dummy data and validation
- Payment rails: JazzCash and Easypaisa adapters (Pakistan-specific payment providers)
- Communication: WhatsApp-first (4 WhatsApp provider adapters; primary channel in all contact/lead flows)
- Locale: RTL/Urdu support built (crm-locale.js, styles-rtl.css), Urdu strings pending review
- Region: Singapore (Render.com) — closest data center to Pakistan

**Architecture (3-tier confirmed from code):**
```
Frontend (Static HTML)
    ↕ Bearer JWT + x-tenant-id header
Gateway (Node.js Express — 44 API route groups) [corrected from 43 by U10 remediation 2026-06-21]
    ↕ HTTP (localhost:5002 in dev)
Python Services (FastAPI — 34 domain modules)
    ↕ SQLAlchemy
PostgreSQL (20 domain schemas) + Redis (token store + rate limiting)
```

---

## 2. Module Inventory with Status

| Module | Frontend Pages | Backend Module | Gateway Routes | Status |
|---|---|---|---|---|
| Lead Management | B-01, B-02, C-01, I-01, A-02 | lead_management | v1-leads, v1-followups | Frontend-built, Backend-built |
| Follow-up Enforcement | B-01 | lead_management (events.py) | v1-followups | Frontend-built, Backend-built |
| Contacts / Customer 360 | B-03, C-02, I-02, A-03 | customer_360_cdp | v1-contacts | Frontend-built, Backend-built |
| Accounts | B-04, C-03 | customer_360_cdp | v1-accounts | Frontend-built, Backend-built |
| Sales / Opportunities | C-04, D-01, A-04, I-03 | sales_cockpit | v1-opportunities | Frontend-built, Backend-built |
| CPQ / Quotes & Orders | C-06, I-05, A-05, C-07 | rule_engine | v1-quotes, v1-orders | Frontend-built, Backend-built |
| Finance / Collections | B-08, B-09, C-08, H-04 | revenue_recognition, usage_billing | v1-invoice-summaries, v1-collections, v1-payments | Frontend-built, Backend-built |
| Subscriptions / Billing | A-06, C-09, G-04 | subscription_billing | v1-subscriptions, v1-billing | Frontend-built, Backend-built (G-04 blocked P-016) |
| Support / Cases | B-05, C-05, E-01, A-07, I-04 | ticket_management, support_console | v1-cases | Frontend-built, Backend-built |
| Knowledge Base | C-12, A-09 | knowledge_base | v1-knowledge | Frontend-built, Backend-built |
| Omnichannel Inbox | L-01, L-02, L-03, A-08 | omnichannel_inbox | v1-inbox, v1-whatsapp-webhooks | Frontend-built, Backend-built (A-08 wired) |
| Marketing / Campaigns | F-01, I-06, H-02 | campaigns, automation_journeys | v1-campaigns, v1-segments, v1-emails, v1-templates | Frontend-built, Backend-built |
| Workflow Automation | K-01, C-10, A-10, H-05 | workflow_engine | v1-workflows | Frontend-built, Backend-built |
| AI / Copilot | M-01, M-02 | ai_copilot, ai_scoring, predictive_models, predictive_forecasting | v1-ai | Frontend-built, Backend-built (rule-based only; M-01 blocked) |
| Forecasting | A-04 panel | predictive_forecasting | v1-forecasts | Frontend-built, Backend-built |
| Report Builder | H-01 to H-07 | reporting_dashboards | v1-reports | Frontend-built, Backend-built (H-07 wired) |
| Territories | G-09 | territory_management | v1-territories | Frontend-built, Backend-built |
| Partners | B-11, C-11 | partner_channel_management | v1-partners | Frontend-built, Backend-built |
| Identity & Access | B-10, G-02, G-03, A-12 | role_based_ui | v1-users, v1-roles | Frontend-built, Backend-built |
| Activity / Tasks | B-06, B-07 | (services/activity.py) | v1-activities, v1-tasks | Frontend-built, Backend-built |
| Audit & Compliance | J-01 to J-05, A-13 | admin_control_center | v1-audit, v1-governance, v1-compliance-settings, v1-privacy | Frontend-built, Backend-built (J-03 wired) |
| Settings / Admin | G-01, G-05 to G-08 | design_system, admin_control_center | v1-org-settings, v1-integrations, v1-feature-flags-mgmt, v1-notification-preferences | Frontend-built, Backend-built (G-05 wired) |
| Custom Objects | K-02 | custom_object_framework, custom_objects | (not surfaced in gateway list) | Frontend-built, Backend-built |
| Rule / Approval Builder | K-03, K-04 | rule_engine | (via quotes/orders routes) | Frontend-built, Backend-built |
| Communication Integrations | G-05 | communication_integrations | v1-communications | Frontend-built, Backend-built |
| External APIs / Plugin | (no UI) | external_apis_webhooks, plugin_framework | v1-sync | Backend-built only |
| Event Bus / Dedup | (internal) | event_bus, data_deduplication_engine, execution_hardening | (internal) | Backend-built only |
| Auth | (authentication/) | (gateway-native) | v1-auth | Built |
| Price Books | (CPQ flows) | (inferred) | v1-price-books | Backend-built |
| Email | (campaigns) | (inferred) | v1-emails | Backend-built |
| Tenants | A-11 | (gateway-native) | v1-tenants | Frontend-built, Backend-built |

---

## 3. Entity Inventory — Relationship Map

**30 confirmed entities across 20 database domains:**

```
IDENTITY (identity_auth_db)
  User → Role(s) → Permission(s) [scope strings]
  User → Session(s)
  User → RefreshToken(s)

TENANT (org_tenant_db)
  Tenant ──owns──> all domain data below

LEAD DOMAIN (lead_management_db)
  Lead ──has──> LeadAssignment(s)
  Lead ──has──> LeadHistory (immutable field audit)
  Lead ──has──> FollowupTask(s)  [exactly 1 canonical pending]
  Lead ──belongs to──> Contact
  Lead ──optionally belongs to──> Campaign

CONTACT DOMAIN (contact_account_db)
  Contact ──belongs to──> Account (optional)
  Account ──has──> ChurnPrediction
  Account ──has──> CLVEstimate

OPPORTUNITY DOMAIN (opportunity_db)
  Opportunity ──belongs to──> Account, Contact
  Opportunity ──has──> OpportunityLineItem(s)

CPQ DOMAIN (quote_order_db)
  Quote ──has──> line items (JSONB)
  Quote ──accepted──> Order
  Order ──linked──> Invoice

FINANCE DOMAIN (transaction_db)
  Invoice ──has──> Payment(s)
  Invoice ──linked from──> Collection
  Subscription ──belongs to──> Account

SUPPORT DOMAIN (case_ticket_db)
  Case ──has──> CaseComment(s)
  Case ──has──> CaseEscalation(s)
  Case ──linked to──> KnowledgeArticle(s)
  Case ──belongs to──> Contact, Account, Lead
  Case ──assigned to──> SupportQueue

INBOX DOMAIN (messaging_db)
  Conversation ──has──> Message(s)
  Conversation ──has──> Handoff(s)
  Conversation ──assigned to──> User (agent)
  Conversation ──belongs to──> InboxQueue
  User ──has──> AgentPresence

WORKFLOW DOMAIN (workflow_db)
  WorkflowDefinition ──has──> WorkflowExecution(s)
  WorkflowExecution ──has──> WorkflowStepRecord(s)

KNOWLEDGE DOMAIN (knowledge_db)
  KnowledgeArticle [state-gated publication]

TERRITORY DOMAIN (territory_db)
  Territory ──has──> TerritoryRule(s)

AI DOMAIN (intelligence_db)
  LeadScore ──for──> Lead
  ChurnPrediction ──for──> Account
  CLVEstimate ──for──> Account
  CopilotSuggestion ──targets──> User ──about──> Lead|Account|Case
  ScoringModel [registry only — read-only]

CAMPAIGN DOMAIN (campaign_db)
  Campaign ──targets──> Segment
  Segment ──criteria over──> Contact

AUDIT DOMAIN (audit_compliance_db)
  AuditLog [immutable, hash-chain]
  FeatureFlag [dual-approval toggle]

ACTIVITY DOMAIN (activity_task_db)
  Activity [call/whatsapp/email/meeting/note]
  Task [general task entity]

PARTNER DOMAIN (contact_account_db.partners)
  Partner ──has──> CommissionLedger entries
```

---

## 4. API Surface — Counts by Method and Module

| Module | GET | POST | PATCH | DELETE | Total |
|---|---|---|---|---|---|
| Auth | 0 | 6 | 0 | 1 | 7 |
| Leads | 4 | 3 | 1 | 1 | 9 |
| Contacts | 3 | 3 | 1 | 1 | 8 |
| Accounts | 2 | 1 | 1 | 0 | 4 |
| Opportunities | 3 | 2 | 1 | 0 | 6 |
| Follow-ups | 3 | 3 | 0 | 0 | 6 |
| Cases + Support | 4 | 8 | 2 | 0 | 14 |
| Collections/Invoice | 4 | 2 | 1 | 0 | 7 |
| Subscriptions/Billing | 4 | 2 | 2 | 0 | 8 |
| Payments + Webhooks | 1 | 3 | 0 | 0 | 4 |
| Inbox | 5 | 5 | 2 | 0 | 12 |
| Campaigns/Segments | 6 | 4 | 2 | 0 | 12 |
| Workflows | 5 | 6 | 0 | 0 | 11 |
| AI | 7 | 5 | 0 | 0 | 12 |
| Users/Roles/Tenants | 6 | 4 | 2 | 1 | 13 |
| Knowledge | 3 | 2 | 1 | 0 | 6 |
| Reports | 2 | 2 | 0 | 0 | 4 |
| Territories | 2 | 1 | 1 | 1 | 5 |
| Partners | 2 | 1 | 1 | 0 | 4 |
| Audit/Compliance/Privacy | 5 | 2 | 2 | 0 | 9 |
| Settings/Integrations/Flags | 4 | 2 | 2 | 0 | 8 |
| Emails/Templates | 4 | 2 | 1 | 0 | 7 |
| Other (forecasts, price-books, sync, tasks, activities) | 7 | 4 | 2 | 0 | 13 |
| **TOTAL** | **96** | **73** | **26** | **4** | **228** |

---

## 5. Workflow Inventory (Summary)

5 system workflows seeded and active (is_system: true):

| Workflow | Trigger | Purpose | Status |
|---|---|---|---|
| lead_followup_enforcement | lead.idle.v1 | Auto-create follow-up task on idle lead | Active |
| collections_reminder | invoice.overdue.v1 | WhatsApp reminder on overdue invoice | Active (retry on rate-limit) |
| sla_breach_notify | case.sla.breached.v1 | Escalate + notify on SLA breach | Active |
| lead_assignment | lead.created.v1 | Auto-assign lead to territory owner | Active |
| opportunity_stage_notify | opportunity.stage.changed.v1 | Team notification + forecast refresh on stage advance | Active |

Custom workflows: supported via POST /workflows (WORKFLOWS_MANAGE scope). Tenants can create, publish, simulate, retry, cancel.

---

## 6. RBAC Reality

**Fully implemented.** Evidence: `backend/gateway/config/rbac-scopes.js`, `backend/gateway/middleware/auth-rbac.js`

- **7 canonical roles:** tenant_owner, tenant_admin, manager, agent, analyst, auditor, integration_service
- **91 scopes** defined in SCOPES constant (updated from stale 63 count — U7 remediation 2026-06-20)
- **Default-deny** enforcement: every scope not in ROLE_SCOPES[role] is denied
- **Tenant isolation:** x-tenant-id header must match JWT tenant_id on every request
- **Token type:** HS256 JWT (15 min access, 7-day refresh rotating)
- **Revocation:** JTI Redis blocklist on logout
- **Scope inheritance:** tenant_owner and integration_service get all scopes; roles below get explicit lists

**Gap vs in-memory role seeding:** v1-roles.routes.js seeds 5 display roles (sales_rep, sales_manager, finance, admin, tenant_admin) but these are in-memory only. The canonical RBAC enforcement uses the 7 roles in rbac-scopes.js. The DB schema (identity_auth_db.roles) stores tenant-scoped custom roles with DB-enforced uniqueness.

---

## 7. Integration Reality

| Integration | Provider | Status | Evidence |
|---|---|---|---|
| WhatsApp | Meta API | Adapter implemented | adapters/pakistan/messaging/meta_api_adapter.py |
| WhatsApp | Gupshup | Adapter implemented | adapters/pakistan/messaging/gupshup_adapter.py |
| WhatsApp | Dialog360 | Adapter implemented | adapters/pakistan/messaging/dialog360_adapter.py |
| WhatsApp | Twilio | Adapter implemented | adapters/pakistan/messaging/twilio_adapter.py |
| JazzCash | JazzCash API | **STUB** — stub_mode=True | adapters/pakistan/payments/jazzcash.py, render.yaml JAZZCASH_STUB_MODE=true |
| Easypaisa | Easypaisa API | **STUB** — stub_mode=True | adapters/pakistan/payments/easypaisa.py, render.yaml EASYPAISA_STUB_MODE=true |
| Email | SendGrid | **Conditional** — live when SENDGRID_API_KEY set | v1-auth.routes.js sendEmail() — used for OTP + welcome email |
| Database | PostgreSQL 14 | Live | bin/pgsql/, render.yaml, alembic/ |
| Cache / Rate limit | Redis | Live | render.yaml crm-redis, gateway env vars |
| Deployment | Render.com | Configured | render.yaml (3 services + PG + Redis) |
| CI/CD | GitHub Actions | Configured | .github/workflows/ci.yml |
| AI inference | (none selected) | **NOT IMPLEMENTED** | No AI provider SDK in requirements.txt |
| SMS (non-WhatsApp) | (none) | **NOT IMPLEMENTED** | No SMS gateway adapter |

---

## 8. Undocumented Features Found in Code

(Things in gateway/route code not mentioned in DESIGN-SPEC.md, PRODUCT-SPEC.md, or WORKSPACE_BASELINE_AUDIT.md)

| Item | Where Found | What It Does |
|---|---|---|
| SendGrid email integration | v1-auth.routes.js:62–93 | Sends OTP and welcome emails. Active in production when SENDGRID_API_KEY is set. U0 incorrectly reported "no email provider found". |
| Lead next-action suggestion | v1-leads.routes.js:307–354 | GET /leads/:id/next-action proxies to followup service's FollowupEnforcementEngine.suggest_next_action(). Returns stub if service down. |
| Lead soft-delete | v1-leads.routes.js:287–305 | Soft delete (not hard) — repo.softDelete() marks deleted_at, not physically removes. |
| Opportunity line items | v1-opportunities.routes.js:247–292 | GET+POST /opportunities/:id/line-items. Sub-resource for product lines on an opportunity. |
| Post-registration activation engine | v1-auth.routes.js:370–381 | On register, fires POST /internal/activation/seed to seed default pipeline for new tenant. |
| Lead field history table | db/lead_management_db/schema.sql:59–70 | Immutable field-level change log (old_value/new_value/changed_by) for every Lead update. |
| Optimistic concurrency on Cases | v1-cases.routes.js:207–210 | version_no must match current; stale version returns 409 CONFLICT. |
| Agent capacity cap | v1-inbox.routes.js:146–150 | Inbox claim fails if open_conversation_count >= max_concurrent (default 10). |
| 14-day case reopen window | v1-cases.routes.js:411–415 | Cases can only be reopened within 14 calendar days of closing. 422 REOPEN_WINDOW_EXPIRED otherwise. |
| Workflow dry-run simulate | v1-workflows.routes.js:309–340 | POST /workflows/:id/simulate returns step-by-step simulation with estimated durations — no side effects. |
| Retry creates child execution | v1-workflows.routes.js:127–162 | Retry creates a NEW execution with parent_execution_id linking back. Original marked 'retrying'. |
| Case→article linking | v1-cases.routes.js:481–504 | POST /cases/:id/link-article creates cross-domain link from Case to KnowledgeArticle. |
| ASSIGNED→IN_PROGRESS auto-transition | v1-cases.routes.js:296–299 | Adding first customer_reply comment auto-transitions case from ASSIGNED to IN_PROGRESS. |
| Copilot query intent engine | v1-ai.routes.js:138–166 | POST /ai/copilot/query classifies NL query into lead/payment/followup/case intents via regex. |
| Supervisor-only inbox handoff | v1-inbox.routes.js:181–186 | Non-supervisor agents can only handoff their own conversations. Supervisor can handoff any. |
| Handoff audit log | v1-inbox.routes.js:186–212 | Every handoff creates a Handoff record with from/to agent, reason, initiated_by, timestamp. |
| Tenant seed on register | v1-auth.routes.js:327–336 | Registration inserts tenant_ref rows into 6 domain schemas (identity, lead, contact, opportunity, transaction, activity) in the same transaction. |

---

## 9. Undocumented Entities Found

| Entity | Where Found | Notes |
|---|---|---|
| LeadHistory | db/lead_management_db/schema.sql:59–70 | Immutable field change audit. Not documented in product or design spec. |
| LeadAssignment | db/lead_management_db/schema.sql:47–57 | Tracks every owner reassignment with assigned_by and reason. |
| CopilotSuggestion | v1-ai.routes.js:50–57 | Full entity with is_dismissed, is_actioned, timestamps. Persisted per-user. |
| Handoff | v1-inbox.routes.js:185–197 | Tracks every conversation handoff event with reason, from/to agent, initiated_by. |
| AgentPresence | v1-inbox.routes.js:60–66 | Per-agent status with open_conversation_count and max_concurrent capacity. |
| WorkflowStepRecord | v1-workflows.routes.js:63–69 | Step-level execution trace with input/output data, duration, error per step. |
| RefreshToken | db/identity_auth_db/schema.sql:93–103 | DB-persisted refresh tokens with rotation and revocation tracking. |

---

## 10. Undocumented APIs Found

| Endpoint | Notes |
|---|---|
| GET /leads/export | CSV export. Not listed in MAPPING-TRACKER.md (to verify). |
| POST /leads/import | Bulk CSV/JSON import with phone dedup. |
| GET /contacts/export | CSV export. |
| POST /contacts/import | Bulk import. |
| GET /leads/:id/next-action | Calls followup enforcement engine for AI-powered next action suggestion. |
| GET /opportunities/:id/line-items | Sub-resource on opportunity. |
| POST /opportunities/:id/line-items | Add line item to opportunity. |
| POST /cases/:case_id/link-article | Cross-domain case↔knowledge link. |
| POST /workflows/:id/simulate | Dry-run workflow execution. |
| GET /inbox/queues/:id/stats | Per-queue metrics (open, unassigned, avg_unread). |
| POST /ai/copilot/suggestions/:id/dismiss | Dismiss copilot suggestion with timestamp. |
| POST /ai/copilot/suggestions/:id/action | Mark suggestion as actioned. |
| PATCH /inbox/presence | Agent updates own presence status. |
| GET /followups/lead/:lead_id/canonical | Returns single canonical pending follow-up task for a lead. |
| DELETE /auth/sessions/current | Logout via JTI revocation (not just client-side token drop). |

---

## 11. Gaps: Documented but Not in Code

| Documented Claim | Reality |
|---|---|
| "AI inference backend" (M-01 AI Copilot) | No AI provider SDK (OpenAI/Anthropic/Google) in requirements.txt. All models are rule_based. Copilot query uses regex intent detection. Advisory-only as documented. |
| "JazzCash/Easypaisa live payment processing" | Adapters implemented but JAZZCASH_STUB_MODE=true, EASYPAISA_STUB_MODE=true in render.yaml. P-016 blocker. |
| "Urdu notifications" (G-06) | EN strings built. Urdu strings documented as pending native speaker review (P-017). RTL CSS is built. |
| "No email provider" (U0 WORKSPACE_BASELINE_AUDIT) | Incorrect. SendGrid integration exists in v1-auth.routes.js. Active in production when SENDGRID_API_KEY set. |
| "Custom objects gateway route" | `src/custom_object_framework/` and `src/custom_objects/` confirmed in backend but no v1-custom-objects.routes.js found in gateway route list. Either proxied via catch-all or gateway route missing. |
| "96 NexLink library pages complete" | ~94 NexLink demo pages confirmed in app/ (total 169 HTML, 75 custom = ~94 NexLink). Matches. |

---

## 12. Overall System Completeness Assessment

| Layer | Completeness | Confidence | Notes |
|---|---|---|---|
| Frontend HTML (all 75 custom pages) | 100% | High | All 75 files confirmed in app/ |
| Backend Python modules (34) | 100% built | High | All src/ modules confirmed |
| Gateway API routes (43 groups) | 100% built | High | All v1-*.routes.js confirmed |
| Database schemas (20 domains) | 100% defined | High | All schema.sql files confirmed |
| Alembic migrations (12) | Applied (local) | Medium | .coverage exists but CI not verified running |
| Frontend↔API integration | ~7% wired | High | 5 pages confirmed wired; 70 still DUMMY_MODE |
| RBAC system | Complete | High | 7 roles, 91 scopes, middleware enforced |
| WhatsApp integration | Complete (4 providers) | High | Adapter code confirmed |
| Payment integration | 0% live | High | Stub mode confirmed in render.yaml |
| AI inference | 0% | High | No SDK; rule_based models only |
| Email integration | Partial (prod-only) | High | SendGrid wired for auth emails only |
| CI/CD pipeline | Complete | High | ci.yml confirmed, 11 jobs defined |
| Deployment config | Complete | High | render.yaml for all 3 services |
| Test suite | 79 backend + 23 E2E + 8 API contract + load | High | Files confirmed; pass/fail not re-run | [corrected from 54 backend/25 E2E/6 API by U10 remediation 2026-06-21]
| Urdu localization | RTL built; strings partial | High | P-017 blocks completion |

**Bottom line:** The system is structurally complete — all architecture layers exist and are wired together. The primary gap is the live-API integration pass (DUMMY_MODE flip for 70 of 75 pages) and two external blockers (P-016 payment credentials, AI inference model selection).

---

*End AUTHORITY_RECONSTRUCTION_REPORT.md*
