# B8-P10::DATA_GOVERNANCE_LAYER

## Scope and Inputs

This governance layer is derived from and constrained by:
- `docs/domain-model.md` (entity ownership and tenant scoping)
- `docs/security-model.md` (RBAC, tenant isolation, and audit invariants)
- `docs/data-architecture.md` (service-owned storage, outbox/events, cache and retention patterns)

All policies below are **system-enforceable controls**, not advisory guidance.

---

## 1) Governance Layer

### 1.1 Governance Planes

| Plane | Purpose | Primary Owners | In-System Enforcement Surfaces |
|---|---|---|---|
| Ownership Governance | Ensure each entity has clear accountable owner and mutation authority | Domain service owners + Tenant Owner/Admin | Service write boundaries, repository guards, RBAC checks |
| Access Governance | Enforce least-privilege + tenant isolation | Identity & Access Service + Security Ops | JWT validation, policy engine, API authorization middleware |
| Lifecycle Governance | Govern retention, archival, deletion, legal hold | Data Governance Admin + Compliance | Retention scheduler, storage tiering jobs, legal hold flags |
| Quality Governance | Maintain data validity/completeness/consistency timeliness | Data Steward + Domain owners | Schema constraints, validation rules, DQ jobs, quarantine queues |
| Sensitive Data Governance | Control PII and high-risk fields over full lifecycle | Security + Privacy + Domain owners | Field classification tags, masking, encryption, purpose checks |
| Change Governance | Trace who changed what, when, and why | Audit & Compliance Service | Immutable `AuditLog`, policy versioning, change reason enforcement |

### 1.2 Governance Roles

| Role | Responsibilities | Required Permissions |
|---|---|---|
| Tenant Owner | Final authority for tenant-level governance defaults and exceptions | `tenant.settings.write`, `users.manage_roles`, `audit.logs.read` |
| Tenant Admin | Operate governance configuration and assign stewards | `tenant.settings.write`, `users.manage_roles`, `audit.logs.read` |
| Data Steward | Owns quality rules, data definitions, and remediation workflows for assigned domains | `records.read`, scoped `records.update`, governance-policy scoped write |
| Compliance Auditor | Read-only oversight of policy adherence and change evidence | `audit.logs.read`, `reports.read` |
| Integration Service | Programmatic data exchange within explicit scope only | `records.read/create/update` (scoped), no policy bypass |
| Platform Security Ops | Security telemetry and break-glass oversight only | Metadata/security scopes; no tenant business data by default |

### 1.3 Governance Objects

