# Related Work Map

This map exists to keep novelty claims narrow. The project is **not** positioned as the first continual-personalization or preference-drift system.

## Continual and online personalization

- **PAHF (2026)** — explicit memory, clarification, post-action feedback, cold start, and preference shifts.
- **SPRInG (2026)** — drift-driven selective parametric adaptation with retrieval-interpolated generation.
- **HypReflect (2026)** — explicit uncertainty-aware preference hypotheses and hypotheses-guided self-distillation.
- **HyperTrace (2026)** — SMC-style online tracing of short- and long-term preference hypotheses; PRISM and PersonaMem-v2 evaluation.
- **CORE / PERSIST (2026)** — selective persona-state revision under ambiguity, conflict, and drift.
- **COPE (2026)** — continual optimization under sparse feedback with personalized embeddings and self-evaluation.
- **PersonaMem / PersonaMem-v2** — dynamic user profiling, implicit personas, and personalized generation.

## Synthetic and counterfactual preference learning

- **PrefPalette (2025)** — counterfactual attribute synthesis for personalized preference modeling.
- **DRIFT (ICLR 2026)** — iterative preference training from real-world dissatisfaction signals; useful contrast because its supervision is naturally occurring rather than system-generated.
- Classical pseudo-labeling/self-training literature documents confirmation bias, but does not by itself explain the oracle-label degradation isolated here.

## Trust, memory, and restraint

- **Beyond Similarity (2026)** — cross-domain memory leakage, over-personalization, sycophancy, and memory-induced failures.
- **LaMP** — benchmark family for personalized language-model tasks and retrieval/fine-tuning baselines.
- MemoryBank, MemGPT, Mem0, and A-MEM study long-term storage, retrieval, and organization.

## Position of this project

**The Unfixed User** is best understood as a mechanism paper about **synthetic personalization data**:

`continual personalization × correct synthetic evidence × evidence reweighting × downstream utility × restraint`

The central distinction is:

`informativeness ≠ correctness ≠ downstream training utility`

The system components around the mechanism study (moving user state, drift handling, relevance gating, eval harness) provide a controlled environment for testing that distinction; they are not individually claimed as unprecedented.

## Source links

- PAHF — https://ai.meta.com/research/publications/learning-personalized-agents-from-human-feedback/
- SPRInG — https://arxiv.org/abs/2601.09974
- HypReflect — https://arxiv.org/abs/2609.00251
- HyperTrace — https://arxiv.org/abs/2609.09835
- CORE — https://arxiv.org/abs/2609.12373
- COPE — https://arxiv.org/abs/2609.26853
- PersonaMem — https://arxiv.org/abs/2504.14225
- PrefPalette — https://arxiv.org/abs/2507.13541
- Beyond Similarity — https://arxiv.org/abs/2606.06054


### Synthetic-user validity

**When Synthetic Users Fail** (Chen, Zhu, Zheng; arXiv:2607.26348) evaluates whether LLM-simulated survey respondents can stand in for real humans and finds systematic individual-level and demographic distortions. It is an important adjacent result, but it targets simulator fidelity. The Unfixed User instead holds a controlled user simulator fixed and asks what happens when generated user-specific evidence is *fed back into training*; its oracle-label experiment is designed specifically to separate data-distribution effects from label correctness.
