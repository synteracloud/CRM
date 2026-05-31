<!-- OWNERSHIP
PRIMARY FOR: Partner entity schema and tier rules; opportunity attribution to partner; commission calculation logic; deal registration flow; partner-facing activity log.
DEFERS TO: opportunities-pipeline.md (Opportunity entity and stage definitions); domain-model.md (Contact base fields); event-catalog.md (canonical event names); activities-tasks.md (ActivityEvent logging); identity-auth-rbac.md (partner_manager role definition).
DO NOT RE-DEFINE: Opportunity stage enum → opportunities-pipeline.md; Contact base fields → domain-model.md; JWT claims → identity-auth-rbac.md.
-->

# Partners Domain Spec

## Purpose

This document is the canonical backend spec for the **Partner Management Service** — the domain that tracks channel partners, attributes sales opportunities to partners, calculates commissions, and manages deal registrations. Pakistan CRM supports a channel-partner model where resellers and referral partners drive a portion of the pipeline.

**Build gates:** This doc must exist before any of the following pages can be implemented: B-11 `partners.html`, C-11 `partners-detail.html`.

---

## 1) Core Principles

### 1.1 Partner Contract
- A **Partner** is a business entity (not an end-user) that refers or co-sells opportunities.
- Partners are not CRM users — they do not log into the system. They are represented by a `Partner` record and a `primary_contact_id` (FK → Contact) who is the human point of contact.
- **Attribution** is the core value: every Opportunity can have at most one `attributed_partner_id`. Attribution is set explicitly by a `manager` or `admin` — it is never automatic.
- **Commission** is calculated on `Opportunity.amount` at the point of `is_won = true`, using the partner's tier rate table.
- Tenant isolation: all partner records are scoped to `tenant_id`.

### 1.2 Partner Tiers (Pakistan context)
Three tiers reflect the standard Pakistan reseller channel structure:

| Tier | Label | Commission rate | Deal registration required | Min attributed opps/quarter |
|---|---|---|---|---|
| `platinum` | Platinum | 15% of opportunity amount | Yes — within 30 days | 10 |
| `gold` | Gold | 10% of opportunity amount | Yes — within 45 days | 5 |
| `silver` | Silver | 5% of opportunity amount | No | 1 |

Tier upgrades are manual (admin action). Tier is reviewed quarterly.

### 1.3 Non-negotiable Invariants
1. An Opportunity can have at most one `attributed_partner_id`.
2. Commission is computed only on `is_won = true` — no partial commissions on open deals.
3. A commission record is immutable once `status = paid` — it cannot be edited or deleted.
4. `Partner.status = inactive` blocks new deal registrations and attribution.
5. Tenant isolation enforced: agents can only view partners within their own tenant.

---

## 2) Entity Model

### 2.1 Partner

```
Partner
├── partner_id           : UUID (PK)
├── tenant_id            : str (FK → Tenant, required)
├── name                 : str (company name, max 255)
├── partner_tier         : PartnerTier enum (platinum | gold | silver)
├── status               : PartnerStatus enum (active | inactive | suspended)
├── region               : str (e.g. "Punjab", "Sindh", "KPK", "Balochistan", "AJK")
├── city                 : str
├── primary_contact_id   : UUID (FK → Contact, nullable — the human PoC)
├── contact_name         : str (denorm — for display without join)
├── contact_phone        : str (denorm)
├── contact_email        : str (nullable, denorm)
├── account_manager_id   : UUID (FK → User — the internal user managing this partner)
├── attributed_opp_count : int (running total, read-only, updated on attribution events)
├── total_commission_earned : decimal(18,2) (cumulative paid commissions, PKR)
├── commission_due       : decimal(18,2) (unpaid commissions, PKR — sum of pending commission records)
├── deal_registration_count : int (running total)
├── notes                : str (optional internal notes, max 2,000)
├── tier_review_due_at   : date (nullable — date of next tier review)
├── created_by           : UUID (FK → User)
├── created_at           : datetime
└── updated_at           : datetime
```

### 2.2 DealRegistration

```
DealRegistration
├── registration_id      : UUID (PK)
├── partner_id           : UUID (FK → Partner, required)
├── tenant_id            : str (required)
├── opportunity_id       : UUID (FK → Opportunity, nullable — null until CRM team creates the opp)
├── prospect_name        : str (company/person name the partner is pursuing)
├── prospect_phone       : str (nullable)
├── prospect_email       : str (nullable)
├── estimated_value      : decimal(18,2) (PKR, partner's estimate)
├── expected_close_date  : date (nullable)
├── status               : DealRegStatus enum (submitted | approved | rejected | linked | expired)
├── submitted_at         : datetime
├── reviewed_at          : datetime (nullable)
├── reviewed_by          : UUID (FK → User, nullable)
├── rejection_reason     : str (nullable)
├── expiry_date          : date (30 days from submitted_at for Platinum; 45 days for Gold)
├── notes                : str (optional)
├── created_at           : datetime
└── updated_at           : datetime
```

