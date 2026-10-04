# Novelty Audit — The Unfixed User

**Author:** Aura Yavary  
**Status:** public-literature/name audit; not a patent or trademark opinion.

## Bottom line

The broad premise — continually personalizing an LLM or agent as a user's preferences change — is **not novel by itself**. Recent work now covers online preference tracing, preference drift, continual personalization, selective adaptation, explicit memory, clarification, and uncertainty-aware user models.

The strongest defensible contribution in **The Unfixed User** is narrower and more interesting:

> **Synthetic personalization evidence can reduce downstream personalization quality even when its labels are almost perfectly correct or oracle-correct, because adding correlated synthetic evidence changes the effective evidence distribution.**

The project therefore studies a failure mode of synthetic experience, not merely another memory system. It separates three quantities that are often conflated: **sample informativeness, sample correctness, and downstream training utility**.

## Closest contemporary work

| Work | What it already establishes | What remains distinct here |
|---|---|---|
| **PAHF — Learning Personalized Agents from Human Feedback** (2026) | Continual personalization with explicit memory, clarification, post-action feedback, cold start, and preference shifts | Do not claim continual adaptation or clarification as new. This project instead isolates the downstream effect of system-generated personalization evidence. |
| **SPRInG** (2026) | Continual LLM personalization with drift-driven selective adaptation plus retrieval-interpolated generation | Do not claim selective updating under drift as new. Our target is synthetic-data utility and evidence reweighting. |
| **HypReflect** (2026) | Uncertainty-aware preference hypotheses refined from heterogeneous user signals, followed by self-distillation | Do not claim revisable preference hypotheses or uncertainty alone. Our distinguishing experiment asks when synthetic/self-generated evidence harms learning despite correctness. |
| **HyperTrace** (2026) | Online latent preference tracing with weighted natural-language hypotheses and SMC-style belief updates; evaluated on PRISM and PersonaMem-v2 | Do not claim latent-state tracing itself. Our contribution is a data-mechanism result about augmentation utility. |
| **CORE / PERSIST** (2026) | Separates turn-local evidence from persistent persona revision and explicitly studies persona drift, ambiguity, conflict, and selective updates | Do not claim controlled persona revision or drift robustness as new. |
| **COPE** (2026) | Continual optimization under sparse feedback using personalized embeddings and self-evaluation proxy rewards | Do not claim continual model updating from sparse feedback as new. |
| **PersonaMem / PersonaMem-v2** | Dynamic user profiling, implicit personas, long histories, and personalized response evaluation | Do not claim dynamic profiling itself. |
| **PrefPalette** (2025) | Counterfactual preference synthesis for personalized modeling | Do not claim counterfactual synthesis itself. We ask whether such generated evidence actually improves downstream personalization. |
| **When Synthetic Users Fail** (2026) | Shows that LLM-simulated survey respondents can systematically diverge from real people across domains and models | Adjacent but distinct: that work tests synthetic-user fidelity as a substitute for humans; this project studies the downstream training effect of adding user-specific synthetic evidence, including an oracle-label condition. |
| **Beyond Similarity** (2026) | Memory leakage, over-personalization, sycophancy, and trustworthy retrieval | Do not claim over-personalization discovery; restraint is an evaluation dimension here. |
| **DRIFT** (ICLR 2026) | Iterative preference training from abundant real dissatisfaction signals | Useful contrast: our negative result concerns generated user-specific evidence, not naturally occurring real feedback. |

## Novelty that is still defensible

### 1. Synthetic Experience Utility Gap
The project measures the divergence between a sample-level selection score and the actual downstream change in held-out personalization after augmentation. Informative-looking synthetic examples can hurt.

### 2. Correct-label failure
The degradation persists when pseudo-label error is extremely small and when labels are replaced by simulator oracle truth. This rules out label noise as a sufficient explanation in the controlled setting.

### 3. Evidence-mass mechanism
A controlled sweep varies the number and weight of synthetic examples. Synthetic evidence mass strongly tracks downstream degradation, supporting a redundancy/reweighting explanation rather than a simple bad-label explanation.

### 4. Dataset-level mitigation
A mass-capped selector recovers most of the harm from raw augmentation across repeated seeds. The project deliberately reports this as mitigation, not as an improvement over real-only learning.

### 5. Selective personalization as a coupled outcome
The same system measures response quality and the cost of personalizing when no personalization is warranted, connecting latent user-state learning to user-facing behavior.

## What is *not* claimed

- first system for changing preferences;
- first continual personalization method;
- first uncertainty-aware user model;
- first counterfactual personalization system;
- first anti-over-personalization system;
- state of the art on PersonaMem, PRISM, PAHF, or another public benchmark;
- human-user benefit from synthetic-user experiments.

## SOTA status

**No external SOTA claim is currently defensible.** The strongest numbers in this release come from a controlled simulator designed for mechanism isolation. The project can be *SOTA-relevant* because it studies a failure mode that contemporary continual-personalization papers do not make their central target, but a performance SOTA claim requires matched runs on recognized public benchmarks and contemporary baselines.

A defensible SOTA submission would require, at minimum:

1. matched evaluation on PersonaMem-v2 and/or another public dynamic-personalization benchmark;
2. same-backend comparisons with HyperTrace, CORE-style revision, SPRInG/HypReflect/COPE-style continual baselines where feasible;
3. frozen model IDs, prompts, dataset versions, random seeds, and raw outputs;
4. repeated trials or paired bootstrap tests;
5. a real-user study kept separate from simulator claims.

## Name audit

The exact phrase **“The Unfixed User”** was searched as an AI/personalization project and paper title. The search did not surface a same-topic AI paper/project using that exact title. This is a practical collision check, **not** trademark clearance or a guarantee of global uniqueness.

Rejected names included candidates with direct product/project collisions (for example, PersonaFlux and EverSelf).

## Public sources checked

- PAHF — https://ai.meta.com/research/publications/learning-personalized-agents-from-human-feedback/
- SPRInG — https://arxiv.org/abs/2601.09974
- HypReflect — https://arxiv.org/abs/2609.00251
- HyperTrace — https://arxiv.org/abs/2609.09835
- CORE — https://arxiv.org/abs/2609.12373
- COPE — https://arxiv.org/abs/2609.26853
- PersonaMem — https://arxiv.org/abs/2504.14225
- PrefPalette — https://arxiv.org/abs/2507.13541
- When Synthetic Users Fail — https://arxiv.org/abs/2607.26348
- Beyond Similarity — https://arxiv.org/abs/2606.06054
- DRIFT — ICLR 2026 proceedings

## Claim language to use publicly

> We study a failure mode of continual personalization in which synthetic user evidence can be individually correct and informative yet still reduce downstream personalization quality by distorting the effective evidence distribution.

> The result separates correctness, informativeness, and training utility, and motivates dataset-level controls on synthetic experience rather than sample-level filtering alone.
