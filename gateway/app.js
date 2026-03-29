const express = require('express');
const routes = require('./routes');
const { requestIdMiddleware } = require('./middleware/request-id');
const { observabilityMiddleware } = require('./middleware/observability');
const { rateLimitHook } = require('./middleware/rate-limit-hook');
const { respondError } = require('./middleware/response-wrapper');
const { authMiddleware } = require('./middleware/auth-rbac');
const { auditMiddleware } = require('./middleware/audit-log');
const { idempotencyMiddleware } = require('./middleware/idempotency');

const app = express();

app.use(express.json());
app.use(requestIdMiddleware);
app.use(observabilityMiddleware());
app.use(authMiddleware());
app.use(
  rateLimitHook({}),
);
app.use(idempotencyMiddleware());
app.use(auditMiddleware({ strict: true }));

app.use(routes);

app.use((err, req, res, next) => {
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return respondError(res, 'bad_request', 'Malformed JSON body.', [{ field: 'body', reason: 'invalid_json' }], 400);
  }

  return respondError(res, 'internal_error', 'An unexpected error occurred.', [], 500);
});

module.exports = {
  app,
};
