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
| Token format | Signed JWT access tokens | Tokens include `sub`, `tenant_id`, `role_ids`, `scopes`, `iat`, `exp`, `jti`. |
| Token lifetime | Short-lived access + rotating refresh | Access tokens <= 15 minutes; refresh tokens revocable and rotation enforced. |
| Session security | Central revocation + inactivity limits | Sessions can be revoked instantly on role change, compromise, or tenant admin action. |
| Auth context binding | Tenant + audience binding | Token must contain a single authoritative `tenant_id` and valid audience for target API. |

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


## Observability & Audit Implementation Baseline

Operational requirements for logging, request tracing, audit trail APIs, and observability hooks are defined in `docs/observability-audit.md`.

## Security Invariants (Must Always Hold)

| Invariant | Assertion |
|---|---|
| Invariant 1 | A principal can only access resources where `principal.tenant_id == resource.tenant_id`, unless break-glass controls are explicitly active. |
| Invariant 2 | Authorization is evaluated for every request and every resource, never inferred from previous calls. |
| Invariant 3 | No role may grant implied global access to tenant data. |
| Invariant 4 | Privilege escalation paths (self-role edits, token scope inflation, insecure defaults) are blocked and audited. |
| Invariant 5 | Revoked users/tokens lose access immediately for all protected APIs. |
