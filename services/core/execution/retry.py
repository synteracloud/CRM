from __future__ import annotations

from dataclasses import dataclass
from random import Random
import time
from typing import Callable, TypeVar

T = TypeVar("T")


class RetryableTransientError(RuntimeError):
    pass


class RetryableContentionError(RuntimeError):
    pass


class NonRetryableBusinessError(RuntimeError):
    pass


class NonRetryableSystemError(RuntimeError):
    pass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 5
    base_backoff_seconds: float = 0.05
    max_backoff_seconds: float = 1.5
    jitter_ratio: float = 0.2


class RetryExecutor:
    def __init__(self, policy: RetryPolicy, *, seed: int = 7) -> None:
        self._policy = policy
        self._random = Random(seed)

    def _is_retryable(self, exc: Exception) -> bool:
        return isinstance(exc, (RetryableTransientError, RetryableContentionError))

    def _sleep_seconds(self, attempt: int) -> float:
        backoff = min(
            self._policy.max_backoff_seconds,
            self._policy.base_backoff_seconds * (2 ** (attempt - 1)),
        )
        jitter = backoff * self._policy.jitter_ratio * self._random.random()
        return min(self._policy.max_backoff_seconds, backoff + jitter)

    def run(self, operation: Callable[[], T]) -> T:
        last_exc: Exception | None = None
        for attempt in range(1, self._policy.max_attempts + 1):
            try:
                return operation()
            except Exception as exc:  # taxonomy resolution remains deterministic
                last_exc = exc
                if not self._is_retryable(exc) or attempt >= self._policy.max_attempts:
                    raise
                time.sleep(self._sleep_seconds(attempt))

        assert last_exc is not None
        raise last_exc
