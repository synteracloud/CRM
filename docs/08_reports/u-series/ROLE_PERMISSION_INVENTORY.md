# ROLE_PERMISSION_INVENTORY.md
> Generated: 2026-06-20 — U1 Authority Reconstruction — evidence from gateway/config/rbac-scopes.js, gateway/routes/v1-roles.routes.js, gateway/middleware/auth-rbac.js, db/identity_auth_db/schema.sql

---

## RBAC Architecture

**Type:** Scope-based RBAC enforced at the API gateway (Node.js) layer.
**Source of truth:** `backend/gateway/config/rbac-scopes.js`

**Enforcement mechanism:**
1. JWT access token carries `role` (string), `scopes` (string[]), `role_ids` (string[]), `territory_ids` (string[])
2. Every protected route calls `requireScopes([...])` middleware
3. Middleware validates: (a) `x-tenant-id` header present and matches JWT `tenant_id`, (b) JWT `scopes` contains all required scopes
4. Token expiry: 15 minutes (access), 7 days (refresh, single-use rotating)
5. Revoked tokens tracked in Redis JTI blocklist (`jti-blocklist.js`)

**Auth algorithm:** HS256 (production, `JWT_SECRET` env var) or unsigned dev token (`SKIP_JWT_VERIFICATION=true`)

---

## Roles — System Roles (from rbac-scopes.js ROLE_SCOPES)

7 canonical roles defined in `backend/gateway/config/rbac-scopes.js`:

| Role | Scope Count | Description |
|---|---|---|
| `tenant_owner` | All (91, via Object.values(SCOPES)) | Unrestricted — every scope defined in SCOPES constant; note: contacts.delete is not in SCOPES, so it is not granted to any role |
| `tenant_admin` | 90 | Full admin minus leads.delete; same as all scopes in practice |
| `manager` | 36 | Full CRM operations; no billing/admin/compliance/privacy |
| `agent` | 22 | Day-to-day CRM; read-only on accounts, campaigns, partners |
| `analyst` | 14 | Read-only across all CRM data; AI models read |
| `auditor` | 5 | audit.read, payments.read, revenue.read, collections.read, sync.read |
| `integration_service` | All (91) | Service account — same as tenant_owner |

---

## Seeded In-Memory Roles (from v1-roles.routes.js)

5 roles seeded in gateway in-memory store (not in DB schema, used for UI display):

| role_id | name | label | Permissions |
|---|---|---|---|
| role-sales-rep | sales_rep | Sales Rep | leads.read, leads.create, followups.read, followups.create, followups.complete, followups.snooze, opportunities.read, contacts.read, activities.read |
| role-sales-mgr | sales_manager | Sales Manager | leads.read/create/update/assign, followups.*, opportunities.read/create/update, contacts.read/create, users.read, audit.read |
| role-finance | finance | Finance | collections.*, payments.*, revenue.read, subscriptions.read, quotes.read, invoices.read |
| role-admin | admin | Admin | users.read/create/update, audit.read, audit.logs.read |
| role-tenant-admin | tenant_admin | Tenant Admin | `*` (all) |

---

## Complete Scope Inventory (91 scopes confirmed in rbac-scopes.js + 1 referenced but missing — see contacts.delete note below)

### Leads
| Scope | Key | Granted To |
|---|---|---|
| leads.read | LEADS_READ | tenant_owner, tenant_admin, manager, agent, analyst, auditor |
| leads.create | LEADS_CREATE | tenant_owner, tenant_admin, manager, agent |
| leads.update | LEADS_UPDATE | tenant_owner, tenant_admin, manager, agent |
| leads.delete | LEADS_DELETE | tenant_owner, tenant_admin |
| leads.assign | LEADS_ASSIGN | tenant_owner, tenant_admin, manager |

### Opportunities
| Scope | Key | Granted To |
|---|---|---|
| opportunities.read | OPPORTUNITIES_READ | tenant_owner, tenant_admin, manager, agent, analyst |
| opportunities.create | OPPORTUNITIES_CREATE | tenant_owner, tenant_admin, manager, agent |
| opportunities.update | OPPORTUNITIES_UPDATE | tenant_owner, tenant_admin, manager, agent |
| opportunities.close | OPPORTUNITIES_CLOSE | tenant_owner, tenant_admin, manager |

### Follow-ups
| Scope | Key | Granted To |
|---|---|---|
| followups.read | FOLLOWUPS_READ | tenant_owner, tenant_admin, manager, agent |
| followups.create | FOLLOWUPS_CREATE | tenant_owner, tenant_admin, manager, agent |
| followups.complete | FOLLOWUPS_COMPLETE | tenant_owner, tenant_admin, manager, agent |
| followups.snooze | FOLLOWUPS_SNOOZE | tenant_owner, tenant_admin, manager, agent |

