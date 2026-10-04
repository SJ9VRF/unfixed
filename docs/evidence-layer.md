# Evidence Layer

The polished project page is the summary. This directory is the research trail.

**13 documented experiments · 5 failed hypotheses · 6 major research decisions · 4 primary failure modes**

- [Experiment journal](experiment-log.md)
- [What didn’t work](failed-experiments.md)
- [Decision log](decision-log.md)
- [Real eval tables](eval-tables.md)
- [Unexpected findings](unexpected-findings.md)
- [Failure trace](failure-trace.md)
- [Git provenance](git-provenance.md)
- [Statistical audit](statistical-audit.md)
- [Benchmark integrity](benchmark-integrity.md)

Raw evidence is mirrored under `artifacts/experiment_logs/`, `artifacts/eval_runs/`, `artifacts/failure_examples/`, `artifacts/plots/`, `artifacts/configs/`, `artifacts/qualitative_cases/`, and `artifacts/ablations/`.

## Machine-readable provenance

The experiment journal is backed by [`artifacts/evidence_registry.json`](../artifacts/evidence_registry.json) and the human-readable [`evidence registry`](evidence-registry.md). Each experiment is linked to its code, frozen inputs/config, raw outputs, reproduction command, and content hashes.
