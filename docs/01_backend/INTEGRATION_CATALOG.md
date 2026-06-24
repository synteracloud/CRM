Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: Shared

# INTEGRATION_CATALOG.md
> Source: backend/gateway/routes/v1-whatsapp-webhooks.routes.js, backend/gateway/routes/v1-payment-webhooks.routes.js, backend/gateway/routes/v1-auth.routes.js, backend/gateway/config/redis-client.js, backend/services/db/__init__.py, AUTHORITY_RECONSTRUCTION_REPORT.md §7

---

## 1. WhatsApp Integrations

### Meta (WhatsApp Business API — official)
**Provider:** Meta Platforms
**Adapter path:** `backend/src/adapters/pakistan/messaging/meta_api_adapter.py` (confirmed in code)
**Status:** Adapter implemented; live activation requires META_WHATSAPP_TOKEN and phone number ID
**Webhook endpoint (inbound):**
- `GET /api/v1/whatsapp-webhooks/meta` — Meta webhook verification (returns hub.challenge)
- `POST /api/v1/whatsapp-webhooks/meta` — Inbound messages (HMAC-SHA256 signature verification via rawBody)
**Message flow:**
1. Meta sends POST to webhook URL with message payload
2. Gateway verifies HMAC signature
3. Payload forwarded to conversation service for classification
4. Classified by intent (payment_query/follow_up_response/lead_inquiry/support_request)
5. Conversation state updated; inbound message stored in messaging_db

### Twilio (WhatsApp channel via Twilio)
**Adapter path:** `backend/src/adapters/pakistan/messaging/twilio_adapter.py`
**Status:** Adapter implemented
**Webhook:** `POST /api/v1/whatsapp-webhooks/twilio`

### 360dialog
**Adapter path:** `backend/src/adapters/pakistan/messaging/dialog360_adapter.py`
**Status:** Adapter implemented
**Webhook:** `POST /api/v1/whatsapp-webhooks/360dialog`

### Gupshup
**Adapter path:** `backend/src/adapters/pakistan/messaging/gupshup_adapter.py`
**Status:** Adapter implemented
**Webhook:** `POST /api/v1/whatsapp-webhooks/gupshup`

**Active provider selection:** CONFIRMED (Phase 3.25): `MESSAGING_PROVIDER` environment variable — accepts `"meta" | "twilio" | "360dialog" | "gupshup"` (default: `"meta"`). Resolved at deployment via `backend/adapters/pakistan/bootstrap/registry.py` `resolve_adapters()`. Provider is deployment-wide (all tenants use same provider on single-instance C6 deployment).

**WhatsApp use cases in the system:**
- Inbound lead capture (conversations classified as lead_inquiry)
- Follow-up reminders sent to contacts
- Invoice payment reminders (collections_reminder workflow)
- Daily summary to managers (daily_summary_scheduler)
- Outbound from inbox (POST /inbox/conversations/:id/messages)
- Campaign broadcasts (campaign type: whatsapp_broadcast)
- Urdu template support (P-017 blocker — requires native speaker approval)

---

## 2. Payment Integrations

### JazzCash
**Adapter path:** `backend/src/adapters/pakistan/payments/jazzcash.py`
**Status:** STUB — `stub_mode=True` confirmed in render.yaml (`JAZZCASH_STUB_MODE=true`)
**Blocker:** P-016 — live credentials not obtained
**Webhook:** `POST /api/v1/payment-webhooks/jazzcash` (HMAC signature verification)
**Integration pattern:**
1. Payment initiated via POST /payments with method=jazzcash
2. Adapter generates payment initiation request in JazzCash API format
3. In stub mode: returns synthetic success response without calling JazzCash API
4. JazzCash posts callback to /payment-webhooks/jazzcash on payment completion
5. HMAC signature verified; payment event ingested by CollectionsService
**Production requirements:** JAZZCASH_MERCHANT_ID, JAZZCASH_PASSWORD, JAZZCASH_HASH_KEY

### Easypaisa
**Adapter path:** `backend/src/adapters/pakistan/payments/easypaisa.py`
**Status:** STUB — `stub_mode=True` confirmed in render.yaml (`EASYPAISA_STUB_MODE=true`)
**Blocker:** P-016 — live credentials not obtained
**Webhook:** `POST /api/v1/payment-webhooks/easypaisa`
**Integration pattern:** Same as JazzCash above
**Production requirements:** EASYPAISA_MERCHANT_ID, EASYPAISA_STORE_ID, EASYPAISA_HASH_KEY

### Bank Transfer
**Status:** Supported as payment method type in payment schema (`payment_method_type: bank_transfer`)
**No external integration:** Bank transfers are recorded manually or via proof upload (POST /collections/invoices/:id/payments/:id/proof)

---

## 3. Email Integration (SendGrid)

