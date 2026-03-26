const CANONICAL_ERROR_CODES = Object.freeze({
  bad_request: 400,
  unauthorized: 401,
  forbidden: 403,
  not_found: 404,
  conflict: 409,
  validation_error: 422,
  rate_limited: 429,
  internal_error: 500,
  service_unavailable: 503,
});

module.exports = {
  CANONICAL_ERROR_CODES,
};
