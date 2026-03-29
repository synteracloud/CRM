from scripts.self_qc_final_supervisor import _gate


def test_final_supervisor_gate_all_green() -> None:
    checks = _gate()
    failed = [name for name, ok, _ in checks if not ok]
    assert failed == []
