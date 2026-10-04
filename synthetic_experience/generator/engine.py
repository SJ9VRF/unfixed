from __future__ import annotations
from dataclasses import dataclass, field
import random, uuid
from user_model.schema import UserState
from user_simulator.profiles.generator import PREFERENCE_SPACE

@dataclass
class SyntheticExperience:
    experience_id: str
    preference_key: str
    assumed_value: str
    context: str
    prompt: str
    counterfactual: bool
    difficulty: float
    metadata: dict = field(default_factory=dict)

class CounterfactualGenerator:
    contexts=['general','high_stakes','low_stakes','time_pressure','shared_context','travel','work']

    def generate(self, state: UserState, n_per_preference: int = 6, seed: int = 0) -> list[SyntheticExperience]:
        rng=random.Random(seed); out=[]
        for key,pref in state.preferences.items():
            space=[str(v) for v in PREFERENCE_SPACE.get(key,[str(pref.value)])]
            alternatives=[v for v in space if v != str(pref.value)]
            for j in range(n_per_preference):
                cf=bool(alternatives) and j%3==0
                assumed=rng.choice(alternatives) if cf else str(pref.value)
                ctx=rng.choice(self.contexts)
                # Boundary targeting: uncertain preferences and context disagreement receive harder samples.
                ctx_value,ctx_conf=pref.value_for_context(ctx)
                boundary_uncertainty=1.0-abs(pref.confidence-.5)*2.0
                contextual_disagreement=1.0 if str(ctx_value)!=str(pref.value) else 0.0
                boundary_score=min(1.0,max(0.0,.65*boundary_uncertainty+.35*contextual_disagreement))
                diff=.30 + .28*float(cf) + .30*boundary_score + rng.random()*.12
                out.append(SyntheticExperience(
                    experience_id=str(uuid.uuid4())[:10], preference_key=key,
                    assumed_value=assumed, context=ctx,
                    prompt=(f'In {ctx}, test whether {key}={assumed} predicts the user choice. '
                            f'Probe near the current decision boundary and preserve uncertainty.'),
                    counterfactual=cf, difficulty=min(1,diff),
                    metadata={
                        'source_confidence':pref.confidence,
                        'true_anchor':str(pref.value),
                        'boundary_score':boundary_score,
                        'contextual_anchor':str(ctx_value),
                        'contextual_confidence':ctx_conf,
                    }
                ))
        return out
