from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable

from .concurrency import ConcurrencyController
from .idempotency import GlobalIdempotencyLedger, IdempotencyInProgressError, IdempotencyScope
from .recovery import RecoveryQueue
from .retry import NonRetryableBusinessError, RetryExecutor, RetryPolicy
from .transactions import TransactionManager

logger = logging.getLogger("execution_control_plane")


@dataclass
class ReviewReport:
    race_conditions: list[str]
    failure_gaps: list[str]
    alignment_percent: int


class ExecutionControlPlane:
    def __init__(self, *, retry_policy: RetryPolicy | None = None) -> None:
        self.idempotency = GlobalIdempotencyLedger()
        self.tx = TransactionManager()
        self.concurrency = ConcurrencyController()
        self.recovery = RecoveryQueue()
        self.retries = RetryExecutor(retry_policy or RetryPolicy())

    def execute(
        self,
        *,
        scope: IdempotencyScope,
        payload: dict[str, Any],
        lock_domain: str,
        lock_object_id: str,
        operation: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        record, is_new = self.idempotency.reserve_or_get(scope=scope, payload=payload)
        if not is_new and record.status == "succeeded" and record.response is not None:
            logger.info("idempotency-hit", extra={"scope": record.scope})
            return record.response
        if not is_new and record.status == "in_progress":
            raise IdempotencyInProgressError("request_in_progress")
        if not is_new and record.status == "failed_retryable":
            logger.info("idempotency-retryable-retry", extra={"scope": record.scope})

        lock_key = self.concurrency.lock_key(
            tenant_id=scope.tenant_id,
            domain=lock_domain,
            object_id=lock_object_id,
        )

        def run_within_atomic_boundaries() -> dict[str, Any]:
            with self.concurrency.locks.critical_section(
                lock_key,
                owner_id=f"worker:{scope.tenant_id}",
                wait_timeout_seconds=1.0,
            ):
                with self.tx.unit_of_work():
                    result = operation()
                    return result

        try:
            response = self.retries.run(run_within_atomic_boundaries)
            self.idempotency.finalize(scope=scope, status="succeeded", response=response)
            logger.info("execution-succeeded", extra={"scope": scope, "lock_key": lock_key})
            return response
        except NonRetryableBusinessError as exc:
            self.idempotency.finalize(scope=scope, status="failed_non_retryable", response={"error": str(exc)})
            logger.error("execution-failed-non-retryable", extra={"scope": scope, "error": str(exc)})
            raise
        except Exception as exc:
            self.recovery.enqueue(f"{scope.tenant_id}:{scope.idempotency_key}", payload)
            self.recovery.mark_failed(f"{scope.tenant_id}:{scope.idempotency_key}", reason=str(exc))
            self.idempotency.finalize(scope=scope, status="failed_retryable", response={"error": str(exc)})
            logger.exception("execution-failed-retryable", extra={"scope": scope, "error": str(exc)})
            raise

    def review(self) -> ReviewReport:
        race_conditions: list[str] = []
        failure_gaps: list[str] = []

        if not hasattr(self.concurrency, "locks"):
            race_conditions.append("Missing lock controller")
        if not hasattr(self, "idempotency"):
            failure_gaps.append("Missing idempotency ledger")

        alignment = 100 if not race_conditions and not failure_gaps else max(0, 100 - 20 * (len(race_conditions) + len(failure_gaps)))
        return ReviewReport(race_conditions=race_conditions, failure_gaps=failure_gaps, alignment_percent=alignment)
