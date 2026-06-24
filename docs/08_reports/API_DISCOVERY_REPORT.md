Status: Draft
Authority Level: High
Last Reviewed: 2026-06-22
Owner: Shared

# API_DISCOVERY_REPORT.md
> API discovery findings from Phase 2 Backend Authority Capture

---

## 1. Discovery Summary

**Total endpoints:** 228 (from API_INVENTORY.md, confirmed during Phase 2)  
**Gateway route files:** 44 v1-*.routes.js  
**API version prefix:** /api/v1/  
**Base URL (prod):** https://crm-gateway.onrender.com/api/v1/

---

## 2. Endpoint Distribution by Domain

| Domain | Route file | Endpoints |
|---|---|---|
| Auth | v1-auth.routes.js | 7 |
| Leads | v1-leads.routes.js | 8 |
| Follow-ups | v1-followups.routes.js | 6 |
| Contacts | v1-contacts.routes.js | 7 |
| Accounts | v1-accounts.routes.js | 4 |
| Opportunities | v1-opportunities.routes.js | 6 |
| Quotes | v1-quotes.routes.js | 7 |
| Orders | v1-orders.routes.js | 4 |
| Cases | v1-cases.routes.js | 14 |
| Support | v1-support-queues.routes.js | 4 |
| Inbox | v1-inbox.routes.js | 9 |
| WhatsApp webhooks | v1-whatsapp-webhooks.routes.js | 6 |
| Payment webhooks | v1-payment-webhooks.routes.js | 3 |
| Collections | v1-collections.routes.js | 5 |
| Invoice summaries | v1-invoice-summaries.routes.js | 3 |
| Payments | v1-payments.routes.js | 4 |
| Subscriptions | v1-subscriptions.routes.js | 4 |
| Billing | v1-billing.routes.js | 4 |
| Activities | v1-activities.routes.js | 4 |
| Tasks | v1-tasks.routes.js | 6 |
| Campaigns | v1-campaigns.routes.js | 9 |
| Segments | v1-segments.routes.js | 4 |
| Templates | v1-templates.routes.js | 5 |
| Emails | v1-emails.routes.js | 3 |
| Communications | v1-communications.routes.js | 4 |
| AI | v1-ai.routes.js | 13 |
| Forecasts | v1-forecasts.routes.js | 3 |
| Reports | v1-reports.routes.js | 3 |
| Workflows | v1-workflows.routes.js | 11 |
| Territories | v1-territories.routes.js | 11 |
| Knowledge | v1-knowledge.routes.js | 5 |
| Partners | v1-partners.routes.js | 13 |
| Users | v1-users.routes.js | 5 |
| Roles | v1-roles.routes.js | 4 |
| Notifications | v1-notifications.routes.js | 4 |
| Notification preferences | v1-notification-preferences.routes.js | 2 |
| Audit | v1-audit.routes.js | 2 |
| Governance | v1-governance.routes.js | 3 |
| Compliance settings | v1-compliance-settings.routes.js | 2 |
| Privacy | v1-privacy.routes.js | 2 |
| Org settings | v1-org-settings.routes.js | 2 |
| Integrations | v1-integrations.routes.js | 3 |
| Feature flags | v1-feature-flags-mgmt.routes.js | 2 |
| Sync | v1-sync.routes.js | 3 |

---

## 3. Public (No-Auth) Endpoints

These endpoints bypass authMiddleware:

| Method | Path | Purpose |
|---|---|---|
| POST | /api/v1/auth/login | Login |
| POST | /api/v1/auth/register | Register |
| POST | /api/v1/auth/refresh | Token refresh |
| POST | /api/v1/auth/forgot-password | OTP request |
| POST | /api/v1/auth/reset-password | OTP + new password |
| GET | /api/v1/whatsapp-webhooks/meta | Meta webhook verification |
| POST | /api/v1/whatsapp-webhooks/meta | Inbound Meta messages |
| POST | /api/v1/whatsapp-webhooks/gupshup | Inbound Gupshup messages |
| POST | /api/v1/whatsapp-webhooks/360dialog | Inbound 360dialog messages |
| POST | /api/v1/whatsapp-webhooks/twilio | Inbound Twilio messages |
| POST | /api/v1/payment-webhooks/jazzcash | JazzCash callback |
| POST | /api/v1/payment-webhooks/easypaisa | Easypaisa callback |
| GET | /health | Gateway health check |
| GET | /ready | Gateway readiness check |

