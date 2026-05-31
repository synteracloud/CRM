'use strict';

/**
 * Contacts gateway routes.
 * Inline fallback: when GATEWAY_UPSTREAM_BASE_URL is not configured (dev mode),
 * serves from in-memory store instead of proxying to downstream contacts service.
 * MR-005: POST /import and GET /export are always inline (never proxied).
 */

const express = require('express');
const { randomUUID } = require('crypto');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { forwardRequest } = require('../middleware/transport-forward');

// Whether to use the downstream proxy or the inline in-memory store.
// True when GATEWAY_UPSTREAM_BASE_URL is set in the environment.
const PROXY_ENABLED = !!process.env.GATEWAY_UPSTREAM_BASE_URL;

// In-memory store: used when proxy is unavailable (dev mode).
// Seeded with 4 sample Pakistan contacts.
const _memContacts = [
  { contact_id:'ct-001', display_name:'Tariq Mehmood', phone_e164:'+923001234567', email:'tariq@citygroup.pk',  account_id:'a-001', account_name:'City Pharma Ltd',      tags:['Customer','Hot'],  open_cases:0, idle:0, completeness_score:90, source:'whatsapp', last_touchpoint:'2026-05-20', created_at:'2026-01-10T08:00:00Z' },
  { contact_id:'ct-002', display_name:'Sana Sheikh',   phone_e164:'+923119876543', email:'sana@nextech.pk',     account_id:'a-002', account_name:'NexTech Solutions',     tags:['Lead','Warm'],     open_cases:1, idle:0, completeness_score:75, source:'web',      last_touchpoint:'2026-05-22', created_at:'2026-02-01T09:00:00Z' },
  { contact_id:'ct-003', display_name:'Bilal Malik',   phone_e164:'+923451122334', email:'bilal@paksteel.pk',   account_id:'a-003', account_name:'Pak Steel HR Module',  tags:['Customer','VIP'],  open_cases:0, idle:1, completeness_score:85, source:'manual',   last_touchpoint:'2026-05-10', created_at:'2026-02-15T10:00:00Z' },
  { contact_id:'ct-004', display_name:'Fatima Zahra',  phone_e164:'+923336677889', email:'fatima@alkhidmat.pk', account_id:'a-004', account_name:'Al-Khidmat Foundation', tags:['Lead','Cold'],     open_cases:0, idle:1, completeness_score:60, source:'import',   last_touchpoint:'2026-04-30', created_at:'2026-03-01T11:00:00Z' },
];

const router = express.Router();

