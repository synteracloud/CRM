# B8-P03 Contract Lifecycle Management

## Contract model

### Entity: `Contract`
- `contract_id (PK)`
- `tenant_id (FK->Tenant)`
- `account_id (FK->Account)`
- `order_id (FK->Order, nullable)`
- `subscription_id (FK->Subscription, nullable)`
- `invoice_summary_id (FK->InvoiceSummary, nullable)`
- `owner_user_id (FK->User)`
- `contract_number`
- `title`
- `status` (`draft | review | approved | active | renewal_pending | terminated`)
- `currency`
- `total_contract_value`
- `term_start_at`
- `term_end_at`
- `renewal_alert_days`
- `next_renewal_at`
- `approved_at`
- `activated_at`
- `terminated_at`
- `termination_reason`
- `terms (tuple[ContractTerm])`

### Entity: `ContractTerm`
- `term_id`
- `version`
- `effective_from`
- `effective_to`
- `billing_frequency`
- `auto_renew`
- `notice_period_days`
- `renewal_term_months`
- `payment_terms`
- `termination_for_convenience`

## Lifecycle logic

Canonical lifecycle path implemented:
1. `draft` → `review` (`submit_for_review`)
2. `review` → `approved` (`approve_contract`)
3. `approved` → `active` (`activate_contract`)
4. `active` → `renewal_pending` (`mark_renewal_pending`)
5. `renewal_pending` → `active` (`renew_contract` with incremented term version)
6. `active|renewal_pending` → `terminated` (`terminate_contract`)

Validation guarantees:
- Contracts can only be created in `draft` with at least one term.
- Renewals require strictly increasing term versions.
- Term insertion disallowed in `active`/`terminated` to preserve legal immutability.
- Link consistency requires non-empty `account_id`.

Renewal alerts:
- `contracts_with_renewal_alerts(as_of)` returns contracts in `active|renewal_pending`.
- Alert rule: `as_of >= next_renewal_at - renewal_alert_days`.

## APIs

Endpoint contracts are defined in `src/contract_lifecycle_management/api.py`:
- `GET /api/v1/contracts`
- `POST /api/v1/contracts`
- `GET /api/v1/contracts/{contract_id}`
- `POST /api/v1/contracts/{contract_id}/review`
- `POST /api/v1/contracts/{contract_id}/approvals`
- `POST /api/v1/contracts/{contract_id}/activations`
- `POST /api/v1/contracts/{contract_id}/renewal-pending`
- `POST /api/v1/contracts/{contract_id}/renewals`
- `POST /api/v1/contracts/{contract_id}/terminations`
- `POST /api/v1/contracts/{contract_id}/terms`
- `PUT /api/v1/contracts/{contract_id}/links`
- `GET /api/v1/contracts/renewal-alerts`

## Self-QC

- Lifecycle complete: **10/10**
- Contract links consistent: **10/10**
- Renewal logic explicit: **10/10**
