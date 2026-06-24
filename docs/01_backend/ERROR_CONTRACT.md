Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: Shared

# ERROR_CONTRACT.md
> Source: backend/gateway/middleware/response-wrapper.js, backend/gateway/types/api.js, backend/gateway/app.js, backend/services/app.py

---

## 1. Standard Error Envelope

Both the gateway (Node.js) and FastAPI service (Python) produce the same error envelope shape:

```json
{
  "error": {
    "code": "string — machine-readable error code",
    "message": "string — human-readable description",
    "details": [
      {
        "field": "string — field name or context",
        "reason": "string — specific reason code"
      }
    ]
  },
  "meta": {
    "request_id": "string — UUID"
  }
}
```

**Notes:**
- `details` is always an array (may be empty `[]`)
- `meta.request_id` is always present (gateway: from `requestIdMiddleware`; FastAPI: generated UUID4)
- The `data` key is absent on error responses

---

## 2. Canonical Error Codes

Defined in `backend/gateway/types/api.js` (CANONICAL_ERROR_CODES):

| Code | HTTP Status | When Used |
|---|---|---|
| `bad_request` | 400 | Malformed JSON body, unparseable request |
| `unauthorized` | 401 | Missing/invalid/expired JWT; revoked JTI; missing required claims |
| `forbidden` | 403 | CORS violation; missing x-tenant-id header; tenant_id mismatch; missing required scope; tenant-scoped resource mismatch |
| `not_found` | 404 | Requested resource does not exist |
| `conflict` | 409 | Duplicate resource; optimistic lock conflict (version_no mismatch); idempotency key reused with different payload; in-flight duplicate; resource in terminal state |
| `validation_error` | 422 | Required fields missing; invalid field format; Pydantic schema validation failure; business rule violation |
| `rate_limited` | 429 | Rate limit window exceeded |
| `internal_error` | 500 | Unhandled exception; unexpected error |
| `service_unavailable` | 503 | Downstream service unreachable |

**Additional codes used in route handlers** (not in CANONICAL_ERROR_CODES — use statusOverride):

| Code | HTTP Status | Context |
|---|---|---|
| `REOPEN_WINDOW_EXPIRED` | 422 | Case reopen attempted > 14 days after close |
| `INVALID_STATUS_TRANSITION` | 422 | Invalid state machine transition |
| `AGENT_CAPACITY_EXCEEDED` | 409 | Agent at max concurrent conversations |
| `NOT_IMPLEMENTED` | 501 | Legacy /auth/sessions endpoint |

---

## 3. HTTP Status to Error Type Mapping

| HTTP Status | Error Code | Typical `details[].reason` values |
|---|---|---|
| 400 | bad_request | invalid_json |
| 401 | unauthorized | missing_bearer_token, invalid_signature, expired_or_missing_exp, token_not_yet_valid, missing_required_claims, missing_iss_or_aud, token_revoked, invalid_token |
| 403 | forbidden | missing_tenant_context, tenant_mismatch, missing_{scope_name}, tenant_resource_mismatch, audit_mapping_missing (strict mode) |
| 404 | not_found | (message describes what was not found) |
| 409 | conflict | (message describes conflict type) |
| 422 | validation_error | required (missing field), invalid_format, idempotency_key_reused_with_different_payload, request_in_progress, required_for_write_operations (missing Idempotency-Key) |
| 429 | rate_limited | rate_limit_exceeded |
| 500 | internal_error | (no details on internal errors — message only) |
| 503 | service_unavailable | (message describes unreachable service) |

---

## 4. Validation Error Format (422 Responses)

### Gateway validation (from middleware/response-wrapper.js + route handlers)
```json
{
  "error": {
    "code": "validation_error",
    "message": "One or more fields are invalid.",
    "details": [
      { "field": "email", "reason": "required" },
      { "field": "owner_id", "reason": "required" },
      { "field": "phone_e164", "reason": "invalid_format" }
    ]
  },
  "meta": { "request_id": "uuid" }
}
```

