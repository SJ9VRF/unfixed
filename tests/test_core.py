from user_model.schema import PreferenceSource
from user_simulator.drift import apply_preference_drift
from user_simulator.profiles import SyntheticProfileConfig, generate_user_state
from evals.cold_start import evaluate_cold_start


def test_profile_generation_is_reproducible():
    a = generate_user_state("u1", SyntheticProfileConfig(seed=7))
    b = generate_user_state("u1", SyntheticProfileConfig(seed=7))
    assert {k: v.value for k, v in a.preferences.items()} == {k: v.value for k, v in b.preferences.items()}


def test_drift_records_conflict():
    state = generate_user_state("u2", SyntheticProfileConfig(n_preferences=7, seed=3))
    key = next(iter(state.preferences))
    old = state.preferences[key].value
    updated = apply_preference_drift(state, key, "changed_value")
    assert updated.preferences[key].value == "changed_value"
    assert f"previous:{old}" in updated.preferences[key].conflicts_with
    assert updated.preferences[key].source == PreferenceSource.EXPLICIT


def test_cold_start_has_requested_points():
    state = generate_user_state("u3", SyntheticProfileConfig(seed=11))
    results = evaluate_cold_start(state)
    assert [r.n_interactions for r in results] == [0, 1, 3, 5, 10, 20, 50]
