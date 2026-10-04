# Experiment Log — The Unfixed User

This journal records the experiments that materially changed the project. It is reconstructed from the frozen scripts and result files in this release; it does **not** invent timestamps, missing runs, or a fake development chronology. Each entry points to raw evidence that is present in the repository.

## Index

| ID | Experiment | Outcome |
|---|---|---|
| EXP-001 | Cold-start: retrieval vs learned personalization | supported-with-boundary |
| EXP-002 | Context-dependent ground truth | supported |
| EXP-003 | Repeated-seed stability | supported |
| EXP-004 | Selector proxy ablation | proxy-supported |
| EXP-005 | Synthetic downstream utility | hypothesis-failed |
| EXP-006 | Oracle vs pseudo-label diagnostic | hypothesis-failed |
| EXP-007 | Synthetic evidence-mass sweep | supported |
| EXP-008 | Mass-capped mitigation | supported-mitigation |
| EXP-009 | Drift detector baseline check | hypothesis-failed |
| EXP-010 | Noise stress test | supported-with-limit |
| EXP-011 | Selective personalization risk–coverage | supported |
| EXP-012 | Response-level restraint benchmark | supported |
| EXP-013 | Personalization regret vs evidence | supported |

## EXP-001 — Cold-start: retrieval vs learned personalization

**Hypothesis.** A learned structured personalization model should beat sparse retrieval when user evidence is scarce.

**Setup.** Controlled synthetic users; interaction counts 0/1/3/5/10/20/50; compare retrieval-weighted voting, learned real-only, and synthetic-augmented learner.

**Result.** At 5 interactions: learned real-only 0.623 accuracy vs retrieval 0.436. At 50 interactions retrieval catches up and slightly exceeds the learned real-only baseline (0.963 vs 0.953).

**Interpretation.** Learning helps most in the sparse-data regime; retrieval becomes competitive once history is dense.

**Next decision.** Focus claims on cold-start/sample-efficiency rather than universal superiority over retrieval.

**Raw evidence.** [`results/benchmark.csv`](../results/benchmark.csv)

**Reproduce.** `python scripts/run_experiment.py EXP-001 --out scratch/exp-001`

## EXP-002 — Context-dependent ground truth

**Hypothesis.** Context should change the correct user preference, not merely be stored as metadata.

**Setup.** Context-aware simulator with context dependence; compare context-aware inference and a trainable context model across interaction counts.

**Result.** At 50 interactions: context-aware inference 0.894 context accuracy and trainable context model 0.891.

**Interpretation.** Context can be evaluated as a real target rather than decorative metadata.

**Next decision.** Use context accuracy, not only global slot accuracy, as a primary controlled metric.

**Raw evidence.** [`results/v2_context_benchmark.csv`](../results/v2_context_benchmark.csv)

**Reproduce.** `python scripts/run_experiment.py EXP-002 --out scratch/exp-002`

## EXP-003 — Repeated-seed stability

**Hypothesis.** The context result should survive independent simulator/training seeds.

**Setup.** Five seeds (7, 13, 29, 41, 73); 140 train / 60 held-out users per seed; 3–50 real interactions.

**Result.** Mean context accuracy rises from 0.512 at 3 interactions to 0.883 at 50; 95% interval at 50: 0.873–0.894.

**Interpretation.** The controlled context result is directionally stable across five independent seeds.

**Next decision.** Keep five-seed limitation explicit; do not treat it as high-powered external evidence.

**Raw evidence.** [`results/v3_seed_stability.csv`](../results/v3_seed_stability.csv), [`results/v3_seed_summary.csv`](../results/v3_seed_summary.csv)

**Reproduce.** `python scripts/run_experiment.py EXP-003 --out scratch/exp-003`

## EXP-004 — Selector proxy ablation

**Hypothesis.** Selection policies that score higher on verified information value should create better training data.

**Setup.** Compare random, uncertainty, diversity, failure-driven, and information-gain-style selection under the same verifier.

**Result.** Failure-driven and information-gain-style selection score ~0.758 verified information value vs random 0.649.

**Interpretation.** The selector successfully changes the proxy distribution, but this says nothing yet about downstream learning utility.

