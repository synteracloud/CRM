# Constraints Register

**Purpose:** Known limitations, architectural decisions with trade-offs, and anything that will require rework if not addressed at the right build stage.
**Updated:** 2026-04-09
**Rule:** Read this before starting a new build layer. Constraints marked CRITICAL must be resolved before the relevant layer begins — they cannot be retrofitted cheaply.

---

## UI / Frontend Constraints

### C-001 — RTL layout must be in component architecture from day 1
**Severity:** CRITICAL
**Layer:** UI
**Status:** OPEN — must be resolved before UI component architecture is finalised

Bilingual support (EN/UR) requires RTL layout for Urdu. This is not a CSS toggle — it affects:
- Flex direction on all row layouts
- Text alignment on all text components
- Icon placement (back arrows, chevrons, action icons flip)
- Form field order (labels, inputs, error messages)
- Navigation direction

**If added after the UI is built:** Every layout component needs structural changes. Estimated rework: 30-50% of all UI components.

**Resolution:** Use a CSS-in-JS or Tailwind `dir` strategy from the first component. Set `dir="rtl"` at root when `locale = "ur"`. All flex layouts must use `start/end` not `left/right`. Validate with an Urdu test string in every screen during development.

**Reference:** docs/pakistan-adapter-architecture.md §3 — E) Bilingual Support

---

### C-002 — Feature visibility ordering cannot be layered on top of a flat nav
**Severity:** HIGH
**Layer:** UI
**Status:** OPEN — must be resolved before navigation architecture is finalised

The 4-tier progressive disclosure model (docs/adoption-ux.md) requires that Tier 2-4 features are not shown until conditions are met. If the navigation is built as a flat menu and visibility tiers are added later, it requires:
- Rework of the navigation component
- Addition of a feature-visibility state machine or feature flag checks at render time
- Possible restructuring of routes

**Resolution:** Design navigation to accept a visibility tier per item from the start. Each nav item has a `tier` property; the renderer filters by user's current tier. Tier promotion rules live in one place (`adoption-ux.md` defines them).

**Reference:** docs/adoption-ux.md — Feature Visibility Ordering

---

### C-003 — ≤2 steps rule must be validated during UI design, not after
**Severity:** HIGH
**Layer:** UI
**Status:** OPEN — process constraint, not a code constraint

The ≤2 steps rule (docs/ui-foundations.md §6) cannot be verified by reading code — it requires user journey mapping. If flows are designed without this constraint, rework means redesigning navigation, merging screens, or removing confirmation steps.

**Resolution:** Add step count annotation to every user journey wireframe. Gate UI design sign-off on step count compliance before implementation starts.

**Reference:** docs/ui-foundations.md §6

---

## Backend / Service Layer Constraints

### C-004 — In-memory stores are not production-safe (all services)
**Severity:** CRITICAL
**Layer:** Backend
**Status:** OPEN — all Python services

All Python service layers (`FollowupEnforcementEngine`, `ConversationalCRMService`, `CollectionsService`, `LeadsRepository`, `ActivityControlEngine`, `SyncService`) use in-memory dicts/lists as their store. Data is lost on process restart.

**Impact:** No persistence, no multi-instance support, no horizontal scaling.

**Resolution:** Each service's store must be replaced with a DB-backed repository. Schemas already exist (`db/` directory). The gateway DB pattern (`gateway/db/repositories/leads.repository.js`) is the reference. Python services need equivalent DB clients or ORM layer.

**Pending link:** P-001, P-002, P-003

---

### C-005 — enforcement_level is per-engine-instance, not persisted per tenant
**Severity:** HIGH
**Layer:** Backend
**Status:** OPEN

`FollowupEnforcementEngine` accepts `enforcement_level` as a constructor argument. There is no mechanism to:
- Persist enforcement phase per tenant in the DB
- Auto-graduate a tenant from `soft` → `medium` → `strict` based on `created_at`
- Allow admin override of enforcement level

**Impact:** Without this, all tenants get the same enforcement level at runtime — likely `strict` (the default), which contradicts the ramp-up model for new tenants.

**Resolution:** Add `enforcement_level` field to tenant config table (`org_tenant_db/schema.sql`). Calculate at engine instantiation: read tenant `created_at`, compute days since creation, derive phase. Store override if admin has manually set it.

**Pending link:** P-007

---

### C-006 — _DictEventStore / _DictLedgerStore are temporary shims
**Severity:** HIGH
**Layer:** Backend
**Status:** OPEN

`services/collections/service.py` uses two shim classes to wrap the existing in-memory dicts in the store interface required by `record_payment_event_uow`. These are explicitly marked as temporary. They have no persistence and no error handling.

**Risk:** The UoW is wired and correct in structure, but the shims mean it provides no real ACID guarantees — if the process crashes between the event write and the ledger write, neither is persisted.

**Resolution:** Replace shims with real DB repository objects once `collections.repository.js` (or Python equivalent) is built.

**Pending link:** P-003

