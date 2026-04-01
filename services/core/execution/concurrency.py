from __future__ import annotations

from src.execution_hardening.concurrency import DistributedLockCluster, InMemoryConcurrencyStore


class ConcurrencyController:
    """Execution control wrapper over lock cluster + OCC store."""

    def __init__(self) -> None:
        self.locks = DistributedLockCluster()
        self.store = InMemoryConcurrencyStore()

    @staticmethod
    def lock_key(*, tenant_id: str, domain: str, object_id: str) -> str:
        return f"lock:{tenant_id}:{domain}:{object_id}"
