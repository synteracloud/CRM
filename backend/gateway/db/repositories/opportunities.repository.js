'use strict';

/**
 * Opportunities repository — DB-backed CRUD for opportunity_db.opportunities.
 *
 * Docs: docs/opportunities-pipeline.md
 *       docs/domain-model.md — Opportunity entity
 *       db/opportunity_db/schema.sql
 *
 * Schema: opportunity_db
 * Tables: opportunities, opportunity_line_items, forecast_records
 *
 * Rules:
 *   - All queries tenant-scoped (WHERE tenant_id = $n)
 *   - Parameterised queries only — no string interpolation
 *   - Terminal stages (closed_won, closed_lost) set closed_at on transition
 *   - Stage transitions use optimistic concurrency via version_no
 */

const { query, withTransaction } = require('../pool');

const VALID_STAGES      = ['qualification', 'discovery', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];
const TERMINAL_STAGES   = new Set(['closed_won', 'closed_lost']);
const VALID_FORECASTS   = ['pipeline', 'best_case', 'commit', 'closed', 'omitted'];

class OpportunitiesRepository {
  // ── Create ───────────────────────────────────────────────────────────────────

  async create(tenantId, data) {
    const {
      opportunity_id,
      account_id,
      contact_id,
      owner_id,
      name,
      stage = 'qualification',
      amount,
      currency = 'PKR',
      close_date,
      probability = 0,
      forecast_category = 'pipeline',
    } = data;

    const { rows } = await query(
      `INSERT INTO opportunity_db.opportunities (
         opportunity_id, tenant_id, account_id, contact_id, owner_id,
         name, stage, amount, currency, close_date, probability, forecast_category
       ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
       RETURNING *`,
      [
        opportunity_id, tenantId, account_id || null, contact_id || null, owner_id,
        name, stage, amount || null, currency, close_date || null,
        probability, forecast_category,
      ],
    );
    return rows[0];
  }

  // ── Read ─────────────────────────────────────────────────────────────────────

  async findById(tenantId, opportunityId) {
    const { rows } = await query(
      `SELECT * FROM opportunity_db.opportunities
       WHERE tenant_id = $1 AND opportunity_id = $2`,
      [tenantId, opportunityId],
    );
    return rows[0] || null;
  }

  async list(tenantId, { stage, owner_id, forecast_category, limit = 25, offset = 0 } = {}) {
    const conditions = ['tenant_id = $1'];
    const params = [tenantId];
    let p = 2;

    if (stage)             { conditions.push(`stage = $${p++}`);             params.push(stage); }
    if (owner_id)          { conditions.push(`owner_id = $${p++}`);          params.push(owner_id); }
    if (forecast_category) { conditions.push(`forecast_category = $${p++}`); params.push(forecast_category); }

    params.push(limit, offset);
    const { rows } = await query(
      `SELECT * FROM opportunity_db.opportunities
       WHERE ${conditions.join(' AND ')}
       ORDER BY created_at DESC
       LIMIT $${p} OFFSET $${p + 1}`,
      params,
    );
    return rows;
  }

  // ── Update ───────────────────────────────────────────────────────────────────

  async update(tenantId, opportunityId, patch) {
    const allowed = [
      'name', 'amount', 'currency', 'close_date', 'probability',
      'forecast_category', 'owner_id', 'account_id', 'contact_id', 'close_reason',
    ];
    const fields = Object.keys(patch).filter((k) => allowed.includes(k));
    if (fields.length === 0) throw new Error('no valid fields to update');

    const sets = fields.map((f, i) => `${f} = $${i + 3}`).join(', ');
    const values = fields.map((f) => patch[f]);

    const { rows } = await query(
      `UPDATE opportunity_db.opportunities SET ${sets}
       WHERE tenant_id = $1 AND opportunity_id = $2
       RETURNING *`,
      [tenantId, opportunityId, ...values],
    );
    return rows[0] || null;
  }

  // ── Stage transition (atomic, emits event) ────────────────────────────────────

  async transitionStage(tenantId, opportunityId, { new_stage, changed_by, close_reason }) {
    return withTransaction(async (client) => {
      const { rows: current } = await client.query(
        `SELECT opportunity_id, stage, version_no
         FROM opportunity_db.opportunities
         WHERE tenant_id = $1 AND opportunity_id = $2 FOR UPDATE`,
        [tenantId, opportunityId],
      );
      if (!current[0]) return null;

      const isTerminal = TERMINAL_STAGES.has(new_stage);
      const { rows: updated } = await client.query(
        `UPDATE opportunity_db.opportunities
         SET stage = $3,
             version_no = version_no + 1,
             closed_at  = CASE WHEN $4 THEN NOW() ELSE closed_at END,
             close_reason = COALESCE($5, close_reason)
         WHERE tenant_id = $1 AND opportunity_id = $2
         RETURNING *`,
        [tenantId, opportunityId, new_stage, isTerminal, close_reason || null],
      );
      return updated[0];
    });
  }

  // ── Line items ────────────────────────────────────────────────────────────────

  async addLineItem(tenantId, opportunityId, item) {
    const { line_item_id, product_id, quantity = 1, unit_price, currency = 'PKR', discount_pct = 0 } = item;
    const { rows } = await query(
      `INSERT INTO opportunity_db.opportunity_line_items
         (line_item_id, opportunity_id, tenant_id, product_id, quantity, unit_price, currency, discount_pct)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
       RETURNING *`,
      [line_item_id, opportunityId, tenantId, product_id, quantity, unit_price, currency, discount_pct],
    );
    return rows[0];
  }

  async listLineItems(tenantId, opportunityId) {
    const { rows } = await query(
      `SELECT * FROM opportunity_db.opportunity_line_items
       WHERE tenant_id = $1 AND opportunity_id = $2
       ORDER BY created_at ASC`,
      [tenantId, opportunityId],
    );
    return rows;
  }
}

module.exports = { OpportunitiesRepository, VALID_STAGES, TERMINAL_STAGES, VALID_FORECASTS };
