# When “Informative” Synthetic Data Makes Personalization Worse

Personalization is often described as a memory problem: store what a user says, retrieve it later, and condition the model on it. That framing breaks as soon as preferences are contextual, uncertain, or changing. A person can prefer concise answers for routine questions and detailed answers for research; they can optimize travel for price until a high-stakes trip changes the tradeoff; and a stored preference can be perfectly real yet completely irrelevant to the next request.

**The Unfixed User** treats personalization as state estimation under uncertainty rather than profile lookup. The system separates observations from inferred state, tracks confidence and provenance, allows context-specific values, detects evidence that a preference may be changing, and uses a relevance gate to ask whether personalization should be applied at all.

The surprising result came from synthetic experience. Boundary-focused selection did exactly what it was designed to do: it selected examples that looked more informative according to the mechanism diagnostic. But when pseudo-labeled synthetic examples were added to downstream training, the most “interesting” examples did not reliably improve held-out context accuracy. Some selection policies made the learner worse.

That failure changed the project. Synthetic data is no longer treated as free supervision. Every candidate must be verified, and selection quality is separated from downstream training utility. The research question becomes stricter: not “can we generate plausible personalized experiences?” but “does this generated experience measurably help the learner on held-out users and contexts?”

The benchmark therefore measures cold start, context dependence, preference drift, conflict, calibration, over-personalization, long-horizon stability, noise robustness and downstream synthetic-data utility. Repeated-seed evaluation and bootstrap intervals are used so a single favorable run cannot carry the conclusion.

The current release is deliberately narrow about what it claims. Results come from controlled synthetic users, not a real population. A blind human-evaluation protocol and an external-model adapter are included, but no human or frontier-model result is reported until it is actually collected. The goal is a research artifact whose strongest signal is not polish alone, but a falsifiable contract between the claim and the evidence.

— Aura Yavary
