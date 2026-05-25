<!-- OWNERSHIP
PRIMARY FOR: Case entity schema and state machine; SLA timer logic (first-response and resolution windows); case routing and assignment rules; escalation ladder; CaseComment types (including resolution comment requirement); KB article linking; Urdu escalation keyword ("مینیجر سے بات کریں" — canonical here).
DEFERS TO: followup-enforcement-model.md (follow-up escalation — distinct system, do not merge); event-catalog.md (canonical event names: case.sla.first_response_breached.v1, case.sla.resolution_breached.v1); observability-audit.md (audit trail requirements); activities-tasks.md (ActivityEvent logging).
DO NOT RE-DEFINE: Follow-up escalation logic → followup-enforcement-model.md; generic activity/task definitions → activities-tasks.md; event payload schemas → event-catalog.md.
-->

# Cases / Support Ticket Domain Spec

## Purpose

This document is the canonical backend spec for the **Case Management Service** — the domain that handles support ticket lifecycle, SLA enforcement, case routing, escalation, and knowledge base article linking. It is the spec counterpart to `followup-enforcement-model.md` for the support domain.

**Build gates:** This doc must exist before any of the following pages can be implemented: B-05 `cases.html`, C-05 `cases-detail.html`, E-01 `support-console.html`, A-07 `support-dashboard.html`, I-04 `case-new.html`, C-12 `knowledge-article.html`.

---

## 1) Core Principles

### 1.1 Support Contract
- Every customer issue that enters the system becomes a **Case**.
- A Case is a first-class entity with a lifecycle, owner, SLA timer, and audit trail.
- No case can exist in an un-owned state for longer than the SLA first-response window.
- Resolution requires explicit confirmation — a case is not closed by inactivity.

### 1.2 Separation from Follow-up Escalation
The Case escalation ladder is distinct from the Follow-up escalation ladder:
- **Follow-up escalation** operates on lead inactivity (no action taken on a sales prospect).
- **Case escalation** operates on SLA breach (customer-facing support commitment not met).
- The two systems run independently. A lead closure does not affect open cases. A case closure does not affect follow-up tasks.

### 1.3 Non-negotiable Invariants
1. A Case must have an `assigned_to` field set within the first-response SLA window.
2. SLA timers start at `created_at` and pause only for explicit `WAITING_ON_CUSTOMER` state transitions.
3. A Case cannot transition to `resolved` unless at least one `CaseComment` of `comment_type = resolution` exists.
4. A Case cannot transition to `closed` unless it is in `resolved` state and `resolution_confirmed_at` is set.
5. Escalation events are immutable once created — they cannot be deleted, only superseded.
6. All `tenant_id` checks are enforced: agents can only view/action cases belonging to their own tenant.

---

## 2) Entity Model

### 2.1 Case

```
Case
├── case_id          : UUID (PK)
├── tenant_id        : str (FK → Tenant, required)
├── case_number      : str (human-readable, e.g. "CAS-2026-004821", unique per tenant)
├── subject          : str (max 255 chars)
├── description      : str (max 10,000 chars, optional)
├── status           : CaseStatus enum (see §3)
├── priority         : CasePriority enum (critical | high | medium | low)
├── source           : CaseSource enum (whatsapp | web_form | email | phone | internal)
├── category         : str (e.g. "billing", "technical", "onboarding", "product") — free string, tenant-configurable
├── contact_id       : UUID (FK → Contact, nullable — case may be pre-contact)
├── account_id       : UUID (FK → Account, nullable)
├── lead_id          : UUID (FK → Lead, nullable — case may originate from unresolved lead)
├── assigned_to      : UUID (FK → User, nullable before assignment)
├── assigned_team_id : UUID (FK → Team, nullable)
├── queue_id         : UUID (FK → SupportQueue, nullable)
├── sla_tier         : SLATier enum (tier_1_critical | tier_2_high | tier_3_standard | tier_4_low)
├── sla_first_response_due_at  : datetime (nullable until SLA tier resolved)
├── sla_resolution_due_at      : datetime (nullable until SLA tier resolved)
├── first_responded_at         : datetime (nullable until first response is sent)
├── resolved_at                : datetime (nullable)
├── resolution_confirmed_at    : datetime (nullable — set when customer confirms or auto-confirm window passes)
├── closed_at                  : datetime (nullable)
├── reopened_at                : datetime (nullable — set on most recent reopen)
├── reopen_count               : int (default 0)
├── escalation_level           : int (0 = none, 1–4 = escalation tier)
├── knowledge_article_ids      : UUID[] (linked knowledge base articles)
├── tags                       : str[] (tenant-defined labels)
├── custom_fields              : JSONB (extensible tenant-specific fields)
├── version_no                 : int (OCC concurrency control)
├── created_at                 : datetime
├── updated_at                 : datetime
├── created_by                 : UUID (FK → User)
└── updated_by                 : UUID (FK → User)
```

