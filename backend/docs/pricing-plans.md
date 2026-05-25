# Pricing Plans Spec

## Purpose

This document defines the pricing plan tier definitions, PKR price benchmarks, feature entitlements per plan, upgrade/downgrade flow, plan-gated feature enforcement in the API, trial period model, and metering model. PRODUCT-SPEC.md §2/§12 states "early value before monetization; visible ROI; revenue features first" — this doc makes that concrete as an implementation contract.

**Important distinction:** `adoption-ux.md` defines UX progressive disclosure tiers (Tier 1–4 by usage maturity). This document defines **billing plan tiers** — these are different concepts. Feature flags (feature-flags-config.md) implement the technical toggle; this document defines which plan unlocks which flag.

---

## 1) Plan Tier Definitions

### 1.1 Tier Structure

| Plan | Internal code | PKR price / month | Target | Contract |
|---|---|---|---|---|
| **Starter** | `plan_starter` | Rs 1,999 | 1–5 users, first-time CRM | Monthly only |
| **Growth** | `plan_growth` | Rs 5,999 | 5–20 users, SMB active sales team | Monthly or annual (15% discount) |
| **Business** | `plan_business` | Rs 14,999 | 20+ users, multi-branch, enterprise-lite | Monthly or annual (20% discount) |
| **Enterprise** | `plan_enterprise` | Custom (quote) | Large orgs, full white-glove | Annual only |

**Annual prices:**
- Growth annual: Rs 61,189 (Rs 5,099/month equivalent — 15% off)
- Business annual: Rs 143,990 (Rs 11,999/month equivalent — 20% off)

**PKR benchmark alignment (PRODUCT-SPEC.md §3/§5):**
- Starter: Rs 1,500–4,500 benchmark → priced at Rs 1,999 (low-end capture)
- Growth: Rs 5,000–12,000 benchmark → priced at Rs 5,999 (mid-market anchor)
- Business: Rs 15,000+ benchmark → priced at Rs 14,999 (approachable enterprise)

### 1.2 User Seat Model

- **Starter:** Maximum 5 users (hard cap; attempt to add 6th returns `402 Payment Required` with upgrade prompt).
- **Growth:** Maximum 20 users (hard cap; same enforcement).
- **Business:** Unlimited users.
- **Enterprise:** Unlimited users + custom SLA.

---

## 2) Feature Entitlements Per Plan

### 2.1 Feature Matrix

| Feature | Starter | Growth | Business | Enterprise |
|---|---|---|---|---|
| WhatsApp lead capture | ✓ | ✓ | ✓ | ✓ |
| Follow-up enforcement (basic) | ✓ | ✓ | ✓ | ✓ |
| Contact management | ✓ | ✓ | ✓ | ✓ |
| Basic pipeline (1 pipeline) | ✓ | ✓ | ✓ | ✓ |
| Owner dashboard | ✓ | ✓ | ✓ | ✓ |
| Invoice creation + manual payment | ✓ | ✓ | ✓ | ✓ |
| JazzCash / Easypaisa payment callbacks | — | ✓ | ✓ | ✓ |
| Collections automation | — | ✓ | ✓ | ✓ |
| Multiple pipelines (up to 5) | — | ✓ | ✓ | ✓ |
| Shared inbox (multi-agent) | — | ✓ | ✓ | ✓ |
| Cases / Support Tickets | — | ✓ | ✓ | ✓ |
| Offline sync | — | ✓ | ✓ | ✓ |
| Custom reporting | — | — | ✓ | ✓ |
| Territory management | — | — | ✓ | ✓ |
| CPQ / Quote Builder | — | — | ✓ | ✓ |
| Workflow automation | — | — | ✓ | ✓ |
| Employee performance analytics | — | — | ✓ | ✓ |
| AI Copilot | — | — | ✓ | ✓ |
| API access (REST) | — | — | ✓ | ✓ |
| Custom objects / fields | — | — | — | ✓ |
| Dedicated onboarding manager | — | — | — | ✓ |
| Custom SLA / uptime guarantee | — | — | — | ✓ |
| Data residency options | — | — | — | ✓ |

