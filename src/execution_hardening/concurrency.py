"""Concurrency-control and distributed-lock primitives.

The module provides:
- optimistic concurrency control via ``version_no`` checks,
- finite-lease distributed locks with heartbeat renewal,
- fencing-token enforcement to reject stale lock owners,
- canonical lock ordering for multi-lock acquisition.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from threading import Condition, RLock
import time
from typing import Any, Callable, Iterator


class StaleVersionError(RuntimeError):
    """Raised when OCC detects a stale ``expected_version_no``."""


class LockAcquisitionTimeout(TimeoutError):
    """Raised when a lock cannot be acquired within bounded wait time."""


class LockOwnershipError(RuntimeError):
    """Raised when renew/release is attempted by a non-owner."""


class FencingTokenError(RuntimeError):
    """Raised when a stale fencing token attempts to write."""


@dataclass(frozen=True)
class VersionedRecord:
    key: str
    value: dict[str, Any]
    version_no: int = 1
    last_fencing_token: int = 0


@dataclass(frozen=True)
class LockLease:
    key: str
    owner_id: str
    fencing_token: int
    expires_at_monotonic: float


class InMemoryConcurrencyStore:
    """Thread-safe in-memory store implementing OCC + fencing checks."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._rows: dict[str, VersionedRecord] = {}

    def create(self, key: str, value: dict[str, Any]) -> VersionedRecord:
        with self._lock:
            if key in self._rows:
                raise ValueError(f"record already exists: {key}")
            row = VersionedRecord(key=key, value=dict(value), version_no=1, last_fencing_token=0)
            self._rows[key] = row
            return row

    def read(self, key: str) -> VersionedRecord:
        with self._lock:
            row = self._rows[key]
            return VersionedRecord(
                key=row.key,
                value=dict(row.value),
                version_no=row.version_no,
                last_fencing_token=row.last_fencing_token,
            )

    def update(
        self,
        key: str,
        *,
        expected_version_no: int,
        mutate: Callable[[dict[str, Any]], dict[str, Any]],
        fencing_token: int | None = None,
    ) -> VersionedRecord:
        """Apply a mutation if version and fencing checks pass."""

        with self._lock:
            row = self._rows[key]
            if row.version_no != expected_version_no:
                raise StaleVersionError(f"STALE_VERSION expected={expected_version_no} actual={row.version_no}")

            next_fencing = row.last_fencing_token
            if fencing_token is not None:
                if fencing_token < row.last_fencing_token:
                    raise FencingTokenError(
                        f"stale fencing token={fencing_token} latest={row.last_fencing_token}"
                    )
                next_fencing = fencing_token

            new_value = mutate(dict(row.value))
            next_row = VersionedRecord(
                key=key,
                value=dict(new_value),
                version_no=row.version_no + 1,
                last_fencing_token=next_fencing,
            )
            self._rows[key] = next_row
            return next_row


class DistributedLockCluster:
    """In-memory lock cluster with finite leases and fencing tokens."""

    def __init__(self) -> None:
        self._mutex = RLock()
        self._cv = Condition(self._mutex)
        self._locks: dict[str, LockLease] = {}
        self._fence_counter = 0

    def _next_fencing_token(self) -> int:
        self._fence_counter += 1
        return self._fence_counter

    def _is_expired(self, lease: LockLease, now: float) -> bool:
        return lease.expires_at_monotonic <= now

    def acquire(
        self,
        key: str,
        *,
        owner_id: str,
        lease_seconds: float = 30.0,
        wait_timeout_seconds: float = 0.0,
        retry_interval_seconds: float = 0.01,
    ) -> LockLease:
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be > 0")
        if wait_timeout_seconds < 0:
            raise ValueError("wait_timeout_seconds must be >= 0")

        deadline = time.monotonic() + wait_timeout_seconds
        with self._cv:
            while True:
                now = time.monotonic()
                current = self._locks.get(key)
                if current is None or self._is_expired(current, now):
                    lease = LockLease(
                        key=key,
                        owner_id=owner_id,
                        fencing_token=self._next_fencing_token(),
                        expires_at_monotonic=now + lease_seconds,
                    )
                    self._locks[key] = lease
                    return lease

                if now >= deadline:
                    raise LockAcquisitionTimeout(f"timeout acquiring lock key={key}")

                self._cv.wait(timeout=min(retry_interval_seconds, max(0.0, deadline - now)))

    def renew(self, key: str, *, owner_id: str, fencing_token: int, lease_seconds: float = 30.0) -> LockLease:
        with self._cv:
            now = time.monotonic()
            current = self._locks.get(key)
            if current is None or self._is_expired(current, now):
                raise LockOwnershipError(f"cannot renew missing/expired lock key={key}")
            if current.owner_id != owner_id or current.fencing_token != fencing_token:
                raise LockOwnershipError(f"cannot renew lock key={key}: owner/fencing mismatch")
            renewed = LockLease(
                key=key,
                owner_id=owner_id,
                fencing_token=fencing_token,
                expires_at_monotonic=now + lease_seconds,
            )
            self._locks[key] = renewed
            self._cv.notify_all()
            return renewed

    def release(self, key: str, *, owner_id: str, fencing_token: int) -> bool:
        with self._cv:
            now = time.monotonic()
            current = self._locks.get(key)
            if current is None or self._is_expired(current, now):
                self._locks.pop(key, None)
                self._cv.notify_all()
                return False
            if current.owner_id != owner_id or current.fencing_token != fencing_token:
                raise LockOwnershipError(f"cannot release lock key={key}: owner/fencing mismatch")
            self._locks.pop(key, None)
            self._cv.notify_all()
            return True

    @contextmanager
    def critical_section(
        self,
        key: str,
        *,
        owner_id: str,
        lease_seconds: float = 30.0,
        wait_timeout_seconds: float = 0.0,
    ) -> Iterator[LockLease]:
        lease = self.acquire(
            key,
            owner_id=owner_id,
            lease_seconds=lease_seconds,
            wait_timeout_seconds=wait_timeout_seconds,
        )
        try:
            yield lease
        finally:
            self.release(key, owner_id=lease.owner_id, fencing_token=lease.fencing_token)

    @contextmanager
    def acquire_many(
        self,
        keys: list[str] | tuple[str, ...],
        *,
        owner_id: str,
        lease_seconds: float = 30.0,
        wait_timeout_seconds: float = 0.0,
    ) -> Iterator[list[LockLease]]:
        leases: list[LockLease] = []
        ordered_keys = sorted(dict.fromkeys(keys))
        try:
            for key in ordered_keys:
                leases.append(
                    self.acquire(
                        key,
                        owner_id=owner_id,
                        lease_seconds=lease_seconds,
                        wait_timeout_seconds=wait_timeout_seconds,
                    )
                )
            yield leases
        finally:
            for lease in reversed(leases):
                self.release(lease.key, owner_id=lease.owner_id, fencing_token=lease.fencing_token)
