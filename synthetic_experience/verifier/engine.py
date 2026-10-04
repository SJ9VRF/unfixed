from __future__ import annotations
from dataclasses import dataclass
from synthetic_experience.generator.engine import SyntheticExperience
from user_model.schema import UserState

@dataclass
class VerificationResult:
    experience: SyntheticExperience
    plausibility: float
    consistency: float
    novelty: float
    information_value: float
    hallucination_risk: float
    accepted: bool

class ExperienceVerifier:
    def __init__(self, threshold: float=0.56): self.threshold=threshold
    def verify(self, exp:SyntheticExperience, state:UserState, seen_contexts:set[tuple[str,str]]|None=None)->VerificationResult:
        seen_contexts=seen_contexts or set()
        pref=state.preferences.get(exp.preference_key)
        anchor=str(pref.value) if pref else None
        plaus=0.92 if pref else 0.25
        consistency=(0.90 if exp.assumed_value==anchor else 0.52 if exp.counterfactual else 0.18)
        novelty=0.88 if (exp.preference_key,exp.context) not in seen_contexts else 0.35
        info=min(0.98,0.40 + 0.35*exp.difficulty + (0.18 if exp.counterfactual else 0))
        risk=max(0.02, 0.65*(1-consistency) * (1-(pref.confidence if pref else 0.0)))
        score=.24*plaus+.25*consistency+.22*novelty+.29*info-.35*risk
        return VerificationResult(exp,plaus,consistency,novelty,info,risk,score>=self.threshold)