### 2.2 CaseComment

```
CaseComment
├── comment_id       : UUID (PK)
├── case_id          : UUID (FK → Case, required)
├── tenant_id        : str (required)
├── comment_type     : CommentType enum (internal_note | customer_reply | resolution | status_change | escalation_note)
├── body             : str (max 10,000 chars)
├── author_id        : UUID (FK → User, required)
├── is_visible_to_customer : bool (true for customer_reply / resolution; false for internal_note)
├── attachment_urls  : str[] (max 5 attachments, max 10MB each)
├── created_at       : datetime
└── updated_at       : datetime
```

**Constraints:**
- At least one `comment_type = resolution` comment must exist before `status → resolved` transition is permitted.
- `internal_note` comments are never surfaced to the customer-facing WhatsApp thread.
- Comments are immutable after creation (agents can only append, not edit).

### 2.3 CaseEscalation

```
CaseEscalation
├── escalation_id    : UUID (PK)
├── case_id          : UUID (FK → Case, required)
├── tenant_id        : str (required)
├── escalation_level : int (1–4)
├── escalation_reason: EscalationReason enum (sla_first_response_breach | sla_resolution_breach | customer_request | manager_override)
├── escalated_by     : UUID (FK → User, nullable — null if system-triggered)
├── escalated_to     : UUID (FK → User, nullable — the agent/manager escalated to)
├── escalated_to_team: UUID (FK → Team, nullable)
├── note             : str (optional context)
├── triggered_at     : datetime
└── resolved_at      : datetime (nullable — null if escalation is still active)
```

### 2.4 SupportQueue

```
SupportQueue
├── queue_id         : UUID (PK)
├── tenant_id        : str (required)
├── name             : str (e.g. "Tier 1 - General", "Tier 2 - Technical", "Billing")
├── description      : str (optional)
├── routing_strategy : RoutingStrategy enum (round_robin | least_loaded | skill_based | manual)
├── skill_tags       : str[] (for skill_based routing: required agent skill tags)
├── sla_tier_default : SLATier enum (applied to cases entering this queue with no explicit SLA tier)
├── team_id          : UUID (FK → Team, nullable — restrict queue to a specific team)
├── is_active        : bool
├── created_at       : datetime
└── updated_at       : datetime
```

### 2.5 SLAPolicy

```
SLAPolicy
├── policy_id        : UUID (PK)
├── tenant_id        : str (required)
├── sla_tier         : SLATier enum (unique per tenant — one policy per tier)
├── first_response_hours   : int (hours from case creation to first agent response)
├── resolution_hours       : int (hours from case creation to resolution)
├── business_hours_only    : bool (if true, SLA clock pauses outside business hours)
├── pause_on_waiting_customer : bool (if true, SLA clock pauses when status = WAITING_ON_CUSTOMER)
├── created_at       : datetime
└── updated_at       : datetime
```

**Default SLA tiers (Pakistan business hours = 9am–7pm PKT, Mon–Sat):**

