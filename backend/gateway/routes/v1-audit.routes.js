const http = require('http');
const https = require('https');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { listAuditEvents } = require('../middleware/audit-log');

const router = express.Router();

const ACTIVITY_SERVICE_URL = process.env.ACTIVITY_SERVICE_URL || 'http://localhost:5003';

// ── Existing: GET /audits/events ──────────────────────────────────────────────
router.get('/events', requestValidationMiddleware(), requireScopes(['audit.logs.read']), (req, res) => {
  const events = listAuditEvents(req.auth.tenant_id);
  return respondSuccess(res, events, {
    pagination: {
      page: Number(req.query.page || 1),
      page_size: Number(req.query.page_size || 25),
      total_items: events.length,
      total_pages: 1,
    },
  });
});

// ── GET /audits/chain-check?tenant_id=xxx ─────────────────────────────────────
// Docs: docs/observability-audit.md, gap-register.md GAP-017
// Calls ActivityControlEngine.verify_chain_integrity() via internal service.
// Requires auditor or tenant_admin scope.
router.get('/chain-check', requireScopes(['audit.logs.read']), async (req, res) => {
  const tenantId = req.query.tenant_id || (req.auth && req.auth.tenant_id);
  if (!tenantId) {
    return respondError(res, 400, 'MISSING_TENANT_ID', 'tenant_id query param required');
  }

  function fetchJson(url) {
    return new Promise((resolve, reject) => {
      const client = url.startsWith('https') ? https : http;
      const request = client.get(url, (resp) => {
        let data = '';
        resp.on('data', (chunk) => { data += chunk; });
        resp.on('end', () => {
          try { resolve(JSON.parse(data)); }
          catch (e) { reject(new Error('invalid JSON from activity service')); }
        });
      });
      request.on('error', reject);
      request.setTimeout(5000, () => { request.destroy(); reject(new Error('timeout')); });
    });
  }

  try {
    const url = `${ACTIVITY_SERVICE_URL}/internal/chain-check?tenant_id=${encodeURIComponent(tenantId)}`;
    const result = await fetchJson(url);
    return respondSuccess(res, result, { tenant_id: tenantId });
  } catch (_err) {
    // Activity service not reachable — return stub so callers get the contract.
    return respondSuccess(res, {
      valid: null,
      entries_checked: 0,
      first_broken_seq: null,
      errors: [],
      note: 'activity_service_unreachable — call verify_chain_integrity() directly',
    }, { tenant_id: tenantId, stub: true });
  }
});

module.exports = router;
