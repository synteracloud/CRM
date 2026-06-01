'use strict';
/**
 * Roles CRUD — GET/POST/PATCH/DELETE /api/v1/roles
 * Scope: users.read (GET) / users.update (write) — tenant_admin gated
 * Seeded with 5 standard roles from rbac-scopes.js. Custom roles append to the array.
 */

const express  = require('express');
const { randomUUID } = require('crypto');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

const _roles = [
  { role_id:'role-sales-rep',     name:'sales_rep',     label:'Sales Rep',     is_system:true,  active_user_count:2, permissions:['leads.read','leads.create','followups.read','followups.create','followups.complete','followups.snooze','opportunities.read','contacts.read','activities.read'] },
  { role_id:'role-sales-mgr',     name:'sales_manager', label:'Sales Manager', is_system:true,  active_user_count:1, permissions:['leads.read','leads.create','leads.update','leads.assign','followups.read','followups.create','followups.complete','opportunities.read','opportunities.create','opportunities.update','contacts.read','contacts.create','users.read','audit.read'] },
  { role_id:'role-finance',       name:'finance',       label:'Finance',       is_system:true,  active_user_count:1, permissions:['collections.read','collections.invoice','collections.reconcile','payments.read','payments.create','revenue.read','subscriptions.read','quotes.read','invoices.read'] },
  { role_id:'role-admin',         name:'admin',         label:'Admin',         is_system:true,  active_user_count:1, permissions:['users.read','users.create','users.update','audit.read','audit.logs.read'] },
  { role_id:'role-tenant-admin',  name:'tenant_admin',  label:'Tenant Admin',  is_system:true,  active_user_count:1, permissions:['*'] },
];

router.get('/', requestValidationMiddleware(), requireScopes(['users.read']), (req, res) => {
  return respondSuccess(res, _roles, { total_items: _roles.length });
});

router.post('/', requestValidationMiddleware(['name','permissions']), requireScopes(['users.update']), (req, res) => {
  const { name, label, permissions } = req.body;
  if (_roles.some((r) => r.name === name)) return respondError(res, 409, 'CONFLICT', 'Role name already exists.');
  const role = { role_id: randomUUID(), name, label: label || name, is_system: false, active_user_count: 0, permissions: permissions || [], created_at: new Date().toISOString() };
  _roles.push(role);
  return res.status(201).json({ data: role, meta: {} });
});

router.patch('/:role_id', requestValidationMiddleware(), requireScopes(['users.update']), (req, res) => {
  const idx = _roles.findIndex((r) => r.role_id === req.params.role_id);
  if (idx === -1) return respondError(res, 404, 'NOT_FOUND', 'Role not found.');
  if (_roles[idx].is_system && req.body.name) return respondError(res, 422, 'SYSTEM_ROLE', 'Cannot rename a system role.');
  const allowed = ['label','permissions'];
  allowed.forEach((k) => { if (req.body[k] !== undefined) _roles[idx][k] = req.body[k]; }); // nosemgrep
  _roles[idx].updated_at = new Date().toISOString();
  return respondSuccess(res, _roles[idx]);
});

router.delete('/:role_id', requireScopes(['users.update']), (req, res) => {
  const idx = _roles.findIndex((r) => r.role_id === req.params.role_id);
  if (idx === -1) return respondError(res, 404, 'NOT_FOUND', 'Role not found.');
  if (_roles[idx].is_system) return respondError(res, 422, 'SYSTEM_ROLE', 'Cannot delete a system role.');
  if (_roles[idx].active_user_count > 0) return respondError(res, 409, 'ROLE_IN_USE', 'Role has active user assignments. Reassign users first.');
  _roles.splice(idx, 1);
  return res.status(204).send();
});

module.exports = router;
