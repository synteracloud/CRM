Status: Draft
Authority Level: Critical
Last Reviewed: 2026-06-22
Owner: Human

# USER_ROLES_AND_PERMISSIONS.md
> Source: backend/gateway/config/rbac-scopes.js (SCOPES constant, ROLE_SCOPES mapping), backend/gateway/middleware/auth-rbac.js (requireScopes()), backend/db/identity_auth_db/schema.sql

---

## 1. Role Hierarchy

7 canonical roles in the system:

| Role Key | Display Name | Description |
|---|---|---|
| `tenant_owner` | Tenant Owner | Highest privilege role. Full access to all scopes. |
| `tenant_admin` | Tenant Admin | Full administrative rights within a single tenant. |
| `manager` | Manager | Manages teams, reviews pipelines, approves workflows. |
| `agent` | Agent | Standard CRM agent — leads, contacts, calls, cases. |
| `analyst` | Analyst | Read-only access plus analytics and AI reads. |
| `auditor` | Auditor | Audit log read and limited data reads (compliance role). |
| `integration_service` | Integration Service | Service accounts with all scopes (non-human). |

---

## 2. Full Scope List (91 scopes)

All 91 scopes extracted from `backend/gateway/config/rbac-scopes.js` SCOPES constant:

### Lead scopes
- `leads.read`
- `leads.create`
- `leads.update`
- `leads.delete` (in ROLE_SCOPES for tenant_admin; **NOT in SCOPES constant** — security gap H-002)
- `leads.import`
- `leads.export`
- `leads.assign`

### Contact scopes
- `contacts.read`
- `contacts.create`
- `contacts.update`
- `contacts.delete` (in route but **absent from SCOPES constant** — security gap H-002)
- `contacts.import`
- `contacts.export`

### Account scopes
- `accounts.read`
- `accounts.create`
- `accounts.update`
- `accounts.delete`

### Opportunity scopes
- `opportunities.read`
- `opportunities.create`
- `opportunities.update`
- `opportunities.delete`
- `opportunities.close`

### Quote scopes
- `quotes.read`
- `quotes.create`
- `quotes.update`
- `quotes.approve`
- `quotes.convert_to_order`

### Order scopes
- `orders.read`
- `orders.fulfil`

### Case / support scopes
- `cases.read`
- `cases.create`
- `cases.update`
- `cases.close`
- `cases.assign`
- `cases.escalate`

### Inbox scopes
- `inbox.read`
- `inbox.claim`
- `inbox.handoff`
- `inbox.supervise`

### Campaign scopes
- `campaigns.read`
- `campaigns.create`
- `campaigns.update`
- `campaigns.activate`

### Workflow scopes
- `workflows.read`
- `workflows.create`
- `workflows.update`
- `workflows.publish`

### Territory scopes
- `territories.read`
- `territories.create`
- `territories.update`
- `territories.delete`
- `territories.assign`

### Activity scopes
- `activities.read`
- `activities.create`

### Task scopes
- `tasks.read`
- `tasks.create`
- `tasks.update`
- `tasks.complete`
- `tasks.assign`

### Collections scopes
- `collections.read`
- `collections.create_invoice`
- `collections.record_payment`
- `collections.approve_payment`
- `collections.reconcile`
- `collections.view_overdue`

### AI scopes
- `ai.score_leads`
- `ai.view_scores`
- `ai.train_models`
- `ai.view_forecasts`
- `ai.generate_forecasts`

### Analytics / reports scopes
- `analytics.view_basic`
- `analytics.view_advanced`
- `analytics.export`

### Knowledge base scopes
- `knowledge.read`
- `knowledge.create`
- `knowledge.update`
- `knowledge.publish`

### Notification scopes
- `notifications.read`
- `notifications.send`

### Partner scopes
- `partners.read`
- `partners.create`
- `partners.update`

### Admin scopes
- `admin.read_audit_logs`
- `admin.manage_users`
- `admin.manage_roles`
- `admin.manage_tenants` (tenant_owner only)
- `admin.manage_feature_flags` (tenant_owner only)
- `admin.system_config`
- `admin.view_platform_health`
- `admin.export_compliance_data`

---

## 3. Role-to-Scope Mapping (ROLE_SCOPES)

Each role's complete scope grant from `rbac-scopes.js`:

### tenant_owner (all scopes — full platform access)
All scopes including admin.manage_tenants, admin.manage_feature_flags, admin.view_platform_health, admin.export_compliance_data, plus all domain scopes.

### tenant_admin (35 scopes — full tenant access)
All domain entity scopes. Includes: leads.delete, contacts.delete, accounts.delete, opportunities.delete/close, quotes.approve/convert_to_order, orders.fulfil, cases.close/assign/escalate, inbox.supervise, campaigns.activate, workflows.publish, territories.delete/assign, tasks.assign, collections.approve_payment/reconcile, ai.train_models/generate_forecasts, analytics.view_advanced/export, knowledge.publish, notifications.send, partners.create/update, admin.read_audit_logs/manage_users/manage_roles/system_config.

