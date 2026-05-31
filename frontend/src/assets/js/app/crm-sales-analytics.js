/* Pakistan CRM — Sales Analytics (H-01) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function pkr(n) { return 'PKR ' + Number(Math.round(n)).toLocaleString('en-IN'); }

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

  function render(opps, leads, users, tasks, acts) {
    var TODAY = new Date().toISOString().substring(0, 10);

    var wonOpps    = opps.filter(function (o) { return o.stage === 'closed_won'; });
    var lostOpps   = opps.filter(function (o) { return o.stage === 'closed_lost'; });
    var closedOpps = wonOpps.length + lostOpps.length;
    var openOpps   = opps.filter(function (o) { return o.stage !== 'closed_won' && o.stage !== 'closed_lost'; });
    var winRate    = closedOpps > 0 ? Math.round((wonOpps.length / closedOpps) * 100) : 0;
    var wonLeads   = leads.filter(function (l) { return l.stage === 'won'; });
    var convRate   = leads.length > 0 ? Math.round((wonLeads.length / leads.length) * 100) + '%' : '0%';

    var fc = computeForecast(opps);

    $('#h01-weighted-pipeline').text(pkr(fc.weighted_value));
    $('#h01-win-rate').text(winRate + '%');
    $('#h01-win-rate-sub').text(wonOpps.length + ' won of ' + closedOpps + ' closed');
    $('#h01-lead-conversion').text(convRate);
    $('#h01-lead-conversion-sub').text(openOpps.length + ' opportunities open');
    $('#h01-open-opps').text(openOpps.length);
    $('#h01-open-opps-sub').text(pkr(openOpps.reduce(function (s, o) { return s + (o.amount || 0); }, 0)) + ' total value');

    var isDark  = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    var textClr = isDark ? '#adb5bd' : '#6c757d';
    var gridClr = isDark ? '#343a40' : '#e9ecef';

    /* Pipeline by Stage chart */
    var stages      = ['qualification','discovery','proposal','negotiation','closed_won','closed_lost'];
    var stageLabels = ['Qualification','Discovery','Proposal','Negotiation','Closed Won','Closed Lost'];
    var stageValues = stages.map(function (s) {
      return opps.filter(function (o) { return o.stage === s; }).reduce(function (sum, o) { return sum + (o.amount || 0); }, 0);
    });
    var pipelineEl = document.querySelector('#H01PipelineChart');
    if (pipelineEl && window.ApexCharts) {
      new ApexCharts(pipelineEl, {
        chart:   { type:'bar', height:260, toolbar:{show:false}, fontFamily:'Instrument Sans, sans-serif' },
        series:  [{ name:'Pipeline Value (PKR)', data: stageValues }],
        xaxis:   { categories: stageLabels, labels:{ style:{ colors:textClr, fontSize:'11px' } } },
        yaxis:   { labels:{ style:{ colors:textClr, fontSize:'11px' }, formatter:function (v) { return 'PKR ' + Number(Math.round(v / 1000)).toLocaleString() + 'k'; } } },
        plotOptions: { bar:{ borderRadius:4, columnWidth:'55%', distributed:true } },
        colors:  ['#17a2b8','#5955D1','#ffc107','#dc3545','#28a745','#6c757d'],
        dataLabels: { enabled:false }, grid:{ borderColor:gridClr }, legend:{ show:false },
        tooltip: { y:{ formatter:function (v) { return 'PKR ' + Number(Math.round(v)).toLocaleString('en-IN'); } } }
      }).render();
    }

    /* Forecast donut chart */
    var fcCats   = ['Pipeline','Best Case','Commit','Closed'];
    var fcValues = [fc.by_category.pipeline.total_value, fc.by_category.best_case.total_value, fc.by_category.commit.total_value, fc.by_category.closed.total_value];
    var forecastEl = document.querySelector('#H01ForecastChart');
    if (forecastEl && window.ApexCharts) {
      new ApexCharts(forecastEl, {
        chart:  { type:'donut', height:160, fontFamily:'Instrument Sans, sans-serif' },
        series: fcValues, labels: fcCats,
        colors: ['#17a2b8','#ffc107','#5955D1','#28a745'],
        legend: { position:'bottom', fontSize:'11px', labels:{ colors:textClr } },
        dataLabels: { enabled:false }, plotOptions:{ pie:{ donut:{ size:'65%' } } },
        tooltip: { y:{ formatter:function (v) { return 'PKR ' + Number(Math.round(v)).toLocaleString('en-IN'); } } }
      }).render();
    }

    /* Forecast detail */
    var fcHtml = [
      { label:'Weighted',  val:fc.weighted_value,                     cls:'primary' },
      { label:'Commit',    val:fc.by_category.commit.total_value,     cls:'success' },
      { label:'Best Case', val:fc.by_category.best_case.total_value,  cls:'warning' },
      { label:'Closed',    val:fc.by_category.closed.total_value,     cls:'info'    }
    ].map(function (r) {
      return '<div class="d-flex justify-content-between mb-1">' +
        '<small class="text-muted">' + r.label + '</small>' +
        '<small class="fw-semibold text-' + r.cls + '">' + pkr(r.val) + '</small></div>';
    }).join('');
    $('#h01-forecast-detail').html(fcHtml);

    /* Lead funnel chart */
    var leadStages = ['new','qualifying','proposal','negotiation','won','lost'];
    var leadLabels = ['New','Qualifying','Proposal','Negotiation','Won','Lost'];
    var leadCounts = leadStages.map(function (s) { return leads.filter(function (l) { return l.stage === s; }).length; });
    var funnelEl   = document.querySelector('#H01LeadFunnelChart');
    if (funnelEl && window.ApexCharts) {
      new ApexCharts(funnelEl, {
        chart:   { type:'bar', height:220, toolbar:{show:false}, fontFamily:'Instrument Sans, sans-serif' },
        series:  [{ name:'Leads', data: leadCounts }],
        xaxis:   { categories: leadLabels, labels:{ style:{ colors:textClr, fontSize:'12px' } } },
        yaxis:   { labels:{ style:{ colors:textClr, fontSize:'11px' } }, tickAmount: Math.max.apply(null, leadCounts) || 5, min:0 },
        plotOptions: { bar:{ borderRadius:4, columnWidth:'40%', distributed:true } },
        colors:  ['#5955D1','#17a2b8','#ffc107','#dc3545','#28a745','#6c757d'],
        dataLabels: { enabled:true, style:{ fontSize:'12px', fontWeight:'600' } },
        grid:    { borderColor:gridClr }, legend:{ show:false },
        tooltip: { y:{ formatter:function (v) { return v + ' lead' + (v === 1 ? '' : 's'); } } }
      }).render();
    }

    /* Rep performance table */
    var ROLE_CLR = { sales_rep:'primary', sales_manager:'info', admin:'danger' };
    var repRows  = users.map(function (u) {
      var ownedLeads   = leads.filter(function (l) { return l.owner_id === u.id; });
      var ownedOpps    = opps.filter(function (o) { return o.owner_id === u.id; });
      var wonOppsU     = ownedOpps.filter(function (o) { return o.stage === 'closed_won'; });
      var closedU      = wonOppsU.length + ownedOpps.filter(function (o) { return o.stage === 'closed_lost'; }).length;
      var winRateU     = closedU > 0 ? Math.round((wonOppsU.length / closedU) * 100) : 0;
      var userActs     = acts.filter(function (a) { return a.performed_by === u.id; });
      var overdueTasks = tasks.filter(function (t) {
        return t.owner_id === u.id && t.status !== 'completed' && t.due_at.substring(0, 10) < TODAY;
      });
      var roleCls = ROLE_CLR[u.role] || 'secondary';
      var avatarN = (parseInt((u.id || '0').replace(/\D/g, '') || '0', 10) % 5) + 1;
      return '<tr>' +
        '<td><div class="d-flex align-items-center justify-content-center gap-2">' +
        '<div class="avatar avatar-xs rounded-circle"><img src="assets/images/avatar/avatar' + avatarN + '.webp" alt=""></div>' +
        '<div><div class="fw-semibold small">' + u.display_name + '</div>' +
        '<span class="badge bg-' + roleCls + '-subtle text-' + roleCls + '" style="font-size:.65rem;">' + (u.role || '').replace(/_/g, ' ') + '</span></div></div></td>' +
        '<td class="text-center">' + ownedLeads.length + '</td>' +
        '<td class="text-center">' + ownedOpps.length + '</td>' +
        '<td class="text-center"><strong class="text-success">' + wonOppsU.length + '</strong></td>' +
        '<td class="text-center">' + winRateU + '%</td>' +
        '<td class="text-center">' + userActs.length + '</td>' +
        '<td class="text-center">' +
        (overdueTasks.length > 0 ? '<span class="badge bg-danger-subtle text-danger">' + overdueTasks.length + '</span>' : '<span class="badge bg-success-subtle text-success">0</span>') +
        '</td></tr>';
    });
    $('#h01-rep-table-body').html(repRows.join(''));

    /* CSV export */
    var exportBtn = document.getElementById('h01-export-btn');
    if (exportBtn) {
      exportBtn.addEventListener('click', function () {
        var csv = 'Rep,Leads Owned,Opps,Deals Won,Win Rate,Activities,Overdue Tasks\n';
        users.forEach(function (u) {
          var ol = leads.filter(function (l) { return l.owner_id === u.id; }).length;
          var oo = opps.filter(function (o) { return o.owner_id === u.id; }).length;
          var ow = opps.filter(function (o) { return o.owner_id === u.id && o.stage === 'closed_won'; }).length;
          var oc = opps.filter(function (o) { return o.owner_id === u.id && (o.stage === 'closed_won' || o.stage === 'closed_lost'); }).length;
          var wr = oc > 0 ? Math.round((ow / oc) * 100) : 0;
          var ua = acts.filter(function (a) { return a.performed_by === u.id; }).length;
          var ot = tasks.filter(function (t) { return t.owner_id === u.id && t.status !== 'completed' && t.due_at.substring(0, 10) < TODAY; }).length;
          csv += '"' + u.display_name + '",' + ol + ',' + oo + ',' + ow + ',' + wr + '%,' + ua + ',' + ot + '\n';
        });
        var link = document.createElement('a');
        link.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
        link.download = 'sales-analytics-' + new Date().toISOString().split('T')[0] + '.csv';
        link.click();
      });
    }
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.opportunities.list({ limit: 200 }),
      window.CRM_API.leads.list({ limit: 500 }),
      window.CRM_API.users.list(),
      window.CRM_API.tasks.list({ limit: 200 }),
      window.CRM_API.activities.list({ limit: 500 })
    ]).then(function (results) {
      render(results[0].data || [], results[1].data || [], results[2].data || [], results[3].data || [], results[4].data || []);
    }).catch(function () {
      render(
        (_d && _d.opportunities && _d.opportunities.data) || [],
        (_d && _d.leads && _d.leads.data) || [],
        (_d && _d.users && _d.users.data) || [],
        (_d && _d.tasks && _d.tasks.data) || [],
        (_d && _d.activities && _d.activities.data) || []
      );
    });
  } else {
    if (!_d) return;
    render(_d.opportunities.data, _d.leads.data, _d.users.data, _d.tasks.data, _d.activities.data);
  }

})();
