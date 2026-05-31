(function () {
  'use strict';
  var cfg = window.CRM_CONFIG;
  var _chart = null;

  var MONTHS = ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'];

  // Dummy metric series for fallback (aligned to kpi-data-pipelines.md canonical KPIs)
  var DUMMY_SERIES = {
    weighted_pipeline:       { label: 'Weighted Pipeline (PKR)', data: [2800000, 3100000, 2600000, 3400000, 3900000, 4280000] },
    lead_conversion_rate:    { label: 'Lead Conversion Rate (%)', data: [28, 31, 29, 33, 34, 33] },
    collection_rate:         { label: 'Collection Rate (%)',      data: [68, 72, 70, 75, 73, 73] },
    invoice_collection_rate: { label: 'Collection Rate (%)',      data: [68, 72, 70, 75, 73, 73] },
    mrr:                     { label: 'MRR (PKR)',                data: [285000, 295000, 310000, 320000, 330000, 335000] },
    won_deals:               { label: 'Won Deals',                data: [4, 6, 5, 7, 8, 6] },
    sla_breach_rate:         { label: 'SLA Breach Rate (%)',      data: [18, 14, 17, 12, 15, 16] },
    avg_deal_cycle:          { label: 'Avg Deal Cycle (days)',    data: [42, 38, 45, 36, 33, 35] },
    follow_up_completion:    { label: 'Follow-up Completion (%)', data: [72, 78, 74, 81, 83, 85] },
    booked_revenue:          { label: 'Booked Revenue (PKR)',     data: [980000, 1150000, 890000, 1320000, 1480000, 1620000] },
    quote_acceptance_rate:   { label: 'Quote Acceptance Rate (%)', data: [42, 45, 38, 51, 48, 52] },
    open_pipeline_value:     { label: 'Open Pipeline (PKR)',      data: [5200000, 5800000, 4900000, 6100000, 7200000, 7900000] },
    cash_collected:          { label: 'Cash Collected (PKR)',     data: [840000, 920000, 780000, 1050000, 1180000, 1290000] },
    subscription_churn_rate: { label: 'Churn Rate (%)',           data: [3.2, 2.8, 3.5, 2.1, 2.4, 2.2] },
  };

  function getSelectedMetrics() {
    return Array.from(document.querySelectorAll('#metric-chips input:checked')).map(function (el) { return el.dataset.metric; });
  }

  function getChartType() {
    var el = document.querySelector('[name="chart-type"]:checked');
    return el ? el.value : 'bar';
  }

  function buildChart(seriesData, labels) {
    var previewEl = document.getElementById('report-preview-chart');
    if (_chart) { try { _chart.destroy(); } catch (e) {} _chart = null; }
    if (!seriesData.length) {
      previewEl.innerHTML = '<div class="text-muted small text-center py-5">Select at least one metric to preview.</div>';
      return;
    }
    var chartType = getChartType();
    var opts = { chart: { height: 320, toolbar: { show: false } }, legend: { position: 'top' }, dataLabels: { enabled: false } };
    if (chartType === 'pie' || chartType === 'donut') {
      Object.assign(opts, { chart: Object.assign({}, opts.chart, { type: 'donut' }), series: seriesData[0].data, labels: labels });
    } else {
      Object.assign(opts, { chart: Object.assign({}, opts.chart, { type: chartType }), series: seriesData, xaxis: { categories: labels } });
      if (chartType === 'line') Object.assign(opts, { stroke: { curve: 'smooth', width: 2 }, markers: { size: 4 } });
      if (chartType === 'bar')  opts.plotOptions = { bar: { columnWidth: '55%', borderRadius: 4 } };
    }
    _chart = new ApexCharts(previewEl, opts);
    _chart.render();
  }

  function updateSummary(seriesData) {
    var names = seriesData.map(function (s) { return s.name; }).join(', ');
    document.getElementById('report-preview-summary').innerHTML =
      '<div class="d-flex flex-wrap gap-2 small text-muted">' +
      '<span>Metrics: <strong class="text-body">' + (names || '—') + '</strong></span>' +
      '<span>·</span><span>Group by: <strong class="text-body">Period (Month)</strong></span>' +
      '<span>·</span><span>Chart: <strong class="text-body">' + getChartType() + '</strong></span></div>';
  }

  function renderPreviewDummy() {
    var series = getSelectedMetrics().filter(function (m) { return DUMMY_SERIES[m]; }).slice(0, 3).map(function (m) {
      return { name: DUMMY_SERIES[m].label, data: DUMMY_SERIES[m].data };
    });
    buildChart(series, MONTHS);
    updateSummary(series);
  }

  function renderPreviewLive() {
    var selected = getSelectedMetrics().slice(0, 3);
    if (!selected.length) { buildChart([], MONTHS); updateSummary([]); return; }
    Promise.all(selected.map(function (m) {
      return CRM_API.reports.execute({ metric_key: m, group_by: 'period' })
        .catch(function () {
          var fb = DUMMY_SERIES[m] || { label: m, data: [0, 0, 0, 0, 0, 0] };
          return { data: { metric_key: m, label: fb.label, series: MONTHS.map(function (l, i) { return { label: l, value: fb.data[i] }; }) } };
        });
    })).then(function (results) {
      var series = results.map(function (r) {
        var d = r.data || r;
        return { name: d.label || d.metric_key, data: (d.series || []).map(function (p) { return p.value; }) };
      });
      buildChart(series, MONTHS);
      updateSummary(series);
    });
  }

  function renderPreview() {
    if (cfg && !cfg.DUMMY_MODE) { renderPreviewLive(); } else { renderPreviewDummy(); }
  }

  function wireSaveButton() {
    var $btn = $('button.btn-primary').filter(function () { return $(this).text().indexOf('Save Report') !== -1; });
    $btn.prop('disabled', false).removeAttr('title');
    $btn.off('click').on('click', function () {
      var name    = $('input[placeholder*="e.g."], input[placeholder*="Monthly"]').first().val() || 'Untitled Report';
      var metrics = getSelectedMetrics();
      var chart_type = getChartType();
      if (!metrics.length) { alert('Select at least one metric before saving.'); return; }
      var $b = $(this).prop('disabled', true).text('Saving…');
      CRM_API.reports.create({ name: name, metrics: metrics, group_by: 'period', chart_type: chart_type })
        .then(function () { $b.prop('disabled', false).text('Saved ✓'); setTimeout(function () { $b.text('Save Report'); }, 2500); })
        .catch(function () { $b.prop('disabled', false).text('Save Report'); });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    renderPreview();
    document.getElementById('btn-preview').addEventListener('click', renderPreview);
    document.querySelectorAll('#metric-chips input').forEach(function (el) { el.addEventListener('change', renderPreview); });
    document.querySelectorAll('[name="chart-type"]').forEach(function (el) { el.addEventListener('change', renderPreview); });

    if (cfg && !cfg.DUMMY_MODE) {
      wireSaveButton();
      CRM_API.reports.list().catch(function () {});
    }
  });
})();
