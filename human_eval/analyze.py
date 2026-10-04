from __future__ import annotations
import csv, json, random, statistics
from collections import defaultdict
from pathlib import Path

def bootstrap_ci(xs, n=5000, seed=17):
    if not xs: return (float('nan'), float('nan'))
    rng=random.Random(seed); vals=[]
    for _ in range(n): vals.append(statistics.mean(rng.choice(xs) for _ in xs))
    vals.sort(); return vals[int(.025*n)], vals[int(.975*n)-1]

def analyze(path: Path) -> dict:
    rows=list(csv.DictReader(path.open()))
    wins=[]; over=[]; stale=[]; invented=[]
    by_type=defaultdict(list)
    for r in rows:
        # winner is expected as left/right/tie in collected annotation export.
        winner=r.get("winner","").lower(); left=r.get("left_system",""); right=r.get("right_system","")
        if winner in {"left","right"}:
            sys = left if winner=="left" else right
            x=1.0 if sys=="personalized" else 0.0; wins.append(x); by_type[r.get("scenario_type","unknown")].append(x)
        elif winner=="tie":
            wins.append(.5); by_type[r.get("scenario_type","unknown")].append(.5)
        for col, dest in [("over_personalized",over),("stale_preference",stale),("invented_preference",invented)]:
            v=r.get(col,"").lower();
            if v in {"1","true","yes"}: dest.append(1)
            elif v in {"0","false","no"}: dest.append(0)
    lo,hi=bootstrap_ci(wins)
    return {"annotations":len(rows),"pairwise_personalized_win_rate":statistics.mean(wins) if wins else None,
            "pairwise_95ci":[lo,hi] if wins else None,
            "over_personalization_rate":statistics.mean(over) if over else None,
            "stale_preference_rate":statistics.mean(stale) if stale else None,
            "invented_preference_rate":statistics.mean(invented) if invented else None,
            "win_rate_by_scenario":{k:statistics.mean(v) for k,v in sorted(by_type.items()) if v}}

if __name__ == "__main__":
    p=Path("human_eval/annotations.csv")
    if not p.exists():
        raise SystemExit("No human_eval/annotations.csv found; collect real labels first.")
    print(json.dumps(analyze(p), indent=2))