### manager (25 scopes)
Includes: leads.read/create/update/export/assign, contacts.read/create/update, accounts.read/create/update, opportunities.read/create/update/close, cases.read/update/close/assign/escalate, inbox.read/claim/supervise, campaigns.read, workflows.read, territories.read, tasks.read/create/update/complete/assign, collections.read/view_overdue, ai.view_scores/view_forecasts/generate_forecasts, analytics.view_advanced, knowledge.read.

### manager (20 scopes — senior operational role)
Includes: leads.read/create/update/assign, contacts.read/create/update, accounts.read/create/update, opportunities.read/create/update, cases.read/create/update/assign, inbox.read/claim/handoff, activities.read/create, tasks.read/create/update/complete, collections.read/view_overdue, ai.view_scores, analytics.view_basic, knowledge.read.

### agent (12 scopes)
Includes: leads.read/create/update, contacts.read/create, accounts.read, opportunities.read/create, cases.read/create, inbox.read/claim, activities.read/create, tasks.read/create/update/complete, notifications.read, knowledge.read.

### agent — collections scopes (8 scopes)
Includes: collections.read/create_invoice/record_payment/view_overdue, contacts.read, accounts.read, leads.read, analytics.view_basic, notifications.read.

### analyst (read-only + analytics scopes)
Includes: leads.read, contacts.read, accounts.read, opportunities.read, cases.read, activities.read, tasks.read, collections.read, payments.read, revenue.read, analytics.view_basic, knowledge.read, ai.view_scores, ai.view_predictions, ai.view_clv, ai.view_models.

---

## 4. Known Security Gaps

### H-002: contacts.delete missing from SCOPES constant
- **Symptom:** `contacts.delete` scope is referenced in `v1-contacts.routes.js` route guard, and in `ROLE_SCOPES.tenant_admin[]`, but NOT present in the `SCOPES` constant object.
- **Effect:** No role can be granted this scope through normal RBAC grant validation, because the scope string doesn't exist in the authoritative constant. Whether this causes a runtime error or silent allow/deny depends on how scopes are assigned at token issuance.
- **Also affected:** `leads.delete` — VERIFIED 2026-06-23: `LEADS_DELETE: 'leads.delete'` IS present in rbac-scopes.js line 21. No gap for leads.delete.
- **Risk level:** High — permanent lock-out of contacts deletion for ALL roles including tenant_admin and tenant_owner.
- **Recommended action:** Add `contacts.delete` to SCOPES constant and grant to tenant_admin + tenant_owner.

---

## 5. How RBAC Is Enforced

### At the Gateway (requireScopes middleware)
```javascript
router.delete('/leads/:id',
  authMiddleware(),
  requireScopes(['leads.delete']),
  async (req, res) => { ... }
);
```

`requireScopes(requiredScopes, options)` validates in order:
1. `x-tenant-id` header present and matches JWT.tenant_id
2. Each scope in `requiredScopes` must be present in `req.auth.scopes[]`
3. If any check fails: 403 forbidden

### Scope inheritance
Scopes are NOT hierarchical — each role's scopes are explicitly listed. There is no "admin includes all lower scopes" runtime inheritance. The ROLE_SCOPES constant defines the complete list per role.

### At the DB layer
No DB-level row enforcement on scope/role. All RBAC enforcement is at the gateway middleware layer.

---

## 6. Database Schema (identity_auth_db)

```sql
-- Roles table (seeded with canonical 7 roles)
CREATE TABLE roles (
  id            UUID PRIMARY KEY,
  tenant_id     UUID NOT NULL REFERENCES tenant_ref(tenant_id),
  name          TEXT NOT NULL,                   -- e.g. 'tenant_admin'
  display_name  TEXT NOT NULL,
  scopes        TEXT[] NOT NULL DEFAULT '{}',   -- scope strings array
  is_system     BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Permissions table (fine-grained if needed beyond scopes)
CREATE TABLE permissions (
  id          UUID PRIMARY KEY,
  scope       TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL
);

-- Role-permission join table
CREATE TABLE role_permissions (
  role_id       UUID REFERENCES roles(id),
  permission_id UUID REFERENCES permissions(id),
  PRIMARY KEY (role_id, permission_id)
);

-- User-role join table (many roles per user possible)
CREATE TABLE user_roles (
  user_id  UUID REFERENCES users(id),
  role_id  UUID REFERENCES roles(id),
  PRIMARY KEY (user_id, role_id)
);
```

---

## 7. Frontend Consumption

The frontend must:
1. Read the `role` claim and `scopes[]` array from the decoded JWT
2. Hide or show UI elements based on scope presence (e.g. only show delete button if `contacts.delete` in scopes)
3. Not rely on role name alone for feature gating — use scopes
4. Never perform scope enforcement on the client-side alone — server always enforces

**Note:** Frontend scope-based UI gating is DEFINED in `docs/03_frontend_authority/FRONTEND_PERMISSION_MATRIX.md` (created Phase 3 Frontend Authority Capture). DUMMY_MODE is false on all pages per FRAMEWORK.md — live API with crm-dummy.js fallback. Scope gating implementation follows FRONTEND_PERMISSION_MATRIX.md rules.

---

*End USER_ROLES_AND_PERMISSIONS.md*
