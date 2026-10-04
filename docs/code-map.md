# Code Map — The Unfixed User

The implementation is split by research responsibility rather than by UI surface.

- `user_model/` — structured user state, contextual values, uncertainty and drift fields.
- `interaction_engine/` — event schema and controlled interaction simulation.
- `inference/` — recency-aware, context-aware preference inference and change detection.
- `personalization/` — semantic relevance gate used to withhold irrelevant personalization.
- `synthetic_experience/` — counterfactual generation, verification, and selection policies.
- `training/` — trainable preference baseline and training-row construction.
- `evals/` — cold-start, context, drift, conflict, anti-personalization, long-horizon, noise and statistical evaluation.
- `backends/` — local reference backend plus provider-neutral/OpenAI-compatible adapter.
- `api/` — FastAPI research service.
- `demo/` — local interactive demo.
- `human_eval/` — randomized blind study generation and analysis.
- `privacy/`, `red_team/`, `validation/` — privacy, regression safety and schema/integrity checks.
- `scripts/` — reproducible benchmark, figure, claim and manifest tooling.
- `tests/` — regression and scientific-contract tests.

## Reproduce

```bash
pip install -e '.[dev]'
pytest -q
python scripts/run_all.py
```
