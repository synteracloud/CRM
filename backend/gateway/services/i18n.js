'use strict';

/**
 * Bilingual string registry + RTL layout — P-013.
 *
 * Docs: docs/pakistan-adapter-architecture.md §3.E, §3.F
 *       docs/adoption-ux.md §1 (principle 3 — Natural habit alignment)
 *       adapters/pakistan/localization/pakistan_locale_adapter.py (Python twin)
 *
 * Supported locales: "en" (English, LTR), "ur" (Urdu, RTL).
 * Falls back to English if Urdu translation is missing.
 * Returns the key itself if neither locale has the string.
 *
 * All UI code must call getString() for every user-visible label.
 * No hardcoded EN strings in components.
 *
 * IMPORTANT: Urdu strings must be reviewed by a native speaker before production (P-017).
 *
 * Usage::
 *   const { getString, isRtl, formatMoney, LOCALE_DIR } = require('./i18n');
 *   const label = getString('nav.leads', req.locale);
 *   const dir   = LOCALE_DIR[req.locale] || 'ltr';
 */

// ── RTL configuration ─────────────────────────────────────────────────────────

const RTL_LOCALES = new Set(['ur', 'ar', 'he', 'fa']);

const LOCALE_DIR = Object.freeze({
  en: 'ltr',
  ur: 'rtl',
});

/**
 * Return true if the locale requires right-to-left layout.
 * Affects: flex-direction, text-align, icon placement, form field order.
 */
function isRtl(locale) {
  return RTL_LOCALES.has((locale || 'en').toLowerCase());
}

// ── Money formatting ──────────────────────────────────────────────────────────

const CURRENCY_SYMBOLS = { PKR: 'Rs.', USD: '$', EUR: '€', GBP: '£' };
const CURRENCY_DECIMALS = { PKR: 0, JPY: 0, KWD: 3 };

/**
 * Format a monetary amount for display.
 *
 * @param {number} amount      — amount in major units (e.g. 1500 = Rs. 1,500)
 * @param {string} currency    — ISO 4217 code (default "PKR")
 * @param {string} [locale]    — "en" | "ur" (affects symbol placement)
 * @returns {string}
 */
