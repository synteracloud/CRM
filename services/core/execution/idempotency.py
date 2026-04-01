from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from threading import RLock
from time import time
from typing import Any


class IdempotencyConflictError(ValueError):
    """Raised when an idempotency key is reused with payload drift."""


class IdempotencyInProgressError(RuntimeError):
    """Raised when an equivalent idempotent request is still in-flight."""


@dataclass(frozen=True)
class IdempotencyScope:
    tenant_id: str
    http_method: str
    canonical_route: str
    idempotency_key: str


@dataclass
class IdempotencyRecord:
    scope: IdempotencyScope
    payload_hash: str
    status: str
    response: dict[str, Any] | None
    first_seen_at: float
    last_seen_at: float


class GlobalIdempotencyLedger:
    """Thread-safe in-memory global idempotency ledger.

    Scope key: (tenant_id, http_method, canonical_route, idempotency_key)
    """

    TERMINAL_STATUSES = {"succeeded", "failed_non_retryable", "failed_retryable"}

    def __init__(self) -> None:
        self._lock = RLock()
        self._records: dict[tuple[str, str, str, str], IdempotencyRecord] = {}

    @staticmethod
    def hash_payload(payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _key(scope: IdempotencyScope) -> tuple[str, str, str, str]:
        return (scope.tenant_id, scope.http_method.upper(), scope.canonical_route, scope.idempotency_key)

    def reserve_or_get(
        self,
        *,
        scope: IdempotencyScope,
        payload: dict[str, Any],
    ) -> tuple[IdempotencyRecord, bool]:
        now = time()
        payload_hash = self.hash_payload(payload)
        key = self._key(scope)

        with self._lock:
            existing = self._records.get(key)
            if existing is None:
                record = IdempotencyRecord(
                    scope=scope,
                    payload_hash=payload_hash,
                    status="in_progress",
                    response=None,
                    first_seen_at=now,
                    last_seen_at=now,
                )
                self._records[key] = record
                return record, True

            if existing.payload_hash != payload_hash:
                raise IdempotencyConflictError("idempotency_key_reused_with_different_payload")

            existing.last_seen_at = now
            return existing, False

    def finalize(self, *, scope: IdempotencyScope, status: str, response: dict[str, Any] | None) -> IdempotencyRecord:
        if status not in self.TERMINAL_STATUSES:
            raise ValueError(f"invalid terminal status: {status}")

        with self._lock:
            key = self._key(scope)
            record = self._records[key]
            record.status = status
            record.response = response
            record.last_seen_at = time()
            return record

    def get(self, scope: IdempotencyScope) -> IdempotencyRecord | None:
        with self._lock:
            return self._records.get(self._key(scope))
