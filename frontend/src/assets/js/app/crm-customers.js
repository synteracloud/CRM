/* Pakistan CRM — Contacts (Customers) Page Driver */
/* Source: FRAMEWORK.md §24 — dt_CustomerList config from dashboard.js */

if ($('#dt_CustomerList').length) {
	const dt_CustomerList = $('#dt_CustomerList').DataTable({
		searching: true,
		pageLength: 12,
		select: false,
		lengthChange: false,
		info: true,
		paging: true,
		language: {
			search: "",
			searchPlaceholder: 'Search',
			paginate: {
				previous: "<i class='fi fi-rr-angle-left'></i>",
				next: "<i class='fi fi-rr-angle-right'></i>",
				first: "<i class='fi fi-rr-angle-double-left'></i>",
				last: "<i class='fi fi-rr-angle-double-right'></i>"
			},
		},
		initComplete: function () {
			var dtSearch = $('#dt_CustomerList_wrapper .dt-search').detach();
			$('#dt_CustomerList_Search').append(dtSearch);
			$('#dt_CustomerList_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
			$('#dt_CustomerList_Search .dt-search label').remove();
			$('#dt_CustomerList_wrapper > .row.mt-2.justify-content-between').first().remove();
		},
		columnDefs: [{
			targets: [0],
			orderable: false,
		}]
	});
}
