# Artifact evaluation guide

## Claims that can be reproduced offline
1. Cold-start personalization improves with additional observations.
2. Context-aware inference tracks context-conditioned preferences.
3. Preference drift is measurable and recoverable under the synthetic benchmark.
4. Synthetic selection heuristics differ in downstream utility; informativeness alone does not guarantee training benefit.
5. Anti-personalization gating can be evaluated independently of response generation.

## Minimal reproduction
```bash
pip install -e '.[dev]'
pytest -q
python scripts/run_all.py
python scripts/quality_gate.py
```

## Expected artifacts
- `results/benchmark.csv`
- `results/v3_seed_summary.csv`
- `results/v3_synthetic_utility.csv`
- `results/robustness.json`
- `results/quality_gate.json`
- `dashboard/index.html`
- `human_eval/study_items.csv`

## Non-claims
The release does not claim completed real-user longitudinal studies, production privacy compliance, or superiority on a proprietary frontier model. Those require external participants, governance, or credentials that are intentionally absent from this self-contained artifact.

## Machine-verifiable claim contract
`claims/reference_claims.json` freezes a small set of headline metrics with a narrow tolerance. `python scripts/verify_claims.py` recomputes those values from generated result files and fails if the release silently diverges. This is a regression contract, not a substitute for statistical interpretation.
