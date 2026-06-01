'use strict';
/**
 * Integration Settings — G-05
 * GET /integrations, PATCH /integrations/:provider, POST /integrations/:provider/test
 * Source: b9-p09 §4 G-05
 * Seed: whatsapp (connected), email (connected), sms (disconnected), push (not_configured)
 */

const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

const _store = {
  whatsapp: {
    provider: 'whatsapp',
    label: 'WhatsApp (360dialog)',
    category: 'communication',
    status: 'connected',
    credentials_set: true,
    api_key_last4: '3f9a',
    webhook_url: 'https://crm.pk/webhooks/whatsapp',
    last_tested_at: '2026-05-30T08:00:00Z',
    last_test_ok: true,
  },
  email: {
    provider: 'email',
    label: 'Email (SendGrid)',
    category: 'communication',
    status: 'connected',
    credentials_set: true,
    api_key_last4: '7b2c',
    from_address: 'noreply@crm.pk',
    last_tested_at: '2026-05-28T10:00:00Z',
    last_test_ok: true,
  },
  sms: {
    provider: 'sms',
    label: 'SMS',
    category: 'notification',
    status: 'disconnected',
    credentials_set: false,
    api_key_last4: null,
    last_tested_at: null,
    last_test_ok: false,
  },
  push: {
    provider: 'push',
    label: 'Push Notifications (FCM)',
    category: 'notification',
    status: 'not_configured',
    credentials_set: false,
    api_key_last4: null,
    last_tested_at: null,
    last_test_ok: false,
  },
};

router.get('/', requestValidationMiddleware(), requireScopes(['integrations.read']), (req, res) => {
  return respondSuccess(res, Object.values(_store));
});

router.patch('/:provider', requestValidationMiddleware(), requireScopes(['integrations.manage']), (req, res) => {
  const { provider } = req.params;
  if (!_store[provider]) return respondError(res, 'not_found', `Unknown provider: ${provider}`, [], 404);
  const allowed = ['label', 'from_address', 'webhook_url'];
  allowed.forEach(k => { if (req.body[k] !== undefined) _store[provider][k] = req.body[k]; }); // nosemgrep
  if (req.body.api_key) {
    _store[provider].credentials_set = true;
    _store[provider].api_key_last4   = String(req.body.api_key).slice(-4);
    _store[provider].status          = 'connected';
  }
  return respondSuccess(res, _store[provider]);
});

router.post('/:provider/test', requestValidationMiddleware(), requireScopes(['integrations.manage']), (req, res) => {
  const { provider } = req.params;
  if (!_store[provider]) return respondError(res, 'not_found', `Unknown provider: ${provider}`, [], 404);
  const ok = _store[provider].credentials_set;
  _store[provider].last_tested_at = new Date().toISOString();
  _store[provider].last_test_ok   = ok;
  if (ok) _store[provider].status = 'connected';
  return respondSuccess(res, {
    ok,
    latency_ms: ok ? (Math.floor(Math.random() * 80) + 20) : null,
    message: ok ? 'Connection successful' : 'No credentials configured',
  });
});

module.exports = router;
