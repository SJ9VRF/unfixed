# The Unfixed User: Mechanisms and Evaluation for Continual Personalization

## Abstract

The Unfixed User studies personalization as an online inference and post-training problem rather than a static memory lookup problem. The system maintains an uncertain, context-conditioned user state; incorporates explicit, implicit and corrective feedback; detects recent preference changes; generates counterfactual experiences concentrated near current decision boundaries; verifies synthetic data before selection; and withholds personalization through a learned semantic relevance gate. The complete reference implementation is offline, deterministic under fixed seeds and paired with cold-start, context, drift, conflict, long-horizon and anti-personalization evaluations.

The controlled V2 benchmark uses 220 training and 90 held-out synthetic users with seven preference dimensions and context-dependent overrides. Context-aware inference reaches 0.894 context-conditioned accuracy after 50 interactions; a trainable context model reaches 0.891. A small held-out semantic relevance benchmark yields 87.5% gate accuracy with Brier score 0.065. Decision-boundary selection raises the mean boundary-targeting score of selected verified synthetic experiences from 0.221 under random selection to 0.296. Synthetic augmentation is not an unconditional win in the reference setting and can reduce predictive accuracy, which is retained as a negative result.

## Novelty and related work

The project does **not** claim that evolving user profiles, preference drift, counterfactual preference data, or over-personalization are individually new. Recent systems and benchmarks already cover each of those ideas. The research position is narrower: combine a non-stationary context-conditioned user state with calibrated abstention and verified counterfactual experience, then judge synthetic data by **downstream personalization utility** rather than by how informative the selected examples appear.

We call the observed divergence between proxy informativeness and post-training benefit the **Synthetic Experience Utility Gap**. In the current controlled study, decision-boundary selection finds intuitively informative examples but can degrade held-out accuracy under imperfect pseudo-labels.

See `docs/novelty-audit.md` for the literature audit and `docs/external-validation-plan.md` for the evidence required before any state-of-the-art claim is permitted.

## 1. Research Question

The core question is:

> How can a personal agent learn an individual from sparse real interactions, adapt when preferences change, and improve through synthetic or counterfactual experience without over-personalizing or becoming overconfident?

This decomposes into five subproblems:

1. infer preferences from sparse, noisy and heterogeneous evidence;
2. represent context dependence rather than collapsing a person into one global value;
3. detect when recent evidence suggests a preference has changed;
4. decide whether a personal preference is relevant to the current request at all;
5. select synthetic experiences that improve information coverage rather than merely reinforce current beliefs.

## 2. User-State Representation

Each preference stores a global value and confidence, evidence count, provenance, stability, temporal evidence, uncertainty reason, drift score and optional context-specific values. A lookup can therefore return a context-specific value when evidence supports one, otherwise falling back to the global preference.

This representation is intentionally more expressive than a vector-database memory. It distinguishes the content of a belief from how strongly the system should trust it and where the belief applies.

## 3. Evidence Inference

Interaction signals are explicit statements, implicit behavior or corrections. Reliability is signal-dependent. Corrections receive additional weight. Recent evidence is exponentially upweighted relative to older evidence so the inferred state can adapt after preference drift.

For each preference value, weighted evidence is aggregated. Confidence combines evidence quantity and the margin between the leading and competing values. Context-specific estimates are created only after a minimum evidence threshold. A lightweight change detector compares older and recent evidence; disagreement with concentrated recent support, especially corrective support, increases the drift score and caps confidence during transition.

## 4. Context-Conditioned Personalization

Synthetic users can contain real context-specific ground truth, for example a preference that differs in `work` versus `general`. Interaction simulation first samples the context and then samples observations from the corresponding true contextual value. This closes a weakness of simpler benchmarks where a context label exists but never changes the correct answer.

The evaluator measures both global preference accuracy and context-conditioned accuracy over `general`, `work`, `travel`, `high_stakes` and `casual` contexts.

## 5. Anti-Personalization Gate

The relevance gate treats personalization itself as a prediction problem. Given a request and a candidate preference key, it predicts whether using that preference is appropriate. The reference gate is a small trainable classifier using deterministic hashed lexical/cross features plus configurable semantic-key overlap features. It is intentionally lightweight and replaceable by an embedding or foundation-model classifier while preserving the same evaluation API.

The held-out test includes paraphrases, generic factual questions and cross-key negatives where a personal preference exists but is irrelevant to the request. On the reference run the gate obtains 87.5% accuracy and Brier score 0.065 on 16 held-out cases after training on 42 controlled relevance pairs.