**Constraints:**
- A deal registration is `approved` when the CRM team confirms the prospect is not already in the pipeline.
- An `approved` registration becomes `linked` when an Opportunity is created and `attributed_partner_id` is set.
- An `expired` registration cannot be re-submitted for the same prospect for 90 days.

### 2.3 PartnerCommission

```
PartnerCommission
├── commission_id        : UUID (PK)
├── partner_id           : UUID (FK → Partner, required)
├── tenant_id            : str (required)
├── opportunity_id       : UUID (FK → Opportunity, required)
├── opportunity_name     : str (denorm)
├── amount               : decimal(18,2) (PKR — opportunity amount * tier rate)
├── rate                 : decimal(5,4) (e.g. 0.15 for 15%)
├── status               : CommissionStatus enum (pending | approved | paid | disputed | cancelled)
├── calculated_at        : datetime (when opportunity was won)
├── approved_at          : datetime (nullable)
├── approved_by          : UUID (FK → User, nullable)
├── paid_at              : datetime (nullable)
├── payment_reference    : str (nullable — bank/payment transfer reference)
├── dispute_reason       : str (nullable)
├── created_at           : datetime
└── updated_at           : datetime
```

**Constraint:** Commission records with `status = paid` are immutable.

### 2.4 PartnerActivityLog

```
PartnerActivityLog
├── log_id               : UUID (PK)
├── partner_id           : UUID (FK → Partner)
├── tenant_id            : str (required)
├── event_type           : PartnerEvent enum (deal_registered | deal_approved | deal_rejected | opp_attributed | opp_won | commission_calculated | commission_paid | tier_changed | status_changed)
├── description          : str (max 1,000)
├── actor_id             : UUID (FK → User, nullable — null if system-triggered)
├── entity_id            : UUID (nullable — the related Opportunity or DealRegistration)
├── created_at           : datetime
```

---

## 3) State Machines

### 3.1 PartnerStatus Enum

| State | Meaning | Allowed transitions |
|---|---|---|
| `active` | Partner in good standing. Can register deals, receive attribution. | → `inactive` (voluntary or tier lapse), → `suspended` (admin action) |
| `inactive` | Not currently active. No new registrations or attribution. | → `active` (reactivated by admin) |
| `suspended` | Blocked due to compliance or dispute. | → `active` (admin lifts suspension), → `inactive` |

### 3.2 DealRegStatus Enum

| State | Meaning | Allowed transitions |
|---|---|---|
| `submitted` | Partner submitted. Awaiting CRM team review. | → `approved`, → `rejected` |
| `approved` | CRM confirmed prospect not in pipeline. Protection window active. | → `linked` (opp created + attributed), → `expired` (window passes) |
| `rejected` | Duplicate or invalid submission. | Terminal. |
| `linked` | Opportunity created and attribution set. | Terminal — commission tracking begins. |
| `expired` | Protection window passed without an opportunity being created. | Terminal. |

### 3.3 CommissionStatus Enum

| State | Meaning | Allowed transitions |
|---|---|---|
| `pending` | Auto-calculated when opp is won. Awaiting admin approval. | → `approved`, → `disputed`, → `cancelled` |
| `approved` | Ready for payment. | → `paid` |
| `paid` | Payment confirmed. Immutable. | Terminal. |
| `disputed` | Partner disputes calculation. | → `approved` (resolved), → `cancelled` |
| `cancelled` | Commission voided (deal reversal, fraud). | Terminal. |

---

## 4) Commission Calculation

### 4.1 Calculation Trigger
- When `Opportunity.is_won` transitions to `true` and `Opportunity.attributed_partner_id` is set:
  1. Look up `Partner.partner_tier` → resolve commission rate from tier table (§1.2).
  2. Create `PartnerCommission` record: `amount = opportunity.amount * rate`, `status = pending`.
  3. Increment `Partner.commission_due` by the commission amount.
  4. Emit `partner.commission_calculated` event.

### 4.2 Recalculation on Amount Change
- If `Opportunity.amount` is updated after a pending commission exists:
  - Recalculate commission amount.
  - Update `PartnerCommission.amount` (only if `status = pending` — never update approved/paid commissions).

### 4.3 Payment Recording
- `POST /api/v1/partners/{id}/commissions/{commission_id}/pay` with `payment_reference`.
- Sets `status = paid`, `paid_at = now()`.
- Decrements `Partner.commission_due` by the paid amount.
- Increments `Partner.total_commission_earned` by the paid amount.

---

## 5) API Endpoints

