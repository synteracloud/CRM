# Pakistan CRM OS — Rebuild Pending Tasks

**Anchor:** `REBUILD-PLAN.md`
**Last updated:** 2026-05-18 — Phase 2 COMPLETE (19/19). Phase 3 next.
**Legend:** `[ ]` Pending · `[x]` Done · `[~]` In progress

---

## Completion Summary

| Phase | Total tasks | Done | % |
|---|---|---|---|
| Phase 1 — Foundation Seal | 14 | 14 | 100% ✓ |
| Phase 2 — Follow-up Engine | 19 | 19 | 100% ✓ |
| Phase 3 — 5 Engines | 30 | 0 | 0% |
| Phase 4 — Frontend (75 pages) | 78 | 0 | 0% |
| Phase 5 — Hardening | 14 | 0 | 0% |
| **Total** | **155** | **33** | **21%** |

---

## Phase 1 — Foundation Seal

### Documentation
- [x] Root `README.md` — GitHub landing page (what it is, how to run, how to contribute)
- [x] `CHANGELOG.md` — version history from session 20
- [x] `CONTRIBUTING.md` — branch naming, commit format, PR process
- [x] `backend/docs/adr/ADR-001.md` — DDD + microservices choice
- [x] `backend/docs/adr/ADR-002.md` — Adapter pattern for Pakistan isolation
- [x] `backend/docs/adr/ADR-003.md` — WhatsApp-first interaction model

### Structure & Tooling
- [x] `Makefile` — make dev, make test, make migrate, make lint
- [x] `.pre-commit-config.yaml` — ruff + black on every commit
- [x] Alembic setup — alembic init + env.py configured + requirements updated

### DevOps
- [x] `docker-compose.yml` — already existed at backend/docker-compose.yml (Postgres + gateway + services)
- [x] `Dockerfile` — backend/gateway (already existed)
- [x] `Dockerfile` — backend/services (already existed)
- [x] Verify: all 96 existing pages still HTTP 200 after Phase 1 push
- [x] GitHub push — Phase 1 complete

---

## Phase 2 — Follow-up Engine

### Models & DB
- [x] SQLAlchemy model — `FollowUp` (services/db/models/followup.py — FollowupTask + FollowupEscalation)
- [x] SQLAlchemy model — `Lead` (services/db/models/lead.py)
- [x] SQLAlchemy model — `Activity` (services/db/models/activity.py)
- [x] Alembic migration — first real schema migration (alembic/versions/0001_followup_schema.py)

### API Endpoints
- [x] `GET /api/v1/followups` — list, overdue-pinned sort
- [x] `POST /api/v1/followups` — create with T+0 trigger
- [x] `GET /api/v1/followups/{id}` — detail
- [x] `PATCH /api/v1/followups/{id}/complete` — mark done
- [x] `POST /api/v1/followups/{id}/escalate` — manual escalation
- [x] `/docs` — OpenAPI endpoint exposed (FastAPI auto-generates)

### Business Logic
- [x] Enforcement timers — T+0 / +2h / +24h / +48h (pre-existing engine.py)
- [x] Inactivity rule engine (precedence: inactivity > time > activity) (pre-existing)
- [x] Reassignment configuration mechanism (pre-existing engine.py)
- [x] Scheduler job — background overdue escalation (pre-existing scheduler.py)

### Security
- [x] JWT middleware wired to all followup routes (services/auth/jwt_deps.py)
- [x] RBAC role gates enforced (from identity-auth-rbac.md)

### Tests
- [x] `conftest.py` + pytest config (pre-existing + requirements updated)
- [x] Unit tests — enforcement timer logic (tests/followup/test_enforcement.py — 18 tests)
- [x] Integration tests — all 5 endpoints (tests/followup/test_public_api.py — 20 tests)
- [x] Verify: all 96 existing pages still HTTP 200 after Phase 2 push
- [x] GitHub push — Phase 2 complete

---

## Phase 3 — Remaining 5 Engines

### S1 — WhatsApp Engine (spec: whatsapp-execution-model.md)
- [ ] Inbound webhook handler
- [ ] Intent detection logic
- [ ] Auto lead creation from inbound message
- [ ] Conversation threading
- [ ] Contact mapping
- [ ] Unit + integration tests

### S2 — Collections Engine (spec: collections-engine-model.md)
- [ ] Invoice lifecycle — create, send, overdue, paid states
- [ ] Overdue detection logic
- [ ] WhatsApp reminder trigger
- [ ] Confidence scoring — ≥85 auto-match / 40–84 manual review
- [ ] Customer opt-out mechanism (WhatsApp STOP)
- [ ] Unit + integration tests

