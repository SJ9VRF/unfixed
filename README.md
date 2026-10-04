# The Unfixed User

**When correct synthetic evidence still makes personalization worse**  
**Aura Yavary**

Personal assistants should learn from people without freezing them into stale profiles. This project asks a narrower question with a surprising answer: **when a personalization system manufactures more evidence about a user, can adding that evidence make the learned user model worse even when the labels are correct?**

In the controlled experiments here, the answer is yes. The failure tracks the aggregate mass of correlated synthetic evidence, not label error alone. The system around that study maintains a context-conditioned user state and a separate relevance gate so personalization can be withheld when it is not warranted.

[Project page](portfolio/index.html) · [Paper](paper/the_unfixed_user.pdf) · [Demo](demo/index.html) · [Benchmark](dashboard/index.html) · [Technical report](paper/technical_report.md)


## Research paper

The paper-facing contribution is narrower than the full project:

> **The Unfixed User: When Synthetic Experience Hurts Continual Personalization**

The central finding is the **Synthetic Experience Utility Gap**. In a targeted diagnostic, selected pseudo labels are wrong only 0.045% of the time and a utility-calibrated selector observes zero wrong selected labels, yet synthetic augmentation still underperforms real-only training. Oracle labels do not remove the degradation. A 25-setting sweep shows that synthetic evidence mass is strongly associated with the performance drop (r = -0.988), implicating redundancy amplification / evidence reweighting rather than label noise alone. A five-seed mass-capped mitigation recovers 94.5% of the raw augmentation harm, while remaining statistically indistinguishable from the real-only reference.

Paper: [`paper/the_unfixed_user.pdf`](paper/the_unfixed_user.pdf)  
Source: [`paper/the_unfixed_user.tex`](paper/the_unfixed_user.tex)  
Submission readiness notes: [`paper/submission_readiness.md`](paper/submission_readiness.md)  
Paper experiments: `make paper`

## What this work asks

Can a personal agent:

- learn useful preferences from very few interactions;
- distinguish stable preferences from context-specific or temporary ones;
- recover when the user changes their mind;
- avoid personalizing when the stored information is irrelevant; and
- use synthetic or counterfactual experience only when it actually improves held-out behavior?

The last question produced the most interesting result in the project: **synthetic examples that look informative are not necessarily useful training data**. In the targeted mechanism study, the degradation persists with nearly perfect pseudo labels and even with oracle labels; a 25-setting sweep instead points to correlated evidence mass and distributional reweighting as the dominant failure mechanism in this controlled setting.

## Method

The reference system has four parts:

1. **Evidence model** — explicit statements, implicit choices, and corrections are stored with source and reliability.
2. **Moving user state** — preferences are inferred with confidence, context-specific overrides, recency weighting, conflict tracking, and drift detection.
3. **Restraint gate** — personalization is applied only when the inferred state is relevant to the current request.
4. **Counterfactual learning loop** — candidate experiences are generated, verified, selected, and tested by downstream utility rather than proxy scores alone.

The implementation is offline-first so the benchmark can be reproduced without a hosted model API. A provider-neutral adapter is included for foundation-model experiments.

## Results

### Learning from sparse interaction

Five independent benchmark seeds, 60 held-out users per seed:

| Real interactions | Mean context accuracy | 95% bootstrap CI |
|---:|---:|---:|
| 3 | 0.512 | [0.501, 0.524] |
| 5 | 0.578 | [0.565, 0.587] |
| 10 | 0.699 | [0.694, 0.704] |
| 20 | 0.803 | [0.796, 0.810] |
| 50 | **0.883** | **[0.873, 0.894]** |

### Synthetic experience is not automatically helpful

At 10 real interactions:

| Training data | Held-out context accuracy |
|---|---:|
| real only | **0.663** |
| uncertainty-selected synthetic | **0.663** |
| failure-driven synthetic | 0.655 |
| information-gain synthetic | 0.655 |
| decision-boundary synthetic | 0.631 |
| diversity synthetic | 0.605 |
| random synthetic | 0.600 |

The practical takeaway is simple: **selection informativeness and training utility are different quantities**. Sample-level correctness is not enough either; synthetic evidence must be controlled at the dataset level so correlated examples do not distort the learner's effective evidence distribution.

### Dataset-level mitigation

Across five independent seeds:

| Training evidence | Mean context accuracy | Delta vs. real-only |
|---|---:|---:|
| real only | **0.660** | -- |
| raw utility-calibrated synthetic | 0.627 | -0.032 |
| mass-capped utility synthetic | 0.658 | -0.002 |

The mass cap recovers **94.5% of the raw augmentation degradation**. It improves on raw augmentation in all five repeated seeds, but five paired seeds are still underpowered for a strong two-sided significance claim (exact sign test: p=0.0625). It is therefore reported as a consistent mitigation, not a claimed gain over real-only training.

### Response-level personalization

A natural-language candidate-response benchmark tests whether user-state quality transfers to user-facing choices and whether the system can refrain from irrelevant personalization. Across five independent seeds, the Bayesian state method reaches **0.680 ± 0.013 overall response-choice accuracy**, versus **0.591 ± 0.009** for an always-personalize policy that over-personalizes every irrelevant factual query. A small PyTorch response ranker trained from scratch reaches **0.450 ± 0.022** and is retained as a negative baseline rather than hidden.

