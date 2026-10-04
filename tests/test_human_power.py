from human_eval.power import proportion_power_n

def test_power_requires_fewer_judgments_for_larger_effect():
    assert proportion_power_n(.5,.65) < proportion_power_n(.5,.60) < proportion_power_n(.5,.56)
