# Reproducibility Contract

## Environment
Python 3.11+.

```bash
pip install -e '.[dev]'
make test
make benchmark
python scripts/build_manifest.py
```

The full reference run requires no network access, hosted model, secret, GPU or external dataset.

## Generated outputs

The benchmark rebuilds the historical and paper-facing result files, including:

- `results/benchmark.csv` / `.json`
- `results/v2_context_benchmark.csv`
- `results/v2_results.json`
- `results/v3_seed_stability.csv`
- `results/v3_seed_summary.csv`
- `results/v3_synthetic_utility.csv`
- `results/v3_synthetic_comparisons.json`
- `results/v3_noise_stress.csv`
- `results/v3_change_detection.csv`
- `results/v3_results.json`
- `results/robustness.json`
- figures in `results/figures/`
- `dashboard/index.html`

## Randomness

Synthetic profile generation, interaction simulation, selection sampling, bootstrap resampling and the logistic-regression baseline all use explicit seeds. The repeated-seed suite reports five independent benchmark seeds rather than relying on one reference split.

## Statistical reporting

The repeated-seed analyses use non-parametric bootstrap confidence intervals and paired bootstrap deltas where user-level paired outcomes are available. The `bootstrap_two_sided_p` field is a descriptive bootstrap sign probability around zero; it is not presented as a classical parametric p-value.

## Release integrity

`python scripts/build_manifest.py` computes a SHA-256 digest and byte count for every packaged file except caches and the manifest itself. A released artifact can therefore be checked for accidental drift.

## Reference status

The release does not hard-code a test count in this document; `pytest -q` is the source of truth. The benchmark and paper-facing results are regenerated from fixed seeds.

## Optional foundation model

Supply any `prompt -> string` callable through `CompletionAdapter`. New model results should not be compared with reference numbers unless the same frozen split, user-state inference, relevance gate and grader contract are used.
