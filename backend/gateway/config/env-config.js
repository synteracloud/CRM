const ALLOWED_NODE_ENVS = new Set(['production', 'development', 'test']);
const ALLOWED_LOG_LEVELS = new Set(['debug', 'info', 'warn', 'error']);

const SENSITIVE_KEYS = new Set([
  'DB_PASSWORD',
  'PAYMENTS_API_KEY',
  'EMAIL_API_KEY',
  'WEBHOOK_SIGNING_SECRET',
]);

const DEFAULTS = Object.freeze({
  NODE_ENV: 'development',
  PORT: 3000,
  LOG_LEVEL: 'info',
  SERVICE_NAME: 'crm-gateway',
  SERVICE_VERSION: 'dev',
  REGION: 'local',
  FEATURE_FLAGS: '{}',
  RUNTIME_CONFIG_OVERRIDES: '{}',
});

function parseInteger(value, key, errors, fallback) {
  if (value === undefined || value === null || value === '') {
    return fallback;
  }

  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed)) {
    errors.push(`${key} must be an integer.`);
    return fallback;
  }

  return parsed;
}

function parseJsonObject(value, key, errors) {
  if (value === undefined || value === null || value === '') {
    return {};
  }

  try {
    const parsed = JSON.parse(value);
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      errors.push(`${key} must be a JSON object.`);
      return {};
    }

    return parsed;
  } catch {
    errors.push(`${key} must be valid JSON.`);
    return {};
  }
}

function validateRequiredValues(resolvedEnv, nodeEnv, errors) {
  const required = [
    'SERVICE_NAME',
    'SERVICE_VERSION',
    'REGION',
  ];

  if (nodeEnv === 'production') {
    required.push('JWT_ISSUER', 'JWT_AUDIENCE', 'JWT_PUBLIC_KEY_URL');
  }

  required.forEach((key) => {
    if (!resolvedEnv[key]) {
      errors.push(`${key} is required.`);
    }
  });
}

function validateOverrides(overrides, errors) {
  Object.keys(overrides).forEach((key) => {
    if (SENSITIVE_KEYS.has(key)) {
      errors.push(`RUNTIME_CONFIG_OVERRIDES cannot override sensitive key ${key}.`);
    }
  });
}

function loadEnvConfig(env = process.env) {
  const errors = [];

  const nodeEnv = env.NODE_ENV || DEFAULTS.NODE_ENV;
  if (!ALLOWED_NODE_ENVS.has(nodeEnv)) {
    errors.push(`NODE_ENV must be one of: ${Array.from(ALLOWED_NODE_ENVS).join(', ')}.`);
  }

  const logLevel = env.LOG_LEVEL || DEFAULTS.LOG_LEVEL;
  if (!ALLOWED_LOG_LEVELS.has(logLevel)) {
    errors.push(`LOG_LEVEL must be one of: ${Array.from(ALLOWED_LOG_LEVELS).join(', ')}.`);
  }

  const resolvedEnv = { ...DEFAULTS, ...env };

  const featureFlags = parseJsonObject(resolvedEnv.FEATURE_FLAGS, 'FEATURE_FLAGS', errors);
  const runtimeOverrides = parseJsonObject(
    resolvedEnv.RUNTIME_CONFIG_OVERRIDES,
    'RUNTIME_CONFIG_OVERRIDES',
    errors,
  );

  validateRequiredValues(resolvedEnv, nodeEnv, errors);
  validateOverrides(runtimeOverrides, errors);

  const config = {
    NODE_ENV: nodeEnv,
    PORT: parseInteger(env.PORT, 'PORT', errors, DEFAULTS.PORT),
    LOG_LEVEL: logLevel,
    SERVICE_NAME: resolvedEnv.SERVICE_NAME,
    SERVICE_VERSION: resolvedEnv.SERVICE_VERSION,
    REGION: resolvedEnv.REGION,
    FEATURE_FLAGS: featureFlags,
    RUNTIME_CONFIG_OVERRIDES: runtimeOverrides,
  };

  if (errors.length) {
    const error = new Error(`Invalid runtime environment configuration:\n- ${errors.join('\n- ')}`);
    error.name = 'RuntimeConfigValidationError';
    throw error;
  }

  return Object.freeze(config);
}

module.exports = {
  DEFAULTS,
  SENSITIVE_KEYS,
  loadEnvConfig,
};
