"""Pakistan phone number formatter.

Normalizes Pakistani local numbers to E.164 and formats E.164 for local display.

Pakistan dial rules:
  - Country code: +92
  - Local mobile prefix: 03xx → +923xx
  - Local landline: 0xx-xxxxxxx → +92xx-xxxxxxx
  - Digits after country code: 10 digits total (9 after dropping leading 0)

Docs: docs/pakistan-adapter-architecture.md §3.C
"""

from __future__ import annotations

import re


_STRIP_RE = re.compile(r"[\s\-().+]")
_PK_MOBILE_RE = re.compile(r"^(03\d{2})(\d{7})$")       # 0300-1234567
_PK_E164_RE = re.compile(r"^\+92(3\d{2})(\d{7})$")       # +923001234567
_PK_INTL_RE = re.compile(r"^92(3\d{2})(\d{7})$")          # 923001234567 (no +)


class PakistanPhoneFormatter:
    """Implements the PhoneFormatter interface for Pakistan (+92)."""

    COUNTRY_CODE = "+92"

    def normalize_to_e164(self, raw_number: str) -> str:
        digits = _STRIP_RE.sub("", raw_number)

        # Already E.164
        if _PK_E164_RE.match("+" + digits.lstrip("+")):
            return "+" + digits.lstrip("+")
        if _PK_E164_RE.match(raw_number.strip()):
            return raw_number.strip()

        # International without +
        m = _PK_INTL_RE.match(digits)
        if m:
            return f"+92{m.group(1)}{m.group(2)}"

        # Local mobile 03xx-xxxxxxx
        m = _PK_MOBILE_RE.match(digits)
        if m:
            return f"+92{digits[1:]}"

        raise ValueError(
            f"Cannot normalize '{raw_number}' to E.164: "
            "expected Pakistani mobile (03xxxxxxxxxx) or +92 format."
        )

    def format_for_display(self, e164_number: str) -> str:
        m = _PK_E164_RE.match(e164_number)
        if not m:
            return e164_number  # pass-through for non-PK numbers
        return f"0{m.group(1)}-{m.group(2)}"

    def is_valid(self, raw_number: str) -> bool:
        try:
            self.normalize_to_e164(raw_number)
            return True
        except ValueError:
            return False
