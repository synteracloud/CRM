const { CANONICAL_ERROR_CODES } = require('../types/api');

function respondSuccess(res, data, meta = {}) {
  const requestId = res.req.request_id || meta.request_id;
  return res.json({
    data,
    meta: {
      request_id: requestId,
      ...meta,
    },
  });
}

function respondError(res, code, message, details = [], statusOverride) {
  const status = statusOverride || CANONICAL_ERROR_CODES[code] || 500;
  const requestId = res.req.request_id;

  return res.status(status).json({
    error: {
      code,
      message,
      details: Array.isArray(details) ? details : [],
    },
    meta: {
      request_id: requestId,
    },
  });
}

module.exports = {
  respondSuccess,
  respondError,
};
