# Threats to validity

This project is strongest as a controlled mechanistic study. The following are the main ways its current conclusions could fail to generalize.

## Simulator dependence

The benchmark controls latent preferences, context, drift, and supervision. That control makes causal diagnostics possible, but it also means the data-generating process is narrower than real human behavior. A result that survives this benchmark may still disappear under natural language ambiguity, long-horizon interaction, or real-user inconsistency.

**Falsifier:** matched evaluation on independent public personalization benchmarks and real longitudinal users fails to reproduce the synthetic-experience utility gap.

## Supervision realism

Training users use simulator ground truth as labels. Test users are disjoint and hidden metadata is not available to inference, but the supervision source is cleaner than real preference feedback.

**Falsifier:** replacing simulator labels with realistic noisy/implicit supervision reverses the mechanism or mitigation result.

## Model-class dependence

Most mechanism experiments use deliberately small, inspectable learners. The response-level neural baseline checks one additional model class, but the study does not establish that the same effect size holds after large-language-model post-training.

**Falsifier:** matched SFT/preference-optimization runs on multiple open-weight LLM families show no degradation as synthetic evidence mass increases.

## Seed-level power

Repeated headline comparisons use five independent seeds. Directional consistency is informative, but exact two-sided sign tests remain underpowered; a 5/5 result has p=0.0625.

**Falsifier:** broader replication changes the direction or substantially shrinks the paired effects.

## Benchmark-policy coupling

The synthetic generator, selector, and learner share a controlled ontology. The oracle-label experiment rules out one simple label-noise explanation, but shared structure could still amplify the observed mass/reweighting effect.

**Falsifier:** independently implemented generators or out-of-ontology tasks eliminate the relationship between synthetic evidence mass and downstream degradation.

## Human-facing utility

Response-level evaluation converts inferred user state into controlled response choices. It is more behavioral than slot accuracy but still not a substitute for blinded longitudinal human evaluation.

**Falsifier:** human raters do not prefer the selective-personalization policy or find it more intrusive despite benchmark gains.

## What would change the paper most

The highest-value next evidence is not another internal ablation. It is a three-way replication: an external public benchmark, an open-weight LLM post-training run, and a longitudinal blinded human evaluation. Those experiments would test transfer across data source, model class, and evaluator simultaneously.
