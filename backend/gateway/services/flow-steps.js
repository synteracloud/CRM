'use strict';

/**
 * ≤2 Steps enforcement registry — P-012.
 *
 * Docs: docs/ui-foundations.md §6 — Interaction Simplicity Rule
 *       docs/adoption-ux.md §4 — "every core action in ≤2 steps"
 *
 * A "step" is any deliberate user action: tap/click, form submission,
 * modal confirmation, or navigation to a new screen.
 * Scrolling within the same screen is NOT a step.
 *
 * Usage (design-time validation)::
 *   const { validate, FLOW_REGISTRY } = require('./flow-steps');
 *   const result = validate('record_cash_payment', ['open_invoice', 'tap_record', 'submit']);
 *   // result.valid === true, result.steps === 2
 *
 * Usage (runtime step tracking)::
 *   const tracker = createFlowTracker('record_cash_payment');
 *   tracker.step('open_invoice');
 *   tracker.step('tap_record');
 *   tracker.step('submit');
 *   tracker.finish();  // throws if steps > max_steps
 */

// ── Flow registry ──────────────────────────────────────────────────────────────
// Each entry documents the canonical step sequence and max allowed steps.
// Docs: docs/ui-foundations.md §6 table

const FLOW_REGISTRY = Object.freeze({
  capture_lead_whatsapp: {
    description:  'Capture a lead from WhatsApp inbound message',
    max_steps:    0,
    steps:        [],   // fully automatic — agent does nothing
    note:         'Auto-capture via webhook; 0 steps by design',
  },
  log_followup_complete: {
    description:  'Mark a follow-up task as done',
    max_steps:    1,
    steps:        ['tap_done_on_task'],
  },
  snooze_followup: {
    description:  'Snooze a follow-up task',
    max_steps:    1,
    steps:        ['tap_snooze_select_time'],   // picker counts as part of the tap
  },
  create_manual_lead: {
    description:  'Create a new lead manually',
    max_steps:    2,
    steps:        ['tap_new_lead_enter_phone', 'submit'],
  },
  record_cash_payment: {
    description:  'Record a cash payment against an invoice',
    max_steps:    2,
    steps:        ['open_invoice_tap_record', 'enter_amount_submit'],
  },
  advance_deal_stage: {
    description:  'Move a deal to the next pipeline stage',
    max_steps:    1,
    steps:        ['tap_stage_chip_select_next'],
  },
  send_followup_message: {
    description:  'Send a follow-up WhatsApp message using a template',
    max_steps:    2,
    steps:        ['tap_send_followup', 'confirm_template'],
  },
});

// ── Validation ─────────────────────────────────────────────────────────────────

/**
 * Validate that a proposed step sequence for a flow respects the ≤2 step rule.
 *
 * @param {string}   flowKey   — key from FLOW_REGISTRY
 * @param {string[]} stepsTaken — array of step names taken by this implementation
 * @returns {{ valid: boolean, steps: number, max: number, violations: string[] }}
 */
function validate(flowKey, stepsTaken = []) {
  const flow = FLOW_REGISTRY[flowKey];
  if (!flow) {
    return { valid: false, steps: stepsTaken.length, max: null, violations: [`Unknown flow: ${flowKey}`] };
  }

  const violations = [];
  if (stepsTaken.length > flow.max_steps) {
    violations.push(
      `Flow "${flowKey}" requires ${stepsTaken.length} steps but max is ${flow.max_steps}. ` +
      `Excess steps: ${stepsTaken.slice(flow.max_steps).join(', ')}`,
    );
  }

  return {
    valid:      violations.length === 0,
    steps:      stepsTaken.length,
    max:        flow.max_steps,
    violations,
  };
}

/**
 * Create a stateful tracker for a single flow execution.
 * Call .step(name) for each user action; call .finish() at end.
 * Throws FlowStepViolationError if steps exceed max.
 */
function createFlowTracker(flowKey) {
  const flow = FLOW_REGISTRY[flowKey];
  if (!flow) throw new Error(`Unknown flow key: ${flowKey}`);

  const taken = [];

  return {
    /** Record a step. */
    step(name) {
      taken.push(name);
    },

    /** Validate and return result.  Throws on violation. */
    finish() {
      const result = validate(flowKey, taken);
      if (!result.valid) {
        const err = new Error(result.violations.join('; '));
        err.name  = 'FlowStepViolationError';
        err.flow  = flowKey;
        err.steps = taken;
        throw err;
      }
      return result;
    },

    /** Non-throwing validation snapshot. */
    snapshot() {
      return validate(flowKey, taken);
    },
  };
}

module.exports = { FLOW_REGISTRY, validate, createFlowTracker };
