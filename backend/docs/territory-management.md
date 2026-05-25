# Territory Management Spec

## Purpose

This document is the canonical spec for the **Territory & Assignment Service** — the domain that defines geographic and logical sales territories, routes leads and accounts to the correct owner, and scopes dashboards to territory boundaries. The `TerritoryRule` entry in `domain-model.md` is a pointer; this document contains the full definition.

**Build gate:** This doc must exist before G-09 `territories.html` can be implemented. It is also required before any territory-scoped dashboard view or lead auto-assignment by territory can be built.

---

## 1) Core Principles

### 1.1 Territory Model
A **Territory** is a named scope that determines ownership responsibility. Territories are:
- Named and hierarchical (parent → child nesting supported).
- Assigned to one or more sales reps and one primary manager.
- Rule-based: a set of `TerritoryRule` criteria determines which leads/accounts belong to this territory.
- Mutually exclusive by design at the leaf level — every subject (lead or account) should resolve to at most one owner territory. Conflict resolution handles exceptions.

### 1.2 Non-negotiable Invariants
1. Every lead must have a territory assignment within 1 minute of creation (scanner auto-assigns within 1-minute SLA).
2. If no matching territory exists for a lead, it goes to the **default territory** (one must always be configured per tenant).
3. A `TerritoryAssignment` record is immutable once created; re-assignment creates a new record (old one is superseded, not deleted).
4. Territory-scoped queries must use the `TerritoryAssignment` table as the source of truth — never re-evaluate criteria at query time.
5. `tenant_id` isolation enforced on all territory entities.

---

## 2) Entity Model

### 2.1 Territory

```
Territory
├── territory_id     : UUID (PK)
├── tenant_id        : str (required)
├── name             : str (max 100 chars — e.g. "Lahore North", "Karachi Korangi Industrial")
├── description      : str (optional, max 500 chars)
├── parent_id        : UUID (FK → Territory, nullable — null for root territories)
├── criteria_type    : TerritoryCriteriaType enum (see §2.2)
├── criteria_value   : JSONB (schema depends on criteria_type — see §2.2)
├── assigned_reps    : UUID[] (FK → User — sales reps responsible for this territory)
├── primary_manager  : UUID (FK → User, nullable — manager who sees territory dashboard)
├── is_default       : bool (exactly one territory per tenant must have is_default=true)
├── is_active        : bool (inactive territories stop receiving new assignments)
├── routing_priority : int (lower = higher priority; used for conflict resolution — see §5)
├── created_by       : UUID (FK → User)
├── created_at       : datetime
└── updated_at       : datetime
```

**Hierarchy constraint:** Maximum 3 levels (root → region → area). No deeper nesting to prevent routing complexity.

**Default territory invariant:** Exactly one `Territory.is_default = true` must exist per tenant at all times. Setting a new territory as default atomically unsets any previous default (checked in service layer, enforced in DB via partial unique index: `WHERE is_default = true`).

### 2.2 TerritoryRule

A `TerritoryRule` is a single criteria clause within a `Territory`. Multiple rules on a territory combine with AND logic (all must match for a subject to belong to that territory).

```
TerritoryRule
├── rule_id          : UUID (PK)
├── territory_id     : UUID (FK → Territory, required)
├── tenant_id        : str (required)
├── rule_type        : TerritoryRuleType enum (see below)
├── field            : str (the entity field being evaluated)
├── operator         : RuleOperator enum (eq | in | not_in | starts_with | contains | geo_within)
├── value            : JSONB (value schema depends on rule_type + operator)
├── created_at       : datetime
└── updated_at       : datetime
```

### 2.3 TerritoryCriteriaType and TerritoryRuleType

**TerritoryCriteriaType** (the `Territory.criteria_type` field — describes the primary grouping dimension):

| Type | Description |
|---|---|
| `geographic` | City, region, or GPS polygon-based |
| `postal` | Pakistan postal code ranges |
| `account_segment` | Account industry, size, or tier |
| `rep_assigned` | Manual assignment to specific reps; rules are advisory only |
| `hybrid` | Combination of multiple rule types |

**TerritoryRuleType** (the `TerritoryRule.rule_type` field — the specific matching criterion):

