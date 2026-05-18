const crypto = require('crypto');

function buildRequestId() {
  return `req_${crypto.randomBytes(13).toString('hex')}`;
}

function requestIdMiddleware(req, res, next) {
  const incoming = req.headers['x-request-id'];
  const requestId = typeof incoming === 'string' && incoming.trim() ? incoming.trim() : buildRequestId();

  req.request_id = requestId;
  res.setHeader('x-request-id', requestId);

  next();
}

module.exports = {
  requestIdMiddleware,
};
