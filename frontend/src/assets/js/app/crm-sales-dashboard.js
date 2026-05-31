/* Pakistan CRM — Sales Pipeline Dashboard (A-04) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var TARGET = 5500000;

  function pkr(n) { return 'PKR ' + Number(n).toLocaleString('en-IN'); }

  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function fmtDate(iso) {
    if (!iso) return '—';
    var p = iso.split('-');
    return MONTHS[parseInt(p[1], 10) - 1] + ' ' + parseInt(p[2], 10) + ', ' + p[0];
  }

  function computeForecast(opps) {
    var byCategory = { pipeline:{count:0,total_value:0}, best_case:{count:0,total_value:0}, commit:{count:0,total_value:0}, closed:{count:0,total_value:0}, omitted:{count:0,total_value:0} };
    var weighted   = 0;
    opps.forEach(function (o) {
      var cat = byCategory[o.forecast_category];
      if (cat) { cat.count++; cat.total_value += o.amount || 0; }
      weighted += (o.amount || 0) * (o.probability || 0) / 100;
    });
    return { weighted_value: Math.round(weighted), by_category: byCategory };
  }

  function render(opps, acts) {
    var TODAY          = new Date().toISOString().substring(0, 10);
    var SEVEN_DAYS_AGO = new Date(Date.now() - 7 * 86400000).toISOString().substring(0, 10);

    var activeOpps  = opps.filter(function (o) { return o.stage !== 'closed_won' && o.stage !== 'closed_lost'; });
    var overdueOpps = activeOpps.filter(function (o) { return o.close_date < TODAY; });

    var recentIds = {};
    acts.forEach(function (a) {
      if (a.entity_type === 'opportunity' && a.occurred_at.substring(0, 10) >= SEVEN_DAYS_AGO) {
        recentIds[a.entity_id] = true;
      }
    });
    var idleOpps = activeOpps.filter(function (o) { return !recentIds[o.opportunity_id]; });

    var idleCount = idleOpps.length;
    if (idleCount === 0) {
      $('#pipeline-posture-row').addClass('d-none');
    } else {
      $('#idle-deal-count').text(idleCount);
      $('#idle-deal-plural').text(idleCount === 1 ? ' has' : 's have');
    }

    var fc = computeForecast(opps);
    $('#kpi-weighted-pipeline').text(pkr(fc.weighted_value));
    $('#kpi-closed-won').text(pkr(fc.by_category.closed.total_value));
    $('#kpi-closed-won-count').text(fc.by_category.closed.count + ' deal' + (fc.by_category.closed.count === 1 ? '' : 's') + ' closed');
    $('#kpi-commit').text(pkr(fc.by_category.commit.total_value));
    $('#kpi-commit-count').text(fc.by_category.commit.count + ' deal' + (fc.by_category.commit.count === 1 ? '' : 's') + ' committed');

    $('#overdue-close-badge').text(overdueOpps.length + ' overdue');

    var stageBadgeCls = {
      qualification:'bg-info-subtle text-info', discovery:'bg-primary-subtle text-primary',
      proposal:'bg-warning-subtle text-warning', negotiation:'bg-danger-subtle text-danger'
    };
    var forecastBadgeCls = {
      pipeline:'bg-info-subtle text-info', best_case:'bg-warning-subtle text-warning', commit:'bg-primary-subtle text-primary'
    };

    var html;
    if (overdueOpps.length === 0) {
      html = '<div class="text-center py-4 text-muted small"><i class="fi fi-rr-badge-check fs-3 d-block mb-2 opacity-25"></i>No overdue close dates — pipeline is on track.</div>';
    } else {
      html = '<ul class="list-group list-group-flush">' +
        overdueOpps.map(function (o) {
          var daysOverdue = Math.floor((new Date(TODAY) - new Date(o.close_date)) / 86400000);
          var sc  = stageBadgeCls[o.stage]             || 'bg-secondary-subtle text-secondary';
          var fc2 = forecastBadgeCls[o.forecast_category] || 'bg-secondary-subtle text-secondary';
          return '<li class="list-group-item px-3 py-3">' +
            '<div class="d-flex align-items-start justify-content-between gap-3">' +
            '<div class="flex-grow-1 overflow-hidden"><div class="fw-semibold text-truncate">' + o.name + '</div>' +
            '<div class="text-muted small mt-1"><i class="fi fi-rr-building me-1"></i>' + (o.account_name || '—') +
            ' · <span class="badge ' + sc + ' ms-1">' + (o.stage || '').replace('_', ' ') + '</span>' +
            ' <span class="badge ' + fc2 + '">' + (o.forecast_category || '').replace('_', ' ') + '</span>' +
            '</div></div>' +
            '<div class="text-end flex-shrink-0">' +
            '<div class="fw-bold text-primary small">' + pkr(o.amount) + '</div>' +
            '<div class="text-danger small fw-semibold mt-1"><i class="fi fi-rr-clock me-1"></i>' + daysOverdue + 'd overdue</div>' +
            '<div class="text-muted small">' + (o.owner_id || '—') + '</div>' +
            '</div></div>' +
            '<div class="d-flex gap-2 mt-2">' +
            '<a href="app/opportunities-detail.html?id=' + o.opportunity_id + '" class="btn btn-xs btn-outline-primary waves-effect btn-sm py-0 px-2">Open Deal</a>' +
            '</div></li>';
        }).join('') + '</ul>';
    }
    $('#overdue-deals-list').html(html);

    /* Gap to target */
    var closedVal = fc.by_category.closed.total_value;
    var gap       = Math.max(0, TARGET - closedVal);
    var pct       = Math.min(100, Math.round((closedVal / TARGET) * 100));
    var bestCase  = fc.by_category.best_case.total_value;
    $('#gap-target-value').text(pkr(TARGET));
    $('#gap-closed-value').text(pkr(closedVal));
    $('#gap-remaining').text(gap > 0 ? pkr(gap) : 'Target Met');
    $('#gap-progress-bar').css('width', pct + '%');
    $('#gap-pct-label').text(pct + '%');
    $('#gap-best-case').text(pkr(bestCase) + ' best case');

    /* Stage velocity chart */
    var stageCounts = { qualification:0, discovery:0, proposal:0, negotiation:0 };
    activeOpps.forEach(function (o) { if (stageCounts.hasOwnProperty(o.stage)) stageCounts[o.stage]++; });
    var stageLabels = ['Qualification', 'Discovery', 'Proposal', 'Negotiation'];
    var stageValues = [stageCounts.qualification, stageCounts.discovery, stageCounts.proposal, stageCounts.negotiation];
    var stageColors = ['#17a2b8', '#5955D1', '#ffc107', '#dc3545'];

    var isDark  = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    var textClr = isDark ? '#adb5bd' : '#6c757d';
    var gridClr = isDark ? '#343a40' : '#e9ecef';

    var chartEl = document.querySelector('#StageVelocityChart');
    if (chartEl && window.ApexCharts) {
      new ApexCharts(chartEl, {
        chart: { type:'bar', height:240, toolbar:{show:false}, fontFamily:'Instrument Sans, sans-serif' },
        series: [{ name:'Deals', data: stageValues }],
        xaxis:  { categories: stageLabels, labels:{ style:{ colors:textClr, fontSize:'12px' } } },
        yaxis:  { title:{ text:'Active Deals', style:{ color:textClr, fontSize:'11px' } }, labels:{ style:{ colors:textClr, fontSize:'11px' } }, tickAmount: Math.max.apply(null, stageValues) || 5, min:0 },
        plotOptions: { bar:{ borderRadius:4, columnWidth:'45%', distributed:true } },
        colors: stageColors,
        dataLabels: { enabled:true, style:{ fontSize:'12px', fontWeight:'600' } },
        grid:   { borderColor: gridClr },
        legend: { show:false },
        tooltip: { y:{ formatter: function (v) { return v + ' deal' + (v === 1 ? '' : 's'); } } }
      }).render();
    }
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.opportunities.list({ limit: 200 }),
      window.CRM_API.activities.list({ limit: 500 })
    ]).then(function (results) {
      render(results[0].data || [], results[1].data || []);
    }).catch(function () {
      render((_d && _d.opportunities && _d.opportunities.data) || [], (_d && _d.activities && _d.activities.data) || []);
    });
  } else {
    if (!_d) return;
    render(_d.opportunities.data, _d.activities.data);
  }

})();
