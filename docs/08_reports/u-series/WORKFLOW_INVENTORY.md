# WORKFLOW_INVENTORY.md
> Generated: 2026-06-20 — U1 Authority Reconstruction — evidence from gateway/routes/v1-workflows.routes.js (seeded definitions), src/automation_journeys/, src/workflow_engine/, src/lead_management/workflow_mapping.py, src/campaigns/workflow_mapping.py, src/subscription_billing/workflow_mapping.py

---

## Workflow Engine Architecture

**Type:** Event-driven workflow engine
**Trigger mechanism:** Events emitted to internal event bus (src/event_bus/) on entity state changes
**Execution:** WorkflowDefinition → WorkflowExecution → WorkflowStepRecords
**Retry policy:** configurable max_retries (default 3), retry_backoff_seconds (default 60)
**Step types:** condition (boolean branch), action (data operation), notification (WhatsApp/email/system)
**Custom workflows:** Tenants can create custom workflow definitions via POST /workflows (WORKFLOWS_MANAGE scope)

---

## System Workflows (seeded — is_system: true, not editable)

### WF-001 — Lead Follow-up Enforcement
**workflow_key:** `lead_followup_enforcement`
**Trigger:** `lead.idle.v1`
**Description:** Triggered when a lead goes idle (no activity within threshold). Ensures no lead remains without an active follow-up task.
**Steps:**
1. `condition` — Check idle threshold: `lead.idle_days > threshold`
2. `action` — Create follow-up task (creates canonical FollowupTask for lead)
3. `notification` — Notify owner via WhatsApp alert
**Entities involved:** Lead, FollowupTask, User (owner)
**max_retries:** 3, **timeout_seconds:** 300
**Status:** Implemented (seeded as active, in-memory + workflow_engine src module)
**Evidence:** gateway/routes/v1-workflows.routes.js:45 (wf-001 seed), src/lead_management/workflow_mapping.py

---

### WF-002 — Collections Auto-Reminder
**workflow_key:** `collections_reminder`
**Trigger:** `invoice.overdue.v1`
**Description:** Sends WhatsApp reminders to contacts when invoices are overdue. Retryable on WhatsApp send failure.
**Steps:**
1. `action` — Load invoice details
2. `notification` — Send WhatsApp reminder to contact
**Entities involved:** Invoice, Contact, Payment
**max_retries:** 3, **timeout_seconds:** 120
**Status:** Implemented (seeded as active); known failure mode: WhatsApp rate-limit (exec-002 shows failed execution, exec-005 shows retry)
**Evidence:** gateway/routes/v1-workflows.routes.js:46 (wf-002 seed), src/subscription_billing/workflow_mapping.py

---

### WF-003 — SLA Breach Notification
**workflow_key:** `sla_breach_notify`
**Trigger:** `case.sla.breached.v1`, `case.sla.first_response_breached.v1`
**Description:** Escalates case and notifies supervisor on SLA breach.
**Steps:**
1. `action` — Load case details
2. `action` — Escalate case (update case.status → ESCALATED, increment escalation_level)
3. `notification` — Notify supervisor
4. `action` — Log escalation event to audit log
**Entities involved:** Case, CaseEscalation, User (supervisor), AuditLog
**max_retries:** 3, **timeout_seconds:** 300
**Status:** Implemented (seeded as active, execution evidence: exec-003/exec-008)
**Evidence:** gateway/routes/v1-workflows.routes.js:47 (wf-003 seed)

---

### WF-004 — Lead Territory Assignment
**workflow_key:** `lead_assignment`
**Trigger:** `lead.created.v1`
**Description:** Auto-assigns new leads to the correct owner based on territory rules (geography/industry/account_size criteria).
**Steps:**
1. `action` — Evaluate territory rules for lead attributes
2. `action` — Assign owner (sets lead.owner_id, creates LeadAssignment record)
**Entities involved:** Lead, Territory, TerritoryRule, LeadAssignment, User
**max_retries:** 3, **retry_backoff_seconds:** 30, **timeout_seconds:** 60
**Status:** Implemented (seeded as active, execution evidence: exec-004)
**Evidence:** gateway/routes/v1-workflows.routes.js:48 (wf-004 seed), src/territory_management/ module

