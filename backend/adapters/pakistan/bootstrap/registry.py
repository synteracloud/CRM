"""Adapter registry — resolves CountryAdapterBundle from environment config.

Docs: docs/pakistan-adapter-architecture.md §6.1 (Plug-and-Play Registry)
      docs/architecture-overview.md §2 (L3 Adapters)

Usage:
    bundle = resolve_adapters("PK")
    result = bundle.payment.create_payment(input, ctx)

Configuration via environment variables:
    COUNTRY              — "PK" (default)
    MESSAGING_PROVIDER   — "meta" | "twilio" | "360dialog" | "gupshup"  (default: meta)
    PAYMENT_PROVIDER     — "jazzcash" | "easypaisa"                      (default: jazzcash)
    COMPLIANCE_PK_ENABLED — "true" | "false"                             (default: false)

No core code changes required when swapping providers.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from adapters.interfaces.compliance_adapter import ComplianceAdapter, NoopComplianceAdapter
from adapters.interfaces.locale_adapter import LocaleAdapter
from adapters.interfaces.messaging_adapter import MessagingAdapter
from adapters.interfaces.payment_adapter import PaymentAdapter
from adapters.interfaces.phone_formatter import PhoneFormatter


@dataclass(frozen=True)
class CountryAdapterBundle:
    payment: PaymentAdapter
    messaging: MessagingAdapter
    compliance: ComplianceAdapter
    phone: PhoneFormatter
    locale: LocaleAdapter
    country_code: str


def resolve_adapters(country_code: str | None = None) -> CountryAdapterBundle:
    """Resolve the full adapter bundle for the given country code.

    Reads provider selection from environment variables.
    Raises ValueError for unsupported country codes.
    """
    code = (country_code or os.environ.get("COUNTRY", "PK")).upper()

    if code == "PK":
        return _build_pakistan_bundle()

    raise ValueError(
        f"No adapter bundle registered for country '{code}'. "
        "Add adapters/<country>/ and register in this registry."
    )


# ── Pakistan bundle ────────────────────────────────────────────────────────────

def _build_pakistan_bundle() -> CountryAdapterBundle:
    from adapters.pakistan.localization.pakistan_locale_adapter import PakistanLocaleAdapter
    from adapters.pakistan.localization.pakistan_phone_formatter import PakistanPhoneFormatter

    return CountryAdapterBundle(
        payment=_resolve_pk_payment(),
        messaging=_resolve_pk_messaging(),
        compliance=_resolve_pk_compliance(),
        phone=PakistanPhoneFormatter(),
        locale=PakistanLocaleAdapter(),
        country_code="PK",
    )


def _resolve_pk_payment() -> PaymentAdapter:
    provider = os.environ.get("PAYMENT_PROVIDER", "jazzcash").lower()
    merchant_id = os.environ.get("PK_MERCHANT_ID", "test_merchant")
    secret = os.environ.get("PK_PAYMENT_SECRET", "test_secret")

    if provider == "jazzcash":
        from adapters.pakistan.payments.jazzcash import JazzCashAdapter
        return JazzCashAdapter(merchant_id=merchant_id, secret=secret)

    if provider == "easypaisa":
        from adapters.pakistan.payments.easypaisa import EasypaisaAdapter
        return EasypaisaAdapter(merchant_id=merchant_id, secret=secret)

    raise ValueError(f"Unknown PAYMENT_PROVIDER '{provider}' for PK. Expected: jazzcash | easypaisa")


def _resolve_pk_messaging() -> MessagingAdapter:
    provider = os.environ.get("MESSAGING_PROVIDER", "meta").lower()

    if provider == "meta":
        from adapters.pakistan.messaging.meta_api_adapter import MetaWhatsAppAdapter
        return MetaWhatsAppAdapter()

    if provider == "twilio":
        from adapters.pakistan.messaging.twilio_adapter import TwilioWhatsAppAdapter
        return TwilioWhatsAppAdapter()

    if provider == "360dialog":
        api_key = os.environ.get("DIALOG360_API_KEY", "")
        webhook_secret = os.environ.get("DIALOG360_WEBHOOK_SECRET", "")
        from adapters.pakistan.messaging.dialog360_adapter import Dialog360Adapter
        return Dialog360Adapter(api_key=api_key, webhook_secret=webhook_secret)

    if provider == "gupshup":
        api_key = os.environ.get("GUPSHUP_API_KEY", "")
        app_name = os.environ.get("GUPSHUP_APP_NAME", "crm")
        source_number = os.environ.get("GUPSHUP_SOURCE_NUMBER", "")
        from adapters.pakistan.messaging.gupshup_adapter import GupshupAdapter
        return GupshupAdapter(api_key=api_key, app_name=app_name, source_number=source_number)

    raise ValueError(
        f"Unknown MESSAGING_PROVIDER '{provider}' for PK. "
        "Expected: meta | twilio | 360dialog | gupshup"
    )


def _resolve_pk_compliance() -> ComplianceAdapter:
    enabled = os.environ.get("COMPLIANCE_PK_ENABLED", "false").lower() == "true"
    if enabled:
        from adapters.pakistan.compliance.pakistan_compliance_adapter import PakistanComplianceAdapter
        return PakistanComplianceAdapter()
    return NoopComplianceAdapter()
