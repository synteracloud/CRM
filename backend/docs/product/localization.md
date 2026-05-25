<!-- OWNERSHIP
PRIMARY FOR: RTL layout rules and CSS class conventions (canonical — all 75 frontend pages must comply; ui-foundations.md defers here); locale identifier definitions (en-PK, ur-PK); Urdu string registry format; date/number/currency formatting rules for ur-PK locale; P-017 constraint (Urdu strings must not ship without native speaker sign-off); WhatsApp template locale requirements.
DEFERS TO: ui-foundations.md (design token primitives that RTL rules are applied against); compliance-adapter.md (consent strings are locale-aware but consent rules owned there).
DO NOT RE-DEFINE: Design token values → ui-foundations.md; consent type definitions → compliance-adapter.md; payment/currency data fields → payments-revenue.md.
-->

# Localization / i18n Spec

## Purpose

This document is the canonical spec for internationalization (i18n), right-to-left (RTL) layout, and locale-aware formatting in the Pakistan CRM OS. **CONSTRAINTS.md C-001 states: RTL from day 1 — cannot be retrofitted.** No frontend page can ship without complying with the rules defined here.

**Build gates:** This doc must exist and be read before any of the 75 custom frontend pages are started. The RTL layout rules and CSS class conventions defined here apply to every page, every component, and every WhatsApp-facing template.

---

## 1) Framework Choice

### 1.1 Decision: Custom JSON key-value registry + browser `Intl` for dates/numbers

Rationale:
- **Browser-native `Intl`** handles dates, numbers, and currency formatting correctly for `ur-PK` locale out of the box — no library overhead.
- **Custom JSON key-value registry** (not a third-party i18n library) keeps the dependency surface minimal, works offline, and gives full control over Urdu string review (CONSTRAINTS.md C-010 / P-017).
- Libraries such as `i18next` add 50KB+ and require build tooling that conflicts with the NexLink frontend architecture (no bundler).

### 1.2 Locale Identifiers

| Locale code | Language | Script | Direction |
|---|---|---|---|
| `en-PK` | English | Latin | LTR (default) |
| `ur-PK` | Urdu | Nastaliq/Naskh | RTL |

Active locale codes used throughout this system:
- In API responses: `locale` field uses IETF BCP 47 tags (`en-PK` or `ur-PK`).
- In HTML: `lang` attribute uses `en` or `ur`; `dir` attribute uses `ltr` or `rtl`.
- In JS: `navigator.language` fallback; user preference stored in `localStorage` overrides.

---

## 2) i18n Key Registry

### 2.1 File Structure

```
frontend/src/i18n/
├── en.json          — English strings (source of truth)
├── ur.json          — Urdu strings (requires native-speaker sign-off per C-010 / P-017)
└── registry.js      — Runtime loader; exposes t(key) function
```

### 2.2 Key Format

```
<namespace>.<sub_namespace>.<key>
```

Examples:
```
common.actions.save          → "Save"
common.actions.cancel        → "منسوخ"
common.status.open           → "Open" / "کھلا"
leads.fields.phone_number    → "Phone Number" / "فون نمبر"
followups.states.overdue     → "Overdue" / "وقت گزر گیا"
collections.invoice.amount   → "Amount (PKR)" / "رقم (PKR)"
cases.priority.critical      → "Critical" / "اہم ترین"
auth.login.submit            → "Login" / "داخل ہوں"
errors.not_found             → "Not found" / "نہیں ملا"
errors.unauthorized          → "Unauthorized" / "اجازت نہیں"
whatsapp.templates.followup_reminder.body → see §6
```

### 2.3 Namespace Catalog

| Namespace | Covers |
|---|---|
| `common` | Shared actions (save, cancel, confirm, delete), statuses (open, closed, active), pagination, empty states, loading states |
| `auth` | Login, logout, session expiry, password reset |
| `nav` | Sidebar labels, header menu items, breadcrumbs |
| `leads` | Lead entity fields, stage labels, priority labels |
| `followups` | Follow-up states, enforcement levels, escalation messages |
| `cases` | Case states, priority, SLA labels, support console strings |
| `collections` | Invoice states, payment methods (JazzCash, Easypaisa), reconciliation labels |
| `contacts` | Contact fields, account fields, partner labels |
| `opportunities` | Pipeline stages, deal fields, forecast labels |
| `whatsapp` | Template message bodies (EN + UR variants; see §6) |
| `dashboard` | KPI card labels, chart axes, insight card text |
| `settings` | Settings page labels, configuration field names |
| `errors` | HTTP error messages, validation messages, system error strings |
| `onboarding` | Activation engine checklist labels, sample data labels |
| `territories` | Territory entity fields, routing rule labels |

