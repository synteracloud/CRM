Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: AI

# SERVICE_CATALOG.md
> Source: backend/services/ (all service directories), backend/services/app.py, backend/src/ (34 domain modules)

---

## 1. Python Service Layer (backend/services/)

These are the active cross-cutting service singletons instantiated at FastAPI startup.

---

### FollowupEnforcementEngine
**Path:** `backend/services/followup/engine.py`
**Purpose:** Authoritative engine for mandatory follow-up ownership enforcement. Schedules, escalates, and suggests next actions for leads. Implements the 3-phase ramp-up model.
**Key classes:** `FollowupEnforcementEngine`, `FollowupJobQueue`, `FollowupPolicy`, `NextActionSuggestion`
**Key methods:**
- `register_lead(lead_snapshot)` — registers a new lead for enforcement tracking
- `schedule_followup(lead_id, due_at)` — creates a canonical pending follow-up task
- `complete_followup(task_id)` — marks task complete (idempotent)
- `snooze_followup(task_id, snoozed_until)` — reschedules task
- `suggest_next_action(lead_id)` → `NextActionSuggestion` — rule-based suggestion (call/send_whatsapp/send_reminder/escalate/close)
- `enforcement_level_for_tenant_age(tenant_created_at)` → "soft"|"medium"|"strict"
**Enforcement levels:**
- soft (days 0–14): warnings only, closure gate advisory
- medium (days 15–30): warnings + owner alerts, closure gate prompts
- strict (day 31+): full enforcement, hard-block, auto-reassignment
**HTTP routes served:**
- Internal: GET /internal/leads/{id}/next-action, POST /internal/leads/{id}/register, POST /internal/process-due, GET /internal/metrics
- Public: /api/v1/followups (via followup_public_router)
**Consumers:** Gateway (v1-leads.routes.js calls POST /internal/leads/:id/register on lead creation; GET /leads/:id/next-action proxies to /internal/leads/:id/next-action)

---

### CollectionsService
**Path:** `backend/services/collections/service.py`
**Purpose:** Invoice/payment/reconciliation lifecycle engine. Integrates with payment adapters (JazzCash, Easypaisa) for callback ingestion.
**Key classes:** `CollectionsService`, `CollectionsAutomationEngine`, `ReminderScheduler`, `InMemoryPaymentEventStore`, `InMemoryPaymentLedgerStore`
**Dependencies:** `PaymentAdapter` protocol (jazzcash, easypaisa adapters), `EventStore`, `LedgerStore`, `TransactionManager`
**Key methods:**
- `create_invoice(invoice)` — validates uniqueness, normalizes state
- `get_invoice(invoice_id)` — retrieves invoice
- `ingest_payment(provider, signature, payload)` — verifies HMAC, normalizes via adapter, deduplicates by provider_txn_id, creates payment record
- `reconcile()` — runs reconciliation pass comparing amount_paid vs amount_due
- `list_invoice_reminders(invoice_id)` — returns scheduled reminder times via ReminderScheduler
**HTTP routes served:**
- Internal: POST /internal/payments, GET /internal/invoices/{id}, POST /internal/invoices/overdue-rollup
- Public: /api/v1/invoices, /api/v1/payments/callback
**Consumers:** Gateway (v1-collections.routes.js proxies via GATEWAY_UPSTREAM_BASE_URL); payment webhook handlers

---

### ActivityControlEngine
**Path:** `backend/services/activity/engine.py`
**Purpose:** Activity timeline control — logs and retrieves activity events across CRM entities.
**HTTP routes served:**
- Internal: GET /internal/chain-check
- Public: /api/v1/activities
**Consumers:** Gateway (v1-activities.routes.js)

---

### ConversationService (inline in conversation module)
**Path:** `backend/services/conversation/`
**Purpose:** WhatsApp message classification and conversation state management.
**Key responsibilities:**
- Classifies inbound messages by intent (payment_query/follow_up_response/lead_inquiry/support_request)
- Manages conversation state (open/resolved/closed)
- Routes messages to appropriate handlers
**HTTP routes served:**
- Internal: POST /internal/classify, POST /internal/messages
- Public: /api/v1/webhooks/whatsapp, /api/v1/conversations

---

