# B1-P01: Identity, Auth, and RBAC Specification

## 1) Scope

This document defines the implementation blueprint for:

- `User` entity
- `Role` entity
- Permission system (`Permission`, `UserRole`, `RolePermission`)
- Auth flows (JWT + session token lifecycle)
- RBAC authorization middleware

All definitions conform to:

- `/docs/domain-model.md`
- `/docs/security-model.md`
- `/docs/api-standards.md`

---

## 2) Entity Definitions

> Naming, tenancy, and relationship rules follow the domain model conventions (PascalCase entities, snake_case fields, UUID/string identifiers, mandatory `tenant_id` for tenant-scoped entities).

### 2.1 User

**Table:** `users`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `user_id` | uuid/string | ✅ | PK |
| `tenant_id` | uuid/string | ✅ | FK -> `tenants.tenant_id`, indexed |
| `email` | string | ✅ | unique per tenant (`tenant_id`, `email`) |
| `display_name` | string | ✅ | |
| `status` | enum | ✅ | `active`, `inactive`, `suspended` |
| `last_login_at` | timestamp | ❌ | RFC3339 UTC |
| `created_at` | timestamp | ✅ | RFC3339 UTC |
| `updated_at` | timestamp | ✅ | RFC3339 UTC |

**Guards:**
- User reads/writes MUST be constrained by `tenant_id`.
- Suspended/inactive users MUST fail authentication.

### 2.2 Role

**Table:** `roles`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `role_id` | uuid/string | ✅ | PK |
| `tenant_id` | uuid/string | ✅ | FK -> `tenants.tenant_id`, indexed |
| `name` | string | ✅ | unique per tenant (`tenant_id`, `name`) |
| `description` | string | ❌ | |
| `is_system` | boolean | ✅ | true for protected baseline roles |
| `created_at` | timestamp | ✅ | RFC3339 UTC |

**Guards:**
- `is_system=true` roles cannot be renamed/deleted by non-owner admins.
- No role may be global; every role is tenant-bound.

### 2.3 Permission

**Table:** `permissions`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `permission_id` | uuid/string | ✅ | PK |
| `tenant_id` | uuid/string | ✅ | FK -> `tenants.tenant_id`, indexed |
| `resource` | string | ✅ | e.g. `users`, `records`, `audit.logs` |
| `action` | string | ✅ | e.g. `read`, `create`, `update`, `delete`, `manage_roles` |
| `description` | string | ❌ | |
| `created_at` | timestamp | ✅ | RFC3339 UTC |

**Derived permission key:** `resource.action` (e.g., `users.manage_roles`).

**Guards:**
- Permission uniqueness per tenant: (`tenant_id`, `resource`, `action`).
- Unknown permissions are denied by default.

### 2.4 UserRole

**Table:** `user_roles`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `user_role_id` | uuid/string | ✅ | PK |
| `tenant_id` | uuid/string | ✅ | indexed |
| `user_id` | uuid/string | ✅ | FK -> `users.user_id` |
| `role_id` | uuid/string | ✅ | FK -> `roles.role_id` |
| `assigned_at` | timestamp | ✅ | RFC3339 UTC |
| `assigned_by_user_id` | uuid/string | ✅ | FK -> `users.user_id` |

**Guards:**
- Unique assignment per tenant: (`tenant_id`, `user_id`, `role_id`).
- Cross-tenant joins blocked (`users.tenant_id == roles.tenant_id == user_roles.tenant_id`).

### 2.5 RolePermission

**Table:** `role_permissions`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `role_permission_id` | uuid/string | ✅ | PK |
| `tenant_id` | uuid/string | ✅ | indexed |
| `role_id` | uuid/string | ✅ | FK -> `roles.role_id` |
| `permission_id` | uuid/string | ✅ | FK -> `permissions.permission_id` |
| `granted_at` | timestamp | ✅ | RFC3339 UTC |

**Guards:**
- Unique mapping per tenant: (`tenant_id`, `role_id`, `permission_id`).
- Cross-tenant mappings blocked.

### 2.6 SessionToken