---

### WF-005 — Opportunity Stage Change Notification
**workflow_key:** `opportunity_stage_notify`
**Trigger:** `opportunity.stage.changed.v1`
**Description:** Notifies the sales team when an opportunity advances to a new pipeline stage. Also refreshes forecast.
**Steps:**
1. `condition` — Check if stage is in notification-enabled stages config
2. `notification` — Send stage alert to team
3. `action` — Refresh revenue forecast (calls predictive_forecasting module)
**Entities involved:** Opportunity, User (team), Forecast
**max_retries:** 3, **timeout_seconds:** 120
**Status:** Implemented (seeded as active, execution evidence: exec-006)
**Evidence:** gateway/routes/v1-workflows.routes.js:49 (wf-005 seed)

---

## System Events Catalog (trigger events found in code)

| Event | Emitted By | Consumed By |
|---|---|---|
| `lead.created.v1` | v1-leads.routes.js (POST /leads) | WF-004 (territory assignment) |
| `lead.idle.v1` | followup service scheduler | WF-001 (followup enforcement) |
| `lead.stage.changed.v1` | repo.transitionStage() in leads | (logging/audit) |
| `invoice.overdue.v1` | billing service scheduler | WF-002 (collections reminder) |
| `case.sla.breached.v1` | SLA monitor in support_console service | WF-003 (SLA breach notify) |
| `case.sla.first_response_breached.v1` | SLA monitor | WF-003 |
| `opportunity.stage.changed.v1` | v1-opportunities.routes.js PATCH | WF-005 (stage notify) |
| `opportunity.closed.v1` | v1-opportunities.routes.js PATCH (terminal stage) | (audit, forecasting) |

**Source:** `src/event_bus/catalog_events.py`, `src/event_bus/catalog_schema.py`, gateway route files

---

## Custom Workflow Support

Custom workflows can be created, published, and managed by tenants with WORKFLOWS_MANAGE scope.

**Create:** POST /workflows — requires `name`, `trigger_events[]`, optional `steps_dsl[]`, `max_retries`, `timeout_seconds`
**Publish:** POST /workflows/:id/publish — transitions draft → active (requires ≥1 step)
**Pause:** PATCH /workflows/:id with `status: "paused"`
**Archive:** PATCH /workflows/:id with `status: "archived"` (terminal — cannot undo)
**Simulate:** POST /workflows/:id/simulate — dry-run with test payload, no side effects
**Retry failed execution:** POST /workflows/runs/:id/retry (max retries enforced)
**Cancel running execution:** POST /workflows/runs/:id/cancel

**Constraint on system workflows:** is_system=true blocks PATCH (403 FORBIDDEN — system workflows cannot be edited)

---

## Automation Journey Modules (Python backend)

`src/automation_journeys/` — confirmed files: api.py, entities.py, services.py, events.py, workflow_mapping.py

This module handles multi-step marketing/sales automation journeys beyond the event-based workflow engine. Journeys are sequences of timed/conditional steps mapped to campaigns and lead lifecycle stages.

**Evidence:** `backend/src/automation_journeys/workflow_mapping.py` — maps journey triggers to workflow events

---

## Workflow Execution Status Lifecycle

```
DRAFT (created)
  ↓ publish (≥1 step, manage scope)
ACTIVE (running and accepting new executions)
  ↓ pause
PAUSED (no new executions, in-flight complete)
  ↓ activate
ACTIVE
  ↓ archive (any state)
ARCHIVED (terminal — no new executions)
```

**Execution lifecycle:**
```
RUNNING → SUCCEEDED (all steps complete)
RUNNING → FAILED (step error, no retries left)
FAILED → RETRYING (retry triggered, retry_count < max_retries)
RETRYING → SUCCEEDED | FAILED
RUNNING | FAILED | RETRYING → CANCELLED (manual cancel)
```

---

*End WORKFLOW_INVENTORY.md*
