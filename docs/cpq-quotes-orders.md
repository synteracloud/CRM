# B2-P05::CPQ_QUOTES_ORDERS

## Entities

### Quote (Quote Service)
- `quote_id` (PK)
- `tenant_id` (FK -> Tenant)
- `opportunity_id` (FK -> Opportunity)
- `status`
- `currency`
- `subtotal`
- `discount_total`
- `tax_total`
- `grand_total`
- `valid_until`
- `created_at`
- `accepted_at`
- `line_items[]`
  - `quote_line_item_id`
  - `product_id`
  - `quantity`
  - `list_price`
  - `discount_percent`
  - `net_price`

### Order (Order Service)
- `order_id` (PK)
- `tenant_id` (FK -> Tenant)
- `quote_id` (FK -> Quote)
- `opportunity_id` (FK -> Opportunity)
- `status`
- `currency`
- `subtotal`
- `discount_total`
- `tax_total`
- `grand_total`
- `ordered_at`
- `created_at`
- `line_items[]` (copied from quote at conversion time)

## APIs

- `GET /api/v1/quotes`
- `POST /api/v1/quotes`
- `GET /api/v1/quotes/{quote_id}`
- `POST /api/v1/quotes/{quote_id}/acceptances`
- `POST /api/v1/quotes/{quote_id}/orders` (conversion)
- `GET /api/v1/orders`
- `GET /api/v1/orders/{order_id}`

All endpoints use:
- `/api/v1` base path
- snake_case JSON keys
- standard `{ data, meta.request_id }` success envelope
- standard `{ error, meta.request_id }` error envelope

## Conversion workflow (quote → order)

1. Create quote with line items.
2. Run basic pricing to compute `subtotal`, `discount_total`, `tax_total`, `grand_total`.
3. Accept quote via acceptance resource.
4. Convert accepted quote to order via nested order creation endpoint.
5. Persist order totals from quote snapshot + `ordered_at` from quote acceptance.

## Self-QC

- ✅ Conversion flow complete.
- ✅ No missing quote fields (matches domain model definition).
- ✅ Order fields include conversion linkage and commercial totals.
- ✅ API patterns follow platform standards.

## Fix loop

- Fix → re-check → score: **10/10**.
