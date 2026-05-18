'use strict';

/**
 * Opportunity pipeline routes.
 *
 * Docs: docs/opportunities-pipeline.md
 *       docs/event-catalog.md — opportunity.stage.changed.v1, opportunity.closed.v1
 *       docs/api-standards.md
 *
 * Stage transitions emit canonical events to the event bus.
 * DB layer: OpportunitiesRepository (gateway/db/repositories/opportunities.repository.js)
 * Fallback: in-memory array when DB_DISABLED=true or pg not installed.
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
let VALID_STAGES, TERMINAL_STAGES, VALID_FORECASTS;

try {
  if (process.env.DB_DISABLED !== 'true') {
    const mod = require('../db/repositories/opportunities.repository');
    repo = new mod.OpportunitiesRepository();
    ({ VALID_STAGES, TERMINAL_STAGES, VALID_FORECASTS } = mod);
  }
} catch (_e) {
  // pg not installed or DB unavailable — use in-memory fallback below.
}

if (!repo) {
  VALID_STAGES    = ['qualification', 'discovery', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];
  TERMINAL_STAGES = new Set(['closed_won', 'closed_lost']);
  VALID_FORECASTS = ['pipeline', 'best_case', 'commit', 'closed', 'omitted'];
}

// In-memory fallback store (used only when repo === null)
const _memOpportunities = [];
const _memEvents = [];

function nowIso() { return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'); }

function emitEvent(eventType, payload) {
  _memEvents.push({ event_type: eventType, occurred_at: nowIso(), ...payload });
}

// ── GET /opportunities ────────────────────────────────────────────────────────
router.get('/', requestValidationMiddleware(), requireScopes([SCOPES.OPPORTUNITIES_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { stage, owner_id, forecast_category } = req.query;
  const limit  = Math.min(parseInt(req.query.limit  || '25', 10), 200);
  const offset = parseInt(req.query.offset || '0', 10);

  if (repo) {
    try {
      const rows = await repo.list(tenantId, { stage, owner_id, forecast_category, limit, offset });
      return respondSuccess(res, rows, { count: rows.length, limit, offset });
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  let rows = _memOpportunities.filter((o) => o.tenant_id === tenantId);
  if (stage)             rows = rows.filter((o) => o.stage             === stage);
  if (owner_id)          rows = rows.filter((o) => o.owner_id          === owner_id);
  if (forecast_category) rows = rows.filter((o) => o.forecast_category === forecast_category);
  const page = rows.slice(offset, offset + limit);
  return respondSuccess(res, page, { count: page.length, total: rows.length, limit, offset });
});

// ── POST /opportunities ───────────────────────────────────────────────────────
router.post(
  '/',
  requestValidationMiddleware(['owner_id', 'name']),
  requireScopes([SCOPES.OPPORTUNITIES_CREATE]),
  async (req, res) => {
    const { owner_id, name, account_id, contact_id, amount, currency, close_date, stage, forecast_category } = req.body;
    const tenantId = req.auth.tenant_id;

    if (stage && !VALID_STAGES.includes(stage))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid stage.', [{ field: 'stage', reason: 'invalid_stage' }]);
    if (amount != null && (typeof amount !== 'number' || amount < 0))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid amount.', [{ field: 'amount', reason: 'must_be_non_negative' }]);

    if (repo) {
      try {
        const opp = await repo.create(tenantId, {
          opportunity_id:    randomUUID(),
          owner_id,
          name,
          account_id:        account_id        || null,
          contact_id:        contact_id        || null,
          amount:            amount            ?? null,
          currency:          currency          || 'PKR',
          close_date:        close_date        || null,
          stage:             stage             || 'qualification',
          forecast_category: forecast_category || 'pipeline',
        });
        return res.status(201).json({ data: opp, meta: { request_id: req.request_id } });
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    const ts  = nowIso();
    const opp = {
      opportunity_id:    `opp_${Math.random().toString(36).slice(2, 14)}`,
      tenant_id:         tenantId,
      owner_id,
      name,
      account_id:        account_id        || null,
      contact_id:        contact_id        || null,
      amount:            amount            ?? null,
      currency:          currency          || 'PKR',
      close_date:        close_date        || null,
      stage:             stage             || 'qualification',
      probability:       0,
      forecast_category: forecast_category || 'pipeline',
      version_no:        1,
      closed_at:         null,
      close_reason:      null,
      created_at:        ts,
      updated_at:        ts,
    };
    _memOpportunities.push(opp);
    return res.status(201).json({ data: opp, meta: { request_id: req.request_id } });
  },
);

// ── GET /opportunities/:opp_id ────────────────────────────────────────────────
router.get('/:opp_id', requestValidationMiddleware(), requireScopes([SCOPES.OPPORTUNITIES_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { opp_id } = req.params;

  if (repo) {
    try {
      const opp = await repo.findById(tenantId, opp_id);
      if (!opp) return respondError(res, 404, 'NOT_FOUND', 'Opportunity not found.');
      return respondSuccess(res, opp);
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  const opp = _memOpportunities.find((o) => o.opportunity_id === opp_id && o.tenant_id === tenantId);
  if (!opp) return respondError(res, 404, 'NOT_FOUND', 'Opportunity not found.');
  return respondSuccess(res, opp);
});

// ── PATCH /opportunities/:opp_id — update fields; advance stage if provided ───
router.patch(
  '/:opp_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.OPPORTUNITIES_UPDATE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { opp_id } = req.params;
    const { stage, amount, probability, forecast_category, close_reason, name, currency, close_date, owner_id } = req.body;

    if (stage && !VALID_STAGES.includes(stage))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid stage.', [{ field: 'stage', reason: 'invalid_stage' }]);
    if (forecast_category && !VALID_FORECASTS.includes(forecast_category))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid forecast_category.', [{ field: 'forecast_category', reason: 'invalid_value' }]);

    if (repo) {
      try {
        let opp = await repo.findById(tenantId, opp_id);
        if (!opp) return respondError(res, 404, 'NOT_FOUND', 'Opportunity not found.');
        if (TERMINAL_STAGES.has(opp.stage))
          return respondError(res, 409, 'CONFLICT', 'Opportunity is already closed.', [{ field: 'stage', reason: 'already_terminal' }]);

        // Stage transition uses dedicated atomic method
        if (stage && stage !== opp.stage) {
          opp = await repo.transitionStage(tenantId, opp_id, {
            new_stage:   stage,
            changed_by:  req.auth.user_id,
            close_reason: close_reason || null,
          });
        }

        // Field-only updates (non-stage)
        const patch = {};
        if (name             != null) patch.name             = name;
        if (amount           != null) patch.amount           = amount;
        if (currency         != null) patch.currency         = currency;
        if (close_date       != null) patch.close_date       = close_date;
        if (probability      != null) patch.probability      = probability;
        if (forecast_category != null) patch.forecast_category = forecast_category;
        if (owner_id         != null) patch.owner_id         = owner_id;
        if (close_reason     != null) patch.close_reason     = close_reason;

        if (Object.keys(patch).length > 0) {
          opp = await repo.update(tenantId, opp_id, patch) || opp;
        }

        return respondSuccess(res, opp);
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    const opp = _memOpportunities.find((o) => o.opportunity_id === opp_id && o.tenant_id === tenantId);
    if (!opp) return respondError(res, 404, 'NOT_FOUND', 'Opportunity not found.');
    if (TERMINAL_STAGES.has(opp.stage))
      return respondError(res, 409, 'CONFLICT', 'Opportunity is already closed.', [{ field: 'stage', reason: 'already_terminal' }]);

    const prevStage = opp.stage;
    if (stage)             opp.stage             = stage;
    if (amount != null)    opp.amount            = amount;
    if (probability != null) opp.probability     = probability;
    if (forecast_category) opp.forecast_category = forecast_category;
    opp.version_no += 1;
    opp.updated_at  = nowIso();

    if (stage && stage !== prevStage) {
      emitEvent('opportunity.stage.changed.v1', {
        opportunity_id: opp.opportunity_id,
        tenant_id:      opp.tenant_id,
        from_stage:     prevStage,
        to_stage:       stage,
      });
      if (TERMINAL_STAGES.has(stage)) {
        opp.closed_at    = nowIso();
        opp.close_reason = close_reason || null;
        emitEvent('opportunity.closed.v1', {
          opportunity_id: opp.opportunity_id,
          tenant_id:      opp.tenant_id,
          outcome:        stage,
          close_reason:   opp.close_reason,
        });
      }
    }

    return respondSuccess(res, opp);
  },
);

// ── GET /opportunities/:opp_id/line-items ─────────────────────────────────────
router.get('/:opp_id/line-items', requestValidationMiddleware(), requireScopes([SCOPES.OPPORTUNITIES_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { opp_id } = req.params;

  if (repo) {
    try {
      const items = await repo.listLineItems(tenantId, opp_id);
      return respondSuccess(res, items, { count: items.length });
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  return respondSuccess(res, [], { count: 0 });
});

// ── POST /opportunities/:opp_id/line-items ────────────────────────────────────
router.post(
  '/:opp_id/line-items',
  requestValidationMiddleware(['product_id', 'unit_price']),
  requireScopes([SCOPES.OPPORTUNITIES_UPDATE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { opp_id } = req.params;
    const { product_id, quantity, unit_price, currency, discount_pct } = req.body;

    if (repo) {
      try {
        const item = await repo.addLineItem(tenantId, opp_id, {
          line_item_id: randomUUID(),
          product_id,
          quantity:     quantity     ?? 1,
          unit_price,
          currency:     currency     || 'PKR',
          discount_pct: discount_pct ?? 0,
        });
        return res.status(201).json({ data: item, meta: { request_id: req.request_id } });
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    return respondError(res, 503, 'SERVICE_UNAVAILABLE', 'Line items require DB connection.');
  },
);

module.exports = router;
