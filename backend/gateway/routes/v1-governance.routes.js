'use strict';
/**
 * Data Governance Console — J-03
 * GET /governance/classification, GET /governance/retention,
 * GET /governance/sar, POST /governance/sar
 * Source: data-governance-layer.md §2.3 + §2.5, b9-p12 §2.5
 */

const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');

const router = express.Router();

const CLASSIFICATION = [
  { entity: 'Contact',       field: 'phone_e164',    classification: 'PII',       legal_basis: 'Legitimate Interest' },
  { entity: 'Contact',       field: 'email',          classification: 'PII',       legal_basis: 'Legitimate Interest' },
  { entity: 'Lead',          field: 'contact_name',   classification: 'PII',       legal_basis: 'Legitimate Interest' },
  { entity: 'Invoice',       field: 'amount_due',     classification: 'financial', legal_basis: 'Contract Obligation' },
  { entity: 'Payment',       field: 'transaction_id', classification: 'financial', legal_basis: 'Contract Obligation' },
  { entity: 'AuditLog',      field: 'actor_id',       classification: 'internal',  legal_basis: 'Legal Obligation' },
  { entity: 'ActivityEvent', field: 'description',    classification: 'internal',  legal_basis: 'Legitimate Interest' },
  { entity: 'Message',       field: 'content',        classification: 'PII',       legal_basis: 'Consent' },
  { entity: 'SessionToken',  field: 'token_hash',     classification: 'internal',  legal_basis: 'Legal Obligation' },
  { entity: 'Opportunity',   field: 'amount',         classification: 'financial', legal_basis: 'Contract Obligation' },
];

// Canonical retention periods from data-governance-layer.md §2.3
const RETENTION = [
  { entity_class: 'Financial records (Invoice, Payment)', hot_period: '7 years',  archive_period: '—',      legal_basis: 'Legal (SECP/FBR)',    deletion_schedule: 'Annual purge after retention window' },
  { entity_class: 'AuditLog',                            hot_period: '7 years',  archive_period: '—',      legal_basis: 'Legal Obligation',    deletion_schedule: 'Annual purge' },
  { entity_class: 'ActivityEvent',                       hot_period: '3 years',  archive_period: '5 years', legal_basis: 'Legitimate Interest', deletion_schedule: 'Rolling deletion' },
  { entity_class: 'Contact / Lead',                      hot_period: '5 years',  archive_period: '7 years', legal_basis: 'Consent + LI',        deletion_schedule: 'On erasure request or inactivity' },
  { entity_class: 'SessionToken',                        hot_period: '90 days',  archive_period: '12 months', legal_basis: 'Security',          deletion_schedule: 'Automated nightly cleanup' },
  { entity_class: 'Message',                             hot_period: '2 years',  archive_period: '5 years', legal_basis: 'Consent',             deletion_schedule: 'Automated on expiry' },
];

const _sarStore = [];

router.get('/classification', requestValidationMiddleware(), requireScopes(['compliance.read']), (req, res) => {
  return respondSuccess(res, CLASSIFICATION);
});

router.get('/retention', requestValidationMiddleware(), requireScopes(['compliance.read']), (req, res) => {
  return respondSuccess(res, RETENTION);
});

router.get('/sar', requestValidationMiddleware(), requireScopes(['privacy.read']), (req, res) => {
  return respondSuccess(res, _sarStore);
});

router.post('/sar', requestValidationMiddleware(), requireScopes(['privacy.manage']), (req, res) => {
  const { contact_id, request_type, reason } = req.body;
  const sar = {
    request_id:  'sar-' + Date.now(),
    contact_id:  contact_id || null,
    request_type: request_type || 'export',
    reason:      reason || '',
    status:      'pending',
    created_at:  new Date().toISOString(),
    sla_due_at:  new Date(Date.now() + 30 * 24 * 3600 * 1000).toISOString(),
  };
  _sarStore.push(sar);
  return respondSuccess(res, sar);
});

module.exports = router;
