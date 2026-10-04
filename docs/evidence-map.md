# Evidence map

A compact map from the paper's claims to the experiment that supports them and the condition that would weaken them.

| Claim | Primary evidence | Main alternative explanation tested | What would weaken the claim |
|---|---|---|---|
| Informative synthetic examples can hurt downstream personalization | synthetic-policy comparison at 10 real interactions | poor selector proxy alone | consistent gains on matched repeated runs |
| Label correctness is not sufficient | pseudo vs. oracle augmentation | pseudo-label noise | oracle augmentation closes the gap |
| Evidence reweighting is a plausible mechanism in the controlled setting | 25-setting count × reliability sweep, r≈-0.988 | label noise | no relationship under matched sweeps or reversal under independent simulator |
| Dataset-level mass control mitigates the diagnosed failure | five-seed mass-cap experiment + exact paired-seed audit | lucky single seed | mitigation disappears across seeds or matched learners |
| Personalization requires restraint | five-seed response-choice benchmark | slot accuracy alone | always-personalize matches selective policy on irrelevant queries |
| Confidence supports selective use of user state | risk–coverage analysis | confidence unrelated to errors | flat/inverted risk–coverage curve |

## Evidence hierarchy

**Measured in this release:** controlled synthetic users, repeated seeds, oracle/pseudo diagnostics, response-choice evaluation, drift/noise stress tests, regression harness.

**Prepared but not measured here:** external benchmark runs, open-weight/foundation-model post-training, real-user longitudinal outcomes.

The second group is intentionally kept outside the result tables until raw outputs exist.

## Statistical restraint

Seed-level paired comparisons are summarized in [`docs/statistical-audit.md`](statistical-audit.md). With five paired seeds, a 5/5 directional result has a two-sided exact sign-test p-value of 0.0625; the project therefore treats those results as directional consistency, not high-powered significance evidence.