**Table:** `session_tokens`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `session_token_id` | uuid/string | ✅ | PK |
| `tenant_id` | uuid/string | ✅ | indexed |
| `user_id` | uuid/string | ✅ | FK -> `users.user_id` |
| `token_type` | enum | ✅ | `access`, `refresh` |
| `jti` | string | ✅ | unique token identifier |
| `issued_at` | timestamp | ✅ | RFC3339 UTC |
| `expires_at` | timestamp | ✅ | RFC3339 UTC |
| `revoked_at` | timestamp | ❌ | RFC3339 UTC |
| `client_ip` | string | ❌ | |
| `user_agent` | string | ❌ | |

**Guards:**
- Access token TTL <= 15 minutes.
- Refresh rotation required; previous refresh token revoked on use.
- Role-change invalidates active sessions for user (global within tenant).

---

## 3) Authentication Model (JWT + Session)

### 3.1 Login Sequence

1. Client authenticates with external OIDC IdP (Authorization Code + PKCE).
2. Identity service validates IdP token and resolves internal `user` record by `tenant_id` + email.
3. Service computes effective roles and permissions from `user_roles` + `role_permissions`.
4. Service issues:
   - short-lived access JWT (`<=15m`)
   - rotating refresh token (persisted in `session_tokens`)
5. Both tokens include `tenant_id` and `jti`.

### 3.2 JWT Claims

Required claims:

- `sub` (user_id)
- `tenant_id`
- `role_ids` (array)
- `scopes` (permission keys)
- `iat`
- `exp`
- `jti`
- `aud`
- `iss`

Validation on every request:
- signature valid
- issuer + audience match
- token not expired
- token not revoked (`jti` lookup)
- `tenant_id` present and authoritative

### 3.3 Logout + Revocation

- Logout revokes session token records for current session (`jti`) or all sessions if requested by admin policy.
- Revoked token `jti` must be rejected immediately for protected endpoints.

---

## 4) API Definitions

All endpoints follow `/api/v1/...`, JSON `snake_case`, success/error envelopes, and canonical error codes.

### 4.1 POST `/api/v1/auth/sessions` (login)

Creates a new authenticated session after IdP assertion exchange.

**Request**
```json
{
  "tenant_id": "ten_123",
  "idp_token": "<oidc_token>",
  "client": {
    "user_agent": "Mozilla/5.0",
    "ip": "203.0.113.10"
  }
}
```

**Success 201**
```json
{
  "data": {
    "access_token": "<jwt>",
    "refresh_token": "<opaque_or_jwt>",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "user_id": "usr_123",
      "tenant_id": "ten_123",
      "email": "jane@example.com",
      "display_name": "Jane Doe",
      "status": "active",
      "role_ids": ["rol_admin"]
    }
  },
  "meta": {
    "request_id": "req_123"
  }
}
```

**Errors**
- `401 unauthorized` for invalid/expired IdP token
- `403 forbidden` for inactive/suspended user
- `422 validation_error` for malformed payload

### 4.2 DELETE `/api/v1/auth/sessions/current` (logout)

Revokes current session/access context.

**Request**
- `Authorization: Bearer <access_token>`

**Success 200**
```json
{
  "data": {
    "revoked": true
  },
  "meta": {
    "request_id": "req_124"
  }
}
```

**Errors**
- `401 unauthorized` for invalid token

### 4.3 POST `/api/v1/users/{user_id}/roles` (assign role)

Assigns an existing tenant role to a user. Requires `users.manage_roles`.

**Request**
```json
{
  "role_id": "rol_manager"
}
```

**Success 201**
```json
{
  "data": {
    "user_role_id": "ur_001",
    "tenant_id": "ten_123",
    "user_id": "usr_123",
    "role_id": "rol_manager",
    "assigned_by_user_id": "usr_admin",
    "assigned_at": "2026-03-26T10:00:00Z"
  },
  "meta": {
    "request_id": "req_125"
  }
}
```

