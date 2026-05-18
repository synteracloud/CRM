'use strict';

/**
 * Follow-up enforcement routes.
 *
 * Docs: docs/followup-enforcement-model.md
 *       docs/integration-end-to-end-auto-fix.md — Flow 1 and Flow 3
 *
 * Enforces: no lead can remain idle; every follow-up must have an owner.
 * DB layer: FollowupsRepository (gateway/db/repositories/followups.repository.js)
 * Fallback: in-memory array when DB_DISABLED=true or pg not installed.
 *
 * Note: DB table uses state ∈ (pending, overdue, completed).
 *       In-memory fallback uses extended states for richer client feedback.
 */

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const router = express.Router();

// ── Repository bootstrap ───────────────────────────────────────────────────────
let repo = null;
let VALID_STATES, VALID_ESCALATION_LEVELS, VALID_RULE_TYPES, VALID_GENERATED_BY;

try {
  if (process.env.DB_DISABLED !== 'true') {
    const mod = require('../db/repositories/followups.repository');
    repo = new mod.FollowupsRepository();
    ({ VALID_STATES, VALID_ESCALATION_LEVELS, VALID_RULE_TYPES, VALID_GENERATED_BY } = mod);
  }
} catch (_e) {
  // pg not installed or DB unavailable — use in-memory fallback below.
}

if (!repo) {
  VALID_STATES           = ['pending', 'overdue', 'completed'];
  VALID_ESCALATION_LEVELS = ['none', 'reminder', 'warning', 'escalated', 'reassigned'];
  VALID_RULE_TYPES       = ['TimeBased', 'ActivityBased', 'InactivityBased'];
}

// In-memory fallback store (used only when repo === null)
const _memFollowups = [];

