"""Auth helpers for outbound integrations and inbound webhook verification."""

from __future__ import annotations

from dataclasses import dataclass

from .entities import ProviderName


class IntegrationAuthError(ValueError):
    """Raised when integration authentication fails validation."""


@dataclass(frozen=True)
class SecretStore:
    secrets: dict[str, str]

    def get(self, key: str) -> str:
        value = self.secrets.get(key)
        if not value:
            raise IntegrationAuthError(f"Missing required secret: {key}")
        return value


class IntegrationAuth:
    def __init__(self, secrets: SecretStore) -> None:
        self._secrets = secrets

    def outbound_headers(self, provider: ProviderName, account_sid: str | None = None) -> dict[str, str]:
        if provider == "stripe":
            return {"Authorization": f"Bearer {self._secrets.get('STRIPE_SECRET_KEY')}"}
        if provider == "sendgrid":
            return {"Authorization": f"Bearer {self._secrets.get('SENDGRID_API_KEY')}"}
        if provider == "twilio":
            sid = account_sid or self._secrets.get("TWILIO_ACCOUNT_SID")
            token = self._secrets.get("TWILIO_AUTH_TOKEN")
            return {"Authorization": f"Basic {sid}:{token}"}
        raise IntegrationAuthError(f"Unknown provider: {provider}")

    def verify_webhook_signature(self, provider: ProviderName, headers: dict[str, str]) -> bool:
        normalized = {k.lower(): v for k, v in headers.items()}

        if provider == "stripe":
            return bool(normalized.get("stripe-signature"))
        if provider == "sendgrid":
            return bool(normalized.get("x-twilio-email-event-webhook-signature")) and bool(
                normalized.get("x-twilio-email-event-webhook-timestamp")
            )
        if provider == "twilio":
            return bool(normalized.get("x-twilio-signature"))
        return False
