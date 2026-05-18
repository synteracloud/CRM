"""Canonical LocaleAdapter interface for currency, datetime, and bilingual string formatting.

Docs: docs/pakistan-adapter-architecture.md §3.D, §3.E
      docs/architecture-overview.md Layer Model (L2 Interfaces)

Rules:
- All formatting is presentation-layer only — no domain rule branches by locale.
- Core stores amounts in minor units (integer). Adapter handles display conversion.
- Dates stored as ISO-8601 UTC. Adapter handles local rendering only.
- String keys are adapter-defined; unknown keys fall back to the key itself (never raise).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class MoneyFormatInput:
    amount_minor: int    # e.g. 10050 = PKR 100.50
    currency: str        # ISO-4217 e.g. "PKR", "USD"


@dataclass(frozen=True)
class MoneyFormatResult:
    formatted: str           # e.g. "PKR 100.50" or "Rs. 100.50"
    currency_symbol: str     # e.g. "Rs." or "₨"
    decimal_places: int      # 2 for PKR, 0 for JPY, etc.


@dataclass(frozen=True)
class DateFormatInput:
    iso_datetime: str               # ISO-8601 UTC string
    format_style: str = "short"     # "short" | "long" | "relative"


class LocaleAdapter(Protocol):
    """Country-specific formatting for money, dates, and bilingual strings."""

    def format_money(self, input: MoneyFormatInput) -> MoneyFormatResult: ...

    def format_date(self, input: DateFormatInput) -> str: ...

    def currency_minor_units(self, currency_code: str) -> int:
        """Return the number of minor units for a given currency (e.g. 2 for PKR)."""
        ...

    def get_string(self, key: str, locale: str = "en") -> str:
        """Return a locale-aware UI/message string for the given key.

        Args:
            key:    Dot-separated string key (e.g. "reminder.polite.greeting").
            locale: ISO 639-1 language code. Supported: "en" (default), "ur" (Urdu).
                    If the key has no translation for the requested locale, falls back
                    to English — never raises.

        Returns:
            The localised string value, or `key` itself if not found in any locale.
        """
        ...