### 2.2 Feature Flag Mapping

Each feature in the entitlement matrix maps to a `FeatureFlag.flag_key`. The plan entitlement service sets the flag `enabled = true` for the appropriate plans.

| Feature | Flag key |
|---|---|
| JazzCash/Easypaisa callbacks | `payment_provider_callbacks` |
| Collections automation | `collections_automation` |
| Multiple pipelines | `multi_pipeline` |
| Shared inbox | `shared_inbox` |
| Cases / Support | `case_management` |
| Offline sync | `offline_sync` |
| Custom reporting | `custom_reporting` |
| Territory management | `territory_management` |
| CPQ / Quote Builder | `cpq_quote_builder` |
| Workflow automation | `workflow_automation` |
| Employee performance | `employee_performance_analytics` |
| AI Copilot | `ai_copilot` |
| REST API access | `api_access` |
| Custom objects | `custom_objects` |

---

## 3) Plan Enforcement in the API

### 3.1 Enforcement Layer

Plan enforcement happens via the `EntitlementGuard` — a FastAPI dependency that is added to any endpoint gated by a plan feature:

```python
# Example
@router.post("/api/v1/cases")
async def create_case(
    ...,
    _: None = Depends(require_feature("case_management"))
):
    ...
```

`require_feature(flag_key)` resolves the current tenant's plan, checks whether the flag is entitled, and raises `402 Payment Required` if not. The `402` response body uses the standard error envelope:

```json
{
  "error": {
    "code": "PLAN_FEATURE_NOT_ENTITLED",
    "message": "This feature requires the Growth plan or higher.",
    "details": [
      {
        "feature": "case_management",
        "required_plan": "plan_growth",
        "current_plan": "plan_starter",
        "upgrade_url": "/settings/billing"
      }
    ]
  },
  "meta": { "request_id": "..." }
}
```

### 3.2 User Seat Cap Enforcement

On `POST /api/v1/users` (invite user):
- Query `COUNT(User WHERE tenant_id=tenant AND is_active=true)`.
- If count >= plan seat limit: return `402` with `SEAT_LIMIT_REACHED` code.

### 3.3 Read vs Write Enforcement

