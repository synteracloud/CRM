# API Standards

This document defines **mandatory API standards** for all services. These rules are normative and apply uniformly across the platform.

## 1) Endpoint Patterns

### 1.1 Base Path
All HTTP APIs MUST use this base path format:

```text
/api/v{major}/{resource}
```

Examples:

- `GET /api/v1/users`
- `GET /api/v1/users/{userId}`
- `POST /api/v1/orders`

### 1.2 Resource Naming
- Resource names MUST be lowercase, plural, and kebab-case where needed.
- Path segments MUST represent nouns, not verbs.
- Nested resources MUST be used only for strict ownership relationships.

Valid examples:

- `/api/v1/users`
- `/api/v1/order-items`
- `/api/v1/users/{userId}/sessions`

Invalid examples:

- `/api/v1/getUsers` (verb in path)
- `/api/v1/UserProfiles` (camel/pascal case)
- `/api/v1/user` (singular where collection is expected)

### 1.3 HTTP Method Semantics
- `GET` MUST be read-only.
- `POST` MUST create a new resource or trigger a non-idempotent operation.
- `PUT` MUST replace a full resource and be idempotent.
- `PATCH` MUST partially update a resource.
- `DELETE` MUST remove a resource and be idempotent.

### 1.4 Query Parameters
- Filtering, sorting, pagination, and field selection MUST be in query params.
- Query parameter names MUST be snake_case.

Standard query params:

- `page` (1-based integer)
- `page_size` (integer, max 100)
- `sort` (comma-separated fields, prefix `-` for descending)
- `fields` (comma-separated response fields)
- `filter[...]` (structured filtering)

Example:

```http
GET /api/v1/users?page=1&page_size=25&sort=-created_at&fields=id,email,status&filter[status]=active
```

## 2) Request Schema

### 2.1 Content Type
- Request body for JSON APIs MUST be `Content-Type: application/json`.
- Clients MUST send `Accept: application/json`.

### 2.2 JSON Structure
- JSON keys MUST be `snake_case`.
- IDs MUST be strings.
- Timestamps MUST be RFC 3339 in UTC (`YYYY-MM-DDTHH:MM:SSZ`).
- Unknown properties MUST be rejected with `400 Bad Request`.

### 2.3 Create Request Example

```http
POST /api/v1/users
Content-Type: application/json
Authorization: Bearer <token>

{
  "email": "jane.doe@example.com",
  "display_name": "Jane Doe",
  "status": "active"
}
```

### 2.4 Update Request Example

```http
PATCH /api/v1/users/usr_01HZX7X4QW2D7B2K4A0G5R9M2C
Content-Type: application/json
Authorization: Bearer <token>

{
  "display_name": "Jane A. Doe"
}
```

## 3) Response Schema

### 3.1 Standard Success Envelope
All successful responses MUST use this envelope:

```json
{
  "data": {},
  "meta": {
    "request_id": "req_01J8Y7K9M9YX3G8W4X9E2N1T6Q"
  }
}
```

Rules:
- `data` MUST contain the primary payload (object or array).
- `meta.request_id` MUST be present in all responses.
- Additional metadata MUST be placed in `meta`.

### 3.2 List Response Example

```json
{
  "data": [
    {
      "id": "usr_01HZX7X4QW2D7B2K4A0G5R9M2C",
      "email": "jane.doe@example.com",
      "display_name": "Jane Doe",
      "status": "active",
      "created_at": "2026-03-26T12:00:00Z",
      "updated_at": "2026-03-26T12:00:00Z"
    }
  ],
  "meta": {
    "request_id": "req_01J8Y7K9M9YX3G8W4X9E2N1T6Q",
    "pagination": {
      "page": 1,
      "page_size": 25,
      "total_items": 1,
      "total_pages": 1
    }
  }
}
```

### 3.3 Single Resource Response Example

```json
{
  "data": {
    "id": "usr_01HZX7X4QW2D7B2K4A0G5R9M2C",
    "email": "jane.doe@example.com",
    "display_name": "Jane Doe",
    "status": "active",
    "created_at": "2026-03-26T12:00:00Z",
    "updated_at": "2026-03-26T12:00:00Z"
  },
  "meta": {
    "request_id": "req_01J8Y7K9M9YX3G8W4X9E2N1T6Q"
  }
}
```

## 4) Error Format

