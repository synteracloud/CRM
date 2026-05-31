/* Pakistan CRM — AI Insights (M-02) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var STAGE_PROB = { qualification:35, discovery:45, proposal:55, negotiation:75, closed_won:100, closed_lost:0, new:10, qualifying:25, won:100, lost:0 };

  var FEATURE_WEIGHTS = [
    { label:'Deal Stage',              weight:28, desc:'Current pipeline stage at scoring time' },
    { label:'Follow-up Attempts',      weight:18, desc:'Number of logged follow-up contacts' },
    { label:'Estimated Deal Value',    weight:14, desc:'PKR value of opportunity' },
    { label:'Days Since Last Contact', weight:12, desc:'Recency signal — negative weight if stale' },
    { label:'Email Opens',             weight:8,  desc:'Engagement signal from outbound emails' },
    { label:'Source Quality Score',    weight:7,  desc:'Inbound vs cold-outreach weighting' },
    { label:'Account Tier',            weight:6,  desc:'Enterprise/SMB/Startup coefficient' },
  ];

  function pkr(n) { return 'PKR ' + Math.round(n).toLocaleString('en-PK'); }

  function buildWinProbChart(opps) {
    var probs   = opps.map(function (o) { return STAGE_PROB[o.stage] || STAGE_PROB[o.forecast_category] || 40; });
    var buckets = [0, 0, 0, 0];
    probs.forEach(function (p) {
      if      (p <= 25) buckets[0]++;
      else if (p <= 50) buckets[1]++;
      else if (p <= 75) buckets[2]++;
      else              buckets[3]++;
    });
    var chartEl = document.getElementById('chart-win-prob');
    if (chartEl && window.ApexCharts) {
      new ApexCharts(chartEl, {
        chart:  { type:'bar', height:220, toolbar:{ show:false }, fontFamily:'Instrument Sans, sans-serif' },
        series: [{ name:'Opportunities', data: buckets }],
        xaxis:  { categories:['0–25%','26–50%','51–75%','76–100%'], labels:{ style:{ fontSize:'12px' } } },
        colors: ['#5955D1'],
        plotOptions: { bar:{ borderRadius:4, columnWidth:'55%' } },
        dataLabels: { enabled:false }, grid:{ borderColor:'#f3f4f6' },
        tooltip: { y:{ formatter:function (v) { return v + ' opps'; } } },
      }).render();
    }
  }

  function buildChurnChart(churns) {
    var high   = churns.filter(function (c) { return c.risk_band === 'high'; }).length;
    var medium = churns.filter(function (c) { return c.risk_band === 'medium'; }).length;
    var low    = churns.length - high - medium;
    var chartEl = document.getElementById('chart-churn');
    if (chartEl && window.ApexCharts) {
      new ApexCharts(chartEl, {
        chart:  { type:'donut', height:220, fontFamily:'Instrument Sans, sans-serif' },
        series: [high || 3, medium || 5, low || 8],
        labels: ['High Risk','Medium Risk','Low Risk'],
        colors: ['#ef4444','#f59e0b','#10b981'],
        legend: { position:'bottom', fontSize:'12px' },
        dataLabels: { formatter:function (val, opts) { return opts.w.globals.labels[opts.seriesIndex] + ': ' + opts.w.globals.series[opts.seriesIndex]; } },
        plotOptions: { pie:{ donut:{ size:'65%', labels:{ show:true, total:{ show:true, label:'Accounts', fontSize:'12px', color:'#6b7280' } } } } },
        tooltip: { y:{ formatter:function (v) { return v + ' accounts'; } } },
      }).render();
    }
  }

  function buildClvChart(estimates, opps) {
    var entries;
    if (estimates.length > 0) {
      entries = estimates.slice(0, 8).map(function (e) { return { name: e.account_id, clv: e.estimated_clv || 0 }; });
    } else {
      var byAccount = {};
      opps.forEach(function (o) {
        var acc = o.account_name || 'Unknown';
        byAccount[acc] = (byAccount[acc] || 0) + (o.estimated_value || o.amount || 0);
      });
      entries = Object.entries(byAccount).map(function (kv) { return { name: kv[0], clv: Math.round(kv[1] * 3.2) }; }).sort(function (a, b) { return b.clv - a.clv; }).slice(0, 8);
    }
    var chartEl = document.getElementById('chart-clv');
    if (chartEl && window.ApexCharts) {
      new ApexCharts(chartEl, {
        chart:  { type:'bar', height:260, toolbar:{ show:false }, fontFamily:'Instrument Sans, sans-serif' },
        series: [{ name:'Est. CLV (PKR)', data: entries.map(function (e) { return e.clv; }) }],
        xaxis:  { categories: entries.map(function (e) { return e.name; }), labels:{ style:{ fontSize:'11px' } } },
        colors: ['#8b5cf6'],
        plotOptions: { bar:{ borderRadius:4, columnWidth:'60%' } },
        dataLabels: { enabled:false }, grid:{ borderColor:'#f3f4f6' },
        tooltip: { y:{ formatter:function (v) { return 'PKR ' + v.toLocaleString('en-PK'); } } },
      }).render();
    }
  }

  function renderFeatureWeights() {
    var max = FEATURE_WEIGHTS[0].weight;
    var el  = document.getElementById('feature-weights');
    if (!el) return;
    el.innerHTML = FEATURE_WEIGHTS.map(function (f) {
      return '<div class="col-md-6"><div class="p-2 border rounded mb-2">' +
        '<div class="d-flex justify-content-between align-items-center mb-1">' +
        '<span class="small fw-semibold">' + f.label + '</span>' +
        '<span class="badge bg-primary-subtle text-primary">' + f.weight + '</span></div>' +
        '<div class="driver-bar mb-1"><div class="driver-fill" style="width:' + Math.round(f.weight / max * 100) + '%"></div></div>' +
        '<div class="small text-muted" style="font-size:.7rem">' + f.desc + '</div></div></div>';
    }).join('');
  }

  document.addEventListener('DOMContentLoaded', function () {
    renderFeatureWeights();

    var opps = (_d && (_d.opportunities || _d.leads) && (_d.opportunities || _d.leads).data) || [];

    if (cfg && !cfg.DUMMY_MODE) {
      Promise.all([
        window.CRM_API.ai.scores.list({ limit: 100 }),
        window.CRM_API.ai.predictions.churn(),
        window.CRM_API.ai.estimates.clv(),
        window.CRM_API.opportunities.list({ limit: 200 })
      ]).then(function (results) {
        var scores    = results[0].data || [];
        var churns    = results[1].data || [];
        var estimates = results[2].data || [];
        var liveOpps  = results[3].data || opps;

        var hot      = scores.filter(function (s) { return s.score_band === 'hot'; }).length;
        var highChurn= churns.filter(function (c) { return c.risk_band === 'high'; }).length;
        var avgClv   = estimates.length ? estimates.reduce(function (s, e) { return s + Number(e.estimated_clv); }, 0) / estimates.length : 0;
        var avgScore = scores.length ? Math.round(scores.reduce(function (s, sc) { return s + sc.score; }, 0) / scores.length) : 0;
        var acc      = (_d && _d.aiModelKpi) ? _d.aiModelKpi.model_accuracy : 78;

        document.getElementById('kpi-win').textContent      = avgScore + '%';
        document.getElementById('kpi-churn').textContent    = highChurn;
        document.getElementById('kpi-clv').textContent      = pkr(avgClv);
        document.getElementById('kpi-accuracy').textContent = acc + '%';

        buildWinProbChart(liveOpps);
        buildChurnChart(churns);
        buildClvChart(estimates, liveOpps);
      }).catch(function () {
        var kpi = computeDummyKpis(opps);
        document.getElementById('kpi-win').textContent      = kpi.avgWin + '%';
        document.getElementById('kpi-churn').textContent    = kpi.churnCount;
        document.getElementById('kpi-clv').textContent      = pkr(kpi.avgClv);
        document.getElementById('kpi-accuracy').textContent = kpi.accuracy + '%';
        buildWinProbChart(opps);
        buildChurnChart([]);
        buildClvChart([], opps);
      });
    } else {
      var kpi = computeDummyKpis(opps);
      document.getElementById('kpi-win').textContent      = kpi.avgWin + '%';
      document.getElementById('kpi-churn').textContent    = kpi.churnCount;
      document.getElementById('kpi-clv').textContent      = pkr(kpi.avgClv);
      document.getElementById('kpi-accuracy').textContent = kpi.accuracy + '%';
      buildWinProbChart(opps);
      buildChurnChart([]);
      buildClvChart([], opps);
    }

    function computeDummyKpis(opps) {
      var probs   = opps.map(function (o) { return STAGE_PROB[o.stage] || 40; }).filter(function (p) { return p > 0 && p < 100; });
      var avgWin  = probs.length ? Math.round(probs.reduce(function (s, p) { return s + p; }, 0) / probs.length) : 0;
      var totalVal= opps.reduce(function (s, o) { return s + (o.estimated_value || o.amount || 0); }, 0);
      var uniqAccts = new Set(opps.map(function (o) { return o.account_name || 'Acc'; })).size || 1;
      return { avgWin: avgWin, churnCount: 3, avgClv: totalVal / uniqAccts * 3.2, accuracy: (_d && _d.aiModelKpi) ? _d.aiModelKpi.model_accuracy : 78 };
    }
  });

})();
