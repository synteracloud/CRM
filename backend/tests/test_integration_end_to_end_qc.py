from scripts.self_qc_integration_end_to_end import run_self_qc


def test_end_to_end_integration_qc_green() -> None:
    score, failed = run_self_qc()
    assert score == 10
    assert failed == []
