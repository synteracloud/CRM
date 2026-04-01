# H-QC_MASTER::SYSTEM_HARDENING_AUTO_FIX

## Outcome

Gateway hardening controls were tightened across security, abuse resistance, audit integrity, observability signal quality, and idempotent recovery behavior.

## Fixes Applied

1. **Security (auth + ABAC)**
   - Extended `requireScopes(...)` with `tenantBoundFields` enforcement so tenant-scoped identifiers in params/body/query cannot cross tenant boundaries.
   - Hardened authorization failures with explicit `tenant_resource_mismatch` denial reason.

2. **Rate limiting**
   - Added canonical route normalization (dynamic IDs collapse to `/:id`) to prevent limit evasion by path-shaping.
   - Applied stricter default limit for audit ingestion endpoints.

3. **Audit logging**
   - Added append-time hash-chain verification (`verifyAuditChain`) to detect tampering before new events are accepted.
   - Returned frozen copies in read APIs to preserve immutability assumptions downstream.

4. **Observability**
   - Added in-flight request metric emission and severity tagging on completion events.
   - Preserved request-id/trace-id continuity.

5. **Failure recovery / idempotency**
   - Updated idempotency middleware to avoid caching 5xx responses so transient failures can be retried safely.

## QC Gate Added

- `scripts/self_qc_system_hardening.py`
  - verifies mandatory hardening anchors remain present in middleware implementation.
- `tests/test_system_hardening_qc.py`
  - enforces QC gate in automated test runs.

## Re-check Commands

- `python3 scripts/self_qc_system_hardening.py`
- `pytest -q`
