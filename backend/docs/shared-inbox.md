# Shared WhatsApp Inbox Spec

## Purpose

This document defines the **multi-agent shared inbox model** — how multiple team members handle customer queries arriving from a single official WhatsApp business number. The current `whatsapp-execution-model.md` assigns conversations per tenant (keyed `tenant_id + phone`); this spec extends that to per-agent assignment within the tenant, conversation handoff, and supervisor visibility.

**Build gates:** Required before L-01 `inbox.html` and L-02 `inbox-thread.html` are implemented.

---

## 1) Core Model

### 1.1 One Number, Many Agents

A Pakistan SMB typically has one official WhatsApp business number. Multiple sales reps or support agents must be able to handle conversations from that number without:
- Two agents replying to the same customer simultaneously.
- Agents seeing conversations assigned to others.
- Supervisors losing visibility of the full queue.

### 1.2 Non-negotiable Invariants
1. Every conversation has exactly one active assigned agent at any time.
2. An agent can only send messages on conversations assigned to them (except supervisors who can interject on any).
3. Reassignment (handoff) is atomic — the old agent loses write access the moment the new agent is assigned.
4. Unassigned conversations are visible to all agents in the pool and claimable by any of them.
5. Presence/availability status is per-agent and affects assignment eligibility.

---

## 2) Entity Extensions

### 2.1 Conversation (extended from whatsapp-execution-model.md)

The existing `Conversation` entity gains the following fields:

```
Conversation (additions only)
├── assigned_agent_id  : UUID (FK → User, nullable — null = unassigned, in pool)
├── assigned_at        : datetime (nullable)
├── queue_id           : UUID (FK → InboxQueue, nullable — which queue this conversation belongs to)
├── assignment_reason  : AssignmentReason enum (auto_routed | claimed | supervisor_assigned | handoff)
├── last_handoff_at    : datetime (nullable)
├── handoff_count      : int (default 0)
```

### 2.2 InboxQueue

A tenant may operate multiple inbox queues (e.g., "Sales", "Support", "Billing") even though messages come from one phone number. Routing rules determine which queue a new conversation enters.

```
InboxQueue
├── queue_id           : UUID (PK)
├── tenant_id          : str (required)
├── name               : str (e.g. "Sales", "Support")
├── routing_strategy   : InboxRoutingStrategy enum (round_robin | least_loaded | claim_first | skill_based)
├── skill_tags         : str[] (for skill_based routing)
├── team_id            : UUID (FK → Team, nullable — restrict queue to a team)
├── auto_assign        : bool (if true, system auto-assigns; if false, agents must claim)
├── is_active          : bool
├── created_at         : datetime
└── updated_at         : datetime
```

**Default:** One `InboxQueue` named "General" is created automatically on tenant bootstrap.

### 2.3 AgentPresence

```
AgentPresence
├── agent_id           : UUID (PK, FK → User)
├── tenant_id          : str (required)
├── status             : PresenceStatus enum (online | away | busy | offline)
├── open_conversation_count : int (managed by service, not directly settable by agent)
├── max_concurrent     : int (agent-configurable, default 10 — max conversations handled at once)
├── last_seen_at       : datetime
└── updated_at         : datetime
```

**Routing eligibility:** An agent is eligible for assignment when `status = online` AND `open_conversation_count < max_concurrent`.

### 2.4 ConversationHandoff

```
ConversationHandoff
├── handoff_id         : UUID (PK)
├── conversation_id    : UUID (FK → Conversation)
├── tenant_id          : str
├── from_agent_id      : UUID (FK → User, nullable — null if previously unassigned)
├── to_agent_id        : UUID (FK → User)
├── handoff_reason     : HandoffReason enum (agent_unavailable | capacity_exceeded | skill_match | manual | escalation)
├── note               : str (optional context from handing-off agent)
├── initiated_by       : UUID (FK → User — who triggered the handoff)
└── created_at         : datetime
```

---

## 3) Assignment Model

### 3.1 Auto-Assignment Pipeline

When a new inbound message arrives with no existing conversation:

```
1. Create Conversation (from whatsapp-execution-model.md pipeline)
2. Determine target InboxQueue via routing rules (see §3.2)
3. If queue.auto_assign = true:
   a. Apply queue.routing_strategy
   b. Select eligible agent (status=online, count < max_concurrent)
   c. Set Conversation.assigned_agent_id + assigned_at + assignment_reason=auto_routed
   d. Emit conversation.assigned event
4. If queue.auto_assign = false OR no eligible agent:
   a. Set Conversation.assigned_agent_id = null (enters unassigned pool)
   b. Emit conversation.queued event
```

