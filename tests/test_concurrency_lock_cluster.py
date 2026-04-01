from __future__ import annotations

import threading
import time

import pytest

from src.execution_hardening import (
    DistributedLockCluster,
    FencingTokenError,
    InMemoryConcurrencyStore,
    LockAcquisitionTimeout,
    StaleVersionError,
)


def test_occ_rejects_stale_versions() -> None:
    store = InMemoryConcurrencyStore()
    store.create("quote:t1:q-1", {"status": "draft"})

    first = store.update(
        "quote:t1:q-1",
        expected_version_no=1,
        mutate=lambda row: {**row, "status": "accepted"},
        fencing_token=11,
    )
    assert first.version_no == 2

    with pytest.raises(StaleVersionError):
        store.update(
            "quote:t1:q-1",
            expected_version_no=1,
            mutate=lambda row: {**row, "status": "cancelled"},
            fencing_token=12,
        )


def test_fencing_rejects_stale_lock_owner_writes() -> None:
    store = InMemoryConcurrencyStore()
    store.create("sub:t1:s-1", {"phase": "active"})
    store.update(
        "sub:t1:s-1",
        expected_version_no=1,
        mutate=lambda row: row,
        fencing_token=100,
    )

    with pytest.raises(FencingTokenError):
        store.update(
            "sub:t1:s-1",
            expected_version_no=2,
            mutate=lambda row: row,
            fencing_token=99,
        )


def test_lock_cluster_serializes_critical_section_without_race() -> None:
    cluster = DistributedLockCluster()
    store = InMemoryConcurrencyStore()
    store.create("counter:t1", {"value": 0})

    def worker(owner: str) -> None:
        for _ in range(20):
            with cluster.critical_section("lock:t1:counter", owner_id=owner, wait_timeout_seconds=1.0) as lease:
                snap = store.read("counter:t1")
                store.update(
                    "counter:t1",
                    expected_version_no=snap.version_no,
                    fencing_token=lease.fencing_token,
                    mutate=lambda row: {"value": row["value"] + 1},
                )

    threads = [threading.Thread(target=worker, args=(f"w-{idx}",)) for idx in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    final = store.read("counter:t1")
    assert final.value["value"] == 100
    assert final.version_no == 101


def test_acquire_many_canonical_order_avoids_deadlock() -> None:
    cluster = DistributedLockCluster()
    completed: list[str] = []

    def lock_in_reverse(owner: str, keys: list[str]) -> None:
        with cluster.acquire_many(keys, owner_id=owner, wait_timeout_seconds=1.0):
            time.sleep(0.01)
            completed.append(owner)

    t1 = threading.Thread(target=lock_in_reverse, args=("a", ["k2", "k1"]))
    t2 = threading.Thread(target=lock_in_reverse, args=("b", ["k1", "k2"]))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert sorted(completed) == ["a", "b"]


def test_lock_timeout_when_contention_exceeds_wait() -> None:
    cluster = DistributedLockCluster()
    lease = cluster.acquire("lock:t1:quote:q-1", owner_id="owner-a", lease_seconds=0.5)

    try:
        with pytest.raises(LockAcquisitionTimeout):
            cluster.acquire(
                "lock:t1:quote:q-1",
                owner_id="owner-b",
                wait_timeout_seconds=0.02,
                retry_interval_seconds=0.01,
            )
    finally:
        cluster.release("lock:t1:quote:q-1", owner_id=lease.owner_id, fencing_token=lease.fencing_token)
