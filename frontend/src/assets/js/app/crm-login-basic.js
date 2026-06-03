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

    var email    = (document.getElementById('loginEmail')    || {}).value || '';
    var password = (document.getElementById('loginPassword') || {}).value || '';

    if (!email || !password) { showError('Email and password are required.'); return; }

    btn.disabled    = true;
    btn.textContent = 'Signing in…';

    fetch(GW + '/api/v1/auth/login', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ email: email, password: password }),
    })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok || !res.d.data || !res.d.data.access_token) {
          throw new Error((res.d.error && res.d.error.message) || 'Login failed.');
        }
        localStorage.setItem('crm_token',     res.d.data.access_token);
        localStorage.setItem('crm_tenant_id', res.d.data.tenant_id);
        window.location.href = 'app/dashboard.html';
      })
      .catch(function (err) {
        showError(err.message || 'Login failed. Check your credentials.');
        btn.disabled    = false;
        btn.textContent = 'Login';
      });
  });
}());
