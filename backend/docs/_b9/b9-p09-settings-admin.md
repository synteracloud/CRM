# B9-P09::SETTINGS_ADMIN_CONFIG_RBAC

## Scope

Defines the **Settings / Admin / Config / RBAC** archetype — 9 named admin surfaces.
Anchored to `docs/security/identity-auth-rbac.md`, `docs/infrastructure/feature-flags-config.md`, `docs/security/org-multi-tenancy.md`.

---

## 1) Archetype Structure

Settings surfaces use a **two-pane configuration shell**:

```
┌─ Left nav (settings categories, role-gated) ──────────────┐
├──────────────────────────┬────────────────────────────────┤
│  Config panel (main)     │  Preview / impact panel        │
│  - Policy editor         │  - Current effective state     │
│  - Form fields           │  - Affected entities/users     │
│  - Save / revert         │  - Audit trail for this config │
└──────────────────────────┴────────────────────────────────┘
```

**Design rules:**
- All changes show an **impact preview** before commit.
- Save emits audit event (captured in `AuditLog`).
- Destructive changes (delete role, disable feature) require confirmation + reason entry.
- Settings not applicable to the user's role are hidden (not just disabled).

---

## 2) The 9 Settings / Admin Pages

### 2.1 — Admin Control Center

**Route:** `/app/admin`
**Role gate:** `tenant_admin`, `super_admin`

Landing page for all admin surfaces. Displays:
- Active tenant name, plan tier, entitlement summary
- Quick-access tiles for each settings section (2.2–2.9)
- Recent admin activity (last 10 audit entries for admin actions)
- Health summary: user count, active sessions, feature flags enabled

---

### 2.2 — Identity & RBAC

**Route:** `/app/admin/identity`
**Role gate:** `tenant_admin`, `super_admin`
**Source entities:** `User`, `Role`, `Permission`, `UserRole`, `RolePermission`

**Sections:**
1. **Users** — list, invite, suspend, reset password. Filter by role/status.
2. **Roles** — create, edit, delete roles. Role = set of permissions.
3. **Permissions** — view all permission constants (read-only; defined in `gateway/config/rbac-scopes.js`).
4. **Role assignments** — assign/remove roles from users. Changes take effect on next session.

**Constraints:**
- Cannot delete a role that has active user assignments.
- Cannot remove the last `tenant_admin` from a tenant.
- All role changes logged in `AuditLog` with actor, target, before/after state.

---

### 2.3 — Feature Flags Config

**Route:** `/app/admin/feature-flags`
**Role gate:** `tenant_admin`, `super_admin`
**Source entities:** `FeatureFlag`, `FeatureFlagRule`

**Sections:**
1. **Flag registry** — list all flags with current enabled/disabled state per tenant.
2. **Flag rules** — per-flag rule editor: enable for specific roles, users, or percentage rollout.
3. **Override panel** — force-enable/disable for current tenant (overrides rules).

**Behaviour:**
- `contact.fuzzy_name_match` flag controls fuzzy duplicate detection.
- Changes evaluated immediately via `gateway/services/feature-flags.js`.
- Default for all new flags: `FALSE` (off by default per `db/feature_flag_db/schema.sql`).

---

### 2.4 — Plugin Framework

**Route:** `/app/admin/plugins`
**Role gate:** `super_admin`
**Source entities:** Custom Object definitions

**Sections:**
1. **Installed plugins** — list active extensions with version, permissions claimed, and install date.
2. **Available plugins** — marketplace listing (read-only in MVP; links to docs).
3. **Plugin permissions** — scopes granted per plugin; revoke individual permissions.

---

### 2.5 — External APIs & Webhooks

**Route:** `/app/admin/integrations/api`
**Role gate:** `tenant_admin`, `super_admin`

**Sections:**
1. **API keys** — create, rotate, revoke API keys per tenant. Display scope + last used.
2. **Webhook endpoints** — register URLs for event push. Select events to subscribe.
3. **Delivery log** — last 100 webhook attempts with HTTP status + retry count.
4. **Dead letter queue** — failed events from `webhook_dead_letter` table. Manual replay or dismiss.

---

### 2.6 — Communication Integrations Config

**Route:** `/app/admin/integrations/communications`
**Role gate:** `tenant_admin`, `super_admin`

**Sections:**
1. **WhatsApp provider** — select Meta / 360dialog / Gupshup / Twilio. Enter API credentials. Test connection.
2. **Email** — SMTP config or provider integration (SendGrid, SES).
3. **Notification channels** — SMS, push notification config.
4. **Webhook verification** — HMAC secret per provider (drives adapter verification).

**Design rule:** Credentials never displayed after save — only masked last-4. Rotate via dedicated button.

---

### 2.7 — Territory Management

**Route:** `/app/admin/territories`
**Role gate:** `sales_manager`, `tenant_admin`
**Source entities:** `Territory`, `TerritoryRule`, `TerritoryAssignment` (from `db/territory_db/schema.sql`)

**Sections:**
1. **Territory tree** — hierarchical view of territories with parent/child relationships.
2. **Rule editor** — criteria JSONB rules per territory (geo, account tier, industry).
3. **Assignments** — current user→territory mapping. Superseded assignments visible in history.

---

### 2.8 — Custom Object Framework Admin

**Route:** `/app/admin/custom-objects`
**Role gate:** `super_admin`, `tenant_admin`
**Source docs:** `docs/domain/custom-object-framework.md`

**Sections:**
1. **Object registry** — list custom object types with field count, record count.
2. **Schema editor** — add/edit/deprecate fields on a custom object type.
3. **Layout builder** — visual field arrangement editor (feeds into Custom Object Layout Builder archetype — see `b9-p08-builder-extensions.md`).
4. **Permissions** — which roles can create/read/update/delete records of each object type.

---

### 2.9 — Price Books Management

**Route:** `/app/admin/price-books`
**Role gate:** `finance`, `tenant_admin`
**Source entities:** `PriceBook`, `PriceBookEntry`, `Product`

**Sections:**
1. **Price books** — list active and archived price books.
2. **Price book editor** — add/edit products and unit prices per price book.
3. **Effective date management** — schedule price changes with future effective dates.
4. **Currency config** — base currency (PKR default) and exchange rate for multi-currency quotes.

---

## 3) Interaction Patterns

1. **Impact preview before save:** Every change shows affected entities count + sample before committing.
2. **Audit every write:** All config saves emit entries to `AuditLog` — actor, timestamp, field, before, after.
3. **Confirmation for destructive ops:** Role delete, flag disable, credential rotate all require typed confirmation.
4. **Settings search:** Global settings search (top of left nav) finds any config panel by keyword.
5. **Role-gate visibility:** Left nav shows only panels accessible to the current user's role — no disabled links.

---

## SELF-QC

- **All 9 Archetype.md settings pages documented:** ✅ — 2.1–2.9 match exactly.
- **Every page role-gated:** ✅
- **Audit trail requirement stated for all write operations:** ✅
- **Credential masking rule documented:** ✅
- **Custom object framework cross-referenced:** ✅
- **Feature flag default (FALSE) confirmed:** ✅

Score: **10/10**