## 6. Synthetic and Counterfactual Experience

The generator proposes both anchor-consistent and counterfactual experiences across multiple contexts. V2 adds a `boundary_score` driven by current preference uncertainty and contextual disagreement. This score concentrates training candidates near parts of the user model where additional evidence is expected to be informative.

The verifier scores plausibility, consistency, novelty, information value and hallucination risk. Rejected experiences are not eligible for selection.

Selection supports random, uncertainty, diversity, failure-driven, information-gain and decision-boundary policies. In the controlled V2 experiment, selected boundary score is 0.296 for decision-boundary selection versus 0.221 for random selection and 0.210 for the existing information-gain policy.

## 7. Training Baseline

The trainable baseline is a multinomial logistic model over aggregated interaction features. V2 exposes query context during training and prediction and gives matching-context evidence additional weight. This is deliberately low capacity: the goal of the reference implementation is to isolate learning mechanisms and evaluations without requiring a GPU or hosted API.

A provider-agnostic foundation-model adapter is included separately. The training/evaluation core therefore runs offline while the same user-state and gating interfaces can later ground a larger model.

## 8. Experiments

### 8.1 Context-conditioned benchmark

| Real interactions | Context-aware inference | Trainable context model |
|---:|---:|---:|
| 1 | 0.716 | 0.397 |
| 3 | 0.785 | 0.509 |
| 5 | 0.767 | 0.579 |
| 10 | 0.803 | 0.688 |
| 20 | 0.828 | 0.806 |
| 50 | 0.894 | 0.891 |

The dip between three and five interactions for the heuristic method is retained. With sparse noisy evidence, additional observations can temporarily move the inferred state in the wrong direction. This is a desirable property of the benchmark: it exposes uncertainty rather than forcing monotonic curves.

### 8.2 Cold-start baseline

At five interactions, preference-state accuracy is 0.436 for retrieval-weighted voting, 0.623 for the learned real-only baseline and 0.606 for the learned synthetic-augmented baseline.

### 8.3 Drift

Median recovery after an induced preference reversal is 10 interactions. 68.75% of cases recover within 10 interactions in the controlled suite.

### 8.4 Conflicting evidence

The explicit-correction conflict suite reaches 100% resolution accuracy. This is a narrow controlled test and should not be generalized to arbitrary natural-language contradictions.

### 8.5 Long-horizon state recovery

Preference-state accuracy is 0.877 at 20 turns, 0.957 at 50 turns, 0.989 at 100 turns and 1.000 at 250 turns under the synthetic simulator.

## 9. Negative Result: Synthetic Augmentation

Synthetic data does not automatically improve the low-capacity learner. In the current run, synthetic augmentation lowers five-interaction accuracy from 0.623 to 0.606 and also trails the real-only baseline at larger interaction counts. Some sparse settings show fewer high-confidence errors, but that does not justify a headline claim of better performance.

This result motivates the V2 shift from generic synthetic augmentation toward boundary-targeted generation and stricter downstream utility evaluation. A future experiment should train directly on selected decision-boundary examples and measure whether their marginal value exceeds the cost and calibration risk of self-generated data.

## 10. Failure Taxonomy

The project tracks at least the following failure classes:

- stale-preference use after drift;
- context collapse, where a local preference is incorrectly generalized globally;
- over-personalization on irrelevant requests;
- under-personalization despite relevant high-confidence evidence;
- false certainty under competing evidence;
- synthetic self-reinforcement;
- cross-key relevance mistakes;
- sparse-evidence instability;
- mismatch between automatic and human graders.

## 11. Foundation-Model Integration

`GroundedFoundationBackend` accepts a generic completion adapter. Before calling a model, it applies the same personalization gate used in the offline benchmark. When personalization is allowed, only the relevant preference, value and confidence are supplied, with an instruction not to generalize beyond the observed context. When the gate rejects personalization, no user preference is passed.

This design keeps the research claims independent of any specific provider while making the system ready for a larger language-model backend.

## 12. Reproducibility

The default experiment suite runs with:

```bash
pip install -e '.[dev]'
pytest -q
python scripts/run_all.py
```

The current release regenerates its metrics, JSON artifacts, CSVs, figures and dashboard from fixed seeds. `pytest -q` is the source of truth for the active test count.

## 13. Limitations

The strongest limitation is external validity. The users and interactions are synthetic, and the semantic gate benchmark is intentionally small. The system does not claim that its synthetic scores represent satisfaction or trust of real users. No human-study result is invented. Annotation and grader-calibration infrastructure is included for a future real evaluation.