### 2.4 Key Registry Runtime (registry.js)

```javascript
// frontend/src/i18n/registry.js
const _strings = { en: {}, ur: {} };
let _locale = 'en-PK';

async function loadLocale(locale) {
  const lang = locale.startsWith('ur') ? 'ur' : 'en';
  const res = await fetch(`/i18n/${lang}.json`);
  _strings[lang] = await res.json();
  _locale = locale;
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'ur' ? 'rtl' : 'ltr';
  document.body.classList.toggle('rtl', lang === 'ur');
}

function t(key, vars = {}) {
  const lang = _locale.startsWith('ur') ? 'ur' : 'en';
  const parts = key.split('.');
  let str = parts.reduce((obj, k) => (obj && obj[k] !== undefined ? obj[k] : null), _strings[lang]);
  if (str === null) {
    // Fallback to English if key missing in Urdu registry
    str = parts.reduce((obj, k) => (obj && obj[k] !== undefined ? obj[k] : null), _strings['en']);
  }
  if (str === null) return `[${key}]`; // Missing key indicator for dev
  return str.replace(/\{\{(\w+)\}\}/g, (_, k) => (vars[k] !== undefined ? vars[k] : `{{${k}}}`));
}
```

**Variable interpolation:** `{{var_name}}` inside string values. Example: `"Overdue by {{days}} days"` → `t('followups.states.overdue_by_days', { days: 3 })`.

**Missing key behavior:** Returns `[namespace.key]` in development. In production, falls back to English equivalent. Never throws.

**P-017 gate:** All entries in `ur.json` must be reviewed and approved by a native Urdu speaker before any Urdu-locale messages are sent to customers. Until P-017 is resolved, `ur.json` exists but the locale toggle is not surfaced to end users in production. Internal testing only.

---

## 3) RTL Layout Rules

### 3.1 CSS Architecture

RTL is implemented via a top-level `dir="rtl"` attribute on `<html>` + a `.rtl` class on `<body>`. All RTL-specific overrides live in a single CSS file:

```
frontend/src/css/crm-rtl.css
```

This file is **always loaded** (not conditionally) and uses the `.rtl` class as a selector prefix. This avoids flash-of-wrong-direction and eliminates conditional CSS loading complexity.

```css
/* crm-rtl.css — loaded unconditionally; only applies when .rtl is on body */

.rtl .app-sidebar { left: auto; right: 0; }
.rtl .app-main    { margin-left: 0; margin-right: var(--sidebar-width); }
.rtl .app-header  { flex-direction: row-reverse; }
.rtl .form-label  { text-align: right; }
.rtl .table th,
.rtl .table td    { text-align: right; }
.rtl .card-meta   { text-align: right; }
.rtl .badge       { margin-left: 0; margin-right: 0.375rem; }
.rtl .btn-group   { flex-direction: row-reverse; }
.rtl .pagination  { flex-direction: row-reverse; }
.rtl input[type="text"],
.rtl textarea     { direction: rtl; text-align: right; }
.rtl .chart-label { text-align: right; }
.rtl .icon-left   { margin-left: 0; margin-right: 0.5rem; }
.rtl .breadcrumb  { flex-direction: row-reverse; }
.rtl .breadcrumb-separator::before { content: "\\"; } /* reversed arrow */
```

### 3.2 Direction Toggle Mechanism

1. **Initial detection:** `localStorage.getItem('crm_locale')` → if set, use stored locale. If not set: use `navigator.language` → map to nearest supported locale.
2. **Locale mapping table:**

| `navigator.language` | Resolved locale | Direction |
|---|---|---|
| `ur`, `ur-PK`, `ur-IN` | `ur-PK` | RTL |
| `en`, `en-PK`, `en-US`, `en-GB`, anything else | `en-PK` | LTR |