function formatMoney(amount, currency = 'PKR', locale = 'en') {
  const symbol   = CURRENCY_SYMBOLS[currency] || currency;
  const decimals = CURRENCY_DECIMALS[currency] ?? 2;
  const formatted = Number(amount).toLocaleString('en-PK', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  return `${symbol} ${formatted}`;
}

// ── String registry ────────────────────────────────────────────────────────────
// Note: Urdu text is UTF-8 Unicode.  Urdu translations flagged for P-017 review.

const _STRINGS = Object.freeze({
  en: {
    // ── Navigation ───────────────────────────────────────────────────────────
    'nav.leads':           'Leads',
    'nav.followups':       'Follow-ups',
    'nav.collections':     'Collections',
    'nav.opportunities':   'Opportunities',
    'nav.contacts':        'Contacts',
    'nav.reports':         'Reports',
    'nav.settings':        'Settings',
    'nav.workflows':       'Workflows',
    'nav.team':            'Team',
    'nav.audit':           'Audit Log',

    // ── Quick actions ────────────────────────────────────────────────────────
    'action.new_lead':        'New Lead',
    'action.record_payment':  'Record Payment',
    'action.send_followup':   'Send Follow-up',
    'action.log_done':        'Done',
    'action.snooze':          'Snooze',
    'action.view_all':        'View All',
    'action.save':            'Save',
    'action.cancel':          'Cancel',
    'action.confirm':         'Confirm',
    'action.retry':           'Retry',
    'action.close':           'Close',

    // ── Lead statuses / stages ────────────────────────────────────────────────
    'stage.new':          'New',
    'stage.qualified':    'Qualified',
    'stage.proposal':     'Proposal',
    'stage.negotiation':  'Negotiation',
    'stage.won':          'Won',
    'stage.lost':         'Lost',
    'status.open':        'Open',
    'status.working':     'Working',
    'status.closed':      'Closed',

    // ── Priority labels ───────────────────────────────────────────────────────
    'priority.urgent': 'Urgent',
    'priority.high':   'High',
    'priority.medium': 'Medium',
    'priority.low':    'Low',
    'priority.hot':    'Hot',
    'priority.warm':   'Warm',
    'priority.cold':   'Cold',

    // ── Follow-up / next-action card ──────────────────────────────────────────
    'next_action.title':         'Next Action',
    'next_action.due_by':        'Due by {when}',
    'next_action.overdue':       'Overdue',
    'next_action.call':          'Call',
    'next_action.send_whatsapp': 'Send WhatsApp',
    'next_action.send_reminder': 'Send Reminder',
    'next_action.escalate':      'Escalate',
    'next_action.close':         'Close Lead',

    // ── Collections ──────────────────────────────────────────────────────────
    'invoice.state.unpaid':   'Unpaid',
    'invoice.state.partial':  'Partial',
    'invoice.state.paid':     'Paid',
    'invoice.state.overdue':  'Overdue',
    'invoice.due_in':         'Due in {days} days',
    'invoice.overdue_by':     'Overdue by {days} days',
    'invoice.record_payment': 'Record Payment',

    // ── System notifications (adoption-ux.md §4) ─────────────────────────────
    'notification.lead_captured':      'Your first lead is in the system. It won\'t slip away.',
    'notification.followup_done':      'Follow-up done. Next one scheduled automatically.',
    'notification.payment_recorded':   'Payment recorded. Invoice updated.',
    'notification.reminder_sent':      'Reminder sent. You\'ll be notified when they respond.',

    // ── Reminder tones (mirror Python adapter) ────────────────────────────────
    'reminder.polite.greeting':        'Dear {name},',
    'reminder.polite.body':            'This is a friendly reminder that invoice #{invoice_no} for {amount} is due on {due_date}. Kindly arrange payment at your earliest convenience.',
    'reminder.polite.footer':          'Thank you for your continued business.',
    'reminder.firm.greeting':          'Dear {name},',
    'reminder.firm.body':              'Your invoice #{invoice_no} for {amount} was due on {due_date} and remains unpaid. Please make payment as soon as possible.',
    'reminder.firm.footer':            'If you have already paid, kindly share your payment confirmation.',
    'reminder.urgent.greeting':        'Dear {name},',
    'reminder.urgent.body':            'Invoice #{invoice_no} for {amount} is now {overdue_days} days overdue. Immediate payment is required to avoid further action.',
    'reminder.urgent.footer':          'Please contact us urgently if you need to discuss a payment plan.',

    // ── Follow-up suggestions ────────────────────────────────────────────────
    'followup.suggestion.call':           'Call {name} — no response for {days} days',
    'followup.suggestion.send_whatsapp':  'Send WhatsApp to {name} — follow-up due',
    'followup.suggestion.send_reminder':  'Send payment reminder — invoice due {when}',

    // ── Empty states ─────────────────────────────────────────────────────────
    'empty.leads':       'No leads yet. Tap "New Lead" to add your first.',
    'empty.followups':   'No follow-ups due. You\'re all caught up.',
    'empty.invoices':    'No outstanding invoices.',
    'empty.no_results':  'No results found. Try adjusting your filters.',

    // ── Errors ────────────────────────────────────────────────────────────────
    'error.generic':          'Something went wrong. Please try again.',
    'error.offline':          'You\'re offline. Changes will sync when you reconnect.',
    'error.session_expired':  'Your session has expired. Please log in again.',
    'error.permission':       'You don\'t have permission to perform this action.',
  },

  ur: {
    // ── Navigation ───────────────────────────────────────────────────────────
    'nav.leads':           'لیڈز',
    'nav.followups':       'فالو اپ',
    'nav.collections':     'وصولیاں',
    'nav.opportunities':   'مواقع',
    'nav.contacts':        'رابطے',
    'nav.reports':         'رپورٹس',
    'nav.settings':        'ترتیبات',
    'nav.workflows':       'ورک فلو',
    'nav.team':            'ٹیم',
    'nav.audit':           'آڈٹ لاگ',

    // ── Quick actions ────────────────────────────────────────────────────────
    'action.new_lead':        'نیا لیڈ',
    'action.record_payment':  'ادائیگی درج کریں',
    'action.send_followup':   'فالو اپ بھیجیں',
    'action.log_done':        'مکمل',
    'action.snooze':          'مؤخر کریں',
    'action.view_all':        'سب دیکھیں',
    'action.save':            'محفوظ کریں',
    'action.cancel':          'منسوخ',
    'action.confirm':         'تصدیق',
    'action.retry':           'دوبارہ کوشش',
    'action.close':           'بند کریں',

    // ── Lead stages ──────────────────────────────────────────────────────────
    'stage.new':          'نیا',
    'stage.qualified':    'اہل',
    'stage.proposal':     'تجویز',
    'stage.negotiation':  'گفت و شنید',
    'stage.won':          'کامیاب',
    'stage.lost':         'ناکام',
    'status.open':        'کھلا',
    'status.working':     'جاری',
    'status.closed':      'بند',

    // ── Priority ─────────────────────────────────────────────────────────────
    'priority.urgent': 'فوری',
    'priority.high':   'زیادہ',
    'priority.medium': 'درمیانہ',
    'priority.low':    'کم',
    'priority.hot':    'گرم',
    'priority.warm':   'معتدل',
    'priority.cold':   'ٹھنڈا',

    // ── Next action card ─────────────────────────────────────────────────────
    'next_action.title':         'اگلا قدم',
    'next_action.due_by':        'آخری تاریخ {when}',
    'next_action.overdue':       'مقررہ وقت گزر گیا',
    'next_action.call':          'کال کریں',
    'next_action.send_whatsapp': 'واٹس ایپ بھیجیں',
    'next_action.send_reminder': 'یاد دہانی بھیجیں',
    'next_action.escalate':      'اعلیٰ سطح پر بھیجیں',
    'next_action.close':         'لیڈ بند کریں',

    // ── Collections ──────────────────────────────────────────────────────────
    'invoice.state.unpaid':   'غیر ادا شدہ',
    'invoice.state.partial':  'جزوی ادا',
    'invoice.state.paid':     'ادا شدہ',
    'invoice.state.overdue':  'واجب الادا',
    'invoice.due_in':         '{days} دن میں واجب',
    'invoice.overdue_by':     '{days} دن سے واجب الادا',
    'invoice.record_payment': 'ادائیگی درج کریں',

    // ── System notifications ──────────────────────────────────────────────────
    'notification.lead_captured':    'آپ کا پہلا لیڈ سسٹم میں ہے۔ یہ ضائع نہیں ہوگا۔',
    'notification.followup_done':    'فالو اپ مکمل۔ اگلا خود بخود شیڈول ہو گیا۔',
    'notification.payment_recorded': 'ادائیگی درج ہو گئی۔ انوائس اپ ڈیٹ ہو گئی۔',
    'notification.reminder_sent':    'یاد دہانی بھیج دی گئی۔ جواب ملنے پر آپ کو مطلع کیا جائے گا۔',

    // ── Reminder tones (mirror Python adapter) ────────────────────────────────
    'reminder.polite.greeting': 'محترم {name}،',
    'reminder.polite.body':     'آپ کو یاد دہانی کرائی جاتی ہے کہ انوائس نمبر #{invoice_no} کی رقم {amount} کی ادائیگی کی تاریخ {due_date} ہے۔ برائے مہربانی جلد از جلد ادائیگی فرمائیں۔',
    'reminder.polite.footer':   'آپ کے کاروباری تعلق کا شکریہ۔',
    'reminder.firm.greeting':   'محترم {name}،',
    'reminder.firm.body':       'آپ کی انوائس نمبر #{invoice_no} کی رقم {amount} کی ادائیگی کی تاریخ {due_date} گزر چکی ہے۔ براہ کرم جلد ادائیگی فرمائیں۔',
    'reminder.firm.footer':     'اگر آپ نے ادائیگی کر دی ہے تو ادائیگی کی تصدیق شیئر فرمائیں۔',
    'reminder.urgent.greeting': 'محترم {name}،',
    'reminder.urgent.body':     'انوائس نمبر #{invoice_no} کی رقم {amount} کی ادائیگی {overdue_days} دن سے واجب الادا ہے۔ فوری ادائیگی ضروری ہے۔',
    'reminder.urgent.footer':   'ادائیگی کے منصوبے کے لیے ہم سے فوری رابطہ فرمائیں۔',

    // ── Empty states ─────────────────────────────────────────────────────────
    'empty.leads':      'ابھی تک کوئی لیڈ نہیں۔ "نیا لیڈ" دبائیں۔',
    'empty.followups':  'کوئی فالو اپ باقی نہیں۔ آپ نے سب مکمل کر لیے۔',
    'empty.invoices':   'کوئی واجب الادا انوائس نہیں۔',
    'empty.no_results': 'کوئی نتیجہ نہیں ملا۔ فلٹر تبدیل کریں۔',

    // ── Errors ────────────────────────────────────────────────────────────────
    'error.generic':         'کچھ غلط ہو گیا۔ دوبارہ کوشش کریں۔',
    'error.offline':         'آپ آف لائن ہیں۔ کنکشن بحال ہونے پر تبدیلیاں ہم آہنگ ہوں گی۔',
    'error.session_expired': 'آپ کا سیشن ختم ہو گیا۔ دوبارہ لاگ ان کریں۔',
    'error.permission':      'آپ کو یہ کام کرنے کی اجازت نہیں۔',
  },
});

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Return a locale-aware string.  Falls back to English; returns key if not found.
 *
 * @param {string} key    — dot-separated string key
 * @param {string} locale — "en" | "ur" (default "en")
 * @returns {string}
 */
function getString(key, locale = 'en') {
  const lang = _STRINGS[locale] ? locale : 'en';
  return _STRINGS[lang]?.[key] ?? _STRINGS['en']?.[key] ?? key;
}

/**
 * Interpolate `{placeholder}` values in a string.
 *
 * @param {string} template — output of getString()
 * @param {object} vars     — { name: 'Ali', days: 3 }
 * @returns {string}
 */
function interpolate(template, vars = {}) {
  return template.replace(/\{(\w+)\}/g, (_, k) => (vars[k] !== undefined ? vars[k] : `{${k}}`));
}

module.exports = {
  getString,
  interpolate,
  isRtl,
  formatMoney,
  LOCALE_DIR,
  RTL_LOCALES,
};