The reference learner is also intentionally low capacity. Its purpose is a reproducible research harness, not state-of-the-art personalized language generation. The provider-agnostic model adapter separates this methodological scaffold from a future large-model experiment.

## 14. Next Research Experiments

The most valuable next experiments are: train directly on decision-boundary-selected examples; compare heuristic drift detection with Bayesian online change-point detection; calibrate the relevance gate on genuine human labels; test multilingual context consistency; and attach a capable instruction-following foundation model while freezing the benchmark and grading contract in advance.

## 15. Statistical Stability and Downstream Synthetic Utility

This stage of the study addresses two weaknesses of the earlier reference: dependence on a single random seed and evaluation of synthetic selection using proxy scores rather than downstream learning.

### 15.1 Repeated-seed stability

The context-aware trainable baseline was rerun over five independent seeds. Each seed used 140 training users and 60 held-out users. Mean context-conditioned accuracy rises from 0.512 at three interactions to 0.883 at fifty interactions. The 95% bootstrap interval at fifty interactions is [0.873, 0.894]. The repeated-seed experiment therefore supports the qualitative cold-start trend without relying on one favorable split.

### 15.2 Does selected synthetic data actually help?

Six selection policies were evaluated by augmenting five real interactions per training user and then measuring held-out context accuracy after ten real interactions. Real-only training reaches 0.663. Uncertainty-selected augmentation reaches 0.663 and is statistically indistinguishable from real-only under paired bootstrap resampling. Failure-driven and information-gain augmentation are slightly lower at 0.655. Decision-boundary augmentation reaches 0.631, diversity 0.605, and random augmentation 0.600.

The paired mean deltas versus real-only are approximately -0.063 for random, +0.0004 for uncertainty, -0.058 for diversity, -0.008 for failure-driven, -0.008 for information gain, and -0.032 for decision-boundary selection. The confidence intervals for random, diversity and decision-boundary augmentation exclude zero in the harmful direction.

This result changes the research interpretation. Decision-boundary selection does achieve its intended *selection proxy*—it chooses more boundary-focused candidates—but those pseudo-labels do not produce better downstream learning. In the current system, uncertainty selection is the only synthetic policy that preserves real-only performance. Selection quality and label quality must therefore be separated.

### 15.3 Noise stress

A controlled observation-noise sweep tests whether user-state inference degrades gracefully. Mean global preference accuracy falls from 0.953 at zero injected noise to 0.881 at noise 0.16 and 0.751 at noise 0.32. The monotone degradation is useful as a regression diagnostic and exposes the expected failure surface rather than hiding it behind a single nominal-noise result.

### 15.4 Drift detection discrimination

A narrow 180-case diagnostic contrasts stationary histories with explicit induced reversals. The current drift score separates these constructed classes with ROC-AUC 1.00. This is *not* evidence of perfect real-world change-point detection: the benchmark intentionally contains strong explicit/corrective post-change evidence. Its role is to verify that the implemented detector responds correctly under an unambiguous controlled intervention before harder ambiguous-drift benchmarks are introduced.

## 16. Updated Conclusions

The strongest supported claims of the current artifact are methodological rather than product-level. Sparse user evidence can be represented as context-conditioned, uncertainty-bearing state; personalization can be gated as a relevance problem; preference changes can be surfaced explicitly; and synthetic experiences can be generated and verified under a reproducible contract. Crucially, the repeated-seed study shows that synthetic examples that score well under a selection heuristic may still hurt downstream prediction. The next research target is therefore **verified label utility**, not merely more sophisticated synthetic sampling.


## 17. Assurance, Privacy Boundaries, and Artifact Evaluation

The assurance layer leaves the scientific headline metrics unchanged and strengthens the evidence chain around them. The release now executes schema/data validation, recursive secret-like value redaction, a red-team regression suite, an append-only experiment registry, and a coverage-enforced quality gate. The quality gate compiles the source tree, runs all tests, requires at least 70% measured coverage, and executes the red-team suite before a release can pass.

The red-team suite checks four concrete invariants in the reference implementation: irrelevant events do not create inferred preferences; corrective evidence can overturn earlier weak implicit evidence; secret-like metadata is redacted; and free-form metadata cannot inject an instruction into preference inference. These are controlled engineering regressions, not a claim of complete adversarial robustness.

A threat model explicitly separates research safeguards from production guarantees. The released benchmark uses synthetic users and contains no intentionally collected personal human data. Production deployment would still require encryption, IAM, deletion/retention controls, consent/governance, and substantially stronger adversarial testing.

