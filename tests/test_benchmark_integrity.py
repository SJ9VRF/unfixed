from copy import deepcopy

from inference.engine import PreferenceInferenceEngine
from interaction_engine.simulator import simulate_interactions
from training.preference_model import _features
from user_simulator.profiles import SyntheticProfileConfig, generate_user_state


def _pref_snapshot(state):
    out = {}
    for key, p in state.preferences.items():
        out[key] = {
            "value": str(p.value),
            "confidence": round(float(p.confidence), 12),
            "drift": round(float(p.drift_score), 12),
            "contexts": {
                ctx: (str(v.value), round(float(v.confidence), 12), int(v.evidence_count))
                for ctx, v in p.context_values.items()
            },
        }
    return out


def test_inference_ignores_simulator_ground_truth_metadata():
    user = generate_user_state(
        "integrity-user",
        SyntheticProfileConfig(n_preferences=7, seed=991, context_dependence_rate=0.6),
    )
    events = simulate_interactions(user, 35, seed=992, noise=0.2)
    tampered = deepcopy(events)
    for i, event in enumerate(tampered):
        event.metadata = {
            "ground_truth": f"deliberately-wrong-{i}",
            "noisy": not bool(event.metadata.get("noisy", False)),
            "extra_hidden_label": "must-not-be-read",
        }

    engine = PreferenceInferenceEngine()
    original = engine.infer(user.user_id, events)
    changed = engine.infer(user.user_id, tampered)
    assert _pref_snapshot(original) == _pref_snapshot(changed)


def test_trainable_feature_extractor_ignores_event_metadata():
    user = generate_user_state(
        "feature-integrity-user",
        SyntheticProfileConfig(n_preferences=5, seed=993, context_dependence_rate=0.5),
    )
    events = simulate_interactions(user, 20, seed=994)
    key = next(iter(user.preferences))
    tampered = deepcopy(events)
    for event in tampered:
        event.metadata = {"ground_truth": "wrong", "oracle": True, "secret_target": "wrong"}

    assert _features(events, key, "travel") == _features(tampered, key, "travel")
