from __future__ import annotations

from typing import Any, Callable

from services.core.execution import ExecutionControlPlane, IdempotencyScope


class ExecutionControlMiddleware:
    """Transport-agnostic middleware that wraps handlers with control-plane guarantees."""

    def __init__(self, control_plane: ExecutionControlPlane | None = None) -> None:
        self.control_plane = control_plane or ExecutionControlPlane()

    def handle(
        self,
        *,
        tenant_id: str,
        method: str,
        route: str,
        idempotency_key: str,
        payload: dict[str, Any],
        lock_domain: str,
        lock_object_id: str,
        handler: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        scope = IdempotencyScope(
            tenant_id=tenant_id,
            http_method=method,
            canonical_route=route,
            idempotency_key=idempotency_key,
        )
        return self.control_plane.execute(
            scope=scope,
            payload=payload,
            lock_domain=lock_domain,
            lock_object_id=lock_object_id,
            operation=handler,
        )