The release includes an artifact-evaluation guide, Docker deployment path, citation metadata, license, changelog, JSON schema, and experiment registry so that reviewers can reproduce the supported claims without reverse-engineering the repository.

---

## Mechanism experiments: Synthetic Experience Utility Gap

The paper-specific suite isolates why synthetic augmentation underperforms real-only training.

### Oracle-vs-pseudo diagnosis

On a held-out context evaluation, real-only training reaches **0.6643** accuracy. Decision-boundary pseudo augmentation reaches **0.6129** even though only **1 / 2200** selected pseudo labels is wrong. Replacing every selected synthetic label with simulator oracle truth reaches **0.6086**, so label error is not a sufficient explanation. Utility-calibrated selection observes **0 selected wrong labels** in the diagnostic but reaches **0.5869**.

### Evidence-mass diagnosis

A 25-setting sweep varies synthetic sample count and reliability weight. Let synthetic evidence mass be `k * reliability`. The relationship between mass and the downstream accuracy delta is **r = -0.9876**. The smallest setting is nearly neutral; the largest setting degrades context accuracy by **7.11 percentage points**. This supports a redundancy-amplification / evidence-reweighting mechanism: synthetic examples generated from the model's own inferred state can over-count correlated evidence even when labels are correct.

### Selective personalization and regret

A probabilistic categorical user posterior supports risk--coverage evaluation. The paper reports personalization only at confidence thresholds rather than treating coverage as free. A separate regret curve falls from **0.869** after one real interaction to **0.199** after twenty.

### Drift baselines

On the noisy induced-shift diagnostic, ROC-AUC is **0.928** for the original heuristic, **0.980** for EWMA, **0.981** for CUSUM, and **0.969** for posterior total-variation shift. The custom heuristic is therefore not treated as a contribution.

### External-model boundary

The package includes PersonaMem/PAHF loaders and an auditable SFT data builder. The environment used to build the reference release had PyTorch but could not retrieve Transformers/PEFT/Datasets or open-weight checkpoints because network package/model access was unavailable. No LLM post-training result is fabricated.

### Dataset-level mass control

The mechanism study suggested that sample-level verification was solving the wrong unit of control. I therefore added a dataset-level mitigation that caps the total reliability mass contributed by synthetic events for one user and discounts repeated `(preference_key, context)` signatures.

Across five independent seeds:

| Evidence | Mean context accuracy | Delta vs. real-only |
|---|---:|---:|
| real-only | **0.6599** | -- |
| raw utility-calibrated synthetic | 0.6274 | -0.0325 |
| mass-capped utility synthetic | 0.6581 | -0.0018 |

The cap recovers **94.47%** of the raw degradation. This is deliberately reported as a mitigation rather than an accuracy improvement: the capped result does not establish a gain over real-only training.

### Response-level evaluation (five seeds)

Latent preference accuracy can be misleading if state estimates do not improve the response a user sees. The response-level suite converts each preference into a natural-language decision with candidate answers and adds factual cases in which personalization is unnecessary. A learned relevance gate decides whether the user state should be consulted.

| Method | Overall response accuracy | Personalized cases | No-personalization cases |
|---|---:|---:|---:|
| generic | 0.417 ± 0.027 | 0.367 ± 0.029 | 1.000 |
| always-personalize state | 0.591 ± 0.009 | 0.642 ± 0.010 | 0.000 |
| Bayesian state + gate | **0.680 ± 0.013** | **0.653 ± 0.015** | **1.000** |
| structured learner + gate | 0.640 ± 0.017 | 0.609 ± 0.019 | 1.000 |
| PyTorch neural response ranker | 0.450 ± 0.022 | 0.402 ± 0.024 | 1.000 |

Values are mean ± sample standard deviation across five independent seeds. The always-personalize baseline makes the restraint failure explicit: its latent state can be useful on personalized tasks while still producing a 100% over-personalization rate on irrelevant factual queries. The neural baseline is a small trainable text ranker, not a pretrained language model; its weak result is kept as a negative control.

### Interpretation after the upgrade

The paper's strongest causal story is now:

1. synthetic labels can be essentially correct and still hurt;
2. the harm grows with the amount of correlated synthetic evidence injected into training;
3. controlling evidence mass removes most of the damage;
4. user-state quality matters at the response level only when paired with restraint.

This is a stronger and narrower claim than "synthetic personalization works." It isolates a failure mechanism, demonstrates a mitigation, and connects the state model to visible response behavior while keeping external-model and human-study conclusions separate.
