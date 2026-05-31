'use strict';

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { ContactsRepository } = require('../db/repositories/contacts.repository');

const router = express.Router();

let repo = null;
try {
  repo = new ContactsRepository();
} catch (_e) { /* pg not available */ }

// ── GET /accounts ─────────────────────────────────────────────────────────────
router.get('/', requestValidationMiddleware(), requireScopes(['accounts.read']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  const limit  = Math.min(Number(req.query.page_size || 25), 100);
  const offset = (Math.max(Number(req.query.page || 1), 1) - 1) * limit;
  try {
    if (repo) {
      const rows = await repo.listAccounts(tenantId, { limit, offset });
      return respondSuccess(res, rows, {
        pagination: { page: Number(req.query.page || 1), page_size: limit, total_items: rows.length, total_pages: 1 },
      });
    }
    return respondSuccess(res, [], { pagination: { page: 1, page_size: 25, total_items: 0, total_pages: 0 } });
  } catch (err) {
    req.app.locals.logger?.error?.({ event: 'accounts.list.error', error: err.message });
    return respondError(res, 'internal_error', 'DB_ERROR', [], 500);
  }
});

// ── POST /accounts ────────────────────────────────────────────────────────────
router.post('/', requestValidationMiddleware(), requireScopes(['accounts.create']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  try {
    if (repo) {
      const account = await repo.createAccount(tenantId, { account_id: randomUUID(), ...req.body });
      return res.status(201).json({ data: account, meta: {} });
    }
    return res.status(201).json({ data: { account_id: randomUUID(), tenant_id: tenantId, ...req.body }, meta: {} });
  } catch (err) {
    return respondError(res, 'internal_error', 'DB_ERROR', [], 500);
  }
});

// ── GET /accounts/:account_id ─────────────────────────────────────────────────
router.get('/:account_id', requestValidationMiddleware(), requireScopes(['accounts.read']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  try {
    if (repo) {
      const account = await repo.findAccountById(tenantId, req.params.account_id);
      if (!account) return respondError(res, 'not_found', 'Account not found.', [], 404);
      return respondSuccess(res, account);
    }
    return respondError(res, 'not_found', 'Account not found.', [], 404);
  } catch (err) {
    return respondError(res, 'internal_error', 'DB_ERROR', [], 500);
  }
});

// ── PATCH /accounts/:account_id ───────────────────────────────────────────────
router.patch('/:account_id', requestValidationMiddleware(), requireScopes(['accounts.update']), async (req, res) => {
  const tenantId = req.auth.tenant_id;
  try {
    if (repo) {
      const account = await repo.updateAccount(tenantId, req.params.account_id, req.body);
      if (!account) return respondError(res, 'not_found', 'Account not found.', [], 404);
      return respondSuccess(res, account);
    }
    return respondError(res, 'not_found', 'Account not found.', [], 404);
  } catch (err) {
    return respondError(res, 'internal_error', 'DB_ERROR', [], 500);
  }
});

module.exports = router;