// ── GET /contacts/export ──────────────────────────────────────────────────────
// MR-005: Export tenant contacts as CSV. Always inline.
router.get('/export', requestValidationMiddleware(), requireScopes(['contacts.read']), (req, res) => {
  const HEADERS = ['contact_id', 'display_name', 'phone_e164', 'email', 'account_name', 'tags', 'open_cases', 'completeness_score', 'source', 'last_touchpoint', 'created_at'];
  const csvRows = [HEADERS.join(',')];
  _memContacts.forEach((c) => {
    csvRows.push(HEADERS.map((h) => {
      const v = h === 'tags' ? (Array.isArray(c[h]) ? c[h].join(';') : '') : (c[h] == null ? '' : String(c[h]));
      return v.includes(',') || v.includes('"') ? '"' + v.replace(/"/g, '""') + '"' : v;
    }).join(','));
  });
  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', 'attachment; filename="contacts-export.csv"');
  res.send(csvRows.join('\r\n'));
});

// ── POST /contacts/import ─────────────────────────────────────────────────────
// MR-005: Import contacts from CSV or JSON array. Always inline.
router.post('/import', requestValidationMiddleware(), requireScopes(['contacts.create']), (req, res) => {
  let rows = [];
  try {
    if (req.is('text/csv') || req.is('text/plain')) {
      const text    = req.body && req.body.toString ? req.body.toString() : '';
      const lines   = text.trim().split(/\r?\n/);
      const headers = lines[0].split(',').map((h) => h.trim().replace(/^"(.*)"$/, '$1'));
      rows = lines.slice(1).filter((l) => l.trim()).map((line) => {
        const vals = line.split(',').map((v) => v.trim().replace(/^"(.*)"$/, '$1'));
        const row  = {};
        headers.forEach((h, i) => { row[h] = vals[i] || ''; });
        return row;
      });
    } else {
      rows = Array.isArray(req.body) ? req.body : (req.body && req.body.contacts ? req.body.contacts : []);
    }
  } catch (_err) {
    return respondError(res, 422, 'PARSE_ERROR', 'Could not parse import body. Send CSV (text/csv) or JSON array.');
  }

  let created = 0, skipped = 0;
  const errors = [];

  rows.forEach((row) => {
    const display_name = row.display_name || row.name || row['Name'] || '';
    const phone_e164   = row.phone_e164 || row.phone || row['Phone'] || '';
    if (!display_name && !phone_e164) { skipped++; return; }

    // Dedup: exact phone match
    if (phone_e164 && _memContacts.some((c) => c.phone_e164 === phone_e164)) { skipped++; return; }

    const now = new Date().toISOString();
    _memContacts.push({
      contact_id:         randomUUID(),
      display_name:       display_name,
      phone_e164:         phone_e164,
      email:              row.email || null,
      account_id:         null,
      account_name:       row.account_name || row.company || null,
      tags:               row.tags ? String(row.tags).split(';').map((t) => t.trim()).filter(Boolean) : [],
      open_cases:         0,
      idle:               0,
      completeness_score: 50,
      source:             'import',
      last_touchpoint:    null,
      created_at:         now,
    });
    created++;
  });

  return respondSuccess(res, { created, skipped, errors }, { total_rows: rows.length, import_source: 'csv' });
});

// ── Standard CRUD ─────────────────────────────────────────────────────────────
// When proxy is configured, forward to downstream contacts service.
// When proxy is absent (dev), serve from in-memory store.

router.get('/', requestValidationMiddleware(), requireScopes(['contacts.read']), (req, res) => {
  if (PROXY_ENABLED) return forwardRequest(req, res);
  return respondSuccess(res, _memContacts, {
    pagination: { page: 1, page_size: _memContacts.length, total_items: _memContacts.length, total_pages: 1 },
  });
});

router.post('/', requestValidationMiddleware(), requireScopes(['contacts.create']), (req, res) => {
  if (PROXY_ENABLED) return forwardRequest(req, res);
  const now     = new Date().toISOString();
  const contact = { contact_id: randomUUID(), completeness_score: 50, created_at: now, open_cases: 0, idle: 0, tags: [], source: 'manual', last_touchpoint: null, ...req.body };
  _memContacts.push(contact);
  return res.status(201).json({ data: contact, meta: {} });
});

router.get('/:contact_id', requestValidationMiddleware(), requireScopes(['contacts.read']), (req, res) => {
  if (PROXY_ENABLED) return forwardRequest(req, res);
  const c = _memContacts.find((x) => x.contact_id === req.params.contact_id);
  if (!c) return respondError(res, 404, 'NOT_FOUND', 'Contact not found.');
  return respondSuccess(res, c);
});

router.patch('/:contact_id', requestValidationMiddleware(), requireScopes(['contacts.update']), (req, res) => {
  if (PROXY_ENABLED) return forwardRequest(req, res);
  const idx = _memContacts.findIndex((x) => x.contact_id === req.params.contact_id);
  if (idx === -1) return respondError(res, 404, 'NOT_FOUND', 'Contact not found.');
  _memContacts[idx] = { ..._memContacts[idx], ...req.body, updated_at: new Date().toISOString() };
  return respondSuccess(res, _memContacts[idx]);
});

router.delete('/:contact_id', requireScopes(['contacts.delete']), (req, res) => {
  if (PROXY_ENABLED) return forwardRequest(req, res);
  const idx = _memContacts.findIndex((x) => x.contact_id === req.params.contact_id);
  if (idx !== -1) _memContacts.splice(idx, 1);
  return res.status(204).send();
});

module.exports = router;