### S3 — Activity Control Engine (spec: activity-control-model.md)
- [ ] Immutable activity log writes
- [ ] Ownership tracking
- [ ] Audit trail endpoints
- [ ] Unit + integration tests

### S4 — Activation Engine (spec: activation-model.md)
- [ ] Onboarding flow (<10 min first value)
- [ ] Auto pipeline creation
- [ ] Sandbox→production WhatsApp transition
- [ ] Sample data localisation (PKR, Pakistan names)
- [ ] Unit + integration tests

### S5 — Execution Control Plane (spec: execution-hardening.md)
- [ ] Idempotency key middleware
- [ ] Retry with exponential backoff (1s base, 2× multiplier, ±20% jitter, 60s max)
- [ ] Dead letter queue (DLQ) + operator action API
- [ ] Unit + integration tests

### Phase 3 close
- [ ] Verify: all 96 existing pages still HTTP 200
- [ ] GitHub push — Phase 3 complete

---

## Phase 4 — Frontend: 75 Custom Pages

### Build Phase 1 — Core Execution Surfaces
- [ ] B-01 `followups.html` — Follow-up Queue (archetype B)
- [ ] B-02 `leads.html` — Lead Queue (archetype B)
- [ ] C-01 `leads-detail.html` — Lead Detail (archetype C)
- [ ] A-01 `dashboard.html` — Owner Dashboard (archetype A)
- [ ] B-08 `collections.html` — Collections Queue (archetype B)
- [ ] B-03 `contacts.html` — Contact List (archetype B)
- [ ] I-01 `lead-new.html` — New Lead Form (archetype I)

### Build Phase 2 — Sales Intelligence
- [ ] C-04 `opportunities-detail.html` — Opportunity Detail (archetype C)
- [ ] D-01 `sales-cockpit.html` — Sales Cockpit (archetype D)
- [ ] A-02 `leads-dashboard.html` — Lead Funnel Dashboard (archetype A)
- [ ] A-04 `sales-dashboard.html` — Opportunity Pipeline Dashboard (archetype A)
- [ ] I-03 `opportunity-new.html` — New Opportunity Form (archetype I)
- [ ] I-05 `quote-builder.html` — CPQ Quote Builder (archetype I)
- [ ] C-06 `quotes-detail.html` — Quote Detail (archetype C)

### Build Phase 3 — Finance & Collections
- [ ] B-09 `invoices.html` — Invoice Queue (archetype B)
- [ ] C-08 `invoices-detail.html` — Invoice Detail (archetype C)
- [ ] A-06 `subscriptions-dashboard.html` — Subscription Revenue Dashboard (archetype A)
- [ ] C-09 `subscriptions-detail.html` — Subscription Detail (archetype C)
- [ ] H-04 `finance-analytics.html` — Finance Analytics (archetype H)

### Build Phase 4 — Support Operations
- [ ] B-05 `cases.html` — Case Queue (archetype B)
- [ ] C-05 `cases-detail.html` — Case Detail (archetype C)
- [ ] E-01 `support-console.html` — Support Console (archetype E)
- [ ] A-07 `support-dashboard.html` — Case SLA Operations Dashboard (archetype A)
- [ ] I-04 `case-new.html` — New Case Form (archetype I)
- [ ] C-12 `knowledge-article.html` — Knowledge Article Detail (archetype C)

### Build Phase 5 — Communication & Inbox
- [ ] L-01 `inbox.html` — Omnichannel Inbox (archetype L)
- [ ] L-02 `inbox-thread.html` — Conversation Thread (archetype L)
- [ ] A-08 `engagement-dashboard.html` — Communication Engagement Dashboard (archetype A)

### Build Phase 6 — Admin & Settings
- [ ] G-02 `user-management-crm.html` — User Management (archetype G)
- [ ] G-03 `roles.html` — Role & Permission Editor (archetype G)
- [ ] G-05 `integrations.html` — Integration Settings (archetype G)
- [ ] G-07 `feature-flags.html` — Feature Flags (archetype G)
- [ ] G-09 `territories.html` — Territory & Assignment Config (archetype G)
- [ ] G-01 `org-settings.html` — Organization Settings (archetype G)

