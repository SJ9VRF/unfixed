from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable

from user_model.schema import UserState


@dataclass
class ColdStartResult:
    n_interactions: int
    personalization_accuracy: float
    calibration_error: float
    incorrect_personalization_rate: float


def simulate_observation(true_state: UserState, n_interactions: int, seed: int = 0) -> dict[str, tuple[object, float]]:
    """Toy observation model used to validate benchmark plumbing before model integration."""
    rng = random.Random(seed + n_interactions)
    learned = {}
    keys = list(true_state.preferences)
    if not keys or n_interactions <= 0:
        return learned
    exposure_prob = min(1.0, n_interactions / max(1, len(keys) * 2))
    for key in keys:
        if rng.random() < exposure_prob:
            true_pref = true_state.preferences[key]
            confidence = min(0.98, 0.35 + 0.08 * n_interactions + rng.uniform(-0.08, 0.08))
            # Early interaction noise simulates incorrect preference inference.
            correct = rng.random() < min(0.97, 0.55 + 0.04 * n_interactions)
            learned[key] = (true_pref.value if correct else "unknown_or_wrong", confidence)
    return learned


def evaluate_cold_start(true_state: UserState, interaction_counts: Iterable[int] = (0, 1, 3, 5, 10, 20, 50), seed: int = 0) -> list[ColdStartResult]:
    results = []
    total = max(1, len(true_state.preferences))
    for n in interaction_counts:
        learned = simulate_observation(true_state, n, seed)
        correct = 0
        calibration_terms = []
        incorrect_high_conf = 0
        for key, (value, confidence) in learned.items():
            is_correct = value == true_state.preferences[key].value
            correct += int(is_correct)
            calibration_terms.append(abs(confidence - float(is_correct)))
            incorrect_high_conf += int((not is_correct) and confidence >= 0.7)
        accuracy = correct / total
        calibration_error = sum(calibration_terms) / len(calibration_terms) if calibration_terms else 0.0
        incorrect_rate = incorrect_high_conf / max(1, len(learned))
        results.append(ColdStartResult(n, accuracy, calibration_error, incorrect_rate))
    return results
