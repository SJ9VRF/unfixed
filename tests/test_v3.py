from evals.suite.statistics import bootstrap_ci, paired_bootstrap_delta
from evals.suite.v3_runner import change_detection_eval


def test_bootstrap_ci_contains_mean():
    x=[.1,.2,.3,.4,.5]; lo,hi=bootstrap_ci(x,n_boot=300,seed=1)
    assert lo <= sum(x)/len(x) <= hi


def test_paired_bootstrap_direction():
    r=paired_bootstrap_delta([.8,.9,.7,.85],[.6,.7,.65,.7],n_boot=300,seed=2)
    assert r['mean_delta']>0 and r['ci95'][0]>0


def test_change_detection_auc(tmp_path):
    r=change_detection_eval(tmp_path,seed=5)
    assert r['roc_auc']>=.9
