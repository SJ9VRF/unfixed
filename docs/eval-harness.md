# Frontier-style evaluation harness

This project treats evaluation as part of the research stack rather than as a final benchmark script.

The harness uses four explicit objects:

- **Task** — a problem with an initial state and success criteria.
- **Trial** — one independent attempt at a task.
- **Grader** — one scoring function for an outcome or behavior.
- **Trajectory** — the inspectable trace of observations, state reads, and decisions.

The reference suite intentionally separates outcome grading from trajectory inspection. A valid solution is not rejected merely because it took a different path; trajectories are preserved for debugging and auditing.

## Graders

The included smoke suite uses four deterministic graders:

1. `outcome_match` — did the system make the correct user-facing choice?
2. `restraint` — did it personalize only when personalization was appropriate?
3. `state_verification` — did the final user state match the task's verified state?
4. `trajectory_sanity` — is the trial trace complete enough to inspect?

The reference suite is a **regression smoke test**, not a capability benchmark. Its job is to verify that the harness, task contracts, state checks, and trajectory capture are working before expensive model evaluation begins.

## Model-change gate

`python scripts/model_change_gate.py` applies frozen release thresholds to the strongest behavior-level results in the repository. A candidate system change fails if it causes a material regression in response accuracy, over-personalization, mass-controlled synthetic training, or the smoke eval suite.

This is deliberately conservative: it is easier to loosen a threshold with an explicit research decision than to discover a silent regression after a model or training-data change.

## Running

```bash
python -m frontier_eval.run_reference --trials 5
python scripts/model_change_gate.py
```

Outputs:

- `results/frontier_eval_report.json`
- `results/model_change_gate.json`
