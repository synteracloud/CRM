/* Pakistan CRM — Workflows Dashboard (A-10) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var STATUS_BADGE = {
    succeeded:'<span class="badge bg-success">Succeeded</span>',
    failed:   '<span class="badge bg-danger">Failed</span>',
    retrying: '<span class="badge bg-warning text-dark">Retrying</span>',
    running:  '<span class="badge bg-info text-white">Running</span>',
  };

  function computeKpi(executions) {
    var total    = executions.length;
    var succeeded= executions.filter(function (e) { return e.status === 'succeeded'; }).length;
    var failed   = executions.filter(function (e) { return e.status === 'failed'; }).length;
    var retrying = executions.filter(function (e) { return e.status === 'retrying'; }).length;
    var rate     = total > 0 ? Math.round(succeeded / total * 100) : 0;
    return { execution_volume: total, success_rate: rate, failure_count: failed, retry_queue_depth: retrying };
  }

  function render(executions) {
    var kpi = computeKpi(executions);

    if (kpi.failure_count > 0) {
      var postureRow = document.getElementById('posture-row');
      if (postureRow) {
        postureRow.style.display = '';
        document.getElementById('posture-text').textContent =
          kpi.failure_count + ' workflow execution(s) failed. Review the retry queue below.';
      }
    }

    document.getElementById('kpi-volume').textContent  = kpi.execution_volume;
    document.getElementById('kpi-success').textContent = kpi.success_rate + '%';
    document.getElementById('kpi-retry').textContent   = kpi.retry_queue_depth;
    document.getElementById('kpi-failed').textContent  = kpi.failure_count;

    var failing = executions.filter(function (e) { return e.status === 'failed' || e.status === 'retrying'; });
    var queueEl = document.getElementById('retry-queue');
    if (queueEl) {
      queueEl.innerHTML = failing.length ? failing.map(function (e) {
        return '<div class="list-group-item d-flex align-items-center gap-3 py-2">' +
          '<i class="fi fi-rr-workflow text-muted"></i>' +
          '<div class="flex-grow-1 overflow-hidden">' +
          '<div class="fw-semibold text-truncate">' + (e.workflow_name || e.workflow_key || e.workflow_id) + '</div>' +
          '<div class="small text-muted">Step: ' + (e.failed_step || '—') + ' · ' + (e.trigger_event || '—') + '</div></div>' +
          (STATUS_BADGE[e.status] || e.status) + '</div>';
      }).join('') : '<div class="p-3 text-muted small">No failed executions.</div>';
    }

    /* Trend chart using static data (no trend endpoint) */
    var trend   = (_d && _d.workflowKpi && _d.workflowKpi.execution_trend) || [];
    var chartEl = document.getElementById('chart-workflow-trend');
    if (chartEl && window.ApexCharts) {
      new ApexCharts(chartEl, {
        chart:  { type:'bar', height:260, toolbar:{ show:false } },
        series: [
          { name:'Succeeded', data: trend.length ? trend.map(function (t) { return t.succeeded; }) : [kpi.execution_volume - kpi.failure_count] },
          { name:'Failed',    data: trend.length ? trend.map(function (t) { return t.failed; })    : [kpi.failure_count] }
        ],
        xaxis:  { categories: trend.length ? trend.map(function (t) { return t.day; }) : ['Today'] },
        colors: ['#0e9f6e','#f05252'],
        plotOptions: { bar:{ columnWidth:'50%', borderRadius:4 } },
        legend: { position:'top' }, dataLabels: { enabled:false },
      }).render();
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.workflows.runs.list({ limit: 200 })
        .then(function (res) { render(res.data || []); })
        .catch(function () { render((_d && _d.workflowExecutions && _d.workflowExecutions.data) || []); });
    } else {
      render((_d && _d.workflowExecutions && _d.workflowExecutions.data) || []);
    }
  });

})();
