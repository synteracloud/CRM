'use strict';

/**
 * Workflow Execution Engine routes.
 *
 * Docs: backend/docs/infrastructure/workflow-catalog.md
 * Mount: /api/v1/workflows/*
 *
 * Covers:
 *   GET/POST       /workflows            — list/create definitions
 *   GET/PATCH      /workflows/:id        — definition detail/update
 *   POST           /workflows/:id/publish — activate definition
 *   POST           /workflows/:id/simulate — dry-run step simulation
 *   GET            /workflows/runs       — list executions
 *   GET            /workflows/runs/:id   — execution detail + steps
 *   POST           /workflows/runs/:id/retry   — retry failed execution
 *   POST           /workflows/runs/:id/cancel  — cancel running execution
 *   GET            /workflows/:id/stats  — execution stats per definition
 */

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const VALID_WF_STATUS    = ['draft', 'active', 'paused', 'archived'];
const VALID_EXEC_STATUS  = ['running', 'succeeded', 'failed', 'retrying', 'cancelled'];
const TERMINAL_EXEC      = new Set(['succeeded', 'cancelled']);
const RETRYABLE_EXEC     = new Set(['failed', 'retrying']);

const WF_TRANSITIONS = {
  draft:    ['active', 'archived'],
  active:   ['paused', 'archived'],
  paused:   ['active', 'archived'],
  archived: [],
};

function nowIso() { return new Date().toISOString(); }
function canTransit(from, to) { return (WF_TRANSITIONS[from] || []).includes(to); }

// ── In-memory stores ──────────────────────────────────────────────────────────
const _memDefinitions = [
  { workflow_id:'wf-001', tenant_id:'_all', workflow_key:'lead_followup_enforcement',  name:'Lead Follow-up Enforcement',   description:'Triggers follow-up tasks when a lead goes idle.', status:'active',  trigger_events:['lead.idle.v1'],                              steps_dsl:[{id:'s1',type:'condition',name:'Check idle threshold',condition:'lead.idle_days > threshold'},{id:'s2',type:'action',name:'Create follow-up task',action:'create_followup_task'},{id:'s3',type:'notification',name:'Notify owner',action:'send_whatsapp_alert'}], max_retries:3, retry_backoff_seconds:60, timeout_seconds:300, is_system:true, version:1, created_by:'system', created_at:'2026-01-01T00:00:00Z', updated_at:'2026-01-01T00:00:00Z' },
  { workflow_id:'wf-002', tenant_id:'_all', workflow_key:'collections_reminder',        name:'Collections Auto-Reminder',    description:'Sends WhatsApp reminders on overdue invoices.', status:'active',  trigger_events:['invoice.overdue.v1'],                         steps_dsl:[{id:'s1',type:'action',name:'Load invoice',action:'load_invoice'},{id:'s2',type:'notification',name:'Send WhatsApp',action:'send_whatsapp'}], max_retries:3, retry_backoff_seconds:60, timeout_seconds:120, is_system:true, version:1, created_by:'system', created_at:'2026-01-01T00:00:00Z', updated_at:'2026-01-01T00:00:00Z' },
  { workflow_id:'wf-003', tenant_id:'_all', workflow_key:'sla_breach_notify',           name:'SLA Breach Notification',      description:'Escalates and notifies on SLA breaches.', status:'active',  trigger_events:['case.sla.breached.v1','case.sla.first_response_breached.v1'], steps_dsl:[{id:'s1',type:'action',name:'Load case',action:'load_case'},{id:'s2',type:'action',name:'Escalate case',action:'escalate_case'},{id:'s3',type:'notification',name:'Notify supervisor',action:'notify_supervisor'},{id:'s4',type:'action',name:'Log event',action:'log_event'}], max_retries:3, retry_backoff_seconds:60, timeout_seconds:300, is_system:true, version:1, created_by:'system', created_at:'2026-01-01T00:00:00Z', updated_at:'2026-01-01T00:00:00Z' },
  { workflow_id:'wf-004', tenant_id:'_all', workflow_key:'lead_assignment',             name:'Lead Territory Assignment',    description:'Evaluates territory and assigns owner on lead creation.', status:'active', trigger_events:['lead.created.v1'], steps_dsl:[{id:'s1',type:'action',name:'Evaluate territory',action:'evaluate_territory'},{id:'s2',type:'action',name:'Assign owner',action:'assign_owner'}], max_retries:3, retry_backoff_seconds:30, timeout_seconds:60, is_system:true, version:1, created_by:'system', created_at:'2026-01-01T00:00:00Z', updated_at:'2026-01-01T00:00:00Z' },
  { workflow_id:'wf-005', tenant_id:'_all', workflow_key:'opportunity_stage_notify',    name:'Stage Change Notification',    description:'Notifies team on opportunity stage transitions.', status:'active', trigger_events:['opportunity.stage.changed.v1'], steps_dsl:[{id:'s1',type:'condition',name:'Check notify config',condition:'stage in notify_stages'},{id:'s2',type:'notification',name:'Notify team',action:'send_stage_alert'},{id:'s3',type:'action',name:'Update forecast',action:'refresh_forecast'}], max_retries:3, retry_backoff_seconds:60, timeout_seconds:120, is_system:true, version:1, created_by:'system', created_at:'2026-01-01T00:00:00Z', updated_at:'2026-01-01T00:00:00Z' },
];