All non-2xx responses MUST use this error envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "One or more fields are invalid.",
    "details": [
      {
        "field": "email",
        "reason": "must_be_valid_email"
      }
    ]
  },
  "meta": {
    "request_id": "req_01J8Y7K9M9YX3G8W4X9E2N1T6Q"
  }
}
```

### 4.1 Error Field Requirements
- `error.code` MUST be stable, machine-readable snake_case.
- `error.message` MUST be human-readable and safe to expose.
- `error.details` MUST be an array (empty array if no granular details).
- `meta.request_id` MUST be present.

### 4.2 Canonical Error Codes
The following canonical codes MUST be used consistently:

- `bad_request` → `400`
- `unauthorized` → `401`
- `forbidden` → `403`
- `not_found` → `404`
- `conflict` → `409`
- `validation_error` → `422`
- `rate_limited` → `429`
- `internal_error` → `500`
- `service_unavailable` → `503`

## 5) Versioning Strategy

### 5.1 Version Placement
- Major version MUST be in the URL path: `/api/v{major}`.
- Only major versions are represented in the path.

### 5.2 Compatibility Rules
- Backward-compatible changes (e.g., additive fields) MUST NOT increase major version.
- Backward-incompatible changes MUST require a new major version.
- Existing major versions MUST be supported for a published deprecation window.

### 5.3 Deprecation Policy
- Deprecations MUST be announced at least 180 days before removal.
- Responses from deprecated versions SHOULD include:
  - `Deprecation: true`
  - `Sunset: <RFC 1123 date>`
  - Link to migration guide in `Link` header.

Example:

```http
Deprecation: true
Sunset: Tue, 22 Sep 2026 00:00:00 GMT
Link: <https://api.example.com/docs/migrations/v1-to-v2>; rel="deprecation"
```

## 6) Authentication and Authorization Rules

### 6.1 Authentication
- All non-public endpoints MUST require OAuth 2.0 Bearer tokens.
- Token MUST be sent in `Authorization` header:

```http
Authorization: Bearer <access_token>
```

- Query-string tokens MUST NOT be accepted.

### 6.2 Authorization
- Authorization MUST be enforced server-side on every request.
- Deny-by-default policy MUST apply.
- Access decisions MUST evaluate subject, action, resource, and tenant scope.

### 6.3 Auth Failure Behavior
- Missing or invalid token MUST return `401 unauthorized`.
- Valid token without required permissions MUST return `403 forbidden`.
- Error payload MUST follow the standard error envelope.

## 7) Cross-Service Consistency Requirements

These standards are mandatory for every service:

1. Same URL pattern format (`/api/v{major}/...`).
2. Same JSON naming convention (`snake_case`).
3. Same success and error envelopes.
4. Same request/response timestamp format (RFC 3339 UTC).
5. Same canonical error codes.
6. Same versioning and deprecation policy.
7. Same authentication transport (`Authorization: Bearer ...`).

No service may define alternate envelope shapes, alternate key casing, or alternate error structures.

## 8) Compliance Checklist

A service is compliant only if all answers are **Yes**:

- Are all endpoints under `/api/v{major}`?
- Are all request/response keys `snake_case`?
- Do all success responses include `data` and `meta.request_id`?
- Do all error responses include `error` and `meta.request_id`?
- Are canonical error codes used exactly as defined?
- Is major-version path-based versioning implemented?
- Are Bearer tokens required for non-public endpoints?
- Are `401` and `403` semantics correctly separated?



## 9) Asynchronous Job API Requirements

These rules are mandatory for background job/scheduler endpoints (for example `POST /api/v1/jobs` and `POST /api/v1/job-schedules`).

### 9.1 Idempotency Header
- Job and schedule creation endpoints MUST accept `Idempotency-Key` header.
- Servers MUST scope idempotency by `(tenant_id, method, route, idempotency_key)`.
- Replays with same key within dedupe window MUST return the original response (or a deterministic equivalent) and MUST NOT create duplicate runnable work.

### 9.2 Accepted Response for Async Work
- Endpoints that enqueue background work SHOULD return `202 Accepted` when execution is deferred.
- Response `data` MUST include `job_id` and an initial `status`.

### 9.3 Conflict Semantics
- If a request is semantically conflicting with active work, API MUST return `409 conflict` and include conflicting `job_id` or `schedule_id` in `error.details`.

