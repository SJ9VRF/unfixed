# Research Notebook — The Unfixed User

## H1 — Learned personalization beats sparse retrieval
Supported in the controlled cold-start benchmark at low interaction counts. At five interactions the learned real-only baseline scores 0.623 versus 0.436 for retrieval-weighted voting.

## H2 — More synthetic data automatically improves personalization
Not supported. The current synthetic-augmented learner scores 0.606 at five interactions versus 0.623 real-only and remains lower at larger interaction counts. This changed the research direction toward uncertain decision boundaries rather than indiscriminately adding self-generated evidence.

## H3 — Context must be represented in the ground truth, not just the event schema
Supported. The earliest scaffold stored context labels but did not make the correct preference depend on context. The subsequent controlled simulator changed the true value as a function of context. This made context accuracy a meaningful metric.

## H4 — Boundary-targeted generation selects qualitatively different data
Supported by the mechanism diagnostic. Mean selected boundary score rises from 0.221 under random selection to 0.296 under the dedicated policy. This does not yet prove downstream training improvement; that is a separate experiment.

## H5 — Anti-personalization can be learned rather than hard-coded
Partially supported. A small key-aware semantic relevance gate reaches 87.5% held-out accuracy with Brier score 0.065 on controlled paraphrases/cross-key negatives. The sample is too small for a real-world claim, so the result remains a mechanism proof rather than an external-validity result.

## H6 — Preference drift should temporarily reduce certainty
Implemented. The engine exposes a drift score and caps confidence when recent evidence strongly disagrees with older evidence. Controlled recovery median is 10 interactions.

## Open questions

- Does training directly on decision-boundary samples improve sample efficiency?
- What is the best change-point detector under gradual rather than abrupt drift?
- How does the relevance gate behave on genuine multi-turn conversations?
- Does a large language model exploit calibrated user-state evidence better than a low-capacity learner without increasing sycophancy?
- How stable are these results across multilingual interactions and noisier implicit signals?
