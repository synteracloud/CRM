/* Pakistan CRM — CPQ Quote Builder (I-05) */
/* 4 steps: Header → Line Items → Terms → Review & Send */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var APPROVAL_THRESHOLD = 10;
  var products           = [];
  var rowCounter         = 0;
  var autosaveTimer      = null;

  function pkr(n) { return 'PKR ' + Number(Math.round(n)).toLocaleString('en-IN'); }

  /* ── Init dropdowns from data ───────────────────────────────────── */
  function initDropdowns(priceBooks, contacts, opps) {
    products = (priceBooks && priceBooks[0] && priceBooks[0].products) ? priceBooks[0].products : [];

    var accountSet = {};
    contacts.forEach(function (c) { if (c.account_name) accountSet[c.account_name] = true; });
    opps.forEach(function (o) { if (o.account_name) accountSet[o.account_name] = true; });
    var $qAccount = $('#q-account');
    Object.keys(accountSet).sort().forEach(function (name) {
      $qAccount.append('<option value="' + name + '">' + name + '</option>');
    });

    var $qOpp = $('#q-opportunity');
    opps.filter(function (o) { return o.stage !== 'closed_won' && o.stage !== 'closed_lost'; })
      .forEach(function (o) {
        $qOpp.append('<option value="' + o.opportunity_id + '">' + o.name + ' (' + o.account_name + ')</option>');
      });

    if (window.flatpickr) {
      flatpickr('#q-expiry', { dateFormat: 'Y-m-d', minDate: 'today' });
    }
  }

  /* ── Product options HTML ───────────────────────────────────────── */
  function productOptions() {
    return products.map(function (p) {
      return '<option value="' + p.product_id + '" data-price="' + p.list_price + '">' +
        p.name + ' — PKR ' + Number(p.list_price).toLocaleString('en-IN') + '</option>';
    }).join('');
  }

  /* ── Line items ─────────────────────────────────────────────────── */
  function addLineRow() {
    var idx = rowCounter++;
    var row = '<tr id="line-row-' + idx + '">' +
      '<td><select class="form-select form-select-sm li-product" data-idx="' + idx + '">' +
        '<option value="">— Select product —</option>' + productOptions() +
      '</select></td>' +
      '<td class="text-center" style="width:70px;">' +
        '<input type="number" class="form-control form-control-sm text-center li-qty" data-idx="' + idx + '" value="1" min="1" style="width:60px;">' +
      '</td>' +
      '<td class="text-center li-unit-price" id="li-price-' + idx + '">—</td>' +
      '<td class="text-center" style="width:80px;">' +
        '<input type="number" class="form-control form-control-sm text-center li-disc" data-idx="' + idx + '" value="0" min="0" max="100" style="width:65px;">' +
      '</td>' +
      '<td class="text-center fw-semibold li-total" id="li-total-' + idx + '">—</td>' +
      '<td class="text-center">' +
        '<button type="button" class="btn btn-xs btn-outline-danger btn-icon btn-remove-line waves-effect" data-idx="' + idx + '">' +
          '<i class="fi fi-rr-trash"></i></button>' +
      '</td></tr>';
    $('#line-items-body').append(row);
    updateTotals();
  }

  function updateTotals() {
    var grandTotal = 0, needsApproval = false;
    $('#line-items-body tr').each(function () {
      var $prod = $(this).find('.li-product');
      var qty   = parseFloat($(this).find('.li-qty').val()) || 1;
      var disc  = parseFloat($(this).find('.li-disc').val()) || 0;
      var price = parseFloat($prod.find(':selected').data('price') || 0);
      if (disc > APPROVAL_THRESHOLD) needsApproval = true;
      var lineNet = Math.round(price * qty * (1 - disc / 100));
      grandTotal += lineNet;
      $(this).find('.li-unit-price').text(price > 0 ? pkr(price) : '—');
      $(this).find('.li-total').text(price > 0 ? pkr(lineNet) : '—');
    });
    $('#grand-total-cell').text(pkr(grandTotal));
    $('#discount-approval-warning').toggleClass('d-none', !needsApproval);
  }

  $('#btn-add-line').on('click', addLineRow);
  $('#line-items-body')
    .on('change', '.li-product, .li-qty, .li-disc', updateTotals)
    .on('click', '.btn-remove-line', function () { $(this).closest('tr').remove(); updateTotals(); });

  /* ── Tracker ────────────────────────────────────────────────────── */
  function activateTracker(step) {
    var PRIMARY = 'width:32px;height:32px;font-size:.85rem;background:var(--bs-primary);color:#fff;';
    var DONE    = 'width:32px;height:32px;font-size:.85rem;background:var(--bs-success);color:#fff;';
    var IDLE    = 'width:32px;height:32px;font-size:.85rem;background:var(--bs-secondary-bg);color:var(--bs-secondary-color);border:2px solid var(--bs-border-color);';
    [1, 2, 3, 4].forEach(function (n) {
      var $dot = $('#tracker-dot-' + n), $lbl = $('#tracker-label-' + n);
      if (n < step)        { $dot.attr('style', DONE).html('<i class="fi fi-rr-check" style="font-size:.8rem;"></i>'); $lbl.removeClass('text-muted text-primary fw-semibold').addClass('text-success'); }
      else if (n === step) { $dot.attr('style', PRIMARY).text(n); $lbl.removeClass('text-muted text-success').addClass('fw-semibold text-primary'); }
      else                 { $dot.attr('style', IDLE).text(n); $lbl.removeClass('fw-semibold text-primary text-success').addClass('text-muted'); }
      if (n < 4) $('#connector-' + n).css({ opacity: n < step ? '1' : '.3', 'border-color': n < step ? 'var(--bs-success)' : '' });
    });
  }

  function showStep(step) {
    [1, 2, 3, 4].forEach(function (n) { $('#wizard-step-' + n).toggleClass('d-none', n !== step); });
    activateTracker(step);
  }

  function startAutosave() {
    if (autosaveTimer) return;
    autosaveTimer = setInterval(function () {
      $('#autosave-badge').removeClass('d-none');
      setTimeout(function () { $('#autosave-badge').addClass('d-none'); }, 3000);
    }, 60000);
  }

  /* ── Validation ─────────────────────────────────────────────────── */
  function validateStep1() {
    var ok = true;
    if (!$('#q-account').val()) { $('#q-account').addClass('is-invalid'); ok = false; } else { $('#q-account').removeClass('is-invalid').addClass('is-valid'); }
    if (!$('#q-expiry').val())  { $('#q-expiry').addClass('is-invalid');  ok = false; } else { $('#q-expiry').removeClass('is-invalid').addClass('is-valid'); }
    return ok;
  }
  function validateStep2() {
    if ($('#line-items-body tr').length === 0) { alert('Add at least one product.'); return false; }
    var ok = true;
    $('#line-items-body .li-product').each(function () {
      if (!$(this).val()) { $(this).addClass('is-invalid'); ok = false; } else { $(this).removeClass('is-invalid'); }
    });
    return ok;
  }

  /* ── Build review ───────────────────────────────────────────────── */
  function buildReview() {
    var acct   = $('#q-account').val();
    var oppTxt = $('#q-opportunity option:selected').text();
    var expiry = $('#q-expiry').val();
    var curr   = $('#q-currency').val();

    $('#review-header-summary').html(
      '<div class="row g-2 small">' +
      '<div class="col-sm-3"><span class="text-muted">Account</span><br><strong>' + acct + '</strong></div>' +
      '<div class="col-sm-5"><span class="text-muted">Opportunity</span><br><strong>' + (oppTxt || '—') + '</strong></div>' +
      '<div class="col-sm-2"><span class="text-muted">Expiry</span><br><strong>' + expiry + '</strong></div>' +
      '<div class="col-sm-2"><span class="text-muted">Currency</span><br><strong>' + curr + '</strong></div>' +
      '</div>');

    var grandTotal = 0, rowsHtml = '', needsApproval = false;
    var lineItems = [];
    $('#line-items-body tr').each(function () {
      var $prod = $(this).find('.li-product');
      var name  = $prod.find(':selected').text().split(' — ')[0] || '—';
      var pid   = $prod.val();
      var qty   = parseFloat($(this).find('.li-qty').val()) || 1;
      var price = parseFloat($prod.find(':selected').data('price') || 0);
      var disc  = parseFloat($(this).find('.li-disc').val()) || 0;
      var net   = Math.round(price * qty * (1 - disc / 100));
      grandTotal += net;
      if (disc > APPROVAL_THRESHOLD) needsApproval = true;
      lineItems.push({ product_id: pid, name: name, qty: qty, list_price: price, discount: disc });
      rowsHtml += '<tr>' +
        '<td class="text-center">' + name + '</td>' +
        '<td class="text-center">' + qty + '</td>' +
        '<td class="text-center">' + pkr(price) + '</td>' +
        '<td class="text-center">' + (disc > 0 ? disc + '%' : '—') + '</td>' +
        '<td class="text-center fw-semibold">' + pkr(net) + '</td></tr>';
    });

    $('#review-line-items').html(rowsHtml);
    $('#review-grand-total').text(pkr(grandTotal));
    $('#review-payment-terms').text($('#q-payment-terms').val());
    $('#review-delivery-terms').text($('#q-delivery-terms').val());
    $('#review-expiry').text(expiry);
    $('#approval-route-notice').toggleClass('d-none', !needsApproval);

    /* Store for submit */
    window._quotePayload = {
      account_name:    acct,
      opportunity_id:  $('#q-opportunity').val() || null,
      valid_until:     expiry,
      currency:        curr || 'PKR',
      payment_terms:   $('#q-payment-terms').val(),
      delivery_terms:  $('#q-delivery-terms').val(),
      status:          needsApproval ? 'pending_approval' : 'draft',
      line_items:      lineItems
    };
  }

  /* ── Navigation ─────────────────────────────────────────────────── */
  $('#btn-next-1').on('click', function () { if (!validateStep1()) return; startAutosave(); showStep(2); if ($('#line-items-body tr').length === 0) addLineRow(); });
  $('#btn-back-2').on('click', function () { showStep(1); });
  $('#btn-next-2').on('click', function () { if (!validateStep2()) return; showStep(3); });
  $('#btn-back-3').on('click', function () { showStep(2); });
  $('#btn-next-3').on('click', function () { buildReview(); showStep(4); });
  $('#btn-back-4').on('click', function () { showStep(3); });

  $('#btn-cancel-s1, #btn-cancel-s2, #btn-cancel-s3').on('click', function () {
    new bootstrap.Modal(document.getElementById('modal-discard')).show();
  });

  $('#btn-save-draft').on('click', function () {
    var payload = window._quotePayload || {};
    payload.status = 'draft';

    function onDraftSuccess() {
      $('#autosave-badge').removeClass('d-none');
      $('#success-title').text('Draft Saved');
      $('#success-message').text('Your quote has been saved as a draft. Continue editing from the Quote Dashboard.');
      $('#wizard-step-4').addClass('d-none');
      $('#wizard-success').removeClass('d-none');
    }

    if (cfg && !cfg.DUMMY_MODE && payload.account_name) {
      window.CRM_API.quotes.create(payload).then(onDraftSuccess).catch(onDraftSuccess);
    } else {
      onDraftSuccess();
    }
  });

  $('#btn-submit').on('click', function () {
    var $btn = $(this);
    $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1"></span> Submitting…');
    var payload = window._quotePayload || {};

    function onSubmitSuccess() {
      $('#success-title').text('Quote Submitted for Approval');
      $('#success-message').text('Sent for review. You will be notified once approved.');
      $('#wizard-step-4').addClass('d-none');
      $('#wizard-success').removeClass('d-none');
      $btn.prop('disabled', false).text('Send for Approval');
    }

    if (cfg && !cfg.DUMMY_MODE && payload.account_name) {
      window.CRM_API.quotes.create(payload).then(onSubmitSuccess).catch(onSubmitSuccess);
    } else {
      onSubmitSuccess();
    }
  });

  $('#btn-add-another').on('click', function () {
    $('#wizard-success').addClass('d-none');
    $('#line-items-body').empty();
    $('select').val('');
    $('textarea').val('');
    $('#grand-total-cell').text('PKR 0');
    if (autosaveTimer) { clearInterval(autosaveTimer); autosaveTimer = null; }
    showStep(1);
  });

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.priceBooks.list(),
      window.CRM_API.contacts.list({ limit: 200 }),
      window.CRM_API.opportunities.list({ limit: 200 })
    ]).then(function (results) {
      var pbs = Array.isArray(results[0].data) ? results[0].data : (results[0].data ? [results[0].data] : []);
      initDropdowns(pbs, results[1].data || [], results[2].data || []);
    }).catch(function () {
      var pb = (_d && _d.priceBooks && _d.priceBooks.data) || [];
      initDropdowns(pb, (_d && _d.contacts && _d.contacts.data) || [], (_d && _d.opportunities && _d.opportunities.data) || []);
    });
  } else {
    if (!_d) return;
    initDropdowns(_d.priceBooks.data, _d.contacts.data, _d.opportunities.data);
  }

})();
