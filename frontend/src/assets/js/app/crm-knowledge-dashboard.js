/* Pakistan CRM — Knowledge Dashboard (A-09) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var CAT_BADGE = {
    billing:         '<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Billing</span>',
    technical:       '<span class="badge bg-danger-subtle text-danger border border-danger-subtle">Technical</span>',
    how_to:          '<span class="badge bg-info-subtle text-info border border-info-subtle">How-To</span>',
    getting_started: '<span class="badge bg-success-subtle text-success border border-success-subtle">Getting Started</span>',
  };

  function render(articles) {
    var published  = articles.filter(function (a) { return a.status === 'published'; });
    var deflection = articles.reduce(function (s, a) { return s + (a.deflection_count || 0); }, 0);
    var total      = articles.length;
    var stale      = articles.filter(function (a) { return a.stale; });
    var zeroView   = articles.filter(function (a) { return !a.view_count; });
    var deflRate   = total > 0 ? Math.round(deflection / (deflection + Math.max(1, total)) * 100) : 0;

    document.getElementById('kpi-published').textContent   = published.length;
    document.getElementById('kpi-deflection').textContent  = deflRate + '%';
    document.getElementById('kpi-stale').textContent       = stale.length;
    document.getElementById('kpi-zero-view').textContent   = zeroView.length;

    var needsWork = articles.filter(function (a) { return a.stale || !a.view_count; });
    var queueEl   = document.getElementById('stale-queue');
    if (queueEl) {
      queueEl.innerHTML = needsWork.length ? needsWork.map(function (a) {
        return '<a href="app/knowledge-article.html?id=' + a.article_id + '" class="list-group-item list-group-item-action d-flex align-items-start gap-3 py-2">' +
          '<i class="fi fi-rr-book-alt text-muted mt-1"></i>' +
          '<div class="flex-grow-1 overflow-hidden">' +
          '<div class="fw-semibold text-truncate">' + a.title + '</div>' +
          '<div class="d-flex gap-2 mt-1">' + (CAT_BADGE[a.category] || a.category) +
          (a.stale ? '<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Stale</span>' : '') +
          (!a.view_count ? '<span class="badge bg-secondary-subtle text-secondary">0 views</span>' : '') +
          '</div></div></a>';
      }).join('') : '<div class="p-3 text-muted small">All articles are current and viewed.</div>';
    }

    var kpi    = (_d && _d.knowledgeKpi) || {};
    var trend  = kpi.article_adoption_trend || [];
    var chartEl = document.getElementById('chart-adoption');
    if (chartEl && window.ApexCharts && trend.length > 0) {
      new ApexCharts(chartEl, {
        chart: { type:'area', height:260, toolbar:{ show:false } },
        series: [{ name:'Article Views', data: trend.map(function (t) { return t.views; }) }],
        xaxis:  { categories: trend.map(function (t) { return t.month; }) },
        colors: ['#3f83f8'],
        stroke: { curve:'smooth', width:2 },
        fill:   { type:'gradient', gradient:{ shadeIntensity:1, opacityFrom:0.35, opacityTo:0.0 } },
        dataLabels: { enabled:false },
      }).render();
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.knowledge.list({ limit: 200 })
        .then(function (res) { render(res.data || []); })
        .catch(function () { render((_d && _d.knowledgeArticles && _d.knowledgeArticles.data) || []); });
    } else {
      render((_d && _d.knowledgeArticles && _d.knowledgeArticles.data) || []);
    }
  });

})();
