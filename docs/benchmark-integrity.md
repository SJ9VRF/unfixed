# Benchmark integrity

The controlled benchmark is designed to isolate mechanisms, not to simulate a production data pipeline. This note states exactly where ground truth exists and where it is unavailable to the evaluated models.

## Separation of roles

- **Synthetic profile generation** defines latent preferences for each simulated user. Those states provide supervised labels for the structured training baseline and evaluation targets for held-out users.
- **Interaction simulation** emits noisy observations. It also stores `ground_truth` in event metadata for diagnostics and debugging.
- **Inference and learned preference models do not read that metadata.** They consume the observable fields: preference key, observed value, signal type, reliability, context, order, and relevance.
- **Oracle labels are used only in the named oracle diagnostic** that asks whether correcting synthetic labels removes the augmentation failure. Oracle-labeled examples are not part of the proposed deployment path.
- **Train and test users are disjoint** in the paper experiments. Models are fit on training-user states/events and scored on separately generated held-out users.

## What this benchmark can establish

It can support mechanistic claims inside the controlled simulator, including whether a failure survives label correction, how synthetic evidence mass changes a downstream learner, and whether restraint changes response-choice behavior under fixed task families.

It cannot establish real-user utility, population representativeness, demographic fairness, production robustness, or external-benchmark state of the art. Those require human data and matched public benchmarks.

## Leakage regression tests

`tests/test_benchmark_integrity.py` enforces two invariants:

1. changing or deleting simulator-only ground-truth metadata does not change preference inference;
2. the trainable preference feature extractor is invariant to event metadata.

`tests/test_link_integrity.py` also verifies that repository-facing relative links resolve, preventing a polished README from pointing to missing artifacts.

## Remaining simulator coupling

The simulator and the evaluated methods still share a closed preference ontology and task families. This is deliberate for causal isolation but makes the benchmark easier than open-world personalization. The external-evaluation adapters and human-study protocol are therefore separate validation stages, not evidence already claimed by this benchmark.
