# Reviewer guide

If you have five minutes, read the paper abstract and Sections 3–5, then inspect these three artifacts:

1. `results/paper_oracle_vs_pseudo.csv` — tests whether label noise explains the synthetic-data failure.
2. `results/paper_synthetic_mass_sweep.csv` — tests the evidence-mass mechanism.
3. `results/paper_mass_control_seeds.csv` — repeated-seed mitigation result.

If you have fifteen minutes, add:

- `results/paper_response_level_seeds.csv` for user-facing behavior and restraint;
- `docs/research-decisions.md` for the sequence of hypotheses and decisions;
- `artifacts/research_memo.md` for the research thesis;
- `docs/eval-harness.md` for task/trial/grader/trajectory semantics.

## Reproduce the paper-facing results

```bash
pip install -e '.[dev,paper]'
make paper
python scripts/verify_paper_claims.py
pytest -q
```

## Scope

The strongest evidence is mechanistic and controlled. External-model, external-benchmark, and real-user experiments are the next validation layer, not numbers inferred from the simulator.

## Statistical audit

Before interpreting repeated-seed headline deltas, read [`docs/statistical-audit.md`](statistical-audit.md). It reports paired seed deltas, exact sign tests, and the distinction between user-level bootstrap uncertainty and seed-level replication uncertainty.

## Threats to validity

Read [`docs/threats-to-validity.md`](threats-to-validity.md) for the strongest ways the current evidence could fail to generalize and the experiments that would falsify the present interpretation.
