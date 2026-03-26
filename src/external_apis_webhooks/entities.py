"""Integration entities and contract constants for external APIs and webhooks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

ProviderName = Literal["stripe", "sendgrid", "twilio"]

ALLOWED_PROVIDERS: tuple[ProviderName, ...] = ("stripe", "sendgrid", "twilio")

OUTBOUND_API_CONTRACTS: dict[ProviderName, dict[str, Any]] = {
    "stripe": {
        "base_url": "https://api.stripe.com",
        "endpoints": {
            "payment_intents": {"method": "POST", "path": "/v1/payment_intents"},
            "customers": {"method": "GET", "path": "/v1/customers"},
            "subscriptions": {"method": "GET", "path": "/v1/subscriptions"},
        },
        "auth": "bearer",
        "timeout_seconds": 10,
        "max_retries": 3,
    },
    "sendgrid": {
        "base_url": "https://api.sendgrid.com",
        "endpoints": {
            "mail_send": {"method": "POST", "path": "/v3/mail/send"},
        },
        "auth": "bearer",
        "timeout_seconds": 8,
        "max_retries": 3,
    },
    "twilio": {
        "base_url": "https://api.twilio.com",
        "endpoints": {
            "messages": {"method": "POST", "path_template": "/2010-04-01/Accounts/{account_sid}/Messages.json"},
        },
        "auth": "basic",
        "timeout_seconds": 8,
        "max_retries": 2,
    },
}

INBOUND_WEBHOOK_ENDPOINTS: dict[ProviderName, dict[str, str]] = {
    "stripe": {"method": "POST", "path": "/webhooks/stripe"},
    "sendgrid": {"method": "POST", "path": "/webhooks/sendgrid/events"},
    "twilio": {"method": "POST", "path": "/webhooks/twilio/status"},
}


@dataclass(frozen=True)
class OutboundRequest:
    provider: ProviderName
    endpoint_key: str
    payload: dict[str, Any]
    account_sid: str | None = None


@dataclass(frozen=True)
class OutboundResponse:
    provider: ProviderName
    status_code: int
    body: dict[str, Any]


@dataclass(frozen=True)
class InboundWebhook:
    provider: ProviderName
    headers: dict[str, str]
    payload: dict[str, Any] | list[dict[str, Any]]


DeliveryStatus = Literal["pending", "failed", "delivered", "dead_lettered"]


@dataclass(frozen=True)
class WebhookSubscription:
    subscription_id: str
    target_url: str
    event_names: tuple[str, ...]
    is_active: bool = True
    max_attempts: int = 10


@dataclass(frozen=True)
class WebhookDelivery:
    delivery_id: str
    subscription_id: str
    event_name: str
    target_url: str
    payload: dict[str, Any]
    max_attempts: int
    attempt_count: int = 0
    status: DeliveryStatus = "pending"
    last_error: str | None = None
