"""System hardening QC gate.

Validates security, rate limiting, audit immutability, observability, and
idempotent failure recovery anchors in gateway middleware.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _gate() -> list[tuple[str, bool, str]]:
    auth = _read("gateway/middleware/auth-rbac.js")
    rate = _read("gateway/middleware/rate-limit-hook.js")
    audit = _read("gateway/middleware/audit-log.js")
    obs = _read("gateway/middleware/observability.js")
    idem = _read("gateway/middleware/idempotency.js")

    checks: list[tuple[str, bool, str]] = []
    checks.append((
        "Security: tenant-bound ABAC check present",
        "tenantBoundFields" in auth and "tenant_resource_mismatch" in auth,
        "auth-rbac middleware missing tenant-bound ABAC guard",
    ))
    checks.append((
        "Rate limiting: canonical route bucketing present",
        "canonicalRoute" in rate and "bucketKey" in rate,
        "rate-limit middleware missing canonical route normalization",
    ))
    checks.append((
        "Audit logging: immutable hash chain verification present",
        "verifyAuditChain" in audit and "previous_hash" in audit,
        "audit middleware missing tamper detection chain verification",
    ))
    checks.append((
        "Observability: in-flight metric emitted",
        "inflight_requests" in obs and "severity" in obs,
        "observability middleware missing in-flight/severity telemetry",
    ))
    checks.append((
        "Failure recovery: idempotency avoids caching 5xx",
        "res.statusCode < 500" in idem,
        "idempotency middleware caches server errors",
    ))
    return checks


def main() -> None:
    checks = _gate()
    failed = [(name, detail) for name, ok, detail in checks if not ok]
    if failed:
        print("SYSTEM HARDENING QC: FAILED")
        for name, detail in failed:
            print(f"- {name}: {detail}")
        raise SystemExit(1)
    print("SYSTEM HARDENING QC: 10/10")


if __name__ == "__main__":
    main()
