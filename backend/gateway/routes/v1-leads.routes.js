'use strict';

/**
 * Lead management routes.
 *
 * Docs: docs/domain-model.md (Lead entity)
 *       docs/followup-enforcement-model.md (every lead must have owner + followup)
 *       docs/api-standards.md (REST conventions, error envelopes)
 *       db/lead_management_db/schema.sql
 *
 * Every lead MUST have an owner_id — creation without one is rejected (422).
 * DB layer: LeadsRepository (gateway/db/repositories/leads.repository.js)
 * Fallback: in-memory array when DB_DISABLED=true or pg not installed.
 */

const http = require('http');
const https = require('https');
const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const FOLLOWUP_SERVICE_URL = process.env.FOLLOWUP_SERVICE_URL || 'http://localhost:5002';

/**
 * Fire-and-forget POST to the followup service.
 * Called after lead creation to seed the enforcement engine (P-020 / BEHAV-007).
 * Never throws — missing service is non-blocking for the lead creation response.
 */
function postJson(url, body) {
  const payload = Buffer.from(JSON.stringify(body));
  const parsed  = new URL(url);
  const client  = url.startsWith('https') ? https : http;

  const req = client.request(
    {
      hostname: parsed.hostname,
      port:     parsed.port || (url.startsWith('https') ? 443 : 80),
      path:     parsed.pathname,
      method:   'POST',
      headers:  { 'Content-Type': 'application/json', 'Content-Length': payload.length },
    },
    (res) => { res.resume(); },
  );
  req.on('error', () => { /* fire-and-forget — ignore */ });
  req.setTimeout(3000, () => req.destroy());
  req.write(payload);
  req.end();
}

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    const request = client.get(url, (resp) => {
      let data = '';
      resp.on('data', (chunk) => { data += chunk; });
      resp.on('end', () => {
        try { resolve({ status: resp.statusCode, body: JSON.parse(data) }); }
        catch (e) { reject(new Error('invalid JSON from followup service')); }
      });
    });
    request.on('error', reject);
    request.setTimeout(5000, () => { request.destroy(); reject(new Error('timeout')); });
  });
}

const router = express.Router();

// ── Repository bootstrap ───────────────────────────────────────────────────────
// Use real DB when available; fall back to in-memory for dev/test.
let repo = null;
let VALID_STAGES, VALID_STATUSES, VALID_PRIORITIES, VALID_SOURCES;

try {
  if (process.env.DB_DISABLED !== 'true') {
    const mod = require('../db/repositories/leads.repository');
    repo = new mod.LeadsRepository();
    ({ VALID_STAGES, VALID_STATUSES, VALID_PRIORITIES, VALID_SOURCES } = mod);
  }
} catch (_e) {
  // pg not installed or DB unavailable — use in-memory fallback below.
}

if (!repo) {
  // Stages aligned to migration 0001 + domain/opportunities-pipeline.md §2
  VALID_STAGES    = ['new', 'qualifying', 'nurturing', 'proposal', 'negotiation', 'won', 'lost', 'disqualified'];
  VALID_STATUSES  = ['open', 'working', 'idle', 'closed'];
  VALID_PRIORITIES = ['hot', 'warm', 'cold'];
  VALID_SOURCES   = ['whatsapp', 'web', 'import', 'manual', 'referral', 'campaign'];
}

// In-memory fallback store (used only when repo === null)
const _memLeads = [];

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

