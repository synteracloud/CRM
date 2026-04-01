const { respondError } = require('./response-wrapper');

function buildUpstreamUrl(req, serviceBaseUrl) {
  const upstream = serviceBaseUrl || process.env.GATEWAY_UPSTREAM_BASE_URL;
  if (!upstream) {
    return null;
  }

  const base = upstream.endsWith('/') ? upstream.slice(0, -1) : upstream;
  const path = req.originalUrl.startsWith('/') ? req.originalUrl : `/${req.originalUrl}`;
  return `${base}${path}`;
}

async function forwardRequest(req, res) {
  const upstreamUrl = buildUpstreamUrl(req);
  if (!upstreamUrl) {
    return respondError(
      res,
      'service_unavailable',
      'Upstream transport is not configured for this gateway route.',
      [{ field: 'gateway_upstream_base_url', reason: 'missing_configuration' }],
      503,
    );
  }

  const headers = {
    accept: 'application/json',
    authorization: req.headers.authorization,
    'content-type': req.headers['content-type'] || 'application/json',
    'x-request-id': req.request_id,
    'x-tenant-id': req.auth?.tenant_id,
  };

  const upstreamResponse = await fetch(upstreamUrl, {
    method: req.method,
    headers,
    body: ['GET', 'HEAD'].includes(req.method) ? undefined : JSON.stringify(req.body || {}),
  });

  const payload = await upstreamResponse.json().catch(() => ({}));
  return res.status(upstreamResponse.status).json(payload);
}

module.exports = {
  forwardRequest,
};