function nowIso() { return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'); }

// ── GET /followups ────────────────────────────────────────────────────────────
router.get('/', requestValidationMiddleware(), requireScopes([SCOPES.FOLLOWUPS_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { lead_id, owner_id, state } = req.query;
  const limit  = Math.min(parseInt(req.query.limit  || '25', 10), 200);
  const offset = parseInt(req.query.offset || '0', 10);

  if (repo) {
    try {
      const rows = await repo.listTasks(tenantId, { lead_id, owner_id, state, limit, offset });
      return respondSuccess(res, rows, { count: rows.length, limit, offset });
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  let rows = _memFollowups.filter((f) => f.tenant_id === tenantId);
  if (lead_id)  rows = rows.filter((f) => f.lead_id  === lead_id);
  if (owner_id) rows = rows.filter((f) => f.owner_id === owner_id);
  if (state)    rows = rows.filter((f) => f.state    === state);
  const page = rows.slice(offset, offset + limit);
  return respondSuccess(res, page, { count: page.length, total: rows.length, limit, offset });
});

// ── POST /followups ───────────────────────────────────────────────────────────
router.post(
  '/',
  requestValidationMiddleware(['lead_id', 'owner_id', 'due_at']),
  requireScopes([SCOPES.FOLLOWUPS_CREATE]),
  async (req, res) => {
    const { lead_id, owner_id, due_at, rule_type, generated_by, is_canonical } = req.body;
    const tenantId = req.auth.tenant_id;

    if (isNaN(Date.parse(due_at)))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid field.', [{ field: 'due_at', reason: 'must_be_iso8601' }]);

    if (repo) {
      try {
        const task = await repo.createTask(tenantId, {
          task_id:          randomUUID(),
          lead_id,
          owner_id,
          state:            'pending',
          due_at,
          rule_type:        rule_type    || 'TimeBased',
          escalation_level: 'none',
          generated_by:     generated_by || 'Scheduler',
          is_canonical:     is_canonical !== false,
        });
        return res.status(201).json({ data: task, meta: { request_id: req.request_id } });
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    const ts = nowIso();
    const followup = {
      task_id:          `fu_${Math.random().toString(36).slice(2, 14)}`,
      tenant_id:        tenantId,
      lead_id,
      owner_id,
      state:            'pending',
      due_at,
      rule_type:        rule_type || 'TimeBased',
      escalation_level: 'none',
      is_canonical:     true,
      completed_at:     null,
      created_at:       ts,
      updated_at:       ts,
    };
    _memFollowups.push(followup);
    return res.status(201).json({ data: followup, meta: { request_id: req.request_id } });
  },
);

// ── GET /followups/:task_id ───────────────────────────────────────────────────
router.get('/:task_id', requestValidationMiddleware(), requireScopes([SCOPES.FOLLOWUPS_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { task_id } = req.params;

  if (repo) {
    try {
      const task = await repo.findTaskById(tenantId, task_id);
      if (!task) return respondError(res, 404, 'NOT_FOUND', 'Follow-up task not found.');
      return respondSuccess(res, task);
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  const fu = _memFollowups.find((f) => f.task_id === task_id && f.tenant_id === tenantId);
  if (!fu) return respondError(res, 404, 'NOT_FOUND', 'Follow-up task not found.');
  return respondSuccess(res, fu);
});

// ── POST /followups/:task_id/complete ─────────────────────────────────────────
router.post(
  '/:task_id/complete',
  requestValidationMiddleware(),
  requireScopes([SCOPES.FOLLOWUPS_COMPLETE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { task_id } = req.params;
    const { completed_activity_id } = req.body;

    if (repo) {
      try {
        const task = await repo.completeTask(tenantId, task_id, { completed_activity_id });
        if (!task) {
          // Could be not found or already completed — check which
          const existing = await repo.findTaskById(tenantId, task_id);
          if (!existing) return respondError(res, 404, 'NOT_FOUND', 'Follow-up task not found.');
          return respondSuccess(res, existing);  // already completed — idempotent
        }
        return respondSuccess(res, task);
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    const fu = _memFollowups.find((f) => f.task_id === task_id && f.tenant_id === tenantId);
    if (!fu) return respondError(res, 404, 'NOT_FOUND', 'Follow-up task not found.');
    if (fu.state === 'completed') return respondSuccess(res, fu);  // idempotent
    fu.state        = 'completed';
    fu.completed_at = nowIso();
    fu.updated_at   = nowIso();
    return respondSuccess(res, fu);
  },
);

// ── POST /followups/:task_id/snooze ──────────────────────────────────────────
router.post(
  '/:task_id/snooze',
  requestValidationMiddleware(['snoozed_until']),
  requireScopes([SCOPES.FOLLOWUPS_SNOOZE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { task_id } = req.params;
    const { snoozed_until } = req.body;

    if (isNaN(Date.parse(snoozed_until)))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid field.', [{ field: 'snoozed_until', reason: 'must_be_iso8601' }]);

    if (repo) {
      try {
        const task = await repo.findTaskById(tenantId, task_id);
        if (!task) return respondError(res, 404, 'NOT_FOUND', 'Follow-up task not found.');
        if (task.state === 'completed')
          return respondError(res, 409, 'CONFLICT', 'Cannot snooze a completed follow-up.');

        const updated = await repo.snoozeTask(tenantId, task_id, { snoozed_until });
        return respondSuccess(res, updated || task);
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    const fu = _memFollowups.find((f) => f.task_id === task_id && f.tenant_id === tenantId);
    if (!fu) return respondError(res, 404, 'NOT_FOUND', 'Follow-up task not found.');
    if (fu.state === 'completed')
      return respondError(res, 409, 'CONFLICT', 'Cannot snooze a completed follow-up.');
    fu.due_at      = snoozed_until;
    fu.updated_at  = nowIso();
    return respondSuccess(res, fu);
  },
);

// ── GET /followups/lead/:lead_id/canonical ─────────────────────────────────────
// Returns the single canonical pending task for a lead (enforced unique by DB).
router.get(
  '/lead/:lead_id/canonical',
  requestValidationMiddleware(),
  requireScopes([SCOPES.FOLLOWUPS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { lead_id } = req.params;

    if (repo) {
      try {
        const task = await repo.getCanonicalPendingTask(tenantId, lead_id);
        if (!task) return respondError(res, 404, 'NOT_FOUND', 'No canonical pending task for this lead.');
        return respondSuccess(res, task);
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    const fu = _memFollowups.find(
      (f) => f.lead_id === lead_id && f.tenant_id === tenantId && f.state === 'pending' && f.is_canonical,
    );
    if (!fu) return respondError(res, 404, 'NOT_FOUND', 'No canonical pending task for this lead.');
    return respondSuccess(res, fu);
  },
);

module.exports = router;
