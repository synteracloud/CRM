<!-- OWNERSHIP
PRIMARY FOR: CommandRecord schema and state machine; sync batch API contract; low-bandwidth budget table §13; conflict resolution rules per entity type; partial batch failure rules.
DEFERS TO: concurrency-control.md (version_no concept for conflict detection); global-idempotency.md (idempotency contract — §8 correctly cross-refs).
DO NOT RE-DEFINE: OCC/version_no mechanics → concurrency-control.md.
-->

# Offline Sync Layer

## 1) Purpose

The Offline Sync Layer enables the system to function correctly when a user's device has no network connectivity, and to converge to consistent state when connectivity is restored.

This is Domain Capability #10 from the system specification. It directly supports the critical integration flow:

```
Offline Action → Sync → Consistent State
```

---

## 2) Design Principles

- **Local-first execution**: actions taken offline are queued locally and treated as pending commands
- **At-least-once delivery**: queued commands are retried until acknowledged by the server
- **Idempotent replay**: all commands carry an `idempotency_key`; server-side deduplication prevents double execution
- **Conflict resolution is deterministic**: conflicts are resolved by explicit rules, not silent last-write-wins

---

## 3) Architecture

```
Device (Offline)
  ├── Local Action Queue (persistent, ordered)
  │     └── CommandRecord { idempotency_key, command_type, payload, created_at, retry_count, status }
  └── Local State Cache (last-known server state snapshot)

       ↕  (network restored)

Sync Service
  ├── Command Ingestor     — deduplicates and validates incoming queued commands
  ├── Conflict Detector    — compares command timestamp against server entity version
  ├── Conflict Resolver    — applies resolution strategy per entity type
  └── State Reconciler     — pushes authoritative state back to device
```

---

## 4) Local Action Queue

### Queue Entry Schema

```
CommandRecord {
  id:               uuid (local)
  idempotency_key:  string  -- (tenant_id + device_id + local_seq_no)
  command_type:     enum    -- see Command Types below
  entity_type:      string
  entity_id:        uuid
  payload:          json
  created_at:       datetime (device clock, UTC)
  status:           enum    -- PENDING | SYNCING | SYNCED | FAILED | CONFLICT
  retry_count:      int
  last_error:       string?
}
```

### Queue Behavior Rules

- Queue is written synchronously on every user action (no action is lost even if the app crashes immediately after)
- Queue is persisted to device storage, not in-memory only
- Commands are replayed in `created_at` order within the same `entity_id`
- A CONFLICT or FAILED entry does not block subsequent commands for other entities

---

## 5) Supported Command Types

| Command | Entity | Offline-Safe | Conflict Risk |
|---|---|---|---|
| `CREATE_LEAD` | Lead | Yes | Low (new entity) |
| `UPDATE_LEAD_STAGE` | Lead | Yes | Medium (concurrent stage changes) |
| `LOG_ACTIVITY` | Activity | Yes | None (append-only) |
| `CREATE_NOTE` | Note | Yes | None (append-only) |
| `COMPLETE_TASK` | Task | Yes | Low |
| `SCHEDULE_FOLLOWUP` | FollowUp | Yes | Low |
| `UPDATE_CONTACT` | Contact | Yes | Medium |
| `SEND_WHATSAPP_MESSAGE` | Message | Yes | Low |
| `RECORD_PAYMENT` | Payment | Yes | High — requires server validation |
| `UPDATE_DEAL_AMOUNT` | Opportunity | Yes | High — requires server validation |

### Duplicate Entity Conflict (CREATE_LEAD)

When a `CREATE_LEAD` command is replayed after the device was offline and the same contact (matched by `phone_e164 + tenant_id`) was created online during the offline period:

1. Sync Service detects phone collision during `CREATE_LEAD` processing.
2. Command is marked `CONFLICT` — the lead is NOT created.
3. A `DuplicateCandidate` is surfaced in the Sync Review panel showing: offline lead payload vs. existing server lead.
4. User chooses: **Use server lead** (discard offline data) or **Merge** (opens merge workflow, applies offline field updates to server lead).
5. If user takes no action within 7 days, server lead wins and offline data is discarded.

