'use strict';

/**
 * Offline sync batch routes.
 *
 * Docs: docs/offline-sync.md §6.2 (sync sequence)
 *       docs/integration-end-to-end-auto-fix.md — Flow 4
 *
 * POST /sync/batch  — device sends array of CommandRecords; server applies them.
 * GET  /sync/status — device polls queue status (pending, conflict, dead_letter counts).
 *
 * Each command is deduplicated by idempotency_key before processing.
 * DB layer: ConversationsRepository.enqueueSyncCommand / updateSyncCommandStatus
 * Fallback: in-memory Map when DB_DISABLED=true or pg not installed.
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
let VALID_SYNC_OPS, VALID_SYNC_STATUSES;

try {
  if (process.env.DB_DISABLED !== 'true') {
    const mod = require('../db/repositories/conversations.repository');
    repo = new mod.ConversationsRepository();
    ({ VALID_SYNC_OPS, VALID_SYNC_STATUSES } = mod);
  }
} catch (_e) {
  // pg not installed or DB unavailable — use in-memory fallback below.
}

if (!repo) {
  VALID_SYNC_OPS     = ['create', 'update', 'delete'];
  VALID_SYNC_STATUSES = ['pending', 'syncing', 'synced', 'failed', 'conflict', 'dead_letter'];
}

// In-memory fallback store (used only when repo === null)
const _processedKeys = new Map();  // `${tenantId}:${idempotency_key}` → result
const _syncLog = [];

function nowIso() { return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'); }

// ── POST /sync/batch ──────────────────────────────────────────────────────────
router.post(
  '/batch',
  requestValidationMiddleware(['commands']),
  requireScopes([SCOPES.SYNC_WRITE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { commands } = req.body;

    if (!Array.isArray(commands) || commands.length === 0)
      return respondError(res, 422, 'VALIDATION_ERROR', 'commands must be a non-empty array.');

    if (commands.length > 100)
      return respondError(res, 422, 'VALIDATION_ERROR', 'Batch exceeds 100 command limit.');

    const results = [];

    for (const cmd of commands) {
      const { idempotency_key, device_id, entity_type, entity_id, op, payload, base_version, client_timestamp } = cmd;

      if (!idempotency_key || !entity_type || !entity_id || !op) {
        results.push({ idempotency_key: idempotency_key || null, status: 'rejected', reason: 'missing_required_fields' });
        continue;
      }

      if (!VALID_SYNC_OPS.includes(op)) {
        results.push({ idempotency_key, status: 'rejected', reason: `invalid_op: ${op}` });
        continue;
      }

      if (repo) {
        try {
          // Enqueue with DB-level idempotency (UNIQUE tenant_id, idempotency_key)
          const record = await repo.enqueueSyncCommand(tenantId, {
            command_id:      randomUUID(),
            device_id:       device_id || 'unknown',
            idempotency_key,
            entity_type,
            entity_id,
            op,
            payload:         payload         || {},
            base_version:    base_version    || 0,
            client_timestamp: client_timestamp || nowIso(),
          });

          if (!record) {
            // Duplicate — idempotency key already exists
            results.push({ idempotency_key, status: 'duplicate' });
            continue;
          }

          // Mark as synced immediately (dispatch to SyncService is a future P-009 concern)
          await repo.updateSyncCommandStatus(tenantId, record.command_id, {
            status:    'synced',
            synced_at: nowIso(),
          });

          const result = {
            idempotency_key,
            status:         'synced',
            command_id:     record.command_id,
            entity_type,
            entity_id,
            server_version: (base_version || 0) + 1,
            synced_at:      nowIso(),
          };
          results.push(result);
        } catch (err) {
          results.push({ idempotency_key, status: 'failed', reason: err.message });
        }
        continue;
      }

      // In-memory fallback
      const scopedKey = `${tenantId}:${idempotency_key}`;
      if (_processedKeys.has(scopedKey)) {
        results.push({ idempotency_key, status: 'duplicate', cached_result: _processedKeys.get(scopedKey) });
        continue;
      }

      const result = {
        idempotency_key,
        status:         'synced',
        entity_type,
        entity_id,
        server_version: (base_version || 0) + 1,
        synced_at:      nowIso(),
      };
      _processedKeys.set(scopedKey, result);
      _syncLog.push({ tenant_id: tenantId, ...cmd, ...result });
      results.push(result);
    }

    return respondSuccess(res, { results, count: results.length });
  },
);

// ── GET /sync/status ──────────────────────────────────────────────────────────
router.get('/status', requestValidationMiddleware(), requireScopes([SCOPES.SYNC_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { device_id } = req.query;

  if (repo) {
    try {
      const pending = await repo.listPendingSyncCommands(tenantId, { device_id, limit: 200 });
      const counts = {};
      for (const cmd of pending) {
        counts[cmd.status] = (counts[cmd.status] || 0) + 1;
      }
      return respondSuccess(res, { tenant_id: tenantId, counts, checked_at: nowIso() });
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  const tenantLog = _syncLog.filter((e) => e.tenant_id === tenantId);
  const counts = tenantLog.reduce((acc, e) => {
    acc[e.status] = (acc[e.status] || 0) + 1;
    return acc;
  }, {});
  return respondSuccess(res, { tenant_id: tenantId, counts, last_sync_at: tenantLog.at(-1)?.synced_at || null });
});

module.exports = router;
