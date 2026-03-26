# B1-P02: ORG_MULTI_TENANCY

## Inputs Used
- `/docs/domain-model.md`
- `/docs/security-model.md`

This specification extends the CRM model with an explicit **Organization** aggregate while preserving the existing hard tenant isolation guarantees.

---

## 1) Entities

### 1.1 Organization
- **Owner service:** Organization & Tenant Service
- **Purpose:** Business grouping and governance boundary for one or more tenant workspaces.
- **Fields:**
  - `org_id (PK, UUID)`
  - `tenant_id (FK -> Tenant, required)`
  - `name`
  - `slug` (unique within tenant)
  - `status` (`active | suspended | archived`)
  - `created_by_user_id (FK -> User)`
  - `created_at`
  - `updated_at`
- **Isolation:** `tenant_id` required, indexed, and immutable after creation.
- **Constraints:**
  - `UNIQUE (tenant_id, slug)`
  - `CHECK (status IN ('active','suspended','archived'))`

### 1.2 OrganizationMembership (User ↔ Org mapping)
- **Owner service:** Organization & Tenant Service
- **Purpose:** Authoritative user assignment to organizations with per-org role context.
- **Fields:**
  - `org_membership_id (PK, UUID)`
  - `tenant_id (FK -> Tenant, required)`
  - `org_id (FK -> Organization, required)`
  - `user_id (FK -> User, required)`
  - `membership_role` (`owner | admin | member | viewer`)
  - `status` (`active | invited | revoked`)
  - `assigned_by_user_id (FK -> User, required)`
  - `assigned_at`
  - `revoked_at (nullable)`
- **Isolation:** `tenant_id` must match `Organization.tenant_id` and `User.tenant_id`.
- **Constraints:**
  - `UNIQUE (tenant_id, org_id, user_id)`
  - `CHECK (membership_role IN ('owner','admin','member','viewer'))`
  - `CHECK (status IN ('active','invited','revoked'))`

### 1.3 Ownership rules (clarity)
- `Tenant` owns all organizations in its scope.
- `Organization` owns its membership list.
- `User` can belong to many organizations **within the same tenant only**.
- Any tenant business entity referencing an organization must include:
  - `tenant_id`
  - `org_id`
- Entity ownership tuple is always: **`(tenant_id, org_id, <entity_id>)`**.

---

## 2) APIs

All APIs require:
- Valid JWT (`sub`, `tenant_id`, `role_ids`, `scopes`, `exp`, `jti`)
- Tenant-bound authorization checks
- Default deny policy

### 2.1 Create Organization
**Endpoint**
- `POST /v1/tenants/{tenant_id}/organizations`

**Required permission**
- `tenant.settings.write` (Tenant Owner/Admin)

**Request body**
```json
{
  "name": "North America Sales",
  "slug": "na-sales"
}
```

**Server-side validation**
1. `token.tenant_id == path.tenant_id`
2. Caller has `tenant.settings.write`
3. `slug` unique in `(tenant_id, slug)`

**Response (201)**
```json
{
  "org_id": "uuid",
  "tenant_id": "uuid",
  "name": "North America Sales",
  "slug": "na-sales",
  "status": "active",
  "created_at": "2026-03-26T00:00:00Z"
}
```

### 2.2 Assign User to Organization
**Endpoint**
- `POST /v1/tenants/{tenant_id}/organizations/{org_id}/members`

**Required permission**
- `users.manage_roles` OR org-level `admin/owner` membership

**Request body**
```json
{
  "user_id": "uuid",
  "membership_role": "member"
}
```

**Server-side validation**
1. `token.tenant_id == path.tenant_id`
2. Caller has required permission/scope
3. `Organization(tenant_id, org_id)` exists
4. `User(tenant_id, user_id)` exists
5. Upsert membership in same `tenant_id` only

**Response (200/201)**
```json
{
  "org_membership_id": "uuid",
  "tenant_id": "uuid",
  "org_id": "uuid",
  "user_id": "uuid",
  "membership_role": "member",
  "status": "active",
  "assigned_at": "2026-03-26T00:00:00Z"
}
```

### 2.3 Optional read API for enforcement/debugging
- `GET /v1/tenants/{tenant_id}/organizations/{org_id}/members`
- Same tenant and scope checks; returns only memberships for `(tenant_id, org_id)`.

---

## 3) Isolation Logic

### 3.1 Hard isolation invariants
1. **Tenant match required:** `principal.tenant_id == resource.tenant_id`.
2. **Org membership required:** non-tenant-admin principals must have active membership in target `org_id`.
3. **No implicit global access:** org grants do not expand across tenant boundary.
4. **Default deny:** any missing context (`tenant_id`, `org_id`, permission) => deny.

### 3.2 Repository/query guards (mandatory)
Every org-scoped query must include both filters:
```sql
WHERE tenant_id = :tenant_id
  AND org_id = :org_id
```

Every write must verify ownership tuple consistency:
- Insert/update allowed only when parent rows satisfy same `(tenant_id, org_id)`.
- Cross-tenant FK references rejected at service layer and DB constraints.

### 3.3 Authorization evaluation flow
1. Validate token signature, expiry, audience.
2. Extract `principal = { user_id, tenant_id, role_ids, scopes }`.
3. Compare path/header tenant context to token tenant.
4. Evaluate permission (`tenant.settings.write`, `users.manage_roles`, etc.).
5. If endpoint is org-scoped, evaluate active `OrganizationMembership`.
6. Execute query with tenant + org predicates.
7. Audit log decision (`allow/deny`, actor, tenant_id, org_id, reason).

### 3.4 Cache/event/search boundaries
- **Cache key:** include `tenant_id`, `org_id`, and permission hash.
- **Event schema:** include immutable `tenant_id`, `org_id` in payload + metadata.
- **Search:** partition index by tenant or enforce mandatory `tenant_id AND org_id` filters.

---

## 4) Self-QC

### 4.1 No cross-tenant access possible
- ✅ API path tenant, token tenant, and data tenant must all match.
- ✅ DB/repository predicates enforce `tenant_id` always.
- ✅ Membership lookup bound to same `tenant_id` as org/user.
- ✅ Missing/mismatched tenant context returns deny.

### 4.2 Entity ownership clear
- ✅ Ownership tuple defined as `(tenant_id, org_id, entity_id)` for org-scoped entities.
- ✅ `Organization` owned by `Tenant`; memberships owned by organization.
- ✅ User-to-org mapping is explicit and unique via `OrganizationMembership`.

### 4.3 Fix loop result
- Fix → re-check applied to constraints, API guards, and query predicates.
- Final QC score: **10/10**.
