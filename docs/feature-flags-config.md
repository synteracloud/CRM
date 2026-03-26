# Feature Flags & Configuration Management

This document defines the **Feature Flag Service** and its **configuration APIs** used by all CRM services.

## Goals

- Provide a centralized, audited system to enable/disable behavior safely at runtime.
- Eliminate hardcoded feature branching in application code.
- Support tenant-, role-, environment-, and percentage-based rollouts.
- Provide deterministic flag evaluation for every request.

## Design Principles

1. **No hardcoded logic**: business code must call the flag/config API, not embed static `if env == ...` checks.
2. **Safe-by-default**: all new flags default to `off` and require explicit targeting to enable.
3. **Deterministic evaluations**: the same input context returns the same decision.
4. **Fast reads, durable writes**: write-through persistence with low-latency cached evaluation paths.
5. **Auditable changes**: every flag/config mutation emits an immutable audit event.

## Domain Model

### `feature_flag`

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable identifier (`ff_<ulid>`) |
| `key` | string | Unique key (`kebab-case`) used by services |
| `description` | string | Human-readable intent and blast radius |
| `status` | enum | `active`, `archived` |
| `default_variant` | enum | `off`, `on`, or named variant |
| `rules` | array | Ordered targeting/evaluation rules |
| `owner_team` | string | Owning team for approval/escalation |
| `expires_at` | datetime? | Required for temporary rollout flags |
| `created_at` | datetime | RFC3339 UTC |
| `updated_at` | datetime | RFC3339 UTC |

### `config_entry`

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable identifier (`cfg_<ulid>`) |
| `namespace` | string | Domain namespace (`billing`, `lead_scoring`, etc.) |
| `key` | string | Unique key within namespace |
| `value_type` | enum | `string`, `number`, `boolean`, `json` |
| `value` | any | Value validated against `value_type` |
| `scope` | object | Context scope: env/tenant/role/service |
| `status` | enum | `active`, `deprecated` |
| `version` | integer | Monotonic version for optimistic concurrency |
| `created_at` | datetime | RFC3339 UTC |
| `updated_at` | datetime | RFC3339 UTC |

## Evaluation Algorithm (Safe Toggle)

1. Load the flag by `key` from cache (fallback datastore).
2. If missing, return `default_variant = off` and emit `flag_missing` metric.
3. Evaluate ordered rules against context (`tenant_id`, `user_role`, `env`, `account_id`).
4. For percentage rollout rules, hash `(flag_key + subject_id)` and map to 0–99 bucket.
5. Return first matching rule variant; otherwise return default.
6. Emit decision event (`evaluated`) with non-PII context summary and latency.

## REST API Contracts

All endpoints follow `/api/v1` and the standard API envelope.

### Flag Management APIs

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/feature-flags` | Create a flag definition |
| `GET` | `/api/v1/feature-flags/{flag_id}` | Get a single flag |
| `GET` | `/api/v1/feature-flags` | List flags with filtering |
| `PATCH` | `/api/v1/feature-flags/{flag_id}` | Update metadata or rules |
| `POST` | `/api/v1/feature-flags/{flag_id}:archive` | Archive flag |
| `POST` | `/api/v1/feature-flags/{flag_id}:unarchive` | Restore flag |

### Flag Evaluation APIs

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/feature-flags/evaluate` | Evaluate one flag for a context |
| `POST` | `/api/v1/feature-flags/evaluate-batch` | Evaluate many flags in one request |

**Single evaluation request example**

```json
{
  "flag_key": "new-quote-approval-flow",
  "context": {
    "tenant_id": "ten_01JAWQX9Q6FJ7QQ44Y2W8P2A9M",
    "user_id": "usr_01JAWQXVM3ADY2VPKN2C5QCMHH",
    "user_role": "sales_manager",
    "environment": "prod"
  }
}
```

### Config Management APIs

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/config-entries` | Create a typed config entry |
| `GET` | `/api/v1/config-entries/{config_id}` | Read config entry |
| `GET` | `/api/v1/config-entries` | Query by namespace/key/scope |
| `PATCH` | `/api/v1/config-entries/{config_id}` | Update value with version check |
| `POST` | `/api/v1/config-entries/{config_id}:deprecate` | Mark config entry deprecated |
| `POST` | `/api/v1/config-resolve` | Resolve effective config for runtime context |

**Resolve request example**

```json
{
  "namespace": "lead_scoring",
  "keys": ["max_daily_enrichment_calls", "score_threshold"],
  "scope": {
    "environment": "prod",
    "tenant_id": "ten_01JAWQX9Q6FJ7QQ44Y2W8P2A9M",
    "service": "lead-management-service"
  }
}
```

## Operational Controls

- **Change approval**: production flag or config changes require two-person approval.
- **Kill switch**: every high-risk feature must define a global off-switch flag.
- **TTL policy**: rollout flags must include `expires_at`; expired flags are reported daily.
- **Drift detection**: detect config divergence across environments and alert.
- **SLO**: flag/config read P95 ≤ 20ms, P99 ≤ 50ms.

## Self-QC Checklist

- [x] Flags can toggle safely without deploys.
- [x] Runtime decisions are deterministic and auditable.
- [x] No hardcoded feature logic outside the flag/config service contract.
- [x] APIs exist for both flag lifecycle and typed config management.

## Fix Loop (Quality Gate)

1. **Fix**: correct missing rule validation, type validation, or concurrency gaps.
2. **Re-check**: rerun API contract checks, schema checks, and evaluation determinism checks.
3. **10/10**: release only when all checklist items pass and no hardcoded bypass paths remain.
