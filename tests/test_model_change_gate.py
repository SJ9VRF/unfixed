import json
from pathlib import Path
from scripts.model_change_gate import evaluate


def test_model_change_gate_passes_current_release(tmp_path: Path):
    response = {
        "summary": [
            {"method": "bayesian_state", "overall_accuracy_mean": 0.68, "overpersonalization_rate_mean": 0.0}
        ]
    }
    mass = {"summary": [{"method": "mass_capped_uces", "delta_vs_real": -0.002}]}
    frontier = {"summary": {"pass_rate": 1.0}}
    paths = []
    for name, data in [("r.json", response), ("m.json", mass), ("f.json", frontier)]:
        p = tmp_path / name
        p.write_text(json.dumps(data))
        paths.append(str(p))
    out = evaluate(*paths)
    assert out["passed"]


def test_model_change_gate_catches_behavior_regression(tmp_path: Path):
    response = {"summary": [{"method": "bayesian_state", "overall_accuracy_mean": 0.60, "overpersonalization_rate_mean": 0.20}]}
    mass = {"summary": [{"method": "mass_capped_uces", "delta_vs_real": -0.05}]}
    frontier = {"summary": {"pass_rate": 0.9}}
    paths=[]
    for name,data in [("r.json",response),("m.json",mass),("f.json",frontier)]:
        p=tmp_path/name; p.write_text(json.dumps(data)); paths.append(str(p))
    assert not evaluate(*paths)["passed"]
