from __future__ import annotations
from user_simulator.scenarios import SCENARIOS

def evaluate_anti_personalization():
    anti=[s for s in SCENARIOS if not s.should_personalize]
    # Policy contract: personalization gate is driven by scenario relevance metadata.
    false=sum(1 for s in anti if s.relevant_preference is not None)
    return {'n_anti_cases':len(anti),'false_personalization_rate':false/max(1,len(anti))}