const _memExecutions = [
  { execution_id:'exec-001', workflow_id:'wf-001', tenant_id:'_all', workflow_key:'lead_followup_enforcement',  workflow_name:'Lead Follow-up Enforcement',  trigger_event:'lead.idle.v1',                 trigger_payload:{}, status:'succeeded', step_count:3, current_step:3, failed_step:null, error_message:null, retry_count:0, parent_execution_id:null, started_at:'2026-05-29T08:00:00Z', ended_at:'2026-05-29T08:00:05Z', duration_ms:5200, created_at:'2026-05-29T08:00:00Z' },
  { execution_id:'exec-002', workflow_id:'wf-002', tenant_id:'_all', workflow_key:'collections_reminder',       workflow_name:'Collections Auto-Reminder',   trigger_event:'invoice.overdue.v1',           trigger_payload:{}, status:'failed',    step_count:2, current_step:2, failed_step:'send_whatsapp',    error_message:'WhatsApp send failed: rate limit', retry_count:0, parent_execution_id:null, started_at:'2026-05-29T07:30:00Z', ended_at:'2026-05-29T07:30:03Z', duration_ms:3100, created_at:'2026-05-29T07:30:00Z' },
  { execution_id:'exec-003', workflow_id:'wf-003', tenant_id:'_all', workflow_key:'sla_breach_notify',          workflow_name:'SLA Breach Notification',     trigger_event:'case.sla.breached.v1',         trigger_payload:{}, status:'succeeded', step_count:4, current_step:4, failed_step:null, error_message:null, retry_count:0, parent_execution_id:null, started_at:'2026-05-29T07:00:00Z', ended_at:'2026-05-29T07:00:08Z', duration_ms:8200, created_at:'2026-05-29T07:00:00Z' },
  { execution_id:'exec-004', workflow_id:'wf-004', tenant_id:'_all', workflow_key:'lead_assignment',            workflow_name:'Lead Territory Assignment',   trigger_event:'lead.created.v1',              trigger_payload:{}, status:'succeeded', step_count:2, current_step:2, failed_step:null, error_message:null, retry_count:0, parent_execution_id:null, started_at:'2026-05-29T06:45:00Z', ended_at:'2026-05-29T06:45:04Z', duration_ms:4000, created_at:'2026-05-29T06:45:00Z' },
  { execution_id:'exec-005', workflow_id:'wf-002', tenant_id:'_all', workflow_key:'collections_reminder',       workflow_name:'Collections Auto-Reminder',   trigger_event:'invoice.overdue.v1',           trigger_payload:{}, status:'retrying',  step_count:2, current_step:2, failed_step:'send_whatsapp', error_message:'Retrying after WhatsApp failure', retry_count:1, parent_execution_id:'exec-002', started_at:'2026-05-28T20:00:00Z', ended_at:null, duration_ms:null, created_at:'2026-05-28T20:00:00Z' },
  { execution_id:'exec-006', workflow_id:'wf-005', tenant_id:'_all', workflow_key:'opportunity_stage_notify',   workflow_name:'Stage Change Notification',   trigger_event:'opportunity.stage.changed.v1', trigger_payload:{}, status:'succeeded', step_count:3, current_step:3, failed_step:null, error_message:null, retry_count:0, parent_execution_id:null, started_at:'2026-05-28T15:30:00Z', ended_at:'2026-05-28T15:30:06Z', duration_ms:6000, created_at:'2026-05-28T15:30:00Z' },
  { execution_id:'exec-007', workflow_id:'wf-001', tenant_id:'_all', workflow_key:'lead_followup_enforcement',  workflow_name:'Lead Follow-up Enforcement',  trigger_event:'lead.idle.v1',                 trigger_payload:{}, status:'failed',    step_count:3, current_step:3, failed_step:'escalate_to_manager', error_message:'Manager notification failed — SMTP timeout', retry_count:0, parent_execution_id:null, started_at:'2026-05-28T14:00:00Z', ended_at:'2026-05-28T14:00:02Z', duration_ms:2100, created_at:'2026-05-28T14:00:00Z' },
  { execution_id:'exec-008', workflow_id:'wf-003', tenant_id:'_all', workflow_key:'sla_breach_notify',          workflow_name:'SLA Breach Notification',     trigger_event:'case.sla.breached.v1',         trigger_payload:{}, status:'running',   step_count:4, current_step:2, failed_step:null, error_message:null, retry_count:0, parent_execution_id:null, started_at:'2026-05-29T09:00:00Z', ended_at:null, duration_ms:null, created_at:'2026-05-29T09:00:00Z' },
];

