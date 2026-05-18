const { respondError } = require('./response-wrapper');
const { ensureKnownFields, ensureSnakeCaseKeys, isPlainObject } = require('../validators/common');

function validateContentHeaders(req) {
  const errors = [];
  const methodNeedsBody = ['POST', 'PUT', 'PATCH'].includes(req.method.toUpperCase());

  const acceptHeader = req.headers.accept || '';
  if (!acceptHeader.includes('application/json')) {
    errors.push({ field: 'accept', reason: 'must_accept_application_json' });
  }

  if (methodNeedsBody) {
    const contentType = req.headers['content-type'] || '';
    if (!contentType.includes('application/json')) {
      errors.push({ field: 'content_type', reason: 'must_be_application_json' });
    }
  }

  return errors;
}

function validateQuery(req) {
  const errors = [];
  const query = req.query || {};

  if (query.page && (!Number.isInteger(Number(query.page)) || Number(query.page) < 1)) {
    errors.push({ field: 'page', reason: 'must_be_positive_integer' });
  }

  if (query.page_size) {
    const pageSize = Number(query.page_size);
    if (!Number.isInteger(pageSize) || pageSize < 1 || pageSize > 100) {
      errors.push({ field: 'page_size', reason: 'must_be_integer_between_1_and_100' });
    }
  }

  for (const key of Object.keys(query)) {
    if (key.includes('-')) {
      errors.push({ field: key, reason: 'query_param_must_be_snake_case' });
    }
  }

  return errors;
}

function requestValidationMiddleware(allowedBodyFields = []) {
  return function validate(req, res, next) {
    const errors = [...validateContentHeaders(req), ...validateQuery(req)];

    if (allowedBodyFields.length > 0 && req.body !== undefined) {
      if (!isPlainObject(req.body)) {
        errors.push({ field: 'body', reason: 'must_be_json_object' });
      } else {
        errors.push(...ensureSnakeCaseKeys(req.body));
        errors.push(...ensureKnownFields(req.body, allowedBodyFields));
      }
    }

    if (errors.length > 0) {
      return respondError(res, 'validation_error', 'One or more fields are invalid.', errors, 422);
    }

    next();
  };
}

module.exports = {
  requestValidationMiddleware,
};