| SLA Tier | First Response | Resolution | Notes |
|---|---|---|---|
| `tier_1_critical` | 1 hour | 8 hours | Business hours only. No pause on WAITING_ON_CUSTOMER. |
| `tier_2_high` | 4 hours | 24 hours | Business hours only. Pause on WAITING_ON_CUSTOMER. |
| `tier_3_standard` | 8 hours | 72 hours | Business hours only. Pause on WAITING_ON_CUSTOMER. |
| `tier_4_low` | 24 hours | 168 hours | Business hours only. Pause on WAITING_ON_CUSTOMER. |

---

## 3) State Machine

### 3.1 CaseStatus Enum

```
OPEN → ASSIGNED → IN_PROGRESS → WAITING_ON_CUSTOMER → IN_PROGRESS
                              → RESOLVED → CLOSED
                              → ESCALATED → ASSIGNED (re-assign after escalation)
```

**Full state list:**

| State | Meaning | Allowed transitions |
|---|---|---|
| `OPEN` | Case created; not yet assigned to an agent. | → `ASSIGNED` (on assignment), → `CLOSED` (admin-only, immediate close without resolution) |
| `ASSIGNED` | Agent assigned but not yet working. SLA first-response clock running. | → `IN_PROGRESS` (agent opens/responds), → `OPEN` (un-assign), → `ESCALATED` (SLA breach or manual) |
| `IN_PROGRESS` | Agent actively working. First response sent (stops first-response SLA). | → `WAITING_ON_CUSTOMER`, → `RESOLVED`, → `ESCALATED` |
| `WAITING_ON_CUSTOMER` | Awaiting customer response/action. SLA clock paused (if policy configured). | → `IN_PROGRESS` (customer replies), → `RESOLVED` (agent resolves without waiting), → `CLOSED` (auto-close after 7-day inactivity) |
| `RESOLVED` | Agent has provided resolution; awaiting customer confirmation or auto-confirm window. | → `CLOSED` (customer confirms or 48-hour auto-confirm window expires), → `IN_PROGRESS` (customer rejects/reopens within window) |
| `ESCALATED` | SLA has breached or manager has escalated. Visible in escalation queue. | → `ASSIGNED` (reassigned to new agent/team), → `IN_PROGRESS` (escalation recipient picks up) |
| `CLOSED` | Final terminal state. No further actions. Can be reopened by customer within 14 days. | → `OPEN` (reopen — increments `reopen_count`, clears `resolved_at` and `closed_at`) |

### 3.2 Transition Guards

| Transition | Guard |
|---|---|
| Any → `RESOLVED` | At least one `CaseComment.comment_type = resolution` must exist. |
| `RESOLVED` → `CLOSED` | `resolution_confirmed_at` must be set (customer confirmed OR 48-hour window passed). |
| Any → `CLOSED` (without RESOLVED) | Only `admin` role. Requires `close_reason` in request body. |
| `CLOSED` → `OPEN` (reopen) | Only within 14 days of `closed_at`. |
| `ESCALATED` → `ASSIGNED` | Requires new `assigned_to` or `assigned_team_id` in request body. |

---

## 4) SLA Enforcement

### 4.1 SLA Timer Rules
- SLA clock starts at `Case.created_at`.
- `sla_first_response_due_at` = `created_at` + SLA policy `first_response_hours` (adjusted for business hours if `business_hours_only = true`).
- `sla_resolution_due_at` = `created_at` + SLA policy `resolution_hours` (adjusted for business hours).
- When `status → WAITING_ON_CUSTOMER` and `pause_on_waiting_customer = true`: store pause timestamp; resolution SLA clock pauses.
- When `status → IN_PROGRESS` (from `WAITING_ON_CUSTOMER`): resume SLA clock from where it paused.
- `first_responded_at` is set on the first outbound `CaseComment.comment_type = customer_reply` by an agent (not internal notes). This stops the first-response SLA breach risk.

### 4.2 SLA Breach Events
- **First-response breach**: scanner job runs every 5 minutes; if `now() > sla_first_response_due_at` and `first_responded_at IS NULL` → emit `case.sla.first_response_breached` event; set `escalation_level = 1`.
- **Resolution breach**: if `now() > sla_resolution_due_at` and `status NOT IN (RESOLVED, CLOSED)` → emit `case.sla.resolution_breached` event; set `escalation_level = max(escalation_level, 2)`.

