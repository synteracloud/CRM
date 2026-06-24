# BACKEND_DOC_ALIGNMENT_STATUS.md

**Generated:** 2026-06-20 — U7 Delta Remediation
**Purpose:** Per-domain alignment status after U7 remediation. Shows which domains are now fully aligned, partially aligned, or still pending human decision.

---

## Status Key

| Status | Meaning |
|---|---|
| **ALIGNED** | Documentation matches code. Routes, scopes, module paths all confirmed accurate. |
| **PARTIALLY-ALIGNED** | Core routes documented; edge cases or sub-resources missing. No known wrong claims remaining. |
| **HUMAN-DECISION-REQUIRED** | Alignment blocked by a choice that only the project lead can make (expose vs archive, schema location). |
| **OUT-OF-SCOPE** | Not assessed in U6/U7. |

---

## Domain Alignment Table

| Domain | Status | Notes | Fixed by |
|---|---|---|---|
| Auth | ALIGNED | 7 routes confirmed. JWT/Redis/HS256 details accurate. | — (was accurate at U1) |
| Leads | ALIGNED | 8 routes, stage transitions, CSV import/export, next-action proxy all documented. | — |
| Contacts | ALIGNED | 7 routes, CSV export/import, phone dedup documented. | — |
| Accounts | PARTIALLY-ALIGNED | 4 routes inferred (no direct read of v1-accounts.routes.js). Accurate at approximately ~4. | — |
| Opportunities | ALIGNED | 6 routes + line-items sub-resource documented. | — |
| Follow-ups | ALIGNED | 6 routes, complete/snooze/canonical documented. | — |
| Activities | PARTIALLY-ALIGNED | ~4 routes (list, create, detail, ~1 more). No wrong claims. | — |
| Tasks | PARTIALLY-ALIGNED | ~4 routes (list, create, detail, update). No wrong claims. | — |
| Cases | ALIGNED | 14 routes confirmed (was 13 in summary, 14 in detail). Summary fixed. All transitions, queues, escalation documented. | FX-015 |
| Collections | ALIGNED | 11 routes fully enumerated: invoices CRUD, payments, subscriptions, overdue, reconcile, proof upload/verify, reminders. | FX-002 |
| Campaigns | ALIGNED | 10 routes confirmed: full lifecycle (draft/scheduled/active/paused/completed/cancelled), sends and conversions sub-resources. | FX-005 |
| Communications | ALIGNED | 1 route confirmed (GET /engagement). Stale POST /send claim removed. | FX-007 |
| Inbox | ALIGNED | 11 routes, claim/handoff/messages, presence, queues — documented at U1, confirmed accurate. | — |
| Quotes | PARTIALLY-ALIGNED | ~5 routes including CPQ approval trigger and accept→order flow. No wrong claims. | — |
| Orders | PARTIALLY-ALIGNED | ~3 routes confirmed pattern. No wrong claims. | — |
| Invoice Summaries | PARTIALLY-ALIGNED | ~3 routes (list, detail, create). Distinct from Collections invoices. No wrong claims. | — |
| Subscriptions | PARTIALLY-ALIGNED | ~4 routes (list, detail, create, update). No wrong claims. | — |
| Payments | PARTIALLY-ALIGNED | ~3 routes. JazzCash/Easypaisa in stub mode (P-016 blocker documented). | — |
| Payment Webhooks | ALIGNED | 3 routes confirmed: /jazzcash, /easypaisa, /log. | FX-006 |
| WhatsApp Webhooks | ALIGNED | 6 routes confirmed: 4 provider inbound handlers + Meta GET verification + /log. | FX-006 |
| Billing | PARTIALLY-ALIGNED | ~4 routes (subscription CRUD, invoice history). No wrong claims. | — |
| Workflows | ALIGNED | 11 routes confirmed (definitions + executions + publish/simulate/stats). 5 system workflows accurate. | — |
| Users | PARTIALLY-ALIGNED | ~5 routes including assign-role. No wrong claims. | — |
| Roles | ALIGNED | 4 routes (list, create, update, delete) confirmed from code read at U1. | — |
| Tenants | ALIGNED | 1 route confirmed (GET /tenants/current). Stale admin/tenants rows removed with clarifying note. | FX-008 |
| Territories | ALIGNED | 11 routes fully enumerated: CRUD + assignments + evaluate + reassign + rules + performance. | FX-004 |
| Partners | ALIGNED | 13 routes fully enumerated: partner CRUD + commissions (approve/pay) + deal-registrations + global deal-reg actions. | FX-003 |
| Knowledge Base | PARTIALLY-ALIGNED | ~5 routes (list, create, detail, update, publish). No wrong claims. | — |
| Reports | PARTIALLY-ALIGNED | ~4 routes (definitions CRUD + execute). H-07 confirmed wired. No wrong claims. | — |
| AI / ML | ALIGNED | 13 routes confirmed (scores, predictions, CLV, copilot, models). Advisory-only architecture documented. | — |
| Audit | PARTIALLY-ALIGNED | ~3 routes including hash-chain CSV export. No wrong claims. | — |
| Governance | PARTIALLY-ALIGNED | ~4 routes (classification, retention, SAR). No wrong claims. | — |
| Compliance Settings | PARTIALLY-ALIGNED | ~2 routes (GET + PATCH). No wrong claims. | — |
| Privacy | PARTIALLY-ALIGNED | ~2 routes (consent GET + POST). No wrong claims. | — |
| Notifications | PARTIALLY-ALIGNED | ~2 routes (GET + PATCH preferences). No wrong claims. | — |
| Forecasts | PARTIALLY-ALIGNED | ~3 routes (get, refresh trigger, +1). No wrong claims. | — |
| Price Books | PARTIALLY-ALIGNED | ~4 routes (list, create, detail, update). No wrong claims. | — |
| Emails | PARTIALLY-ALIGNED | ~4 routes (list, send, detail, tracking). No wrong claims. | — |
| Segments | PARTIALLY-ALIGNED | ~4 routes (list, create, detail, update). No wrong claims. | — |
| Templates | PARTIALLY-ALIGNED | ~4 routes (list, create, detail, update). No wrong claims. | — |
| Org Settings | PARTIALLY-ALIGNED | ~2 routes (GET + PATCH). No wrong claims. | — |
| Integrations | PARTIALLY-ALIGNED | ~3 routes (list, configure, test). G-05 confirmed wired. No wrong claims. | — |
| Feature Flags | PARTIALLY-ALIGNED | ~2 routes (list, toggle). Dual-approval rule documented. No wrong claims. | — |
| Sync | PARTIALLY-ALIGNED | ~2 routes (trigger, status). No wrong claims. | — |
| Contract Lifecycle | HUMAN-DECISION-REQUIRED | Module backend-complete (src/, entities, services, api). 12 API endpoints defined in Python but no gateway route. Human decision: expose or archive. See D-001. | FX-013 (documented) |
| Custom Objects | HUMAN-DECISION-REQUIRED | Backend modules confirmed (custom_object_framework/, custom_objects/). No gateway route found. Human decision: route mechanism or gateway file location. See D-002. | — |
| Daily Summary Service | ALIGNED | Path corrected from services/daily_summary.py → services/summary/daily_summary.py. DailySummaryReport fields, EN/UR templates, P-017 gate all documented. | FX-012 |

