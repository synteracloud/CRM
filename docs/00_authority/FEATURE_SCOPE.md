Status: Draft
Authority Level: Critical
Last Reviewed: 2026-06-21
Owner: Human

---

# FEATURE SCOPE — Pakistan CRM OS

## Overview

This document defines the full feature set of Pakistan CRM OS, grouped by domain, with commercialisation phase mapping and freeze status. Source: FEATURE_INVENTORY.md (U1), DESIGN-SPEC.md, COMMERCIALISATION-PLAN.md.

**Total features inventoried:** 131 (features 1–131 in FEATURE_INVENTORY.md + 15 undocumented features U-01–U-15)
**Feature numbering:** Features 1–36 (GROUP A), 37–104 (GROUP B), 63–99 (GROUP C), 105–131 (GROUP D); U-01–U-15 are undocumented features discovered during U1 audit. Full sequential list in FEATURE_INVENTORY.md (U1 document).
**Module count:** 22 user-facing product modules (Modules 1–22). AUTHORITY_RECONSTRUCTION_REPORT.md lists 30+ backend modules because it includes infrastructure-only modules (Email, Price Books, Event Bus, External APIs, Tenants, Custom Objects, etc.) that are implementation-level and not counted in this feature scope.
**All features status:** Built (HTML + backend), with 5 confirmed Wired to live API, 3 Blocked by external dependencies

---

## GROUP A — Core CRM

### Module 1: Lead Management
| # | Feature | Status |
|---|---|---|
| 1 | Lead list with DataTable (stage/priority/source filter chips) | Built |
| 2 | Lead detail view (timeline, follow-up panel, score) | Built |
| 3 | New lead form (stage, priority, source, phone E.164) | Built |
| 4 | Lead stage transitions: new→qualifying→nurturing→proposal→negotiation→won/lost/disqualified | Built |
| 5 | Lead priority toggle (hot/warm/cold) | Built |
| 6 | Lead owner assignment | Built |
| 7 | Lead CSV export | Built |
| 8 | Lead CSV/JSON bulk import with phone dedup | Built |
| 9 | Lead next-action suggestion (AI-powered advisory, rule-based) | Built |
| 10 | Lead funnel dashboard (KPI tiles, funnel chart) | Built |
| U-03 | Lead soft-delete (not hard delete) | Built |

### Module 2: Follow-up Enforcement
| # | Feature | Status |
|---|---|---|
| 11 | Follow-up queue (overdue/pending filter, escalation badges) | Built |
| 12 | Follow-up complete action | Built |
| 13 | Follow-up snooze action | Built |
| 14 | Follow-up create (from lead detail) | Built |
| 15 | Canonical pending task per lead (exactly one enforced by DB constraint) | Built |
| 16 | Follow-up enforcement engine (auto-creates tasks on idle leads via WF-001) | Built |

### Module 3: Contacts
| # | Feature | Status |
|---|---|---|
| 17 | Contact list with health indicators (completeness score, open cases, idle flag) | Built |
| 18 | Contact detail (touchpoint timeline, linked account, cases) | Built |
| 19 | New contact form | Built |
| 20 | Contact health dashboard (KPI tiles, completeness distribution) | Built |
| 21 | Contact CSV export/import | Built |
| 22 | Contact tag management | Built |

### Module 4: Accounts
| # | Feature | Status |
|---|---|---|
| 23 | Account list (tier/industry filter) | Built |
| 24 | Account detail (contacts, opportunities, invoices, churn risk) | Built |