### 4.3 Business Hours Calculation
- Pakistan timezone: `UTC+5` (PKT, no DST).
- Business hours: 09:00–19:00 PKT, Monday–Saturday.
- Business-hours calculation: count only minutes within business hours windows when computing SLA deadlines.
- Holidays: not enforced in v1. Tracked in `backend/PENDING.md` for Phase 5.

---

## 5) Case Routing

### 5.1 Routing Pipeline

On case creation:
```
1. Source detection → set Case.source
2. Category mapping → determine target SupportQueue
3. SLA tier resolution → look up SLAPolicy for queue's sla_tier_default
4. Set sla_first_response_due_at + sla_resolution_due_at
5. Apply routing strategy for the target queue → assign Case.assigned_to or Case.assigned_team_id
6. Emit case.created + case.assigned events
```

### 5.2 Routing Strategies

**Round-robin:**
- Maintain a per-queue cursor pointing to the last assigned agent index.
- On assignment: advance cursor; assign to next available (active + not at capacity) agent in queue's team.
- Agent capacity: configurable `max_open_cases` per agent (default: 20). Skip over-capacity agents.

**Least-loaded:**
- Count `open_case_count` per agent in queue's team.
- Assign to agent with lowest count.
- Tie-break: alphabetical by `user_id` (deterministic).

**Skill-based:**
- Queue defines `skill_tags` (e.g., ["billing", "refunds"]).
- Eligible agents: members of queue's team where `User.skill_tags ⊇ queue.skill_tags`.
- Among eligible agents, apply round-robin sub-strategy.
- If no eligible agents: fall back to least-loaded from full team; set `Case.tags += ["skill_gap"]` for visibility.

**Manual:**
- Case is created with `status = OPEN`, `assigned_to = null`.
- Appears in supervisor's unassigned queue. Supervisor manually assigns.

