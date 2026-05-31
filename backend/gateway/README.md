# API Gateway (B1-P03::API_GATEWAY)

## Gateway structure

```text
gateway/
  app.js
  server.js
  routes/
    index.js                         ← 42 routers mounted under /api/v1
    v1-auth.routes.js
    v1-users.routes.js
    v1-accounts.routes.js
    v1-contacts.routes.js
    v1-leads.routes.js
    v1-opportunities.routes.js
    v1-followups.routes.js
    v1-quotes.routes.js
    v1-orders.routes.js
    v1-payments.routes.js
    v1-payment-webhooks.routes.js
    v1-whatsapp-webhooks.routes.js
    v1-forecasts.routes.js
    v1-subscriptions.routes.js
    v1-invoice-summaries.routes.js
    v1-collections.routes.js
    v1-activities.routes.js
    v1-tasks.routes.js
    v1-price-books.routes.js
    v1-emails.routes.js
    v1-audit.routes.js
    v1-sync.routes.js
    v1-cases.routes.js               ← Sprint 5B-1
    v1-knowledge.routes.js           ← Sprint 5B-1
    v1-inbox.routes.js               ← Sprint 5B-2
    v1-territories.routes.js         ← Sprint 5B-3
    v1-campaigns.routes.js           ← Sprint 5B-4
    v1-segments.routes.js            ← Sprint 5B-4
    v1-templates.routes.js           ← Sprint 5B-4
    v1-partners.routes.js            ← Sprint 5B-5
    v1-workflows.routes.js           ← Sprint 5B-6
    v1-ai.routes.js                  ← Sprint 5B-7
    v1-org-settings.routes.js        ← Phase 6 wiring
    v1-roles.routes.js               ← Phase 6 wiring
    v1-notification-preferences.routes.js ← Phase 6 wiring
    v1-feature-flags-mgmt.routes.js  ← Phase 6 wiring
    v1-compliance-settings.routes.js ← Phase 6 wiring
    v1-privacy.routes.js             ← Phase 6 wiring
    v1-tenants.routes.js             ← Phase 6 wiring
    v1-billing.routes.js             ← Phase 6 wiring (G-04)
    v1-integrations.routes.js        ← Phase 6 wiring (G-05)
    v1-governance.routes.js          ← Phase 6 wiring (J-03)
    v1-reports.routes.js             ← Phase 6 wiring (H-07)
    v1-communications.routes.js      ← Phase 6 wiring (A-08)
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

## Gateway Route Map (all 42 prefixes under /api/v1)

| Prefix | Route file | Domain |
|---|---|---|
| `/auth` | v1-auth.routes.js | Identity |
| `/users` | v1-users.routes.js | Identity |
| `/accounts` | v1-accounts.routes.js | Accounts |
| `/contacts` | v1-contacts.routes.js | Contacts |
| `/leads` | v1-leads.routes.js | Leads |
| `/opportunities` | v1-opportunities.routes.js | Pipeline |
| `/followups` | v1-followups.routes.js | Follow-up Enforcement |
| `/quotes` | v1-quotes.routes.js | CPQ |
| `/orders` | v1-orders.routes.js | CPQ |
| `/payments` | v1-payments.routes.js | Payments |
| `/webhooks/payments` | v1-payment-webhooks.routes.js | Payments |
| `/webhooks/whatsapp` | v1-whatsapp-webhooks.routes.js | WhatsApp |
| `/forecasts` | v1-forecasts.routes.js | Forecasting |
| `/subscriptions` | v1-subscriptions.routes.js | Billing |
| `/invoice-summaries` | v1-invoice-summaries.routes.js | Collections |
| `/collections` | v1-collections.routes.js | Collections |
| `/activities` | v1-activities.routes.js | Activity Timeline |
| `/tasks` | v1-tasks.routes.js | Tasks |
| `/price-books` | v1-price-books.routes.js | Product Catalog |
| `/emails` | v1-emails.routes.js | Communication |
| `/audits` | v1-audit.routes.js | Audit & Compliance |
| `/sync` | v1-sync.routes.js | Offline Sync |
| `/cases` | v1-cases.routes.js | Case Management (5B-1) |
| `/support` | v1-cases.routes.js (supportRouter) | Support Console (5B-1) |
| `/knowledge` | v1-knowledge.routes.js | Knowledge Base (5B-1) |
| `/inbox` | v1-inbox.routes.js | Shared Inbox (5B-2) |
| `/territories` | v1-territories.routes.js | Territory Management (5B-3) |
| `/campaigns` | v1-campaigns.routes.js | Marketing Campaigns (5B-4) |
| `/segments` | v1-segments.routes.js | Campaign Segments (5B-4) |
| `/templates` | v1-templates.routes.js | Message Templates (5B-4) |
| `/partners` | v1-partners.routes.js | Partner Management (5B-5) |
| `/deal-registrations` | v1-partners.routes.js (dealRegsRouter) | Deal Registrations (5B-5) |
| `/workflows` | v1-workflows.routes.js | Workflow Engine (5B-6) |
| `/ai` | v1-ai.routes.js | AI & Predictive Models (5B-7) |
| `/org/settings` | v1-org-settings.routes.js | Org Settings (Phase 6) |
| `/roles` | v1-roles.routes.js | Role Management (Phase 6) |
| `/notification-preferences` | v1-notification-preferences.routes.js | Notification Prefs (Phase 6) |
| `/feature-flags` | v1-feature-flags-mgmt.routes.js | Feature Flag Management (Phase 6) |
| `/compliance/settings` | v1-compliance-settings.routes.js | Compliance Config (Phase 6) |
| `/privacy` | v1-privacy.routes.js | Consent & Privacy (Phase 6) |
| `/tenants` | v1-tenants.routes.js | Tenant Entitlements (Phase 6) |
| `/billing` | v1-billing.routes.js | Billing & Subscription (Phase 6) |
| `/integrations` | v1-integrations.routes.js | Integration Settings (Phase 6) |
| `/governance` | v1-governance.routes.js | Data Governance Console (Phase 6) |
| `/reports` | v1-reports.routes.js | Custom Report Builder (Phase 6) |
| `/communications` | v1-communications.routes.js | Comms Engagement (Phase 6) |

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

## Forecasting APIs (B2-P06::FORECASTING)

### `POST /api/v1/forecasts/model`
Builds an opportunity forecast model from caller-provided opportunity rows.

- Required scope: `forecasts.read`
- Request body fields:
  - `opportunities` (array)

### `POST /api/v1/forecasts/aggregate`
Returns aggregate forecast totals and buckets from caller-provided opportunity rows.

- Required scope: `forecasts.read`
- Request body fields:
  - `opportunities` (array)
  - `group_by` (`stage` or `forecast_category`, optional; defaults to `stage`)

Both endpoints validate opportunity rows using the domain-model shape (`opportunity_id`, `tenant_id`, `stage`, `amount`, `close_date`, `forecast_category`, `is_closed`, `is_won`) and reject invalid data with `422 validation_error`.

## Audit APIs

- `GET /api/v1/audits/events` (scope: `audit.logs.read`)
