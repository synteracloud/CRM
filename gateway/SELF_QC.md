# SELF-QC

## B2-P02::ACCOUNTS_CONTACTS

### Standards conformance check

- ✅ Base paths use `/api/v1/accounts` and `/api/v1/contacts`.
- ✅ Resource naming uses lowercase, plural nouns and noun-based linking path (`/accounts/{account_id}/contacts/{contact_id}`).
- ✅ Query parameters remain snake_case (`page`, `page_size`).
- ✅ Request/response payload keys are snake_case.
- ✅ Unknown body properties are rejected by shared validation middleware.
- ✅ Success envelope is `{ data, meta.request_id }`.
- ✅ Error envelope is `{ error, meta.request_id }`.
- ✅ Canonical error codes are reused from shared API types.
- ✅ Tenant isolation is enforced using token tenant + `x-tenant-id` guard.
- ✅ Account ↔ Contact relationship implemented as `Account 1-N Contact` using nullable `contact.account_id`.
- ✅ Account deletion unlinks related contacts to preserve nullable FK semantics.
- ✅ Linking APIs validate that both account and contact exist in the same tenant.
- ✅ Service layer is centralized to avoid route-level duplication.

## FIX LOOP

1. Fix: implemented account/contact entities, service layer, CRUD routes, and explicit link/unlink APIs.
2. Re-check: verified model fields and relationship semantics against `docs/domain-model.md`; re-validated route and envelope rules against `docs/api-standards.md`.
3. Re-check: executed syntax checks for all new/updated gateway modules.
4. Score: **10/10**.
