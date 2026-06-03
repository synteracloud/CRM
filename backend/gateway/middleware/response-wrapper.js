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
  // Support legacy call convention used across route files:
  // respondError(res, 422, 'ERROR_CODE', 'Human message', [details])
  if (typeof code === 'number') {
    const httpStatus = code;
    const errCode    = message;
    const errMessage = typeof details === 'string' ? details : '';
    const errDetails = Array.isArray(statusOverride) ? statusOverride
                     : Array.isArray(details)        ? details
                     : [];
    code           = errCode;
    message        = errMessage;
    details        = errDetails;
    statusOverride = httpStatus;
  }
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
