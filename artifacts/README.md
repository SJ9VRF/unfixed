# Raw Research Artifacts

This directory is the Evidence Layer behind the polished project page.

- `experiment_logs/` — one structured record per documented experiment
- `eval_runs/` — frozen CSV/JSON outputs copied from the canonical `results/` directory
- `failure_examples/` — failures that changed the research direction
- `plots/` — generated figures from the same result files
- `configs/` — parameter snapshots tied to source functions
- `qualitative_cases/` — non-cherry-picked response cases, including errors and no-personalize controls
- `ablations/` — raw ablation tables

Canonical result files remain under `results/`; these mirrors exist so a reviewer can inspect the research trail without hunting through the repository.

## Provenance registry

`evidence_registry.json` maps every documented experiment to code, configs, raw outputs, reproduction commands, and SHA-256 hashes. Regenerate it with `python scripts/build_evidence_registry.py`.
