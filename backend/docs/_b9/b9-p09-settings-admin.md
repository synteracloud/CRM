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

### 2.2 — User Management (G-02)

**Route:** `/app/admin/users/manage`
**Role gate:** `tenant_admin`, `super_admin`
**Source entities:** `User`, `UserRole`

**Sections:**
1. **Users** — list, invite, suspend, reset password. Filter by role/status.
2. **Role assignments** — assign/remove roles from users. Changes take effect on next session.

**Constraints:**
- Cannot remove the last `tenant_admin` from a tenant.
- All role changes logged in `AuditLog` with actor, target, before/after state.

---

### 2.3 — Role & Permission Editor (G-03)

**Route:** `/app/admin/roles`
**Role gate:** `tenant_admin`, `super_admin`
**Source entities:** `Role`, `Permission`, `RolePermission`

**Sections:**
1. **Roles** — create, edit, delete roles. Role = set of permissions.
2. **Permissions** — view all permission constants (read-only; defined in `gateway/config/rbac-scopes.js`).

**Constraints:**
- Cannot delete a role that has active user assignments.
- All role changes logged in `AuditLog` with actor, target, before/after state.

---

### 2.4 — Feature Flags Config (G-07)

**Route:** `/app/admin/feature-flags`
**Role gate:** `tenant_admin`, `super_admin`
**Source entities:** `FeatureFlag`, `FeatureFlagRule`
**Entity contract:** `docs/infrastructure/feature-flags-config.md`

**Sections:**
1. **Flag registry** — list all flags with current enabled/disabled state per tenant.
2. **Flag rules** — per-flag rule editor. `rule_type` values (from `feature-flags-config.md`): `tenant_match` / `role_match` / `percentage_rollout` / `env_match`. Priority order: highest numeric priority wins. Percentage rollout uses SHA-256 deterministic bucket assignment on `tenant_id`.
3. **Override panel** — force-enable/disable for current tenant (overrides rules).

**Behaviour:**
- `contact.fuzzy_name_match` flag controls fuzzy duplicate detection.
- Changes evaluated immediately via `gateway/services/feature-flags.js`. SLO: P95 ≤20ms evaluation.
- Default for all new flags: `FALSE` (off by default).
- **Change approval:** Flag changes require 2-person approval (4hr timeout). Emergency override allowed with 24hr post-review. All approvals logged in `AuditLog`.
- Expired flags (past `expires_at`) auto-archive after 7 days.

---

### 2.5 — Plugin Framework

**Route:** `/app/admin/plugins`
**Role gate:** `super_admin`
**Source entities:** Custom Object definitions

**Sections:**
1. **Installed plugins** — list active extensions with version, permissions claimed, and install date.
2. **Available plugins** — marketplace listing (read-only in MVP; links to docs).
3. **Plugin permissions** — scopes granted per plugin; revoke individual permissions.

---

### 2.6 — External APIs & Webhooks

**Route:** `/app/admin/integrations/api`
**Role gate:** `tenant_admin`, `super_admin`

**Sections:**
1. **API keys** — create, rotate, revoke API keys per tenant. Display scope + last used.
2. **Webhook endpoints** — register URLs for event push. Select events to subscribe.
3. **Delivery log** — last 100 webhook attempts with HTTP status + retry count.
4. **Dead letter queue** — failed events from `webhook_dead_letter` table. Manual replay or dismiss.

---

### 2.7 — Communication Integrations Config

**Route:** `/app/admin/integrations/communications`
**Role gate:** `tenant_admin`, `super_admin`

**Sections:**
1. **WhatsApp provider** — select Meta / 360dialog / Gupshup / Twilio. Enter API credentials. Test connection.
2. **Email** — SMTP config or provider integration (SendGrid, SES).
3. **Notification channels** — SMS, push notification config.
4. **Webhook verification** — HMAC secret per provider (drives adapter verification).

**Design rule:** Credentials never displayed after save — only masked last-4. Rotate via dedicated button.

---

### 2.8 — Territory & Assignment Config (G-09)

**Route:** `/app/admin/territories`
**Role gate:** `sales_manager`, `tenant_admin`
**Source entities:** `Territory`, `TerritoryRule`, `TerritoryAssignment`
**Entity contract:** `docs/domain/territory-management.md`

