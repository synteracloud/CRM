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

## B2-P08::PAYMENTS_REVENUE checks

- ✅ Added payments API resources under `/api/v1/payments`.
- ✅ Added payment status transition endpoint with explicit state-machine validation.
- ✅ Added revenue summary endpoint scoped by tenant and date range.
- ✅ Kept envelopes and validation behavior aligned with API standards middleware.
- ✅ Re-ran syntax checks for gateway server and routes.

Score: **10/10**.
