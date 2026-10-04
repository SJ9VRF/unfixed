# Failure Taxonomy

| Failure | Description | Detection signal | Mitigation path |
|---|---|---|---|
| Stale preference | Old state survives a real change | drift score + post-change errors | recency weighting / change-point model |
| Context collapse | Local preference generalized everywhere | context accuracy gap | context-specific state |
| Over-personalization | Irrelevant preference injected | gate false positive | relevance gate / threshold calibration |
| Under-personalization | Relevant evidence ignored | gate false negative | richer semantic features / FM gate |
| False certainty | Wrong value with high confidence | high-confidence error | calibration / confidence cap |
| Synthetic self-reinforcement | Generated data amplifies current mistake | accuracy/calibration regression | verifier + boundary targeting + utility test |
| Cross-key confusion | Correct personalization dimension, wrong key | cross-key negative errors | key-aware relevance model |
| Sparse instability | A few noisy events flip state | non-monotonic cold-start curve | conservative uncertainty / abstention |
| Drift overshoot | Recent noise mistaken for a real change | false drift alarms | Bayesian/gradual change model |
| Grader mismatch | Automatic score diverges from human judgment | agreement/calibration audit | human calibration set |