### Drift and robustness

- preference-reversal recovery within 10 interactions: **68.75%**
- median recovery time after induced reversal: **10 interactions**
- semantic anti-personalization gate: **87.5%** held-out accuracy on the controlled gate set
- global preference inference under 32% observation noise: **0.751** accuracy
- explicit-correction conflict benchmark: **100%** on the controlled cases

Full results and confidence intervals are in the [evaluation dashboard](dashboard/index.html) and `results/`.

## Benchmark integrity

The controlled benchmark uses simulator ground truth to create **training labels for synthetic training users** and evaluation targets for separate held-out users. The evaluated inference and preference models do not read simulator-only `ground_truth` metadata at test time. A regression test deliberately corrupts that metadata and verifies that predictions are unchanged. Oracle labels appear only in the named oracle diagnostic. See [`docs/benchmark-integrity.md`](docs/benchmark-integrity.md).

The remaining limitation is important: train and test users share a closed preference ontology and task families. That makes the benchmark useful for mechanism isolation, but it is not evidence of real-user or external-benchmark SOTA.

## Evaluation and regression infrastructure

Beyond the paper benchmark, the release includes a task/trial/grader/trajectory eval harness and a model-change gate. The smoke suite preserves trajectories for debugging, verifies outcomes and final state independently, and keeps restraint as a first-class behavior. Candidate model or data changes can be blocked if they regress response accuracy, over-personalization, mass-controlled synthetic behavior, or harness invariants. See [`docs/eval-harness.md`](docs/eval-harness.md), [`docs/research-decisions.md`](docs/research-decisions.md), and [`docs/evidence-map.md`](docs/evidence-map.md).

## Run it

For the canonical research and release verification paths, see [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

```bash
pip install -e '.[dev,paper]'
pytest -q
python scripts/run_all.py
```

Start the API and browser demo:

```bash
uvicorn api.app:app --reload
```

Then open `http://127.0.0.1:8000/demo`.

## Repository map

```text
the-unfixed-user/
├── api/                     FastAPI service
├── backends/                local and foundation-model adapters
├── dashboard/               generated evaluation dashboard
├── demo/                    browser and CLI demos
├── docs/                    architecture, benchmark, privacy, failure analysis
├── evals/                   cold-start, drift, conflict, response-level, long-horizon
├── human_eval/              blind study generator and analysis
├── inference/               context-, recency-, and drift-aware inference
├── interaction_engine/      interaction event schema and simulator
├── personalization/         relevance / anti-personalization gate
├── paper/                   manuscript and technical report
├── privacy/                 redaction utilities
├── red_team/                regression cases for unsafe state use
├── synthetic_experience/    generation, verification, and selection
├── training/                structured + PyTorch response baselines
├── user_model/              structured user-state schema
├── user_simulator/          controlled profiles, contexts, and drift
└── tests/                   unit, regression, and project-page tests
```

## Research artifacts

- [Project homepage](portfolio/index.html)
- [Paper](paper/the_unfixed_user.pdf)
- [Technical report](paper/technical_report.md)
- [Evaluation dashboard](dashboard/index.html)
- [Interactive demo](demo/index.html)
- [Benchmark integrity](docs/benchmark-integrity.md)
- [Evidence map](docs/evidence-map.md)
- [Statistical audit](docs/statistical-audit.md)
- [Threats to validity](docs/threats-to-validity.md)
- [Research decisions](docs/research-decisions.md)
- [Full documentation index](docs/INDEX.md)

## Scope

The benchmark uses controlled synthetic users to isolate mechanisms and make ablations reproducible. It does not establish real-world user satisfaction, demographic fairness, clinical safety, or external-benchmark state of the art. Those questions require separate human and external-model evaluation.

For consequential actions, inferred preferences are evidence—not authorization. Spending money, sending messages, exposing private data, or changing accounts should require an explicit confirmation policy above the personalization layer.

## Citation

```bibtex
@misc{yavary_unfixed_user,
  author = {Aura Yavary},
  title = {The Unfixed User: When Synthetic Experience Hurts Continual Personalization},
  note = {Research artifact}
}
```

## Evidence Layer

The result page is intentionally clean; the research process is not hidden. The repository includes **13 documented experiments, 5 failed hypotheses, 6 major design decisions, and 4 primary failure modes**, each linked to frozen CSV/JSON evidence.

[Experiment journal](docs/experiment-log.md) · [What didn’t work](docs/failed-experiments.md) · [Decision log](docs/decision-log.md) · [Real eval tables](docs/eval-tables.md) · [Unexpected findings](docs/unexpected-findings.md) · [Raw evidence](artifacts/README.md)

Git history is not backfilled: the source archive did not preserve earlier incremental commits, so [`docs/git-provenance.md`](docs/git-provenance.md) states that limitation rather than manufacturing a believable-looking history.



Evidence provenance: [`docs/evidence-registry.md`](docs/evidence-registry.md).