When a follow-up message arrives on an existing conversation:
- If `assigned_agent_id` is set and agent is online → deliver to assigned agent.
- If `assigned_agent_id` is set but agent is offline → reassign via handoff pipeline (see §3.4).
- If `assigned_agent_id` is null → deliver to unassigned pool; notify all eligible agents in queue.

### 3.2 Queue Routing Rules

A new conversation is routed to a queue based on intent classification:

```
intent: lead_inquiry → "Sales" queue (or first queue with team.skill_tags ⊇ ["sales"])
intent: payment_query → "Billing" queue (or first queue with team.skill_tags ⊇ ["billing"])
intent: support_request → "Support" queue (or first queue with team.skill_tags ⊇ ["support"])
intent: follow_up_response → queue of assigned agent (if conversation exists); else "Sales"
fallback → "General" queue
```

If no matching queue is found for the intent: route to the tenant's first active queue.

### 3.3 Claim (Manual Pool)

When `auto_assign = false` or no eligible agent is available, the conversation enters the unassigned pool. Any eligible agent in the queue can claim it:

```
POST /api/v1/inbox/conversations/{id}/claim
  → Guard: conversation.assigned_agent_id must be null
  → Guard: requesting agent must be in queue.team_id
  → Guard: agent.status = online AND open_conversation_count < max_concurrent
  → Set conversation.assigned_agent_id = requesting_agent_id
  → assignment_reason = claimed
  → Emit conversation.assigned event
```

**Race condition:** Two agents may attempt to claim simultaneously. Enforced via `UPDATE ... WHERE assigned_agent_id IS NULL` — only one succeeds; the other receives a `409 Conflict` response.

### 3.4 Handoff (Re-assign)

An agent can transfer an active conversation to another agent or back to the pool:

```
POST /api/v1/inbox/conversations/{id}/handoff
  Request: { to_agent_id: UUID | null, reason: HandoffReason, note?: string }

  If to_agent_id is set:
    → Create ConversationHandoff record
    → Update Conversation.assigned_agent_id = to_agent_id
    → Update handoff_count++, last_handoff_at
    → Notify receiving agent
    → assignment_reason = handoff

  If to_agent_id is null:
    → Returns conversation to unassigned pool
    → Notify all eligible agents in queue
    → assignment_reason = handoff
```

**Authorization:** An agent can only hand off conversations assigned to them. Supervisors (`manager`, `admin`) can handoff any conversation.

---

## 4) Presence and Availability

### 4.1 Presence Updates

Agents set their availability status via:

```
PATCH /api/v1/inbox/presence
  Request: { status: "online" | "away" | "busy" | "offline" }
```

The system also auto-sets presence:
- `offline` after 30 minutes of inactivity (no message reads or sends).
- `busy` when `open_conversation_count >= max_concurrent`.
- `online` when the agent reconnects (WebSocket reconnect or activity detected).

### 4.2 Presence in Assignment Eligibility

The routing pipeline only considers agents with `status = online`. `away` agents are excluded from auto-assignment but can still manually claim conversations. `busy` and `offline` agents are excluded from both auto-assignment and manual claim.

### 4.3 Agent Goes Offline Mid-Conversation

When `status → offline` for an agent with open conversations:
- Conversations with unread messages from the customer are automatically handed off to the queue (returned to pool).
- Conversations with no pending customer message remain assigned but are flagged `agent_offline`.
- After 5 minutes: all remaining conversations are returned to the pool.

---

## 5) Inbox Views

### 5.1 Agent View

An agent sees:
- **My Conversations:** `WHERE assigned_agent_id = current_user.id AND status != CLOSED`
- **Unassigned Pool:** `WHERE assigned_agent_id IS NULL AND queue_id IN (agent's queues) AND status = OPEN`
- Counts for each category displayed in left sidebar.

### 5.2 Supervisor View

A manager or admin sees:
- **All Conversations:** `WHERE tenant_id = current_tenant AND status != CLOSED`
- **By Agent:** filterable by `assigned_agent_id`.
- **Queue Summary:** per-queue open/unassigned/assigned counts.
- **Team Presence Board:** all agents with their current status and open_conversation_count.

