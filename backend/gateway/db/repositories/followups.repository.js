'use strict';

/**
 * Followups repository — DB-backed CRUD for followup_tasks and escalations.
 *
 * Docs: docs/followup-enforcement-model.md
 *       db/activity_task_db/followup_enforcement_schema.sql
 *
 * Schema: public (followup_enforcement_schema.sql uses no explicit schema prefix)
 * Tables: followup_tasks, followup_escalations, followup_violations, followup_enforcement_audit
 *
 * Invariants enforced by DB:
 *   - Only one canonical pending task per lead (ux_followup_tasks_one_canonical_pending)
 *   - state ∈ (pending, overdue, completed)
 *   - escalation_level ∈ (none, reminder, warning, escalated, reassigned)
 */

const { query, withTransaction } = require('../pool');

const VALID_STATES           = ['pending', 'overdue', 'completed'];
const VALID_ESCALATION_LEVELS = ['none', 'reminder', 'warning', 'escalated', 'reassigned'];
const VALID_RULE_TYPES       = ['TimeBased', 'ActivityBased', 'InactivityBased'];
const VALID_GENERATED_BY     = ['Scheduler', 'EscalationEngine', 'SystemRepair'];

class FollowupsRepository {
  // ── Tasks ────────────────────────────────────────────────────────────────────

  async createTask(tenantId, data) {
    const {
      task_id,
      lead_id,
      owner_id,
      state = 'pending',
      due_at,
      rule_type,
      escalation_level = 'none',
      generated_by,
      is_canonical = true,
    } = data;

    const { rows } = await query(
      `INSERT INTO followup_tasks
         (task_id, tenant_id, lead_id, owner_id, state, due_at,
          rule_type, escalation_level, generated_by, is_canonical)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
       RETURNING *`,
      [task_id, tenantId, lead_id, owner_id, state, due_at,
       rule_type, escalation_level, generated_by, is_canonical],
    );
    return rows[0];
  }

  async findTaskById(tenantId, taskId) {
    const { rows } = await query(
      `SELECT * FROM followup_tasks WHERE tenant_id = $1 AND task_id = $2`,
      [tenantId, taskId],
    );
    return rows[0] || null;
  }

  async listTasks(tenantId, { lead_id, owner_id, state, limit = 25, offset = 0 } = {}) {
    const conditions = ['tenant_id = $1'];
    const params = [tenantId];
    let p = 2;

    if (lead_id)  { conditions.push(`lead_id = $${p++}`);  params.push(lead_id); }
    if (owner_id) { conditions.push(`owner_id = $${p++}`); params.push(owner_id); }
    if (state)    { conditions.push(`state = $${p++}`);    params.push(state); }

    params.push(limit, offset);
    const { rows } = await query(
      `SELECT * FROM followup_tasks
       WHERE ${conditions.join(' AND ')}
       ORDER BY due_at ASC
       LIMIT $${p} OFFSET $${p + 1}`,
      params,
    );
    return rows;
  }

  // Canonical pending task for a lead (enforced unique by DB index)
  async getCanonicalPendingTask(tenantId, leadId) {
    const { rows } = await query(
      `SELECT * FROM followup_tasks
       WHERE tenant_id = $1 AND lead_id = $2 AND state = 'pending' AND is_canonical = TRUE`,
      [tenantId, leadId],
    );
    return rows[0] || null;
  }

  // Atomic complete — marks task completed, records activity link
  async completeTask(tenantId, taskId, { completed_activity_id } = {}) {
    return withTransaction(async (client) => {
      const { rows } = await client.query(
        `UPDATE followup_tasks
         SET state = 'completed', completed_at = NOW(), completed_activity_id = $3
         WHERE tenant_id = $1 AND task_id = $2 AND state != 'completed'
         RETURNING *`,
        [tenantId, taskId, completed_activity_id || null],
      );
      return rows[0] || null;
    });
  }

  // Snooze — updates due_at; state stays pending
  async snoozeTask(tenantId, taskId, { snoozed_until }) {
    const { rows } = await query(
      `UPDATE followup_tasks SET due_at = $3
       WHERE tenant_id = $1 AND task_id = $2 AND state = 'pending'
       RETURNING *`,
      [tenantId, taskId, snoozed_until],
    );
    return rows[0] || null;
  }

  // Bulk mark overdue — called by scheduler sweep
  async markOverdueBefore(tenantId, cutoffIso) {
    const { rows } = await query(
      `UPDATE followup_tasks SET state = 'overdue'
       WHERE tenant_id = $1 AND state = 'pending' AND due_at < $2
       RETURNING task_id, lead_id, owner_id`,
      [tenantId, cutoffIso],
    );
    return rows;
  }

  // ── Escalations ───────────────────────────────────────────────────────────────

  async createEscalation(tenantId, data) {
    const { escalation_id, lead_id, task_id, escalation_level, owner_id, reason } = data;
    const { rows } = await query(
      `INSERT INTO followup_escalations
         (escalation_id, tenant_id, lead_id, task_id, escalation_level, owner_id, reason)
       VALUES ($1,$2,$3,$4,$5,$6,$7)
       RETURNING *`,
      [escalation_id, tenantId, lead_id, task_id, escalation_level, owner_id, reason],
    );
    return rows[0];
  }

  async listEscalations(tenantId, leadId) {
    const { rows } = await query(
      `SELECT * FROM followup_escalations
       WHERE tenant_id = $1 AND lead_id = $2
       ORDER BY generated_at DESC`,
      [tenantId, leadId],
    );
    return rows;
  }

  // ── Audit ─────────────────────────────────────────────────────────────────────

  async appendAudit(tenantId, { audit_id, lead_id, task_id, actor_type, action, reason }) {
    await query(
      `INSERT INTO followup_enforcement_audit
         (audit_id, tenant_id, lead_id, task_id, actor_type, action, reason)
       VALUES ($1,$2,$3,$4,$5,$6,$7)`,
      [audit_id, tenantId, lead_id, task_id || null, actor_type, action, reason],
    );
  }
}

module.exports = {
  FollowupsRepository,
  VALID_STATES,
  VALID_ESCALATION_LEVELS,
  VALID_RULE_TYPES,
  VALID_GENERATED_BY,
};
