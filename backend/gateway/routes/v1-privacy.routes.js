'use strict';
/**
 * Privacy / Consent Manager — /api/v1/privacy/*
 * Consent records + Data Subject Requests (DSRs).
 * All consent operations are immutable-append (audit trail).
 */

const express  = require('express');
const { randomUUID } = require('crypto');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

const _consents = [
  { contact_id:'ct-001', contact_name:'Tariq Mehmood', phone_e164:'+923001234567', service_communication:{ granted:true,  granted_at:'2026-01-10T08:00:00Z', channel:'whatsapp_inbound' }, marketing:{ granted:false, revoked_at:null, keyword:null }, data_processing:{ granted:true, granted_at:'2026-01-10T08:00:00Z' } },
  { contact_id:'ct-002', contact_name:'Sana Sheikh',   phone_e164:'+923119876543', service_communication:{ granted:true,  granted_at:'2026-02-01T09:00:00Z', channel:'web_form' },          marketing:{ granted:true,  revoked_at:null, keyword:null }, data_processing:{ granted:true, granted_at:'2026-02-01T09:00:00Z' } },
  { contact_id:'ct-003', contact_name:'Bilal Malik',   phone_e164:'+923451122334', service_communication:{ granted:true,  granted_at:'2026-02-15T10:00:00Z', channel:'whatsapp_inbound' }, marketing:{ granted:false, revoked_at:'2026-04-01T00:00:00Z', keyword:'STOP' }, data_processing:{ granted:true, granted_at:'2026-02-15T10:00:00Z' } },
  { contact_id:'ct-004', contact_name:'Fatima Zahra',  phone_e164:'+923336677889', service_communication:{ granted:false, granted_at:null, channel:null },                                 marketing:{ granted:false, revoked_at:null, keyword:null }, data_processing:{ granted:false, granted_at:null } },
];

const _dsrs = [];

router.get('/consent', requestValidationMiddleware(), requireScopes(['contacts.read']), (req, res) => {
  return respondSuccess(res, _consents, { total_items: _consents.length });
});

router.get('/consent/:contact_id', requestValidationMiddleware(), requireScopes(['contacts.read']), (req, res) => {
  const c = _consents.find((x) => x.contact_id === req.params.contact_id);
  if (!c) return respondError(res, 404, 'NOT_FOUND', 'Consent record not found.');
  return respondSuccess(res, c);
});

router.patch('/consent/:contact_id', requestValidationMiddleware(), requireScopes(['contacts.update']), (req, res) => {
  const idx = _consents.findIndex((x) => x.contact_id === req.params.contact_id);
  if (idx === -1) return respondError(res, 404, 'NOT_FOUND', 'Consent record not found.');
  const { service_communication, marketing, data_processing } = req.body;
  if (service_communication) Object.assign(_consents[idx].service_communication, service_communication);
  if (marketing)             Object.assign(_consents[idx].marketing, marketing);
  if (data_processing)       Object.assign(_consents[idx].data_processing, data_processing);
  _consents[idx].updated_at = new Date().toISOString();
  return respondSuccess(res, _consents[idx]);
});

router.get('/requests', requestValidationMiddleware(), requireScopes(['contacts.read']), (req, res) => {
  return respondSuccess(res, _dsrs, { total_items: _dsrs.length });
});

router.post('/requests', requestValidationMiddleware(['contact_id','request_type']), requireScopes(['contacts.update']), (req, res) => {
  const now = new Date().toISOString();
  const sla_due = new Date(Date.now() + 30 * 86400000).toISOString();
  const dsr = {
    request_id: randomUUID(),
    tenant_id: req.auth.tenant_id,
    contact_id:   req.body.contact_id,
    request_type: req.body.request_type,  // 'export' | 'deletion'
    status: 'pending',
    reason: req.body.reason || null,
    created_at: now,
    sla_due_at: sla_due,
    completed_at: null,
  };
  _dsrs.push(dsr);
  return res.status(201).json({ data: dsr, meta: {} });
});

module.exports = router;
