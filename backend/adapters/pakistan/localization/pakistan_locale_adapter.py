"""Pakistan locale adapter: PKR currency formatting, datetime display, and EN/UR strings.

Docs: docs/pakistan-adapter-architecture.md §3.D, §3.E, §3.F
"""

from __future__ import annotations

from datetime import datetime, timezone

from adapters.interfaces.locale_adapter import DateFormatInput, MoneyFormatInput, MoneyFormatResult

_MINOR_UNITS: dict[str, int] = {
    "PKR": 2,
    "USD": 2,
    "EUR": 2,
    "GBP": 2,
    "JPY": 0,
    "KWD": 3,
}

_CURRENCY_SYMBOLS: dict[str, str] = {
    "PKR": "Rs.",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
}


class PakistanLocaleAdapter:
    """Implements the LocaleAdapter interface for Pakistan (PKR, Urdu/English)."""

    def format_money(self, input: MoneyFormatInput) -> MoneyFormatResult:
        minor = self.currency_minor_units(input.currency)
        symbol = _CURRENCY_SYMBOLS.get(input.currency, input.currency)
        if minor == 0:
            major = input.amount_minor
            formatted = f"{symbol} {major:,}"
        else:
            factor = 10 ** minor
            major = input.amount_minor / factor
            formatted = f"{symbol} {major:,.{minor}f}"
        return MoneyFormatResult(
            formatted=formatted,
            currency_symbol=symbol,
            decimal_places=minor,
        )

    def format_date(self, input: DateFormatInput) -> str:
        try:
            dt = datetime.fromisoformat(input.iso_datetime.replace("Z", "+00:00"))
        except ValueError:
            return input.iso_datetime

        if input.format_style == "long":
            return dt.strftime("%d %B %Y, %I:%M %p")
        if input.format_style == "relative":
            delta = datetime.now(timezone.utc) - dt
            seconds = int(delta.total_seconds())
            if seconds < 60:
                return "just now"
            if seconds < 3600:
                return f"{seconds // 60}m ago"
            if seconds < 86400:
                return f"{seconds // 3600}h ago"
            return f"{seconds // 86400}d ago"
        # short (default)
        return dt.strftime("%d/%m/%Y")

    def currency_minor_units(self, currency_code: str) -> int:
        return _MINOR_UNITS.get(currency_code.upper(), 2)

    def get_string(self, key: str, locale: str = "en") -> str:
        """Return a locale-aware string for UI/message templates.

        Supported locales: "en" (English, default), "ur" (Urdu).
        Falls back to English if Urdu translation missing. Returns key if not found.

        Urdu strings use Unicode UTF-8; rendering requires RTL text support in UI layer.
        """
        lang = locale.lower() if locale.lower() in _STRINGS else "en"
        return _STRINGS[lang].get(key) or _STRINGS["en"].get(key) or key


# ── Bilingual string registry (EN + UR) ──────────────────────────────────────
# Keys: dot-separated descriptors. Urdu text is UTF-8 Unicode.
# Note: Urdu translations must be reviewed by a native speaker before production.
_STRINGS: dict[str, dict[str, str]] = {
    "en": {
        # Reminder tones — polite (pre-due)
        "reminder.polite.greeting": "Dear {name},",
        "reminder.polite.body": "This is a friendly reminder that invoice #{invoice_no} for {amount} is due on {due_date}. Kindly arrange payment at your earliest convenience.",
        "reminder.polite.footer": "Thank you for your continued business.",
        # Reminder tones — firm (1–7 days overdue)
        "reminder.firm.greeting": "Dear {name},",
        "reminder.firm.body": "Your invoice #{invoice_no} for {amount} was due on {due_date} and remains unpaid. Please make payment as soon as possible.",
        "reminder.firm.footer": "If you have already paid, kindly share your payment confirmation.",
        # Reminder tones — urgent (8+ days overdue)
        "reminder.urgent.greeting": "Dear {name},",
        "reminder.urgent.body": "Invoice #{invoice_no} for {amount} is now {overdue_days} days overdue. Immediate payment is required to avoid further action.",
        "reminder.urgent.footer": "Please contact us urgently if you need to discuss a payment plan.",
        # Follow-up suggestions
        "followup.suggestion.call": "Call {name} — no response for {days} days",
        "followup.suggestion.send_whatsapp": "Send WhatsApp to {name} — follow-up due",
        "followup.suggestion.send_reminder": "Send payment reminder — invoice due {when}",
        # System notifications
        "notification.lead_captured": "Your first lead is in the system. It won't slip away.",
        "notification.followup_done": "Follow-up done. Next one scheduled automatically.",
        "notification.payment_recorded": "Payment recorded. Invoice updated.",
    },
    "ur": {
        # Reminder tones — polite (pre-due) [Urdu]
        "reminder.polite.greeting": "محترم {name}،",
        "reminder.polite.body": "آپ کو یاد دہانی کرائی جاتی ہے کہ انوائس نمبر #{invoice_no} کی رقم {amount} کی ادائیگی کی تاریخ {due_date} ہے۔ برائے مہربانی جلد از جلد ادائیگی فرمائیں۔",
        "reminder.polite.footer": "آپ کے کاروباری تعلق کا شکریہ۔",
        # Reminder tones — firm (1–7 days overdue) [Urdu]
        "reminder.firm.greeting": "محترم {name}،",
        "reminder.firm.body": "آپ کی انوائس نمبر #{invoice_no} کی رقم {amount} کی ادائیگی کی تاریخ {due_date} گزر چکی ہے۔ براہ کرم جلد ادائیگی فرمائیں۔",
        "reminder.firm.footer": "اگر آپ نے ادائیگی کر دی ہے تو ادائیگی کی تصدیق شیئر فرمائیں۔",
        # Reminder tones — urgent (8+ days overdue) [Urdu]
        "reminder.urgent.greeting": "محترم {name}،",
        "reminder.urgent.body": "انوائس نمبر #{invoice_no} کی رقم {amount} کی ادائیگی {overdue_days} دن سے واجب الادا ہے۔ فوری ادائیگی ضروری ہے۔",
        "reminder.urgent.footer": "ادائیگی کے منصوبے کے لیے ہم سے فوری رابطہ فرمائیں۔",
    },
}