**Provider:** SendGrid (Twilio)
**Source:** `backend/gateway/routes/v1-auth.routes.js` (sendEmail function, lines 62-93)
**Status:** Conditional — live when `SENDGRID_API_KEY` env var is set. In development: logs stub output only.
**Endpoint used:** SendGrid v3 Mail Send API (`POST https://api.sendgrid.com/v3/mail/send`)
**From address:** `SENDGRID_FROM` env var (default: `noreply@crm.pk`)
**Timeout:** 5000ms
**Current use cases:**
1. OTP email (forgot-password flow): Subject + OTP code body
2. Welcome email (post-registration): CONFIRMED IMPLEMENTED (Phase 3.25) — v1-auth.routes.js line 383: `sendEmail(email, 'Welcome to Pakistan CRM', ...)` called during POST /auth/register after activation engine call.
**Content type:** `text/plain` only (no HTML templates in SendGrid calls confirmed)
**Error handling:** Fire-and-forget on success; rejects on SendGrid API error or timeout
**Configuration required for production:**
- `SENDGRID_API_KEY` — SendGrid API key with Mail Send permission
- `SENDGRID_FROM` — verified sender email address

---

## 4. Redis

**Provider:** Render.com managed Redis (production); ioredis-mock in-process (development)
**Source:** `backend/gateway/config/redis-client.js`
**Connection URL:** `REDIS_URL` env var
**Client library:** `ioredis` npm package
**Connection settings:** connectTimeout=5000ms, maxRetriesPerRequest=3, enableOfflineQueue=true

**Use cases and key namespaces:**

| Use Case | Key Pattern | TTL |
|---|---|---|
| Rate limiting | `rl:{tenant_id}:{user_sub}:{METHOD}:{canonical_path}` | 60 seconds (sliding window) |
| OTP storage | `otp:{tenant_id}:{email}` | 15 minutes |
| Refresh token tracking | `rt:{jti}` | 7 days |
| Feature flag cache | `ff:{tenant_id}:{flag_key}` | Not confirmed in code — likely not implemented in C6; feature flags served directly from DB |
| JTI blocklist | In-memory Set (not Redis) in current implementation | In-process only |

**Degradation behavior:** If Redis is unavailable, rate limiting falls back to in-process Map and requests are allowed through (fail-open, not fail-closed). This prevents infrastructure failure from blocking the application.

---

## 5. PostgreSQL

**Version:** PostgreSQL 14 (from render.yaml)
**Provider:** Render.com managed PostgreSQL (production); local Docker (development)
**Connection URL:** `DATABASE_URL` env var

**Gateway connection:**
- Node.js `pg` package via `backend/gateway/db/pool.js`
- Connection pool settings: CONFIRMED (Phase 3.25, G-LOW-001 CLOSED): `DB_POOL_MAX` env var (default 10), `DB_POOL_IDLE_MS` (default 10000ms), `DB_POOL_CONN_TIMEOUT` (default 5000ms) — all configurable via render.yaml env vars

**FastAPI connection:**
- SQLAlchemy with `psycopg2` driver (`postgresql+psycopg2://...`)
- `pool_pre_ping=True` — validates connections before use
- `sessionmaker(autocommit=False, autoflush=False)` — explicit transactions
- Single engine instance (module-level singleton)

**Database organisation:** 18 domain schemas in a single PostgreSQL instance (CONFIRMED from render.yaml: single `crm-postgres` service). All 18 schemas (`CREATE SCHEMA IF NOT EXISTS ...`) reside in the same DB instance. Schema separation provides logical isolation; no physical separation.

---

## 6. GitHub Actions / CI

**Configuration:** `.github/workflows/ci.yml`
**Status:** Configured — 11 jobs defined (confirmed from AUTHORITY_RECONSTRUCTION_REPORT.md §12)
**Purpose:** Automated testing on push/PR

---

## 7. Render.com (Deployment)

**Configuration:** `render.yaml`
**Services deployed:**
- `crm-gateway` — Express.js gateway
- `crm-python-services` — FastAPI service
- `crm-frontend` — Static HTML frontend
- Render managed PostgreSQL
- Render managed Redis (`crm-redis`)
**Region:** Singapore (closest to Pakistan)

---

## 8. Integrations NOT Implemented

| Integration | Status | Notes |
|---|---|---|
| AI inference (OpenAI/Anthropic/Google) | NOT IMPLEMENTED | No provider SDK in requirements.txt. All models are rule_based. |
| SMS (non-WhatsApp) | NOT IMPLEMENTED | No SMS gateway adapter found |
| CRM data sync (Salesforce/HubSpot) | NOT IMPLEMENTED | v1-sync.routes.js handles internal sync only |
| ERP integration | NOT IMPLEMENTED | No ERP adapter found |
| Stripe/PayPal | NOT IMPLEMENTED | Only JazzCash and Easypaisa (Pakistan-specific) |

---

*End INTEGRATION_CATALOG.md*
