/* Pakistan CRM — Collections Queue Page Driver */

var _collOverdueActive = false;

$.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
  if (settings.nTable.id !== 'dt_Collections') return true;
  if (!_collOverdueActive) return true;
  var rowNode = settings.aoData[dataIndex].nTr;
  return $(rowNode).data('overdue') === 1;
});

if ($('#dt_Collections').length) {
  var dtCollections = $('#dt_Collections').DataTable({
    searching: true,
    pageLength: 10,
    select: false,
    lengthChange: false,
    info: true,
    paging: true,
    order: [[4, 'asc']],
    language: {
      search: '',
      searchPlaceholder: 'Search invoices',
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
      var dtSearch = $('#dt_Collections_wrapper .dt-search').detach();
      $('#dt_Collections_Search').append(dtSearch);
      $('#dt_Collections_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
      $('#dt_Collections_Search .dt-search label').remove();
      $('#dt_Collections_wrapper > .row.mt-2.justify-content-between').first().remove();
    }
  });

  /* Status filter */
  $('#coll-filter-status button').on('click', function () {
    $('#coll-filter-status button').removeClass('active');
    $(this).addClass('active');
    dtCollections.column(3).search($(this).data('filter')).draw();
  });

  /* Overdue toggle */
  $('#coll-filter-overdue, #show-overdue-invoices').on('click', function () {
    _collOverdueActive = !_collOverdueActive;
    $('#coll-filter-overdue').toggleClass('btn-danger btn-outline-danger');
    dtCollections.draw();
  });
}
