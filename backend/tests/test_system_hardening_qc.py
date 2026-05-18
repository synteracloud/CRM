from scripts.self_qc_system_hardening import _gate


def test_system_hardening_gate_all_green() -> None:
    checks = _gate()
    failed = [name for name, ok, _ in checks if not ok]
    assert failed == []