### Collections / Invoices / Revenue
| Scope | Key | Granted To |
|---|---|---|
| collections.read | COLLECTIONS_READ | tenant_owner, tenant_admin, manager, agent, analyst, auditor |
| collections.invoice | COLLECTIONS_INVOICE | tenant_owner, tenant_admin, manager |
| collections.reconcile | COLLECTIONS_RECONCILE | tenant_owner, tenant_admin |
| payments.read | PAYMENTS_READ | tenant_owner, tenant_admin, manager, agent, analyst, auditor |
| payments.create | PAYMENTS_CREATE | tenant_owner, tenant_admin |
| payments.update | PAYMENTS_UPDATE | tenant_owner, tenant_admin |
| revenue.read | REVENUE_READ | tenant_owner, tenant_admin, manager, analyst, auditor |
| invoices.create | INVOICES_CREATE | tenant_owner, tenant_admin |

### Contacts & Accounts
| Scope | Key | Granted To |
|---|---|---|
| contacts.read | CONTACTS_READ | tenant_owner, tenant_admin, manager, agent, analyst |
| contacts.create | CONTACTS_CREATE | tenant_owner, tenant_admin, manager, agent |
| contacts.update | CONTACTS_UPDATE | tenant_owner, tenant_admin, manager, agent |
| contacts.delete | CONTACTS_DELETE | **SECURITY GAP — scope referenced in v1-contacts.routes.js:139 but absent from rbac-scopes.js SCOPES constant. Route currently inaccessible to all roles (403 on every attempt). Requires human decision: add to rbac-scopes.js and grant to tenant_owner + tenant_admin (consistent with leads.delete pattern), or remove the DELETE endpoint. See H-002 in REMEDIATION_REPORT.md.** |
| accounts.read | ACCOUNTS_READ | tenant_owner, tenant_admin, manager, agent, analyst |
| accounts.create | ACCOUNTS_CREATE | tenant_owner, tenant_admin, manager |
| accounts.update | ACCOUNTS_UPDATE | tenant_owner, tenant_admin, manager |

### CPQ / Quotes / Orders
| Scope | Key | Granted To |
|---|---|---|
| quotes.read | QUOTES_READ | tenant_owner, tenant_admin, manager, agent, analyst |
| quotes.create | QUOTES_CREATE | tenant_owner, tenant_admin, manager, agent |
| quotes.update | QUOTES_UPDATE | tenant_owner, tenant_admin, manager |
| quotes.accept | QUOTES_ACCEPT | tenant_owner, tenant_admin |
| orders.read | ORDERS_READ | tenant_owner, tenant_admin, manager, analyst |
| orders.create | ORDERS_CREATE | tenant_owner, tenant_admin |

### Cases / Support
| Scope | Key | Granted To |
|---|---|---|
| cases.read | CASES_READ | tenant_owner, tenant_admin, manager, agent, analyst |
| cases.create | CASES_CREATE | tenant_owner, tenant_admin, manager, agent |
| cases.update | CASES_UPDATE | tenant_owner, tenant_admin, manager, agent |
| cases.admin | CASES_ADMIN | tenant_owner, tenant_admin, manager |

### Knowledge Base
| Scope | Key | Granted To |
|---|---|---|
| knowledge.read | KNOWLEDGE_READ | tenant_owner, tenant_admin, manager, agent, analyst |
| knowledge.manage | KNOWLEDGE_MANAGE | tenant_owner, tenant_admin, manager |

### Inbox
| Scope | Key | Granted To |
|---|---|---|
| inbox.read | INBOX_READ | tenant_owner, tenant_admin, manager, agent |
| inbox.write | INBOX_WRITE | tenant_owner, tenant_admin, manager, agent |
| inbox.admin | INBOX_ADMIN | tenant_owner, tenant_admin, manager |

### Territories
| Scope | Key | Granted To |
|---|---|---|
| territories.read | TERRITORIES_READ | tenant_owner, tenant_admin, manager, agent |
| territories.write | TERRITORIES_WRITE | tenant_owner, tenant_admin, manager |
| territories.admin | TERRITORIES_ADMIN | tenant_owner, tenant_admin |

### Campaigns / Marketing
| Scope | Key | Granted To |
|---|---|---|
| campaigns.read | CAMPAIGNS_READ | tenant_owner, tenant_admin, manager, agent |
| campaigns.manage | CAMPAIGNS_MANAGE | tenant_owner, tenant_admin, manager |
| marketing.read | MARKETING_READ | tenant_owner, tenant_admin |

