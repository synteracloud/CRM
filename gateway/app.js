const express = require('express');
const routes = require('./routes');
const { requestIdMiddleware } = require('./middleware/request-id');
const { rateLimitHook } = require('./middleware/rate-limit-hook');
const { respondError } = require('./middleware/response-wrapper');
const { authMiddleware } = require('./middleware/auth-rbac');

const app = express();

app.use(express.json());
app.use(requestIdMiddleware);
app.use(authMiddleware());

app.use(
  rateLimitHook({
    evaluate: async () => ({ allowed: true }),
  }),
);

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
