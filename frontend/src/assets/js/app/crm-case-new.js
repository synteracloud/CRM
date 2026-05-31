/* Pakistan CRM — New Case Form (I-04) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var selectedContact = null;

  function setStep(n) {
    document.getElementById('step-1').style.display = n === 1 ? '' : 'none';
    document.getElementById('step-2').style.display = n === 2 ? '' : 'none';
    var ind2 = document.getElementById('step-2-indicator');
    if (!ind2) return;
    var circle2 = ind2.querySelector('.avatar');
    if (n === 2) {
      ind2.classList.remove('opacity-50');
      if (circle2) circle2.classList.replace('bg-secondary', 'bg-primary');
    } else {
      ind2.classList.add('opacity-50');
      if (circle2) circle2.classList.replace('bg-primary', 'bg-secondary');
    }
  }

  function populateSuggestions(contacts, q) {
    var suggestEl  = document.getElementById('contact-suggestions');
    var selectedEl = document.getElementById('selected-contact');
    if (!q) { suggestEl.innerHTML = ''; suggestEl.style.display = 'none'; return; }
    var matches = contacts.filter(function (c) {
      return (c.display_name || '').toLowerCase().includes(q) || (c.phone_e164 || '').includes(q);
    }).slice(0, 5);
    suggestEl.innerHTML = matches.length ? matches.map(function (c) {
      return '<div class="p-2 border-bottom hover-bg cursor-pointer contact-opt" style="cursor:pointer" data-id="' + c.contact_id + '" data-name="' + c.display_name + '" data-phone="' + (c.phone_e164 || '') + '">' +
        '<div class="fw-semibold">' + c.display_name + '</div>' +
        '<div class="small text-muted">' + (c.phone_e164 || '') + ' · ' + (c.account_name || '—') + '</div></div>';
    }).join('') : '<div class="p-2 text-muted small">No contacts found.</div>';
    suggestEl.style.display = '';

    suggestEl.onclick = function (e) {
      var opt = e.target.closest('.contact-opt');
      if (!opt) return;
      selectedContact = { id: opt.dataset.id, name: opt.dataset.name, phone: opt.dataset.phone };
      document.getElementById('contact-search').value = selectedContact.name;
      suggestEl.style.display = 'none';
      selectedEl.style.display = '';
      selectedEl.innerHTML = '<div class="alert alert-success-subtle p-2 small border border-success-subtle rounded"><i class="fi fi-rr-user text-success me-1"></i><strong>' + selectedContact.name + '</strong> — ' + selectedContact.phone + '</div>';
    };
  }

  document.addEventListener('DOMContentLoaded', function () {
    var searchEl = document.getElementById('contact-search');

    if (cfg && !cfg.DUMMY_MODE) {
      searchEl.addEventListener('input', function () {
        var q = this.value.trim().toLowerCase();
        if (!q) { document.getElementById('contact-suggestions').style.display = 'none'; return; }
        window.CRM_API.contacts.list({ search: q, limit: 5 })
          .then(function (res) { populateSuggestions(res.data || [], q); })
          .catch(function () { populateSuggestions((_d && _d.contacts && _d.contacts.data) || [], q); });
      });
    } else {
      searchEl.addEventListener('input', function () {
        populateSuggestions((_d && _d.contacts && _d.contacts.data) || [], this.value.trim().toLowerCase());
      });
    }

    document.getElementById('btn-next-1').addEventListener('click', function () {
      var subject  = document.getElementById('case-subject').value.trim();
      var priority = document.getElementById('case-priority').value;
      if (!selectedContact) { alert('Please select a contact.'); return; }
      if (!subject)          { alert('Please enter a subject.'); return; }
      if (!priority)         { alert('Please select a priority.'); return; }
      setStep(2);
    });

    document.getElementById('btn-back-2').addEventListener('click', function () { setStep(1); });

    document.getElementById('btn-submit').addEventListener('click', function () {
      var description = document.getElementById('case-description').value.trim();
      if (!description) { alert('Please enter a description.'); return; }

      var btn     = this;
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Creating…';

      var queue = document.getElementById('case-queue');
      var payload = {
        contact_id:  selectedContact ? selectedContact.id  : null,
        contact_name: selectedContact ? selectedContact.name : null,
        subject:     document.getElementById('case-subject').value.trim(),
        priority:    document.getElementById('case-priority').value,
        queue:       queue ? queue.value : 'General Support',
        description: description,
        source:      'crm'
      };

      function onSuccess() {
        btn.disabled  = false;
        btn.innerHTML = 'Submit Case';
        var toast = document.createElement('div');
        toast.className = 'alert alert-success position-fixed top-0 end-0 m-3';
        toast.style.zIndex = 9999;
        toast.innerHTML = '<i class="fi fi-rr-check me-2"></i>Case created successfully.';
        document.body.appendChild(toast);
        setTimeout(function () { toast.remove(); window.location.href = 'app/cases.html'; }, 1800);
      }
      function onError() {
        btn.disabled  = false;
        btn.innerHTML = 'Submit Case';
        alert('Error creating case. Please try again.');
      }

      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.cases.create(payload).then(onSuccess).catch(onError);
      } else {
        setTimeout(onSuccess, 600);
      }
    });
  });

})();
