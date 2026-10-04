# Research decisions

This is the short version of how the project changed when the evidence disagreed with the original plan.

## 1. Synthetic selection was supposed to improve sample efficiency

The first hypothesis was straightforward: generate counterfactual interactions, select the most informative ones, and use them to improve personalization with fewer real interactions.

That hypothesis failed. Boundary-focused and diversity-based selection produced examples that looked useful under proxy scores but reduced held-out accuracy after training.

**Decision:** stop optimizing the selection proxy and measure downstream utility directly.

## 2. Label noise looked like the obvious explanation

The next hypothesis was that selected synthetic examples were simply mislabeled near decision boundaries.

Targeted diagnostics did not support it. Pseudo-label error was negligible in the diagnostic set, and oracle labels did not remove the degradation.

**Decision:** treat label correctness as necessary but insufficient, and test dataset-level effects.

## 3. The failure tracked evidence mass

Sweeping the number and weight of synthetic examples exposed a strong relationship between total synthetic evidence mass and downstream degradation. Repeated synthetic evidence was changing the effective training distribution even when individual labels were correct.

**Decision:** move the intervention from sample scoring to dataset composition. Cap synthetic evidence mass and discount repeated preference-context signatures.

## 4. The mitigation is deliberately modest

Mass control recovers most of the harm caused by raw augmentation, but it does not establish an improvement over real-only training.

**Decision:** report it as a mechanism-grounded mitigation, not as a win manufactured from an ablation.

## 5. Slot accuracy was not enough

A personal model can infer a user state correctly and still produce an irrelevant or intrusive response.

**Decision:** add response-level evaluation and a relevance gate. Measure both useful personalization and restraint on queries that do not need user context.

## 6. Drift detection was not a contribution

The project's custom drift heuristic worked, but standard EWMA/CUSUM baselines were stronger in the controlled benchmark.

**Decision:** keep drift detection as infrastructure and remove it from the novelty story.

## 7. What would change the conclusion

The central mechanism is currently established in a controlled learner and simulator. The next decisive test is to hold the data mixtures and evaluation contract fixed while changing the learner and data distribution: open-weight/foundation-model adaptation, an external personalization benchmark, and real-user evaluation.

A failure to reproduce the evidence-mass effect there would narrow the claim rather than be explained away.