**Next decision.** Run the selected samples through actual downstream training rather than optimizing the proxy in isolation.

**Raw evidence.** [`results/selection_ablation.csv`](../results/selection_ablation.csv)

**Reproduce.** `python scripts/run_experiment.py EXP-004 --out scratch/exp-004`

## EXP-005 — Synthetic downstream utility

**Hypothesis.** More informative synthetic examples should improve downstream personalization.

**Setup.** At 10 real interactions, compare real-only training with random, uncertainty, diversity, failure-driven, information-gain-style, and decision-boundary synthetic selection.

**Result.** Real-only 0.663. Uncertainty 0.663 (effectively tied); failure-driven/information-gain 0.655; decision-boundary 0.631; diversity 0.605; random 0.600.

**Interpretation.** Informativeness is not downstream utility. Several selectors make the trained model worse.

**Next decision.** Diagnose whether the failure comes from bad pseudo-labels or dataset-level effects.

**Raw evidence.** [`results/v3_synthetic_utility.csv`](../results/v3_synthetic_utility.csv), [`results/v3_synthetic_comparisons.json`](../results/v3_synthetic_comparisons.json)

**Reproduce.** `python scripts/run_experiment.py EXP-005 --out scratch/exp-005`

## EXP-006 — Oracle vs pseudo-label diagnostic

**Hypothesis.** Synthetic degradation is primarily caused by incorrect pseudo-labels near difficult decision boundaries.

**Setup.** Compare real-only, pseudo-labeled synthetic, oracle-labeled synthetic, and utility-calibrated selected data on held-out users.

**Result.** Real-only 0.664; pseudo 0.613; oracle 0.609; UCES 0.587. Pseudo-label error was 1/2200 (0.045%); selected UCES label error was 0/2173.

**Interpretation.** Label correctness is necessary but not sufficient; oracle labels do not remove the degradation.

**Next decision.** Test evidence duplication / reweighting directly.

**Raw evidence.** [`results/paper_oracle_vs_pseudo.csv`](../results/paper_oracle_vs_pseudo.csv), [`results/paper_results.json`](../results/paper_results.json)

**Reproduce.** `python scripts/run_experiment.py EXP-006 --out scratch/exp-006`

## EXP-007 — Synthetic evidence-mass sweep

**Hypothesis.** If distributional reweighting is the mechanism, harm should grow with injected synthetic evidence mass.

**Setup.** 25 count × reliability settings; vary synthetic count and reliability while holding the learner/evaluation fixed.

**Result.** Synthetic evidence mass is strongly negatively associated with downstream delta; recorded correlation is approximately -0.988 in the claim contract.

**Interpretation.** The failure tracks how much correlated evidence is injected, not merely whether each label is correct.

**Next decision.** Move intervention from sample scoring to dataset composition.

**Raw evidence.** [`results/paper_synthetic_mass_sweep.csv`](../results/paper_synthetic_mass_sweep.csv), [`results/paper_results.json`](../results/paper_results.json)

**Reproduce.** `python scripts/run_experiment.py EXP-007 --out scratch/exp-007`

## EXP-008 — Mass-capped mitigation

**Hypothesis.** Capping total synthetic evidence mass and duplicate signatures should recover the degradation.

**Setup.** Five independent seeds (701, 733, 761, 797, 823); compare real-only, raw UCES augmentation, and mass-capped UCES.

**Result.** Mean accuracy: real-only 0.660, raw UCES 0.627, mass-capped 0.658. Mass control recovers ~94.5% of the raw augmentation harm. It does not beat real-only.

**Interpretation.** A dataset-level intervention addresses the diagnosed failure, but this is mitigation rather than a new SOTA result.

**Next decision.** Test the same mechanism with different learners and external user distributions.

**Raw evidence.** [`results/paper_mass_control.csv`](../results/paper_mass_control.csv), [`results/paper_mass_control_seeds.csv`](../results/paper_mass_control_seeds.csv)

**Reproduce.** `python scripts/run_experiment.py EXP-008 --out scratch/exp-008`

## EXP-009 — Drift detector baseline check

