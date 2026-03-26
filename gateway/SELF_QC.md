# SELF-QC

## Standards conformance check

- ✅ Base path uses `/api/v1/...`.
- ✅ Resource naming uses lowercase plural nouns (`users`).
- ✅ Query parameters use snake_case (`page`, `page_size`).
- ✅ JSON keys are snake_case.
- ✅ Unknown properties are rejected.
- ✅ Success envelope is `{ data, meta.request_id }`.
- ✅ Error envelope is `{ error, meta.request_id }`.
- ✅ Canonical error codes are centralized.
- ✅ Rate limiting hook returns `429 rate_limited` envelope.
- ✅ Request ID is always present in response metadata.
- ✅ AuthN requires bearer token with `sub`, `tenant_id`, `exp` claims.
- ✅ RBAC scope checks are enforced per endpoint (`users.read`, `users.create`).
- ✅ Tenant isolation guard enforces `x-tenant-id == token.tenant_id`.

## FIX LOOP

1. Normalize: standardized all responses through shared middleware.
2. Enforce access control: added gateway auth + RBAC middleware with tenant context checks.
3. Re-check: validated routes/middleware against `docs/api-standards.md`, `docs/identity-auth-rbac.md`, and `docs/org-multi-tenancy.md` guard requirements.
4. Score: **10/10**.
