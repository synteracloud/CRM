<!-- OWNERSHIP
PRIMARY FOR: Threat model categorisation; break-glass access procedure; security boundary definitions; session revocation flow.
DEFERS TO: identity-auth-rbac.md (JWT claims, token TTL, deny-by-default operational detail); data-architecture.md (tenant isolation implementation).
DO NOT RE-DEFINE: JWT claims list → identity-auth-rbac.md §3.2; token TTL table → identity-auth-rbac.md §2.6; tenant isolation table → data-architecture.md §1.3.
-->

# Security Model

This document defines the authentication model, RBAC roles, permissions, tenant isolation rules, and API security controls for the CRM platform.

## Security Principles

| Principle | Requirement | Enforcement |
|---|---|---|
| No privilege leaks | Users, services, and tokens must never gain permissions outside their assigned scope. | Default-deny authorization, explicit allow-lists, server-side policy checks on every request. |
| Strict tenant isolation | Data and operations from one tenant must be inaccessible to all other tenants. | Tenant-scoped identities, tenant-bound tokens, tenant filters in all queries, and cross-tenant access hard-blocked. |
| Least privilege | Every principal receives only minimum required permissions. | Role templates with minimal grants, scoped API tokens, periodic access reviews. |
| Defense in depth | Security controls must exist at multiple layers. | IdP authn, app-layer authz, DB row filtering, audit logging, and anomaly monitoring. |

## Auth Model

| Area | Model | Rules |
|---|---|---|
| Identity provider | OIDC/OAuth 2.1 compatible IdP | All user authentication delegated to trusted IdP; no local passwords in app DB. |
| User authentication | Authorization Code + PKCE | Required for browser and mobile clients; MFA enforced by tenant policy. |
| Service authentication | Client credentials / workload identity | Non-human services use short-lived tokens and secretless identity where possible. |
| Token format | Signed JWT access tokens | Tokens include `sub`, `tenant_id`, `role_ids`, `territory_ids`, `scopes`, `iat`, `exp`, `jti`. Full claims list: `identity-auth-rbac.md §3.2`. |
| Token lifetime | Short-lived access + rotating refresh | Access tokens <= 15 minutes; refresh tokens revocable and rotation enforced. |
| Session security | Central revocation + inactivity limits | Sessions can be revoked instantly on role change, compromise, or tenant admin action. |
| Auth context binding | Tenant + audience binding | Token must contain a single authoritative `tenant_id` and valid audience for target API. |

### Token Lifetime Specifics

> Canonical token TTL table and rotation policy: `identity-auth-rbac.md §2.6` (SessionToken entity) and `§3.1` (login sequence). Summary: Access JWT ≤15 min; Refresh token 7 days rotated on every use; Service credential 1 hour. Revocation on: logout, role change, suspension, admin action, or suspicious activity.

## RBAC Roles

| Role | Purpose | Allowed Scope |
|---|---|---|
| Tenant Owner | Full tenant administration and governance. | Entire tenant only; never platform/global scope. |
| Tenant Admin | Manage users, roles, configs, and tenant operations. | Entire tenant only. |
| Manager | Team-level operational management. | Assigned teams/business units within tenant. |
| Agent | Day-to-day CRM interaction with customer records. | Assigned records/accounts within tenant. |
| Analyst | Reporting and analytics with read-heavy access. | Authorized datasets within tenant. |
| Auditor | Compliance read-only access and audit trails. | Read-only, tenant-wide visibility. |
| Integration Service | API-based machine-to-machine workflow execution. | Explicit API scopes for one tenant. |
| Platform Security Ops | Security operations for platform runtime. | Metadata and security telemetry only; no tenant business data by default. |

## Permissions Matrix

| Permission | Tenant Owner | Tenant Admin | Manager | Agent | Analyst | Auditor | Integration Service |
|---|---:|---:|---:|---:|---:|---:|---:|
| `tenant.settings.read` | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| `tenant.settings.write` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `users.read` | ✅ | ✅ | ✅ (team) | ❌ | ❌ | ✅ | ❌ |
| `users.manage_roles` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `records.read` | ✅ | ✅ | ✅ (team) | ✅ (assigned) | ✅ | ✅ | ✅ (scoped) |
| `records.create` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ (scoped) |
| `records.update` | ✅ | ✅ | ✅ (team) | ✅ (assigned) | ❌ | ❌ | ✅ (scoped) |
| `records.delete` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `reports.read` | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| `audit.logs.read` | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| `api.tokens.manage` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

### Permission Evaluation Rules

| Rule | Description |
|---|---|
| Default deny | Any action without explicit permission is denied. |
| Scope check required | Permission grant is valid only if object scope matches principal scope (tenant, team, record assignment). |
| Most restrictive wins | When multiple roles/scopes apply, deny overrides allow if conflict exists. |
| Server-side enforcement | UI checks are non-authoritative; APIs must enforce authorization independently. |
| Policy versioning | Policy changes are versioned and auditable to detect/rollback unsafe grants. |

## Tenant Isolation Rules

| Control | Rule | Leak Prevention Mechanism |
|---|---|---|
| Tenant identity | Every principal must carry immutable `tenant_id`. | Reject requests missing tenant context or with mismatched tenant claim/path/header. |
| Data partitioning | All tenant business data is keyed and filtered by `tenant_id`. | Enforced query predicates, row-level security, and repository guards. |
| Cross-tenant access | Disallowed by default and requires explicit platform break-glass workflow. | Hard authorization deny + dual approval + time-boxed access + full audit trail. |
| Cache isolation | Cache keys must include `tenant_id` and permission context. | Prevent stale cross-tenant data reuse. |
| Queue/event isolation | Events include tenant context and route through tenant-aware consumers. | Consumer validates tenant context before processing or persistence. |
| Search indexing | Search indices segmented by tenant or include mandatory tenant filter. | Query-time tenant filter cannot be bypassed by user input. |
| File/object storage | Object paths and encryption context bound to tenant. | Bucket/object ACL policy denies cross-tenant reads/writes. |
| Observability data | Logs/metrics/traces with tenant labels and access controls. | Ops tooling enforces tenant-scoped visibility for non-platform users. |

