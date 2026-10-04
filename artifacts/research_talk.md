# The Unfixed User — 9-minute Research Talk

## 1 — Problem (45 sec)
Personal assistants usually personalize through retrieval: store facts, fetch relevant memories, place them in context. That helps recall, but it does not answer a harder question: **how should an agent learn a changing person from sparse, noisy evidence without inventing preferences or personalizing when it should not?**

## 2 — Research contract (45 sec)
The Unfixed User treats personalization as a calibrated learning problem. Better means five things together: correct preference inference, context sensitivity, uncertainty awareness, temporal adaptation, and restraint when personalization is irrelevant.

## 3 — System (75 sec)
Real interactions become structured evidence with source reliability and context. A temporal user model aggregates evidence, tracks uncertainty and drift, and stores context-specific overrides. A relevance gate decides whether a preference should influence the request. A counterfactual generator proposes synthetic experiences, a verifier filters them, and a selection policy chooses candidates for training.

## 4 — Benchmark (60 sec)
Synthetic users provide controlled hidden ground truth, including context-dependent preferences and preference reversals. Evaluation covers cold start, conflict, drift, anti-personalization, long-horizon behavior, calibration, noise stress and repeated seeds.

## 5 — Sparse learning result (60 sec)
Across five independent seeds, context-conditioned accuracy of the trainable baseline rises from about 0.51 after three interactions to about 0.88 after fifty. The 95% bootstrap interval at fifty interactions is roughly 0.873–0.894. The important point is not the absolute synthetic score; it is that the learning curve and its variability are measured under a fixed contract.

## 6 — Anti-personalization (45 sec)
A personalized agent also needs to know when *not* to personalize. A lightweight learned relevance gate distinguishes preference-relevant prompts from generic factual tasks and cross-key distractors. The small held-out diagnostic reaches 87.5% accuracy with Brier score 0.065.

## 7 — The negative result (90 sec)
The most useful result was a failure. Decision-boundary selection successfully chooses more boundary-focused synthetic examples than random selection. But training on those pseudo-labels reduces held-out accuracy. Random and diversity selection also hurt. Uncertainty selection is approximately neutral relative to real-only training. So **an example looking informative is not evidence that its synthetic label is trustworthy enough to train on**.

This changes the agenda from “generate smarter synthetic data” to “estimate the downstream value and reliability of synthetic labels before updating the model.”

## 8 — Robustness (45 sec)
Under injected observation noise, global preference accuracy degrades gradually from about 0.95 at zero noise to about 0.75 at noise 0.32. A narrow induced-reversal benchmark verifies that the drift detector responds strongly to explicit changes, while the report is careful not to generalize that controlled result to natural human preference drift.

## 9 — What I would do next (60 sec)
The next experiment is utility-aware synthetic learning: learn a verifier calibrated on genuine human corrections, estimate expected downstream improvement before accepting pseudo-labels, and compare that against retrieval-only personalization on a frozen human benchmark. The architecture already separates user state, relevance gating, training and evaluation so a larger foundation model can be attached without changing the scientific contract.

## Closing
The core lesson is: **personalization is not remembering more about a user. It is learning the right user state, knowing how uncertain it is, knowing when it changed, and knowing when not to use it.**
