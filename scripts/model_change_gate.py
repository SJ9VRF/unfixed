from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_json(path: str):
    return json.loads(Path(path).read_text())


def evaluate(response_path: str, mass_path: str, frontier_path: str) -> dict:
    response = _load_json(response_path)
    mass = _load_json(mass_path)
    frontier = _load_json(frontier_path)

    by_method = {row["method"]: row for row in response["summary"]}
    mass_by = {row["method"]: row for row in mass["summary"]}

    checks = [
        {
            "name": "bayesian_response_accuracy_floor",
            "observed": by_method["bayesian_state"]["overall_accuracy_mean"],
            "threshold": 0.66,
            "op": ">=",
        },
        {
            "name": "bayesian_overpersonalization_ceiling",
            "observed": by_method["bayesian_state"]["overpersonalization_rate_mean"],
            "threshold": 0.02,
            "op": "<=",
        },
        {
            "name": "mass_capped_synthetic_regression_ceiling",
            "observed": abs(mass_by["mass_capped_uces"]["delta_vs_real"]),
            "threshold": 0.01,
            "op": "<=",
        },
        {
            "name": "frontier_eval_smoke_pass_rate",
            "observed": frontier["summary"]["pass_rate"],
            "threshold": 1.0,
            "op": ">=",
        },
    ]
    for c in checks:
        c["passed"] = c["observed"] >= c["threshold"] if c["op"] == ">=" else c["observed"] <= c["threshold"]
    return {"passed": all(c["passed"] for c in checks), "checks": checks}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail a candidate model/system change if frozen behavior thresholds regress.")
    parser.add_argument("--response", default="results/paper_response_level_repeated.json")
    parser.add_argument("--mass", default="results/paper_mass_control.json")
    parser.add_argument("--frontier", default="results/frontier_eval_report.json")
    parser.add_argument("--out", default="results/model_change_gate.json")
    args = parser.parse_args()
    report = evaluate(args.response, args.mass, args.frontier)
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    for check in report["checks"]:
        print(f"{'PASS' if check['passed'] else 'FAIL'} {check['name']}: {check['observed']:.6f} {check['op']} {check['threshold']:.6f}")
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
