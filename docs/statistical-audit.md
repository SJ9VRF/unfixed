# Statistical audit

This audit treats independent benchmark seeds as the unit of replication for the repeated-seed headline comparisons. It is intentionally conservative: five seeds are useful for checking directional stability, but they are too few for strong asymptotic significance claims.

## Exact paired-seed checks

| Comparison | Mean paired delta | Wins / losses | Two-sided exact sign p | Paired effect dz |
|---|---:|---:|---:|---:|
| Raw synthetic − real-only | -0.0325 | 0 / 5 | 0.0625 | -3.47 |
| Mass-capped − raw synthetic | +0.0307 | 5 / 0 | 0.0625 | 4.87 |
| Mass-capped − real-only | -0.0018 | 3 / 2 | 1.0000 | -0.23 |
| Bayesian response − always-personalize | +0.0892 | 5 / 0 | 0.0625 | 14.73 |
| Bayesian response − generic | +0.2636 | 5 / 0 | 0.0625 | 9.91 |
| Bayesian response − last-event | +0.0111 | 5 / 0 | 0.0625 | 1.55 |
| Inferred-state response − last-event | +0.0009 | 3 / 2 | 1.0000 | 0.21 |

## Interpretation

- Raw synthetic augmentation is worse than real-only in all five seeds.
- Mass capping improves over raw augmentation in all five seeds, but with only five paired seeds the two-sided exact sign test is still 0.0625. The release therefore describes this as a consistent mitigation, not a statistically definitive superiority claim.
- Mass-capped augmentation is mixed relative to real-only (3 wins, 2 losses) and should not be described as an improvement over the real-only reference.
- The Bayesian response policy beats always-personalize, generic, and last-event baselines in all five seeds. The repeated direction is encouraging, but the same five-seed limitation applies.
- Inferred-state and last-event response policies are effectively tied at this replication level (3 wins, 2 losses, very small mean delta).

## Why this file exists

A small-seed research artifact can look more certain than it is if it reports only means. This audit keeps the unit of replication explicit and prevents seed-level consistency from being misreported as high-powered statistical evidence. User-level bootstrap intervals in the paper answer a different question: uncertainty over held-out examples conditional on the benchmark design.
