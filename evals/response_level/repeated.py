from __future__ import annotations

import csv
import json
import shutil
import statistics
import tempfile
from pathlib import Path

from evals.response_level.benchmark import run_response_level_benchmark

DEFAULT_SEEDS = [401, 433, 461, 497, 523]
FIELDS = [
    "overall_accuracy",
    "personalized_choice_accuracy",
    "no_personalize_accuracy",
    "overpersonalization_rate",
    "response_regret",
]


def run_repeated_response_level(
    out_dir: str | Path = "results",
    seeds: list[int] | None = None,
    n_train: int = 70,
    n_test: int = 35,
    n_history: int = 8,
) -> dict:
    """Run the natural-language response benchmark across independent seeds.

    Each seed trains a fresh structured learner, relevance gate, and scratch
    PyTorch response ranker. Temporary per-seed artifacts are discarded after
    their scalar summaries are aggregated; the release keeps the complete
    per-seed table and the aggregate table.
    """
    seeds = list(DEFAULT_SEEDS if seeds is None else seeds)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict] = []

    for seed in seeds:
        tmp = Path(tempfile.mkdtemp(prefix=f"tuu-response-{seed}-"))
        try:
            payload = run_response_level_benchmark(
                tmp,
                seed=seed,
                n_train=n_train,
                n_test=n_test,
                n_history=n_history,
            )
            for row in payload["summary"]:
                all_rows.append({"seed": seed, **row})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    methods = sorted({str(row["method"]) for row in all_rows})
    summary: list[dict] = []
    for method in methods:
        rows = [r for r in all_rows if r["method"] == method]
        rec: dict = {"method": method, "n_seeds": len(rows)}
        for field in FIELDS:
            values = [float(r[field]) for r in rows]
            rec[f"{field}_mean"] = statistics.mean(values)
            rec[f"{field}_sd"] = statistics.stdev(values) if len(values) > 1 else 0.0
            rec[f"{field}_min"] = min(values)
            rec[f"{field}_max"] = max(values)
        summary.append(rec)

    seed_csv = out / "paper_response_level_seeds.csv"
    with seed_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    summary_csv = out / "paper_response_level_repeated.csv"
    with summary_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)

    payload = {
        "seeds": seeds,
        "summary": summary,
        "n_train_users_per_seed": n_train,
        "n_test_users_per_seed": n_test,
        "n_history": n_history,
    }
    (out / "paper_response_level_repeated.json").write_text(json.dumps(payload, indent=2))
    return payload


if __name__ == "__main__":
    print(json.dumps(run_repeated_response_level(), indent=2))
