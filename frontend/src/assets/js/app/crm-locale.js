/* Pakistan CRM — RTL / Locale Switcher (loads last on every page) */
(function () {
  'use strict';

  function setLocale(locale) {
    const html    = document.documentElement;
    const cssLink = document.getElementById('main-stylesheet');
    if (!cssLink) return;
    if (locale === 'ur') {
      html.setAttribute('dir', 'rtl');
      html.setAttribute('lang', 'ur');
      cssLink.href = cssLink.href.replace('styles.css', 'styles-rtl.css');
    } else {
      html.setAttribute('dir', 'ltr');
      html.setAttribute('lang', 'en');
      cssLink.href = cssLink.href.replace('styles-rtl.css', 'styles.css');
    }
    localStorage.setItem('crm_locale', locale);
    /* Update toggle button state if present */
    const btn = document.getElementById('crm-locale-toggle');
    if (btn) btn.textContent = locale === 'ur' ? 'EN' : 'اردو';
  }

  /* Apply saved locale on every page load */
  const saved = localStorage.getItem('crm_locale') || 'en';
  setLocale(saved);

  /* Expose for header toggle button */
  window.CRM = window.CRM || {};
  window.CRM.setLocale = setLocale;
})();
