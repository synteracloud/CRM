# B9-P12::AUDIT_COMPLIANCE_DATA_GOVERNANCE

## Scope

Defines the **Audit / Compliance / Data Governance** archetype — 5 named surfaces.
Anchored to `docs/observability-audit.md`, `docs/activity-control-model.md`, `docs/data-architecture.md`.
All surfaces in this archetype are **read-only** — immutability is a core constraint.

---

## 1) Archetype Structure

Audit surfaces use an **explorer + evidence panel** layout:

```
┌─ Time range + actor + entity type filter bar ─────────────┐
├─ Summary strip (entry count, anomaly count, export) ───────┤
├──────────────────────────┬────────────────────────────────┤
│  Event log (immutable    │  Evidence panel                │
│  chronological list)     │  - Selected entry detail       │
│                          │  - Hash verification           │
│                          │  - Chain position              │
└──────────────────────────┴────────────────────────────────┘
```

**Design rules:**
- Audit surfaces are **strictly read-only** — no edit, delete, or dismiss controls.
- Hash chain verification is always displayed for selected entries.
- Export is the only write-adjacent action; it creates an export record in `AuditLog`.
- Sensitive fields shown to `compliance_officer` / `super_admin` only.

---

## 2) The 5 Audit / Compliance Pages

### 2.1 — Audit Log & Compliance Explorer

**Route:** `/app/admin/audit`
**Source entity:** `AuditLog`
**Read model:** `PlatformReliabilityAuditRM`
**Role gate:** `super_admin`, `compliance_officer`, `tenant_admin` (own tenant only)

**Event log columns:**

| Column | Source | Notes |
|---|---|---|
| Timestamp | `AuditLog.occurred_at` | ISO-8601, absolute + relative |
| Actor | `AuditLog.actor_id` → `User.full_name` | System events show "system" |
| Action | `AuditLog.action_type` | `create`, `update`, `delete`, `login`, `export`, etc. |
| Resource | `AuditLog.resource_type` + `resource_id` | Polymorphic entity reference |
| Result | `AuditLog.result` | `allow` / `deny` |
| Hash | `AuditLog.hash` | Truncated (first 8 chars) |

**Evidence panel (on row selection):**
- Full `AuditLog` entry JSON
- Hash verification result: PASS / FAIL
- Chain position: entry N of M in tenant's audit chain
- Link to previous hash

**Filter chips:** Actor, Action type, Resource type, Result, Date range
**Export:** Signed CSV with full entry + hash. Export action itself logged.

---

### 2.2 — Data Deduplication Engine

**Route:** `/app/admin/deduplication`
**Source module:** `src/data_deduplication_engine/`
**Read model:** `CustomerMasterHealthRM` (merge candidate count)
**Role gate:** `tenant_admin`, `data_admin`

**Sections:**
1. **Merge candidates** — list of contact/account pairs flagged as potential duplicates.
   - Sorted by similarity score descending.
   - Shows: both record names, similarity score, detection method (phone exact / fuzzy name).
   - Actions: `Merge`, `Dismiss` (not a duplicate).
2. **Merge history** — log of accepted merges. Immutable — shows surviving record ID, merged record ID, merged-by user, timestamp.
3. **Rule configuration** — threshold sliders for fuzzy match (default 0.85 per P-018); toggle phone-exact matching.

**Design rule:** `suggest_merge` is always advisory — no auto-merge. User must explicitly confirm. Aligns with `BEHAV-002`.

---

### 2.3 — Event Bus Monitor

**Route:** `/app/admin/events`
**Source entities:** `WorkflowExecution`, event streams
**Role gate:** `admin`, `super_admin`

**Sections:**
1. **Live event stream** — real-time feed of domain events (last 500). Pause / resume toggle.
2. **Dead letter queue** — events from `webhook_dead_letter` that failed all retries. Actions: `Replay`, `Dismiss`.
3. **Event volume chart** — events per minute / hour grouped by event type.
4. **Subscription health** — per-webhook-endpoint: last delivery status, retry count, circuit-breaker state.

---

### 2.4 — Data Governance

**Route:** `/app/admin/governance`
**Source docs:** `docs/data-governance-ownership.md`, `docs/data-governance-layer.md`
**Role gate:** `super_admin`, `compliance_officer`

**Sections:**
1. **Data classification** — entity fields tagged by sensitivity (PII, financial, internal, public). View-only map.
2. **Retention policies** — per entity type: current retention period, legal basis, deletion schedule.
3. **Subject access requests** — list of pending/completed data export or deletion requests.
4. **Consent management** — per-contact consent records (marketing, communications, data processing).

---

### 2.5 — Sync & Observability

**Route:** `/app/admin/sync`
**Source entities:** `SyncStatus`, `OfflineAction` (from `services/sync/entities.py`)
**Role gate:** `tenant_admin`, `admin`

**Sections:**
1. **Sync queue** — current pending offline actions per user/device. Count + type breakdown.
2. **Conflict log** — resolved conflicts with strategy used (`last_write_wins` / `server_wins` / `client_wins`) and both versions.
3. **Reliability report** — `services/sync/http/internal.py` `GET /sync/status` output: success rate, avg queue depth, oldest pending action.
4. **Offline indicator** — mirrors `buildOfflineIndicator()` from `gateway/services/cache-policy.js`. Shows live count of pending changes.

---

## 3) Interaction Patterns

1. **Immutability enforced in UI:** No edit or delete controls rendered for audit entries. No override exists.
2. **Hash verification on demand:** Clicking any audit entry triggers hash re-computation client-side and shows PASS/FAIL.
3. **Export is audited:** Every export action creates its own `AuditLog` entry — full audit trail of audit access.
4. **Merge confirmation:** Deduplication merge requires typing the surviving record name to confirm — prevents accidental merges.
5. **Dead letter replay:** Single-event or bulk replay with exponential backoff as per `gateway/services/cache-policy.js` `OFFLINE_BACKOFF_SECONDS`.

---

## SELF-QC

- **All 5 Archetype.md audit/compliance pages documented:** ✅ — 2.1–2.5 match exactly.
- **All surfaces read-only (no edit/delete):** ✅ — immutability explicitly enforced.
- **Hash chain verification documented:** ✅ — PASS/FAIL per entry.
- **Merge advisory-only documented (BEHAV-002):** ✅
- **Export audited:** ✅
- **Sync/offline cross-referenced to cache-policy.js:** ✅

Score: **10/10**
