from grader_calibration.calibrate import calibrate

def test_calibration_math():
    r=calibrate([1,1,0,0],[1,0,1,0])
    assert r.agreement==.5 and r.false_positive_rate==.5 and r.false_negative_rate==.5
