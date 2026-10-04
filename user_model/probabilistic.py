from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from math import log
from interaction_engine.models import InteractionEvent, SignalType

@dataclass(frozen=True)
class PosteriorValue:
    value: str
    probability: float

class CategoricalUserPosterior:
    """Small Bayesian state estimator for categorical user preferences.

    Each observed value contributes reliability-weighted pseudo-counts.  Context
    posteriors back off to the global posterior through a symmetric Dirichlet
    prior, which makes uncertainty explicit instead of turning a margin into a
    hand-written confidence score.
    """
    def __init__(self, alpha: float = 0.65, correction_multiplier: float = 1.35):
        self.alpha = float(alpha)
        self.correction_multiplier = float(correction_multiplier)

    def posterior(self, events: list[InteractionEvent], key: str, context: str | None = None) -> dict[str, float]:
        relevant = [e for e in events if e.relevant and e.preference_key == key and e.observed_value is not None]
        if not relevant:
            return {}
        values = sorted({str(e.observed_value) for e in relevant})
        counts = {v: self.alpha for v in values}
        # context evidence is preferred; global evidence provides a weaker backoff
        for e in relevant:
            w = float(e.reliability)
            if e.signal_type == SignalType.CORRECTION:
                w *= self.correction_multiplier
            if context is not None:
                w *= 1.0 if e.context == context else 0.28
            counts[str(e.observed_value)] += w
        z = sum(counts.values())
        return {v: c / z for v, c in counts.items()}

    def predict(self, events: list[InteractionEvent], key: str, context: str | None = None) -> PosteriorValue | None:
        p = self.posterior(events, key, context)
        if not p:
            return None
        value, prob = max(p.items(), key=lambda kv: kv[1])
        return PosteriorValue(value, prob)

    def entropy(self, events: list[InteractionEvent], key: str, context: str | None = None) -> float:
        p = self.posterior(events, key, context)
        return -sum(v * log(max(v, 1e-12)) for v in p.values())

    def label_probability(self, events: list[InteractionEvent], key: str, label: str, context: str | None = None) -> float:
        return float(self.posterior(events, key, context).get(str(label), 0.0))
