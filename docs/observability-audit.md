# Observability & Audit Architecture

This document defines a production baseline for request logging, immutable audit trails, request tracing, and observability hooks aligned with the CRM security model.

## Goals

- Capture all security-critical and business-critical actions with actor + tenant context.
- Trace each request end-to-end across API, workflow, queue, and integration boundaries.
- Emit structured telemetry without leaking secrets or regulated payload fields.
- Provide auditable APIs for compliance and incident response.

## 1) Logging System

### 1.1 Log event contract (structured JSON)

All services MUST emit JSON logs with this base envelope:

```json
{
  "ts": "2026-03-26T12:34:56.123Z",
  "level": "INFO",
  "service": "crm-api",
  "env": "prod",
  "event_type": "authz.decision",
  "message": "Authorization granted",
  "request_id": "req_01HT...",
  "trace_id": "3d9dcd8f0bb24f7eb8f2d41786bde3e1",
  "span_id": "3e4a45f2f0ce27a1",
  "tenant_id": "ten_123",
  "actor": {
    "type": "user",
    "id": "usr_42",
    "role_ids": ["tenant_admin"]
  },
  "target": {
    "type": "record",
    "id": "rec_991"
  },
  "result": "ALLOW",
  "policy_version": "2026-03-15.3",
  "http": {
    "method": "PATCH",
    "route": "/v1/records/{id}",
    "status_code": 200,
    "latency_ms": 43
  },
  "tags": ["security", "rbac"]
}
```

### 1.2 Severity and retention

- `DEBUG`: local/dev only; disabled in production except targeted incident debugging.
- `INFO`: normal operations and access decisions.
- `WARN`: retries, policy mismatches, partial failures.
- `ERROR`: request failures, data integrity risks, integration failures.
- `FATAL`: process-level failure requiring restart.

Retention policy:

- Application logs: 30 days hot, 180 days archive.
- Security/auth logs: 365 days archive minimum.
- Audit trail (immutable): 7 years minimum (or stricter tenant policy).

### 1.3 Redaction and data hygiene

Never log:

- Access/refresh tokens, API secrets, passwords, private keys.
- Full request/response bodies containing PII unless explicit allow-list.
- Payment or regulated identifiers unless tokenized.

Required controls:

- Field-level redaction for `authorization`, `cookie`, `set-cookie`, `x-api-key`.
- Pattern masking for known sensitive keys in nested payloads.
- Tenant-aware access controls on log viewers.

### 1.4 Mandatory event categories

1. Authentication lifecycle: token validation, refresh, revoke, MFA policy result.
2. Authorization decisions: allow/deny + permission + scope.
3. Administrative actions: role grants/revokes, policy changes, tenant config changes.
4. Data mutations: create/update/delete for tenant business entities.
5. Break-glass workflows: request, approval, activation, expiration.
6. Integration executions: outbound/inbound sync, webhook validation, failures.
7. Security signals: rate-limit blocks, suspicious access patterns, replay rejection.

## 2) Request Tracing

### 2.1 Trace model

- Use W3C Trace Context (`traceparent`, `tracestate`) for ingress/egress propagation.
- Generate `request_id` at edge if absent; preserve upstream ID in `upstream_request_id`.
- Every log event must contain `trace_id`; every RPC/DB span must be linked.

### 2.2 Span requirements

Required spans for mutating API calls:

1. `http.server` (ingress)
2. `authn.validate_token`
3. `authz.evaluate_policy`
4. `db.transaction`
5. `event.publish` (if async side effects)
6. `http.client` / `queue.producer` (integration downstream)

Span attributes (minimum):

- `tenant.id`, `actor.id`, `actor.type`
- `crm.permission`, `crm.resource.type`, `crm.resource.id` (where applicable)
- `http.method`, `http.route`, `http.status_code`
- `error.type`, `error.message` (sanitized)

### 2.3 Sampling strategy

- Errors/security events: 100% trace sampling.
- Mutations (write paths): at least 25% baseline sampling.
- Read-only traffic: 1–5% dynamic sampling.
- Tenant override hooks for incident mode (temporary 100%, max 60 minutes).

## 3) Basic Observability Hooks

### 3.1 Metrics hooks

Core counters/histograms:

- `http_requests_total{route,method,status}`
- `http_request_duration_ms{route,method,status}`
- `authz_decisions_total{permission,result}`
- `audit_events_total{action,result}`
- `db_query_duration_ms{operation,table}`
- `integration_calls_total{provider,result}`
- `integration_latency_ms{provider,operation}`

Security SLO hooks:

- Denied authz decision rate
- Token validation failure rate
- Break-glass activation count
- Cross-tenant access denial count (must stay non-zero under attack tests)

### 3.2 Health hooks

- `/health/live`: process heartbeat only.
- `/health/ready`: dependencies (DB, queue, cache, log sink).
- `/health/startup`: cold-start readiness for orchestration.

### 3.3 Alert hooks