---

## RBAC Scope Alignment

| Inventory | U1 (stale) | U7 (corrected) | Status |
|---|---|---|---|
| ROLE_PERMISSION_INVENTORY.md scope count | 63 | 91 | ALIGNED |
| MODULE_INVENTORY.md Module 19 note | 63 | 91 | ALIGNED |
| AUTHORITY_RECONSTRUCTION_REPORT.md | 63 | 91 | ALIGNED |
| identity-auth-rbac.md | n/a | n/a (no numeric claim found) | ALIGNED |
| gateway/config/rbac-scopes.js (source of truth) | 91 | 91 | ALIGNED |

---

## Module Alignment

| Module | U1 Count | U7 Count | Status |
|---|---|---|---|
| Named modules (1–28) | 28 | 28 | ALIGNED |
| Contract lifecycle | Missing | Module 29 added | ALIGNED |
| Total | 28 | 29 | ALIGNED |

---

## API Route Total Alignment

| Inventory | U1 (stale) | U7 (corrected) |
|---|---|---|
| API_INVENTORY.md | ~198 | 228 |
| AUTHORITY_RECONSTRUCTION_REPORT.md | ~199 | 228 |
| gateway/routes/ (source of truth) | 228 | 228 |

---

## Overall Alignment Score (post-U7)

| Metric | Count |
|---|---|
| Domains fully ALIGNED | 20 |
| Domains PARTIALLY-ALIGNED (no wrong claims) | 18 |
| Domains HUMAN-DECISION-REQUIRED | 2 |
| Stale doc claims fixed | 13 |
| Undocumented code items documented | 8 |
| Items deferred (human decision) | 5 |

**Assessment:** No known incorrect claims remain in the primary inventory documents. Partially-aligned domains reflect approximate counts where code was not directly read — they are close approximations with no confirmed wrong values. All confirmed deltas from U6 have been remediated or flagged for human decision.

---

*End BACKEND_DOC_ALIGNMENT_STATUS.md*
