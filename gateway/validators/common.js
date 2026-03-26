const RFC3339_UTC = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
const SNAKE_CASE = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;

function isPlainObject(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function ensureSnakeCaseKeys(obj, path = '') {
  const violations = [];

  if (!isPlainObject(obj)) return violations;

  for (const key of Object.keys(obj)) {
    if (!SNAKE_CASE.test(key)) {
      violations.push({
        field: path ? `${path}.${key}` : key,
        reason: 'must_be_snake_case',
      });
    }

    const value = obj[key];
    if (isPlainObject(value)) {
      violations.push(...ensureSnakeCaseKeys(value, path ? `${path}.${key}` : key));
    }
  }

  return violations;
}

function ensureKnownFields(obj, allowedFields) {
  if (!isPlainObject(obj)) {
    return [{ field: 'body', reason: 'must_be_json_object' }];
  }

  const allowed = new Set(allowedFields);
  return Object.keys(obj)
    .filter((key) => !allowed.has(key))
    .map((key) => ({ field: key, reason: 'unknown_property' }));
}

function isRfc3339Utc(value) {
  return typeof value === 'string' && RFC3339_UTC.test(value);
}

module.exports = {
  ensureSnakeCaseKeys,
  ensureKnownFields,
  isRfc3339Utc,
  isPlainObject,
};