---

## 6) Sync Process

### 6.1 Trigger Conditions

Sync initiates when:
- Network connectivity is detected (event-driven, not polling)
- User manually triggers sync
- App returns to foreground after background period

### 6.2 Sync Sequence

```
1. Device sends batch of PENDING commands (ordered by created_at)
2. Sync Service checks each command for idempotency (already processed? return result)
3. Sync Service validates command against current server state
4. If no conflict: apply command, return success + updated entity version
5. If conflict: invoke conflict resolver, return resolution result + merged state
6. Device updates local queue status (SYNCED / CONFLICT)
7. Device receives authoritative state snapshot for affected entities
8. Local cache updated with server-authoritative state
```

### 6.3 Batch Limits

- Maximum 100 commands per sync batch
- Batches are processed in strict FIFO order per entity
- Cross-entity ordering within a batch is best-effort (no cross-entity guarantees)

---

## 7) Conflict Resolution

### 7.1 Conflict Definition

A conflict occurs when:
- An offline command targets an entity whose `version_no` on the server is higher than the version the device had when the command was created
- (i.e., someone else modified the entity while the device was offline)

### 7.2 Resolution Strategies by Entity

| Entity | Strategy | Rationale |
|---|---|---|
| Lead stage | **Server wins** — server stage is authoritative; offline change is discarded and surfaced as notification | Stage transitions carry business significance; silent merge is unsafe |
| Activity / Note | **Append both** — offline activity is appended to timeline regardless | Activities are immutable append-only; no conflict possible |
| Contact fields | **Field-level merge** — non-overlapping field updates are merged; overlapping fields: server wins | Minimize data loss on concurrent edits |
| Follow-up schedule | **Latest timestamp wins** — most recent scheduled_at is used | User intent is most-recent-update |
| Payment record | **Reject and require re-entry** — payment commands are rejected if entity state changed | Financial accuracy requires explicit user confirmation |
| Task completion | **Accept if task still open** — reject if task already closed | No double-completion |

### 7.3 Conflict Notification

- All conflicts are surfaced to the user in a dedicated Sync Review panel
- Each conflict shows: what changed offline, what the current server state is, and the resolution applied
- User can manually override server-wins decisions for Contact fields

---

## 8) Idempotency Contract

All commands sent to the Sync Service carry an `idempotency_key`.

The server uses the same global idempotency model as all other operations:
- Deduplication window: 24 hours
- Scope: `(tenant_id, idempotency_key)`
- On duplicate receipt: return original result without re-executing

This guarantees at-least-once delivery from device does not cause double execution on server.

See [`global-idempotency.md`](global-idempotency.md).

---

## 9) State Cache Management

### 9.1 What Is Cached

- Last-known state of entities the user has viewed or acted on
- Cached at entity level with `version_no` and `cached_at` timestamp
- Not a full local replica — only accessed entities are cached

### 9.2 Cache Staleness

- Cache entries older than 7 days are considered stale
- Stale cache reads are flagged in the UI with a "last synced X ago" indicator
- Stale cache does not block offline action creation — user is warned, not blocked

### 9.3 Cache Invalidation

- On successful sync, server sends back authoritative versions for all affected entities
- Cache entries are atomically replaced on each sync completion
- On forced refresh (user pull-to-refresh), entire viewed entity set is re-fetched

---

## 10) Failure Handling

| Failure Type | Behavior |
|---|---|
| Network timeout during sync | Command stays PENDING; retry with exponential backoff (30s, 2m, 10m) |
| Server validation error (e.g. entity not found) | Command marked FAILED; surfaced to user with error |
| Conflict resolution failure | Command marked CONFLICT; surfaced to Sync Review panel |
| Sync batch partial failure | Successful commands are committed; failed commands retried individually |
| Device storage full | Oldest SYNCED commands purged; PENDING commands preserved |

