from __future__ import annotations

from copy import deepcopy
from user_model.schema import PreferenceSource, UserState


def apply_preference_drift(state: UserState, key: str, new_value, confidence: float = 0.8) -> UserState:
    updated = deepcopy(state)
    pref = updated.preferences[key]
    old_value = pref.value
    pref.value = new_value
    pref.confidence = confidence
    pref.source = PreferenceSource.EXPLICIT
    pref.evidence_count += 1
    pref.conflicts_with.append(f"previous:{old_value}")
    pref.uncertainty_reason = "Preference recently changed; confidence is temporarily reduced."
    updated.global_uncertainty = min(1.0, updated.global_uncertainty + 0.2)
    return updated
