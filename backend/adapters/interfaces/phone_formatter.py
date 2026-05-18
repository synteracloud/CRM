"""Canonical PhoneFormatter interface for E.164 normalization and local output.

Docs: docs/pakistan-adapter-architecture.md §3.C
      docs/architecture-overview.md Layer Model (L2 Interfaces)

Rules:
- Core always stores phone numbers in E.164 format (e.g. "+923001234567").
- Adapters normalize local input to E.164 on ingest.
- Adapters format E.164 to local display on output.
- Invalid numbers raise ValueError — never silently truncate.
"""

from __future__ import annotations

from typing import Protocol


class PhoneFormatter(Protocol):
    """Country-specific phone number normalization and display formatting."""

    def normalize_to_e164(self, raw_number: str) -> str:
        """Parse any local format and return E.164 string (e.g. '+923001234567').

        Raises ValueError if number cannot be normalized to valid E.164.
        """
        ...

    def format_for_display(self, e164_number: str) -> str:
        """Format an E.164 number for human-readable local display.

        E.g. "+923001234567" → "0300-1234567" for Pakistan.
        """
        ...

    def is_valid(self, raw_number: str) -> bool:
        """Return True if the raw number can be normalized to a valid E.164."""
        ...
