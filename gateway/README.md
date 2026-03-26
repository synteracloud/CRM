# API Gateway (B1-P03::API_GATEWAY)

## Gateway structure

```text
gateway/
  app.js
  server.js
  routes/
    index.js
    v1-orders.routes.js
    v1-quotes.routes.js
    v1-users.routes.js
  data/
    cpq-store.js
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

## CPQ quote/order APIs

- `GET /api/v1/quotes` (scope: `quotes.read`)
- `POST /api/v1/quotes` (scope: `quotes.create`)
- `GET /api/v1/quotes/{quote_id}` (scope: `quotes.read`)
- `POST /api/v1/quotes/{quote_id}/acceptances` (scope: `quotes.accept`)
- `POST /api/v1/quotes/{quote_id}/orders` (scope: `orders.create`) — quote → order conversion
- `GET /api/v1/orders` (scope: `orders.read`)
- `GET /api/v1/orders/{order_id}` (scope: `orders.read`)

`cpq-store.js` contains:
- quote entity shape (aligned to domain model fields)
- order entity shape
- basic pricing logic for subtotal/discount/tax/grand_total
- conversion logic from accepted quote to order

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