- **Read operations** on gated features: return data if it exists (downgrades don't delete data; they only prevent new creation). The UI handles the upgrade prompt display separately.
- **Write operations** on gated features: blocked by `EntitlementGuard`.

---

## 4) Trial Period Model

### 4.1 Trial Structure

- Every new tenant starts on a **14-day free trial** of the **Growth plan**.
- Trial gives full Growth plan entitlements for 14 days.
- No credit card required to start a trial.
- After 14 days without conversion: tenant is automatically downgraded to **Starter plan** (not suspended).

**Why Starter and not suspended:** PRODUCT-SPEC.md §2/§12 — "early value before monetization." Forcing suspension on trial end causes abandonment. Downgrading to Starter keeps the user in the product with core value intact.

### 4.2 Trial State Entity

```
TenantEntitlement (additions)
├── plan_code            : str (plan_starter | plan_growth | plan_business | plan_enterprise)
├── trial_started_at     : datetime (nullable — null if no trial)
├── trial_ends_at        : datetime (nullable)
├── is_trial             : bool
├── billing_cycle        : str (monthly | annual)
├── current_period_start : date
├── current_period_end   : date
├── subscription_status  : EntitlementStatus enum (trialing | active | past_due | canceled | suspended)
└── seat_limit           : int (null = unlimited)
```

### 4.3 Trial-to-Paid Conversion

```
trial_ends_at approaching:
  T-7 days: in-app banner + email "7 days left on trial"
  T-3 days: in-app banner + WhatsApp notification to tenant admin
  T-1 day: in-app full-screen prompt (not blocking — dismissible)
  T+0:      auto-downgrade to Starter plan
             emit tenant.trial_expired event
             tenant.subscription_status → "active" (on Starter)
```

On payment method addition + plan selection:
1. Tenant selects plan and billing cycle.
2. System creates/updates `TenantEntitlement` with chosen plan.
3. Sets `is_trial = false`, `trial_ends_at = null`.
4. First invoice generated.
5. Emit `tenant.plan_activated` event.

---

## 5) Upgrade and Downgrade Flow

### 5.1 Upgrade Rules
- Effective: **immediately** on payment confirmation.
- Proration: charge difference between current plan and new plan, prorated to remaining days in current billing period.
- All new feature flags enabled immediately after `TenantEntitlement` update.
- No data migration needed on upgrade — features work with existing data.

### 5.2 Downgrade Rules
- Effective: **end of current billing period** (not immediate).
- During the period between downgrade request and effective date: tenant retains current plan features.
- On effective date: `plan_code` updated; `EntitlementGuard` enforces new limits.
- **Data handling on downgrade:** Existing data is retained. Only new creation is blocked by `EntitlementGuard`. Example: a Business tenant with 3 pipelines who downgrades to Starter retains all 3 pipelines in read-only mode; they cannot create new pipelines until they upgrade.
- **User seat handling:** If tenant has more active users than the new plan allows, no users are deactivated. A warning banner is shown to admin: "You have X users on a plan that allows Y. Please deactivate Z users by [date] or upgrade." After 14 days without resolution: oldest-created excess users are automatically deactivated (not deleted).

### 5.3 Suspension

Tenant suspension (payment failure after 14-day grace) is handled by the billing provider (Stripe integration) outside this system. On suspension:
- `subscription_status → suspended`
- All API endpoints return `402` with `ACCOUNT_SUSPENDED` code.
- Data is retained for 90 days before final deletion.

---

## 6) Metering Model

**v1:** Flat-rate per plan. No usage-based metering in v1.

**Future (Phase 6 scope):**
- WhatsApp message volume metering (per template message sent above plan limit).
- Storage metering (attachment storage above plan limit).
- These are tracked but not billed in v1. Meter counters are stored in `TenantUsageMetric` for Phase 6 implementation.

---

## 7) API Endpoints

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/billing/plans` | Public | None | List available plans with pricing and features. |
| `GET` | `/api/v1/billing/subscription` | JWT | `admin` | Current tenant's subscription status and entitlements. |
| `POST` | `/api/v1/billing/subscription/upgrade` | JWT | `admin` | Request plan upgrade. |
| `POST` | `/api/v1/billing/subscription/downgrade` | JWT | `admin` | Schedule plan downgrade for end of period. |
| `GET` | `/api/v1/billing/entitlements` | JWT | Any | Returns list of enabled feature flags for current tenant's plan. |

---

## 8) Implementation Acceptance Checklist

- [ ] `TenantEntitlement` extended with `plan_code`, `trial_started_at`, `trial_ends_at`, `is_trial`, `billing_cycle`, `subscription_status`, `seat_limit`.
- [ ] 3 plan tiers implemented (Starter/Growth/Business) with PKR prices.
- [ ] Feature flag mappings table implemented in entitlement service.
- [ ] `EntitlementGuard` FastAPI dependency created; `require_feature()` helper.
- [ ] `402 PLAN_FEATURE_NOT_ENTITLED` response with upgrade URL in error details.
- [ ] `402 SEAT_LIMIT_REACHED` on user invite when at limit.
- [ ] 14-day Growth trial auto-provisioned on tenant creation.
- [ ] Auto-downgrade to Starter on trial expiry (not suspension).
- [ ] Trial expiry notifications at T-7, T-3, T-1, T+0.
- [ ] Upgrade: immediate with proration calculation.
- [ ] Downgrade: deferred to end of billing period; data retained in read-only mode.
- [ ] `billing/plans` endpoint public (no auth required — needed for marketing page).
- [ ] `billing/entitlements` endpoint returns current tenant's enabled flag list.
