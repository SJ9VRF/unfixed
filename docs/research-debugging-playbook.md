# Research debugging playbook

The project is organized around a simple rule: **a metric change is not an explanation**.

When an experiment moves, the debugging sequence is:

1. **Reproduce across seeds.** Eliminate lucky runs before interpreting the result.
2. **Inspect task families.** Determine whether the change is broad or isolated to drift, context, conflict, or restraint.
3. **Read trajectories.** Separate genuine model failures from evaluator or harness failures.
4. **Check labels and state.** Verify that the task remains solvable and the expected user state is internally consistent.
5. **Run the closest ablation.** Remove one source of complexity at a time.
6. **Measure the mechanism directly.** Prefer a diagnostic quantity over a story inferred from aggregate accuracy.
7. **Only then change the method.** A mitigation should target the observed mechanism rather than the most convenient component.

This sequence produced the central result in the project. The first hypothesis was that synthetic augmentation failed because pseudo labels were wrong. Direct measurement showed a pseudo-label error rate of only 0.045%, and oracle labels still failed to remove the degradation. A synthetic-evidence-mass sweep then exposed the stronger relationship with evidence reweighting, which led to mass control as the targeted mitigation.

The same standard applies to future foundation-model runs. If an LLM underperforms, the first question is not “what prompt should we try?” but whether the failure comes from user-state inference, relevance gating, response generation, the grader, or the environment.
