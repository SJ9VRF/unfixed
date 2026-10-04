# Model Card — The Unfixed User Reference Models

## Components
- recency/context-aware evidence inference engine;
- low-capacity multinomial logistic context model;
- small trainable semantic relevance gate;
- offline reference response backend;
- provider-agnostic completion adapter for future foundation-model integration.

## Strengths
Fully offline, deterministic under fixed seeds, interpretable, inexpensive and suitable for ablations. Context and drift are first-class concepts rather than metadata-only labels.

## Known weaknesses
The learned context model is weak in the extreme cold-start regime. The relevance gate has only a small controlled training/evaluation set. Synthetic augmentation does not consistently improve accuracy. No real-user external-validity claim is made.

## Safety/trust behavior
The backend withholds preferences when relevance is rejected and only supplies the selected preference/value/confidence to a foundation-model adapter. This reduces accidental preference leakage but is not a complete privacy or safety system.
