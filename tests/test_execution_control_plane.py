from __future__ import annotations

import pytest

from middleware.execution_control import ExecutionControlMiddleware
from services.core.execution import (
    ExecutionControlPlane,
    IdempotencyConflictError,
    IdempotencyInProgressError,
    IdempotencyScope,
    NonRetryableBusinessError,
    RetryPolicy,
    RetryableTransientError,
)


def test_idempotency_duplicate_returns_same_response() -> None:
    plane = ExecutionControlPlane()
    calls = {"count": 0}

    def op() -> dict[str, str]:
        calls["count"] += 1
        return {"result": "ok"}

    scope = IdempotencyScope("t1", "POST", "/v1/orders", "idem-1")
    first = plane.execute(scope=scope, payload={"quote_id": "q1"}, lock_domain="quote", lock_object_id="q1", operation=op)
    second = plane.execute(scope=scope, payload={"quote_id": "q1"}, lock_domain="quote", lock_object_id="q1", operation=op)

    assert first == second
    assert calls["count"] == 1


def test_payload_drift_is_rejected() -> None:
    plane = ExecutionControlPlane()
    scope = IdempotencyScope("t1", "POST", "/v1/subscriptions", "idem-2")

    plane.execute(
        scope=scope,
        payload={"sub_id": "s1", "plan": "pro"},
        lock_domain="subscription",
        lock_object_id="s1",
        operation=lambda: {"ok": True},
    )

    with pytest.raises(IdempotencyConflictError):
        plane.execute(
            scope=scope,
            payload={"sub_id": "s1", "plan": "enterprise"},
            lock_domain="subscription",
            lock_object_id="s1",
            operation=lambda: {"ok": True},
        )


def test_retry_with_exponential_backoff_recovers_transient_failures() -> None:
    plane = ExecutionControlPlane(retry_policy=RetryPolicy(max_attempts=3, base_backoff_seconds=0.001, max_backoff_seconds=0.01))
    attempts = {"n": 0}

    def flaky() -> dict[str, bool]:
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RetryableTransientError("dependency timeout")
        return {"recovered": True}

    out = plane.execute(
        scope=IdempotencyScope("t1", "POST", "/v1/payments/events", "idem-3"),
        payload={"event": "captured"},
        lock_domain="payment",
        lock_object_id="p1",
        operation=flaky,
    )

    assert out["recovered"] is True
    assert attempts["n"] == 3


def test_non_retryable_failure_marks_terminal_status() -> None:
    plane = ExecutionControlPlane()
    scope = IdempotencyScope("t2", "POST", "/v1/orders", "idem-4")

    with pytest.raises(NonRetryableBusinessError):
        plane.execute(
            scope=scope,
            payload={"quote_id": "q-no"},
            lock_domain="quote",
            lock_object_id="q-no",
            operation=lambda: (_ for _ in ()).throw(NonRetryableBusinessError("invalid quote state")),
        )

    record = plane.idempotency.get(scope)
    assert record is not None
    assert record.status == "failed_non_retryable"


def test_middleware_wraps_handler() -> None:
    middleware = ExecutionControlMiddleware()
    result = middleware.handle(
        tenant_id="t3",
        method="POST",
        route="/v1/workflows/transition",
        idempotency_key="idem-5",
        payload={"workflow_id": "wf1", "transition": "approve"},
        lock_domain="workflow",
        lock_object_id="wf1",
        handler=lambda: {"state": "approved"},
    )
    assert result["state"] == "approved"


def test_review_agent_reports_10_of_10_alignment() -> None:
    plane = ExecutionControlPlane()
    report = plane.review()
    assert report.race_conditions == []
    assert report.failure_gaps == []
    assert report.alignment_percent == 100


def test_inflight_duplicate_is_blocked() -> None:
    plane = ExecutionControlPlane()
    scope = IdempotencyScope("t4", "POST", "/v1/orders", "idem-6")
    plane.idempotency.reserve_or_get(scope=scope, payload={"quote_id": "q1"})

    with pytest.raises(IdempotencyInProgressError):
        plane.execute(
            scope=scope,
            payload={"quote_id": "q1"},
            lock_domain="quote",
            lock_object_id="q1",
            operation=lambda: {"ok": True},
        )


def test_retryable_failures_become_retryable_terminal_state() -> None:
    plane = ExecutionControlPlane(retry_policy=RetryPolicy(max_attempts=2, base_backoff_seconds=0.001, max_backoff_seconds=0.01))
    scope = IdempotencyScope("t5", "POST", "/v1/payments", "idem-7")

    with pytest.raises(RetryableTransientError):
        plane.execute(
            scope=scope,
            payload={"payment_id": "p1"},
            lock_domain="payment",
            lock_object_id="p1",
            operation=lambda: (_ for _ in ()).throw(RetryableTransientError("temporarily unavailable")),
        )

    record = plane.idempotency.get(scope)
    assert record is not None
    assert record.status == "failed_retryable"


def test_payload_hash_is_stable_for_nested_payload_key_order() -> None:
    plane = ExecutionControlPlane()
    scope = IdempotencyScope("t6", "POST", "/v1/workflows", "idem-8")
    payload_a = {"workflow_id": "wf-1", "metadata": {"priority": "high", "owner": "u1"}}
    payload_b = {"workflow_id": "wf-1", "metadata": {"owner": "u1", "priority": "high"}}

    first = plane.execute(
        scope=scope,
        payload=payload_a,
        lock_domain="workflow",
        lock_object_id="wf-1",
        operation=lambda: {"ok": True},
    )
    second = plane.execute(
        scope=scope,
        payload=payload_b,
        lock_domain="workflow",
        lock_object_id="wf-1",
        operation=lambda: {"ok": True},
    )

    assert first == second