3. **Toggle:** Locale toggle button in user settings (`settings.html` → Profile tab) calls `loadLocale('ur-PK')` or `loadLocale('en-PK')`, saves to `localStorage('crm_locale')`, and fires a `localechange` custom event that all components listen to.

4. **Page reload:** Not required. All components must be reactive to `localechange` by re-rendering string content without reload. This is enforced as a build constraint.

5. **Persistence:** `localStorage` per browser session. Server-side preference storage (in User profile) is Phase 5 scope.

### 3.3 RTL-Safe Component Rules

| Component | LTR behavior | RTL override |
|---|---|---|
| Sidebar | Fixed left | Fixed right (`.app-sidebar { right: 0; left: auto }`) |
| Content area | Margin-left = sidebar width | Margin-right = sidebar width |
| Header | Logo left, actions right | Logo right, actions left (flex `row-reverse`) |
| Form labels | Left-aligned | Right-aligned |
| Input fields | Text flows LTR | `direction: rtl; text-align: right` |
| Tables | Headers and cells left-aligned | Right-aligned |
| Cards | Icon left of text | Icon right of text |
| Pagination | Prev ← · · · Next → | Next ← · · · Prev → (row-reverse) |
| Toast/alerts | Slide in from right | Slide in from left |
| Charts (labels) | Left-aligned axis labels | Right-aligned |
| WhatsApp chat bubble | Customer bubble left, agent bubble right | Customer bubble right, agent bubble left |

### 3.4 Urdu Typography

**Font:** Noto Nastaliq Urdu (Google Fonts — `https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap`)

**Font loading rule:** Load font asynchronously using `<link rel="preconnect">` + `<link rel="stylesheet">` in `<head>`. Do not block render. Apply to `.rtl` scope only:

```css
.rtl body, .rtl input, .rtl textarea, .rtl select {
  font-family: 'Noto Nastaliq Urdu', serif;
  line-height: 2.0; /* Nastaliq requires more vertical space */
  font-size: 1.05em; /* Nastaliq reads better slightly larger */
}
```

**Line-height rule:** Noto Nastaliq Urdu requires `line-height: 2.0` minimum. Failing to set this causes Urdu text to visually overlap between lines.

**Fallback font stack:** `'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', 'Urdu Typesetting', serif`

---

## 4) Locale-Aware Date and Number Formatting

### 4.1 Date Formatting

All date display uses `Intl.DateTimeFormat` with the resolved locale. Never use `Date.toLocaleDateString()` without explicit locale argument.

**Canonical formatter helper:**

```javascript
function formatDate(dateOrStr, options = {}) {
  const locale = _locale; // from registry.js
  const d = typeof dateOrStr === 'string' ? new Date(dateOrStr) : dateOrStr;
  const defaults = { day: '2-digit', month: '2-digit', year: 'numeric' };
  return new Intl.DateTimeFormat(locale, { ...defaults, ...options }).format(d);
}
```

**Output examples:**

| Locale | Output |
|---|---|
| `en-PK` | `19/05/2026` |
| `ur-PK` | `۱۹/۰۵/۲۰۲۶` (Eastern Arabic numerals) |

**Date-time format (with time):** `{ day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }` — 24-hour clock; Pakistan does not use AM/PM in business contexts.

**Relative time:** Use `Intl.RelativeTimeFormat(locale, { numeric: 'auto' })` for "2 days ago" / "in 3 hours" style displays. Never hardcode English relative strings.

**Islamic calendar:** Not implemented in v1. Islamic calendar display is a Phase 6 option, tracked in PENDING.md.

### 4.2 Currency Formatting

**PKR canonical formatter:**

```javascript
function formatPKR(amount, options = {}) {
  const locale = _locale;
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: 'PKR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    ...options
  }).format(amount);
}
```

**Output examples:**

| Locale | Input | Output |
|---|---|---|
| `en-PK` | 125000 | `Rs 1,25,000` |
| `ur-PK` | 125000 | `₨ ۱,۲۵,۰۰۰` |

**Lakh/Crore notation:** Pakistan uses South Asian number grouping (`1,00,000` = 1 lakh, not `100,000`). `Intl.NumberFormat` with `en-PK` locale handles this automatically. Do not implement manual grouping logic.

