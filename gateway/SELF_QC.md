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

## FIX LOOP

1. Normalize: standardized all responses through shared middleware.
2. Re-check: validated endpoints/middleware against `docs/api-standards.md` requirements.
3. Score: **10/10** (no inconsistent API formats found).
