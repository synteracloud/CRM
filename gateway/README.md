# API Gateway (B1-P03::API_GATEWAY)

## Gateway structure

```text
gateway/
  app.js
  server.js
  routes/
    index.js
    v1-users.routes.js
    v1-activities.routes.js
    v1-tasks.routes.js
  middleware/
    request-id.js
    request-validation.js
    response-wrapper.js
    rate-limit-hook.js
  validators/
    common.js
  types/
    api.js
```

## Middleware

- `request-id.js` injects/propagates `meta.request_id`.
- `request-validation.js` enforces:
  - `Accept: application/json`
  - `Content-Type: application/json` for body methods
  - snake_case keys
  - unknown-field rejection
  - query standards (`page`, `page_size`, snake_case)
- `response-wrapper.js` normalizes success/error envelopes.
- `rate-limit-hook.js` exposes an integration hook for external limit engines.

## Standard response wrapper

Success envelope:

```json
{
  "data": {},
  "meta": {
    "request_id": "req_xxx"
  }
}
```

Error envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "One or more fields are invalid.",
    "details": []
  },
  "meta": {
    "request_id": "req_xxx"
  }
}
```

## Activities + Tasks APIs (B2-P04)

- `GET /api/v1/activities`
- `POST /api/v1/activities`
- `GET /api/v1/tasks`
- `POST /api/v1/tasks`
- `POST /api/v1/tasks/{task_id}/reschedule`

All endpoints follow the same envelope, auth, and tenant-context rules as other v1 resources.
