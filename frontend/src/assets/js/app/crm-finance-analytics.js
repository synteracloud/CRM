/* Pakistan CRM — Finance Analytics (H-04) */
/* NOTE: JazzCash/Easypaisa payment method split hidden — P-016 (JAZZCASH_STUB_MODE=true) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function pkr(n) { return 'PKR ' + Number(Math.round(n)).toLocaleString('en-IN'); }
  var MONTHS_ABBR = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function fmtDate(iso) {
    if (!iso) return '—';
    var p = iso.split('-');
    return MONTHS_ABBR[parseInt(p[1], 10) - 1] + ' ' + parseInt(p[2], 10) + ', ' + p[0];
  }

  function computeKpi(collections) {
    var outstanding = 0, overdueCount = 0, overdueValue = 0, paidMonth = 0, totalDue = 0, totalPaid = 0;
    var thisMonth = new Date().toISOString().slice(0, 7);
    collections.forEach(function (inv) {
      var amt = Number(inv.amount_due) || 0;
      if (inv.status !== 'paid' && inv.status !== 'void' && inv.status !== 'uncollectible') {
        outstanding += amt; totalDue += amt;
      }
      if (inv.is_overdue) { overdueCount++; overdueValue += amt; }
      if (inv.status === 'paid') {
        totalPaid += amt;
        if (inv.due_date && inv.due_date.substring(0, 7) === thisMonth) paidMonth += amt;
      }
    });
    var collectionRate = totalDue > 0 ? Math.round((totalPaid / (totalDue + totalPaid)) * 100) : 0;
    return { total_outstanding: outstanding, overdue_count: overdueCount, overdue_value: overdueValue, paid_this_month: paidMonth, collection_rate: collectionRate };
  }

  function render(collections) {
    var TODAY   = new Date().toISOString().substring(0, 10);
    var kpi     = computeKpi(collections);

    function daysDiff(dateStr) {
      return Math.floor((new Date(TODAY) - new Date(dateStr)) / 86400000);
    }

    /* KPI strip */
    $('#h04-total-outstanding').text(pkr(kpi.total_outstanding));
    $('#h04-overdue-value').text(pkr(kpi.overdue_value));
    $('#h04-overdue-count').text(kpi.overdue_count);
    $('#h04-paid-month').text(pkr(kpi.paid_this_month));
    $('#h04-collection-rate').text(kpi.collection_rate + '%');

    var isDark  = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    var textClr = isDark ? '#adb5bd' : '#6c757d';
    var gridClr = isDark ? '#343a40' : '#e9ecef';

    /* Overdue aging buckets */
    var bucketValues = [0, 0, 0, 0];
    var bucketCounts = [0, 0, 0, 0];
    collections.forEach(function (inv) {
      if (!inv.is_overdue) return;
      var days = daysDiff(inv.due_date);
      var idx  = days <= 30 ? 0 : days <= 60 ? 1 : days <= 90 ? 2 : 3;
      bucketValues[idx] += Number(inv.amount_due) || 0;
      bucketCounts[idx]++;
    });

    var agingEl = document.querySelector('#H04AgingChart');
    if (agingEl && window.ApexCharts) {
      new ApexCharts(agingEl, {
        chart:   { type:'bar', height:260, toolbar:{show:false}, fontFamily:'Instrument Sans, sans-serif' },
        series:  [{ name:'Outstanding (PKR)', data: bucketValues }],
        xaxis:   { categories:['0–30 Days','31–60 Days','61–90 Days','90+ Days'], labels:{ style:{ colors:textClr, fontSize:'12px' } } },
        yaxis:   { labels:{ style:{ colors:textClr, fontSize:'11px' }, formatter:function (v) { return 'PKR ' + Number(Math.round(v / 1000)).toLocaleString() + 'k'; } } },
        plotOptions: { bar:{ borderRadius:4, columnWidth:'50%', distributed:true } },
        colors:  ['#ffc107','#fd7e14','#dc3545','#6f1926'],
        dataLabels: { enabled:true, style:{ fontSize:'11px', fontWeight:'600' }, formatter:function (v) { return v > 0 ? pkr(v) : '—'; } },
        grid:    { borderColor:gridClr }, legend:{ show:false },
        tooltip: { y:{ formatter:function (v) { return pkr(v); } } }
      }).render();
    }

    /* Revenue trend chart (uses static dummy data as no live monthly trend endpoint exists) */
    var inv    = (_d && _d.invoiceSummaries) || {};
    var trend  = inv.monthly_trend || [];
    var months = trend.map(function (t) { return t.month; });
    var revenues = trend.map(function (t) { return t.revenue; });
    var expenses = trend.map(function (t) { return t.expenses; });

    if (months.length === 0) {
      /* Generate stub months from collection data dates */
      var monthMap = {};
      collections.forEach(function (c) {
        if (c.due_date) {
          var mo = c.due_date.substring(0, 7);
          if (!monthMap[mo]) monthMap[mo] = { revenue: 0, expenses: 0 };
          if (c.status === 'paid') monthMap[mo].revenue += Number(c.amount_due) || 0;
          else monthMap[mo].expenses += Number(c.amount_due) || 0;
        }
      });
      Object.keys(monthMap).sort().forEach(function (mo) {
        months.push(mo.substring(5, 7) + '/' + mo.substring(0, 4));
        revenues.push(monthMap[mo].revenue);
        expenses.push(monthMap[mo].expenses);
      });
    }

    var trendEl = document.querySelector('#H04RevenueTrendChart');
    if (trendEl && window.ApexCharts) {
      new ApexCharts(trendEl, {
        chart:  { type:'line', height:260, toolbar:{show:false}, fontFamily:'Instrument Sans, sans-serif' },
        series: [{ name:'Revenue', data: revenues }, { name:'Expenses', data: expenses }],
        xaxis:  { categories: months, labels:{ style:{ colors:textClr, fontSize:'11px' } } },
        yaxis:  { labels:{ style:{ colors:textClr, fontSize:'10px' }, formatter:function (v) { return 'PKR ' + Number(Math.round(v / 1000)).toLocaleString() + 'k'; } } },
        colors: ['#28a745','#dc3545'],
        stroke: { curve:'smooth', width:2 },
        markers: { size:4 },
        grid:   { borderColor:gridClr },
        legend: { position:'top', labels:{ colors:textClr } },
        tooltip: { y:{ formatter:function (v) { return pkr(v); } } }
      }).render();
    }

    /* Collections detail table */
    var sorted = collections.slice().sort(function (a, b) {
      if (a.is_overdue && !b.is_overdue) return -1;
      if (!a.is_overdue && b.is_overdue) return 1;
      return new Date(a.due_date) - new Date(b.due_date);
    });

    var tableRows = sorted.map(function (c) {
      var days    = daysDiff(c.due_date);
      var overdue = c.is_overdue;
      var badge   = c.status === 'paid'
        ? '<span class="badge bg-success-subtle text-success">Paid</span>'
        : overdue
          ? '<span class="badge bg-danger-subtle text-danger">Overdue ' + days + 'd</span>'
          : '<span class="badge bg-warning-subtle text-warning">Open</span>';
      var lastRem = c.last_reminder_at ? fmtDate(c.last_reminder_at.substring(0, 10)) : '—';
      return '<tr>' +
        '<td class="text-center"><strong>' + (c.invoice_number || '—') + '</strong></td>' +
        '<td class="text-center">' + (c.account_name || '—') + (c.account_tier ? '<br><small class="text-muted">' + c.account_tier + '</small>' : '') + '</td>' +
        '<td class="text-center fw-semibold' + (overdue ? ' text-danger' : '') + '">' + pkr(c.amount_due) + '</td>' +
        '<td class="text-center' + (overdue ? ' text-danger' : '') + '">' + fmtDate(c.due_date) + '</td>' +
        '<td class="text-center">' + badge + '</td>' +
        '<td class="text-center text-muted small">' + lastRem + '</td>' +
        '</tr>';
    });
    $('#h04-collections-body').html(tableRows.join(''));

    /* CSV export */
    var exportBtn = document.getElementById('h04-export-btn');
    if (exportBtn) {
      exportBtn.addEventListener('click', function () {
        var csv = 'Invoice,Account,Amount Due,Due Date,Status,Is Overdue\n';
        collections.forEach(function (c) {
          csv += '"' + (c.invoice_number || '') + '","' + (c.account_name || '') + '",' + (c.amount_due || 0) + ',' + (c.due_date || '') + ',' + (c.status || '') + ',' + (c.is_overdue ? 'Yes' : 'No') + '\n';
        });
        var link = document.createElement('a');
        link.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
        link.download = 'finance-analytics-' + new Date().toISOString().split('T')[0] + '.csv';
        link.click();
      });
    }
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.collections.list({ limit: 500 })
      .then(function (res) { render(res.data || []); })
      .catch(function () { render((_d && _d.collections && _d.collections.data) || []); });
  } else {
    if (!_d) return;
    render(_d.collections.data || []);
  }

})();