**`Territory.criteria_type` enum:** `geographic` / `postal` / `account_segment` / `rep_assigned` / `hybrid`

**`TerritoryRule.rule_type` enum:** `city` / `postal_code` / `region` / `geo_polygon` / `account_industry` / `account_size` / `account_tier` / `rep_explicit` / `custom_field`

Multiple rules on a territory combine with AND logic. Conflict resolution uses `Territory.routing_priority` (lower = higher priority) → rule specificity → UUID tiebreaker.

**Rep assignment strategies within territory:** `round_robin` / `least_loaded` / `explicit_rule` / `single_rep`

**Sections:**
1. **Territory tree** — hierarchical view (max 3 levels: root → region → area). Parent/child relationships. Shows `assigned_reps[]` and `primary_manager` per territory.
2. **Rule editor** — add/edit `TerritoryRule` criteria per territory. `criteria_value` JSONB schema varies by `rule_type`. Rules combine with AND logic.
3. **Assignments** — current user→territory mapping. `TerritoryAssignment` records are immutable; re-assignment creates new record (old superseded). History tab shows superseded assignments.
4. **Performance** — links to `TerritoryPerformanceRM` read model (from `read-models.md`) for territory-scoped KPIs.

**Invariants:**
- Exactly one territory per tenant must have `is_default = true`.
- Every lead must receive a territory assignment within 1 minute of creation (scanner SLA).
- Territory-scoped queries use `TerritoryAssignment` table — never re-evaluate criteria at query time.

---

### 2.9 — Custom Object Framework Admin

**Route:** `/app/admin/custom-objects`
**Role gate:** `super_admin`, `tenant_admin`
**Source docs:** `docs/domain/custom-object-framework.md`

**Sections:**
1. **Object registry** — list custom object types with field count, record count.
2. **Schema editor** — add/edit/deprecate fields on a custom object type.
3. **Layout builder** — visual field arrangement editor (feeds into Custom Object Layout Builder archetype — see `b9-p08-builder-extensions.md`).
4. **Permissions** — which roles can create/read/update/delete records of each object type.

---

### 2.10 — Price Books Management

**Route:** `/app/admin/price-books`
**Role gate:** `finance`, `tenant_admin`
**Source entities:** `PriceBook`, `PriceBookEntry`, `Product`

**Sections:**
1. **Price books** — list active and archived price books.
2. **Price book editor** — add/edit products and unit prices per price book.
3. **Effective date management** — schedule price changes with future effective dates.
4. **Currency config** — base currency (PKR default) and exchange rate for multi-currency quotes.

---

### 2.11 — Organization Settings (G-01)

**Route:** `/app/settings/org`
**Role gate:** `tenant_admin`, `super_admin`

**Sections:**
1. **Tenant identity** — name, logo upload, business address.
2. **Locale** — timezone (default `UTC+5 PKT`), date format, language default (EN / UR).
3. **Currency** — base currency (default PKR); Lakh/Crore notation enabled by default.
4. **Business hours** — 09:00–19:00 PKT Mon–Sat default; configurable per tenant (affects SLA calculations).

---

### 2.12 — Billing & Subscription Settings (G-04)

**Route:** `/app/settings/billing`
**Role gate:** `finance`, `tenant_admin`
**Blocked by:** P-016 (JazzCash/Easypaisa credentials) — payment method configuration is stub-mode until P-016 resolved.

**Sections:**
1. **Current plan** — display plan tier (Starter/Growth/Business/Enterprise from `pricing-plans.md`), billing cycle, renewal date, seat count.
2. **Upgrade / downgrade** — plan change flow. Downgrade deferred to period end; data retained read-only + 14-day grace for seat over-limit.
3. **Payment method** — JazzCash / Easypaisa / bank transfer. Stub badge shown until P-016 unblocked.
4. **Invoice history** — past billing invoices (PDF download).

---

### 2.13 — Notification Settings (G-06)

**Route:** `/app/settings/notifications`
**Role gate:** any authenticated user (own preferences); `tenant_admin` for tenant-wide defaults

**Sections:**
1. **Per-event rules** — toggle notification on/off per event type (new lead, follow-up overdue, SLA breach, payment received, etc.).
2. **Channel preference** — per event: WhatsApp / email / in-app / SMS. WhatsApp channel requires `P-017` Urdu string sign-off before customer-facing notifications are enabled.
3. **Quiet hours** — define window when notifications are suppressed (respects PKT timezone).

