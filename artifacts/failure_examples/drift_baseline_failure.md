# Failure example: custom drift detector loses to standard baselines

The project heuristic reaches ROC-AUC 0.928, but EWMA and CUSUM reach ~0.980–0.981. This result is preserved specifically because it changed the contribution story: drift detection was removed from the novelty claim instead of being tuned or hidden.
