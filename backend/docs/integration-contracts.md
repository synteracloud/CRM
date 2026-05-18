# Integration Contracts

This document defines all approved integration contracts for the CRM platform.

## External APIs

| Integration | Purpose | Base URL | Endpoints Used | Method(s) | Request Contract | Response Contract | Auth Method | Retry/Timeout Contract | Owner |
|---|---|---|---|---|---|---|---|---|---|
| **Stripe API** | Payment intents, subscription status sync | `https://api.stripe.com` | `/v1/payment_intents`, `/v1/customers`, `/v1/subscriptions` | `GET`, `POST` | Form-encoded fields per endpoint (`customer`, `amount`, `currency`, `metadata[account_id]`) | JSON objects including `id`, `status`, `customer`, `amount`, `currency` | Server-side secret key via `Authorization: Bearer <STRIPE_SECRET_KEY>` | Retry on `429/5xx` with exponential backoff (max 3); timeout 10s | Billing Team |
| **SendGrid API** | Transactional email delivery | `https://api.sendgrid.com` | `/v3/mail/send` | `POST` | JSON body with `personalizations[]`, `from`, `template_id`, `dynamic_template_data` | `202 Accepted` with empty body on success; JSON error payload on failure | API key via `Authorization: Bearer <SENDGRID_API_KEY>` | Retry on `429/5xx` (max 3); timeout 8s | Platform Team |
| **Twilio API** | SMS notifications and OTP messages | `https://api.twilio.com` | `/2010-04-01/Accounts/{AccountSid}/Messages.json` | `POST` | Form fields `To`, `From`, `Body`, optional `StatusCallback` | Form/JSON response containing `sid`, `status`, `error_code` | HTTP Basic Auth using `AccountSid` + `AuthToken` | Retry on network errors and `5xx` (max 2); timeout 8s | Communications Team |

## Webhooks

| Webhook Source | Direction | Endpoint (CRM) | Event Types | Payload Contract | Verification Contract | Idempotency Contract | Processing SLA | Failure Handling |
|---|---|---|---|---|---|---|---|---|
| **Stripe** | External → CRM | `POST /webhooks/stripe` | `payment_intent.succeeded`, `invoice.payment_failed`, `customer.subscription.updated` | JSON event envelope with `id`, `type`, `created`, `data.object` | Verify `Stripe-Signature` using endpoint signing secret; reject invalid signature with `400` | Store unique Stripe `event.id`; ignore duplicates | Ack within 3s | Return `5xx` on transient errors for Stripe retry; dead-letter after 10 failed attempts |
| **SendGrid Event Webhook** | External → CRM | `POST /webhooks/sendgrid/events` | `processed`, `delivered`, `bounce`, `dropped`, `open`, `click` | JSON array of event objects containing `email`, `event`, `timestamp`, `sg_event_id` | Verify signed webhook headers (`X-Twilio-Email-Event-Webhook-*`) | Deduplicate on `sg_event_id` | Ack within 3s | Persist raw events; reprocess from queue on internal failure |
| **Twilio Status Callback** | External → CRM | `POST /webhooks/twilio/status` | `queued`, `sent`, `delivered`, `undelivered`, `failed` | Form-encoded payload with `MessageSid`, `MessageStatus`, `To`, `ErrorCode` | Validate Twilio signature header `X-Twilio-Signature` | Deduplicate on `MessageSid` + `MessageStatus` | Ack within 3s | Retry internal processing from queue; alert after 5 consecutive failures |

## Data Contracts

| Contract Name | Producer | Consumer | Transport | Schema (Explicit Fields) | Required Fields | Validation Rules | Versioning Contract | Breaking Change Policy |
|---|---|---|---|---|---|---|---|---|
| **CustomerSync v1** | CRM | Stripe integration worker | Internal event bus | `account_id:string`, `email:string`, `full_name:string`, `billing_address:object`, `updated_at:datetime` | `account_id`, `email`, `updated_at` | `email` must be RFC 5322 compliant; `updated_at` in ISO-8601 UTC | `contract_version: "1.0"` field required in envelope | New required fields require v2; v1 maintained for 90 days |
| **PaymentStatus v1** | Stripe webhook processor | CRM billing domain | Internal queue | `payment_intent_id:string`, `account_id:string`, `status:enum`, `amount_minor:int`, `currency:string`, `occurred_at:datetime` | All fields required | `status ∈ {succeeded, processing, failed, canceled}`; `amount_minor > 0` | Semantic version in envelope, default `1.0` | Enum expansion is non-breaking; field removal is breaking |
| **MessageDelivery v1** | SendGrid/Twilio webhook processor | CRM notifications domain | Internal queue | `provider:enum`, `provider_message_id:string`, `recipient:string`, `status:enum`, `error_code:string?`, `occurred_at:datetime` | `provider`, `provider_message_id`, `recipient`, `status`, `occurred_at` | `provider ∈ {sendgrid, twilio}`; E.164 validation for SMS recipients | `schema_version` required, starting at `1` | Breaking changes require new topic suffix `.v2` |