### 5.3 Real-time Updates

The inbox UI subscribes to real-time events via Server-Sent Events (SSE) or WebSocket (Phase 5 choice). Key events that trigger UI refresh:

| Event | Target view update |
|---|---|
| `conversation.created` | Appears in unassigned pool (if unassigned) or assigned agent's inbox |
| `conversation.assigned` | Moves from pool to assigned agent's "My Conversations" |
| `conversation.message_received` | Unread badge increments; conversation bubbles to top |
| `conversation.handoff_completed` | Old agent's inbox removes conversation; new agent's inbox gains it |
| `presence.updated` | Team presence board refreshes |

---

## 6) Concurrent Assignment Conflict Rules

| Scenario | Resolution |
|---|---|
| Two agents claim the same unassigned conversation | First `UPDATE WHERE assigned_agent_id IS NULL` wins; second gets `409`. |
| Supervisor assigns while agent is claiming | Supervisor's assignment wins (supervisor assignment bypasses the null check). |
| Agent tries to send on conversation assigned to someone else | `403 Forbidden` — service checks `assigned_agent_id == current_user.id`. |
| Agent's presence flips to `offline` mid-handoff | Handoff completes to the target agent regardless of sender's presence. |

---

## 7) API Endpoints

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/inbox/conversations` | JWT | Any | List conversations (role-scoped — see §5). |
| `GET` | `/api/v1/inbox/conversations/{id}` | JWT | Any | Conversation detail with message thread. |
| `POST` | `/api/v1/inbox/conversations/{id}/claim` | JWT | `agent`, `manager`, `admin` | Claim unassigned conversation. |
| `POST` | `/api/v1/inbox/conversations/{id}/handoff` | JWT | `agent`, `manager`, `admin` | Transfer conversation to another agent or back to pool. |
| `POST` | `/api/v1/inbox/conversations/{id}/messages` | JWT | `agent`, `manager`, `admin` | Send message on assigned conversation. |
| `PATCH` | `/api/v1/inbox/presence` | JWT | Any authenticated | Update own presence status. |
| `GET` | `/api/v1/inbox/presence` | JWT | `manager`, `admin` | Get all agents' presence status (supervisor view). |
| `GET` | `/api/v1/inbox/queues` | JWT | `manager`, `admin` | List inbox queues. |
| `POST` | `/api/v1/inbox/queues` | JWT | `admin` | Create inbox queue. |
| `PATCH` | `/api/v1/inbox/queues/{id}` | JWT | `admin` | Update queue settings. |
| `GET` | `/api/v1/inbox/queues/{id}/stats` | JWT | `manager`, `admin` | Queue statistics (open/assigned/unassigned counts, avg response time). |

---

## 8) Events Emitted

| Event | Trigger |
|---|---|
| `conversation.queued` | New conversation entered pool (unassigned). |
| `conversation.assigned` | Conversation assigned to agent (auto or claim). |
| `conversation.handoff_initiated` | Handoff requested. |
| `conversation.handoff_completed` | New agent assignment confirmed. |
| `conversation.message_sent` | Agent sent outbound message. |
| `presence.updated` | Agent presence status changed. |
| `inbox.agent_offline_handoff` | System returned conversations to pool due to agent going offline. |

---

## 9) Implementation Acceptance Checklist

- [ ] `Conversation` entity extended with `assigned_agent_id`, `queue_id`, `assignment_reason`, `handoff_count`.
- [ ] `InboxQueue` entity created with routing strategy and team scope.
- [ ] `AgentPresence` entity created; auto-offline trigger after 30-min inactivity.
- [ ] `ConversationHandoff` entity created (immutable, append-only audit).
- [ ] Auto-assignment pipeline fires on new inbound message.
- [ ] Claim endpoint enforces `WHERE assigned_agent_id IS NULL` atomic update.
- [ ] Handoff transfers ownership and notifies receiving agent.
- [ ] Agent going offline triggers pool return for conversations with pending messages.
- [ ] Agent view (my + unassigned) scoped correctly.
- [ ] Supervisor view sees all conversations with team presence board.
- [ ] `403` returned when agent tries to message on another's conversation.
- [ ] All events in §8 emitted.
- [ ] `tenant_id` isolation enforced on all queries.
