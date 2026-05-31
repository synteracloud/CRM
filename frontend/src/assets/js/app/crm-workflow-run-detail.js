/* Pakistan CRM — Workflow Run Detail (C-10) */

(function () {
  'use strict';

  var cfg    = window.CRM_CONFIG;
  var _d     = window.CRM_DUMMY;
  var execId = new URLSearchParams(window.location.search).get('id') || null;

  var STATUS_BADGE = {
    succeeded:'<span class="badge bg-success">Succeeded</span>',
    failed:   '<span class="badge bg-danger">Failed</span>',
    retrying: '<span class="badge bg-warning text-dark">Retrying</span>',
    running:  '<span class="badge bg-info text-white">Running</span>',
  };
  var STEP_ICONS = {
    succeeded:'<span class="text-success"><i class="fi fi-rr-check-circle"></i></span>',
    failed:   '<span class="text-danger"><i class="fi fi-rr-x-circle"></i></span>',
    skipped:  '<span class="text-muted"><i class="fi fi-rr-minus-circle"></i></span>',
  };

  var DEMO_STEPS = [
    { name:'check_idle_threshold', status:'succeeded', duration_ms:120,  input:'{ "lead_id": "l-001", "idle_days": 7 }', output:'{ "threshold_met": true }' },
    { name:'load_lead_record',     status:'succeeded', duration_ms:340,  input:'{ "lead_id": "l-001" }',                  output:'{ "lead": {...} }' },
    { name:'escalate_to_manager',  status:'failed',    duration_ms:1640, input:'{ "owner_id": "u-001", "manager_id": "u-003" }', output:'ERROR: manager notification failed — SMTP timeout' },
  ];

  function render(exec) {
    if (!exec) {
      if (_d && _d.workflowExecutions && _d.workflowExecutions.data[6]) render(_d.workflowExecutions.data[6]);
      return;
    }

    document.getElementById('bc-exec-id').textContent          = exec.execution_id;
    document.getElementById('exec-id').textContent             = exec.execution_id;
    document.getElementById('exec-workflow-name').textContent  = exec.workflow_name || exec.workflow_key || '—';
    document.getElementById('exec-status-badge').innerHTML     = STATUS_BADGE[exec.status] || exec.status;
    document.getElementById('exec-trigger').textContent        = exec.trigger_event || '—';
    document.getElementById('exec-duration').textContent       = exec.duration_ms ? exec.duration_ms + 'ms' : '—';
    document.getElementById('exec-steps').textContent          = exec.step_count || DEMO_STEPS.length;

    var btnRetry = document.getElementById('btn-retry');
    if (btnRetry) {
      if (!['failed','retrying'].includes(exec.status)) {
        btnRetry.style.display = 'none';
      } else {
        btnRetry.addEventListener('click', function () {
          if (!window.confirm('Retry this execution?')) return;
          btnRetry.disabled = true;
          window.CRM_API.workflows.runs.retry(exec.execution_id)
            .then(function () { btnRetry.textContent = 'Retried'; btnRetry.className = 'btn btn-sm btn-success'; })
            .catch(function () { btnRetry.disabled = false; });
        });
      }
    }

    var steps = exec.step_log || DEMO_STEPS;

    var logEl = document.getElementById('exec-log-list');
    if (logEl) {
      logEl.innerHTML = steps.map(function (s) {
        return '<div class="d-flex align-items-start gap-3 py-2 border-bottom">' +
          '<div class="mt-1">' + (STEP_ICONS[s.status] || '') + '</div>' +
          '<div class="flex-grow-1"><div class="fw-semibold font-monospace small">' + s.name + '</div>' +
          '<div class="small text-muted">Duration: ' + (s.duration_ms || 0) + 'ms</div></div>' +
          (STATUS_BADGE[s.status] || s.status) + '</div>';
      }).join('') || '<div class="text-muted small">No log entries.</div>';
    }

    var stepsEl = document.getElementById('exec-steps-list');
    if (stepsEl) {
      stepsEl.innerHTML = steps.map(function (s, i) {
        return '<div class="card mb-2" style="height:auto"><div class="card-body py-2">' +
          '<div class="d-flex align-items-center gap-2 mb-1">' +
          '<span class="badge bg-secondary-subtle text-secondary">Step ' + (i + 1) + '</span>' +
          '<span class="fw-semibold font-monospace small">' + s.name + '</span>' + STATUS_BADGE[s.status] + '</div>' +
          '<div class="row small">' +
          '<div class="col-6"><span class="text-muted">Input:</span><pre class="mb-0 small bg-light rounded p-1 mt-1">' + (s.input || '{}') + '</pre></div>' +
          '<div class="col-6"><span class="text-muted">Output:</span><pre class="mb-0 small bg-light rounded p-1 mt-1">' + (s.output || '{}') + '</pre></div>' +
          '</div></div></div>';
      }).join('');
    }

    var failedStep = steps.find(function (s) { return s.status === 'failed'; });
    var errEl = document.getElementById('exec-error-detail');
    if (errEl) {
      errEl.innerHTML = failedStep
        ? '<div class="alert alert-danger mb-3"><strong>Step Failed:</strong> <code>' + failedStep.name + '</code></div>' +
          '<pre class="bg-light rounded p-3 small">' + failedStep.output + '</pre>' +
          '<div class="small text-muted mt-2">Error policy: <strong>fail_fast</strong> — downstream steps halted.</div>'
        : '<div class="text-muted small">No error details.</div>';
    }

    var summaryEl = document.getElementById('exec-summary');
    if (summaryEl) {
      summaryEl.innerHTML = '<dl class="row mb-0 small">' +
        '<dt class="col-6 text-muted">Workflow</dt><dd class="col-6 fw-semibold">' + (exec.workflow_key || exec.workflow_id || '—') + '</dd>' +
        '<dt class="col-6 text-muted">Started</dt><dd class="col-6">' + (exec.started_at ? new Date(exec.started_at).toLocaleTimeString('en-PK') : '—') + '</dd>' +
        '<dt class="col-6 text-muted">Ended</dt><dd class="col-6">' + (exec.ended_at ? new Date(exec.ended_at).toLocaleTimeString('en-PK') : '—') + '</dd>' +
        '<dt class="col-6 text-muted">Steps</dt><dd class="col-6">' + (exec.step_count || steps.length) + '</dd>' +
        '<dt class="col-6 text-muted">Failed Step</dt><dd class="col-6 text-danger">' + (exec.failed_step || '—') + '</dd></dl>';
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      var prom = execId
        ? window.CRM_API.workflows.runs.get(execId).catch(function () { return { data: null }; })
        : Promise.resolve({ data: null });
      prom.then(function (res) {
        var exec = res.data;
        if (!exec && _d && _d.workflowExecutions) exec = _d.workflowExecutions.data[6];
        render(exec);
      });
    } else {
      if (!_d) return;
      var exec = execId
        ? (_d.workflowExecutions.data.filter(function (e) { return e.execution_id === execId; })[0] || _d.workflowExecutions.data[6])
        : _d.workflowExecutions.data[6];
      render(exec);
    }
  });

})();
