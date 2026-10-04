# The Unfixed User Benchmark v0.1

## Evaluation axes
- Cold start: 0, 1, 3, 5, 10, 20, 50 interactions
- Preference drift
- Conflicting evidence
- Explicit vs implicit signals
- Context-dependent preferences
- Anti-personalization controls
- Long-horizon stability

## Core metrics
- personalization accuracy
- interactions-to-target
- calibration error
- incorrect personalization rate
- stale preference rate
- over-personalization rate
- adaptation speed after drift
- unseen-context generalization

## Required baseline families
1. no personalization
2. prompt-only
3. retrieval-only
4. memory-only
5. real-data SFT
6. real + synthetic SFT
7. counterfactual augmentation
8. preference optimization
9. personalized reward model
10. full The Unfixed User pipeline