**Hypothesis.** The project-specific drift heuristic is a strong change detector.

**Setup.** 320 controlled cases; compare heuristic, EWMA, CUSUM, and Bayesian-shift scores by ROC-AUC.

**Result.** Heuristic 0.928 ROC-AUC; EWMA 0.980; CUSUM 0.981; Bayesian shift 0.969.

**Interpretation.** The custom heuristic works but is not competitive with standard detectors in this setting.

**Next decision.** Remove drift detection from the novelty claim; keep standard baselines in the evaluation stack.

**Raw evidence.** [`results/paper_drift_baselines.csv`](../results/paper_drift_baselines.csv)

**Reproduce.** `python scripts/run_experiment.py EXP-009 --out scratch/exp-009`

## EXP-010 — Noise stress test

**Hypothesis.** Personalization quality should degrade gracefully as evidence corruption rises.

**Setup.** Controlled observation noise from 0% to 32%; measure global inference accuracy with bootstrap intervals.

**Result.** Accuracy falls from 0.953 at 0% noise to 0.751 at 32% noise.

**Interpretation.** The model degrades monotonically rather than catastrophically, but robustness at high corruption remains insufficient.

**Next decision.** Keep uncertainty/restraint in the behavior policy and treat robust inference as open work.

**Raw evidence.** [`results/v3_noise_stress.csv`](../results/v3_noise_stress.csv)

**Reproduce.** `python scripts/run_experiment.py EXP-010 --out scratch/exp-010`

## EXP-011 — Selective personalization risk–coverage

**Hypothesis.** Confidence should support a useful abstention/restraint policy.

**Setup.** 250 controlled users; sweep confidence thresholds and report coverage vs selective risk.

**Result.** At threshold 0.65, coverage is 0.815 and selective accuracy 0.798, compared with 0.768 accuracy at near-full coverage (threshold 0.35).

**Interpretation.** Confidence contains useful information for selective personalization, though the curve is not monotonic at the highest thresholds.

**Next decision.** Use restraint as a behavior policy rather than forcing personalization everywhere.

**Raw evidence.** [`results/paper_risk_coverage.csv`](../results/paper_risk_coverage.csv)

**Reproduce.** `python scripts/run_experiment.py EXP-011 --out scratch/exp-011`

## EXP-012 — Response-level restraint benchmark

**Hypothesis.** Better state inference should improve actual response selection, and always-personalize should fail on irrelevant queries.

**Setup.** Five seeds; natural-language response-choice cases; compare generic, always-personalize, last-event, inferred-state, Bayesian-state, structured learner, and a scratch neural ranker.

**Result.** Bayesian state + restraint: 0.680 ± 0.013 overall. Always-personalize: 0.591 ± 0.009 and 100% over-personalization on no-personalize cases. Neural ranker: 0.450 ± 0.022.

**Interpretation.** Behavioral restraint matters; a more flexible neural scorer is not automatically stronger in this small controlled regime.

**Next decision.** Move response-level evaluation to real model generations and blinded human judgments.

**Raw evidence.** [`results/paper_response_level_repeated.csv`](../results/paper_response_level_repeated.csv), [`results/paper_response_level_seeds.csv`](../results/paper_response_level_seeds.csv), [`results/paper_response_cases.csv`](../results/paper_response_cases.csv)

**Reproduce.** `python scripts/run_experiment.py EXP-012 --out scratch/exp-012`

## EXP-013 — Personalization regret vs evidence

**Hypothesis.** Regret should decrease as the system accumulates real interactions.

**Setup.** 180 controlled users; measure regret after 1/3/5/10/20 interactions.

**Result.** Mean regret drops from 0.869 at 1 interaction to 0.199 at 20.

**Interpretation.** The moving-state estimator becomes materially more useful with evidence, but the early-interaction regime remains the hardest.

**Next decision.** Prioritize evaluation and methods for the first 5–10 interactions where uncertainty and correction burden are highest.

**Raw evidence.** [`results/paper_regret.csv`](../results/paper_regret.csv)

**Reproduce.** `python scripts/run_experiment.py EXP-013 --out scratch/exp-013`