| rule_type | field examples | operator options | value schema |
|---|---|---|---|
| `city` | `lead.city` or `account.city` | `eq`, `in`, `not_in` | `{ "cities": ["Lahore", "Sheikhupura"] }` |
| `postal_code` | `lead.postal_code` | `eq`, `in`, `starts_with` | `{ "codes": ["54000", "54600"] }` |
| `region` | `lead.province` or `account.province` | `eq`, `in` | `{ "provinces": ["Punjab", "KPK"] }` |
| `geo_polygon` | `lead.lat_lng` | `geo_within` | `{ "polygon": [[lat,lng], [lat,lng], ...] }` (GeoJSON polygon) |
| `account_industry` | `account.industry` | `eq`, `in` | `{ "industries": ["FMCG", "Pharma"] }` |
| `account_size` | `account.employee_count` | `eq`, `in` | `{ "sizes": ["1-10", "11-50", "51-200"] }` |
| `account_tier` | `account.tier` | `eq`, `in` | `{ "tiers": ["enterprise", "mid_market"] }` |
| `rep_explicit` | (no field) | (no operator — direct assignment) | `{ "rep_ids": ["uuid1", "uuid2"] }` |
| `custom_field` | any `lead.custom_fields.key` | `eq`, `contains`, `in` | `{ "key": "channel", "match_values": ["distributor"] }` |

### 2.4 TerritoryAssignment

```
TerritoryAssignment
├── assignment_id    : UUID (PK)
├── tenant_id        : str (required)
├── subject_type     : SubjectType enum (lead | account | contact)
├── subject_id       : UUID (FK → the subject entity)
├── territory_id     : UUID (FK → Territory)
├── assigned_rep_id  : UUID (FK → User, nullable — the specific rep within the territory)
├── assignment_reason: AssignmentReason enum (auto_rule_match | manual_override | conflict_resolution | default_fallback)
├── superseded_by    : UUID (FK → TerritoryAssignment, nullable — points to the new record that replaced this one)
├── is_active        : bool (only one active assignment per subject at any time)
├── effective_at     : datetime
├── created_by       : UUID (FK → User, nullable — null if system-assigned)
└── created_at       : datetime
```

**Active assignment invariant:** Only one `TerritoryAssignment` with `is_active = true` may exist per `(tenant_id, subject_type, subject_id)` at a time. Enforced via partial unique index.

---

## 3) Territory Criteria Evaluation

### 3.1 Evaluation Pipeline

On lead or account creation (or field update that affects territory criteria):

```
1. Load all active territories for tenant (ordered by routing_priority ASC)
2. For each territory (in priority order):
   a. Load all TerritoryRules for the territory
   b. Evaluate each rule against the subject's fields
   c. ALL rules must match (AND logic) for the territory to be a candidate
3. Collect matching territories
4. Apply conflict resolution (see §5)
5. Create TerritoryAssignment record for winning territory
6. Within the winning territory: apply rep assignment strategy (see §4)
7. Emit territory.assigned event
```

### 3.2 Rule Evaluation

**City matching example:**
```
TerritoryRule: rule_type=city, field=lead.city, operator=in, value={ "cities": ["Lahore", "Shahdara"] }
Subject: lead.city = "Lahore"
Result: MATCH
```

**Postal code matching example:**
```
TerritoryRule: rule_type=postal_code, field=lead.postal_code, operator=starts_with, value={ "codes": ["546"] }
Subject: lead.postal_code = "54680"
Result: MATCH (starts_with "546")
```

**Geo polygon matching** (Phase 5 feature; not implemented in v1):
- Requires `lead.latitude` and `lead.longitude` to be populated (from field check-in or geocoding).
- Uses PostgreSQL `ST_Within()` for geo containment check.
- In v1: `geo_polygon` rule type resolves to NO MATCH if `lat_lng` is null on the subject; falls through to lower-priority territories.

### 3.3 Criteria Evaluation Scope

Territory evaluation applies to:
- `Lead` entities (on creation and on `city`/`province`/`postal_code` field update).
- `Account` entities (on creation and on `city`/`province`/`industry`/`tier` field update).
- `Contact` entities follow their parent `Account` territory (not independently assigned).

---

## 4) Rep Assignment Within Territory

Once a territory is matched, the winning rep within `territory.assigned_reps[]` is determined:

### 4.1 Rep Assignment Strategy

| Strategy | Logic |
|---|---|
| `round_robin` (default) | Cycle through `assigned_reps[]` in order; persist cursor in `territory_rep_cursor` (Redis or DB). |
| `least_loaded` | Count open leads per rep in this territory; assign to rep with fewest. |
| `explicit_rule` | If `TerritoryRule.rule_type = rep_explicit` matched, use `value.rep_ids[0]` directly. |

