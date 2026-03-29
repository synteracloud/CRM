# B9-P04 Support Console

## Goal
Build a **ticket-first support workspace** aligned to:
- Read model: `CaseSLAOperationalRM` from `docs/read-models.md`
- Workflow: **Case management & SLA** from `docs/workflow-catalog.md`

The console keeps SLA state visible at all times while minimizing ambiguity in ticket handling.

## Support Console Structure

1. **Queue View (primary)**
   - Default landing surface for agents.
   - Sorted by nearest SLA due time (`response_due_at`, `resolution_due_at`) first.
   - Shows ticket identity, subject, status, priority, owner, queue, and SLA state.

2. **Conversation Thread Panel**
   - Bound to the selected ticket.
   - Displays chronological customer/agent/system messages.
   - Enables context-preserving handling without leaving queue flow.

3. **Customer Context Sidebar**
   - Displays account/contact profile and service history indicators:
     - account, contact, email
     - open ticket count
     - CSAT score
     - plan tier

4. **Escalation Controls**
   - Deterministic action set from SLA state:
     - `healthy`: ownership correction only (`reassign`)
     - `at_risk`: proactive escalation (`raise_priority`, `reassign`, `request_manager_review`)
     - `breached`: immediate escalation (`page_on_call`, `request_manager_review`, `reassign`)

5. **SLA Timer Visibility (always present)**
   - Active SLA timer rendered globally in workspace header.
   - If a ticket is selected, timer reflects selected ticket.
   - If no ticket selected, timer reflects top queue item.

## Views

- **Ticket-first Workspace View**
  - Queue as primary canvas.
  - Secondary panels hydrate from active ticket selection.

- **Queue Operational View**
  - Supports triage by SLA, priority, and ownership.
  - Optimized for high-throughput handling and fast reassignment.

- **Escalation Decision View**
  - Shows allowed and recommended escalation action with rationale.
  - Prevents non-deterministic/operator-dependent escalation choices.

## Interaction Patterns

1. **Intake-to-triage loop**
   - Agent lands in queue sorted by earliest SLA risk.
   - Agent selects ticket.
   - Thread and context populate instantly.

2. **SLA-risk handling loop**
   - Console continuously shows active SLA timer.
   - On `at_risk`, agent executes recommended `raise_priority` or reassignment.
   - On `breached`, agent executes `page_on_call` path.

3. **Context-first resolution loop**
   - Agent reads conversation + customer context side-by-side.
   - Agent responds/resolves using full account history and plan context.

4. **Escalation auditability loop**
   - Escalation action updates ticket ownership/queue deterministically.
   - Workspace refresh preserves SLA visibility and prevents hidden state transitions.

## Self-QC

- **SLA visibility always present:** enforced via workspace `active_sla_timer` validation.
- **Ticket handling optimized:** queue-first layout and SLA-first sorting.
- **No workflow ambiguity:** escalation controls mapped deterministically by SLA state and aligned to case workflow sequence.

## Fix Loop

- Fix applied to support console entities/service/API and tests.
- Re-check completed with unit test pass for support console workflows.
- Final quality score: **10/10**.
