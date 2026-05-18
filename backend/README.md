# Execution-First CRM OS

## System Identity

**System Name:** Execution-First CRM OS
**System Type:** Operational Execution Platform (not a traditional CRM)

**Core Purpose:**
Manage and enforce the complete business execution lifecycle:

```
Lead → Follow-up → Close → Invoice → Payment → Reconciliation
```

**Primary Goal:** Ensure no revenue opportunity is lost due to lack of execution.

---

## Market Positioning

This is **not** CRM software.

This is a **Business Execution System** — built for Pakistan's SMB market where leads are lost in WhatsApp, follow-ups are forgotten, and cash position is unknown until it's too late.

**Three core guarantees:**

> 1. **Never lose a lead** — every WhatsApp message becomes a tracked contact. No prospect falls through the cracks.
> 2. **Never miss a follow-up** — the system auto-schedules, enforces, and escalates every follow-up commitment.
> 3. **Always know your cash position** — invoices, payments (cash and digital), and collections are tracked in real time.

---

## Design Principles

### Architecture Principles
1. **Execution over Data Storage** — the system enforces execution, not just records it
2. **Enforcement over Passive Tracking** — idle leads, unpaid invoices, and missed follow-ups trigger automated enforcement
3. **WhatsApp-first over UI-first** — WhatsApp is the primary interaction layer, not an integration
4. **Cash Flow Visibility over Reporting Complexity** — collections and reconciliation are first-class features
5. **Simplicity of Use over Feature Density** — value delivered within 10 minutes of onboarding

### Behavioral Principles (Pakistan Market)
1. **Adapt to user behavior** — the system adapts to how users work, not the other way around
2. **Near-zero manual entry** — inbound WhatsApp messages auto-create contacts, leads, and activities
3. **Natural habit alignment** — workflows run inside WhatsApp, not in a separate form-based UI
4. **Reduced cognitive load** — every core action must be achievable in ≤2 steps
5. **Immediate visible value** — first lead captured and first follow-up scheduled within 10 minutes of onboarding
6. **Gradual discipline** — enforcement ramps up progressively; no hard-blocking on day 1

---

## Architecture Overview

The system uses a **Layered + Engine-driven + Adapter-based** architecture.

| Layer | Name | Contents |
|---|---|---|
| L1 | Core (country-agnostic) | Domain models, business services, workflow logic, orchestration |
| L2 | Interfaces | `MessagingAdapter`, `PaymentAdapter`, `ComplianceAdapter` |
| L3 | Adapters (country-specific) | `adapters/pakistan/*`, external provider integrations |

**Architectural rules:**
- No country-specific logic in Core
- Core depends only on Interfaces (L2), never on L3 implementations
- Adapters implement Interfaces and can be swapped without affecting Core
- Future countries follow the same pattern via `adapters/<country>/*`

See [`docs/architecture-overview.md`](docs/architecture-overview.md) for the full model.

---

## Core Engines

The system is built around six reusable engines. No domain may reimplement engine logic.

| Engine | Purpose | Doc |
|---|---|---|
| WhatsApp Engine | Inbound/outbound messaging, conversation threading, contact mapping | [`whatsapp-execution-model.md`](docs/whatsapp-execution-model.md) |
| Follow-up Engine | Scheduling, enforcement rules, escalation logic | [`followup-enforcement-model.md`](docs/followup-enforcement-model.md) |
| Collections Engine | Invoice lifecycle, payment tracking, reconciliation, reminder automation | [`collections-engine-model.md`](docs/collections-engine-model.md) |
| Activity Control Engine | Immutable activity logs, ownership tracking, audit trail | [`activity-control-model.md`](docs/activity-control-model.md) |
| Activation Engine | Zero-setup onboarding, auto pipeline creation, instant value | [`activation-model.md`](docs/activation-model.md) |
| Execution Control Plane | Idempotency, retry mechanisms, transaction safety, concurrency control | [`execution-hardening.md`](docs/execution-hardening.md) |

---

## Domain Capabilities