---

### 2.14 — Compliance Settings (G-08)

**Route:** `/app/settings/compliance`
**Role gate:** `super_admin`, `compliance_officer`

**Sections:**
1. **Audit retention policy** — configure retention window per entity class (min: 7 years for financial; configurable for others per `data-governance-layer.md`).
2. **Data governance controls** — link to Data Governance Console (J-03) for classification, retention rules, and subject access requests.
3. **Break-glass log** — read-only log of all break-glass access events (Platform Security Ops only; 4hr TTL; 2-approver requirement per `security-model.md`).

---

## 3) Interaction Patterns

1. **Impact preview before save:** Every change shows affected entities count + sample before committing.
2. **Audit every write:** All config saves emit entries to `AuditLog` — actor, timestamp, field, before, after.
3. **Confirmation for destructive ops:** Role delete, flag disable, credential rotate all require typed confirmation.
4. **Settings search:** Global settings search (top of left nav) finds any config panel by keyword.
5. **Role-gate visibility:** Left nav shows only panels accessible to the current user's role — no disabled links.

---

## 4) API Routes

All endpoints below **must be created as inline gateway routes** before building. Follow the Phase 5B inline stub pattern: in-memory store, `respondSuccess`/`respondError`, `requireScopes`, no downstream service dependency.

### G-01 — Organization Settings

| Endpoint | Method | Scope | Payload / Response | Status |
|---|---|---|---|---|
| `/org/settings` | GET | `org.read` | Returns org config object (see field contract below) | **CREATE in `v1-org-settings.routes.js`** |
| `/org/settings` | PATCH | `org.update` | Partial update of org config fields | **CREATE in `v1-org-settings.routes.js`** |

**Org settings field contract:**
```json
{
  "tenant_name": "string",
  "timezone": "Asia/Karachi",
  "date_format": "DD/MM/YYYY",
  "language_default": "en",
  "base_currency": "PKR",
  "lakh_crore_notation": true,
  "business_hours": {
    "start": "09:00",
    "end": "19:00",
    "days": ["mon","tue","wed","thu","fri","sat"],
    "timezone": "Asia/Karachi"
  }
}
```

---

### G-03 — Roles & Permissions

| Endpoint | Method | Scope | Notes | Status |
|---|---|---|---|---|
| `/roles` | GET | `roles.read` | Returns array of `Role` objects with permission lists | **CREATE in `v1-roles.routes.js`** |
| `/roles` | POST | `roles.create` | Create new role with `name` + `permissions[]` | **CREATE in `v1-roles.routes.js`** |
| `/roles/:role_id` | PATCH | `roles.update` | Update role name or permissions | **CREATE in `v1-roles.routes.js`** |
| `/roles/:role_id` | DELETE | `roles.delete` | 409 if active user assignments exist | **CREATE in `v1-roles.routes.js`** |
| `/users` | GET | `users.read` | **EXISTS** — `CRM_API.users.list()` — for displaying user→role assignments | Live |

**Role entity shape:**
```json
{
  "role_id": "string",
  "name": "string",
  "tenant_id": "string",
  "permissions": ["leads.read", "leads.create", "..."],
  "active_user_count": 0,
  "created_at": "ISO-8601"
}
```

Seed data: standard roles from `gateway/config/rbac-scopes.js` — `sales_rep`, `sales_manager`, `finance`, `admin`, `tenant_admin`.

---

### G-06 — Notification Settings

| Endpoint | Method | Scope | Notes | Status |
|---|---|---|---|---|
| `/notification-preferences` | GET | `notifications.read` | Returns per-user preference object | **CREATE in `v1-notification-preferences.routes.js`** |
| `/notification-preferences` | PATCH | `notifications.update` | Partial update of toggles | **CREATE in `v1-notification-preferences.routes.js`** |

**Notification preference field contract:**
```json
{
  "user_id": "string",
  "events": {
    "new_lead":          { "in_app": true, "email": true, "whatsapp": false, "sms": false },
    "followup_overdue":  { "in_app": true, "email": true, "whatsapp": true,  "sms": false },
    "sla_breach":        { "in_app": true, "email": true, "whatsapp": true,  "sms": false },
    "payment_received":  { "in_app": true, "email": false,"whatsapp": false, "sms": false }
  },
  "quiet_hours": {
    "enabled": false,
    "start": "22:00",
    "end": "08:00",
    "timezone": "Asia/Karachi"
  }
}
```

