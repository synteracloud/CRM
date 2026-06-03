(function () {
  var GW = (function () {
    var h = window.location.hostname;
    return (h === 'localhost' || h === '127.0.0.1')
      ? 'http://localhost:3000'
      : 'https://crm-gateway-l3rm.onrender.com';
  }());

  var form   = document.querySelector('form');
  var btn    = document.querySelector('button[type=submit]');
  var errDiv = null;

  function showError(msg) {
    if (!errDiv) {
      errDiv = document.createElement('div');
      errDiv.className = 'alert alert-danger mt-3';
      form.appendChild(errDiv);
    }
    errDiv.textContent = msg;
    errDiv.style.display = 'block';
  }

  function clearError() { if (errDiv) errDiv.style.display = 'none'; }

  if (!form) return;

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    clearError();

    var name     = (document.getElementById('registerName')     || {}).value || '';
    var email    = (document.getElementById('registerEmail')    || {}).value || '';
    var password = (document.getElementById('registerPassword') || {}).value || '';

    if (!name || !email || !password) { showError('Name, email and password are required.'); return; }
    if (password.length < 8)          { showError('Password must be at least 8 characters.'); return; }

    var terms = document.getElementById('termsConditions');
    if (terms && !terms.checked) { showError('Please accept the terms and conditions.'); return; }

    btn.disabled    = true;
    btn.textContent = 'Creating account…';

    fetch(GW + '/api/v1/auth/register', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ name: name, email: email, password: password }),
    })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok || !res.d.data || !res.d.data.access_token) {
          throw new Error((res.d.error && res.d.error.message) || 'Registration failed.');
        }
        localStorage.setItem('crm_token',     res.d.data.access_token);
        localStorage.setItem('crm_tenant_id', res.d.data.tenant_id);
        window.location.href = 'app/dashboard.html';
      })
      .catch(function (err) {
        showError(err.message || 'Registration failed. Please try again.');
        btn.disabled    = false;
        btn.textContent = 'Sign up';
      });
  });
}());
