<!-- OWNERSHIP
PRIMARY FOR: System overview narrative, capability boundaries, high-level non-functional requirements.
DEFERS TO: data-architecture.md (CQRS-lite detail); pakistan-adapter-architecture.md (L1/L2/L3 layer model); docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md (architecture decisions — that is the governance authority for architectural decisions).
DO NOT RE-DEFINE: CQRS-lite mechanics → data-architecture.md §2.1; L1/L2/L3 adapter layers → pakistan-adapter-architecture.md §1; architectural decisions → ADR-001_PROJECT_FOUNDATION.md.
CROSS-REFERENCE (DUP-006, 2026-06-21): docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md is the designated authority for architecture decisions (3-tier architecture, tech stack, deployment model). This file is the narrative Supporting Reference. When architecture changes occur, update ADR-001_PROJECT_FOUNDATION.md first.
-->

# Architecture Overview

## 1) System Architecture Style

**Layered + Engine-driven + Adapter-based**

The CRM OS is structured around three mutually reinforcing patterns:
- **Layered**: strict dependency direction (L1 → L2 only; L3 → L2 only)
- **Engine-driven**: reusable engines owned by the platform, consumed by all domains
- **Adapter-based**: country/provider-specific logic fully isolated behind interface contracts

---

## 2) Layer Model

```
┌──────────────────────────────────────────────────────────────┐
│  L1 — CORE (country-agnostic)                                │
│  ─────────────────────────────────────────────────────────── │
│  Domain Models · Business Services · Workflow Logic          │
│  Orchestration Logic · Engine Implementations                │
│                                                              │
│  Rule: Contains ZERO country-specific conditions             │
└────────────────────────┬─────────────────────────────────────┘
                         │ depends on
┌────────────────────────▼─────────────────────────────────────┐
│  L2 — INTERFACES                                             │
│  ─────────────────────────────────────────────────────────── │
│  MessagingAdapter · PaymentAdapter · ComplianceAdapter       │
│  PhoneFormatter · LocaleAdapter · AdapterError taxonomy      │
│                                                              │
│  Rule: Stable contracts. Core depends ONLY on these.         │
└────────────────────────┬─────────────────────────────────────┘
                         │ implements
┌────────────────────────▼─────────────────────────────────────┐
│  L3 — ADAPTERS (country/provider-specific)                   │
│  ─────────────────────────────────────────────────────────── │
│  adapters/pakistan/payment/   — JazzCash, Easypaisa          │
│  adapters/pakistan/messaging/ — 360dialog, Gupshup           │
│  adapters/pakistan/compliance/ — PTA, FBR hooks (optional)   │
│  adapters/pakistan/localization/ — PKR, PK phone, locale     │
│                                                              │
│  Rule: Adapters may import L2 + provider SDKs.               │
│  Rule: Core NEVER imports L3.                                │
└──────────────────────────────────────────────────────────────┘
```

### Dependency Rules (Non-Negotiable)

| Allowed | Forbidden |
|---|---|
| `core/*` → `adapters/interfaces/*` | `core/*` → `adapters/pakistan/*` |
| `adapters/pakistan/*` → `adapters/interfaces/*` | `domain/*` containing provider/country enums |
| `adapters/pakistan/*` → provider SDKs | Any adapter importing another country adapter |

See [`pakistan-adapter-architecture.md`](../adapters/pakistan-adapter-architecture.md) for the full adapter model and extensibility guide.

---

## 3) Engine Registry

Six platform-owned engines are available to all domains. No domain may reimplement engine logic.

| Engine | Role | Key Guarantees | Doc |
|---|---|---|---|
| **WhatsApp Engine** | Primary interaction layer; inbound/outbound messaging, conversation threading, contact mapping | Idempotent webhook processing, canonical message status, provider abstraction | [`whatsapp-execution-model.md`](../adapters/whatsapp-execution-model.md) |
| **Follow-up Engine** | Schedules, enforces, and escalates follow-up tasks | No lead idles beyond threshold; 4-level escalation ladder; anti-bypass controls | [`followup-enforcement-model.md`](../domain/followup-enforcement-model.md) |
| **Collections Engine** | Invoice lifecycle, payment tracking, reminder automation, reconciliation | 98% match rate target; DSO reduction; 99.5% reminder SLA | [`collections-engine-model.md`](../domain/collections-engine-model.md) |
| **Activity Control Engine** | Immutable activity log, ownership tracking, audit trail | Append-only chain with hash verification; mandatory on every CRM entity action | [`activity-control-model.md`](../domain/activity-control-model.md) |
| **Activation Engine** | Zero-setup onboarding, auto pipeline creation, early-success event | Value delivered within 10 minutes; aha event = first WhatsApp + first deal stage move | [`activation-model.md`](../product/activation-model.md) |
| **Execution Control Plane** | Idempotency, retry with backoff, ACID boundaries, concurrency control | Idempotency key `(tenant_id, method, route, key)`; OCC default + pessimistic escalation | [`execution-hardening.md`](../infrastructure/execution-hardening.md) |

