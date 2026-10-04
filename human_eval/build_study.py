from __future__ import annotations
import csv, json, random
from pathlib import Path

SCENARIOS = [
    ("cold_start", "The system has little evidence about the user's preference."),
    ("stable", "The user has repeatedly expressed a stable preference."),
    ("context", "The user prefers concise answers at work but detailed answers for research."),
    ("drift", "The user's previously stable preference has recently reversed."),
    ("ambiguous", "Observed behavior weakly suggests a preference but evidence is uncertain."),
    ("conflict", "Two pieces of evidence conflict, and one is more recent and explicit."),
    ("anti_personalization", "The query is factual and unrelated to known preferences."),
]

def build(out: Path, n_per_type: int = 12, seed: int = 41) -> None:
    rng = random.Random(seed)
    rows=[]
    for kind, desc in SCENARIOS:
        for i in range(n_per_type):
            left_is_personalized = rng.random() < 0.5
            rows.append({
                "item_id": f"{kind}-{i:03d}", "scenario_type": kind, "scenario": desc,
                "left_system": "personalized" if left_is_personalized else "baseline",
                "right_system": "baseline" if left_is_personalized else "personalized",
            })
    rng.shuffle(rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    meta={"seed":seed,"n_per_type":n_per_type,"items":len(rows),"scenario_types":[x[0] for x in SCENARIOS]}
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2))

if __name__ == "__main__":
    build(Path("human_eval/study_items.csv"))
