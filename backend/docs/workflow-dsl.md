# Workflow DSL Specification

This document defines a machine-readable DSL for workflow definitions across the CRM platform.

## Design Goals

- Encode workflows with explicit `triggers`, `conditions`, `actions`, and `sequencing`.
- Stay aligned to the canonical workflow set in `docs/workflow-catalog.md`.
- Support deterministic parsing/validation and runtime execution.

## Alignment with Workflow Catalog

- `workflow_key` MUST match a workflow name from `docs/workflow-catalog.md` using snake_case.
- `triggers.events` MUST use canonical event names from the workflow catalog/event catalog.
- `sequencing.steps` MUST preserve the ordered step semantics defined in the workflow catalog.
- `actions.service` SHOULD map to service names in the workflow catalog.

## DSL Shape (Pseudo-Syntax)

```text
workflow <workflow_key> {
  version: "v1"
  metadata {
    name: <string>
    domain: <string>
    owner_service: <string>
    tags: [<string>, ...]
  }

  triggers {
    mode: any | all
    events: [<event_name>, ...]
    schedule: <cron_expr>?          // optional non-event trigger
    manual: true | false            // manual invocation allowed
  }

  conditions {
    match: all | any
    rules: [
      <field_path> <op> <value>,
      ...
    ]
  }

  sequencing {
    strategy: linear | branching
    on_error: fail_fast | continue | compensate
    steps: [
      step <step_id> {
        when: <condition_ref>?      // optional step-level guard
        action: <action_ref>
        timeout: <duration>?         // e.g., "30s", "5m"
        retries: <int>?              // default 0
        next: <step_id | end>        // required for branching
      },
      ...
    ]
  }

  actions {
    <action_ref>: {
      type: emit_event | call_service | notify | mutate_state | wait
      service: <service_name>
      operation: <string>
      input: { <json_object> }
      output: { <json_object_schema> }?
      emits: [<event_name>, ...]?
    }
  }
}
```

## Machine-Readable JSON Form

```json
{
  "workflow_key": "lead_intake_assignment_conversion",
  "version": "v1",
  "metadata": {
    "name": "Lead intake, assignment, conversion",
    "domain": "sales",
    "owner_service": "Workflow Automation Service",
    "tags": ["lead", "conversion", "routing"]
  },
  "triggers": {
    "mode": "any",
    "events": [
      "lead.created.v1",
      "lead.assignment.updated.v1",
      "lead.converted.v1"
    ],
    "manual": false
  },
  "conditions": {
    "match": "all",
    "rules": [
      {
        "field": "context.tenant_id",
        "op": "exists",
        "value": true
      },
      {
        "field": "context.entity.lead_status",
        "op": "in",
        "value": ["new", "qualified"]
      }
    ]
  },
  "sequencing": {
    "strategy": "linear",
    "on_error": "fail_fast",
    "steps": [
      {
        "id": "compute_assignment",
        "action": "assign_owner"
      },
      {
        "id": "notify_owner",
        "action": "send_assignment_notification"
      },
      {
        "id": "append_timeline",
        "action": "record_timeline"
      },
      {
        "id": "run_conversion_automation",
        "when": "context.event == 'lead.converted.v1'",
        "action": "execute_conversion_playbook"
      }
    ]
  },
  "actions": {
    "assign_owner": {
      "type": "call_service",
      "service": "Territory & Assignment Service",
      "operation": "compute_and_persist_lead_assignment",
      "input": {
        "lead_id": "${context.entity.id}",
        "tenant_id": "${context.tenant_id}"
      },
      "emits": ["lead.assignment.updated.v1"]
    },
    "send_assignment_notification": {
      "type": "notify",
      "service": "Notification Orchestrator",
      "operation": "notify_assigned_owner",
      "input": {
        "lead_id": "${context.entity.id}",
        "owner_id": "${state.assign_owner.owner_id}"
      }
    },
    "record_timeline": {
      "type": "call_service",
      "service": "Activity Timeline Service",
      "operation": "append_event",
      "input": {
        "entity_type": "lead",
        "entity_id": "${context.entity.id}",
        "event": "${context.event}"
      }
    },
    "execute_conversion_playbook": {
      "type": "call_service",
      "service": "Workflow Automation Service",
      "operation": "run_playbook",
      "input": {
        "playbook_key": "lead_conversion_default",
        "lead_id": "${context.entity.id}"
      }
    }
  }
}
```

## Validation Rules

1. `workflow_key` MUST be unique and snake_case.
2. `triggers.events[*]` MUST be valid canonical event names (`<bounded_context>.<entity>.<verb>.vN`).
3. Every `sequencing.steps[*].action` MUST exist in `actions`.
4. `sequencing.steps` MUST be non-empty and acyclic.
5. If `sequencing.strategy = branching`, each step MUST define `next`.
6. Any `actions[*].emits` event SHOULD be present in platform event catalog.
7. Workflows MUST remain semantically consistent with the ordered steps of their workflow catalog counterpart.

## Minimal Template

```json
{
  "workflow_key": "<catalog_workflow_key>",
  "version": "v1",
  "triggers": { "mode": "any", "events": ["<event>"] },
  "conditions": { "match": "all", "rules": [] },
  "sequencing": {
    "strategy": "linear",
    "on_error": "fail_fast",
    "steps": [{ "id": "step_1", "action": "action_1" }]
  },
  "actions": {
    "action_1": {
      "type": "call_service",
      "service": "<service>",
      "operation": "<operation>",
      "input": {}
    }
  }
}
```