### SyncService
**Path:** `backend/services/sync/service.py`
**Purpose:** Offline-first sync command queue processing. Handles entity sync batches from field devices.
**HTTP routes served:**
- Internal: POST /internal/sync/batch, GET /internal/sync/status, GET /internal/sync/queue
- Public: /api/v1/sync (via v1-sync.routes.js in gateway)
**Consumers:** Gateway (v1-sync.routes.js)

---

### ActivationOrchestrator
**Path:** `backend/services/activation/service.py`
**Purpose:** Tenant pipeline seeding on registration. Seeds default workflows, pipeline stages, and configuration for a new tenant.
**HTTP routes served:** /api/v1/activation (activation_public_router)
**Called by:** Gateway on POST /auth/register → fires POST /internal/activation/seed

---

### ExecutionControlPlane
**Path:** `backend/services/core/execution/control_plane.py`
**Purpose:** Cross-cutting execution infrastructure combining idempotency, concurrency control, retry, transaction management, and recovery queue.
**Components:**
- `GlobalIdempotencyLedger` — thread-safe in-memory idempotency tracking with scope key (tenant_id, method, route, key)
- `ConcurrencyController` — prevents race conditions on shared resources
- `RetryExecutor` + `RetryPolicy` — configurable retry with backoff
- `TransactionManager` — unit-of-work patterns
- `RecoveryQueue` — queues failed operations for retry
**HTTP routes served:** /api/v1/admin/dead-letters (dlq_public_router)

---