### Partners Resource

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/partners` | JWT | `manager`, `admin` | Create partner. |
| `GET` | `/api/v1/partners` | JWT | Any | List partners (tenant-scoped). |
| `GET` | `/api/v1/partners/{id}` | JWT | Any | Partner detail. |
| `PATCH` | `/api/v1/partners/{id}` | JWT | `manager`, `admin` | Update partner fields. |
| `GET` | `/api/v1/partners/{id}/opportunities` | JWT | Any | Opportunities attributed to this partner. |
| `GET` | `/api/v1/partners/{id}/commissions` | JWT | `manager`, `admin` | Commission ledger for partner. |
| `POST` | `/api/v1/partners/{id}/commissions/{commission_id}/approve` | JWT | `manager`, `admin` | Approve pending commission. |
| `POST` | `/api/v1/partners/{id}/commissions/{commission_id}/pay` | JWT | `admin` | Mark commission as paid with payment reference. |
| `GET` | `/api/v1/partners/{id}/activity` | JWT | `manager`, `admin` | Partner activity log. |

### Deal Registrations Resource

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/partners/{id}/deal-registrations` | JWT | `manager`, `admin` | Submit deal registration on behalf of partner. |
| `GET` | `/api/v1/partners/{id}/deal-registrations` | JWT | Any | List registrations for partner. |
| `POST` | `/api/v1/deal-registrations/{id}/approve` | JWT | `manager`, `admin` | Approve registration. |
| `POST` | `/api/v1/deal-registrations/{id}/reject` | JWT | `manager`, `admin` | Reject with reason. |

### Attribution

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/opportunities/{id}/attribute-partner` | JWT | `manager`, `admin` | Set `attributed_partner_id` on an opportunity. |
| `DELETE` | `/api/v1/opportunities/{id}/attribute-partner` | JWT | `admin` | Remove attribution (resets to null). Cancels any pending commission. |

---

## 6) RBAC Role Gates

| Operation | `sales_rep` | `agent` | `manager` | `admin` |
|---|---|---|---|---|
| View partners | ✓ | ✓ | ✓ | ✓ |
| Create / edit partner | — | — | ✓ | ✓ |
| Submit deal registration | — | — | ✓ | ✓ |
| Approve / reject registration | — | — | ✓ | ✓ |
| View commission ledger | — | — | ✓ | ✓ |
| Approve commission | — | — | ✓ | ✓ |
| Record commission payment | — | — | — | ✓ |
| Attribute opportunity to partner | — | — | ✓ | ✓ |
| Change partner tier / status | — | — | — | ✓ |

---

## 7) Events Emitted

| Event | Trigger |
|---|---|
| `partner.created` | Partner record created. |
| `partner.tier_changed` | Tier upgraded or downgraded. |
| `partner.status_changed` | Status transition (active/inactive/suspended). |
| `partner.deal_registered` | Deal registration submitted. |
| `partner.deal_approved` | Deal registration approved. |
| `partner.deal_rejected` | Deal registration rejected. |
| `partner.opportunity_attributed` | `attributed_partner_id` set on an Opportunity. |
| `partner.commission_calculated` | Commission created on `is_won = true`. |
| `partner.commission_approved` | Commission approved for payment. |
| `partner.commission_paid` | Commission marked as paid. |

---

## 8) Scanner Jobs

### 8.1 Deal Registration Expiry Job
- **Schedule:** Daily at 02:00 PKT.
- **Action:** Query `DealRegistration WHERE status = approved AND expiry_date < today`. Set `status = expired`. Notify partner account manager via WhatsApp.

### 8.2 Tier Review Reminder Job
- **Schedule:** Weekly (Monday 09:00 PKT).
- **Action:** Query `Partner WHERE tier_review_due_at <= today + 7 days AND status = active`. Notify account manager to review and update tier.

---

## 9) Implementation Acceptance Checklist

- [ ] `Partner`, `DealRegistration`, `PartnerCommission`, `PartnerActivityLog` entities created.
- [ ] State machine transitions enforced — invalid transitions return `422`.
- [ ] Commission auto-calculated when `Opportunity.is_won = true` and `attributed_partner_id` is set.
- [ ] Commission rate applied from tier table (platinum=15%, gold=10%, silver=5%).
- [ ] `status = paid` commissions are immutable — PATCH/DELETE returns `409`.
- [ ] `Partner.commission_due` and `total_commission_earned` maintained atomically.
- [ ] Attribution is exclusive: second `attribute-partner` on same opp replaces first; cancels pending commission for displaced partner.
- [ ] Deal registration expiry dates: 30 days (platinum), 45 days (gold), no expiry (silver).
- [ ] All API endpoints respect RBAC role gates (§6).
- [ ] All events in §7 emitted via activity log.
- [ ] Scanner jobs (expiry, tier review) scheduled and testable.
- [ ] Tenant isolation enforced on all list endpoints.
