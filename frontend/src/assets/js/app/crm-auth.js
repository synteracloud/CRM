/* Pakistan CRM — Auth Page Logic */
document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  /* ── Login ────────────────────────────────────────────────────── */
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const email    = document.getElementById('loginEmail').value.trim();
      const password = document.getElementById('loginPassword').value;
      const errEl    = document.getElementById('loginError');
      const btn      = document.getElementById('loginBtn');
      const spinner  = document.getElementById('loginSpinner');
      const btnText  = document.getElementById('loginBtnText');

      btn.disabled = true; spinner.classList.remove('d-none'); btnText.textContent = 'Signing in…';
      errEl.classList.add('d-none');

      try {
        const res = await window.CRM_API.auth.login(email, password);
        localStorage.setItem('crm_token', res.data.token);
        localStorage.setItem('crm_user', JSON.stringify(res.data.user));
        window.location.href = '/app/dashboard.html';
      } catch (err) {
        errEl.textContent = (err && err.error && err.error.message) || 'Invalid email or password.';
        errEl.classList.remove('d-none');
      } finally {
        btn.disabled = false; spinner.classList.add('d-none'); btnText.textContent = 'Sign In';
      }
    });
  }

  /* ── Register ─────────────────────────────────────────────────── */
  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    registerForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const btn     = document.getElementById('registerBtn');
      const spinner = document.getElementById('registerSpinner');
      const errEl   = document.getElementById('registerError');
      btn.disabled = true; spinner.classList.remove('d-none');

      try {
        /* In dummy mode: simulate success */
        await new Promise(r => setTimeout(r, 800));
        window.location.href = '/app/dashboard.html';
      } catch (err) {
        errEl.textContent = 'Registration failed. Please try again.';
        errEl.classList.remove('d-none');
      } finally {
        btn.disabled = false; spinner.classList.add('d-none');
      }
    });
  }


});