---

### G-07 — Feature Flags

| Endpoint | Method | Scope | Notes | Status |
|---|---|---|---|---|
| `/feature-flags` | GET | `feature_flags.read` | Returns all flags with current state per tenant | **CREATE in `v1-feature-flags-mgmt.routes.js`** |
| `/feature-flags/:flag_key` | PATCH | `feature_flags.manage` | Toggle or update rule for a single flag | **CREATE in `v1-feature-flags-mgmt.routes.js`** |

**Note:** `gateway/services/feature-flags.js` handles flag **evaluation** (P95 ≤20ms). This new route handles **management** (CRUD of flag state). The management route reads/writes the same flag registry that `feature-flags.js` evaluates.

**Feature flag entity shape:**
```json
{
  "flag_key": "contact.fuzzy_name_match",
  "description": "Enable fuzzy duplicate detection on contact create",
  "enabled": false,
  "rule_type": "tenant_match",
  "rule_value": null,
  "expires_at": null,
  "approval_required": true,
  "last_changed_by": "user_id",
  "last_changed_at": "ISO-8601"
}
```

---

### G-08 — Compliance Settings

| Endpoint | Method | Scope | Notes | Status |
|---|---|---|---|---|
| `/compliance/settings` | GET | `compliance.read` | Returns compliance configuration object | **CREATE in `v1-compliance-settings.routes.js`** |
| `/compliance/settings` | PATCH | `compliance.update` | Update retention windows or break-glass policy | **CREATE in `v1-compliance-settings.routes.js`** |
| `/audits/events` | GET | `audit.logs.read` | **EXISTS** — break-glass log sourced from `listAuditEvents()` | Live |

**Compliance settings field contract:**
```json
{
  "retention_policies": {
    "financial": { "years": 7, "legal_basis": "regulatory" },
    "crm_activity": { "years": 3, "legal_basis": "legitimate_interest" },
    "audit_log": { "years": 7, "legal_basis": "regulatory" }
  },
  "break_glass": {
    "require_two_approvers": true,
    "ttl_hours": 4,
    "post_review_window_hours": 24
  },
  "gdpr_mode": false,
  "pdpa_mode": true
}
```

---

### J-05 — Consent & Privacy Manager

| Endpoint | Method | Scope | Notes | Status |
|---|---|---|---|---|
| `/privacy/consent` | GET | `privacy.read` | Returns consent records list for tenant | **CREATE in `v1-privacy.routes.js`** |
| `/privacy/consent/:contact_id` | GET | `privacy.read` | Returns consent record for a specific contact | **CREATE in `v1-privacy.routes.js`** |
| `/privacy/consent/:contact_id` | PATCH | `privacy.update` | Revoke or update consent flags | **CREATE in `v1-privacy.routes.js`** |
| `/privacy/requests` | GET | `privacy.read` | Lists data subject requests (DSRs) | **CREATE in `v1-privacy.routes.js`** |
| `/privacy/requests` | POST | `privacy.manage` | Create new DSR (export or deletion) | **CREATE in `v1-privacy.routes.js`** |

**Consent record field contract:**
```json
{
  "contact_id": "string",
  "contact_name": "string",
  "service_communication": { "granted": true, "granted_at": "ISO-8601", "channel": "whatsapp_inbound" },
  "marketing": { "granted": false, "revoked_at": "ISO-8601", "keyword": "STOP" },
  "data_processing": { "granted": true, "granted_at": "ISO-8601" }
}
```

---

### G-04 — Billing & Subscription Settings

**Source doc:** `docs/product/pricing-plans.md` §7 (canonical endpoint definitions).
**Note:** P-016 (JazzCash/Easypaisa payment method) remains stub-only. All endpoints below are internally wirable without P-016.

