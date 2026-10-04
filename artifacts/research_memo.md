# Research memo — The Unfixed User

## Question

How should a personal model learn a user who is sparse, contextual, contradictory, and changing—without turning memory into an always-on source of bias?

## Research bet

Personalization should be treated as **selective state estimation**, not profile retrieval. The system should maintain uncertainty over user state, update that state as evidence changes, and abstain from using it when the current request does not benefit from personalization.

## What changed the research direction

The original plan expected carefully selected synthetic experience to improve sample efficiency. It did not. More informative synthetic examples often reduced held-out performance.

The tempting explanation was bad pseudo labels. That explanation failed: pseudo-label error was nearly zero in the targeted diagnostic, utility-calibrated selection contained no observed wrong labels, and oracle labels did not restore performance.

A controlled sweep then showed that increasing synthetic evidence mass tracked the degradation closely. The resulting hypothesis is that correlated synthetic evidence **reweights the learner's evidence distribution and amplifies its current belief**, even when individual labels are correct.

## Result

A simple mass cap recovers most of the raw synthetic-augmentation harm across repeated seeds without pretending to create a gain over real-only training. The useful lesson is not “synthetic data is bad”; it is that synthetic-data quality cannot be reduced to correctness or informativeness of individual samples. Its effect depends on how much correlated evidence it injects into training.

## Why this matters beyond the benchmark

The same failure pattern can appear in post-training systems that repeatedly generate data from a model's current beliefs. If data generation and selection do not account for correlated evidence mass, a pipeline can become more certain without becoming more correct.

## Next decisive experiment

The next experiment is not another synthetic selector. It is an external-model replication in which the same data mixtures are used for actual language-model adaptation and evaluated on frozen response-level tasks and an external personalization benchmark. The claim should graduate only if the mechanism survives that change in learner and evaluation distribution.