### Partial Batch Failure — Client Consistency

When a sync batch returns mixed results (some commands SYNCED, some FAILED or CONFLICT):

1. Device receives per-command status in the sync response.
2. Successfully synced commands are marked SYNCED in the local queue.
3. Failed commands remain PENDING with their error noted; they are retried in the next sync.
4. Conflict commands are marked CONFLICT and surfaced in the Sync Review panel.
5. **The client MUST NOT show a "Sync complete" indicator until all commands in the batch are in a terminal state (SYNCED, CONFLICT-resolved, or FAILED-acknowledged by user).**
6. The "Last synced" timestamp reflects the most recent fully-acknowledged batch, not partial batch completion.

---

## 11) Security Constraints

- Offline queue is stored encrypted on device using device keystore
- Commands are signed with device identity token; unsigned commands rejected by Sync Service
- Sync endpoint requires valid session token; expired sessions block sync until re-authenticated
- No PII is stored in device cache beyond what the user has explicitly viewed

---

## 12) Observability

- `sync.batch.submitted` — emitted per sync batch
- `sync.command.applied` — emitted per successfully applied command
- `sync.command.conflict` — emitted per conflict with resolution type
- `sync.command.failed` — emitted per failed command with error code
- `sync.latency_ms` — time from connectivity restored to sync complete

Sync health visible in observability dashboards. Alert threshold: >5% conflict rate or >10% failure rate per tenant per day.

See [`observability-audit.md`](observability-audit.md).

---

## 13) Low-Bandwidth Operation

Pakistan's mobile network reality includes 3G/EDGE connectivity, intermittent signal, and shared bandwidth environments. The system must degrade gracefully rather than fail silently.

### 13.1 API Response Size Budget

| Endpoint type | Max payload (uncompressed) | Notes |
|---|---|---|
| List endpoints (GET /leads, /followups) | 50 KB | Paginate at 25 records max; no embedded relations |
| Single entity (GET /leads/:id) | 20 KB | Core fields only by default; expand=timeline optional |
| Sync batch response | 100 KB | 100 commands max; server snapshot optional |
| WhatsApp message send | 5 KB | Text only in default path; media via separate upload URL |
| Dashboard summary | 30 KB | Aggregated counts only; no row-level data |

### 13.2 Transport Layer Requirements

- All API responses MUST support gzip compression (Content-Encoding: gzip). Server and client must negotiate.
- Images (payment proof, profile photos) are never inline in API responses — always served as signed CDN URLs.
- WebSocket or long-polling is not used for core flows; polling at 30s intervals maximum.

### 13.3 Offline-First Fallback

When a sync attempt times out (> 10 seconds with no response):
1. Device keeps commands in `PENDING` state.
2. UI shows "Working offline — changes will sync when connection is restored."
3. Next sync attempt after exponential backoff: 30s, 2m, 10m.
4. If device has been offline > 7 days, state cache is marked stale and a full snapshot is requested on next sync.

### 13.4 Progressive Loading

- Lead list renders immediately from local cache (stale-while-revalidate pattern).
- Fresh data replaces cached data in-place without screen reload.
- Critical data (lead count, overdue follow-ups) is always fetched fresh on app foreground.
- Non-critical data (analytics, historical timeline) is deferred and loads on scroll/interaction.

### 13.5 Offline Device Schema Compatibility

Offline devices may replay commands after a major API schema change. Compatibility rules:

- **Additive changes** (new optional fields): safe — device command is accepted, new fields default.
- **Breaking changes** (required new fields, renamed fields, removed fields): offline commands using the old schema are rejected with `422 validation_error` + `error.code = schema_version_mismatch`.
- On schema mismatch: command is marked FAILED with reason `schema_version_mismatch`. Device is instructed to perform a full state cache refresh before retrying. Full refresh forces device to re-fetch current schema and re-present the command with current field names.
- Schema version is embedded in sync batch request headers (`X-Client-Schema-Version`). Server validates and rejects batch if version is more than 2 major versions behind.
