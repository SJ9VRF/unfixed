from __future__ import annotations
import random
from synthetic_experience.verifier.engine import VerificationResult

def select_experiences(results:list[VerificationResult], k:int, policy:str='information_gain', seed:int=0)->list[VerificationResult]:
    pool=[r for r in results if r.accepted]
    if k>=len(pool): return pool
    if policy=='random':
        return random.Random(seed).sample(pool,k)
    if policy=='uncertainty':
        ranked=sorted(pool,key=lambda r:abs(r.consistency-.5))
    elif policy=='diversity':
        chosen=[]; seen=set()
        for r in sorted(pool,key=lambda r:r.novelty,reverse=True):
            sig=(r.experience.preference_key,r.experience.context)
            if sig not in seen:
                chosen.append(r); seen.add(sig)
            if len(chosen)==k:return chosen
        ranked=chosen+[r for r in pool if r not in chosen]
    elif policy=='failure_driven':
        ranked=sorted(pool,key=lambda r:(r.experience.counterfactual,r.experience.difficulty,r.information_value),reverse=True)
    elif policy=='decision_boundary':
        ranked=sorted(pool,key=lambda r:(r.experience.metadata.get('boundary_score',0.0),r.information_value*(1-r.hallucination_risk)),reverse=True)
    else: # information_gain
        ranked=sorted(pool,key=lambda r:r.information_value*r.novelty*(1-r.hallucination_risk),reverse=True)
    return ranked[:k]