**Strategy configuration:** `Territory.routing_priority` defines territory priority; rep strategy is configured per territory as an additional field (Phase 4 Sprint 2 enhancement; for v1, `round_robin` is the default for all territories).

### 4.2 Single-Rep Territory

If `territory.assigned_reps` contains exactly one rep, all leads assigned to this territory go to that rep. No strategy calculation needed.

### 4.3 No Available Reps

If all reps in `assigned_reps[]` are inactive or over capacity (more than `max_leads_per_rep` open leads, default 100):
1. Try parent territory's reps (if hierarchy exists).
2. If still no available rep: assign to territory's `primary_manager`.
3. If no manager: assign to default territory's reps.
4. Set `TerritoryAssignment.assignment_reason = default_fallback`.
5. Emit `territory.assignment_fallback` event for supervisor alerting.

---

## 5) Conflict Resolution

A lead matches multiple territories when their criteria overlap (e.g., two territories both cover Lahore).

### 5.1 Priority-Based Resolution

Territories have a `routing_priority` integer field (1 = highest priority). When multiple territories match:
1. Select the territory with the lowest `routing_priority` value (highest priority).
2. If tie on priority: select the more specific territory (one with more `TerritoryRule` criteria).
3. If still tied: select the territory with the lower `territory_id` UUID (deterministic tiebreaker).

### 5.2 Conflict Event

On conflict resolution:
- Emit `territory.conflict_resolved` event with `{ subject_id, matched_territories: [...], winning_territory_id, resolution_reason: "priority_order" | "rule_specificity" | "uuid_tiebreak" }`.
- Log to `AuditLog` for administrator review.

### 5.3 Manual Override

Managers and admins can manually reassign territory via `POST /api/v1/territories/assignments/{id}/reassign`:
- Creates new `TerritoryAssignment` with `assignment_reason = manual_override`.
- Sets old assignment `is_active = false` and `superseded_by = new_assignment_id`.
- Emits `territory.manually_reassigned` event.
- Manual overrides are sticky: the next auto-routing event will NOT override a manually set assignment (checked by `assignment_reason` on latest active record).

---

## 6) Territory-Scoped Dashboard Views

### 6.1 Scoping Rule

All dashboard queries for users with `sales_rep` role are automatically filtered to leads/accounts where `TerritoryAssignment.assigned_rep_id = current_user.id`.

All dashboard queries for users with `manager` role who have a territory assignment (`primary_manager` on a Territory):
- See all data within their assigned territory's subtree (including child territories if hierarchy exists).
- Cross-territory visibility is NOT granted to managers — they see their territory only.

Users with `admin` role see all territories with no filter.

### 6.2 Visibility Enforcement

Territory scoping is enforced in the service layer via a `TerritoryScope` middleware/decorator pattern:

```
GET /api/v1/leads
  → resolve user's territory scope:
      admin: no filter
      manager: WHERE territory_id IN (their territories + children)
      sales_rep: WHERE assigned_rep_id = current_user.id
  → apply scope to query before returning results
```

This scope is pre-computed at login and cached in the JWT claims as `territory_ids: [uuid1, ...]` — agents/managers only see what their claim allows.

### 6.3 Territory Performance Metrics

Read model: `TerritoryPerformanceRM` (computed daily by aggregation job):

```
TerritoryPerformanceRM
├── territory_id         : UUID
├── tenant_id            : str
├── metric_date          : date
├── open_leads           : int
├── leads_added_today    : int
├── leads_converted      : int
├── conversion_rate      : float (converted / total_assigned in period)
├── avg_follow_up_response_time_hours : float
├── overdue_follow_ups   : int
├── open_invoices_amount_pkr : bigint
├── collected_amount_pkr : bigint
├── collection_rate      : float
└── computed_at          : datetime
```

Used by `A-07 support-dashboard.html` and territory performance panel in `territories.html`.

---

## 7) API Endpoints