### Module 5: Sales / Opportunities
| # | Feature | Status |
|---|---|---|
| 25 | Opportunity detail (stage, forecast category, amount PKR, line items) | Built |
| 26 | Opportunity stage transition (qualification→discovery→proposal→negotiation→closed_won/closed_lost) | Built |
| 27 | New opportunity form | Built |
| 28 | Opportunity line item management | Built |
| 29 | Sales cockpit (pipeline overview, today's tasks, at-risk deals) | Built |
| 30 | Opportunity pipeline dashboard (funnel, forecast by category) | Built |

### Module 6: CPQ / Quotes & Orders
| # | Feature | Status |
|---|---|---|
| 31 | CPQ quote builder (line items, discount, auto-approval trigger) | Built |
| 32 | Quote detail (approval history, line items, status) | Built |
| 33 | Quote approval dashboard (pending approvals queue) | Built |
| 34 | Quote accept → order creation | Built |
| 35 | Order detail (linked invoice, fulfilment status) | Built |
| 36 | Discount >10% auto-routes to approval (rule_engine) | Built |

### Module 18: Identity & Access Management
| # | Feature | Status |
|---|---|---|
| 105 | User directory | Built |
| 106 | User management (invite, status, role assignment) | Built |
| 107 | Role editor (create custom roles, set permissions) | Built |
| 108 | Identity dashboard (role distribution, login heatmap) | Built |
| 109 | RBAC audit (permission matrix view) | Wired (J-03) |

### Module 21: Auth & Registration
| # | Feature | Status |
|---|---|---|
| 123 | Email + password login | Built |
| 124 | Multi-tenant self-registration (creates tenant, seeds pipeline, returns JWT) | Built |
| 125 | JWT token refresh (silent renewal, 15-min access / 7-day refresh) | Built |
| 126 | Logout (JTI revocation in Redis) | Built |
| 127 | Forgot password (6-digit OTP via SendGrid email) | Built |
| 128 | Reset password (OTP validation) | Built |
| U-01 | SendGrid email integration (OTP + welcome email) | Built (prod-only when SENDGRID_API_KEY set) |
| U-05 | Post-registration activation engine (seeds default pipeline) | Built |

---

## GROUP B — Finance & Operations

### Module 7: Finance / Collections
| # | Feature | Status |
|---|---|---|
| 37 | Invoice queue (overdue flag, PKR amounts) | Built |
| 38 | Invoice detail (payment history, balance) | Built |
| 39 | Collections queue (days overdue, contact, next action) | Built |
| 40 | Finance analytics (revenue trends, collections rate, PKR charts) | Built |
| 41 | JazzCash payment processing | Blocked (P-016) |
| 42 | Easypaisa payment processing | Blocked (P-016) |
| 43 | Payment webhook handler | Built (stub) |

### Module 8: Subscriptions / Billing
| # | Feature | Status |
|---|---|---|
| 44 | Subscription revenue dashboard (MRR/ARR, status breakdown) | Built |
| 45 | Subscription detail (billing cycle, status, renewal) | Built |
| 46 | Billing settings (plan, payment methods) | Blocked (P-016) |

### Module 9: Support / Cases
| # | Feature | Status |
|---|---|---|
| 47 | Case queue (SLA status, priority, queue assignment) | Built |
| 48 | Case detail (SLA timers, comment thread, escalation history) | Built |
| 49 | New case form (SLA tier, source, category, queue) | Built |
| 50 | Case assignment (to agent or team) | Built |
| 51 | Case comment (internal note, customer reply, resolution) | Built |
| 52 | Case resolve | Built |
| 53 | Case force-close (admin) | Built |
| 54 | Case reopen (14-day window — 422 REOPEN_WINDOW_EXPIRED after 14 days) | Built |
| 55 | Case escalation (SLA breach / manager override) | Built |
| 56 | Link knowledge article to case | Built |
| 57 | Support console (agent workspace with queue view) | Built |
| 58 | Support dashboard (SLA compliance, CSAT, queue depth) | Built |
| 59 | SLA breach notification (auto-escalation workflow WF-003) | Built |
| U-07 | Optimistic concurrency locking on Cases (version_no, 409 CONFLICT on stale) | Built |
| U-10 | 14-day case reopen window enforcement | Built |
| U-15 | SLA auto-advance: ASSIGNED→IN_PROGRESS on first customer_reply | Built |

### Module 10: Knowledge Base
| # | Feature | Status |
|---|---|---|
| 60 | Knowledge article view (rich content, version) | Built |
| 61 | Knowledge dashboard (effectiveness metrics) | Built |
| 62 | Article publish workflow (draft→review→published) | Built |

### Module 16: Territories
| # | Feature | Status |
|---|---|---|
| 100 | Territory list and configuration | Built |
| 101 | Territory rule management (geography/industry/account_size criteria) | Built |
| 102 | Auto-assignment of leads to territory owner (WF-004) | Built |

### Module 17: Partners
| # | Feature | Status |
|---|---|---|
| 103 | Partner list (tier, YTD revenue, commission) | Built |
| 104 | Partner detail (deal registrations, commission ledger, attribution) | Built |

---

## GROUP C — Automation, Engagement & Intelligence

### Module 11: Omnichannel Inbox
| # | Feature | Status |
|---|---|---|
| 63 | Inbox conversation list (channel badges, unread count, intent tags) | Built |
| 64 | Conversation thread view (message history, agent info) | Built |
| 65 | Send message (WhatsApp/email outbound) | Built |
| 66 | Claim conversation from pool (atomic assignment) | Built |
| 67 | Handoff conversation to another agent | Built |
| 68 | Agent presence status (online/away/busy/offline) | Built |
| 69 | Supervisor presence board | Built |
| 70 | Inbox queue management | Built |
| 71 | Engagement dashboard (WhatsApp metrics, channel breakdown) | Wired (2026-05-31) |
| 72 | WhatsApp webhook receiver | Built |
| U-09 | Agent max_concurrent capacity enforcement (10 concurrent conversations cap) | Built |

### Module 12: Marketing / Campaigns
| # | Feature | Status |
|---|---|---|
| 73 | Campaign builder (WhatsApp blast/email/SMS) | Built |
| 74 | Marketing workspace (active campaigns, performance) | Built |
| 75 | Marketing analytics (open rate, click rate, conversion) | Built |
| 76 | Segment management (criteria-based contact lists) | Built |

### Module 13: Workflow Automation
| # | Feature | Status |
|---|---|---|
| 77 | Workflow builder (canvas with trigger + step DSL) | Built |
| 78 | Workflow publish/activate | Built |
| 79 | Workflow dry-run simulate (no side effects) | Built |
| 80 | Workflow run detail (step-by-step execution trace) | Built |
| 81 | Workflow retry (failed execution — creates child execution with parent_execution_id) | Built |
| 82 | Workflow cancel (running execution) | Built |
| 83 | Workflow dashboard (execution stats, success rate) | Built |
| 84 | Workflow analytics | Built |
| 85 | 5 system workflows (lead idle, collections, SLA, territory, opp stage) | Built |
| U-11 | Workflow dry-run simulate (no side effects, returns simulated steps) | Built |
| U-12 | Workflow retry creates new child execution with parent_execution_id link | Built |

### Module 14: AI / Copilot
| # | Feature | Status |
|---|---|---|
| 86 | AI copilot chat (NL query → regex intent → lead/payment/followup/case) | Built (rule-based only) |
| 87 | Copilot suggestions (overdue follow-ups, deal nudges, risk flags) | Built |
| 88 | Dismiss/action copilot suggestion | Built |
| 89 | Lead scoring (0–100, score_band, trend, top_drivers) | Built (rule-based) |
| 90 | Force recompute lead score | Built |
| 91 | Churn prediction (risk_band, churn_probability, recommended_action) | Built (rule-based) |
| 92 | CLV estimate (PKR, 24-month horizon) | Built (rule-based) |
| 93 | AI model registry (rule_based models only) | Built |

### Module 15: Report Builder
| # | Feature | Status |
|---|---|---|
| 94 | Report builder (custom query, field selection, visualisation) | Wired (2026-05-31) |
| 95 | Sales analytics (win rate, pipeline velocity, rep performance) | Built |
| 96 | Support analytics (CSAT, resolution time, escalation rate) | Built |
| 97 | Finance analytics (revenue recognition, collections efficiency) | Built |
| 98 | Workflow analytics | Built |
| 99 | Audit report | Built |

---

## GROUP D — Admin & Settings

### Module 19: Audit & Compliance
| # | Feature | Status |
|---|---|---|
| 110 | Audit log (hash-chain verified, actor/action/entity, immutable) | Built |
| 111 | Audit log export (signed CSV) | Built |
| 112 | Compliance report | Built |
| 113 | Data governance (classification, retention, SAR) | Wired (2026-05-31) |
| 114 | Privacy consent management | Built |
| 115 | Audit dashboard (platform health, event volume) | Built |

### Module 20: Settings / Administration
| # | Feature | Status |
|---|---|---|
| 116 | Org settings (branding, timezone, currency PKR) | Built |
| 117 | Integration settings (WhatsApp, payment rails config) | Wired (2026-05-31) |
| 118 | Integration connection test | Built |
| 119 | Notification preferences (EN strings) | Built |
| 120 | Notification preferences (Urdu) | Blocked (P-017) |
| 121 | Feature flag management (dual-approval toggle) | Built |
| 122 | Tenant admin panel (entitlements, seat count) | Built |

### Module 22: Builder Tools
| # | Feature | Status |
|---|---|---|
| 129 | Custom object builder (schema definition, layout) | Built |
| 130 | Rule builder (business rule canvas) | Built |
| 131 | Approval lanes builder | Built |

---

## Phase Gate Mapping (C0–C6 Commercialisation Phases)

| Phase | Name | Gate | Status |
|---|---|---|---|
| C0 | Environment Seal | Zero silent C: writes; all tool caches on D: | COMPLETE 2026-05-31 |
| C1 | DB Wiring (local) | All 42 gateway routes use PostgreSQL; no data loss on restart | COMPLETE 2026-05-31 |
| C2 | Automated Test Suite | 80% coverage; all E2E pass; security scan clean | COMPLETE 2026-06-01 |
| C3 | Code Hardening | Redis rate-limit; JWT refresh; helmet(); CORS allowlist | COMPLETE 2026-06-01 |
| C4 | Infrastructure Deployment | Render.com live; CI/CD pipeline green | COMPLETE 2026-06-01 |
| C5 | Post-Deploy Smoke + Sign-Off | All tests pass on production URL | COMPLETE 2026-06-02 |
| C6 | Commercial Launch | Final audit; v1.0.0 tag; push | CURRENT |

---

## Feature Freeze Status

### Frozen (must not change without human sign-off)
- All 131 core features listed above — scope is complete for v1
- PKR as sole currency
- 7 canonical roles and 91 scopes in rbac-scopes.js
- 5 system workflows (is_system=true; cannot be edited by tenants)
- Authentication flow (JWT HS256, 15-min/7-day token pair)
- Multi-tenant isolation model (application-level, x-tenant-id header)

### Open for Change (within approved process)
- Individual page bug fixes (via PAGE-BUILD-PROTOCOL.md T1–T4)
- Adding new Playwright E2E tests
- Backend test additions (pytest)
- Documentation updates
- Feature flag toggles (dual-approval required for flags with requires_dual_approval=true)

### Blocked (awaiting external input)
- JazzCash/Easypaisa live integration (P-016)
- Urdu notification strings (P-017)
- AI inference model selection (no provider SDK yet)
- Facebook/Instagram lead capture (MR-001)
- Voice note transcription (MR-003)
- Kuickpay adapter (MR-007)

---

*End FEATURE_SCOPE.md*