| Object | Description | Stored In |
|---|---|---|
| DataClassificationPolicy | Field-level classification (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`) | Governance config schema |
| DataOwnershipRegistry | Maps entity + tenant scope to accountable owner role/service | Governance config schema |
| RetentionPolicy | Entity/event retention windows, archival tier, deletion strategy | Governance config schema |
| DataQualityRuleSet | Declarative validation and score thresholds by entity | Governance config schema |
| SensitiveHandlingPolicy | Access, masking, encryption, logging and transfer controls | Governance config schema |
| ChangeAuditPolicy | Auditable action set + required evidence and reason codes | Governance config schema |

---

## 2) Policies

## 2.1 Data Ownership Rules

1. **Single write-owner per entity**: every domain entity is mutable only by its owner service as defined in domain ownership catalog.
2. **Tenant accountability**: each tenant-scoped entity instance must have `tenant_id` and an accountable business owner (`owner_user_id` where modeled, otherwise steward mapping).
3. **No cross-service direct writes**: non-owner services must publish commands/events, never write into another service DB.
4. **Steward assignment required**: each governed entity type per tenant must have a designated steward group.
5. **Ownership transfer is auditable**: owner/steward reassignment requires actor, reason code, ticket/reference, and immutable audit entry.

## 2.2 Stewardship / Admin Controls

1. **Policy admin segregation**: policy creation/edit requires Tenant Owner/Admin; stewards can propose but not self-approve high-impact changes.
2. **Dual-control for high-impact actions**: retention shortening, bulk delete approvals, sensitive classification downgrades, and break-glass toggles require dual approval.
3. **Scoped stewardship**: stewards operate only within assigned domains (e.g., Lead, Account, Opportunity).
4. **Periodic attestation**: quarterly steward attestation on ownership completeness, quality score, and unresolved violations.
5. **Automated revocation**: steward/admin privilege removal is immediate on role change.

## 2.3 Retention Rules

Retention values below are minimum defaults; stricter tenant regulatory policy may extend them.

| Data Class | Examples | Hot Retention | Archive Retention | Deletion Mode |
|---|---|---:|---:|---|
| Core business records | `Lead`, `Contact`, `Account`, `Opportunity`, `Quote`, `Order`, `Case` | Active lifecycle + 24 months | Up to 84 months | Soft-delete + timed hard-delete |
| Partner financial attribution | `PartnerAttribution`, `PartnerCommission` | 36 months | Up to 120 months | Immutable ledger corrections, no hard-delete before expiry |
| Security and compliance logs | `AuditLog`, authz/authn decisions | 24 months | Up to 120 months | WORM-style immutable archive |
| Session/security tokens metadata | `SessionToken` lifecycle records | 90 days | 12 months | Hard-delete after expiry unless on legal hold |
| High-volume timeline/events | `ActivityEvent`, `Message` metadata | 12 months | 24-60 months | Tiered archive + lifecycle purge |

Additional rules:
- **Legal hold supersedes retention deletion** for in-scope records.
- **Retention is tenant-aware** and executes by `tenant_id` partitions.
- **Deletion jobs are idempotent** and emit auditable `RetentionActionExecuted` events.

## 2.4 Data Quality Rules

Quality dimensions and gates:

| Dimension | Rule Type | Enforcement |
|---|---|---|
| Completeness | Required attributes per lifecycle stage (e.g., Opportunity stage requires `amount`, `close_date`) | Synchronous API validation + batch backfill checks |
| Validity | Type/format/range checks (email, phone, currency, enumerations) | Schema constraints + validation library |
| Consistency | Cross-entity consistency (`tenant_id` match, account/opportunity linkage validity) | Transaction checks within service + async reconciliation |
| Uniqueness | Tenant-scoped duplicates (`tenant_id + email`, partner code uniqueness) | Unique indexes + duplicate detection jobs |
| Timeliness | Freshness SLAs for projections/indexes | Lag monitors and freshness alerts |
| Integrity | Referential integrity in service boundary | FK constraints + orphan detection job |

Scoring policy:
- Each domain computes a daily `dq_score` (0-100).
- `dq_score < 95` creates steward task; `< 90` escalates to Tenant Admin.
- Critical-rule failures block state transitions (e.g., cannot close-won without mandatory billing fields).

## 2.5 Sensitive Data Handling Policy

### Classification
- **RESTRICTED**: direct identifiers, regulated personal/sensitive fields, token/security secrets.
- **CONFIDENTIAL**: customer contact and financial details.
- **INTERNAL**: operational metadata.
- **PUBLIC**: explicitly non-sensitive shareable data.

### Controls
1. **Least-privilege field access**: field-level policy checks for `CONFIDENTIAL`/`RESTRICTED` attributes.
2. **Encryption**: encryption in transit (TLS) and at rest; envelope encryption for restricted datasets.
3. **Masking/redaction**: default mask in UI/logs for restricted values; explicit unmask permission required.
4. **Purpose limitation**: sensitive exports require declared purpose and approval path.
5. **Telemetry hygiene**: sensitive fields prohibited in logs, traces, and error payloads.
6. **Secure data movement**: cross-system exports require approved connector, tenant scoping, and audit.
7. **Break-glass access**: time-boxed, dual-approved, fully audited, auto-revoked.

## 2.6 Change Audit Policy

Auditable actions include:
- RBAC/permission changes
- policy changes (classification, retention, quality, stewardship assignments)
- sensitive-field read/unmask/export
- bulk mutations/deletions
- break-glass grants and use
- retention execution outcomes and legal hold overrides

Required audit envelope:
- `event_id`, `event_time`, `actor_id`, `actor_type`, `tenant_id`, `action`, `resource_type`, `resource_id`, `before_hash`, `after_hash`, `reason_code`, `request_id`, `trace_id`, `policy_version`, `result`.

Audit guarantees:
1. Immutable append-only storage.
2. Time-synchronized ordering (trusted clock source).
3. Queryable by tenant, actor, policy, resource, and time window.
4. Tamper-evidence via hash-chain or signed digest per batch.

---

## 3) Enforcement Hooks

## 3.1 Write-Path Hooks (Synchronous)

1. **API Gateway AuthZ Hook**
   - Validate JWT (`tenant_id`, scopes, roles, expiry, audience).
   - Attach policy context (`policy_version`, principal scopes).
2. **Service Command Guard Hook**
   - Enforce owner-service write authority.
   - Enforce tenant scope equality (`principal.tenant_id == payload.tenant_id`).
3. **Field Classification Hook**
   - Block forbidden writes/reads of `RESTRICTED` fields without explicit permission.
4. **Validation Hook**
   - Apply quality critical rules before commit.
5. **Audit Emit Hook**
   - Emit immutable audit event on all governed mutations.

## 3.2 Data-Layer Hooks

1. **Repository Tenant Predicate Hook**
   - Mandatory `tenant_id` predicate injection for all queries.
2. **DB Constraint Hook**
   - PK/FK/unique/not-null/check constraints for core quality and ownership attributes.
3. **Row-Level Security Hook**
   - Tenant-based RLS policies for all tenant-scoped tables.
4. **Outbox Governance Hook**
   - Governed mutation commits must include outbox event for downstream policy observability.

## 3.3 Async Governance Hooks

1. **DQ Evaluation Job**
   - Scheduled rule execution; writes violations and scorecards.
2. **Retention Executor Job**
   - Partition-aware retention/delete/archive runs with legal-hold checks.
3. **Sensitive Access Monitor**
   - Detect anomalous sensitive reads/exports; trigger alerts.
4. **Policy Drift Detector**
   - Detect mismatch between declared policy and active DB/API enforcement configuration.
5. **Reconciliation Worker**
   - Cross-service consistency checks via event replay and remediation tasks.

## 3.4 Admin and Workflow Hooks

1. **Policy Change Workflow Hook**
   - Draft → review → approve → activate with versioning and audit.
2. **Dual-Approval Hook**
   - Required for high-impact governance operations.
3. **Exception Register Hook**
   - Time-bounded policy exceptions with owner, justification, expiry, and compensating controls.
4. **Attestation Hook**
   - Quarterly stewardship attestations with non-response escalation.

---

## 4) Self-QC and Fix Loop

### QC Checklist

| Check | Status | Evidence |
|---|---|---|
| Ownership explicit | ✅ Pass | Data ownership rules define single write-owner, tenant accountability, and steward assignment |
| Sensitive data controls defined | ✅ Pass | Classification tiers, encryption, masking, purpose, logging, transfer, break-glass controls |
| Governance enforceable in-system | ✅ Pass | Explicit synchronous, data-layer, async, and workflow enforcement hooks |

### Fix Loop Result

- **Iteration 1:** Added explicit ownership + stewardship rules.
- **Iteration 2:** Added enforceable sensitive-data controls and break-glass constraints.
- **Iteration 3:** Added concrete enforcement hooks across API, DB, jobs, and workflow.
- **Iteration 4:** Re-checked against QC checklist.

**Final self-score: 10/10**