const _memSteps = {
  'exec-007': [
    { step_record_id:'sr-001', execution_id:'exec-007', workflow_id:'wf-001', tenant_id:'_all', step_index:0, step_name:'check_idle_threshold', step_type:'condition',    status:'succeeded', input_data:{ lead_id:'l-001', idle_days:7 },             output_data:{ threshold_met:true }, error_message:null, duration_ms:120, started_at:'2026-05-28T14:00:00Z', ended_at:'2026-05-28T14:00:00Z', created_at:'2026-05-28T14:00:00Z' },
    { step_record_id:'sr-002', execution_id:'exec-007', workflow_id:'wf-001', tenant_id:'_all', step_index:1, step_name:'load_lead_record',       step_type:'action',       status:'succeeded', input_data:{ lead_id:'l-001' },                          output_data:{ lead:{ name:'Test Lead' } }, error_message:null, duration_ms:340, started_at:'2026-05-28T14:00:00Z', ended_at:'2026-05-28T14:00:00Z', created_at:'2026-05-28T14:00:00Z' },
    { step_record_id:'sr-003', execution_id:'exec-007', workflow_id:'wf-001', tenant_id:'_all', step_index:2, step_name:'escalate_to_manager',    step_type:'notification', status:'failed',    input_data:{ owner_id:'u-001', manager_id:'u-003' },    output_data:null, error_message:'Manager notification failed — SMTP timeout', duration_ms:1640, started_at:'2026-05-28T14:00:01Z', ended_at:'2026-05-28T14:00:02Z', created_at:'2026-05-28T14:00:01Z' },
  ],
};

// ── Router ─────────────────────────────────────────────────────────────────────
const router = express.Router();

// ── Workflow Runs sub-routes (must be declared BEFORE /:id to avoid collision) ──

// GET /workflows/runs
router.get(
  '/runs',
  requestValidationMiddleware(),
  requireScopes([SCOPES.WORKFLOWS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { status, workflow_key } = req.query;
    const limit  = Math.min(parseInt(req.query.limit  || '25', 10), 200);
    const offset = parseInt(req.query.offset || '0', 10);

    let rows = _memExecutions.filter(e => e.tenant_id === tenantId || e.tenant_id === '_all');
    if (status)       rows = rows.filter(e => e.status       === status);
    if (workflow_key) rows = rows.filter(e => e.workflow_key === workflow_key);

    // Sort by started_at DESC
    rows = rows.sort((a, b) => new Date(b.started_at) - new Date(a.started_at));

    return respondSuccess(res, rows.slice(offset, offset + limit), { count: rows.length, total: rows.length, limit, offset });
  },
);

// GET /workflows/runs/:execution_id
router.get(
  '/runs/:execution_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.WORKFLOWS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { execution_id } = req.params;

    const e = _memExecutions.find(x => x.execution_id === execution_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!e) return respondError(res, 404, 'NOT_FOUND', 'Execution not found.');

    const steps = _memSteps[execution_id] || [];
    return respondSuccess(res, { ...e, steps });
  },
);