**Display rule:** All PKR amounts in the UI are displayed as whole rupees (no paise). Pass `{ minimumFractionDigits: 0, maximumFractionDigits: 0 }` everywhere. The only exception is percentage displays for discount/tax rates: use 2 decimal places.

**Currency symbol display:** Use `Rs` in LTR mode, `₨` in RTL mode (automatically handled by `Intl.NumberFormat` with locale).

### 4.3 Phone Number Formatting

Pakistan mobile numbers: `+92 3XX XXXXXXX` (11 digits with +92 country code).

```javascript
function formatPKPhone(phone) {
  // Accepts: "03001234567", "+923001234567", "923001234567"
  const digits = phone.replace(/\D/g, '');
  const local = digits.startsWith('92') ? digits.slice(2) : digits;
  return `+92 ${local.slice(0, 3)} ${local.slice(3)}`;
}
```

---

## 5) Locale Toggle UI

### 5.1 Placement

Locale toggle appears in two places:
1. **Login page** — bottom-right corner (`dir="ltr"` forced regardless of default, since login uses English or Urdu based on user choice before login).
2. **Authenticated app** — top-right header area, next to user avatar. Uses a small flag + label button: `EN | اردو`.

### 5.2 Behavior

```
Click toggle
  → if current locale = en-PK → call loadLocale('ur-PK')
  → if current locale = ur-PK → call loadLocale('en-PK')
  → save to localStorage('crm_locale')
  → fire CustomEvent('localechange', { detail: { locale } })
  → all t() calls in the DOM re-evaluate without page reload
```

### 5.3 Page Load

```javascript
// In every page's <script> init block:
(async function() {
  const stored = localStorage.getItem('crm_locale') || 'en-PK';
  await loadLocale(stored);
  // Now all t() calls are safe
  renderPage();
})();
```

---

## 6) WhatsApp Template Messages

### 6.1 Template Message Locale Rules

All WhatsApp Business API template messages must have registered variants per language. The system supports `en` and `ur` variants for every customer-facing template.

- Template locale is determined by: (1) customer's preferred language on their `Contact.preferred_locale` field; (2) fallback to tenant's default locale; (3) fallback to `en-PK`.
- Templates approved by Meta/360dialog/Gupshup must be registered under the correct language code (`en` or `ur`).
- **P-017 gate:** No Urdu template may be sent to customers until a native Urdu speaker has reviewed and approved the `ur.json` strings for that template namespace.

### 6.2 Template Registry

All templates are stored in `i18n/ur.json` and `i18n/en.json` under `whatsapp.templates.*` namespace. Each template has a `body` and optional `footer` and `cta_label` fields.

**Template naming convention:** `whatsapp.templates.<template_name>.<field>`

**Registered templates:**

| Template name | EN body | UR body (P-017 gated) |
|---|---|---|
| `followup_reminder` | "Hi {{name}}, just a reminder about {{subject}}. Please reply to confirm." | "السلام علیکم {{name}}، {{subject}} کے بارے میں یاددہانی۔ برائے کرم جواب دیں۔" |
| `invoice_due` | "Hi {{name}}, your invoice of Rs {{amount}} is due on {{due_date}}. Pay via JazzCash: {{jazzcash_number}}." | "السلام علیکم {{name}}، آپ کا Rs {{amount}} کا بل {{due_date}} کو واجب الادا ہے۔ JazzCash سے ادا کریں: {{jazzcash_number}}" |
| `invoice_overdue` | "Hi {{name}}, your invoice of Rs {{amount}} is overdue. Please pay at your earliest." | "السلام علیکم {{name}}، آپ کا Rs {{amount}} کا بل ادائیگی سے گزر چکا ہے۔ جلد ادا کریں۔" |
| `payment_confirmed` | "Hi {{name}}, we received your payment of Rs {{amount}}. Thank you!" | "السلام علیکم {{name}}، Rs {{amount}} کی ادائیگی موصول ہوئی۔ شکریہ!" |
| `case_opened` | "Hi {{name}}, your support case #{{case_number}} has been created. We'll respond within {{sla_hours}} hours." | "السلام علیکم {{name}}، آپ کا سپورٹ کیس نمبر #{{case_number}} بن گیا۔ ہم {{sla_hours}} گھنٹوں میں جواب دیں گے۔" |
| `case_resolved` | "Hi {{name}}, your case #{{case_number}} has been resolved. Reply REOPEN if you need further help." | "السلام علیکم {{name}}، کیس نمبر #{{case_number}} حل ہو گیا۔ مزید مدد کے لیے REOPEN لکھیں۔" |
| `followup_escalation` | "Hi {{name}}, your request has been escalated to our manager. They'll contact you shortly." | "السلام علیکم {{name}}، آپ کی درخواست منیجر کو بھیج دی گئی ہے۔ وہ جلد رابطہ کریں گے۔" |
| `daily_digest` | "Good morning {{name}}. Today: {{open_leads}} leads open, {{overdue_tasks}} tasks overdue, {{pending_invoices}} invoices pending." | "صبح بخیر {{name}}۔ آج: {{open_leads}} لیڈز کھلی، {{overdue_tasks}} کام باقی، {{pending_invoices}} انوائس زیر التواء۔" |