## Break-Glass Access Workflow

Break-glass grants a platform operator temporary cross-tenant read access for incident response. This is the ONLY permitted mechanism for cross-tenant access.

### Approval requirements
- Requester: Platform Security Ops role only.
- Approvers: Two independent Tenant Owner/Admin approvals OR one emergency override by Platform Security Lead with immediate post-hoc review.
- Approval channel: Dedicated break-glass request queue (audited, immutable).

### Access parameters
- TTL: 4 hours maximum. Auto-revoked at expiry — no extension without new approval.
- Scope: Read-only access to specified tenant and resource type. Write access never granted.
- Isolation: Break-glass session is isolated — no cross-contamination of tenant data.

### Activation sequence
1. Platform Security Ops submits request with: target `tenant_id`, resource scope, incident ticket reference, justification.
2. Two approvers confirm in break-glass queue. System generates time-boxed scoped token.
3. Access granted. `break_glass.state_change` audit event emitted (see `docs/infrastructure/observability-audit.md §1.4`).
4. At TTL expiry, token automatically invalidated. `break_glass.state_change` (deactivate) emitted.
5. Post-incident review required within 24 hours.

### Revocation on failure
If auto-revocation fails (token store unavailable), the session falls to deny-by-default — the token cannot be refreshed and expires on next validation attempt.

## API Security

| Area | Standard | Requirement |
|---|---|---|
| Transport security | TLS 1.2+ (prefer TLS 1.3) | HTTPS required end-to-end; HSTS enabled for public endpoints. |
| AuthN/AuthZ | Bearer JWT + RBAC/ABAC checks | Validate signature, issuer, audience, expiry, tenant, scopes, and role permissions on every call. |
| Input security | Strict validation + schema enforcement | Validate payloads, reject unknown/unsafe fields, and sanitize outputs to prevent injection. |
| Rate limiting | Per-tenant and per-principal quotas | Protect against abuse and noisy-neighbor effects while preserving tenant fairness. |
| Idempotency | Idempotency keys for mutating endpoints | Prevent replay duplicates and race-condition side effects. |
| Secret handling | No secrets in code or logs | Use KMS/secret manager, rotate credentials, and redact sensitive values in telemetry. |
| CORS/CSRF | Restricted origins and anti-CSRF tokens | Only trusted origins allowed; state-changing browser calls require CSRF protection. |
| Error handling | Safe error responses | Never expose stack traces, policy internals, or cross-tenant object identifiers. |
| Auditability | Immutable security events | Log authn/authz decisions, admin actions, token events, and policy changes with actor + tenant context. |


### Rate Limiting Thresholds

| Scope | Limit | Window | Action on breach |
|---|---|---|---|
| Per-tenant (all endpoints) | 10,000 requests | 1 minute | `429 Too Many Requests` + `Retry-After` header |
| Per-principal (authenticated user) | 500 requests | 1 minute | `429 Too Many Requests` + `Retry-After` header |
| Auth endpoints (`/api/v1/auth/*`) | 20 requests | 1 minute per IP | `429` + 30-second lockout |
| Webhook ingest endpoints | 1,000 requests | 1 minute per tenant | `429` — provider expected to back off |
| Bulk/export endpoints | 10 requests | 1 hour per tenant | `429` |

Enforcement layer: API Gateway middleware. Per-tenant quotas use a sliding window counter keyed by `tenant_id`. Per-principal quotas keyed by `(tenant_id, user_id)`. Rate limit state stored in Redis.

### Cache Permission Context Definition

The "permission context" included in cache keys is a deterministic hash of the principal's effective permission set:

```
permission_context = SHA-256(sorted(principal.permissions).join(","))
```

This hash changes whenever roles or permissions change. Cache invalidation on permission change is triggered by consuming `identity.user.role.assigned.v1` events — all cache keys matching `tenant:{tenant_id}:*:{user_id}:*` are evicted.

## Observability & Audit Implementation Baseline

Operational requirements for logging, request tracing, audit trail APIs, and observability hooks are defined in `docs/infrastructure/observability-audit.md`.

## Security Invariants (Must Always Hold)

| Invariant | Assertion |
|---|---|
| Invariant 1 | A principal can only access resources where `principal.tenant_id == resource.tenant_id`, unless break-glass controls are explicitly active. |
| Invariant 2 | Authorization is evaluated for every request and every resource, never inferred from previous calls. |
| Invariant 3 | No role may grant implied global access to tenant data. |
| Invariant 4 | Privilege escalation paths (self-role edits, token scope inflation, insecure defaults) are blocked and audited. |
| Invariant 5 | Revoked users/tokens lose access immediately for all protected APIs. |

## Session Revocation Implementation

Revocation is enforced via a distributed revocation store (Redis):

1. On logout/role-change/suspend: `jti` written to revocation store with TTL = remaining token lifetime.
2. On every request: middleware calls `is_revoked(jti)` before processing.
3. Revocation store TTL matches token expiry — entries auto-expire, no unbounded growth.
4. Cache miss (revocation store unavailable): fail-closed — deny request until store is available.
5. SLA: revocation propagation < 100ms (Redis RTT).

Cache key format: `revoked:{tenant_id}:{jti}`. Value: `1`. TTL: remaining seconds until `exp`.