### Territory Management

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/territories` | JWT | Any authenticated | List territories (admin: all; manager: their territory + children; rep: own). |
| `POST` | `/api/v1/territories` | JWT | `admin` | Create territory with criteria rules. |
| `GET` | `/api/v1/territories/{id}` | JWT | `manager`, `admin` | Territory detail with rules and performance summary. |
| `PATCH` | `/api/v1/territories/{id}` | JWT | `admin` | Update territory (name, reps, rules, priority). |
| `DELETE` | `/api/v1/territories/{id}` | JWT | `admin` | Deactivate territory (soft delete; re-assigns active subjects to default territory). |
| `POST` | `/api/v1/territories/{id}/rules` | JWT | `admin` | Add criteria rule to territory. |
| `DELETE` | `/api/v1/territories/{id}/rules/{rule_id}` | JWT | `admin` | Remove criteria rule. |

### Territory Assignments

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/territories/assignments` | JWT | `manager`, `admin` | List active assignments (filterable by territory, subject_type, rep). |
| `POST` | `/api/v1/territories/assignments/evaluate` | JWT | `manager`, `admin` | Dry-run: evaluate which territory a hypothetical subject would match. Returns ranked candidates. |
| `POST` | `/api/v1/territories/assignments/{id}/reassign` | JWT | `manager`, `admin` | Manually reassign subject to a different territory/rep. |

### Territory Performance

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/territories/{id}/performance` | JWT | `manager`, `admin` | Territory performance metrics (from `TerritoryPerformanceRM`). |

---

## 8) Events Emitted

| Event | Trigger |
|---|---|
| `territory.created` | Territory created. |
| `territory.updated` | Territory criteria, reps, or settings changed. |
| `territory.assigned` | Lead/account assigned to a territory (auto or manual). |
| `territory.conflict_resolved` | Multiple territories matched; winner selected. |
| `territory.manually_reassigned` | Manager manually reassigned a subject. |
| `territory.assignment_fallback` | No eligible rep found; assigned to default territory. |
| `territory.deactivated` | Territory deactivated; subjects re-routed. |

---

## 9) RBAC Role Gates

| Operation | `sales_rep` | `manager` | `admin` |
|---|---|---|---|
| View own territory assignments | ✓ | ✓ | ✓ |
| View territory performance | Own territory only | Own + child territories | All |
| Create / edit territory | — | — | ✓ |
| Add / remove rules | — | — | ✓ |
| Manual reassignment | — | Own territories | All |
| Dry-run evaluation | — | ✓ | ✓ |
| Set default territory | — | — | ✓ |
| Deactivate territory | — | — | ✓ |

---

## 10) Scanner Jobs

### 10.1 Auto-Assignment Job
- **Schedule:** Every 1 minute.
- **Action:**
  1. Query `Lead WHERE territory_assignment IS NULL AND created_at > now() - INTERVAL 5 minutes`.
  2. Run criteria evaluation pipeline for each unassigned lead.
  3. Create `TerritoryAssignment` records.
  4. Emit `territory.assigned` events.
- **SLA:** All leads must have an assignment within 1 minute of creation.

### 10.2 Territory Performance Aggregation Job
- **Schedule:** Daily at 01:00 PKT.
- **Action:** Aggregate metrics for all territories and upsert into `TerritoryPerformanceRM` for metric_date = yesterday.

### 10.3 Inactive Territory Cleanup Job
- **Schedule:** Weekly (Sunday 02:00 PKT).
- **Action:** Find territories with `is_active = false` where all active `TerritoryAssignment` records have been re-routed; archive them with a final status audit log entry.

---

## 11) Implementation Acceptance Checklist

- [ ] `Territory` entity created; partial unique index on `(tenant_id, is_default) WHERE is_default = true`.
- [ ] `TerritoryRule` entity created with all `rule_type` variants and JSON `value` schemas.
- [ ] `TerritoryAssignment` entity created; partial unique index on `(tenant_id, subject_type, subject_id) WHERE is_active = true`.
- [ ] Criteria evaluation pipeline handles: city, postal_code, region, account_industry, account_size, account_tier, rep_explicit, custom_field.
- [ ] Geo polygon rule type evaluates to NO MATCH (not error) when `lat_lng` is null.
- [ ] Conflict resolution: priority order → rule specificity → UUID tiebreaker.
- [ ] Manual override sets `superseded_by` and creates new active assignment.
- [ ] Manual override is sticky (not overridden by next auto-routing run).
- [ ] Dashboard scoping: admin = all, manager = territory subtree, rep = own assignments.
- [ ] Territory JWT claims (`territory_ids`) populated at login.
- [ ] Default territory assignment fires when no rule matches.
- [ ] Auto-assignment scanner job runs every 1 minute.
- [ ] All events in §8 emitted via activity log.
- [ ] API endpoints respect RBAC gates in §9.
- [ ] `tenant_id` isolation enforced on all queries.
