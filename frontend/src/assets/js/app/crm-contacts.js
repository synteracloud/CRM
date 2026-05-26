/* Pakistan CRM — Contact List Page Driver */

var _contactOpenCaseActive = false;
var _contactIdleActive = false;

$.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
  if (settings.nTable.id !== 'dt_Contacts') return true;
  var rowNode = settings.aoData[dataIndex].nTr;
  if (_contactOpenCaseActive && !$(rowNode).data('open-cases')) return false;
  if (_contactIdleActive && $(rowNode).data('idle') !== 1) return false;
  return true;
});

if ($('#dt_Contacts').length) {
  var dtContacts = $('#dt_Contacts').DataTable({
    searching: true,
    pageLength: 10,
    select: false,
    lengthChange: false,
    info: true,
    paging: true,
    order: [[3, 'asc']],
    language: {
      search: '',
      searchPlaceholder: 'Search contacts',
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
      var dtSearch = $('#dt_Contacts_wrapper .dt-search').detach();
      $('#dt_Contacts_Search').append(dtSearch);
      $('#dt_Contacts_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
      $('#dt_Contacts_Search .dt-search label').remove();
      $('#dt_Contacts_wrapper > .row.mt-2.justify-content-between').first().remove();
    }
  });

  /* Tag filter */
  $('#contact-filter-tag button').on('click', function () {
    $('#contact-filter-tag button').removeClass('active');
    $(this).addClass('active');
    dtContacts.column(5).search($(this).data('filter')).draw();
  });

  /* Open Case toggle */
  $('#contact-filter-open-case').on('click', function () {
    _contactOpenCaseActive = !_contactOpenCaseActive;
    $(this).toggleClass('btn-warning btn-outline-warning');
    dtContacts.draw();
  });

  /* Idle toggle */
  $('#contact-filter-idle').on('click', function () {
    _contactIdleActive = !_contactIdleActive;
    $(this).toggleClass('btn-info btn-outline-info');
    dtContacts.draw();
  });
}
