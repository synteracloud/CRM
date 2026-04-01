function normalizeBooleanFlag(value, defaultValue = false) {
  if (typeof value === 'boolean') {
    return value;
  }

  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase();
    if (normalized === 'true') {
      return true;
    }

    if (normalized === 'false') {
      return false;
    }
  }

  return defaultValue;
}

function buildFeatureFlags(rawFlags = {}) {
  return Object.freeze({
    enableCanaryReadPath: normalizeBooleanFlag(rawFlags.enableCanaryReadPath, false),
    enableClusterFailover: normalizeBooleanFlag(rawFlags.enableClusterFailover, false),
    enableShadowTraffic: normalizeBooleanFlag(rawFlags.enableShadowTraffic, false),
  });
}

module.exports = {
  buildFeatureFlags,
};
