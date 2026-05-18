const test = require('node:test');
const assert = require('node:assert/strict');

const { loadEnvConfig } = require('./env-config');
const { buildFeatureFlags } = require('./feature-flags');
const { applySafeOverrides, buildRuntimeConfig } = require('./runtime-config');

test('loadEnvConfig rejects sensitive override keys', () => {
  assert.throws(() => loadEnvConfig({
    NODE_ENV: 'development',
    SERVICE_NAME: 'gateway',
    SERVICE_VERSION: '1.0.0',
    REGION: 'us-east-1',
    RUNTIME_CONFIG_OVERRIDES: JSON.stringify({ DB_PASSWORD: 'never' }),
  }), /cannot override sensitive key DB_PASSWORD/);
});

test('buildFeatureFlags normalizes boolean values safely', () => {
  const flags = buildFeatureFlags({
    enableCanaryReadPath: 'true',
    enableClusterFailover: 'FALSE',
    enableShadowTraffic: 'unknown',
  });

  assert.equal(flags.enableCanaryReadPath, true);
  assert.equal(flags.enableClusterFailover, false);
  assert.equal(flags.enableShadowTraffic, false);
});

test('applySafeOverrides only accepts approved keys', () => {
  const merged = applySafeOverrides(
    {
      PORT: 3000,
      LOG_LEVEL: 'info',
      SERVICE_VERSION: '1.0.0',
    },
    {
      PORT: 4000,
      SERVICE_VERSION: '2.0.0',
    },
  );

  assert.equal(merged.PORT, 4000);
  assert.equal(merged.SERVICE_VERSION, '1.0.0');
});

test('buildRuntimeConfig creates immutable runtime config tree', () => {
  const runtimeConfig = buildRuntimeConfig({
    NODE_ENV: 'development',
    SERVICE_NAME: 'crm-gateway',
    SERVICE_VERSION: '2.1.0',
    REGION: 'us-west-2',
    FEATURE_FLAGS: JSON.stringify({ enableClusterFailover: true }),
  });

  assert.equal(runtimeConfig.service.name, 'crm-gateway');
  assert.equal(runtimeConfig.featureFlags.enableClusterFailover, true);
  assert.equal(Object.isFrozen(runtimeConfig), true);
  assert.equal(Object.isFrozen(runtimeConfig.service), true);
  assert.equal(Object.isFrozen(runtimeConfig.featureFlags), true);
});
