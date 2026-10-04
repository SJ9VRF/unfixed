# Architecture — The Unfixed User

```text
User interaction
      │
      ▼
InteractionEvent
(explicit / implicit / correction, reliability, context, time)
      │
      ▼
PreferenceInferenceEngine
 ├─ recency weighting
 ├─ competing-evidence confidence
 ├─ context-specific estimates
 └─ drift score
      │
      ▼
Structured UserState
 ├─ global preference
 ├─ contextual values
 ├─ confidence / provenance
 ├─ stability
 └─ uncertainty / drift
      │
      ├────────► PersonalizationGate ───────► withhold when irrelevant
      │
      ├────────► CounterfactualGenerator
      │               └─ decision-boundary score
      │                        ▼
      │                ExperienceVerifier
      │                        ▼
      │                 SelectionPolicy
      │
      └────────► AgentBackend
                   ├─ fully offline reference backend
                   └─ provider-agnostic FM adapter
                            │
                            ▼
                       agent response
                            │
                            ▼
                      evaluation loop
                            │
                  failure-driven iteration
```

## Design invariants

1. A preference is not considered universally relevant merely because it is stored.
2. Context-specific evidence can override a global preference only for that context.
3. Corrections and recent evidence should be able to overturn stale history.
4. Synthetic examples must be verified before they are eligible for selection.
5. Offline experiments must remain runnable without a hosted model API.
6. Foundation-model integration must not change the benchmark contract.
