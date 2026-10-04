# External validation plan

External validity is intentionally gated on matched public-benchmark evidence.

## Gate A — recognized benchmark

Primary target: PersonaMem-v2/v3 dynamic/implicit preference tasks. Secondary targets may include PAHF-compatible scenarios or other public evolving-personalization benchmarks.

## Gate B — matched baselines

All methods must share the same foundation-model backend and decoding settings where applicable:

1. no personalization
2. full-history / long-context
3. retrieval-only memory
4. recency-weighted memory
5. explicit user-profile prompting
6. real-only learned preference model
7. PAHF-style memory + clarification/feedback baseline (where protocol permits)
8. synthetic augmentation without verification
9. verified synthetic augmentation
10. full The Unfixed User method

## Gate C — metrics

- personalized task accuracy / preference alignment
- incorrect personalization
- abstention/relevance precision and recall
- stale-preference error
- drift-recovery latency
- calibration (ECE/Brier where probabilistic outputs exist)
- human pairwise preference with over-personalization flags
- cost / interactions to target performance

## Gate D — statistics

- repeated seeds or repeated stochastic runs
- paired comparison on identical examples
- 95% bootstrap confidence intervals
- multiplicity-aware interpretation for large ablation families

## Gate E — frozen provenance

Record model identifier, endpoint/provider, date, prompt template hash, dataset version/hash, seed, raw model outputs, judge configuration, and analysis commit.

Only after these gates pass should the work make comparative performance claims beyond the controlled benchmark.
