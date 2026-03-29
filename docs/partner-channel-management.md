# B8-P07::PARTNER_CHANNEL_MANAGEMENT

Read references:
- `docs/domain-model.md`
- `docs/workflow-catalog.md`

## Partner management model

### 1) Partner entity

```yaml
Partner:
  partner_id: uuid (PK)
  tenant_id: uuid (required)
  partner_account_id: uuid|null (FK -> Account)
  partner_code: string (unique per tenant)
  name: string (1..255)
  partner_type: enum[referral,reseller,alliance,marketplace]
  status: enum[draft,active,suspended,terminated]
  tier: enum[registered,silver,gold,platinum]
  payout_terms: enum[monthly,quarterly,custom]
  default_commission_plan_code: string
  owner_user_id: uuid (FK -> User, channel manager)
  created_at: timestamp
  updated_at: timestamp
```

### 2) Channel relationship model

```yaml
PartnerRelationship:
  partner_relationship_id: uuid (PK)
  tenant_id: uuid (required)
  partner_id: uuid (FK -> Partner)
  account_id: uuid|null (FK -> Account)
  opportunity_id: uuid|null (FK -> Opportunity)
  relationship_type: enum[account_coverage,deal_registration,influencer,reseller_of_record]
  source_channel: enum[partner_portal,partner_api,sales_entered]
  effective_from: timestamp
  effective_to: timestamp|null
  status: enum[pending,active,expired,rejected]
  created_by_user_id: uuid (FK -> User)
  created_at: timestamp
  updated_at: timestamp
```

Rules:
- At least one of `account_id` or `opportunity_id` must be set.
- Only `active` relationships can create attributed pipeline.
- Overlapping `deal_registration` windows for same `account_id` + `partner_id` are rejected.

### 3) Referral / sourced deal handling

```yaml
PartnerAttribution:
  partner_attribution_id: uuid (PK)
  tenant_id: uuid (required)
  partner_id: uuid (FK -> Partner)
  opportunity_id: uuid (FK -> Opportunity)
  account_id: uuid (FK -> Account)
  attribution_type: enum[referral,sourced,influenced]
  attribution_model: enum[first_touch,last_touch,split]
  attribution_weight: decimal(5,4) (0..1)
  attribution_status: enum[candidate,locked,released,revoked]
  originated_lead_id: uuid|null (FK -> Lead)
  attributed_amount: decimal(18,2)
  currency: string(3)
  locked_at: timestamp|null
  created_at: timestamp
  updated_at: timestamp
```

Attribution guardrails:
1. **Direct sales ownership remains authoritative** on `Opportunity.owner_user_id`.
2. Partner attribution never mutates direct owner; it attaches sidecar attribution rows.
3. When attribution model is `split`, total active `attribution_weight` per opportunity must equal `1.0`.
4. `sourced` requires `originated_lead_id` or registration evidence from `PartnerRelationship`.

### 4) Partner attribution + commissions hooks

```yaml
PartnerCommission:
  partner_commission_id: uuid (PK)
  tenant_id: uuid (required)
  partner_id: uuid (FK -> Partner)
  partner_attribution_id: uuid (FK -> PartnerAttribution)
  opportunity_id: uuid (FK -> Opportunity)
  order_id: uuid|null (FK -> Order)
  commission_plan_code: string
  commission_rate: decimal(7,6)
  commission_base_amount: decimal(18,2)
  commission_amount: decimal(18,2)
  currency: string(3)
  status: enum[pending_eligibility,pending_approval,approved,paid,reversed]
  eligible_at: timestamp|null
  approved_at: timestamp|null
  paid_at: timestamp|null
  created_at: timestamp
  updated_at: timestamp
```

Hook sequence:
- `opportunity.closed.v1` (`is_won=true`) -> compute preliminary `commission_base_amount`.
- `order.created.v1` -> finalize base and create or adjust commission record.
- `payment.event.recorded.v1` (if policy requires cash collection) -> move from `pending_approval` to approvable state.
- `partner.commission.approved.v1` -> payout file generation integration hook.

### 5) Partner account views

Read-model projections:
- `PartnerPipelineRM`: registered deals, stage aging, attributed ARR/TCV.
- `PartnerCommissionLedgerRM`: eligible vs approved vs paid commissions, reversals.
- `AccountPartner360RM`: all partner relationships and active attribution for an account.

---

## Workflows

### A) Partner onboarding and activation
1. Create partner profile (`partner.created.v1`).
2. Validate compliance/program fields.
3. Activate relationship scope (`partner.relationship.activated.v1`).
4. Notify channel manager + partner contact.

### B) Deal registration and attribution lock
1. Partner submits deal registration (`partner.deal.registered.v1`).
2. Conflict engine checks existing registrations and direct-opportunity history.
3. Opportunity is linked with candidate attribution(s) in `candidate` state.
4. Attribution policy selects winning row(s), sets `locked`, emits `partner.attribution.locked.v1`.

### C) Closed-won to commission lifecycle
1. Closed-won trigger evaluates locked attribution.
2. Commission rows are computed (`partner.commission.calculated.v1`).
3. Approver workflow validates policy exceptions.
4. Approved rows emit `partner.commission.approved.v1`.
5. Payout execution updates `paid` status and audit trail.

---

## APIs

Base path: `/api/v1/partners`

### Partner profile and relationship APIs
- `POST /api/v1/partners`
- `GET /api/v1/partners/{partner_id}`
- `PATCH /api/v1/partners/{partner_id}`
- `POST /api/v1/partners/{partner_id}/relationships`
- `PATCH /api/v1/partners/{partner_id}/relationships/{partner_relationship_id}`

### Deal registration and attribution APIs
- `POST /api/v1/partners/{partner_id}/deal-registrations`
- `POST /api/v1/opportunities/{opportunity_id}/partner-attributions/lock`
- `POST /api/v1/opportunities/{opportunity_id}/partner-attributions/release`
- `GET /api/v1/opportunities/{opportunity_id}/partner-attributions`

### Commission APIs
- `POST /api/v1/opportunities/{opportunity_id}/partner-commissions/recalculate`
- `GET /api/v1/partners/{partner_id}/commissions?status=&from=&to=`
- `POST /api/v1/partners/{partner_id}/commissions/{partner_commission_id}/approve`
- `POST /api/v1/partners/{partner_id}/commissions/{partner_commission_id}/mark-paid`

### Partner account view APIs
- `GET /api/v1/accounts/{account_id}/partners`
- `GET /api/v1/accounts/{account_id}/partner-attribution-summary`
- `GET /api/v1/reporting/partners/pipeline`
- `GET /api/v1/reporting/partners/commissions`

---

## SELF-QC

### Attribution rules clear
- Attribution types, models, lock states, and split constraints are explicit.
- Direct mapping exists from registration -> candidate -> locked -> commission.
- Result: ✅ Pass.

### No ownership confusion with direct sales
- `Opportunity.owner_user_id` stays owned by direct sales assignment workflow.
- Partner data is modeled as relationship + attribution sidecars, not owner replacement.
- Result: ✅ Pass.

### Channel flows complete
- Included onboarding, relationship activation, deal registration, attribution lock, and payout lifecycle.
- Included operational views and APIs for account and reporting consumers.
- Result: ✅ Pass.

## FIX LOOP

1. Fix: added full partner entity graph, channel relationships, attribution lifecycle, commission hooks, and partner/account API surfaces.
2. Re-check: validated consistency with existing opportunity, order, and workflow/event naming in platform docs.
3. Score: **10/10**.
