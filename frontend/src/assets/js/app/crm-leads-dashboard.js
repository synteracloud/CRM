/* Pakistan CRM — Lead Funnel Dashboard (A-02) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function pkr(n) { return 'PKR ' + Number(n).toLocaleString('en-IN'); }

  function computeKpi(leads) {
    var today    = new Date().toISOString().substring(0, 10);
    var weekAgo  = new Date(Date.now() - 7 * 86400000).toISOString().substring(0, 10);
    var total    = leads.length;
    var newWeek  = leads.filter(function (l) { return l.created_at && l.created_at.substring(0, 10) >= weekAgo; }).length;
    var won      = leads.filter(function (l) { return l.stage === 'won'; }).length;
    var qualified= leads.filter(function (l) { return ['qualifying','proposal','negotiation','won'].indexOf(l.stage) !== -1; }).length;
    var opps     = leads.filter(function (l) { return ['proposal','negotiation','won'].indexOf(l.stage) !== -1; }).length;
    var convRate = total > 0 ? Math.round((won / total) * 100) + '%' : '0%';
    return { total: total, new_week: newWeek, conversion_rate: convRate, qualified: qualified, opportunities: opps };
  }

  function render(leads) {
    var TODAY   = new Date().toISOString().substring(0, 10);
    var THREE_DAYS_AGO = new Date(Date.now() - 3 * 86400000).toISOString().substring(0, 10);

    var idleLeads = leads.filter(function (l) {
      var closed  = l.stage === 'won' || l.stage === 'lost';
      var updDate = l.updated_at ? l.updated_at.substring(0, 10) : '2000-01-01';
      return !closed && updDate < THREE_DAYS_AGO;
    });

    var idleCount = idleLeads.length;
    if (idleCount === 0) {
      $('#lead-posture-row').addClass('d-none');
    } else {
      $('#idle-lead-count').text(idleCount);
      $('#idle-lead-plural').text(idleCount === 1 ? ' is' : 's are');
    }

    var kpi = computeKpi(leads);
    $('#kpi-total-leads').text(Number(kpi.total).toLocaleString());
    $('#kpi-new-week').text(Number(kpi.new_week).toLocaleString());
    $('#kpi-conversion-rate').text(kpi.conversion_rate);
    $('#kpi-opportunities').text(Number(kpi.opportunities).toLocaleString());
    $('#kpi-avg-latency').text('—');

    var wonCount = leads.filter(function (l) { return l.stage === 'won'; }).length;
    var convPct  = leads.length > 0 ? Math.round((wonCount / leads.length) * 100) : 0;

    $('#funnel-total').text(Number(kpi.total).toLocaleString());
    $('#funnel-qualified').text(Number(kpi.qualified).toLocaleString());
    $('#funnel-opps').text(Number(kpi.opportunities).toLocaleString());
    $('#funnel-won').text(wonCount);
    $('#funnel-progress').css('width', convPct + '%');
    $('#funnel-rate-label').text(kpi.conversion_rate + ' conversion rate');

    $('#idle-queue-badge').text(idleLeads.length);

    var STAGE_CLS = { new:'primary', qualifying:'info', proposal:'warning', negotiation:'danger', won:'success', lost:'secondary' };
    var listHtml;
    if (idleLeads.length === 0) {
      listHtml = '<div class="text-center py-4 text-muted small"><i class="fi fi-rr-badge-check fs-3 d-block mb-2 opacity-25"></i>No idle leads — execution is on track.</div>';
    } else {
      listHtml = '<ul class="list-group list-group-flush">' +
        idleLeads.slice(0, 10).map(function (l) {
          var updDate  = l.updated_at ? l.updated_at.substring(0, 10) : '2000-01-01';
          var daysOld  = Math.floor((new Date(TODAY) - new Date(updDate)) / 86400000);
          var stageCls = STAGE_CLS[l.stage] || 'secondary';
          return '<li class="list-group-item px-3 py-3">' +
            '<div class="d-flex align-items-start justify-content-between gap-3">' +
            '<div class="flex-grow-1">' +
            '<div class="fw-semibold">' + l.contact_name + '</div>' +
            '<div class="text-muted small mt-1">' +
            '<i class="fi fi-rr-phone-call me-1"></i>' + (l.contact_phone_e164 || '—') +
            ' · <span class="badge bg-' + stageCls + '-subtle text-' + stageCls + ' ms-1">' + l.stage + '</span>' +
            '</div></div>' +
            '<div class="text-end">' +
            '<div class="fw-bold text-primary small">' + pkr(l.estimated_value || 0) + '</div>' +
            '<div class="text-warning small fw-semibold mt-1"><i class="fi fi-rr-clock me-1"></i>' + daysOld + 'd idle</div>' +
            '</div></div>' +
            '<div class="d-flex gap-2 mt-2">' +
            '<a href="app/leads-detail.html?id=' + l.lead_id + '" class="btn btn-xs btn-outline-primary btn-sm py-0 px-2 waves-effect">Open Lead</a>' +
            '</div></li>';
        }).join('') + '</ul>';
    }
    $('#idle-leads-list').html(listHtml);

    /* Stage distribution chart */
    var isDark  = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    var textClr = isDark ? '#adb5bd' : '#6c757d';
    var gridClr = isDark ? '#343a40' : '#e9ecef';
    var stageOrder  = ['new', 'qualifying', 'proposal', 'negotiation', 'won', 'lost'];
    var stageCounts = {};
    stageOrder.forEach(function (s) { stageCounts[s] = 0; });
    leads.forEach(function (l) { if (stageCounts.hasOwnProperty(l.stage)) stageCounts[l.stage]++; });

    var chartEl = document.querySelector('#LeadStageChart');
    if (chartEl && window.ApexCharts) {
      new ApexCharts(chartEl, {
        chart:   { type: 'bar', height: 240, toolbar: { show: false }, fontFamily: 'Instrument Sans, sans-serif' },
        series:  [{ name: 'Leads', data: stageOrder.map(function (s) { return stageCounts[s]; }) }],
        xaxis:   { categories: ['New', 'Qualifying', 'Proposal', 'Negotiation', 'Won', 'Lost'], labels: { style: { colors: textClr, fontSize: '12px' } } },
        yaxis:   { labels: { style: { colors: textClr, fontSize: '11px' } }, tickAmount: 4, min: 0 },
        plotOptions: { bar: { borderRadius: 4, columnWidth: '50%', distributed: true } },
        colors:  ['#5955D1', '#17a2b8', '#ffc107', '#dc3545', '#28a745', '#6c757d'],
        dataLabels: { enabled: true, style: { fontSize: '12px', fontWeight: '600' } },
        grid:    { borderColor: gridClr },
        legend:  { show: false },
        tooltip: { y: { formatter: function (v) { return v + ' lead' + (v === 1 ? '' : 's'); } } }
      }).render();
    }
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.leads.list({ limit: 500 })
      .then(function (res) { render(res.data || []); })
      .catch(function () { render((_d && _d.leads && _d.leads.data) || []); });
  } else {
    if (!_d) return;
    render(_d.leads.data);
  }

})();
