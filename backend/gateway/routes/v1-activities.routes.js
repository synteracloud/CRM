'use strict';

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');

const router = express.Router();

let _dbQuery = null;
const _memActivities = [];

try {
  if (process.env.DB_DISABLED !== 'true') {
    _dbQuery = require('../db/pool').query;
  }
} catch (_e) {}

router.get('/', requestValidationMiddleware(), requireScopes(['activities.read']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const limit  = Math.min(Number(req.query.page_size || 25), 100);
  const offset = (Math.max(Number(req.query.page || 1), 1) - 1) * limit;

  if (_dbQuery) {
    try {
      const { rows } = await _dbQuery(
        `SELECT * FROM activity_task_db.activity WHERE tenant_id = $1 ORDER BY event_time DESC LIMIT $2 OFFSET $3`,
        [tenantId, limit, offset],
      );
      return respondSuccess(res, rows, {
        pagination: { page: Number(req.query.page || 1), page_size: limit, total_items: rows.length, total_pages: 1 },
      });
    } catch (err) {
      req.app.locals.logger?.error?.({ event: 'activities.list.error', error: err.message });
    }
  }

  const rows = _memActivities.filter((a) => a.tenant_id === tenantId).slice(offset, offset + limit);
  return respondSuccess(res, rows, {
    pagination: { page: Number(req.query.page || 1), page_size: limit, total_items: rows.length, total_pages: 1 },
  });
});

router.post('/', requestValidationMiddleware(), requireScopes(['activities.create']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { entity_type, entity_id, event_type, payload_json = {}, source_service = 'gateway' } = req.body;

  if (_dbQuery) {
    try {
      const { rows } = await _dbQuery(
        `INSERT INTO activity_task_db.activity (activity_id, tenant_id, actor_user_id, entity_type, entity_id, event_type, event_time, payload_json, source_service, created_at)
         VALUES ($1,$2,$3,$4,$5,$6,NOW(),$7,$8,NOW()) RETURNING *`,
        [randomUUID(), tenantId, req.auth.sub, entity_type, entity_id, event_type,
         JSON.stringify(payload_json), source_service],
      );
      return res.status(201).json({ data: rows[0], meta: {} });
    } catch (err) {
      req.app.locals.logger?.error?.({ event: 'activities.create.error', error: err.message });
    }
  }

  const activity = {
    activity_id: randomUUID(),
    tenant_id: tenantId,
    actor_user_id: req.auth.sub,
    entity_type: entity_type || null,
    entity_id: entity_id || null,
    event_type: event_type || 'generic',
    event_time: new Date().toISOString(),
    payload_json: payload_json || {},
    source_service,
    created_at: new Date().toISOString(),
  };
  _memActivities.push(activity);
  return res.status(201).json({ data: activity, meta: {} });
});

module.exports = router;