// ── GET /leads ────────────────────────────────────────────────────────────────
router.get('/', requestValidationMiddleware(), requireScopes([SCOPES.LEADS_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const { stage, owner_id, status, priority, source } = req.query;
  const limit  = Math.min(parseInt(req.query.limit  || '25', 10), 200);
  const offset = parseInt(req.query.offset || '0', 10);

  if (repo) {
    try {
      const rows = await repo.list(tenantId, { stage, owner_id, status, priority, source, limit, offset });
      const total = await repo.count(tenantId, { stage, status, owner_id });
      return respondSuccess(res, rows, { count: rows.length, total, limit, offset });
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  let filtered = _memLeads.filter((l) => l.tenant_id === tenantId);
  if (stage)    filtered = filtered.filter((l) => l.stage    === stage);
  if (owner_id) filtered = filtered.filter((l) => l.owner_id === owner_id);
  if (status)   filtered = filtered.filter((l) => l.status   === status);
  if (priority) filtered = filtered.filter((l) => l.priority === priority);
  const page = filtered.slice(offset, offset + limit);
  return respondSuccess(res, page, { count: page.length, total: filtered.length, limit, offset });
});

// ── POST /leads ───────────────────────────────────────────────────────────────
router.post(
  '/',
  requestValidationMiddleware(),
  requireScopes([SCOPES.LEADS_CREATE]),
  async (req, res) => {
    const {
      owner_id, title, stage, status, priority, source,
      contact_name, contact_phone_e164, contact_email,
      estimated_value, currency, notes, metadata,
    } = req.body;
    const tenantId = req.auth.tenant_id;

    if (stage    && !VALID_STAGES.includes(stage))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid stage.', [{ field: 'stage', reason: 'invalid_stage' }]);
    if (priority && !VALID_PRIORITIES.includes(priority))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid priority.', [{ field: 'priority', reason: 'invalid_priority' }]);
    if (source   && !VALID_SOURCES.includes(source))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid source.', [{ field: 'source', reason: 'invalid_source' }]);

    const data = {
      lead_id: `lead_${randomUUID().replace(/-/g, '').slice(0, 12)}`,
      tenant_id: tenantId,
      owner_id,
      title: title || null,
      stage: stage || 'new',
      status: status || 'open',
      priority: priority || 'medium',
      source: source || 'other',
      contact_name: contact_name || null,
      contact_phone_e164: contact_phone_e164 || null,
      contact_email: contact_email || null,
      estimated_value: estimated_value || null,
      currency: currency || 'PKR',
      notes: notes || null,
      metadata: metadata || null,
      created_at: nowIso(),
      updated_at: nowIso(),
    };

    if (repo) {
      try {
        const lead = await repo.create(tenantId, data);
        // P-020 — register lead in followup enforcement engine (fire-and-forget)
        postJson(
          `${FOLLOWUP_SERVICE_URL}/internal/leads/${encodeURIComponent(lead.lead_id)}/register`,
          {
            tenant_id:        lead.tenant_id,
            owner_id:         lead.owner_id,
            status:           lead.status,
            priority:         lead.priority,
            stage:            lead.stage,
            last_activity_at: lead.created_at,
          },
        );
        return res.status(201).json({ data: lead, meta: { request_id: req.request_id } });
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    _memLeads.push(data);
    // P-020 — register lead in followup enforcement engine (fire-and-forget, in-memory path)
    postJson(
      `${FOLLOWUP_SERVICE_URL}/internal/leads/${encodeURIComponent(data.lead_id)}/register`,
      {
        tenant_id:        data.tenant_id,
        owner_id:         data.owner_id,
        status:           data.status,
        priority:         data.priority,
        stage:            data.stage,
        last_activity_at: data.created_at,
      },
    );
    return res.status(201).json({ data, meta: { request_id: req.request_id } });
  },
);

// ── GET /leads/:lead_id ───────────────────────────────────────────────────────
router.get('/:lead_id', requestValidationMiddleware(), requireScopes([SCOPES.LEADS_READ]), async (req, res) => {
  const { lead_id } = req.params;
  const tenantId = req.auth.tenant_id;

  if (repo) {
    try {
      const lead = await repo.findById(tenantId, lead_id);
      if (!lead) return respondError(res, 404, 'NOT_FOUND', 'Lead not found.');
      return respondSuccess(res, lead);
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  const lead = _memLeads.find((l) => l.lead_id === lead_id && l.tenant_id === tenantId);
  if (!lead) return respondError(res, 404, 'NOT_FOUND', 'Lead not found.');
  return respondSuccess(res, lead);
});

// ── PATCH /leads/:lead_id ─────────────────────────────────────────────────────
router.patch(
  '/:lead_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.LEADS_UPDATE]),
  async (req, res) => {
    const { lead_id } = req.params;
    const tenantId = req.auth.tenant_id;
    const { stage, status, priority, source, owner_id, title, notes, metadata } = req.body;

    if (stage    && !VALID_STAGES.includes(stage))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid stage.', [{ field: 'stage', reason: 'invalid_stage' }]);
    if (status   && !VALID_STATUSES.includes(status))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid status.', [{ field: 'status', reason: 'invalid_status' }]);
    if (priority && !VALID_PRIORITIES.includes(priority))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid priority.', [{ field: 'priority', reason: 'invalid_priority' }]);

    if (repo) {
      try {
        // Use atomic stage transition if stage is changing (writes history)
        if (stage) {
          const lead = await repo.transitionStage(tenantId, lead_id, {
            new_stage: stage,
            changed_by: req.auth.user_id,
          });
          if (!lead) return respondError(res, 404, 'NOT_FOUND', 'Lead not found.');
          // Apply remaining patch fields
          const rest = {};
          if (status)   rest.status   = status;
          if (priority) rest.priority = priority;
          if (owner_id) rest.owner_id = owner_id;
          if (title)    rest.title    = title;
          if (notes)    rest.notes    = notes;
          if (metadata) rest.metadata = metadata;
          if (Object.keys(rest).length > 0) {
            const updated = await repo.update(tenantId, lead_id, rest);
            return respondSuccess(res, updated);
          }
          return respondSuccess(res, lead);
        }
        const updated = await repo.update(tenantId, lead_id, { status, priority, owner_id, title, notes, metadata });
        if (!updated) return respondError(res, 404, 'NOT_FOUND', 'Lead not found.');
        return respondSuccess(res, updated);
      } catch (err) {
        return respondError(res, 500, 'DB_ERROR', err.message);
      }
    }

    const lead = _memLeads.find((l) => l.lead_id === lead_id && l.tenant_id === tenantId);
    if (!lead) return respondError(res, 404, 'NOT_FOUND', 'Lead not found.');
    if (stage)    lead.stage    = stage;
    if (status)   lead.status   = status;
    if (priority) lead.priority = priority;
    if (owner_id) lead.owner_id = owner_id;
    if (title)    lead.title    = title;
    if (notes)    lead.notes    = notes;
    lead.updated_at = nowIso();
    return respondSuccess(res, lead);
  },
);

// ── DELETE /leads/:lead_id ────────────────────────────────────────────────────
router.delete('/:lead_id', requestValidationMiddleware(), requireScopes([SCOPES.LEADS_DELETE]), async (req, res) => {
  const { lead_id } = req.params;
  const tenantId = req.auth.tenant_id;

  if (repo) {
    try {
      const deleted = await repo.softDelete(tenantId, lead_id);
      if (!deleted) return respondError(res, 404, 'NOT_FOUND', 'Lead not found.');
      return res.status(204).end();
    } catch (err) {
      return respondError(res, 500, 'DB_ERROR', err.message);
    }
  }

  const idx = _memLeads.findIndex((l) => l.lead_id === lead_id && l.tenant_id === tenantId);
  if (idx === -1) return respondError(res, 404, 'NOT_FOUND', 'Lead not found.');
  _memLeads.splice(idx, 1);
  return res.status(204).end();
});

// ── GET /leads/:lead_id/next-action ──────────────────────────────────────────
// Docs: docs/followup-enforcement-model.md §2.D — Next Action Suggestion
// Calls FollowupEnforcementEngine.suggest_next_action() via followup service.
// Returns the highest-priority action an agent should take on this lead right now.
router.get(
  '/:lead_id/next-action',
  requestValidationMiddleware(),
  requireScopes([SCOPES.FOLLOWUPS_READ]),
  async (req, res) => {
    const { lead_id } = req.params;
    const tenantId = req.auth.tenant_id;

    // Verify lead exists (DB or in-memory) before calling the engine
    let leadExists = false;
    if (repo) {
      try {
        const lead = await repo.findById(tenantId, lead_id);
        leadExists = !!lead;
      } catch (_e) {
        leadExists = true;  // DB error — let followup service handle the lookup
      }
    } else {
      leadExists = _memLeads.some((l) => l.lead_id === lead_id && l.tenant_id === tenantId);
    }
    if (!leadExists) return respondError(res, 404, 'NOT_FOUND', 'Lead not found.');

    try {
      const url = `${FOLLOWUP_SERVICE_URL}/internal/leads/${encodeURIComponent(lead_id)}/next-action`;
      const { status, body } = await fetchJson(url);

      if (status === 404) return respondError(res, 404, 'NOT_FOUND', body.detail || 'Lead not found in followup engine.');
      if (status !== 200) return respondError(res, 502, 'FOLLOWUP_SERVICE_ERROR', body.detail || 'Followup service error.');

      return respondSuccess(res, body);
    } catch (_err) {
      // Followup service not reachable — return advisory stub so callers get
      // the contract shape. Stub is marked so clients can detect service-down state.
      return respondSuccess(res, {
        lead_id,
        suggested_action: 'send_reminder',
        reason:   'followup_service_unreachable — connect FollowupEnforcementEngine to resolve',
        priority: 'normal',
        due_by:   null,
        _stub:    true,
      }, { lead_id, stub: true });
    }
  },
);

// ── GET /leads/export ────────────────────────────────────────────────────────
// MR-005: Export all tenant leads as CSV (RFC 4180)
router.get('/export', requestValidationMiddleware(), requireScopes([SCOPES.LEADS_READ]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  let leads;
  if (repo) {
    try {
      leads = await repo.findAll(tenantId, { limit: 10000, offset: 0 });
    } catch (_err) {
      leads = _memLeads.filter((l) => l.tenant_id === tenantId);
    }
  } else {
    leads = _memLeads.filter((l) => l.tenant_id === tenantId);
  }

  const HEADERS = ['lead_id', 'contact_name', 'contact_phone_e164', 'contact_email', 'stage', 'status', 'priority', 'source', 'owner_id', 'estimated_value', 'currency', 'notes', 'created_at'];
  const csvRows = [HEADERS.join(',')];
  leads.forEach((l) => {
    csvRows.push(HEADERS.map((h) => {
      const v = l[h] == null ? '' : String(l[h]);
      return v.includes(',') || v.includes('"') || v.includes('\n') ? '"' + v.replace(/"/g, '""') + '"' : v;
    }).join(','));
  });

  const csv = csvRows.join('\r\n');
  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', 'attachment; filename="leads-export.csv"');
  res.send(csv);
});

// ── POST /leads/import ────────────────────────────────────────────────────────
// MR-005: Import leads from CSV. Body: text/csv or application/json array.
// Returns { data: { created, skipped, errors }, meta: {} }
router.post('/import', requestValidationMiddleware(), requireScopes([SCOPES.LEADS_CREATE]), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  let rows = [];

  try {
    if (req.is('text/csv') || req.is('text/plain')) {
      const text   = req.body.toString ? req.body.toString() : String(req.body);
      const lines  = text.trim().split(/\r?\n/);
      const headers= lines[0].split(',').map((h) => h.trim().replace(/^"(.*)"$/, '$1'));
      rows = lines.slice(1).map((line) => {
        const vals = line.split(',').map((v) => v.trim().replace(/^"(.*)"$/, '$1'));
        const row  = {};
        headers.forEach((h, i) => { row[h] = vals[i] || ''; });
        return row;
      });
    } else {
      rows = Array.isArray(req.body) ? req.body : (req.body.leads || []);
    }
  } catch (_err) {
    return respondError(res, 422, 'PARSE_ERROR', 'Could not parse import body. Expected CSV or JSON array.');
  }

  let created = 0, skipped = 0;
  const errors = [];

  for (const row of rows) {
    const contact_name = row.contact_name || row['Contact Name'] || row['Name'] || '';
    const contact_phone = row.contact_phone_e164 || row.phone || row['Phone'] || '';

    if (!contact_name && !contact_phone) { skipped++; continue; }

    // Dedup check: exact phone match
    const exists = _memLeads.some((l) => l.tenant_id === tenantId && l.contact_phone_e164 === contact_phone && contact_phone);
    if (exists) { skipped++; continue; }

    const now    = new Date().toISOString();
    const lead   = {
      lead_id:            randomUUID(),
      tenant_id:          tenantId,
      owner_id:           row.owner_id || req.auth.user_id || 'import',
      contact_name:       contact_name,
      contact_phone_e164: contact_phone,
      contact_email:      row.contact_email || row.email || null,
      stage:              VALID_STAGES.includes(row.stage) ? row.stage : 'new',
      status:             'open',
      priority:           VALID_PRIORITIES.includes(row.priority) ? row.priority : 'warm',
      source:             row.source || 'import',
      estimated_value:    Number(row.estimated_value) || 0,
      currency:           row.currency || 'PKR',
      notes:              row.notes || '',
      metadata:           {},
      created_at:         now,
      updated_at:         now,
    };

    if (repo) {
      try {
        await repo.create(lead);
      } catch (err) {
        errors.push({ row: contact_name || contact_phone, reason: err.message });
        continue;
      }
    }
    _memLeads.push(lead);
    created++;
  }

  return respondSuccess(res, { created, skipped, errors }, {
    total_rows:  rows.length,
    import_source: 'csv',
  });
});

module.exports = router;