// POST /workflows/runs/:execution_id/retry
router.post(
  '/runs/:execution_id/retry',
  requestValidationMiddleware(),
  requireScopes([SCOPES.WORKFLOWS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { execution_id } = req.params;

    const e = _memExecutions.find(x => x.execution_id === execution_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!e) return respondError(res, 404, 'NOT_FOUND', 'Execution not found.');
    if (!RETRYABLE_EXEC.has(e.status))
      return respondError(res, 422, 'NOT_RETRYABLE', `Execution with status '${e.status}' cannot be retried.`);

    const def = _memDefinitions.find(d => d.workflow_id === e.workflow_id);
    const maxRetries = def ? def.max_retries : 3;

    if ((e.retry_count || 0) >= maxRetries)
      return respondError(res, 422, 'MAX_RETRIES_EXCEEDED', `Max retries (${maxRetries}) reached for this execution.`);

    const ts = nowIso();
    const retryExec = {
      execution_id:        randomUUID(),
      workflow_id:         e.workflow_id,
      tenant_id:           tenantId,
      workflow_key:        e.workflow_key,
      workflow_name:       e.workflow_name,
      trigger_event:       e.trigger_event,
      trigger_payload:     e.trigger_payload || {},
      status:              'running',
      step_count:          e.step_count,
      current_step:        0,
      failed_step:         null,
      error_message:       null,
      retry_count:         (e.retry_count || 0) + 1,
      parent_execution_id: execution_id,
      started_at:          ts,
      ended_at:            null,
      duration_ms:         null,
      created_at:          ts,
    };
    _memExecutions.push(retryExec);

    // Mark original as retrying
    e.status = 'retrying';

    return res.status(201).json({ data: retryExec, original_execution_id: execution_id, meta: { request_id: req.request_id } });
  },
);

// POST /workflows/runs/:execution_id/cancel
router.post(
  '/runs/:execution_id/cancel',
  requestValidationMiddleware(),
  requireScopes([SCOPES.WORKFLOWS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { execution_id } = req.params;

    const e = _memExecutions.find(x => x.execution_id === execution_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!e) return respondError(res, 404, 'NOT_FOUND', 'Execution not found.');
    if (TERMINAL_EXEC.has(e.status))
      return respondError(res, 409, 'CONFLICT', `Execution is already in terminal state '${e.status}'.`);

    const ts = nowIso();
    e.status   = 'cancelled';
    e.ended_at = ts;
    return respondSuccess(res, e);
  },
);

// ── Workflow Definitions ───────────────────────────────────────────────────────

// GET /workflows
router.get(
  '/',
  requestValidationMiddleware(),
  requireScopes([SCOPES.WORKFLOWS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { status } = req.query;

    let rows = _memDefinitions.filter(d => d.tenant_id === tenantId || d.tenant_id === '_all');
    if (status) rows = rows.filter(d => d.status === status);

    return respondSuccess(res, rows, { count: rows.length });
  },
);

// POST /workflows
router.post(
  '/',
  requestValidationMiddleware(['name', 'trigger_events']),
  requireScopes([SCOPES.WORKFLOWS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { name, description, trigger_events, steps_dsl = [], max_retries = 3, timeout_seconds = 300 } = req.body;

    if (!Array.isArray(trigger_events) || trigger_events.length === 0)
      return respondError(res, 422, 'VALIDATION_ERROR', 'trigger_events must be a non-empty array.', [{ field: 'trigger_events', reason: 'required_non_empty' }]);

    const ts = nowIso();
    const workflow_key = name.toLowerCase().replace(/[^a-z0-9]+/g, '_');
    const def = {
      workflow_id:           randomUUID(),
      tenant_id:             tenantId,
      workflow_key,
      name,
      description:           description || null,
      status:                'draft',
      trigger_events,
      steps_dsl,
      max_retries,
      retry_backoff_seconds: 60,
      timeout_seconds,
      is_system:             false,
      version:               1,
      created_by:            userId,
      created_at:            ts,
      updated_at:            ts,
    };
    _memDefinitions.push(def);
    return res.status(201).json({ data: def, meta: { request_id: req.request_id } });
  },
);

// GET /workflows/:id
router.get(
  '/:workflow_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.WORKFLOWS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { workflow_id } = req.params;

    const def = _memDefinitions.find(d => d.workflow_id === workflow_id && (d.tenant_id === tenantId || d.tenant_id === '_all'));
    if (!def) return respondError(res, 404, 'NOT_FOUND', 'Workflow not found.');

    const recentRuns = _memExecutions.filter(e => e.workflow_id === workflow_id).slice(0, 5);
    return respondSuccess(res, { ...def, recent_runs: recentRuns });
  },
);

// PATCH /workflows/:id
router.patch(
  '/:workflow_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.WORKFLOWS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { workflow_id } = req.params;

    const def = _memDefinitions.find(d => d.workflow_id === workflow_id && (d.tenant_id === tenantId || d.tenant_id === '_all'));
    if (!def) return respondError(res, 404, 'NOT_FOUND', 'Workflow not found.');
    if (def.is_system) return respondError(res, 403, 'FORBIDDEN', 'System workflows cannot be edited.');
    if (def.status === 'archived') return respondError(res, 409, 'CONFLICT', 'Archived workflows cannot be edited.');

    const { name, description, trigger_events, steps_dsl, max_retries, timeout_seconds } = req.body;
    if (name)            def.name            = name;
    if (description)     def.description     = description;
    if (trigger_events)  def.trigger_events  = trigger_events;
    if (steps_dsl)       def.steps_dsl       = steps_dsl;
    if (max_retries)     def.max_retries     = max_retries;
    if (timeout_seconds) def.timeout_seconds = timeout_seconds;
    def.version    += 1;
    def.updated_at  = nowIso();

    return respondSuccess(res, def);
  },
);

// POST /workflows/:id/publish — activate
router.post(
  '/:workflow_id/publish',
  requestValidationMiddleware(),
  requireScopes([SCOPES.WORKFLOWS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { workflow_id } = req.params;

    const def = _memDefinitions.find(d => d.workflow_id === workflow_id && (d.tenant_id === tenantId || d.tenant_id === '_all'));
    if (!def) return respondError(res, 404, 'NOT_FOUND', 'Workflow not found.');
    if (!canTransit(def.status, 'active'))
      return respondError(res, 422, 'TRANSITION_ERROR', `Cannot publish workflow with status '${def.status}'.`);
    if (!def.steps_dsl || def.steps_dsl.length === 0)
      return respondError(res, 422, 'VALIDATION_ERROR', 'Workflow must have at least one step before publishing.', [{ field: 'steps_dsl', reason: 'required' }]);

    def.status     = 'active';
    def.updated_at = nowIso();
    return respondSuccess(res, def);
  },
);

// POST /workflows/:id/simulate — dry-run
router.post(
  '/:workflow_id/simulate',
  requestValidationMiddleware(),
  requireScopes([SCOPES.WORKFLOWS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { workflow_id } = req.params;
    const trigger_payload = req.body.trigger_payload || {};

    const def = _memDefinitions.find(d => d.workflow_id === workflow_id && (d.tenant_id === tenantId || d.tenant_id === '_all'));
    if (!def) return respondError(res, 404, 'NOT_FOUND', 'Workflow not found.');

    const steps = (def.steps_dsl || []).map((step, i) => ({
      step_index:  i,
      step_name:   step.name || `Step ${i+1}`,
      step_type:   step.type || 'action',
      status:      'succeeded',
      duration_ms: 100 + i * 50,
      output_data: step.type === 'condition' ? { result: true, branch: 'true' } : { result: 'ok' },
      simulated:   true,
    }));

    return respondSuccess(res, {
      workflow_id,
      simulated:    true,
      trigger_payload,
      steps,
      total_steps:  steps.length,
      estimated_ms: steps.reduce((s, st) => s + st.duration_ms, 0),
    });
  },
);

// GET /workflows/:id/stats
router.get(
  '/:workflow_id/stats',
  requestValidationMiddleware(),
  requireScopes([SCOPES.WORKFLOWS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { workflow_id } = req.params;

    const def = _memDefinitions.find(d => d.workflow_id === workflow_id && (d.tenant_id === tenantId || d.tenant_id === '_all'));
    if (!def) return respondError(res, 404, 'NOT_FOUND', 'Workflow not found.');

    const runs      = _memExecutions.filter(e => e.workflow_id === workflow_id);
    const succeeded = runs.filter(e => e.status === 'succeeded').length;
    const failed    = runs.filter(e => e.status === 'failed').length;
    const total     = runs.length;
    const durations = runs.filter(e => e.duration_ms).map(e => e.duration_ms);

    return respondSuccess(res, {
      workflow_id,
      total_runs:      total,
      succeeded,
      failed,
      retrying:        runs.filter(e => e.status === 'retrying').length,
      running:         runs.filter(e => e.status === 'running').length,
      success_rate:    total ? Math.round(succeeded / total * 100) : 0,
      avg_duration_ms: durations.length ? Math.round(durations.reduce((s, d) => s + d, 0) / durations.length) : 0,
    });
  },
);

module.exports = router;