### FastAPI validation (Pydantic — from services/app.py exception handler)
```json
{
  "error": {
    "code": "validation_error",
    "message": "human-readable description from Pydantic"
  },
  "meta": { "request_id": "generated-uuid" }
}
```
Note: CONFIRMED Phase 3.25 — `backend/services/app.py` registers `@app.exception_handler(HTTPException)` which normalizes HTTP exceptions to canonical format. However, Pydantic `RequestValidationError` (422) is NOT overridden — those come through in FastAPI's native `{ detail: [{ loc, msg, type }] }` format. Gateway-level 422 responses (from gateway route validation) follow the canonical format. For 422 from FastAPI-proxied service endpoints, frontend must handle FastAPI's native format. (This gap is captured in VALIDATION_PARITY.md V-003.)

---

## 5. Auth Error Examples

### 401 — Missing bearer token
```json
{
  "error": {
    "code": "unauthorized",
    "message": "Missing bearer token.",
    "details": [{ "field": "authorization", "reason": "missing_bearer_token" }]
  },
  "meta": { "request_id": "uuid" }
}
```

### 401 — Expired token
```json
{
  "error": {
    "code": "unauthorized",
    "message": "Token is expired or missing exp claim.",
    "details": [{ "field": "authorization", "reason": "expired_or_missing_exp" }]
  },
  "meta": { "request_id": "uuid" }
}
```

### 401 — Revoked JTI
```json
{
  "error": {
    "code": "unauthorized",
    "message": "Token has been revoked.",
    "details": [{ "field": "authorization", "reason": "token_revoked" }]
  },
  "meta": { "request_id": "uuid" }
}
```

---

## 6. Forbidden Error Examples

### 403 — Missing x-tenant-id header
```json
{
  "error": {
    "code": "forbidden",
    "message": "Missing tenant context header.",
    "details": [{ "field": "x-tenant-id", "reason": "missing_tenant_context" }]
  },
  "meta": { "request_id": "uuid" }
}
```

### 403 — Missing scope
```json
{
  "error": {
    "code": "forbidden",
    "message": "Missing required scope for this operation.",
    "details": [
      { "field": "scopes", "reason": "missing_leads.create" }
    ]
  },
  "meta": { "request_id": "uuid" }
}
```

---

## 7. Not Found Format (404)
```json
{
  "error": {
    "code": "not_found",
    "message": "Lead not found.",
    "details": []
  },
  "meta": { "request_id": "uuid" }
}
```

---

## 8. Conflict Format (409)

### Optimistic concurrency conflict
```json
{
  "error": {
    "code": "conflict",
    "message": "Case has been updated by another request. Please refresh and retry.",
    "details": []
  },
  "meta": { "request_id": "uuid" }
}
```

### Idempotency key reuse
```json
{
  "error": {
    "code": "conflict",
    "message": "Idempotency key was already used with a different payload.",
    "details": [{ "field": "idempotency_key", "reason": "idempotency_key_reused_with_different_payload" }]
  },
  "meta": { "request_id": "uuid" }
}
```

---

## 9. Gateway vs FastAPI Error Handling Differences

| Aspect | Gateway (Node.js) | FastAPI (Python) |
|---|---|---|
| Error format | `respondError()` — canonical envelope | `http_exception_handler` — same envelope shape |
| request_id | From `requestIdMiddleware` (UUID assigned on arrival) | Generated UUID4 per error response |
| Pydantic validation | N/A — uses manual field validation | FastAPI's built-in 422 with potential Pydantic detail format |
| Unhandled errors | Global Express error handler → 500 | `unhandled_exception_handler` → 500 |
| CORS errors | 403 forbidden | N/A (CORS handled at gateway) |
| Stack traces | Logged; never returned in response | Logged; never returned in response |

---

## 10. Rate Limit Error

```json
{
  "error": {
    "code": "rate_limited",
    "message": "Rate limit exceeded. Please retry later.",
    "details": [{ "field": "request", "reason": "rate_limit_exceeded" }]
  },
  "meta": { "request_id": "uuid" }
}
```

**Response headers when rate limited:**
```
Retry-After: 47
```

---

## 11. Error Logging Behavior

**Gateway:**
- All unhandled errors are logged via `logger.error({ event: 'unhandled_error', error: err.message, stack: err.stack })`
- Auth failures: NOT explicitly logged (silent 401/403 — security practice)
- Rate limit blocks: NOT logged (only responded to with 429)
- Structured JSON to stdout on every completed request includes `status_code` — 4xx/5xx are detectable by log aggregation

**FastAPI:**
- `unhandled_exception_handler` uses `logger.exception()` which includes full traceback
- HTTPExceptions (expected business errors) are NOT logged — only returned as responses

---

*End ERROR_CONTRACT.md*
