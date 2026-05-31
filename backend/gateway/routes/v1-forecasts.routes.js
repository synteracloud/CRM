const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { requireScopes } = require('../middleware/auth-rbac');
const { forwardRequest } = require('../middleware/transport-forward');

const router = express.Router();

// Stage weights for weighted pipeline value calculation
const STAGE_WEIGHTS = {
  qualification: 0.10,
  discovery:     0.20,
  proposal:      0.40,
  negotiation:   0.70,
  closed_won:    1.00,
  closed_lost:   0.00,
};

// ── GET /forecasts — summary forecast for current pipeline ────────────────────
router.get('/', requestValidationMiddleware(), requireScopes(['forecasts.read']), (req, res) => {
  const now = new Date().toISOString();
  return res.json({
    data: {
      period:        'current_quarter',
      generated_at:  now,
      weighted_value: 0,
      by_category: {
        pipeline:  { count: 0, total_value: 0 },
        best_case: { count: 0, total_value: 0 },
        commit:    { count: 0, total_value: 0 },
        closed:    { count: 0, total_value: 0 },
      },
      stage_breakdown: Object.keys(STAGE_WEIGHTS).map((stage) => ({
        stage,
        weight:            STAGE_WEIGHTS[stage],
        opportunity_count: 0,
        total_value:       0,
        weighted:          0,
      })),
    },
    meta: { request_id: req.request_id || null },
  });
});

router.post('/model', requestValidationMiddleware(), requireScopes(['forecasts.read']), forwardRequest);
router.post('/aggregate', requestValidationMiddleware(), requireScopes(['forecasts.read']), forwardRequest);

module.exports = router;
