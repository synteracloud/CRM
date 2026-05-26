/* Pakistan CRM — Follow-up Queue Page Driver */

/* ── Custom search extension: overdue filter ─────────────────────────── */
var _overdueActive = false;

$.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
  if (settings.nTable.id !== 'dt_Followups') return true;
  if (!_overdueActive) return true;
  var rowNode = settings.aoData[dataIndex].nTr;
  return $(rowNode).data('overdue') === 1;
});

/* ── DataTable init ──────────────────────────────────────────────────── */
if ($('#dt_Followups').length) {
  var dtFollowups = $('#dt_Followups').DataTable({
    searching: true,
    pageLength: 10,
    select: false,
    lengthChange: false,
    info: true,
    paging: true,
    order: [[2, 'asc']],
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
    columnDefs: [
      { targets: [0, 6], orderable: false }
    ],
    initComplete: function () {
      var dtSearch = $('#dt_Followups_wrapper .dt-search').detach();
      $('#dt_Followups_Search').append(dtSearch);
      $('#dt_Followups_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
      $('#dt_Followups_Search .dt-search label').remove();
      $('#dt_Followups_wrapper > .row.mt-2.justify-content-between').first().remove();
      _updateEnforcementStrip();
    }
  });

  /* ── Action type filter ── */
  $('#filter-action-type button').on('click', function () {
    $('#filter-action-type button').removeClass('active');
    $(this).addClass('active');
    dtFollowups.column(1).search($(this).data('filter')).draw();
  });

  /* ── Enforcement level filter ── */
  $('#filter-level button').on('click', function () {
    $('#filter-level button').removeClass('active');
    $(this).addClass('active');
    dtFollowups.column(3).search($(this).data('filter')).draw();
  });

  /* ── Overdue toggle filter ── */
  $('#filter-overdue').on('click', function () {
    _overdueActive = !_overdueActive;
    $(this).toggleClass('btn-danger btn-outline-danger');
    dtFollowups.draw();
  });

  /* ── Enforcement strip "Show overdue only" shortcut ── */
  $('#show-overdue-only').on('click', function () {
    if (!_overdueActive) {
      _overdueActive = true;
      $('#filter-overdue').removeClass('btn-outline-danger').addClass('btn-danger');
      dtFollowups.draw();
    }
  });
}

/* ── Enforcement strip: count overdue rows from DOM ─────────────────── */
function _updateEnforcementStrip() {
  var today = new Date();
  today.setHours(0, 0, 0, 0);
  var count = 0;
  $('#dt_Followups tbody tr').each(function () {
    if ($(this).data('overdue') === 1) count++;
  });
  var $strip = $('#enforcement-strip-row');
  if (count > 0) {
    $('#overdue-count').text(count);
    $('#overdue-plural').text(count === 1 ? ' is' : 's are');
    $('#kpi-overdue').text(count);
    $strip.removeClass('d-none');
  } else {
    $strip.addClass('d-none');
  }
}
