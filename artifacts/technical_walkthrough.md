# Five-minute technical walkthrough

## 0:00–0:45 — Problem

Most personalization systems are good at remembering a fact and weak at deciding whether that fact is still true, contextually relevant, or appropriate to use. I framed personalization as a moving-state estimation problem rather than a memory retrieval problem.

## 0:45–1:45 — System

The pipeline separates evidence ingestion, user-state inference, relevance gating, response generation, and evaluation. Explicit statements, implicit choices, and corrections have provenance and reliability. Context-specific evidence can override a global preference locally. A relevance gate can withhold personalization entirely.

## 1:45–2:45 — Research result

I expected targeted synthetic experience to improve sample efficiency. It did not. Decision-boundary and other “informative” selection methods often hurt held-out personalization. I tested the obvious explanation—pseudo-label errors—and found it was insufficient: oracle labels still degraded performance. A controlled mass sweep showed a strong relationship between synthetic evidence mass and the drop, suggesting redundancy amplification / distributional reweighting.

## 2:45–3:30 — Mitigation

I added a mass-controlled synthetic-data policy. Across repeated seeds it recovers most of the raw augmentation degradation while remaining statistically indistinguishable from the real-only reference. I report that as mitigation, not as an invented win.

## 3:30–4:15 — Model behavior and evals

The project includes response-level evaluation because user-state accuracy is not enough. The best state-aware policy outperforms an always-personalize policy while avoiding over-personalization on irrelevant factual requests. The eval stack now uses task / trial / grader / trajectory semantics, state verification, repeated trials, transcript preservation, and a release gate for regressions.

## 4:15–5:00 — Scale-up plan

I would keep the benchmark frozen, replace the reference learner with a production model, train on controlled evidence mixtures, add model- and human-calibrated graders, and run external benchmarks plus real-user studies. The important part is preserving attribution: generation, verification, data selection, training, and evaluation stay separate so regressions can be traced to the right layer.
