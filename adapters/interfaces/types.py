"""Shared adapter types and error taxonomy for country-isolated integrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AdapterErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    CONFLICT_IDEMPOTENCY = "CONFLICT_IDEMPOTENCY"
    UNKNOWN_PROVIDER_ERROR = "UNKNOWN_PROVIDER_ERROR"
    TEMPLATE_REJECTED = "TEMPLATE_REJECTED"
    INVALID_RECIPIENT = "INVALID_RECIPIENT"


@dataclass(frozen=True)
class AdapterContext:
    tenant_id: str
    trace_id: str
    country_code: str
    channel: str = "whatsapp"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdapterError(Exception):
    code: AdapterErrorCode
    message: str
    retryable: bool
    provider: str
    provider_code: str | None = None
    correlation_id: str | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"



def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
