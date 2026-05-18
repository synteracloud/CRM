'use strict';

/**
 * Feature visibility ordering — P-011.
 *
 * Docs: docs/adoption-ux.md §2 — Feature Visibility Ordering
 *
 * The four-tier progressive disclosure model governs which features are
 * surfaced to a user and when.  All UI code must use this module to decide
 * visibility — never hard-code tier decisions in components.
 *
 * Tier 1 — Always visible (day 1, all roles)
 * Tier 2 — Visible after first session (≥1 Tier-1 action completed)
 * Tier 3 — Discoverable on demand (not on home screen by default)
 * Tier 4 — Expert / Settings only
 *
 * Usage::
 *   const { isVisible, getVisibleFeatures } = require('./feature-visibility');
 *   if (isVisible('opportunities', sessionCtx)) { ... }
 */

// ── Feature registry ───────────────────────────────────────────────────────────
// key → { tier, roles }
// roles: null = all roles; array = allowlist

const FEATURE_REGISTRY = Object.freeze({
  // ── Tier 1 — revenue-generating, day 1 ────────────────────────────────────
  lead_pipeline:         { tier: 1, roles: null },
  followup_queue:        { tier: 1, roles: null },
  collections:           { tier: 1, roles: null },
  quick_action_new_lead: { tier: 1, roles: null },
  quick_action_payment:  { tier: 1, roles: null },
  quick_action_followup: { tier: 1, roles: null },

  // ── Tier 2 — visible after first session ──────────────────────────────────
  opportunities:         { tier: 2, roles: null },
  employee_activity:     { tier: 2, roles: ['manager', 'owner', 'admin'] },
  escalation_status:     { tier: 2, roles: null },
  owner_dashboard:       { tier: 2, roles: ['owner', 'admin'] },
  reminder_templates:    { tier: 2, roles: null },

  // ── Tier 3 — discoverable (settings / search / menu) ─────────────────────
  analytics_reports:     { tier: 3, roles: null },
  workflow_builder:      { tier: 3, roles: ['admin', 'owner'] },
  custom_pipeline:       { tier: 3, roles: ['admin', 'owner'] },
  team_management:       { tier: 3, roles: ['admin', 'owner'] },
  contacts_accounts:     { tier: 3, roles: null },
  knowledge_base:        { tier: 3, roles: null },
  campaigns:             { tier: 3, roles: ['admin', 'owner', 'manager'] },

  // ── Tier 4 — expert / settings only ──────────────────────────────────────
  api_integrations:      { tier: 4, roles: ['admin'] },
  webhook_config:        { tier: 4, roles: ['admin'] },
  custom_objects:        { tier: 4, roles: ['admin'] },
  feature_flag_overrides:{ tier: 4, roles: ['admin'] },
  audit_log_export:      { tier: 4, roles: ['admin', 'owner'] },
  territory_management:  { tier: 4, roles: ['admin', 'owner'] },
});

/**
 * Session context expected by all visibility functions.
 *
 * @typedef {Object} SessionContext
 * @property {string}   role            — user role (admin | owner | manager | agent)
 * @property {boolean}  hasCompletedTier1Action — true after any Tier-1 action in this session
 * @property {string[]} [grantedFeatures] — explicit feature overrides (feature flag outcomes)
 */

// ── Core API ──────────────────────────────────────────────────────────────────

/**
 * Return the tier (1–4) for a feature key.
 * Returns null for unknown features.
 */
function getTier(featureKey) {
  return FEATURE_REGISTRY[featureKey]?.tier ?? null;
}

/**
 * Return true if the feature should be visible given the session context.
 *
 * Rules:
 *  - Unknown features → false (safe default).
 *  - Tier 1 → always visible if role is permitted.
 *  - Tier 2 → visible only after hasCompletedTier1Action.
 *  - Tier 3 → requires explicit navigation (returned as `discoverable: true`).
 *  - Tier 4 → never visible outside Settings.
 *  - Feature flag override in grantedFeatures → always visible regardless of tier.
 *
 * @param {string}         featureKey
 * @param {SessionContext} sessionCtx
 * @returns {boolean}
 */
function isVisible(featureKey, sessionCtx) {
  const feature = FEATURE_REGISTRY[featureKey];
  if (!feature) return false;

  // Explicit feature-flag grant overrides tier logic
  if (Array.isArray(sessionCtx.grantedFeatures) && sessionCtx.grantedFeatures.includes(featureKey)) {
    return true;
  }

  // Role check
  if (feature.roles !== null && !feature.roles.includes(sessionCtx.role)) {
    return false;
  }

  switch (feature.tier) {
    case 1: return true;
    case 2: return !!sessionCtx.hasCompletedTier1Action;
    case 3: return false;  // discoverable only — not auto-surfaced
    case 4: return false;  // settings-only — not auto-surfaced
    default: return false;
  }
}

/**
 * Return true if the feature is accessible (discoverable or settings) but not
 * automatically surfaced.  Use this to decide whether to render a nav item
 * at a lower prominence level.
 */
function isDiscoverable(featureKey, sessionCtx) {
  const feature = FEATURE_REGISTRY[featureKey];
  if (!feature) return false;
  if (feature.roles !== null && !feature.roles.includes(sessionCtx.role)) return false;
  return feature.tier === 3 || feature.tier === 4;
}

/**
 * Return all features that should be actively surfaced to the user right now.
 * Does not include Tier 3/4 (those are discoverable, not auto-surfaced).
 *
 * @param {SessionContext} sessionCtx
 * @returns {string[]}
 */
function getVisibleFeatures(sessionCtx) {
  return Object.keys(FEATURE_REGISTRY).filter((key) => isVisible(key, sessionCtx));
}

/**
 * Return all features a user can access (including discoverable Tier 3/4).
 * Used to build the full navigation tree.
 *
 * @param {SessionContext} sessionCtx
 * @returns {{ key: string, tier: number, surfaced: boolean }[]}
 */
function getAllAccessibleFeatures(sessionCtx) {
  return Object.entries(FEATURE_REGISTRY)
    .filter(([key, feature]) => {
      if (feature.roles !== null && !feature.roles.includes(sessionCtx.role)) return false;
      if (Array.isArray(sessionCtx.grantedFeatures) && sessionCtx.grantedFeatures.includes(key)) return true;
      return true;  // role passes — accessible at some tier
    })
    .map(([key, feature]) => ({
      key,
      tier:     feature.tier,
      surfaced: isVisible(key, sessionCtx),
    }));
}

module.exports = {
  FEATURE_REGISTRY,
  getTier,
  isVisible,
  isDiscoverable,
  getVisibleFeatures,
  getAllAccessibleFeatures,
};
