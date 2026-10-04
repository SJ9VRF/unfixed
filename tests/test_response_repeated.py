from evals.response_level.repeated import FIELDS, DEFAULT_SEEDS


def test_repeated_response_contract():
    assert len(DEFAULT_SEEDS) == 5
    assert len(set(DEFAULT_SEEDS)) == 5
    assert "overall_accuracy" in FIELDS
    assert "overpersonalization_rate" in FIELDS
