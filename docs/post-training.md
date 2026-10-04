# Training and post-training details

## What is implemented

The reproducible reference path deliberately uses a low-capacity multinomial logistic preference model so the effect of evidence, context, synthetic augmentation, and selection can be isolated without a GPU or hosted API. Training examples are aggregated from explicit, implicit, and corrective interaction events. Query context is exposed to the learner and matching-context evidence receives additional weight.

The synthetic post-training experiment is closed-loop:

1. infer the current moving user state from real evidence;
2. generate counterfactual candidate experiences;
3. score candidates for plausibility, preference consistency, novelty/information value, and hallucination risk;
4. select candidates under a named policy;
5. convert accepted non-counterfactual candidates into low-reliability training evidence;
6. retrain the preference learner;
7. evaluate held-out users and reject synthetic-data claims unless downstream behavior improves.

The evaluated selection policies are random, uncertainty, diversity, failure-driven, information gain, and decision boundary. The strongest scientific result is negative: a candidate can look informative while degrading downstream held-out accuracy.

## What is not claimed

The release does **not** claim that reinforcement learning was executed. The architecture exposes an RL-compatible post-training boundary: the same verified trajectories, preference pairs, reward/evaluation contract, and frozen benchmark can be connected to preference optimization or RL without changing the evaluation protocol. That extension must be run and measured before any RL result is reported.

## Foundation-model backend

A provider-neutral OpenAI-compatible adapter can receive the structured user state after the relevance gate. Hosted-model quality, latency, and cost are intentionally not imputed into the offline headline results.

## Reproducibility

The benchmark, synthetic-data ablations, claim verifier, and quality gate are all included in the release. See `docs/reproducibility.md`, `docs/benchmark-spec.md`, and `paper/technical_report.md`.
