'use strict';

/**
 * Leads repository — DB-backed CRUD for lead_management.leads.
 *
 * Docs: docs/domain-model.md — Lead entity
 *       db/lead_management_db/schema.sql — table definition
 *
 * Schema: lead_management_db (PostgreSQL schema: lead_management)
 * Table:  lead_management.leads
 *
 * This is the authoritative pattern for repository objects in this codebase.
 * All other domain repositories (opportunities, contacts, etc.) follow the
 * same structure:
 *   - All queries are tenant-scoped (WHERE tenant_id = $n)
 *   - Use parameterised queries ($1, $2 …) — never string interpolation
 *   - Timestamps are ISO-8601 strings in UTC
 *   - Soft-delete via deleted_at; hard delete not exposed
 *
 * Usage:
 *   const LeadsRepository = require('../db/repositories/leads.repository');
 *   const repo = new LeadsRepository();                    // uses shared pool
 *
 *   const lead = await repo.create(tenantId, data);
 *   const lead = await repo.findById(tenantId, leadId);
 *   const leads = await repo.list(tenantId, { stage, limit, offset });
 *   const lead = await repo.update(tenantId, leadId, patch);
 *   await repo.softDelete(tenantId, leadId);
 */

const { query, withTransaction } = require('../pool');

const VALID_STAGES = ['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];
const VALID_STATUSES = ['open', 'contacted', 'working', 'closed'];
const VALID_PRIORITIES = ['low', 'medium', 'high', 'urgent'];
const VALID_SOURCES = ['web', 'whatsapp', 'referral', 'cold_call', 'event', 'import', 'other'];

class LeadsRepository {
  // ── Create ──────────────────────────────────────────────────────────────────

  async create(tenantId, data) {
    const {
      lead_id,
      owner_id,
      title,
      stage = 'new',
      status = 'open',
      priority = 'medium',
      source = 'other',
      contact_name,
      contact_phone_e164,
      contact_email,
      estimated_value,
      currency = 'PKR',
      notes,
      metadata,
    } = data;

    const { rows } = await query(
      `INSERT INTO lead_management.leads (
         lead_id, tenant_id, owner_id, title, stage, status, priority, source,
         contact_name, contact_phone_e164, contact_email,
         estimated_value, currency, notes, metadata
       ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
       RETURNING *`,
      [
        lead_id, tenantId, owner_id, title, stage, status, priority, source,
        contact_name || null, contact_phone_e164 || null, contact_email || null,
        estimated_value || null, currency, notes || null,
        metadata ? JSON.stringify(metadata) : null,
      ],
    );
    return rows[0];
  }

  // ── Read ────────────────────────────────────────────────────────────────────

  async findById(tenantId, leadId) {
    const { rows } = await query(
      `SELECT * FROM lead_management.leads
       WHERE tenant_id = $1 AND lead_id = $2 AND deleted_at IS NULL`,
      [tenantId, leadId],
    );
    return rows[0] || null;
  }

  async list(tenantId, { stage, status, owner_id, priority, source, limit = 25, offset = 0 } = {}) {
    const conditions = ['tenant_id = $1', 'deleted_at IS NULL'];
    const params = [tenantId];
    let p = 2;

    if (stage)    { conditions.push(`stage = $${p++}`);    params.push(stage); }
    if (status)   { conditions.push(`status = $${p++}`);   params.push(status); }
    if (owner_id) { conditions.push(`owner_id = $${p++}`); params.push(owner_id); }
    if (priority) { conditions.push(`priority = $${p++}`); params.push(priority); }
    if (source)   { conditions.push(`source = $${p++}`);   params.push(source); }

    params.push(limit, offset);
    const { rows } = await query(
      `SELECT * FROM lead_management.leads
       WHERE ${conditions.join(' AND ')}
       ORDER BY created_at DESC
       LIMIT $${p} OFFSET $${p + 1}`,
      params,
    );
    return rows;
  }

  async count(tenantId, filters = {}) {
    const conditions = ['tenant_id = $1', 'deleted_at IS NULL'];
    const params = [tenantId];
    let p = 2;
    const { stage, status, owner_id } = filters;
    if (stage)    { conditions.push(`stage = $${p++}`);    params.push(stage); }
    if (status)   { conditions.push(`status = $${p++}`);   params.push(status); }
    if (owner_id) { conditions.push(`owner_id = $${p++}`); params.push(owner_id); }

    const { rows } = await query(
      `SELECT COUNT(*)::int AS total FROM lead_management.leads WHERE ${conditions.join(' AND ')}`,
      params,
    );
    return rows[0].total;
  }

  // ── Update ──────────────────────────────────────────────────────────────────

  async update(tenantId, leadId, patch) {
    const allowed = [
      'title', 'stage', 'status', 'priority', 'source',
      'owner_id', 'contact_name', 'contact_phone_e164', 'contact_email',
      'estimated_value', 'currency', 'notes', 'metadata',
    ];
    const fields = Object.keys(patch).filter((k) => allowed.includes(k));
    if (fields.length === 0) throw new Error('no valid fields to update');

    const sets = fields.map((f, i) => `${f} = $${i + 3}`).join(', ');
    const values = fields.map((f) => (f === 'metadata' && patch[f] != null ? JSON.stringify(patch[f]) : patch[f]));

    const { rows } = await query(
      `UPDATE lead_management.leads SET ${sets}
       WHERE tenant_id = $1 AND lead_id = $2 AND deleted_at IS NULL
       RETURNING *`,
      [tenantId, leadId, ...values],
    );
    return rows[0] || null;
  }

  // ── Soft delete ─────────────────────────────────────────────────────────────

  async softDelete(tenantId, leadId) {
    const { rows } = await query(
      `UPDATE lead_management.leads SET deleted_at = NOW()
       WHERE tenant_id = $1 AND lead_id = $2 AND deleted_at IS NULL
       RETURNING lead_id`,
      [tenantId, leadId],
    );
    return rows.length > 0;
  }

  // ── History (immutable change log) ──────────────────────────────────────────

  async appendHistory(client, { lead_id, tenant_id, changed_by, field_name, old_value, new_value }) {
    // Uses a passed-in transaction client to participate in the caller's UoW.
    await client.query(
      `INSERT INTO lead_management.lead_history
         (tenant_id, lead_id, changed_by, field_name, old_value, new_value)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [tenant_id, lead_id, changed_by, field_name,
       old_value != null ? String(old_value) : null,
       new_value != null ? String(new_value) : null],
    );
  }

  // ── Atomic stage transition with history ─────────────────────────────────────

  async transitionStage(tenantId, leadId, { new_stage, changed_by }) {
    return withTransaction(async (client) => {
      const { rows: current } = await client.query(
        `SELECT lead_id, stage FROM lead_management.leads
         WHERE tenant_id = $1 AND lead_id = $2 AND deleted_at IS NULL FOR UPDATE`,
        [tenantId, leadId],
      );
      if (!current[0]) return null;

      const old_stage = current[0].stage;
      const { rows: updated } = await client.query(
        `UPDATE lead_management.leads SET stage = $3
         WHERE tenant_id = $1 AND lead_id = $2
         RETURNING *`,
        [tenantId, leadId, new_stage],
      );

      await this.appendHistory(client, {
        lead_id: leadId, tenant_id: tenantId,
        changed_by, field_name: 'stage',
        old_value: old_stage, new_value: new_stage,
      });

      return updated[0];
    });
  }
}

module.exports = { LeadsRepository, VALID_STAGES, VALID_STATUSES, VALID_PRIORITIES, VALID_SOURCES };