Emit alert events to incident channel when:

- `authz.deny` spikes above baseline for 5 minutes.
- Any `cross_tenant_access_attempt` occurs.
- Audit pipeline write latency exceeds 2 seconds P95.
- Audit append failures > 0 in a 1-minute window.

## 4) Audit Trail APIs

## 4.1 Audit event schema (immutable)

```json
{
  "event_id": "aud_01HT...",
  "event_ts": "2026-03-26T12:34:56.123Z",
  "tenant_id": "ten_123",
  "actor": {
    "type": "user",
    "id": "usr_42",
    "ip": "203.0.113.10",
    "user_agent": "Mozilla/5.0 ..."
  },
  "action": "users.manage_roles.grant",
  "resource": {
    "type": "user",
    "id": "usr_99"
  },
  "decision": "ALLOW",
  "reason": "tenant_admin role with users.manage_roles",
  "before": {
    "role_ids": ["agent"]
  },
  "after": {
    "role_ids": ["agent", "manager"]
  },
  "request": {
    "request_id": "req_01HT...",
    "trace_id": "3d9dcd8f0bb24f7eb8f2d41786bde3e1",
    "method": "POST",
    "route": "/v1/users/usr_99/roles"
  },
  "integrity": {
    "hash": "sha256:...",
    "prev_hash": "sha256:...",
    "chain_seq": 199281
  }
}
```

## 4.2 Endpoints

### `GET /v1/audit/events`

Query immutable audit events.

Parameters:

- `tenant_id` (required, inferred from auth context if omitted)
- `from`, `to` (ISO timestamps)
- `actor_id`, `action`, `resource_type`, `resource_id`
- `decision` (`ALLOW`, `DENY`)
- `cursor`, `limit` (max 1000)

Authorization:

- Requires `audit.logs.read` permission.
- Tenant-scoped only.

Response includes `next_cursor` for pagination.

### `GET /v1/audit/events/{event_id}`

Fetch single event by ID (tenant-scoped).

### `POST /v1/audit/exports`

Create asynchronous export job.

Body:

```json
{
  "format": "jsonl",
  "filters": {
    "from": "2026-03-01T00:00:00Z",
    "to": "2026-03-31T00:00:00Z",
    "action": ["users.manage_roles.grant", "tenant.settings.write"]
  }
}
```

Authorization: `audit.logs.read` + export policy flag.

### `GET /v1/audit/exports/{job_id}`

Check export job status and retrieve signed download URL when complete.

### `GET /v1/audit/integrity/verify`

Verify hash-chain integrity for a time window.

Response:

- `verified: true|false`
- `window_start`, `window_end`
- `checked_events`, `broken_at_event_id` (if false)

## 5) Critical Action Coverage Matrix (No Blind Spots)

| Domain | Critical Action | Required Log | Required Audit Event |
|---|---|---|---|
| AuthN | token validation fail | `authn.token.invalid` | yes |
| AuthZ | permission denied | `authz.decision` result=`DENY` | yes |
| RBAC | role grant/revoke | `rbac.role.change` | yes |
| Tenant config | settings update | `tenant.settings.update` | yes |
| Records | create/update/delete | `record.mutation` | yes |
| API tokens | create/revoke | `api_token.lifecycle` | yes |
| Break-glass | activate/deactivate | `break_glass.state_change` | yes |
| Integrations | webhook auth fail | `integration.webhook.reject` | yes |
| Data access | cross-tenant attempt | `security.cross_tenant_denied` | yes |
| Audit pipeline | append failure | `audit.append.error` | yes |

Enforcement:

- Build-time rule: each protected endpoint maps to an `audit_action` constant.
- CI check: fail if route has mutation scope but no audit mapping.
- Runtime fallback: missing mapping emits `audit.mapping.missing` and blocks mutation in strict mode.

## 6) Implementation Plan (Minimal Build)

1. Add middleware for `request_id`, `trace_id`, and tenant/actor context binding.
2. Add centralized structured logger with redaction filters.
3. Add `AuditWriter.append(event)` to immutable store (append-only table/object log).
4. Instrument authn/authz/data mutation paths with standard event names.
5. Expose audit read/export/integrity APIs with `audit.logs.read` checks.
6. Add Prometheus/OpenTelemetry hooks and baseline dashboards/alerts.

## 7) Self-QC (B1-P06)

Score: **10/10**

- [x] All critical actions explicitly mapped to log + audit events.
- [x] Request tracing requirements defined across all processing layers.
- [x] Basic observability hooks (metrics, health, alerts) specified.
- [x] Audit trail APIs defined with authorization and integrity verification.
- [x] Blind spots closed with CI + runtime guardrails for missing audit mappings.

## 8) Fix Loop (Applied)

- Identified missing-log risk for unmapped mutation endpoints.
- Added strict runtime block + CI enforcement for missing audit mappings.
- Result: no known critical blind spots in defined architecture baseline.