### Build Phase 7 — Marketing & Automation
- [ ] F-01 `marketing-workspace.html` — Marketing Workspace (archetype F)
- [ ] I-06 `campaign-new.html` — Campaign Builder (archetype I)
- [ ] H-02 `marketing-analytics.html` — Marketing Analytics (archetype H)
- [ ] K-01 `workflow-builder.html` — Workflow Builder (archetype K)
- [ ] A-10 `workflows-dashboard.html` — Workflow Automation Dashboard (archetype A)

### Build Phase 8 — Enterprise Features (36 pages)
- [ ] A-03 `contacts-health.html` — Customer Health Dashboard
- [ ] A-05 `quotes-dashboard.html` — Quote Approval Dashboard
- [ ] A-09 `knowledge-dashboard.html` — Knowledge Effectiveness Dashboard
- [ ] A-11 `tenants-dashboard.html` — Tenant & Entitlement Dashboard
- [ ] A-12 `identity-dashboard.html` — Identity & Access Posture Dashboard
- [ ] A-13 `audit-dashboard.html` — Platform Audit & Reliability Dashboard
- [ ] B-04 `accounts.html` — Account List
- [ ] B-06 `activity.html` — Activity Feed
- [ ] B-07 `tasks.html` — Task Queue
- [ ] B-10 `users.html` — User Directory
- [ ] B-11 `partners.html` — Partner List
- [ ] C-02 `contacts-detail.html` — Customer 360
- [ ] C-03 `accounts-detail.html` — Account Profile
- [ ] C-07 `orders-detail.html` — Order Detail
- [ ] C-10 `workflow-run-detail.html` — Workflow Execution Detail
- [ ] C-11 `partners-detail.html` — Partner Detail
- [ ] G-04 `billing-settings.html` — Billing & Subscription Settings
- [ ] G-06 `notifications.html` — Notification Settings
- [ ] G-08 `compliance.html` — Compliance Settings
- [ ] H-01 `sales-analytics.html` — Sales Analytics
- [ ] H-03 `support-analytics.html` — Support Analytics
- [ ] H-05 `workflow-analytics.html` — Workflow Analytics
- [ ] H-06 `audit-report.html` — Audit Report
- [ ] H-07 `report-builder.html` — Custom Report Builder
- [ ] I-02 `contact-new.html` — New Contact Form
- [ ] J-01 `audit-log.html` — Audit Log
- [ ] J-02 `compliance-report.html` — Compliance Report
- [ ] J-03 `data-governance.html` — Data Governance Console
- [ ] J-04 `rbac-audit.html` — RBAC Audit
- [ ] J-05 `privacy.html` — Consent & Privacy Manager
- [ ] K-02 `object-builder.html` — Custom Object Layout Builder
- [ ] K-03 `rule-builder.html` — Rule / CPQ Logic Builder
- [ ] K-04 `approval-lanes.html` — CPQ Approval Lane Board
- [ ] L-03 `routing-config.html` — Routing Configuration
- [ ] M-01 `ai-copilot.html` — AI Copilot Panel
- [ ] M-02 `ai-insights.html` — AI Insights Dashboard

### Phase 4 close
- [ ] All 75 pages wired to live backend endpoints (FRONTEND-BACKEND-MAPPING.md)
- [ ] RTL verified on all pages (CONSTRAINTS.md C-001)
- [ ] Mobile responsiveness verified on all pages (b9-p08-mobile-responsiveness-system.md)
- [ ] Verify: all 96 existing pages still HTTP 200
- [ ] GitHub push — Phase 4 complete

---

## Phase 5 — Hardening

### CI/CD
- [ ] GitHub Actions — lint on every push
- [ ] GitHub Actions — test on every push
- [ ] GitHub Actions — Docker build on push to main
- [ ] GitHub Actions — deploy to staging on merge to main

### Security
- [ ] Rate limiting middleware — 10k/min per-tenant (security-model.md)
- [ ] Secrets moved to GitHub Secrets (remove raw values from .env references in CI)
- [ ] Bandit security scan added to CI pipeline
- [ ] npm audit added to CI pipeline

### Observability
- [ ] structlog wired to all backend services
- [ ] Request logging middleware
- [ ] Distributed trace headers

### Testing
- [ ] Coverage gate — CI blocks merge if coverage < 80%
- [ ] Load test (locust) — follow-up queue + collections happy path
- [ ] Full E2E test — lead capture → follow-up → close → invoice → payment

### Phase 5 close
- [ ] Verify: all 96 existing pages still HTTP 200
- [ ] GitHub push — Phase 5 complete
- [ ] Final grade audit across all 8 areas
