/* Pakistan CRM — Customer Health Dashboard (A-03) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function computeKpi(contacts) {
    var total      = contacts.length;
    var waActive   = contacts.filter(function (c) { return c.phone_e164; }).length;
    var openCases  = contacts.reduce(function (s, c) { return s + (Number(c.open_cases) || 0); }, 0);
    var idle7d     = contacts.filter(function (c) { return c.idle === 1 || c.idle === true; }).length;
    var avgScore   = total > 0 ? Math.round(contacts.reduce(function (s, c) { return s + (Number(c.completeness_score) || 0); }, 0) / total) : 0;
    var lowCount   = contacts.filter(function (c) { return (Number(c.completeness_score) || 0) < 70; }).length;
    /* Merge candidates: contacts sharing same phone or very similar name (exact phone = confirmed dup) */
    var phones     = contacts.map(function (c) { return c.phone_e164; }).filter(Boolean);
    var phoneSet   = {};
    var dupeCount  = 0;
    phones.forEach(function (p) { phoneSet[p] = (phoneSet[p] || 0) + 1; });
    Object.values(phoneSet).forEach(function (n) { if (n > 1) dupeCount++; });
    return { total: total, whatsapp_active: waActive, open_cases: openCases, idle_7d: idle7d, avg_completeness: avgScore, low_completeness: lowCount, duplicate_count: dupeCount, merge_candidate_count: dupeCount };
  }

  var TAG_CLR = { Lead:'primary', Hot:'danger', Customer:'success', VIP:'warning', WhatsApp:'success', New:'info' };

  function render(contacts) {
    var kpi = computeKpi(contacts);

    /* Posture strip */
    var casesCount = contacts.filter(function (c) { return (c.open_cases || 0) > 0; }).length;
    if (casesCount === 0) {
      $('#health-posture-row').addClass('d-none');
    } else {
      $('#open-cases-count').text(casesCount);
      $('#open-cases-plural').text(casesCount === 1 ? ' has' : 's have');
    }

    /* Primary KPI */
    $('#kpi-total-contacts').text(Number(kpi.total).toLocaleString());
    $('#kpi-whatsapp-active').text(Number(kpi.whatsapp_active).toLocaleString());
    $('#kpi-open-cases').text(kpi.open_cases);

    /* Risk panel */
    $('#risk-idle-count').text(kpi.idle_7d);
    $('#risk-avg-completeness').text(kpi.avg_completeness + '%');
    $('#risk-low-completeness').text(kpi.low_completeness);
    $('#completeness-bar').css('width', kpi.avg_completeness + '%');
    $('#completeness-label').text('Avg completeness: ' + kpi.avg_completeness + '%');

    /* Duplicate / merge candidates */
    $('#risk-merge-candidates').text(kpi.merge_candidate_count);

    /* Execution queue: open cases */
    var withCases = contacts.filter(function (c) { return (c.open_cases || 0) > 0; });
    $('#open-cases-queue-badge').text(withCases.length);

    var listHtml;
    if (withCases.length === 0) {
      listHtml = '<div class="text-center py-4 text-muted small"><i class="fi fi-rr-badge-check fs-3 d-block mb-2 opacity-25"></i>No contacts with open cases.</div>';
    } else {
      listHtml = '<ul class="list-group list-group-flush">' +
        withCases.map(function (c, i) {
          var avatarN = (i % 5) + 1;
          var tags = (c.tags || []).map(function (t) {
            var cls = TAG_CLR[t] || 'secondary';
            return '<span class="badge bg-' + cls + '-subtle text-' + cls + '">' + t + '</span>';
          }).join(' ');
          return '<li class="list-group-item px-3 py-3">' +
            '<div class="d-flex align-items-center justify-content-between gap-3">' +
            '<div class="d-flex align-items-center gap-2">' +
            '<div class="avatar avatar-sm rounded-circle"><img src="assets/images/avatar/avatar' + avatarN + '.webp" alt=""></div>' +
            '<div><div class="fw-semibold">' + (c.display_name || '—') + '</div>' +
            '<div class="text-muted small">' + (c.account_name || '—') + (tags ? ' · ' + tags : '') + '</div></div></div>' +
            '<div class="text-end"><div class="badge bg-warning text-dark">' + c.open_cases + ' case' + (c.open_cases > 1 ? 's' : '') + '</div>' +
            '<div class="text-muted small mt-1">' + (c.last_touchpoint || '—') + '</div></div></div></li>';
        }).join('') + '</ul>';
    }
    $('#open-cases-list').html(listHtml);

    /* Trend chart: completeness distribution */
    var buckets = [0, 0, 0, 0];
    contacts.forEach(function (c) {
      var s = Number(c.completeness_score) || 0;
      if      (s <= 50) buckets[0]++;
      else if (s <= 70) buckets[1]++;
      else if (s <= 85) buckets[2]++;
      else              buckets[3]++;
    });

    var isDark  = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    var textClr = isDark ? '#adb5bd' : '#6c757d';
    var gridClr = isDark ? '#343a40' : '#e9ecef';

    var chartEl = document.querySelector('#ContactHealthChart');
    if (chartEl && window.ApexCharts) {
      new ApexCharts(chartEl, {
        chart:   { type:'bar', height:240, toolbar:{ show:false }, fontFamily:'Instrument Sans, sans-serif' },
        series:  [{ name:'Contacts', data: buckets }],
        xaxis:   { categories:['0–50 (Low)','51–70 (Fair)','71–85 (Good)','86–100 (High)'], labels:{ style:{ colors:textClr, fontSize:'12px' } } },
        yaxis:   { labels:{ style:{ colors:textClr, fontSize:'11px' } }, tickAmount: Math.max.apply(null, buckets) || 5, min:0 },
        plotOptions: { bar:{ borderRadius:4, columnWidth:'50%', distributed:true } },
        colors:  ['#dc3545','#ffc107','#17a2b8','#28a745'],
        dataLabels: { enabled:true, style:{ fontSize:'12px', fontWeight:'600' } },
        grid:    { borderColor:gridClr }, legend:{ show:false },
        tooltip: { y:{ formatter:function (v) { return v + ' contact' + (v === 1 ? '' : 's'); } } }
      }).render();
    }
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.contacts.list({ limit: 500 })
      .then(function (res) { render(res.data || []); })
      .catch(function () { render((_d && _d.contacts && _d.contacts.data) || []); });
  } else {
    if (!_d) return;
    render(_d.contacts.data || []);
  }

})();