| Endpoint | Method | Scope | Notes | Status |
|---|---|---|---|---|
| `/billing/plans` | GET | (public — no scope) | Returns all available plans with PKR pricing and feature matrix from `pricing-plans.md` | **CREATE in `v1-billing.routes.js`** |
| `/billing/subscription` | GET | `billing.read` | Returns current tenant plan tier, billing cycle, renewal date, seat count, `is_trial` | **CREATE in `v1-billing.routes.js`** |
| `/billing/subscription/upgrade` | POST | `billing.manage` | Request plan upgrade — stub returns 200 with updated plan (real flow requires P-016) | **CREATE in `v1-billing.routes.js`** |
| `/billing/subscription/downgrade` | POST | `billing.manage` | Schedule downgrade for end of period — stub returns 200 with effective date | **CREATE in `v1-billing.routes.js`** |
| `/billing/invoices` | GET | `billing.read` | Returns past billing invoice history (subscription payment records) | **CREATE in `v1-billing.routes.js`** |
| `/billing/entitlements` | GET | `billing.read` | Returns list of enabled feature flag keys for current tenant's plan | **CREATE in `v1-billing.routes.js`** |

**`/billing/subscription` response shape:**
```json
{
  "plan_code": "plan_growth",
  "plan_label": "Growth",
  "billing_cycle": "annual",
  "current_period_start": "2026-01-01",
  "current_period_end": "2027-01-01",
  "renewal_date": "2027-01-01",
  "seat_limit": 20,
  "seat_used": 5,
  "is_trial": false,
  "subscription_status": "active",
  "monthly_price_pkr": 5999,
  "annual_price_pkr": 61189
}
```

**`/billing/invoices` response shape:**
```json
{
  "data": [
    { "invoice_id": "string", "invoice_number": "string", "period": "string", "amount_pkr": 0, "status": "paid", "issued_at": "ISO-8601" }
  ]
}
```

---

### G-05 — Integration Settings

**Route note:** DESIGN-SPEC.md §3 places G-05 at `/app/settings/integrations`. b9-p09 §2.7 lists route as `/app/admin/integrations/communications` — the page was built at the DESIGN-SPEC route. b9-p09 §2.7 route reference is informational only; `/app/settings/integrations` is authoritative.

| Endpoint | Method | Scope | Notes | Status |
|---|---|---|---|---|
| `/integrations` | GET | `integrations.read` | Returns all integration configs (WhatsApp/Email/SMS/Push) with `status` and `last_tested_at` | **CREATE in `v1-integrations.routes.js`** |
| `/integrations/:provider` | PATCH | `integrations.manage` | Update credentials/config for a provider. Credentials never returned after save — only masked `last_4` | **CREATE in `v1-integrations.routes.js`** |
| `/integrations/:provider/test` | POST | `integrations.manage` | Test connection — returns `{ ok: bool, latency_ms: int, message: string }` | **CREATE in `v1-integrations.routes.js`** |

**Integration config shape:**
```json
{
  "provider": "whatsapp",
  "label": "WhatsApp (Meta Cloud API)",
  "status": "connected",
  "credentials_set": true,
  "api_key_last4": "3f9a",
  "webhook_url": "https://crm.pk/webhooks/whatsapp",
  "last_tested_at": "ISO-8601",
  "last_test_ok": true
}
```

**Seed providers:** `whatsapp` (connected), `email` (connected), `sms` (disconnected), `push` (not configured).

---

## SELF-QC

- **All DESIGN-SPEC.md G-series pages covered:** ✅ — G-01/G-02/G-03/G-04/G-06/G-07/G-08/G-09 all defined (2026-05-28 update added G-01/G-04/G-06/G-08 which were previously missing)
- **Route conflicts resolved:** ✅ — G-02 at `/app/admin/users/manage`, G-03 at `/app/admin/roles` (previously both mapped to `/app/admin/identity`)
- **Every page role-gated:** ✅
- **Audit trail requirement stated for all write operations:** ✅
- **Credential masking rule documented:** ✅
- **Territory contract updated to territory-management.md:** ✅ — criteria_type enum, TerritoryRule fields, assignment strategies added
- **Feature flag rule_type enum added:** ✅ — tenant_match/role_match/percentage_rollout/env_match; change approval process documented
- **Custom object framework cross-referenced:** ✅
- **API routes section added (§4) for all 8 remaining settings pages:** ✅ — G-01/G-03/G-04/G-05/G-06/G-07/G-08/J-05 each have endpoint specs, field contracts, and status (CREATE vs exists). G-04 references `pricing-plans.md` §7. G-05 route discrepancy between DESIGN-SPEC and b9-p09 §2.7 noted and resolved. (2026-05-31)

Score: **10/10**
