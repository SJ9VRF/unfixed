# Failure example: informative selection, worse downstream model

The selector-proxy ablation assigns higher verified information value to failure/information-style selection (~0.758) than random (~0.649). Yet the downstream training table shows no corresponding gain, and decision-boundary selection reaches only 0.631 context accuracy versus 0.663 real-only.

This is the aggregate failure that triggered the oracle diagnostic and evidence-mass investigation. See `docs/failure-trace.md` for the complete trace.
