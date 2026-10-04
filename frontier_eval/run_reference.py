from __future__ import annotations

import argparse
import time
from pathlib import Path

from .graders import outcome_match, restraint, state_verification, trajectory_sanity
from .harness import EvalHarness, EvalTask
from .reference_suite import build_reference_tasks


def reference_agent(task: EvalTask, trial_index: int):
    start = time.perf_counter()
    state = dict(task.initial_state)
    if task.family == "anti_personalization":
        decision, personalized = "factual", False
    elif state.get("travel_priority") == "price":
        decision, personalized = "cheaper", True
    elif state.get("travel_priority") == "comfort":
        decision, personalized = "convenient", True
    elif state.get("work_style") == "detailed":
        decision, personalized = "detailed", True
    else:
        decision, personalized = "generic", False
    trajectory = [
        {"event": "observe", "prompt": task.prompt},
        {"event": "read_state", "state": state},
        {"event": "decide", "decision": decision, "personalized": personalized},
    ]
    latency_ms = (time.perf_counter() - start) * 1000
    return {"decision": decision, "personalized": personalized}, state, trajectory, latency_ms, 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/frontier_eval_report.json")
    parser.add_argument("--trials", type=int, default=5)
    args = parser.parse_args()
    harness = EvalHarness(reference_agent, [outcome_match, restraint, state_verification, trajectory_sanity], args.trials)
    report = harness.run(build_reference_tasks())
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    report.to_json(args.out)
    print(report.summary())


if __name__ == "__main__":
    main()
