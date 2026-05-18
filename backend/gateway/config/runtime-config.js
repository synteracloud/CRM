const { loadEnvConfig } = require('./env-config');
const { buildFeatureFlags } = require('./feature-flags');

const ALLOWED_OVERRIDE_KEYS = new Set([
  'PORT',
  'LOG_LEVEL',
  'REGION',
]);

function applySafeOverrides(baseConfig, overrideConfig = {}) {
  const merged = { ...baseConfig };

  Object.entries(overrideConfig).forEach(([key, value]) => {
    if (!ALLOWED_OVERRIDE_KEYS.has(key)) {
      return;
    }

    merged[key] = value;
  });

  return merged;
}

function buildRuntimeConfig(env = process.env) {
  const envConfig = loadEnvConfig(env);
  const featureFlags = buildFeatureFlags(envConfig.FEATURE_FLAGS);

  const merged = applySafeOverrides(envConfig, envConfig.RUNTIME_CONFIG_OVERRIDES);

  return Object.freeze({
    service: Object.freeze({
      name: merged.SERVICE_NAME,
      version: merged.SERVICE_VERSION,
      region: merged.REGION,
      nodeEnv: merged.NODE_ENV,
      logLevel: merged.LOG_LEVEL,
      port: Number(merged.PORT),
    }),
    featureFlags,
  });
}

module.exports = {
  ALLOWED_OVERRIDE_KEYS,
  applySafeOverrides,
  buildRuntimeConfig,
};
