# B2-P04::DATA_GOVERNANCE

## Read Basis

This specification is built from `docs/enterprise-depth.md`, especially the governance lifecycle, non-negotiable invariants, and retention/audit closure points.

---

## Build

## 1) Ownership Rules

### 1.1 Ownership Model
- Every governed record must have:
  - `tenant_id`
  - `data_owner_type` (`service`, `team`, `user`)
  - `data_owner_id`
  - `steward_group_id`
  - `ownership_version`
- Ownership is **single-writer authoritative**: one owner at a time for mutation authority.
- Attribution metadata (partner/channel/assist) is sidecar-only and cannot replace core ownership.

### 1.2 Enforcement
1. **Write authority gate**
   - Reject writes when `caller_owner != data_owner_id` and no approved delegation token exists.
2. **Tenant boundary gate**
   - Reject if `caller.tenant_id != record.tenant_id`.
3. **Ownership transfer workflow**
   - Required fields: `reason_code`, `ticket_ref`, `effective_at`, `approved_by`.
   - Transfer increments `ownership_version` and emits immutable `OwnershipTransferred` event.
4. **No uncontrolled owner nulls**
   - `data_owner_id` and `steward_group_id` are non-null on create and update.

### 1.3 Required Invariants
- No record exists without accountable owner.
- No cross-tenant ownership assignment.
- No direct write by non-owner service.

---

## 2) Retention Rules

### 2.1 Retention Policy Matrix

| Data Domain | Active Retention | Archive Retention | Delete Mode | Legal Hold Behavior |
|---|---:|---:|---|---|
| Core CRM entities (`Lead`, `Account`, `Opportunity`, `Quote`, `Order`, `Case`) | lifecycle + 24 months | up to 84 months | soft-delete then timed hard-delete | deletion blocked while hold active |
| Governance/audit events (`AuditLog`, ownership/retention actions) | 24 months | up to 120 months | immutable archive; no early hard-delete | hold extends archive lock |
| Activity telemetry (`ActivityEvent`, message metadata) | 12 months | 24-60 months | tiered archive + purge | hold blocks purge for scoped subjects |
| Auth/session metadata | 90 days | 12 months | hard-delete post-expiry | hold exception requires compliance approval |

### 2.2 Retention Execution Controls
1. Jobs run by `tenant_id` partition with deterministic cursor checkpoints.
2. Each execution writes `RetentionActionExecuted` with counts and policy version.
3. Deletes are idempotent (re-runs do not duplicate destructive actions).
4. Legal hold check runs before archive/delete action.
5. Retention policy shortening requires dual approval.

### 2.3 Required Invariants
- No data deleted while legal hold active.
- No retention action without audit evidence.
- No orphaned archive object without source lineage metadata.

---

## 3) Quality Rules

### 3.1 Rule Categories

| Dimension | Rule | Gate |
|---|---|---|
| Completeness | Stage-required fields present (e.g., close data before closed-won) | synchronous write validation |
| Validity | Type/range/format constraints (email, currency, enums) | schema + API validation |
| Consistency | Cross-entity tenant and reference consistency | transactional checks + async reconciliation |
| Uniqueness | Tenant-scoped duplicate prevention keys | unique indexes + dedupe worker |
| Timeliness | Projection freshness SLA compliance | lag monitor alerts |
| Integrity | Referential non-orphan guarantees | FK constraints + integrity jobs |

### 3.2 Severity and Actions
- **Critical:** block write/transition immediately.
- **High:** allow write with remediation task due within SLA.
- **Medium/Low:** score penalty and steward queue.

### 3.3 Data Quality Score Policy
- `dq_score` computed daily per `{tenant, domain}`.
- Threshold actions:
  - `< 95`: open steward remediation task.
  - `< 90`: escalate to tenant admin.
  - `< 85`: freeze non-essential bulk imports until recovered.

### 3.4 Required Invariants
- No critical quality violation can progress lifecycle stage.
- No quality rule runs without versioned rule set identifier.
- No unresolved critical violations older than SLA.

---

## 4) No Uncontrolled Data (Hard Guarantee)

Data is classified as **uncontrolled** if any of these are true:
- Missing owner (`data_owner_id` null/invalid).
- Missing tenant scope (`tenant_id` null/invalid).
- Missing retention class/policy binding.
- Missing minimum quality rule binding for its entity type.
- Missing audit envelope for governed mutation.

### 4.1 Control Gates
1. **Ingest gate:** rejects uncontrolled payloads before persistence.
2. **Write gate:** blocks updates that remove governance bindings.
3. **Nightly sweep:** finds historical uncontrolled records and queues mandatory remediation.
4. **Release gate:** deployment fails if governance drift introduces uncontrolled write path.

### 4.2 Remediation SLA
- Critical uncontrolled data: fix within 24h.
- High uncontrolled data: fix within 72h.
- Repeated violations trigger policy hardening review.

---

## 5) QC (Fix → Re-fix → 10/10)

### 5.1 QC Checklist

| QC Item | Result | Evidence |
|---|---|---|
| Ownership built | ✅ Pass | Explicit owner model, transfer workflow, and write authority gates |
| Retention built | ✅ Pass | Matrix + legal hold + idempotent execution + audit evidence |
| Quality rules built | ✅ Pass | Dimension table + severity actions + score thresholds |
| No uncontrolled data | ✅ Pass | Definition + ingest/write/sweep/release control gates |

### 5.2 Fix Loop
1. **Fix:** added ownership, retention, and quality baseline controls.
2. **Re-fix:** added strict invariants, severity handling, and audit-coupled enforcement.
3. **Re-fix:** added uncontrolled-data hard guarantee with multi-gate prevention and remediation SLA.
4. **Final Re-check:** validated against requested scope and enterprise governance constraints.

**Final score: 10/10**
