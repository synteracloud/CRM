/* Pakistan CRM — New Contact Form (I-02) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function populateAccounts(accounts) {
    var $account = $('#c-account');
    if (!$account.length) return;
    accounts.slice().sort(function (a, b) { return (a.name || '').localeCompare(b.name || ''); }).forEach(function (a) {
      $account.append('<option value="' + a.account_id + '">' + a.name + '</option>');
    });
  }

  function activateTracker(step) {
    var PRIMARY = 'background:var(--bs-primary);color:#fff;border:none;';
    var DONE    = 'background:var(--bs-success);color:#fff;border:none;';
    var IDLE    = 'background:var(--bs-secondary-bg);color:var(--bs-secondary-color);border:2px solid var(--bs-border-color);';
    $('#tracker-dot-1').attr('style','width:32px;height:32px;font-size:.85rem;' + (step > 1 ? DONE : PRIMARY));
    $('#tracker-dot-1').html(step > 1 ? '<i class="fi fi-rr-check" style="font-size:.8rem;"></i>' : '1');
    $('#tracker-label-1').toggleClass('fw-semibold text-primary', step === 1).toggleClass('text-success', step > 1).toggleClass('text-muted', false);
    $('#tracker-dot-2').attr('style','width:32px;height:32px;font-size:.85rem;' + (step === 2 ? PRIMARY : IDLE)).text('2');
    $('#tracker-label-2').toggleClass('fw-semibold text-primary', step === 2).toggleClass('text-muted', step < 2);
    $('#tracker-connector').css('opacity', step > 1 ? '1' : '.3').css('border-color', step > 1 ? 'var(--bs-success)' : '');
  }

  function validateStep1() {
    var ok = true;
    ['c-first-name','c-last-name','c-phone'].forEach(function (id) {
      var $el = $('#' + id);
      if (!$el.val().trim()) { $el.addClass('is-invalid'); ok = false; } else { $el.removeClass('is-invalid').addClass('is-valid'); }
    });
    return ok;
  }

  var selectedTags = [];

  function initForm(accounts, contacts) {
    populateAccounts(accounts);

    /* Phone dedup */
    $('#c-phone').on('blur', function () {
      var phone = $(this).val().trim();
      if (!phone) return;
      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.contacts.list({ phone_e164: phone, limit: 1 })
          .then(function (res) {
            var found = res.data && res.data.length > 0;
            $('#c-phone-dedup-warn').toggleClass('d-none', !found);
          })
          .catch(function () {});
      } else {
        var match = contacts.filter(function (c) { return c.phone_e164 === phone; })[0];
        $('#c-phone-dedup-warn').toggleClass('d-none', !match);
      }
    });

    /* Tags */
    $(document).on('click', '.tag-toggle', function () {
      var tag = $(this).data('tag');
      if (selectedTags.indexOf(tag) === -1) {
        selectedTags.push(tag);
        $(this).removeClass('btn-outline-secondary').addClass('btn-primary');
      } else {
        selectedTags = selectedTags.filter(function (t) { return t !== tag; });
        $(this).removeClass('btn-primary').addClass('btn-outline-secondary');
      }
    });

    /* Navigation */
    $('#btn-next').on('click', function () {
      if (!validateStep1()) return;
      var fname = $('#c-first-name').val().trim(), lname = $('#c-last-name').val().trim();
      $('#s2-name-preview').text(fname + ' ' + lname);
      $('#wizard-step-1').addClass('d-none');
      $('#wizard-step-2').removeClass('d-none');
      activateTracker(2);
    });
    $('#btn-back').on('click', function () {
      $('#wizard-step-2').addClass('d-none');
      $('#wizard-step-1').removeClass('d-none');
      activateTracker(1);
    });

    $('#btn-submit').on('click', function () {
      var fname   = $('#c-first-name').val().trim();
      var lname   = $('#c-last-name').val().trim();
      var phone   = $('#c-phone').val().trim();
      var account = $('#c-account').val();
      var email   = $('#c-email').val().trim();
      var fullName= fname + ' ' + lname;

      var payload = { display_name: fullName, first_name: fname, last_name: lname, phone_e164: phone, account_id: account || null, email: email || null, tags: selectedTags };

      var $btn = $(this);
      $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1"></span> Saving…');

      function onSuccess() {
        $('#success-name').text(fullName);
        $('#wizard-step-2').addClass('d-none');
        $('#wizard-success').removeClass('d-none');
        $btn.prop('disabled', false).text('Save Contact');
      }
      function onError() {
        $btn.prop('disabled', false).text('Save Contact');
        alert('Error saving contact. Please try again.');
      }

      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.contacts.create(payload).then(onSuccess).catch(onError);
      } else {
        setTimeout(onSuccess, 600);
      }
    });

    $('#btn-cancel-s1').on('click', function () { new bootstrap.Modal(document.getElementById('modal-discard')).show(); });

    $('#btn-add-another').on('click', function () {
      $('#wizard-success').addClass('d-none');
      $('#wizard-step-1').removeClass('d-none');
      $('input, select').val('').removeClass('is-valid is-invalid');
      selectedTags = [];
      $('.tag-toggle').removeClass('btn-primary').addClass('btn-outline-secondary');
      $('#c-phone-dedup-warn').addClass('d-none');
      activateTracker(1);
    });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.accounts.list({ limit: 200 }).catch(function () { return { data: [] }; }),
      window.CRM_API.contacts.list({ limit: 200 }).catch(function () { return { data: [] }; })
    ]).then(function (results) {
      initForm(results[0].data || [], results[1].data || []);
    });
  } else {
    if (!_d) return;
    initForm((_d.accounts && _d.accounts.data) || [], _d.contacts.data || []);
  }

})();
