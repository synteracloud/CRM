# Integration Contracts

This document defines all approved integration contracts for the CRM platform.

## External APIs

| Integration | Purpose | Base URL | Endpoints Used | Method(s) | Request Contract | Response Contract | Auth Method | Retry/Timeout Contract | Owner |
|---|---|---|---|---|---|---|---|---|---|
| **Stripe API** | Payment intents, subscription status sync | `https://api.stripe.com` | `/v1/payment_intents`, `/v1/customers`, `/v1/subscriptions` | `GET`, `POST` | Form-encoded fields per endpoint (`customer`, `amount`, `currency`, `metadata[crm_account_id]`) | JSON objects including `id`, `status`, `customer`, `amount`, `currency` | Server-side secret key via `Authorization: Bearer <STRIPE_SECRET_KEY>` | Retry on `429/5xx` with exponential backoff (max 3); timeout 10s | Billing Team |
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
| **CustomerSync v1** | CRM | Stripe integration worker | Internal event bus | `customer_id:string`, `email:string`, `full_name:string`, `billing_address:object`, `updated_at:datetime` | `customer_id`, `email`, `updated_at` | `email` must be RFC 5322 compliant; `updated_at` in ISO-8601 UTC | `contract_version: "1.0"` field required in envelope | New required fields require v2; v1 maintained for 90 days |
| **PaymentStatus v1** | Stripe webhook processor | CRM billing domain | Internal queue | `payment_intent_id:string`, `crm_account_id:string`, `status:enum`, `amount_minor:int`, `currency:string`, `occurred_at:datetime` | All fields required | `status ∈ {succeeded, processing, failed, canceled}`; `amount_minor > 0` | Semantic version in envelope, default `1.0` | Enum expansion is non-breaking; field removal is breaking |
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

## Contract Governance Rules

| Rule | Requirement | Enforcement |
|---|---|---|
| No undefined integrations | Any new integration must be added to this document before implementation. Unknown providers are prohibited in runtime configuration. | CI check validates provider allowlist (`stripe`, `sendgrid`, `twilio`) against this contract document. |
| Contracts must be explicit | Every integration must define endpoint(s), payload schema, auth mechanism, retry behavior, and versioning policy before deployment. | Architecture review gate and schema validation tests must pass prior to release. |