---

## 4) Service Architecture

40 services organized in three tiers (updated 2026-05-30: AI & Predictive Models Service added for Sprint 5B-7):

| Tier | Count | Examples |
|---|---|---|
| **Core** | ~6 | API Gateway, Identity & Access, Organization & Tenant, Workflow Automation |
| **Domain** | ~16 | Lead Management, Contact, Opportunity, Quote, Billing & Subscription, Case Management, AI & Predictive Models |
| **Platform** | ~12 | Event Bus, Job Scheduler, Feature Flag, Audit & Compliance, Data Warehouse |

Ownership is non-overlapping: each capability has exactly one owning service.

See [`service-map.md`](service-map.md) for the full service catalog and [`capability-matrix.md`](capability-matrix.md) for capability-to-service mapping.

---

## 5) Data Flow Architecture

```
Inbound (WhatsApp / API / Web)
  └─→ API Gateway (auth, rate limiting, routing)
        └─→ Domain Services (business logic, state transitions)
              ├─→ Event Bus (async domain events)
              │     ├─→ Workflow Automation Service
              │     ├─→ Activity Timeline Service
              │     ├─→ Analytics & Reporting Service
              │     └─→ Notification Orchestrator
              └─→ Write DB (tenant-scoped relational store)
                    └─→ Read Models (denormalized projections for dashboards)
```

CQRS-lite pattern: services own write schemas; read models are built from domain events for query/reporting surfaces.

---

## 6) Multi-Tenancy Model

- Every entity carries `tenant_id` as a scoping field
- Hard isolation: no cross-tenant data access at any layer
- Tenant configuration (entitlements, feature flags, regional settings) managed by Organization & Tenant Service

See [`org-multi-tenancy.md`](../security/org-multi-tenancy.md) and [`identity-auth-rbac.md`](../security/identity-auth-rbac.md).

---

## 7) Integration Architecture

The system connects to external providers via the adapter pattern (L3) and validated integration contracts:

| Category | Providers | Contract Doc |
|---|---|---|
| Messaging (WhatsApp) | Meta Business API, Twilio WhatsApp, 360dialog, Gupshup | [`integration-contracts.md`](../infrastructure/integration-contracts.md) |
| Payments (Pakistan) | JazzCash, Easypaisa, Bank Transfer | [`integration-contracts.md`](../infrastructure/integration-contracts.md) |
| Payments (Global) | Stripe | [`integration-contracts.md`](../infrastructure/integration-contracts.md) |
| Email | SendGrid | [`integration-contracts.md`](../infrastructure/integration-contracts.md) |
| SMS | Twilio | [`integration-contracts.md`](../infrastructure/integration-contracts.md) |

---

## 8) Critical End-to-End Flows

Four flows must operate end-to-end with no data loss:

```
Flow 1: WhatsApp → Lead → Follow-up → Close
Flow 2: Lead → Invoice → Payment → Reconciliation
Flow 3: Follow-up → Escalation → Reassignment
Flow 4: Offline Action → Sync → Consistent State
```

See [`BACKEND-QC.md`](../../BACKEND-QC.md) (integration flow validation — consolidated) and [`offline-sync.md`](../infrastructure/offline-sync.md).

---

## 9) Architecture Validation

Architecture purity is enforced at CI level:
- Static import lint rules block `core → adapters/pakistan` imports
- Contract test suite runs against all country adapters
- Final supervisor QC validates cross-domain consistency on every build

See [`BACKEND-QC.md`](../../BACKEND-QC.md) (architecture purity QC — consolidated).
