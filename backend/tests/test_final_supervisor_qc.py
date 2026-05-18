from scripts.self_qc_final_supervisor import _discover_qc_scripts, _gate


def test_final_supervisor_gate_all_green() -> None:
    checks = _gate()
    failed = [name for name, ok, _ in checks if not ok]
    assert failed == []


def test_qc_discovery_includes_system_hardening_and_excludes_self() -> None:
    scripts = _discover_qc_scripts()
    assert "scripts/self_qc_system_hardening.py" in scripts
    assert "scripts/self_qc_final_supervisor.py" not in scripts