## Authentication Methods

| Integration Surface | Auth Type | Credential Location | Header/Mechanism | Rotation Contract | Least-Privilege Contract | Audit Contract |
|---|---|---|---|---|---|---|
| Outbound Stripe API | Secret token | Secret manager (`STRIPE_SECRET_KEY`) | `Authorization: Bearer <token>` | Rotate every 90 days; dual-key overlap for 7 days | Restricted to payment and customer scopes required by CRM | All API key reads and changes logged in SIEM |
| Outbound SendGrid API | API key | Secret manager (`SENDGRID_API_KEY`) | `Authorization: Bearer <token>` | Rotate every 90 days | Key scoped to Mail Send only | Key usage tracked and anomaly alerts enabled |
| Outbound Twilio API | Basic credentials | Secret manager (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`) | HTTP Basic Auth | Rotate auth token every 90 days | Subaccount restricted to CRM messaging use case | Access and rotation events logged |
| Inbound Stripe webhooks | Signed request verification | Secret manager (`STRIPE_WEBHOOK_SIGNING_SECRET`) | `Stripe-Signature` HMAC verification | Rotate signing secret with coordinated cutover | Endpoint only accepts Stripe IP ranges where feasible and valid signatures always required | Signature failures logged with request metadata |
| Inbound Twilio webhooks | Signed request verification | Secret manager (`TWILIO_WEBHOOK_AUTH_TOKEN`) | `X-Twilio-Signature` validation | Rotate every 90 days | Endpoint locked to webhook-only route and POST method | Failed signature attempts alert security |
| Inbound SendGrid webhooks | Signed request verification | Secret manager (`SENDGRID_WEBHOOK_PUBLIC_KEY`) | Signed webhook header validation | Rotate public key as provider rotates key material | Verify signatures before parsing payload | Verification result persisted for audit |
| Inbound JazzCash callbacks | HMAC-SHA256 signature verification | Secret manager (`JAZZCASH_HASH_KEY`) | Verify `pp_SecureHash` field: compute HMAC-SHA256 over sorted non-empty request params concatenated as `key=value&` pairs using `JAZZCASH_HASH_KEY`; reject on mismatch with `400`; log rejection with request metadata | Rotate every 90 days with coordinated JazzCash portal update and dual-key overlap period | Endpoint locked to POST + JazzCash callback route only; no read access to business data | Signature failures logged with IP, payload hash, and timestamp |
| Inbound Easypaisa callbacks | HMAC-SHA256 signature verification | Secret manager (`EASYPAISA_STORE_ID`, `EASYPAISA_STORE_PASSWORD`) | Verify HMAC-SHA256 signature field in payload; reject on mismatch with `400`; log rejection | Rotate every 90 days; requires coordinated Easypaisa merchant portal update | Endpoint locked to POST + Easypaisa callback route only | Signature failures and rejection events logged |

---

## WhatsApp Provider Contracts

The CRM OS treats WhatsApp as its primary execution interface (not a side integration). All WhatsApp providers are accessed via the `MessagingAdapter` interface. The contracts below define the canonical integration surface per provider class.

### External APIs (WhatsApp)

| Integration | Purpose | Base URL | Endpoints Used | Method(s) | Auth Method | Retry/Timeout Contract | Owner |
|---|---|---|---|---|---|---|---|
| **Meta WhatsApp Business API** | Direct WhatsApp message send/receive | `https://graph.facebook.com/v18.0` | `/{phone-number-id}/messages`, `/{phone-number-id}/message_templates` | `POST`, `GET` | `Authorization: Bearer <SYSTEM_ACCESS_TOKEN>` | Retry on `429/5xx` with exponential backoff (max 3); timeout 10s | Communications Team |
| **Twilio WhatsApp** | WhatsApp via Twilio aggregator | `https://api.twilio.com` | `/2010-04-01/Accounts/{Sid}/Messages.json` | `POST` | HTTP Basic Auth (`AccountSid` + `AuthToken`) | Retry on `5xx` (max 3); timeout 8s | Communications Team |
| **360dialog WhatsApp** | Regional WhatsApp gateway (Pakistan) | `https://waba.360dialog.io/v1` | `/messages`, `/configs/webhook` | `POST`, `GET` | `D360-API-KEY` header | Retry on `429/5xx` (max 3); timeout 10s | Communications Team |
| **Gupshup WhatsApp** | Regional WhatsApp gateway (Pakistan) | `https://api.gupshup.io/sm/api/v1` | `/msg`, `/template/msg` | `POST` | `apikey` header | Retry on `429/5xx` (max 3); timeout 10s | Communications Team |

### Webhooks (WhatsApp)

| Webhook Source | Direction | Endpoint (CRM) | Event Types | Payload Contract | Verification Contract | Idempotency Contract | Failure Handling |
|---|---|---|---|---|---|---|---|
| **Meta WhatsApp Webhook** | External → CRM | `POST /webhooks/whatsapp/meta` | `messages`, `statuses` (sent/delivered/read/failed) | JSON with `object: "whatsapp_business_account"`, `entry[].changes[].value` containing messages array | Verify `X-Hub-Signature-256` using app secret; reject invalid with `403` | Deduplicate on `messages[].id` | Return `200` immediately; process async; dead-letter after 10 failures |
| **Twilio WhatsApp Callback** | External → CRM | `POST /webhooks/whatsapp/twilio` | `queued`, `sent`, `delivered`, `undelivered`, `failed`, `read` | Form-encoded `MessageSid`, `MessageStatus`, `To`, `From`, `ErrorCode?` | Validate `X-Twilio-Signature` | Deduplicate on `MessageSid` + `MessageStatus` | Retry internal processing; alert after 5 consecutive failures |
| **360dialog Webhook** | External → CRM | `POST /webhooks/whatsapp/360dialog` | inbound messages, delivery receipts | JSON `messages[]` with `id`, `from`, `type`, `timestamp`, `text/media` | Verify `D360-API-KEY` header matches stored secret | Deduplicate on `messages[].id` | Dead-letter on persistent failure; manual replay available |
| **Gupshup Webhook** | External → CRM | `POST /webhooks/whatsapp/gupshup` | inbound messages, delivery receipts | JSON with `app`, `timestamp`, `version`, `type`, `payload` | API key validation | Deduplicate on `payload.id` | Dead-letter on persistent failure |

**WhatsApp Webhook Deduplication Windows:**

| Provider | Dedup Key | Dedup Window TTL | Post-Window Behavior |
|---|---|---|---|
| Meta WhatsApp | `messages[].id` | 24 hours | After 24h, duplicate delivery is reprocessed (provider SLA guarantees no duplication beyond 24h) |
| Twilio WhatsApp | `MessageSid` + `MessageStatus` | 24 hours | After 24h, reprocessed — downstream idempotency keys prevent double execution |
| 360dialog | `messages[].id` | 24 hours | After 24h, reprocessed — domain idempotency guards apply |
| Gupshup | `payload.id` | 24 hours | After 24h, reprocessed — domain idempotency guards apply |

Dedup records are stored in `event_inbox` per `(tenant_id, event_name, event_id)` per `docs/global-idempotency.md §3.2`.

**360dialog and Gupshup Key Rotation:**

| Provider | Secret | Rotation Procedure | Overlap Strategy |
|---|---|---|---|
| 360dialog | `D360_API_KEY` in secret manager | 1. Generate new key in 360dialog partner portal. 2. Update secret manager with new key. 3. Deploy with dual-key check (accept both old and new key) for 15-minute overlap window. 4. Remove old key from secret manager after overlap. | 15-minute dual-accept window using `D360_API_KEY` + `D360_API_KEY_PREV` |
| Gupshup | `GUPSHUP_API_KEY` in secret manager | 1. Regenerate key in Gupshup dashboard. 2. Update secret manager. 3. Deploy immediately (Gupshup does not support dual-key; brief validation gap accepted). 4. Monitor for rejected callbacks during transition. | No overlap — immediate cutover with monitoring |

All WhatsApp webhooks are normalized by `MessagingAdapter.parseWebhook()` into canonical `MessageWebhookEvent` before any domain processing. See [`pakistan-adapter-architecture.md`](pakistan-adapter-architecture.md) for the `MessagingAdapter` interface contract.

---

## Pakistan Payment Provider Contracts

Pakistan payment providers are accessed via the `PaymentAdapter` interface. All payment amounts are in minor units (paisa for PKR). See [`pakistan-adapter-architecture.md`](pakistan-adapter-architecture.md) for the `PaymentAdapter` interface contract.

### External APIs (Pakistan Payments)

| Integration | Purpose | Base URL | Key Endpoints | Auth Method | Retry/Timeout Contract | Owner |
|---|---|---|---|---|---|---|
| **JazzCash API** | Mobile wallet + OTC payment collection (Pakistan) | `https://payments.jazzcash.com.pk` | `/CustomerPortal/transactionmanagement/merchantform/` (initiate), `/PaymentGatewayUserAuthenticationAPI/` (status) | HMAC-SHA256 request signing using `MerchantID` + `Password` + `HashKey` | Retry on `5xx`/timeout (max 3, exponential backoff); timeout 15s | Payments Team |
| **Easypaisa API** | Mobile wallet + over-the-counter payments (Pakistan) | `https://easypaisa.com.pk/paymentsapi` | `/initiate-transaction`, `/get-transaction-status` | OAuth2 client credentials (`store_id` + `store_password`); HMAC-SHA256 per request | Retry on `5xx`/timeout (max 3); timeout 15s | Payments Team |
| **Bank Transfer** | Direct bank account payment confirmation | N/A (manual upload / bank statement import) | Reconciliation via statement parser | API key for statement upload endpoint | N/A (batch import) | Finance Team |

### Webhooks (Pakistan Payments)

| Webhook Source | Direction | Endpoint (CRM) | Event Types | Payload Contract | Verification Contract | Idempotency Contract | Failure Handling |
|---|---|---|---|---|---|---|---|
| **JazzCash Callback** | External → CRM | `POST /webhooks/payments/jazzcash` | transaction success, failure, pending | Form-encoded or JSON: `pp_TxnRefNo`, `pp_ResponseCode`, `pp_Amount`, `pp_TxnDateTime`, `pp_SecureHash` | Verify `pp_SecureHash` HMAC-SHA256 against shared `HashKey`; reject on mismatch | Deduplicate on `pp_TxnRefNo` | Return `200` immediately; process async; dead-letter after 10 failures |
| **Easypaisa Callback** | External → CRM | `POST /webhooks/payments/easypaisa` | payment success, failure | JSON: `storeId`, `orderId`, `transactionId`, `transactionStatus`, `transactionAmount`, `transactionDateTime` | Verify HMAC-SHA256 signature field | Deduplicate on `transactionId` + `orderId` | Dead-letter on persistent failure; trigger reconciliation sweep |

All payment webhooks are normalized by `PaymentAdapter.parseWebhook()` into canonical `PaymentWebhookEvent` before domain processing.

### Data Contracts (Pakistan Payments)

| Contract Name | Producer | Consumer | Schema (Key Fields) | Versioning |
|---|---|---|---|---|
| **JazzCashPaymentStatus v1** | JazzCash webhook processor | CRM billing domain | `payment_ref:string`, `provider_txn_id:string`, `status:enum{SUCCESS,FAILED,PENDING}`, `amount_minor:int`, `currency:"PKR"`, `occurred_at:datetime` | `schema_version` required; enum expansion non-breaking |
| **EasypaisaPaymentStatus v1** | Easypaisa webhook processor | CRM billing domain | `payment_ref:string`, `provider_txn_id:string`, `status:enum{SUCCESS,FAILED,PENDING}`, `amount_minor:int`, `currency:"PKR"`, `occurred_at:datetime` | `schema_version` required; enum expansion non-breaking |

---

## Contract Governance Rules

| Rule | Requirement | Enforcement |
|---|---|---|
| No undefined integrations | Any new integration must be added to this document before implementation. Unknown providers are prohibited in runtime configuration. | CI check validates provider allowlist (`stripe`, `sendgrid`, `twilio`, `meta_whatsapp`, `twilio_whatsapp`, `360dialog`, `gupshup`, `jazzcash`, `easypaisa`) against this contract document. |
| Contracts must be explicit | Every integration must define endpoint(s), payload schema, auth mechanism, retry behavior, and versioning policy before deployment. | Architecture review gate and schema validation tests must pass prior to release. |
| Adapter interface compliance | All new payment and messaging providers must implement the `PaymentAdapter` or `MessagingAdapter` interface contract. Direct provider API calls from core services are forbidden. | Architecture test fails CI if core imports provider SDKs directly. |

---

## Forecasts API Endpoint

The `GET /api/v1/forecasts` endpoint is owned by the Opportunity Service and returns pipeline forecast aggregates.

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `GET` | `/api/v1/forecasts` | Return weighted pipeline forecast for current tenant | `reports.read` |
| `GET` | `/api/v1/forecasts?period=<YYYY-MM>` | Filter to specific calendar month | `reports.read` |

**Response shape:**
```json
{
  "data": {
    "period": "2026-05",
    "commit": { "amount": 0, "currency": "PKR", "count": 0 },
    "best_case": { "amount": 0, "currency": "PKR", "count": 0 },
    "pipeline": { "amount": 0, "currency": "PKR", "count": 0 },
    "weighted_pipeline": { "amount": 0, "currency": "PKR" }
  },
  "meta": { "request_id": "req_..." }
}
```

**Source:** `OpportunityPipelineSnapshotRM` read model. `weighted_pipeline` = sum of `amount × stage_probability` across all open opportunities. Stage probabilities: `qualification=10%`, `discovery=25%`, `proposal=50%`, `negotiation=75%`, `commit category=90%`.

---

## Plugin Framework

*Added from src/plugin_framework overlay — 2026-04-02*

The plugin framework provides a sandboxed extension mechanism. Plugins can register hooks, maintain isolated state, and read (but never mutate) a read-only view of core state.

### PluginManifest

Static plugin metadata used by the registry.

| Field | Notes |
|---|---|
| `plugin_id` | Globally unique plugin identifier |
| `display_name` | Human-readable plugin name |
| `version` | Semantic version string |

### HookExecutionContext

Execution context provided to hooks. `core_view` is read-only (`MappingProxyType`) — plugins cannot mutate core state. `plugin_state` is isolated and unique per plugin.

| Field | Notes |
|---|---|
| `plugin_id` | Plugin invoking the hook |
| `plugin_state` | Mutable dict scoped to the plugin |
| `core_view` | Immutable mapping of core state |

### PluginRecord

Runtime record for an installed plugin.

| Field | Notes |
|---|---|
| `manifest` | `PluginManifest` |
| `hooks` | Dict of `hook_name → tuple[HookHandler, ...]` |
| `state` | Plugin-private mutable state dict |

### Plugin Protocol

Contract all plugins must implement:

- `manifest` property → `PluginManifest`
- `hooks()` → `dict[str, tuple[HookHandler, ...]]`
- `on_install(context: HookExecutionContext) → None`
- `on_uninstall(context: HookExecutionContext) → None`

**Safety invariant:** `readonly_core_view(core_state)` wraps core state in `MappingProxyType` before passing to any plugin. No plugin can write to core state through this path.

---

## Integration Typed Entities (Webhook Delivery + Communication)

*Added from src/external_apis_webhooks and src/communication_integrations overlay — 2026-04-02*

### Outbound/Inbound Request Entities

| Entity | Fields |
|---|---|
| `OutboundRequest` | `provider (ProviderName)`, `endpoint_key`, `payload (dict)`, `account_sid (nullable)` |
| `OutboundResponse` | `provider`, `status_code`, `body (dict)` |
| `InboundWebhook` | `provider`, `headers (dict)`, `payload (dict or list[dict])` |

**ProviderName values:** `stripe | sendgrid | twilio`

### WebhookSubscription

| Field | Notes |
|---|---|
| `subscription_id` | PK |
| `target_url` | Delivery endpoint |
| `event_names` | Tuple of subscribed event names |
| `is_active` | Boolean toggle |
| `max_attempts` | Default 10 delivery attempts |

### WebhookDelivery

Tracks per-delivery attempt state with retry.

| Field | Notes |
|---|---|
| `delivery_id` | PK |
| `subscription_id` | FK→WebhookSubscription |
| `event_name` | Event being delivered |
| `target_url` | Resolved at delivery time |
| `payload` | Event payload dict |
| `max_attempts` | Inherited from subscription |
| `attempt_count` | Current attempt count |
| `status` | `pending \| failed \| delivered \| dead_lettered` |
| `last_error` | Last error message (nullable) |

### CommunicationThread / CommunicationMessage

Integration-layer typed projections of `MessageThread` / `Message` used when routing through SendGrid/Twilio providers.

**CommunicationThread** — fields: `message_thread_id`, `tenant_id`, `channel_type`, `provider`, `provider_thread_key`, `linked_entity_type`, `linked_entity_id`, `subject`, `participants`, `status`, `created_at`, `updated_at`

**CommunicationMessage** — fields: `message_id`, `tenant_id`, `message_thread_id`, `provider`, `provider_message_id`, `channel_type`, `direction`, `sender`, `recipient`, `body`, `status`, `linked_entity_type`, `linked_entity_id`, `sent_at`, `delivered_at (nullable)`

**SUPPORTED_PROVIDERS:** `sendgrid | twilio`
**SUPPORTED_CHANNELS:** `email | sms | whatsapp | message`
**SUPPORTED_ENTITY_TYPES (linked entities):** `lead | contact | ticket`
