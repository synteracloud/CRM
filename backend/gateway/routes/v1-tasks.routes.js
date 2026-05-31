'use strict';

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { query } = require('../db/pool');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['tasks.read']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const limit  = Math.min(Number(req.query.page_size || 25), 100);
  const offset = (Math.max(Number(req.query.page || 1), 1) - 1) * limit;
  try {
    const { rows } = await query(
      `SELECT * FROM activity_task_db.task WHERE tenant_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3`,
      [tenantId, limit, offset],
    );
    return respondSuccess(res, rows, {
      pagination: { page: Number(req.query.page || 1), page_size: limit, total_items: rows.length, total_pages: 1 },
    });
  } catch (err) {
    req.app.locals.logger?.error?.({ event: 'tasks.list.error', error: err.message });
    return respondError(res, 'internal_error', 'DB_ERROR', [], 500);
  }
});

router.post('/', requestValidationMiddleware(), requireScopes(['tasks.create']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { entity_type, entity_id, title, status = 'open', priority = 'normal', due_at, starts_at } = req.body;
  try {
    const { rows } = await query(
      `INSERT INTO activity_task_db.task (task_id, tenant_id, entity_type, entity_id, title, status, priority, created_by_user_id, assignment_method, starts_at, due_at, created_at, updated_at)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,'explicit',$9,$10,NOW(),NOW()) RETURNING *`,
      [randomUUID(), tenantId, entity_type, entity_id, title, status, priority, req.auth.sub,
       starts_at || new Date().toISOString(), due_at],
    );
    return res.status(201).json({ data: rows[0], meta: {} });
  } catch (err) {
    return respondError(res, 'internal_error', 'DB_ERROR', [], 500);
  }
});

router.post('/:task_id/reschedule', requestValidationMiddleware(), requireScopes(['tasks.update']), async (req, res) => {
  return respondSuccess(res, { task_id: req.params.task_id, rescheduled: true });
});

module.exports = router;
