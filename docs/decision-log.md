# Decision Log

The decisions below are the ones that materially changed the research path. Format: **Decision → Alternatives → Evidence → Trade-off → Outcome.**

## D-001 — Measure downstream utility, not selector informativeness

**Decision →** judge synthetic experience by the held-out model it produces.

**Alternatives →** optimize information value, diversity, uncertainty, or decision-boundary proximity directly.

**Evidence →** selector proxy scores improved while several downstream-trained models got worse (`selection_ablation.csv`, `v3_synthetic_utility.csv`).

**Trade-off →** downstream evaluation is slower and noisier than a cheap proxy, but it measures the quantity that matters.

**Outcome →** the paper’s central failure is framed as an **informativeness–utility gap**.

## D-002 — Do not blame pseudo-label noise without an oracle check

**Decision →** run an oracle-label diagnostic before designing a more elaborate verifier.

**Alternatives →** immediately increase verifier complexity or filter more aggressively.

**Evidence →** oracle augmentation still underperformed real-only, while observed pseudo-label error was negligible.

**Trade-off →** the oracle diagnostic is simulator-specific, but it cleanly falsifies the simplest explanation in the controlled setting.

**Outcome →** the project shifted to dataset-level evidence reweighting.

## D-003 — Control synthetic evidence mass at the dataset level

**Decision →** cap total synthetic mass and repeated preference-context signatures.

**Alternatives →** score every sample more aggressively; train on all generated examples; add another selector heuristic.

**Evidence →** harm tracked synthetic evidence mass (~−0.988 correlation in the controlled sweep) and mass capping recovered ~94.5% of raw augmentation harm across five seeds.

**Trade-off →** capping can discard individually useful examples; it also does not establish improvement over real-only training.

**Outcome →** mitigation is reported as harm recovery, not SOTA improvement.

## D-004 — Add restraint instead of personalizing every query

**Decision →** separate “what do I know about the user?” from “should this query use it?”.

**Alternatives →** always condition the response on the inferred profile; rely on the response model to ignore irrelevant state.

**Evidence →** always-personalize achieved 0% accuracy on no-personalize cases and a 100% over-personalization rate; Bayesian state + restraint reached 0.680 ± 0.013 overall across five seeds.

**Trade-off →** restraint can miss useful personalization when relevance is uncertain.

**Outcome →** selective personalization is part of the behavior policy and risk–coverage analysis.

## D-005 — Keep standard drift baselines even when they beat the custom method

**Decision →** retain EWMA/CUSUM/Bayesian-shift results and remove custom drift detection from the contribution list.

**Alternatives →** tune the heuristic until it wins or report only the custom detector.

**Evidence →** CUSUM/EWMA materially outperform the heuristic on controlled ROC-AUC.

**Trade-off →** the project loses one potential “novel” component but gains a more honest attribution of what is actually new.

**Outcome →** drift detection is infrastructure; synthetic-data failure mechanism remains the paper’s contribution.

## D-006 — Keep external validation outside the headline until it is run

**Decision →** ship adapters/protocols for PersonaMem/PAHF/open-weight post-training, but do not populate result tables with unexecuted numbers.

**Alternatives →** treat controlled simulator results as SOTA or use model-judge placeholders as if they were external evidence.

**Evidence →** the present release has reproducible controlled results but no completed matched external benchmark or real-user study.

**Trade-off →** the headline is narrower.

**Outcome →** the release is a mechanism/evaluation study with explicit external-validity gates.
