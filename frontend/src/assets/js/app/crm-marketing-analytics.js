/* Pakistan CRM — Marketing Analytics (H-02) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function render(campaigns) {
    if (typeof flatpickr !== 'undefined') {
      flatpickr('#date-range-picker', { mode:'range', dateFormat:'d M Y', defaultDate:[new Date(Date.now() - 29 * 86400000), new Date()] });
    }

    var active    = campaigns.filter(function (c) { return c.reach > 0; });
    var delivered = active.filter(function (c) { return c.delivery_rate > 0; });

    document.getElementById('kpi-delivery').textContent    = delivered.length ? Math.round(delivered.reduce(function (s, c) { return s + c.delivery_rate; }, 0) / delivered.length) + '%' : '—';
    document.getElementById('kpi-open').textContent        = delivered.length ? Math.round(delivered.reduce(function (s, c) { return s + (c.open_rate || 0); }, 0) / delivered.length) + '%' : '—';
    document.getElementById('kpi-leads').textContent       = campaigns.reduce(function (s, c) { return s + (c.leads_generated || 0); }, 0);
    document.getElementById('kpi-conversions').textContent = campaigns.reduce(function (s, c) { return s + (c.conversions || 0); }, 0);

    new ApexCharts(document.getElementById('chart-channel'), {
      chart: { type:'bar', height:260, toolbar:{ show:false } },
      series: [{ name:'Delivery %', data:[93,88,91] }, { name:'Open %', data:[65,42,55] }, { name:'Reply %', data:[21,8,18] }],
      xaxis: { categories:['WhatsApp','Email','SMS'] },
      colors: ['#0e9f6e','#3f83f8','#9061f9'],
      plotOptions: { bar:{ columnWidth:'55%', borderRadius:4 } },
      legend: { position:'top' }, dataLabels: { enabled:false },
    }).render();

    new ApexCharts(document.getElementById('chart-optin'), {
      chart: { type:'area', height:260, toolbar:{ show:false } },
      series: [{ name:'Opted-in', data:[720,745,768,790,820,843] }, { name:'Opt-outs', data:[12,8,15,10,14,11] }],
      xaxis: { categories:['Dec','Jan','Feb','Mar','Apr','May'] },
      colors: ['#0e9f6e','#f05252'], stroke:{ curve:'smooth', width:2 },
      fill:{ type:'gradient', gradient:{ shadeIntensity:1, opacityFrom:0.3, opacityTo:0.0 } },
      legend: { position:'top' }, dataLabels: { enabled:false },
    }).render();

    $('#dt_MarketingCampaigns').DataTable({
      data: campaigns, pageLength: 10,
      columns: [
        { data:'name',           className:'dt-body-left', render:function (n) { return '<span class="fw-semibold">' + n + '</span>'; } },
        { data:'type',           className:'dt-body-center', render:function (t) { return ({ whatsapp_broadcast:'WhatsApp', email:'Email', sms:'SMS' })[t] || t; } },
        { data:'reach',          className:'dt-body-center', render:function (r) { return r ? Number(r).toLocaleString() : '—'; } },
        { data:'delivery_rate',  className:'dt-body-center', render:function (r) { return r ? r + '%' : '—'; } },
        { data:'open_rate',      className:'dt-body-center', render:function (r) { return r ? r + '%' : '—'; } },
        { data:'reply_rate',     className:'dt-body-center', render:function (r) { return r ? r + '%' : '—'; } },
        { data:'leads_generated',className:'dt-body-center', render:function (r) { return r || '—'; } },
        { data:'conversions',    className:'dt-body-center', render:function (r) { return r || '—'; } },
      ],
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.campaigns.list({ limit: 200 })
        .then(function (res) { render(res.data || []); })
        .catch(function () { render((_d && _d.campaigns && _d.campaigns.data) || []); });
    } else {
      render((_d && _d.campaigns && _d.campaigns.data) || []);
    }
  });

})();
