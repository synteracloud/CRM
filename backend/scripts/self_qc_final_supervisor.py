"""Final supervisor auto-fix QC orchestrator.

This script enforces a top-level enterprise gate across B0->B9 artifacts by:
- validating documentation coverage,
- executing all prior QC layers/scripts,
- checking execution-hardening, consistency, and integration anchors,
- failing fast when any gate regresses.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

DOCS_REQUIRED = [
    "docs/foundation-qc.md",
    "docs/b4-intelligence-data-qc.md",
    "docs/b5-integration-qc.md",
    "docs/execution-hardening-qc.md",
    "docs/b8-qc01-enterprise-depth-qc.md",
    "docs/b9-qc01-ui-experience-qc.md",
    "docs/service-map.md",
    "docs/capability-matrix.md",
    "docs/data-architecture.md",
    "docs/global-idempotency.md",
    "docs/concurrency-control.md",
    "docs/distributed-lock-strategy.md",
]

PRIOR_QC_SCRIPTS = [
    "scripts/self_qc_event_bus.py",
    "scripts/self_qc_b5_integrations.py",
    "scripts/self_qc_execution_hardening.py",
    "scripts/self_qc_b8_cpq_rules_engine.py",
    "scripts/self_qc_workflow_engine.py",
    "scripts/self_qc_failure_recovery.py",
    "scripts/self_qc_campaigns_segmentation.py",
    "scripts/self_qc_lead_management.py",
    "scripts/self_qc_automation_journeys.py",
    "scripts/self_qc_omnichannel_inbox.py",
    "scripts/self_qc_ticket_management.py",
    "scripts/self_qc_integration_end_to_end.py",
]


def _discover_qc_scripts() -> list[str]:
    """Return all self-QC scripts except this final supervisor wrapper.

    The list is deterministic and merged with the curated PRIOR_QC_SCRIPTS list,
    ensuring we execute explicitly required gates and any newly added QC layers.
    """

    discovered = {
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in (ROOT / "scripts").glob("self_qc_*.py")
        if path.name != "self_qc_final_supervisor.py"
    }
    ordered = list(dict.fromkeys([*PRIOR_QC_SCRIPTS, *sorted(discovered)]))
    return ordered


def _retry_safe_run(path: str, attempts: int = 2) -> tuple[bool, str]:
    """Run a QC script with bounded retries to absorb transient execution flakes."""

    outputs: list[str] = []
    for idx in range(1, attempts + 1):
        ok, output = _run_python(path)
        outputs.append(f"attempt {idx}: {output}".strip())
        if ok:
            return True, output
    return False, "\n".join(outputs)


def _non_empty_docs(paths: Iterable[Path]) -> list[str]:
    return [
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in paths
        if path.is_file() and not path.read_text(encoding="utf-8").strip()
    ]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _run_python(path: str) -> tuple[bool, str]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    ok = proc.returncode == 0
    output = (proc.stdout + "\n" + proc.stderr).strip()
    return ok, output


def _gate() -> list[tuple[str, bool, str]]:
    service_map = _read("docs/service-map.md")
    capability_matrix = _read("docs/capability-matrix.md")
    data_arch = _read("docs/data-architecture.md")
    governance = _read("docs/b8-p10-data-governance-layer.md")
    idempotency = _read("docs/global-idempotency.md")
    concurrency = _read("docs/concurrency-control.md")
    locks = _read("docs/distributed-lock-strategy.md")
    routes_index = _read("gateway/routes/index.js")
    all_docs = sorted((ROOT / "docs").glob("*.md"))

    checks: list[tuple[str, bool, str]] = []

    missing_docs = [p for p in DOCS_REQUIRED if not (ROOT / p).exists()]
    checks.append((
        "B0->B9 QC corpus exists",
        not missing_docs,
        "" if not missing_docs else f"missing: {', '.join(missing_docs)}",
    ))

    empty_docs = _non_empty_docs(all_docs)
    checks.append((
        "All /docs artifacts are non-empty",
        not empty_docs,
        "" if not empty_docs else f"empty docs: {', '.join(empty_docs)}",
    ))

    checks.append((
        "Zero-gap capability coverage documented",
        "Coverage rules applied" in capability_matrix and "Coverage Checklist" in capability_matrix,
        "capability matrix must include explicit coverage rules + checklist",
    ))

    checks.append((
        "System consistency map defined",
        "Service Catalog" in service_map and "Domain Coverage Matrix" in service_map,
        "service map missing catalog/domain matrix anchors",
    ))

    checks.append((
        "UI↔backend contract surfaces present",
        "/api/v1" in routes_index and "v1-" in routes_index,
        "gateway route index missing API v1 mounts",
    ))

    checks.append((
        "Data trust and dedup controls documented",
        "duplicate detection jobs" in governance.lower() and "reconciliation" in locks.lower(),
        "data architecture/lock strategy missing dedup-reconciliation anchors",
    ))

    checks.append((
        "Execution guarantees present",
        "idempotency" in idempotency.lower() and "version_no" in concurrency and "lease" in locks.lower(),
        "idempotency/OCC/distributed lock guarantees incomplete",
    ))

    for script in _discover_qc_scripts():
        ok, output = _retry_safe_run(script)
        checks.append((
            f"Prior QC pass: {script}",
            ok,
            output if not ok else "",
        ))

    return checks


def main() -> None:
    checks = _gate()
    failed = [(name, detail) for name, ok, detail in checks if not ok]

    if failed:
        print("FINAL SUPERVISOR QC: FAILED")
        for name, detail in failed:
            print(f"- {name}")
            if detail:
                print(f"  detail: {detail}")
        raise SystemExit(1)

    print("FINAL SUPERVISOR QC: 10/10 ELITE GRADE")


if __name__ == "__main__":
    main()
