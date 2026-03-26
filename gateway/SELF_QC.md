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
- ✅ Quote entity fields include all canonical domain fields (`quote_id`, `tenant_id`, `opportunity_id`, `status`, `currency`, `subtotal`, `discount_total`, `tax_total`, `grand_total`, `valid_until`, `created_at`, `accepted_at`).
- ✅ Order entity is defined for quote conversion (`order_id`, `tenant_id`, `quote_id`, `opportunity_id`, `status`, `currency`, totals, `ordered_at`, `created_at`).
- ✅ Basic pricing logic computes line-level net and aggregate totals.
- ✅ Conversion flow is complete: create quote → accept quote → convert to order.
- ✅ Conversion rejects non-accepted quotes with `409 conflict`.

## FIX LOOP

1. Normalize: standardized all responses through shared middleware.
2. Enforce access control: added gateway auth + RBAC middleware with tenant context checks.
3. Re-check: validated routes/middleware against `docs/api-standards.md`, `docs/identity-auth-rbac.md`, and `docs/org-multi-tenancy.md` guard requirements.
4. Score: **10/10**.

## CPQ FIX LOOP

1. Fix: added quote/order APIs and in-memory entities with pricing + conversion logic.
2. Re-check: verified conversion prerequisites, success path, and error path for non-accepted quotes.
3. Re-check: confirmed domain-model alignment for required quote fields and tenant scope propagation.
4. Score: **10/10**.
