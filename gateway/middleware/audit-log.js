const crypto = require('crypto');
const { respondError } = require('./response-wrapper');

const auditEvents = [];

function canonicalRoute(path = '') {
  return path.replace(/\/[A-Za-z0-9_\-]{6,}/g, '/:id');
}

function hashEnvelope(envelope) {
  return crypto.createHash('sha256').update(JSON.stringify(envelope)).digest('hex');
}

function appendAuditEvent(event) {
  const chainState = verifyAuditChain();
  if (!chainState.valid) {
    throw new Error(`Audit chain tamper detected at index ${chainState.failing_index}`);
  }
  const previousHash = auditEvents.length > 0 ? auditEvents[auditEvents.length - 1].hash : null;
  const envelope = {
    ...event,
    previous_hash: previousHash,
  };
  const hash = hashEnvelope(envelope);
  const immutableRecord = Object.freeze({ ...envelope, hash });
  auditEvents.push(immutableRecord);
  return immutableRecord;
}

function verifyAuditChain() {
  for (let i = 0; i < auditEvents.length; i += 1) {
    const current = auditEvents[i];
    const expectedPrevHash = i === 0 ? null : auditEvents[i - 1].hash;
    if (current.previous_hash !== expectedPrevHash) {
      return { valid: false, failing_index: i, reason: 'previous_hash_mismatch' };
    }

    const { hash, ...envelope } = current;
    if (hashEnvelope(envelope) !== hash) {
      return { valid: false, failing_index: i, reason: 'hash_mismatch' };
    }
  }
  return { valid: true };
}

const ACTIONS_BY_ROUTE = Object.freeze({
  'POST /api/v1/users': 'users.create',
  'POST /api/v1/accounts': 'accounts.create',
  'PATCH /api/v1/accounts/:id': 'accounts.update',
  'DELETE /api/v1/accounts/:id': 'accounts.delete',
  'PUT /api/v1/accounts/:id/contacts/:id': 'accounts.contacts.link',
  'DELETE /api/v1/accounts/:id/contacts/:id': 'accounts.contacts.unlink',
  'POST /api/v1/contacts': 'contacts.create',
  'PATCH /api/v1/contacts/:id': 'contacts.update',
  'DELETE /api/v1/contacts/:id': 'contacts.delete',
  'POST /api/v1/quotes': 'quotes.create',
  'POST /api/v1/quotes/:id/acceptances': 'quotes.accept',
  'POST /api/v1/quotes/:id/orders': 'orders.create',
  'POST /api/v1/payments': 'payments.create',
  'POST /api/v1/payments/:id/status': 'payments.update',
  'POST /api/v1/subscriptions': 'billing.create',
  'POST /api/v1/invoice-summaries': 'invoices.create',
  'POST /api/v1/price-books': 'pricing.create',
  'POST /api/v1/tasks': 'tasks.create',
  'POST /api/v1/tasks/:id/reschedule': 'tasks.update',
  'POST /api/v1/activities': 'activities.create',
  'POST /api/v1/emails': 'emails.send',
  'POST /api/v1/emails/:id/events': 'emails.track',
  'POST /api/v1/forecasts/model': 'forecasts.read',
  'POST /api/v1/forecasts/aggregate': 'forecasts.read',
});

function auditMiddleware({ strict = true } = {}) {
  return function audit(req, res, next) {
    const mutating = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method.toUpperCase());
    if (!mutating) return next();

    const actionKey = `${req.method.toUpperCase()} ${canonicalRoute(req.path)}`;
    const auditAction = ACTIONS_BY_ROUTE[actionKey] || null;

    if (!auditAction && strict) {
      return respondError(
        res,
        'forbidden',
        'Mutation blocked: missing audit mapping.',
        [{ field: 'route', reason: 'audit_mapping_missing' }],
        403,
      );
    }

    res.on('finish', () => {
      if (!auditAction) return;
      appendAuditEvent({
        event_id: `aud_${crypto.randomBytes(12).toString('hex')}`,
        event_time: new Date().toISOString(),
        request_id: req.request_id,
        trace_id: req.trace_id || null,
        tenant_id: req.auth?.tenant_id || null,
        actor_id: req.auth?.sub || null,
        action: auditAction,
        method: req.method.toUpperCase(),
        route: req.path,
        resource_id: Object.values(req.params || {})[0] || null,
        result: res.statusCode < 400 ? 'success' : 'failure',
      });
    });

    return next();
  };
}

function listAuditEvents(tenantId) {
  return Object.freeze(auditEvents.filter((event) => event.tenant_id === tenantId).map((event) => Object.freeze({ ...event })));
}

module.exports = {
  auditMiddleware,
  listAuditEvents,
  verifyAuditChain,
};
