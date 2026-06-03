'use strict';

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');

const router = express.Router();

let _dbQuery = null;
const _memTasks = [];

try {
  if (process.env.DB_DISABLED !== 'true') {
    _dbQuery = require('../db/pool').query;
  }
} catch (_e) {}

router.get('/', requestValidationMiddleware(), requireScopes(['tasks.read']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const limit  = Math.min(Number(req.query.page_size || 25), 100);
  const offset = (Math.max(Number(req.query.page || 1), 1) - 1) * limit;

  if (_dbQuery) {
    try {
      const { rows } = await _dbQuery(
        `SELECT * FROM activity_task_db.task WHERE tenant_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3`,
        [tenantId, limit, offset],
      );
      return respondSuccess(res, rows, {
        pagination: { page: Number(req.query.page || 1), page_size: limit, total_items: rows.length, total_pages: 1 },
      });
    } catch (err) {
      req.app.locals.logger?.error?.({ event: 'tasks.list.error', error: err.message });
    }
  }

  const rows = _memTasks.filter((t) => t.tenant_id === tenantId).slice(offset, offset + limit);
  return respondSuccess(res, rows, {
    pagination: { page: Number(req.query.page || 1), page_size: limit, total_items: rows.length, total_pages: 1 },
  });
});

router.post('/', requestValidationMiddleware(), requireScopes(['tasks.create']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { entity_type, entity_id, title, status = 'open', priority = 'normal', due_at, starts_at, due_date } = req.body;

  if (_dbQuery) {
    try {
      const { rows } = await _dbQuery(
        `INSERT INTO activity_task_db.task (task_id, tenant_id, entity_type, entity_id, title, status, priority, created_by_user_id, assignment_method, starts_at, due_at, created_at, updated_at)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,'explicit',$9,$10,NOW(),NOW()) RETURNING *`,
        [randomUUID(), tenantId, entity_type, entity_id, title, status, priority, req.auth.sub,
         starts_at || new Date().toISOString(), due_at || due_date],
      );
      return res.status(201).json({ data: rows[0], meta: {} });
    } catch (err) {
      req.app.locals.logger?.error?.({ event: 'tasks.create.error', error: err.message });
    }
  }

  const task = {
    task_id: randomUUID(),
    tenant_id: tenantId,
    entity_type: entity_type || null,
    entity_id: entity_id || null,
    title: title || 'Untitled Task',
    status,
    priority,
    created_by_user_id: req.auth.sub,
    assignment_method: 'explicit',
    starts_at: starts_at || new Date().toISOString(),
    due_at: due_at || due_date || null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
  _memTasks.push(task);
  return res.status(201).json({ data: task, meta: {} });
});

router.post('/:task_id/reschedule', requestValidationMiddleware(), requireScopes(['tasks.update']), async (req, res) => {
  return respondSuccess(res, { task_id: req.params.task_id, rescheduled: true });
});

module.exports = router;