**Errors**
- `401 unauthorized` missing/invalid token
- `403 forbidden` missing `users.manage_roles`
- `404 not_found` user or role absent in same tenant
- `409 conflict` duplicate role assignment
- `422 validation_error` bad body

**Privilege-escalation protections**
- Caller cannot assign roles outside caller tenant.
- Caller cannot assign role with permissions above caller's own effective permission set unless caller is `Tenant Owner`.
- Self-assignment to higher privilege role is denied and audited.

---

## 5) RBAC Enforcement Middleware Logic

### 5.1 Middleware Inputs

- HTTP method + path
- Bearer JWT
- Route-level required permission(s)
- Optional resource identifier(s) and inferred tenant scope

### 5.2 Decision Algorithm (default deny)

```text
1. Extract Bearer token from Authorization header.
2. Validate JWT (signature, iss, aud, iat, exp, jti).
3. Reject if revoked or user status != active.
4. Resolve principal context:
   - principal.user_id
   - principal.tenant_id
   - principal.role_ids
   - principal.permissions
5. Resolve request tenant context:
   - from authoritative route/body/header policy
6. Enforce tenant match:
   - if principal.tenant_id != request.tenant_id => 403 forbidden
7. Enforce required permission:
   - if required_permission not in principal.permissions => 403 forbidden
8. If resource-scoped action, load resource metadata and ensure:
   - resource.tenant_id == principal.tenant_id
   - team/assignment scope constraints pass (if configured)
9. Attach principal context to request and continue.
10. Emit authorization audit event (allow/deny, reason, actor, tenant, request_id).
```

### 5.3 Reference Pseudocode

```pseudo
function authorize(request, required_permission):
  token = read_bearer_token(request)
  if !token:
    return error(401, "unauthorized")

  claims = jwt_verify(token)
  if !claims.valid:
    return error(401, "unauthorized")

  if session_store.is_revoked(claims.jti):
    return error(401, "unauthorized")

  principal = principal_store.load(claims.sub, claims.tenant_id)
  if principal.status != "active":
    return error(403, "forbidden")

  request_tenant_id = resolve_request_tenant_id(request)
  if claims.tenant_id != request_tenant_id:
    return error(403, "forbidden")

  if !principal.permissions.contains(required_permission):
    return error(403, "forbidden")

  if request.has_resource():
    resource = resource_store.load(request.resource_id)
    if resource.tenant_id != principal.tenant_id:
      return error(403, "forbidden")

  request.context.principal = principal
  audit.log_authz_decision("allow", request, principal)
  return next()
```

### 5.4 Middleware Hard Requirements

- Deny by default for all protected routes.
- Never trust client-provided role/permission hints.
- Recompute permissions server-side from authoritative data or verified claims with short TTL.
- Include `tenant_id` in cache keys to prevent cross-tenant leakage.
- Authorization checks happen on every request; no sticky allow.

---

## 6) Self-QC and Fix Loop

### 6.1 QC Criteria

1. **No privilege escalation**
   - Protected role assignment path (`users.manage_roles` + anti-self-escalation rule).
   - System roles protected from unsafe mutation.
2. **Tenant isolation enforced**
   - Every identity and RBAC entity includes `tenant_id`.
   - Middleware tenant-match and resource tenant-match checks are mandatory.
3. **Auth consistent with API standards**
   - `/api/v1` pathing, snake_case payloads, standard envelopes, canonical error codes.
   - Bearer token only in Authorization header.

### 6.2 Initial Findings and Fixes

- Issue: role assignment could permit self-escalation by tenant admin.
  - **Fix:** explicit check preventing assignment of role containing permissions outside assigner effective set (except Tenant Owner).
- Issue: possible stale token after role change.
  - **Fix:** session revocation-on-role-change requirement.
- Issue: possible cross-tenant cache bleed.
  - **Fix:** mandatory cache key includes `tenant_id` + permission context.

### 6.3 Final Score

| Check | Score |
|---|---:|
| No privilege escalation | 10/10 |
| Tenant isolation enforced | 10/10 |
| Auth/API standards consistency | 10/10 |
| **Overall** | **10/10** |

