/* Pakistan CRM — Workflow Analytics (H-05) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var STATUS_BADGE = { succeeded:'<span class="badge bg-success">Succeeded</span>', failed:'<span class="badge bg-danger">Failed</span>', retrying:'<span class="badge bg-warning text-dark">Retrying</span>', running:'<span class="badge bg-info text-white">Running</span>' };

  function render(executions) {
    if (typeof flatpickr !== 'undefined') {
      flatpickr('#date-range-picker', { mode:'range', dateFormat:'d M Y', defaultDate:[new Date(Date.now() - 29 * 86400000), new Date()] });
    }

    var total    = executions.length;
    var succeeded= executions.filter(function (e) { return e.status === 'succeeded'; }).length;
    var failed   = executions.filter(function (e) { return e.status === 'failed'; }).length;
    var retrying = executions.filter(function (e) { return e.status === 'retrying'; }).length;
    var rate     = total > 0 ? Math.round(succeeded / total * 100) : 0;

    document.getElementById('kpi-volume').textContent  = total;
    document.getElementById('kpi-success').textContent = rate + '%';
    document.getElementById('kpi-failed').textContent  = failed;
    document.getElementById('kpi-retry').textContent   = retrying;

    var kpi    = (_d && _d.workflowKpi) || {};
    var trend  = kpi.execution_trend || [];

    var chartVolEl = document.getElementById('chart-volume');
    if (chartVolEl && window.ApexCharts) {
      new ApexCharts(chartVolEl, {
        chart: { type:'bar', height:260, toolbar:{ show:false } },
        series: [
          { name:'Succeeded', data: trend.length ? trend.map(function (t) { return t.succeeded; }) : [succeeded] },
          { name:'Failed',    data: trend.length ? trend.map(function (t) { return t.failed;    }) : [failed]    }
        ],
        xaxis:  { categories: trend.length ? trend.map(function (t) { return t.day; }) : ['Today'] },
        colors: ['#0e9f6e','#f05252'],
        plotOptions: { bar:{ columnWidth:'55%', borderRadius:4 } },
        legend: { position:'top' }, dataLabels: { enabled:false },
      }).render();
    }

    var failMap = {};
    executions.filter(function (e) { return e.status === 'failed'; }).forEach(function (e) {
      var name = e.workflow_name || e.workflow_key || e.workflow_id;
      failMap[name] = (failMap[name] || 0) + 1;
    });
    var chartFailEl = document.getElementById('chart-failure');
    if (chartFailEl && window.ApexCharts && Object.keys(failMap).length > 0) {
      new ApexCharts(chartFailEl, {
        chart: { type:'bar', height:260, toolbar:{ show:false } },
        series: [{ name:'Failures', data: Object.values(failMap) }],
        xaxis:  { categories: Object.keys(failMap) },
        colors: ['#f05252'],
        plotOptions: { bar:{ horizontal:true, borderRadius:4 } },
        dataLabels: { enabled:true },
      }).render();
    }

    $('#dt_WorkflowExec').DataTable({
      data: executions, pageLength: 10, order: [[6,'desc']],
      columns: [
        { data:'execution_id',  className:'dt-body-center', render:function (id) { return '<a href="app/workflow-run-detail.html?id=' + id + '" class="fw-semibold font-monospace small">' + id + '</a>'; } },
        { data:'workflow_name', className:'dt-body-left',   render:function (n) { return '<span class="small">' + (n || '—') + '</span>'; }, defaultContent:'—' },
        { data:'status',        className:'dt-body-center', render:function (s) { return STATUS_BADGE[s] || s; } },
        { data:'trigger_event', className:'dt-body-center', render:function (t) { return '<code class="small">' + (t || '—') + '</code>'; }, defaultContent:'—' },
        { data:'duration_ms',   className:'dt-body-center', render:function (ms) { return ms ? ms + 'ms' : '—'; }, defaultContent:'—' },
        { data:'failed_step',   className:'dt-body-center', render:function (s) { return s ? '<code class="small text-danger">' + s + '</code>' : '—'; }, defaultContent:'—' },
        { data:'started_at',    className:'dt-body-center', render:function (t) { return t ? new Date(t).toLocaleTimeString('en-PK', { hour:'2-digit', minute:'2-digit' }) : '—'; }, defaultContent:'—' },
      ],
    });
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
