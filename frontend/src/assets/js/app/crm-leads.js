/* Pakistan CRM — Leads & Opportunities Page Driver */

/* ── 1. Lead Source Donut (Chart.js canvas — DOMContentLoaded required) ── */
function initLeadSourceDonut() {
  var ctx = document.getElementById('leadSourceDonut');
  if (!ctx) return;
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Website', 'Email', 'LinkedIn'],
      datasets: [{
        data: [2310, 1850, 1320],
        backgroundColor: ['#5955D1', '#009966', '#F5A70D'],
        borderWidth: 0
      }]
    },
    options: {
      cutout: '65%',
      plugins: {
        legend: { display: false }
      }
    }
  });
}
document.addEventListener('DOMContentLoaded', initLeadSourceDonut);

/* ── 2. Opportunity Value Trend (ApexCharts area — verbatim from dashboard.js) ─ */
var opportunityTrendChartConfig = {
  series: [
    {
      name: 'Opportunity Value',
      data: [890000, 760000, 1020000, 960000, 880000, 910000, 940000, 1000000, 980000, 920000, 970000, 1010000]
    }
  ],
  chart: {
    height: 280,
    type: 'area',
    zoom: { enabled: false },
    toolbar: { show: false },
  },
  colors: [
    "var(--bs-primary)",
    "var(--bs-dark)"
  ],
  fill: {
    type: ["gradient"],
    gradient: {
      shade: 'light',
      type: "vertical",
      shadeIntensity: 0.1,
      gradientToColors: ["var(--bs-primary)"],
      inverseColors: false,
      opacityFrom: 0.08,
      opacityTo: 0.01,
      stops: [20, 100]
    }
  },
  dataLabels: { enabled: false },
  stroke: {
    width: 2,
    curve: 'smooth',
    dashArray: 5
  },
  markers: {
    size: 0,
    colors: ['#FFFFFF'],
    strokeColors: 'var(--bs-primary)',
    strokeWidth: 2,
    hover: {
      size: 6
    }
  },
  yaxis: {
    min: 700000,
    max: 1100000,
    tickAmount: 5,
    labels: {
      formatter: function (value) {
        return "$" + (value / 100) + "M";
      },
      style: {
        colors: 'var(--bs-body-color)',
        fontSize: '13px',
        fontWeight: '500',
        fontFamily: 'var(--bs-body-font-family)'
      }
    }
  },
  xaxis: {
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    axisBorder: { color: 'var(--bs-border-color)' },
    axisTicks: { show: false },
    labels: {
      style: {
        colors: 'var(--bs-body-color)',
        fontSize: '13px',
        fontWeight: '500',
        fontFamily: 'var(--bs-body-font-family)'
      }
    }
  },
  tooltip: {
    y: {
      formatter: function (val) {
        return "$ " + val + "M";
      }
    }
  },
  grid: {
    borderColor: 'var(--bs-border-color)',
    strokeDashArray: 5,
    xaxis: { lines: { show: false } },
    yaxis: { lines: { show: true } }
  },
  legend: {
    show: false
  }
};
const opportunityTrendChart = document.querySelector("#opportunityTrendChart");
if (opportunityTrendChart) {
  new ApexCharts(opportunityTrendChart, opportunityTrendChartConfig).render();
}

/* ── 3. Lead Queue DataTable ─────────────────────────────────────────── */
/* Columns: Lead/Phone(0) | Stage(1) | Source(2) | Owner(3) | Due(4) | Last(5) | Action(6) */

var _leadOverdueActive = false;

$.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
  if (settings.nTable.id !== 'dt_NewCustomers') return true;
  if (!_leadOverdueActive) return true;
  var rowNode = settings.aoData[dataIndex].nTr;
  return $(rowNode).data('overdue') === 1;
});

if ($('#dt_NewCustomers').length) {
  var dt_NewCustomers = $('#dt_NewCustomers').DataTable({
    searching: true,
    pageLength: 6,
    select: false,
    lengthChange: false,
    info: true,
    paging: true,
    order: [[4, 'asc']],
    language: {
      search: '',
      searchPlaceholder: 'Search',
      paginate: {
        previous: "<i class='fi fi-rr-angle-left'></i>",
        next:     "<i class='fi fi-rr-angle-right'></i>",
        first:    "<i class='fi fi-rr-angle-double-left'></i>",
        last:     "<i class='fi fi-rr-angle-double-right'></i>"
      }
    },
    initComplete: function () {
      var dtSearch = $('#dt_NewCustomers_wrapper .dt-search').detach();
      $('#dt_NewCustomers_Search').append(dtSearch);
      $('#dt_NewCustomers_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
      $('#dt_NewCustomers_Search .dt-search label').remove();
      $('#dt_NewCustomers_wrapper > .row.mt-2.justify-content-between').first().remove();
    },
    columnDefs: [
      { targets: [0, 6], orderable: false }
    ]
  });

  /* Stage filter */
  $('#lead-filter-stage button').on('click', function () {
    $('#lead-filter-stage button').removeClass('active');
    $(this).addClass('active');
    dt_NewCustomers.column(1).search($(this).data('filter')).draw();
  });

  /* Source filter */
  $('#lead-filter-source button').on('click', function () {
    $('#lead-filter-source button').removeClass('active');
    $(this).addClass('active');
    dt_NewCustomers.column(2).search($(this).data('filter')).draw();
  });

  /* Overdue follow-up toggle */
  $('#lead-filter-overdue').on('click', function () {
    _leadOverdueActive = !_leadOverdueActive;
    $(this).toggleClass('btn-danger btn-outline-danger');
    dt_NewCustomers.draw();
  });
}

/* ── 4. dt_ScrollVertical — NOT initialised in seed dashboard.js ───────── */
/* The seed loads dashboard.js which has no dt_ScrollVertical config.       */
/* It renders as a plain HTML table — all rows visible, natural order.      */
/* Do not wrap in DataTable — doing so reorders rows and adds pagination.   */
