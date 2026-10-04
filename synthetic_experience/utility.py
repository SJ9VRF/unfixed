from __future__ import annotations
from dataclasses import dataclass
from interaction_engine.models import InteractionEvent
from user_model.probabilistic import CategoricalUserPosterior
from synthetic_experience.verifier.engine import VerificationResult

@dataclass(frozen=True)
class UtilityEstimate:
    label_probability: float
    informativeness: float
    expected_utility: float
    expected_harm: float

class UtilityCalibratedScorer:
    """Scores synthetic experiences by estimated downstream training utility.

    The score explicitly trades off informativeness against the probability that
    the pseudo-label is wrong.  This is deliberately different from active-
    learning-style informativeness, where the queried label is assumed to come
    from a trustworthy oracle.
    """
    def __init__(self, harm_weight: float = 1.65, posterior: CategoricalUserPosterior | None = None):
        self.harm_weight = float(harm_weight)
        self.posterior = posterior or CategoricalUserPosterior()

    def score(self, result: VerificationResult, events: list[InteractionEvent]) -> UtilityEstimate:
        x = result.experience
        # Candidate label probability under the context-conditioned user posterior.
        p_correct = self.posterior.label_probability(events, x.preference_key, x.assumed_value, x.context)
        # Preserve a small amount of verifier evidence, but do not let it replace label calibration.
        p_correct = min(0.995, max(0.005, 0.82 * p_correct + 0.18 * result.consistency))
        informativeness = result.information_value * result.novelty * (1.0 - result.hallucination_risk)
        expected_gain = p_correct * informativeness
        expected_harm = (1.0 - p_correct) * self.harm_weight * (0.45 + 0.55 * informativeness)
        return UtilityEstimate(p_correct, informativeness, expected_gain - expected_harm, expected_harm)

    def rank(self, results: list[VerificationResult], events: list[InteractionEvent], k: int) -> list[tuple[VerificationResult, UtilityEstimate]]:
        scored = [(r, self.score(r, events)) for r in results if r.accepted and not r.experience.counterfactual]
        scored.sort(key=lambda pair: (pair[1].expected_utility, pair[1].label_probability), reverse=True)
        # Abstain from adding examples whose expected training utility is negative.
        positive = [pair for pair in scored if pair[1].expected_utility > 0.0]
        return positive[:k]
