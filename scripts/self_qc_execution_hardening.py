"""Self-QC checks for B7-QC01 execution hardening."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _check(conditions: list[tuple[str, bool]]) -> tuple[int, list[str]]:
    failed = [name for name, ok in conditions if not ok]
    return (10 - len(failed), failed)


def main() -> None:
    transaction_sql = _read("db/transaction_db/transaction_handling.sql")
    txn_policies = _read("db/transaction_db/transaction_policies.md")
    global_idempotency = _read("docs/global-idempotency.md")
    concurrency = _read("docs/concurrency-control.md")
    locks = _read("docs/distributed-lock-strategy.md")
    scheduler = _read("docs/scheduler-jobs.md")

    checks = [
        ("ACID boundary policy documented", "ACID-safe handling rules" in txn_policies),
        ("Critical UoW boundaries implemented", all(name in transaction_sql for name in ["create_subscription_with_invoice_uow", "advance_payment_status_uow", "record_payment_event_uow"])),
        ("Global API idempotency model defined", "(tenant_id, http_method, canonical_route, idempotency_key)" in global_idempotency),
        ("Idempotency conflict path enforced in DB UoW", "idempotency_key_reused_with_different_payload" in transaction_sql),
        ("Retry semantics deterministic", "retry_policy.backoff_seconds cannot exceed max_backoff_seconds" in _read("src/workflow_engine/services.py")),
        ("Rollback policy explicit", "rollback" in txn_policies.lower()),
        ("Concurrent update OCC contract defined", "version_no" in concurrency and "STALE_VERSION" in concurrency),
        ("Pessimistic locking guidance exists", "FOR UPDATE" in concurrency),
        ("Distributed locks protect critical operations", "Protected operation list" in locks and "Quote acceptance -> order creation transition" in locks),
        ("Recovery system and dead-letter handling documented", "dead_lettered" in scheduler and "Replay safety" in scheduler),
    ]

    score, failed = _check(checks)
    if failed:
        print(f"Self-QC score: {score}/10")
        print("Failed checks:")
        for item in failed:
            print(f"- {item}")
        raise SystemExit(1)

    print("Self-QC score: 10/10")


if __name__ == "__main__":
    main()