---

### C-007 — chain-check audit endpoint returns stub when activity service is down
**Severity:** MEDIUM
**Layer:** Backend / Infrastructure
**Status:** OPEN

`GET /audits/chain-check` in `gateway/routes/v1-audit.routes.js` calls the activity service. When the activity service is unreachable, it returns a stub response with `{ valid: true, note: "activity service unreachable" }`. This silently masks audit failures — a degraded audit endpoint looks like a passing one.

**Risk:** In a security/compliance context, a stub "valid" response is worse than an error. Auditors may see "valid" and not investigate further.

**Resolution:** When activity service is unreachable, return HTTP 503 with `{ valid: false, error: "AUDIT_SERVICE_UNAVAILABLE" }` instead of stub. Only return `valid: true` when a real check was performed.

**Pending link:** P-005

---

### C-008 — Feature flag evaluation not implemented
**Severity:** MEDIUM
**Layer:** Backend
**Status:** OPEN

Feature flags are referenced in adapters (compliance adapter is feature-flagged; fuzzy name match is feature-flagged) but there is no evaluation engine. All feature-flagged code currently uses hardcoded fallback behaviour (the flag is effectively always `false`/disabled).

**Impact:** No controlled rollout capability. Cannot A/B test or safely enable features per tenant without deploying new code.

**Resolution:** Build `services/feature_flags/evaluator.py` before any feature-flagged code path needs to be enabled in production.

**Pending link:** P-010

---

## Integration / Provider Constraints

### C-009 — JazzCash / Easypaisa: stub_mode=True is default, live mode untested
**Severity:** HIGH
**Layer:** Integration
**Status:** OPEN

`PakistanPaymentAdapter` and both provider adapters default to `stub_mode=True`. The live code path (`_create_payment_live()`) was written but has never been executed against real or sandbox endpoints.

**Risk:** HMAC signing logic, field ordering, and response parsing may have undiscovered bugs that only appear against the real API.

**Hard rule:** Never set `stub_mode=False` in production without first running against the provider sandbox with real credentials and verifying the full payment → webhook → reconciliation cycle end-to-end.

**Pending link:** P-016

---

### C-010 — Urdu strings are unreviewed and must not go to production as-is
**Severity:** HIGH
**Layer:** Content / Localisation
**Status:** OPEN — hard pre-launch gate

All Urdu strings in `adapters/pakistan/localization/pakistan_locale_adapter.py` (`_STRINGS["ur"]`) are machine-translated placeholders. They are Unicode-valid but linguistically unverified. Incorrect or awkward Urdu in customer-facing payment reminders will damage brand trust in the Pakistan market.

**Hard rule:** All `_STRINGS["ur"]` values must be reviewed and approved by a native Urdu speaker before any Urdu-locale messages are sent to customers.

**Pending link:** P-017

---

### C-011 — Phone formatter only handles Pakistani national format (03xx)
**Severity:** MEDIUM
**Layer:** Backend / Localisation
**Status:** OPEN — low priority until international numbers are needed

`adapters/pakistan/localization/pakistan_phone_formatter.py` normalises `03xx-xxxxxxx` → `+923xxxxxxxxx`. It does not handle:
- Numbers already in E.164 format (`+92...`)
- International callers (non-Pakistan country codes)
- Landline numbers
- Numbers with spaces, dashes, or parentheses in non-standard positions

**Impact:** Any non-standard input format will either fail silently or produce an incorrect E.164 string, breaking the `detect_duplicate_contact()` dedup (which keys on E.164).

**Resolution:** Add E.164 pass-through detection (if starts with `+`, validate and return as-is). Add basic sanitisation (strip whitespace, dashes, parentheses) before pattern matching.

---

## Data / Schema Constraints

### C-012 — DB schemas are PostgreSQL-only
**Severity:** LOW (known decision)
**Layer:** Data
**Status:** ACCEPTED TRADE-OFF

All 11 DB schemas (`db/` directory) use PostgreSQL-specific features: `pgcrypto`, `gen_random_uuid()`, `GENERATED ALWAYS AS`, row-level security hooks, and `NO UPDATE / NO DELETE` rules on audit log. These are intentional choices for data integrity.

**Impact:** Cannot switch to MySQL, SQLite, or any non-Postgres store without rewriting schemas and losing some integrity guarantees.

**Resolution:** This is an accepted constraint. Document that PostgreSQL ≥14 is a hard infrastructure requirement.

---

### C-013 — Audit log uses NO UPDATE / NO DELETE rules — cannot correct mistakes
**Severity:** MEDIUM
**Layer:** Data
**Status:** ACCEPTED TRADE-OFF — with operational implication

`db/audit_compliance_db/schema.sql` enforces `NO UPDATE` and `NO DELETE` rules on `audit_log`. This is correct for tamper-evidence but means:
- Incorrect audit entries cannot be corrected in-place
- A correction requires an additional "correction" audit entry
- Ops teams must be trained on this constraint to avoid confusion

