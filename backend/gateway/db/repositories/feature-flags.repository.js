'use strict';

/**
 * Feature flag evaluation repository — DB-backed flag + rule lookup with
 * in-memory fallback for dev/test.
 *
 * Docs: db/feature_flag_db/schema.sql
 *       services/feature_flags/evaluator.py (Python twin)
 *
 * Schema: feature_flag_db
 * Tables: feature_flags, flag_rules, flag_evaluations
 *
 * Evaluation contract:
 *   - Safe-by-default: unknown flags → false.
 *   - Rules evaluated in ascending priority order; first match wins.
 *   - Rule types: always_off, always_on, tenant, role, percentage.
 *   - Deterministic: same flag_key + tenant_id → same percentage bucket.
 *
 * Usage::
 *   const { FeatureFlagsRepository } = require('./feature-flags.repository');
 *   const flagRepo = new FeatureFlagsRepository();
 *   const on = await flagRepo.evaluate('whatsapp_360dialog', tenantId, { role: 'agent' });
 */

const crypto = require('crypto');
const { query } = require('../pool');

class FeatureFlagsRepository {
  // ── Evaluate ──────────────────────────────────────────────────────────────

  /**
   * Evaluate flag_key for the given tenant + context.
   * Returns boolean (true = enabled).  Never throws — returns false on error.
   *
   * @param {string} flagKey
   * @param {string|null} tenantId
   * @param {{ role?: string, userId?: string }} [context={}]
   */
  async evaluate(flagKey, tenantId, context = {}) {
    try {
      // 1. Load flag record
      const { rows: flags } = await query(
        `SELECT flag_id, default_value, status
         FROM feature_flag_db.feature_flags
         WHERE key = $1`,
        [flagKey],
      );
      if (!flags[0] || flags[0].status === 'archived') return false;

      const { flag_id, default_value } = flags[0];

      // 2. Load rules ordered by priority (ascending)
      const { rows: rules } = await query(
        `SELECT rule_type, condition_json, value, priority
         FROM feature_flag_db.flag_rules
         WHERE flag_id = $1
         ORDER BY priority ASC`,
        [flag_id],
      );

      // 3. Evaluate rules — first match wins
      for (const rule of rules) {
        const { matched, value } = this._applyRule(rule, flagKey, tenantId, context);
        if (matched) {
          // Log edge-case evaluations (non-default results only)
          this._logEvaluation(flag_id, tenantId, context.userId, value, rule.rule_type).catch(() => {});
          return value;
        }
      }

      // 4. No rule matched — return default (safe = false)
      return default_value;
    } catch (_err) {
      // DB unavailable or flag not found — safe default
      return false;
    }
  }

  /**
   * Batch-evaluate multiple flags for the same context.
   * Returns Map<flagKey, boolean>.
   */
  async evaluateMany(flagKeys, tenantId, context = {}) {
    const results = new Map();
    await Promise.all(
      flagKeys.map(async (key) => {
        results.set(key, await this.evaluate(key, tenantId, context));
      }),
    );
    return results;
  }

  // ── Flag management ───────────────────────────────────────────────────────

  async getFlag(flagKey) {
    const { rows } = await query(
      `SELECT * FROM feature_flag_db.feature_flags WHERE key = $1`,
      [flagKey],
    );
    return rows[0] || null;
  }

  async listFlags({ status } = {}) {
    const conditions = [];
    const params = [];
    if (status) { conditions.push(`status = $${params.length + 1}`); params.push(status); }

    const { rows } = await query(
      `SELECT * FROM feature_flag_db.feature_flags
       ${conditions.length ? `WHERE ${conditions.join(' AND ')}` : ''}
       ORDER BY key ASC`,
      params,
    );
    return rows;
  }

  async listRulesForFlag(flagKey) {
    const { rows } = await query(
      `SELECT r.*
       FROM feature_flag_db.flag_rules r
       JOIN feature_flag_db.feature_flags f ON f.flag_id = r.flag_id
       WHERE f.key = $1
       ORDER BY r.priority ASC`,
      [flagKey],
    );
    return rows;
  }

  // ── Rule application ──────────────────────────────────────────────────────

  _applyRule(rule, flagKey, tenantId, context) {
    const cond = rule.condition_json || {};

    switch (rule.rule_type) {
      case 'always_off':
        return { matched: true, value: false };

      case 'always_on':
        return { matched: true, value: true };

      case 'tenant': {
        const matched = cond.tenant_id && tenantId === cond.tenant_id;
        return { matched: !!matched, value: matched ? rule.value : false };
      }

      case 'role': {
        const matched = cond.role && context.role === cond.role;
        return { matched: !!matched, value: matched ? rule.value : false };
      }

      case 'percentage': {
        const pct = Number(cond.percentage || 0);
        if (pct <= 0)  return { matched: false, value: false };
        if (pct >= 100) return { matched: true,  value: rule.value };
        // Deterministic hash — same key+tenant always lands in same bucket
        const seed   = `${flagKey}:${tenantId || ''}`;
        const digest = crypto.createHash('sha256').update(seed).digest('hex');
        const bucket = parseInt(digest.slice(0, 8), 16) % 100;
        return { matched: bucket < pct, value: rule.value };
      }

      default:
        return { matched: false, value: false };
    }
  }

  async _logEvaluation(flagId, tenantId, userId, evaluatedValue, ruleMatched) {
    await query(
      `INSERT INTO feature_flag_db.flag_evaluations
         (flag_id, tenant_id, user_id, evaluated_value, rule_matched)
       VALUES ($1, $2, $3, $4, $5)`,
      [flagId, tenantId || null, userId || null, evaluatedValue, ruleMatched],
    );
  }
}

// ── In-memory fallback evaluator (used when DB unavailable) ──────────────────
// Populated via registerFallback() for dev/test environments.

const _fallbackFlags = new Map();  // flagKey → { default_value, rules }

function registerFallback(flagKey, defaultValue = false, rules = []) {
  _fallbackFlags.set(flagKey, {
    default_value: defaultValue,
    rules:         rules.sort((a, b) => (a.priority || 0) - (b.priority || 0)),
  });
}

function evaluateFallback(flagKey, tenantId, context = {}) {
  const flag = _fallbackFlags.get(flagKey);
  if (!flag) return false;

  const repo = new FeatureFlagsRepository();
  for (const rule of flag.rules) {
    const { matched, value } = repo._applyRule(rule, flagKey, tenantId, context);
    if (matched) return value;
  }
  return flag.default_value;
}

module.exports = { FeatureFlagsRepository, registerFallback, evaluateFallback };