### 6.3 Template Variable Escaping

- All `{{var_name}}` values must be HTML-entity-escaped before insertion.
- Do not allow raw user input directly into WhatsApp template bodies. Names and subjects must come from the CRM entity record only.

---

## 7) Urdu Input Support

### 7.1 Input Fields

- All `<input type="text">` and `<textarea>` elements support Urdu character entry natively via OS keyboard.
- No custom keyboard or virtual input required.
- Fields that may receive Urdu input must have `lang="ur"` attribute when locale is `ur-PK` (helps mobile OS keyboard selection).

### 7.2 Search

- Search queries submitted in Urdu are passed as-is to the backend.
- Backend search must use case-insensitive collation and Unicode normalization (NFC) before matching.
- Diacritics (`harakat`) are stripped from search terms before matching (use regex `/[ً-ٰٟ]/g`).

### 7.3 Number Input

- When locale is `ur-PK`, numeric input fields still accept Western Arabic digits (`0-9`) — users can enter numbers with standard keyboard. Eastern Arabic digit display is for output only.

---

## 8) Constraints and Invariants

1. **C-001 (non-negotiable):** RTL layout is applied from the first page. No page may ship without `crm-rtl.css` loaded and RTL CSS rules verified.
2. **P-017 gate:** No Urdu string may reach a customer via WhatsApp or any channel until native-speaker review is complete. The locale toggle may show Urdu in the UI, but outbound customer messages require the P-017 sign-off.
3. **Fallback invariant:** Missing Urdu key always falls back to English. Never returns a `[key]` placeholder in production for English keys — if English key is missing, it is a build error.
4. **Bundle constraint:** `i18n/en.json` and `i18n/ur.json` are loaded once per locale switch. They must be kept under 100KB each (uncompressed). If they grow beyond this, split by namespace.
5. **No hardcoded strings rule:** No user-facing string literal may appear directly in HTML or JS. All strings must reference `t('key')`. This is enforced in code review.
6. **Date storage rule:** All dates are stored and transported as ISO 8601 UTC strings. Locale-specific formatting happens only at display layer. Never store formatted dates.

---

## 9) Implementation Acceptance Checklist

- [ ] `frontend/src/i18n/en.json` created with all 14 namespaces.
- [ ] `frontend/src/i18n/ur.json` created (internal testing only; P-017 review gate in place).
- [ ] `frontend/src/i18n/registry.js` created with `loadLocale()`, `t()`, fallback to English, variable interpolation.
- [ ] `frontend/src/css/crm-rtl.css` created with all component RTL overrides.
- [ ] Noto Nastaliq Urdu loaded via Google Fonts preconnect in all pages.
- [ ] Locale toggle button present in login page (bottom-right) and authenticated header (top-right).
- [ ] `loadLocale()` called on page init from `localStorage`.
- [ ] `localechange` event fires and all component strings re-render without page reload.
- [ ] `formatPKR()` and `formatDate()` helpers verified for both locales.
- [ ] `formatPKPhone()` helper verified for all input formats.
- [ ] All 8 WhatsApp templates registered in `en.json` and `ur.json`.
- [ ] No hardcoded user-facing strings in any HTML or JS file (code review gate).
- [ ] RTL verified on all 75 custom pages before Phase 5 sign-off.