**Resolution:** Document the correction process: incorrect entries are never deleted; a `CORRECTION` event type is appended referencing the original `event_id`. Ensure all ops runbooks reflect this.

---

## UI / Archetype Constraints
*Identified during archetype overlay (2026-04-02). Apply when building page archetypes.*

### C-014 — Enterprise features must be Tier 3/4 visibility — not shown to new Pakistan SMB users
**Severity:** HIGH
**Layer:** UI
**Status:** OPEN — apply during archetype build

The archetype defines 75 pages across 11 archetypes. Many of these are enterprise features that conflict with the Behaviour spec's progressive disclosure model if shown to new users. The following archetype pages must be **Tier 3 or Tier 4** (hidden until promoted):

| Page | Archetype | Reason |
|---|---|---|
| AI Copilot Insight Panel | §11 AI/Copilot | No relevance until user has data history |
| Predictive Forecasting, AI Scoring, Predictive Models | §5 Reporting | Requires data volume Pakistan SMB won't have on day 1 |
| Knowledge Effectiveness, Knowledge Article | §1 Dashboard, §3 Entity Detail | Knowledge base is enterprise feature |
| Campaign Detail, Campaign Journey Builder | §3 Entity Detail, §8 Builder | Marketing automation is post-core adoption |
| Partner Profile, Partner List | §2 List, §3 Entity Detail | Channel management is enterprise tier |
| Custom Object Framework Admin | §4 Settings | Power user / admin only |
| Plugin Framework | §4 Settings | Developer / integrator only |
| Territory Management | §4 Settings | Enterprise org structure feature |
| Contract Detail, Contract Lifecycle Form | §3 Entity Detail, §6 Form | Enterprise contract management |
| Revenue Recognition, Usage Billing Analytics | §5 Reporting | Enterprise billing complexity |

**Pakistan SMB Tier 1 pages (always visible from session 1):**
WhatsApp/Messaging Thread, Lead Queue, Lead Detail, Followup Queue, Collections Queue, Invoice Queue, Customer 360, Activity Feed.

**Reference:** `docs/adoption-ux.md` — Feature Visibility Ordering

---

### C-015 — `src/` enterprise layer has no gateway routes — UI cannot call these services yet
**Severity:** HIGH
**Layer:** UI / Backend
**Status:** OPEN — blocks UI build for enterprise archetype pages

35 `src/` modules (AI copilot, campaigns, tickets, knowledge, etc.) have Python implementations but zero gateway routes. Any archetype page backed by a `src/` module cannot be wired to real data until HTTP routes are built.

**Impact on UI build:** Enterprise archetype pages can be built as UI shells with mock data, but live wiring requires backend work first (pending P-019/P-020 pattern applied to `src/` modules).

**Reference:** `PENDING.md` P-019 — Python HTTP layer

---

### C-016 — `src/` modules have no DB schemas for 8 domains — data will not persist
**Severity:** HIGH
**Layer:** Data
**Status:** RESOLVED — 2026-04-09 (Group 4 — P-025 to P-030)

All 6 missing schemas have been created:

| Domain | Schema file | P item |
|---|---|---|
| Tickets / Cases | `db/case_ticket_db/schema.sql` | P-025 |
| Knowledge Base | `db/knowledge_db/schema.sql` | P-026 |
| Campaigns + Journeys | `db/campaign_db/schema.sql` | P-027 |
| Territories | `db/territory_db/schema.sql` | P-028 |
| AI / Intelligence | `db/intelligence_db/schema.sql` | P-029 |
| Usage Billing | `db/transaction_db/migrations/0004_add_usage_billing.up.sql` | P-030 |

**Remaining risk:** `src/` service classes still use in-memory state — they need DB client wiring before schemas are utilised. Schema files are ready; wire-up is a future task when `src/` services get HTTP layers.

---

### C-017 — Two parallel Python layers (services/ and src/) must not diverge
**Severity:** MEDIUM
**Layer:** Backend
**Status:** RESOLVED — 2026-04-02 (Round 0 of src/ overlay)

The repo has two Python service layers:
- `services/` — core Pakistan CRM execution (leads, followup, collections, conversation, sync)
- `src/` — enterprise depth features (tickets, campaigns, AI, knowledge, billing)

**Overlap decision (finalised):**
- `src/lead_management/` vs `services/leads/`: **Complementary, not competing.** `services/leads/` is the WhatsApp capture and routing layer. `src/lead_management/` is the CRM domain model layer. Wiring rule: WhatsApp inbound → `services/leads/` → `src/lead_management/` entity model. Do not merge.
- `src/workflow_engine/` vs `services/workflow/`: **Complementary.** `services/workflow/` is execution orchestration; `src/workflow_engine/` is the rule-based workflow definition model. Both are needed and serve different layers.

**Remaining risk:** Do not wire both overlap pairs to the same gateway routes. Respect the layer boundary when building P-019/P-020 HTTP wiring.