### 5.3 Re-routing on Escalation
When `status → ESCALATED`:
1. Create `CaseEscalation` record.
2. If `escalated_to` is set: assign case to that user directly.
3. If `escalated_to_team` is set: re-enter routing pipeline for that team using least-loaded strategy.
4. If neither is set: assign to queue supervisor (first active user with `supervisor` role in queue's team).

---

## 6) Escalation Rules

### 6.1 Escalation Ladder (Cases)

| Level | Trigger | Action |
|---|---|---|
| 0 | No breach | Normal operation. |
| 1 | First-response SLA breached | Notify assigned agent + queue supervisor. WhatsApp alert to agent. |
| 2 | Resolution SLA breached (first 25%) | Notify supervisor. Case surfaced in escalation view. |
| 3 | Resolution SLA breached (50%) | Notify manager. Case assigned to Tier 2 / senior agent. `case.sla.critical` event emitted. |
| 4 | Resolution SLA breached (100%) | Notify tenant admin. Case escalated to manual queue with VIP flag. |

**Timing rule:** Resolution SLA milestones use percentage of total resolution window, not fixed hours. Example: for `tier_3_standard` (72h resolution), Level 3 triggers at T+36h.

### 6.2 Customer-Requested Escalation
- Customer can request escalation via WhatsApp keyword "ESCALATE" or "مینیجر سے بات کریں" (Urdu: speak to manager).
- System creates `CaseEscalation.escalation_reason = customer_request`; `escalation_level = max(current, 3)`.
- Notifies supervisor immediately (does not wait for SLA breach).

### 6.3 Manager Override Escalation
- Agents with `manager` or `admin` role can POST `/api/v1/cases/{id}/escalate` with `escalation_reason = manager_override`.
- This bypasses SLA timers and immediately creates a level-3 escalation.

---

## 7) Knowledge Base Article Linking

### 7.1 KnowledgeArticle Entity (abridged)

```
KnowledgeArticle
├── article_id       : UUID (PK)
├── tenant_id        : str (required)
├── title            : str (max 255)
├── body             : str (markdown, max 100,000 chars)
├── category         : str (aligned with Case.category values)
├── tags             : str[]
├── status           : ArticleStatus enum (draft | published | archived)
├── language         : str ("en" | "ur")
├── author_id        : UUID (FK → User)
├── published_at     : datetime (nullable)
├── view_count       : int (read-only, incremented on read)
├── helpful_count    : int (customer thumbs-up)
├── not_helpful_count: int (customer thumbs-down)
├── created_at       : datetime
└── updated_at       : datetime
```

### 7.2 Article Suggestion at Case Creation
- On `POST /api/v1/cases`, the system performs a synchronous keyword lookup against published `KnowledgeArticle` records matching `Case.category` + top 3 words from `Case.subject`.
- Up to 3 suggested articles are returned in the case creation response (`suggested_articles: [...]`).
- Agents can link suggestions to the case by POST `/api/v1/cases/{id}/link-article`.

### 7.3 Article Linking
- `Case.knowledge_article_ids` stores linked article IDs.
- When an article is linked, `KnowledgeArticle.view_count` is incremented.
- Agents can surface linked articles directly to customers as part of a `CaseComment.comment_type = customer_reply`.

---

## 8) API Endpoints

### Cases Resource

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/cases` | JWT | `agent`, `manager`, `admin`, `sales_rep` | Create new case. Returns case + suggested articles. |
| `GET` | `/api/v1/cases` | JWT | Any authenticated | List cases (filtered by tenant; scoped by role — agent sees assigned cases + unassigned queue; manager/admin sees all). |
| `GET` | `/api/v1/cases/{id}` | JWT | Any authenticated | Case detail with full comment thread and escalation history. |
| `PATCH` | `/api/v1/cases/{id}` | JWT | `agent`, `manager`, `admin` | Update case fields (subject, priority, category, custom_fields). Requires `version_no`. |
| `POST` | `/api/v1/cases/{id}/assign` | JWT | `manager`, `admin` | Assign or reassign case to agent/team. |
| `POST` | `/api/v1/cases/{id}/comments` | JWT | `agent`, `manager`, `admin` | Add comment (internal note or customer reply). |
| `POST` | `/api/v1/cases/{id}/resolve` | JWT | `agent`, `manager`, `admin` | Transition to `RESOLVED`. Requires resolution comment in body. |
| `POST` | `/api/v1/cases/{id}/close` | JWT | `manager`, `admin` | Force-close (admin). |
| `POST` | `/api/v1/cases/{id}/reopen` | JWT | Any authenticated | Reopen within 14-day window. |
| `POST` | `/api/v1/cases/{id}/escalate` | JWT | `manager`, `admin` | Manager-override escalation. |
| `POST` | `/api/v1/cases/{id}/link-article` | JWT | `agent`, `manager`, `admin` | Link knowledge article to case. |

### Knowledge Base Resource

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/knowledge/articles` | JWT | `manager`, `admin` | Create draft article. |
| `GET` | `/api/v1/knowledge/articles` | JWT | Any authenticated | List published articles (filtered by category/tags). |
| `GET` | `/api/v1/knowledge/articles/{id}` | JWT | Any authenticated | Article detail. |
| `PATCH` | `/api/v1/knowledge/articles/{id}` | JWT | `manager`, `admin` | Update article. |
| `POST` | `/api/v1/knowledge/articles/{id}/publish` | JWT | `manager`, `admin` | Publish draft article. |

### Support Queue Resource

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/support/queues` | JWT | `manager`, `admin` | List queues for tenant. |
| `POST` | `/api/v1/support/queues` | JWT | `admin` | Create support queue. |
| `PATCH` | `/api/v1/support/queues/{id}` | JWT | `admin` | Update queue settings. |

---

## 9) RBAC Role Gates

| Operation | `sales_rep` | `agent` | `manager` | `admin` |
|---|---|---|---|---|
| Create case | ✓ (own leads only) | ✓ | ✓ | ✓ |
| View case list | Own only | Assigned + unassigned queue | All | All |
| View case detail | If creator | If assigned or in team | All | All |
| Add comment | If creator | If assigned | All | All |
| Assign / reassign | — | — | ✓ | ✓ |
| Resolve case | — | ✓ | ✓ | ✓ |
| Force-close | — | — | ✓ | ✓ |
| Escalate (manager override) | — | — | ✓ | ✓ |
| Manage queues | — | — | — | ✓ |
| Manage SLA policies | — | — | — | ✓ |
| Publish knowledge articles | — | — | ✓ | ✓ |

---

## 10) Events Emitted

All events follow the `observability-audit.md` structured event schema.

| Event | Trigger |
|---|---|
| `case.created` | Case creation. |
| `case.assigned` | Case assigned to agent/team. |
| `case.commented` | Comment added (type = customer_reply only — internal notes emit `case.internal_note_added` which is audit-log only). |
| `case.status_changed` | Any state transition. Includes `from_status`, `to_status`. |
| `case.sla.first_response_breached.v1` | First-response deadline missed. |
| `case.sla.resolution_breached.v1` | Resolution deadline missed (emitted at each escalation level threshold: 25%, 50%, 100%). |
| `case.escalated` | Escalation created (system or manual). |
| `case.resolved` | Status → RESOLVED. |
| `case.closed` | Status → CLOSED. |
| `case.reopened` | Case reopened from CLOSED. |
| `case.article_linked` | Knowledge article linked to case. |
| `knowledge_article.published` | Article moves from draft → published. |

---

## 11) Scanner Jobs

### 11.1 SLA Monitor Job
- **Schedule:** Every 5 minutes.
- **Action:**
  1. Query `Case WHERE status NOT IN (RESOLVED, CLOSED)`.
  2. For each case: evaluate first-response breach and resolution breach milestones.
  3. Emit breach events and update `escalation_level` as required.
  4. Insert `CaseEscalation` records for newly breached levels.

### 11.2 Auto-Close Job
- **Schedule:** Every hour.
- **Action:**
  1. Query `Case WHERE status = WAITING_ON_CUSTOMER AND updated_at < now() - INTERVAL 7 days`.
  2. Transition to `CLOSED` with comment: "Auto-closed: no customer response in 7 days."
  3. Emit `case.closed` event.

### 11.3 Resolution Confirm Auto-Close Job
- **Schedule:** Every hour.
- **Action:**
  1. Query `Case WHERE status = RESOLVED AND resolved_at < now() - INTERVAL 48 hours AND resolution_confirmed_at IS NULL`.
  2. Set `resolution_confirmed_at = now()`. Transition to `CLOSED`.
  3. Emit `case.closed` event.

---

## 12) Implementation Acceptance Checklist

- [ ] `Case` entity created with all fields; `CaseComment`, `CaseEscalation`, `SupportQueue`, `SLAPolicy` entities created.
- [ ] State machine transitions enforced in service layer — invalid transitions return `422`.
- [ ] SLA timer computation correct for Pakistan business hours (PKT, Mon–Sat 09:00–19:00).
- [ ] SLA clock pauses correctly on `WAITING_ON_CUSTOMER` transition when policy `pause_on_waiting_customer = true`.
- [ ] `RESOLVED` guard: requires resolution comment, else `422`.
- [ ] `CLOSED` guard: requires `resolution_confirmed_at` or admin role.
- [ ] Escalation ladder fires at correct breach percentages.
- [ ] Customer escalation via "ESCALATE" / "مینیجر سے بات کریں" keywords is handled.
- [ ] Knowledge article suggestion returns ≤3 results on case creation.
- [ ] All API endpoints respect RBAC role gates (table in §9).
- [ ] All events in §10 emitted via activity log.
- [ ] Scanner jobs (SLA monitor, auto-close, resolution confirm) scheduled and testable.
- [ ] `tenant_id` isolation enforced on all list endpoints.
- [ ] `version_no` OCC on PATCH operations.
