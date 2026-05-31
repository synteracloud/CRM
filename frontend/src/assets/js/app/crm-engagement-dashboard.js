(function () {
  'use strict';
  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var TYPE_ICON  = { whatsapp_broadcast: '📱', email: '✉️', sms: '💬' };
  var STATUS_BADGE = {
    active:    '<span class="badge bg-success">Active</span>',
    completed: '<span class="badge bg-secondary">Completed</span>',
    draft:     '<span class="badge bg-light text-dark border">Draft</span>',
    paused:    '<span class="badge bg-warning text-dark">Paused</span>',
  };

  function renderKpis(kpi) {
    document.getElementById('kpi-delivery').textContent = kpi.delivery_rate + '%';
    document.getElementById('kpi-open').textContent     = kpi.open_rate + '%';
    document.getElementById('kpi-reply').textContent    = kpi.reply_rate + '%';
    document.getElementById('kpi-failed').textContent   = kpi.failed_delivery_count;
    document.getElementById('wa-opted-in').textContent  = (kpi.whatsapp_opted_in || 0).toLocaleString();
    document.getElementById('wa-opt-out').textContent   = kpi.whatsapp_opt_out_rate + '%';
  }

  function renderChart(channelData) {
    new ApexCharts(document.getElementById('chart-engagement'), {
      chart:  { type: 'bar', height: 260, toolbar: { show: false } },
      series: [
        { name: 'Delivery %', data: channelData.map(function (c) { return c.delivery; }) },
        { name: 'Open %',     data: channelData.map(function (c) { return c.open; }) },
        { name: 'Reply %',    data: channelData.map(function (c) { return c.reply; }) },
      ],
      xaxis:       { categories: channelData.map(function (c) { return c.label || c.channel; }) },
      colors:      ['#0e9f6e', '#3f83f8', '#9061f9'],
      plotOptions: { bar: { columnWidth: '55%', borderRadius: 4 } },
      legend:      { position: 'top' },
      dataLabels:  { enabled: false },
    }).render();
  }

  function renderCampaigns(campaigns) {
    var active = (campaigns || []).filter(function (c) { return c.status !== 'completed'; }).slice(0, 5);
    document.getElementById('campaign-queue').innerHTML = active.map(function (c) {
      return '<a href="app/marketing-workspace.html" class="list-group-item list-group-item-action d-flex align-items-center gap-3 py-2">' +
        '<span class="fs-5">' + (TYPE_ICON[c.type] || '📢') + '</span>' +
        '<div class="flex-grow-1 overflow-hidden">' +
        '<div class="fw-semibold text-truncate">' + c.name + '</div>' +
        '<div class="small text-muted">' + (c.reach ? c.reach.toLocaleString() + ' reached · ' + c.delivery_rate + '% delivery' : 'Not started') + '</div>' +
        '</div>' + (STATUS_BADGE[c.status] || c.status) + '</a>';
    }).join('');
  }

  var DUMMY_CHANNEL = (_d && _d.campaigns) ? _d.campaigns.data.filter(function (c) { return c.reach > 0; }).slice(0, 5).map(function (c) {
    return { label: c.name.split(' ').slice(0, 2).join(' '), delivery: c.delivery_rate, open: c.open_rate, reply: c.reply_rate };
  }) : [
    { label: 'Eid Offer',  delivery: 94, open: 68, reply: 22 },
    { label: 'Q2 Launch',  delivery: 88, open: 42, reply: 8  },
    { label: 'Re-engage',  delivery: 91, open: 55, reply: 18 },
    { label: 'Enterprise', delivery: 97, open: 51, reply: 12 },
    { label: 'Ramadan',    delivery: 89, open: 61, reply: 19 },
  ];

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      CRM_API.communications.engagement()
        .then(function (r) {
          var kpi = r.data || r;
          renderKpis(kpi);
          renderChart(kpi.delivery_open_click_reply_rate || DUMMY_CHANNEL);
        })
        .catch(function () { renderKpis(_d.commsKpi); renderChart(DUMMY_CHANNEL); });

      CRM_API.campaigns.list()
        .then(function (r) { renderCampaigns(r.data || []); })
        .catch(function () { renderCampaigns(_d ? _d.campaigns.data : []); });
    } else {
      renderKpis(_d.commsKpi);
      renderCampaigns(_d.campaigns.data);
      renderChart(DUMMY_CHANNEL);
    }
  });
})();