### AIService
**Path:** `backend/services/ai/service.py` + `backend/services/ai/entities.py`
**Purpose:** Stateless AI domain service. All methods are pure rule-based computations.
**Key methods:**
- `score_lead(lead_data, previous_score, tenant_id)` — computes weighted-sum score 0-100
- `predict_churn(account_data)` — computes churn probability 0-1
- `estimate_clv(account_data)` — estimates customer lifetime value in PKR
- `classify_query_intent(query)` — regex-based NL intent classification
**Scoring models** (all rule_based, no ML inference):
- `lead_score_v1`: 7 weighted features (deal_stage 28%, follow_up_count 18%, estimated_value 14%, days_since_last_contact 12%, email_open_rate 8%, activity_recency 8%, whatsapp_engagement 12%)
- `churn_predict_v1`: rule-based churn probability
- `clv_estimate_v1`: rule-based CLV estimation
**HTTP routes served:** /api/v1/ai/* (ai_public_router)
**Note:** No ML inference provider (OpenAI/Anthropic/Google) — all models are rule-based

---

### Daily Summary Scheduler
**Path:** `backend/services/summary/daily_summary.py` (called from services/app.py)
**Purpose:** Background asyncio task sending daily WhatsApp summary to managers. Fires once per day at DAILY_SUMMARY_UTC_HOUR (default 03:00 UTC = 08:00 PKT).
**Behavior:** Uses date-keyed sentinel to prevent duplicate sends. Dry-run mode when DAILY_SUMMARY_ENABLED=false or messaging engine not configured.

---

### Overdue Scanner
**Path:** `backend/services/followup/overdue.py` (called from services/app.py)
**Purpose:** Background asyncio task polling every 60 seconds. Marks pending follow-up tasks past `due_at` as `overdue` in the DB.

---

### GlobalIdempotencyLedger + EvictionWorker
**Path:** `backend/services/core/execution/idempotency.py`, `backend/services/core/execution/eviction_worker.py`
**Purpose:** Thread-safe in-memory idempotency ledger for Python service layer. Scoped by (tenant_id, method, route, idempotency_key). EvictionWorker daemon thread evicts expired records every IDEMPOTENCY_EVICT_INTERVAL seconds (default 3600).

---

## 2. Domain Modules (backend/src/ — 34 modules)

Each module follows the pattern: `api.py` (FastAPI router), `services.py` (business logic), `entities.py` (Pydantic schemas + DB models).

| Module | Path | Purpose |
|---|---|---|
| admin_control_center | src/admin_control_center/ | Admin panel operations, compliance settings |
| ai_copilot | src/ai_copilot/ | NL query copilot, suggestion management |
| ai_scoring | src/ai_scoring/ | Lead/opportunity scoring models, feature weights |
| automation_journeys | src/automation_journeys/ | Journey definition and execution |
| campaigns | src/campaigns/ | Campaign + segment management |
| communication_integrations | src/communication_integrations/ | WhatsApp/email integration config management |
| contract_lifecycle_management | src/contract_lifecycle_management/ | Contract entities — 12 endpoints in api.py API_ENDPOINTS dict; no gateway route in C6 (OA-005 AUTO-CLOSED — deferred to C7) |
| custom_object_framework | src/custom_object_framework/ | Custom object type definition |
| custom_objects | src/custom_objects/ | Custom object instance CRUD |
| data_deduplication_engine | src/data_deduplication_engine/ | Contact/lead deduplication logic |
| design_system | src/design_system/ | UI component/theme configuration |
| event_bus | src/event_bus/ | Internal event dispatch and subscription |
| execution_hardening | src/execution_hardening/ | Hardened execution primitives |
| external_apis_webhooks | src/external_apis_webhooks/ | External API/webhook management |
| knowledge_base | src/knowledge_base/ | Knowledge article CRUD, publish workflow |
| lead_management | src/lead_management/ | Lead entity, assignment, stage transitions, history |
| marketing_admin_workflow_ui | src/marketing_admin_workflow_ui/ | Marketing admin operations |
| omnichannel_inbox | src/omnichannel_inbox/ | Unified inbox management |
| partner_channel_management | src/partner_channel_management/ | Partner + commission management |
| plugin_framework | src/plugin_framework/ | Plugin registration and lifecycle |
| predictive_forecasting | src/predictive_forecasting/ | Revenue/pipeline forecast generation |
| predictive_models | src/predictive_models/ | ML/rule-based model orchestration |
| reporting_dashboards | src/reporting_dashboards/ | Report definition and execution |
| revenue_recognition | src/revenue_recognition/ | Revenue recognition rules and ledger |
| role_based_ui | src/role_based_ui/ | User/role management |
| rule_engine | src/rule_engine/ | CPQ approval rules, pricing rules |
| sales_cockpit | src/sales_cockpit/ | Opportunity/pipeline management |
| subscription_billing | src/subscription_billing/ | Subscription lifecycle |
| support_console | src/support_console/ | Support team management, queue routing |
| territory_management | src/territory_management/ | Territory hierarchy, rule-based routing |
| ticket_management | src/ticket_management/ | Case/ticket entities, SLA, escalation |
| usage_billing | src/usage_billing/ | Usage-based billing tracking |
| workflow_engine | src/workflow_engine/ | Workflow DSL execution |
| customer_360_cdp | src/customer_360_cdp/ | Contact/account unified profile |

**Note:** `custom_object_framework` and `custom_objects` modules exist in `src/` but no gateway route file (`v1-custom-objects.routes.js`) was found. RESOLVED Phase 3.25 (D-002 CLOSED): K-02 (object-builder.html) is a C6 advisory shell — no gateway route is needed. Backend route will be added in C7 when live connectivity is activated.

---

## 3. Cross-Cutting Infrastructure Services

### PostgreSQL Connection Pool (gateway)
**Path:** `backend/gateway/db/pool.js`
**Configuration:** `DATABASE_URL` env var. Used by gateway route handlers for direct SQL queries.

### PostgreSQL / SQLAlchemy (FastAPI)
**Path:** `backend/services/db/__init__.py`
**Configuration:** `DATABASE_URL` env var (default: postgresql+psycopg2://crm:changeme@localhost:5432/crm)
**Pool settings:** `pool_pre_ping=True` (validates connections before use)
**Session pattern:** `sessionmaker(autocommit=False, autoflush=False)` — explicit transaction management

### Redis Client (gateway)
**Path:** `backend/gateway/config/redis-client.js`
**Purpose:** Rate limiting (rl: namespace), OTP storage (otp: namespace), JTI revocation (rt: namespace), feature flag cache (ff: namespace)
**Fallback:** ioredis-mock in-process when REDIS_URL not set
**Connection:** ioredis with connectTimeout=5000ms, maxRetriesPerRequest=3, enableOfflineQueue=true
**Fail-open:** Redis errors fall back to allowing requests through

### JTI Blocklist (gateway)
**Path:** `backend/gateway/middleware/jti-blocklist.js`
**Purpose:** In-memory Set of revoked JWT IDs. `addRevoked(jti)` called on logout. `isRevoked(jti)` checked on every authenticated request.
**Note:** In-memory — revocations do not survive gateway restarts. Redis-backed revocation deferred to Post-C6 Auth Sprint (OA-002 SAFE-DEFAULT, G-CRIT-001). See BACKEND_GAP_REGISTER.md.

---

*End SERVICE_CATALOG.md*