---

## 4. API Request Lifecycle

Every authenticated API request follows this sequence:

1. `requestId` middleware assigns `X-Request-ID`
2. `helmet` applies security headers
3. `cors` validates origin
4. `rateLimitHook` checks Redis sliding window (fails-open)
5. `observabilityMiddleware` starts timer, parses/generates traceparent
6. `idempotencyMiddleware` validates Idempotency-Key on writes
7. Auth bypass check for public paths
8. `authMiddleware()` validates JWT (9-step validation)
9. Route handler executes
10. `respondSuccess(res, data, meta)` wraps response
11. `observabilityMiddleware` logs request on response finish
12. `auditMiddleware` appends to hash-chain on mutations

---

## 5. Idempotency Requirement

All write requests (POST, PATCH, PUT, DELETE) require:
```
Idempotency-Key: <unique-uuid>
```

Missing header: 422 `validation_error`  
Duplicate key with same body: 200 (returns cached response)  
Duplicate key with different body: 409 `conflict`

**Note:** Frontend does not currently auto-generate Idempotency-Key headers (Gap V-002).

---

## 6. Pagination

All list endpoints support:
```
GET /leads?page=1&per_page=25
```
Default: page=1, per_page=25.

Response `meta` includes: page, per_page, total, total_pages.

---

## 7. Rate Limits by Endpoint Type

| Endpoint category | Limit per 60-second window |
|---|---|
| GET requests | 300 |
| POST /payments, /emails, /users, /forecasts | 20 |
| POST /audit | 10 |
| Other write requests | 120 |

Rate limit key: `rl:{tenant_id}:{user_id}:{METHOD}:{canonical_path}`  
Response on limit: 429 `rate_limited` with Retry-After header

---

## 8. FastAPI Internal Routes

These routes are called exclusively by the gateway (not by frontend):

| Path | Purpose |
|---|---|
| POST /internal/leads/:id/register | Register lead with FollowupEnforcementEngine |
| GET /internal/leads/:id/next-action | Get next-action suggestion |
| POST /internal/process-due | Process overdue follow-up tasks |
| GET /internal/metrics | FollowupEnforcementEngine metrics |
| POST /internal/payments | Create payment (proxied from gateway) |
| GET /internal/invoices/:id | Get invoice (proxied) |
| POST /internal/invoices/overdue-rollup | Overdue rollup (proxied) |
| POST /internal/classify | Classify WhatsApp message |
| POST /internal/messages | Store inbound message |
| POST /internal/sync/batch | Process sync batch |
| GET /internal/sync/status | Sync status |
| GET /internal/sync/queue | Sync queue |
| GET /internal/chain-check | Activity chain integrity |
| POST /internal/activation/seed | Seed new tenant pipeline |
| POST /internal/migrate | Run Alembic upgrade |

---

## 9. Key API Findings

| Finding | Detail |
|---|---|
| contacts.delete gap | contacts.delete scope absent from SCOPES constant — effectively removes this endpoint from all roles (H-002) |
| dev token endpoint | POST /dev/token exists in gateway (when JWT_SECRET unset) — returns unsigned dev token. Must be blocked in production. |
| Raw body capture | Webhook endpoints receive raw request body for HMAC verification before JSON parsing |
| Response wrapper | All responses use standard envelope: `{ data, meta }` / `{ error, meta }` |
| Idempotency cache | In-memory only — does not survive gateway restarts |

---

*End API_DISCOVERY_REPORT.md*
