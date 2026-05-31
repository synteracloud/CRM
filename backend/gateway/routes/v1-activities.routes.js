'use strict';

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { query } = require('../db/pool');

const router = express.Router();

router.get('/', requestValidationMiddleware(), requireScopes(['activities.read']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const limit  = Math.min(Number(req.query.page_size || 25), 100);
  const offset = (Math.max(Number(req.query.page || 1), 1) - 1) * limit;
  try {
    const { rows } = await query(
      `SELECT * FROM activity_task_db.activity WHERE tenant_id = $1 ORDER BY event_time DESC LIMIT $2 OFFSET $3`,
      [tenantId, limit, offset],
    );
    return respondSuccess(res, rows, {
      pagination: { page: Number(req.query.page || 1), page_size: limit, total_items: rows.length, total_pages: 1 },
    });
  } catch (err) {
    req.app.locals.logger?.error?.({ event: 'activities.list.error', error: err.message });
    return respondError(res, 'internal_error', 'DB_ERROR', [], 500);
  }
});

router.post('/', requestValidationMiddleware(), requireScopes(['activities.create']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { entity_type, entity_id, event_type, payload_json = {}, source_service = 'gateway' } = req.body;
  try {
    const { rows } = await query(
      `INSERT INTO activity_task_db.activity (activity_id, tenant_id, actor_user_id, entity_type, entity_id, event_type, event_time, payload_json, source_service, created_at)
       VALUES ($1,$2,$3,$4,$5,$6,NOW(),$7,$8,NOW()) RETURNING *`,
      [randomUUID(), tenantId, req.auth.sub, entity_type, entity_id, event_type,
       JSON.stringify(payload_json), source_service],
    );
    return res.status(201).json({ data: rows[0], meta: {} });
  } catch (err) {
    return respondError(res, 'internal_error', 'DB_ERROR', [], 500);
  }
});

module.exports = router;
