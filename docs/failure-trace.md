# Failure Trace — Synthetic Evidence Amplification

A concrete trace of the research loop behind the main finding.

```text
Generate targeted synthetic user evidence
        ↓
Selector proxy improves
  random information value: ~0.649
  failure/info-style: ~0.758
        ↓
Train downstream personalization model
        ↓
Unexpected regression
  real-only @10:       0.663
  decision-boundary:   0.631
  diversity:           0.605
  random:              0.600
        ↓
Hypothesis: labels near the boundary are wrong
        ↓
Oracle-label diagnostic
  pseudo error: 1 / 2200
  oracle accuracy: 0.609 < real-only 0.664
        ↓
Hypothesis rejected
        ↓
Sweep synthetic count × reliability (25 settings)
        ↓
Harm tracks total synthetic evidence mass
  correlation ≈ -0.988
        ↓
Intervention moves from sample scoring → dataset composition
        ↓
Cap total synthetic evidence mass + duplicate signatures
        ↓
Five-seed result
  raw augmentation:  0.627
  mass-capped:       0.658
  real-only:         0.660
        ↓
~94.5% of raw harm recovered
        ↓
New boundary discovered
Mass capping mitigates harm but does not establish a gain over real-only.
```

This trace is deliberately not a perfect-success story. The final intervention solves most of the diagnosed regression, but the release does **not** claim an external or SOTA improvement.