| # | Capability | Primary Doc |
|---|---|---|
| 1 | WhatsApp Lead Capture | [`whatsapp-execution-model.md`](docs/whatsapp-execution-model.md) |
| 2 | Conversational CRM | [`whatsapp-execution-model.md`](docs/whatsapp-execution-model.md) |
| 3 | Follow-up Assistant | [`followup-enforcement-model.md`](docs/followup-enforcement-model.md) |
| 4 | Collections Automation | [`collections-engine-model.md`](docs/collections-engine-model.md) |
| 5 | Payment Integration (JazzCash, Easypaisa) | [`pakistan-adapter-architecture.md`](docs/pakistan-adapter-architecture.md) |
| 6 | Owner Dashboard | [`owner-dashboard.md`](docs/owner-dashboard.md) |
| 7 | Employee Activity Monitoring | [`activity-control-model.md`](docs/activity-control-model.md) |
| 8 | Deal and Revenue Tracking | [`opportunities-pipeline.md`](docs/opportunities-pipeline.md) |
| 9 | Workflow Engine | [`workflow-catalog.md`](docs/workflow-catalog.md) |
| 10 | Offline Sync Layer | [`offline-sync.md`](docs/offline-sync.md) |

---

## Critical Integration Flows

All four flows must operate end-to-end with no data loss:

1. `WhatsApp → Lead → Follow-up → Close`
2. `Lead → Invoice → Payment → Reconciliation`
3. `Follow-up → Escalation → Reassignment`
4. `Offline Action → Sync → Consistent State`

See [`BACKEND-QC.md`](BACKEND-QC.md) for end-to-end flow validation (consolidated).

---

## Key Documentation Index

### Foundation
- [`architecture-overview.md`](docs/architecture-overview.md) — L1/L2/L3 layer model, engine registry
- [`domain-model.md`](docs/domain-model.md) — 58 canonical domain entities
- [`service-map.md`](docs/service-map.md) — 39 services with ownership boundaries
- [`capability-matrix.md`](docs/capability-matrix.md) — 30 capabilities mapped to services
- [`api-standards.md`](docs/api-standards.md) — Uniform API contract

### Security & Data
- [`identity-auth-rbac.md`](docs/identity-auth-rbac.md) — Auth, roles, permissions
- [`security-model.md`](docs/security-model.md) — Security principles and invariants
- [`data-architecture.md`](docs/data-architecture.md) — Storage, CQRS, caching
- [`data-governance-ownership.md`](docs/data-governance-ownership.md) — Ownership, retention, quality

### Execution Hardening
- [`execution-hardening.md`](docs/execution-hardening.md) — ACID, idempotency, retry
- [`global-idempotency.md`](docs/global-idempotency.md) — Deduplication model
- [`concurrency-control.md`](docs/concurrency-control.md) — OCC + pessimistic concurrency
- [`distributed-lock-strategy.md`](docs/distributed-lock-strategy.md) — Redis-backed locks

### Deployment
- [`runtime-deployment.md`](docs/runtime-deployment.md) — Environments, K8s, canary rollout
- [`runtime-deployment.md`](docs/runtime-deployment.md) — CI/CD pipelines, QC gates, environments, K8s, canary rollout

---

## Python Environment Setup

| Item | Location |
|---|---|
| Python runtime | `D:\Python\python.exe` (3.12.10) |
| Virtual environment | `D:\CRM\backend\.venv` |
| pip cache | `D:\CRM\.pip-cache` |
| Installed packages | `D:\CRM\backend\.venv\Lib\site-packages` |

Nothing touches C: during normal development.

### Activate the venv

**PowerShell:**
```powershell
D:\CRM\backend\.venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
D:\CRM\backend\.venv\Scripts\activate.bat
```

### Installed packages

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.8.2
```

To reinstall from scratch:
```powershell
pip install -r D:\CRM\backend\services\requirements.txt
```

### Recreate venv from scratch

```powershell
D:\Python\python.exe -m venv D:\CRM\backend\.venv
D:\CRM\backend\.venv\Scripts\Activate.ps1
pip install -r D:\CRM\backend\services\requirements.txt
```

pip cache is locked to `D:\CRM\.pip-cache` via `%APPDATA%\pip\pip.ini`.

---

## Target Classification

**Final System Classification:** Execution-First Enterprise CRM OS

**Comparable Benchmark:**
- Execution discipline of internal sales ops systems
- Usability of modern SaaS tools
- Breadth of mid-market CRMs

**Primary Differentiator:** Enforced execution + WhatsApp-first interaction + cash flow focus