### Partners
| Scope | Key | Granted To |
|---|---|---|
| partners.read | PARTNERS_READ | tenant_owner, tenant_admin, manager, agent |
| partners.manage | PARTNERS_MANAGE | tenant_owner, tenant_admin, manager |
| partners.admin | PARTNERS_ADMIN | tenant_owner, tenant_admin |

### Workflows
| Scope | Key | Granted To |
|---|---|---|
| workflows.read | WORKFLOWS_READ | tenant_owner, tenant_admin, manager, agent |
| workflows.manage | WORKFLOWS_MANAGE | tenant_owner, tenant_admin, manager |

### AI / ML
| Scope | Key | Granted To |
|---|---|---|
| ai.scores.read | AI_SCORES_READ | tenant_owner, tenant_admin, manager, agent, analyst |
| ai.scores.recompute | AI_SCORES_RECOMPUTE | tenant_owner, tenant_admin, manager |
| ai.predictions.read | AI_PREDICTIONS_READ | tenant_owner, tenant_admin, manager, analyst |
| ai.clv.read | AI_CLV_READ | tenant_owner, tenant_admin, manager, analyst |
| ai.copilot | AI_COPILOT | tenant_owner, tenant_admin, manager, agent |
| ai.models.read | AI_MODELS_READ | tenant_owner, tenant_admin, manager, analyst |

### Tasks & Activities
| Scope | Key | Granted To |
|---|---|---|
| tasks.read | TASKS_READ | tenant_owner, tenant_admin |
| tasks.create | TASKS_CREATE | tenant_owner, tenant_admin |
| tasks.update | TASKS_UPDATE | tenant_owner, tenant_admin |
| activities.read | ACTIVITIES_READ | tenant_owner, tenant_admin |
| activities.create | ACTIVITIES_CREATE | tenant_owner, tenant_admin |

### Email
| Scope | Key | Granted To |
|---|---|---|
| emails.read | EMAILS_READ | tenant_owner, tenant_admin |
| emails.send | EMAILS_SEND | tenant_owner, tenant_admin |
| emails.track | EMAILS_TRACK | tenant_owner, tenant_admin |

### Forecasting / Pricing
| Scope | Key | Granted To |
|---|---|---|
| forecasts.read | FORECASTS_READ | tenant_owner, tenant_admin |
| pricing.read | PRICING_READ | tenant_owner, tenant_admin |
| pricing.create | PRICING_CREATE | tenant_owner, tenant_admin |

### Subscriptions / Billing
| Scope | Key | Granted To |
|---|---|---|
| subscriptions.read | SUBSCRIPTIONS_READ | tenant_owner, tenant_admin, analyst |
| subscriptions.create | SUBSCRIPTIONS_CREATE | tenant_owner, tenant_admin |
| subscriptions.update | SUBSCRIPTIONS_UPDATE | tenant_owner, tenant_admin |
| billing.read | BILLING_READ | tenant_owner, tenant_admin |
| billing.create | BILLING_CREATE | tenant_owner, tenant_admin |
| billing.manage | BILLING_MANAGE | tenant_owner, tenant_admin |

### Reports
| Scope | Key | Granted To |
|---|---|---|
| reports.read | REPORTS_READ | tenant_owner, tenant_admin |
| reports.create | REPORTS_CREATE | tenant_owner, tenant_admin |

### Integrations / Sync
| Scope | Key | Granted To |
|---|---|---|
| integrations.read | INTEGRATIONS_READ | tenant_owner, tenant_admin |
| integrations.manage | INTEGRATIONS_MANAGE | tenant_owner, tenant_admin |
| sync.read | SYNC_READ | tenant_owner, tenant_admin, manager, agent, analyst, auditor |
| sync.write | SYNC_WRITE | tenant_owner, tenant_admin, manager, agent |

### Compliance / Governance / Privacy
| Scope | Key | Granted To |
|---|---|---|
| compliance.read | COMPLIANCE_READ | tenant_owner, tenant_admin |
| privacy.read | PRIVACY_READ | tenant_owner, tenant_admin |
| privacy.manage | PRIVACY_MANAGE | tenant_owner, tenant_admin |

### Users / Admin
| Scope | Key | Granted To |
|---|---|---|
| users.read | USERS_READ | tenant_owner, tenant_admin, manager |
| users.create | USERS_CREATE | tenant_owner, tenant_admin |
| users.update | USERS_UPDATE | tenant_owner, tenant_admin |
| users.manage_roles | USERS_MANAGE_ROLES | tenant_owner, tenant_admin |
| audit.read | AUDIT_READ | tenant_owner, tenant_admin, auditor |
| audit.logs.read | AUDIT_LOGS_READ | tenant_owner, tenant_admin |

