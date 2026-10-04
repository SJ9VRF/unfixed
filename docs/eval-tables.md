# Real Eval Tables

These tables are copied from the frozen result files; values are not hand-edited hero numbers.

## Cold-start benchmark

| Variant | 5 interactions | 10 interactions | 20 interactions | 50 interactions | Notes |
|---|---:|---:|---:|---:|---|
| Retrieval-weighted vote | 0.436 | 0.661 | **0.854** | **0.963** | sparse-history weakness, strong dense-history baseline |
| Learned real-only | **0.623** | **0.743** | 0.847 | 0.953 | strongest in the sparse regime |
| Learned + naive synthetic | 0.606 | 0.720 | 0.839 | 0.934 | consistently below real-only |

Raw: [`results/benchmark.csv`](../results/benchmark.csv)

## Synthetic-data policy at 10 real interactions

| Variant | Context accuracy | 95% interval | Interpretation |
|---|---:|---:|---|
| Real-only | 0.663 | 0.629–0.695 | reference |
| Uncertainty | 0.663 | 0.630–0.695 | effectively tied |
| Failure-driven | 0.655 | 0.623–0.689 | no improvement |
| Information-gain-style | 0.655 | 0.623–0.687 | no improvement |
| Decision boundary | 0.631 | 0.599–0.662 | informative-looking but harmful |
| Diversity | 0.605 | 0.573–0.639 | harmful |
| Random | 0.600 | 0.569–0.630 | largest degradation |

Raw: [`results/v3_synthetic_utility.csv`](../results/v3_synthetic_utility.csv)

## Oracle diagnostic

| Variant | Accuracy | 95% interval | Label note |
|---|---:|---:|---|
| Real-only | **0.664** | 0.643–0.685 | no synthetic evidence |
| Pseudo synthetic | 0.613 | 0.589–0.638 | 1/2200 observed label errors |
| Oracle synthetic | 0.609 | 0.585–0.633 | simulator oracle labels |
| UCES synthetic | 0.587 | 0.561–0.613 | 0/2173 observed label errors in diagnostic selection |

Raw: [`results/paper_oracle_vs_pseudo.csv`](../results/paper_oracle_vs_pseudo.csv)

## Dataset-level mitigation — five seeds

| Variant | Mean accuracy | 95% interval | Δ vs real-only | Notes |
|---|---:|---:|---:|---|
| Real-only | **0.660** | 0.653–0.667 | — | reference |
| Raw UCES augmentation | 0.627 | 0.615–0.636 | −0.0325 | degradation in all five seeds |
| Mass-capped UCES | 0.658 | 0.649–0.667 | −0.0018 | recovers ~94.5% of harm; does not beat real-only |

Seeds: 701, 733, 761, 797, 823. Exact paired-seed analysis: [`docs/statistical-audit.md`](statistical-audit.md).

Raw: [`results/paper_mass_control.csv`](../results/paper_mass_control.csv), [`results/paper_mass_control_seeds.csv`](../results/paper_mass_control_seeds.csv)

## Response-level behavior — five seeds

| Variant | Overall accuracy mean ± SD | No-personalize accuracy | Over-personalization | Notes |
|---|---:|---:|---:|---|
| Bayesian state + restraint | **0.680 ± 0.013** | 1.000 | 0.000 | best controlled policy |
| Inferred state + restraint | 0.670 ± 0.009 | 1.000 | 0.000 | close to last-event |
| Last event + restraint | 0.669 ± 0.008 | 1.000 | 0.000 | strong simple baseline |
| Structured learner | 0.640 ± 0.017 | 1.000 | 0.000 | lower personalized-choice accuracy |
| Always personalize | 0.591 ± 0.009 | 0.000 | 1.000 | fails restraint cases |
| Neural response ranker | 0.450 ± 0.022 | 1.000 | 0.000 | negative learned baseline |
| Generic | 0.417 ± 0.027 | 1.000 | 0.000 | no user-state benefit |

Raw: [`results/paper_response_level_repeated.csv`](../results/paper_response_level_repeated.csv)

## Drift baselines

| Detector | ROC-AUC |
|---|---:|
| CUSUM | **0.981** |
| EWMA | 0.980 |
| Bayesian shift | 0.969 |
| Project heuristic | 0.928 |

Raw: [`results/paper_drift_baselines.csv`](../results/paper_drift_baselines.csv)