---

## Route → Scope Mapping (key routes from code evidence)

| Route | Method | Required Scopes |
|---|---|---|
| /auth/login | POST | none |
| /auth/register | POST | none |
| /auth/refresh | POST | none |
| /auth/forgot-password | POST | none |
| /auth/reset-password | POST | none |
| /auth/sessions/current | DELETE | auth (JWT) |
| /leads | GET | leads.read |
| /leads | POST | leads.create |
| /leads/:id | GET | leads.read |
| /leads/:id | PATCH | leads.update |
| /leads/:id | DELETE | leads.delete |
| /leads/:id/next-action | GET | followups.read |
| /leads/export | GET | leads.read |
| /leads/import | POST | leads.create |
| /contacts | GET | contacts.read |
| /contacts | POST | contacts.create |
| /contacts/:id | PATCH | contacts.update |
| /contacts/:id | DELETE | contacts.delete [SECURITY GAP — scope absent from rbac-scopes.js; endpoint inaccessible to all roles] |
| /opportunities | GET | opportunities.read |
| /opportunities | POST | opportunities.create |
| /opportunities/:id | PATCH | opportunities.update |
| /opportunities/:id/line-items | GET | opportunities.read |
| /opportunities/:id/line-items | POST | opportunities.update |
| /followups | GET | followups.read |
| /followups | POST | followups.create |
| /followups/:id/complete | POST | followups.complete |
| /followups/:id/snooze | POST | followups.snooze |
| /cases | GET | cases.read |
| /cases | POST | cases.create |
| /cases/:id | PATCH | cases.update |
| /cases/:id/assign | POST | cases.admin |
| /cases/:id/comments | POST | cases.update |
| /cases/:id/resolve | POST | cases.update |
| /cases/:id/close | POST | cases.admin |
| /cases/:id/reopen | POST | cases.update |
| /cases/:id/escalate | POST | cases.admin |
| /cases/:id/link-article | POST | cases.update |
| /support/queues | GET | cases.read |
| /support/queues | POST | cases.admin |
| /support/queues/:id | PATCH | cases.admin |
| /workflows | GET | workflows.read |
| /workflows | POST | workflows.manage |
| /workflows/:id/publish | POST | workflows.manage |
| /workflows/:id/simulate | POST | workflows.read |
| /workflows/runs | GET | workflows.read |
| /workflows/runs/:id/retry | POST | workflows.manage |
| /workflows/runs/:id/cancel | POST | workflows.manage |
| /ai/scores/leads | GET | ai.scores.read |
| /ai/scores/leads/:id/recompute | POST | ai.scores.recompute |
| /ai/predictions/churn | GET | ai.predictions.read |
| /ai/estimates/clv | GET | ai.clv.read |
| /ai/copilot/query | POST | ai.copilot |
| /ai/copilot/suggestions | GET | ai.copilot |
| /ai/models | GET | ai.models.read |
| /inbox/conversations | GET | inbox.read |
| /inbox/conversations/:id/claim | POST | inbox.write |
| /inbox/conversations/:id/handoff | POST | inbox.write |
| /inbox/conversations/:id/messages | POST | inbox.write |
| /inbox/presence | PATCH | inbox.read |
| /inbox/presence | GET | inbox.admin |
| /inbox/queues | GET | inbox.admin |
| /inbox/queues | POST | inbox.admin |
| /roles | GET | users.read |
| /roles | POST | users.update |
| /roles/:id | PATCH | users.update |
| /roles/:id | DELETE | users.update |

---

## DB Schema — Identity/RBAC Tables

Source: `backend/db/identity_auth_db/schema.sql`

- **users** — user_id (PK), tenant_id (FK), email (UNIQUE per tenant), password_hash, full_name, status (active/suspended/deactivated), last_login_at, created_at, updated_at
- **roles** — role_id (PK), tenant_id (FK), name (UNIQUE per tenant), description, is_system (bool), created_at
- **permissions** — permission_id (PK), scope (TEXT UNIQUE), description, created_at
- **role_permissions** — (role_id, permission_id) PK — junction table
- **user_roles** — (user_id, role_id) PK — junction table with tenant_id, granted_by, granted_at
- **sessions** — session_id (PK), user_id, tenant_id, token_hash (UNIQUE), ip_address, user_agent, expires_at, revoked_at, created_at
- **refresh_tokens** — token_id (PK), user_id, tenant_id, token_hash (UNIQUE), expires_at, rotated_at, revoked_at, created_at

---

*End ROLE_PERMISSION_INVENTORY.md*
