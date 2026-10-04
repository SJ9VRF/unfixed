from __future__ import annotations
import random
from interaction_engine.models import InteractionEvent, SignalType
from user_model.schema import UserState
from user_simulator.profiles.generator import PREFERENCE_SPACE

SOURCE_RELIABILITY = {
    SignalType.EXPLICIT: 0.95,
    SignalType.CORRECTION: 0.99,
    SignalType.IMPLICIT: 0.72,
}

CONTEXTS=['general','work','travel','high_stakes','casual']

def simulate_interactions(state: UserState, n: int, seed: int = 0, noise: float = 0.12) -> list[InteractionEvent]:
    rng = random.Random(seed)
    keys = list(state.preferences)
    if not keys or n <= 0:
        return []
    events=[]
    for i in range(n):
        key = rng.choice(keys)
        pref=state.preferences[key]
        ctx = rng.choice(CONTEXTS)
        true, _ = pref.value_for_context(ctx)
        true=str(true)
        signal = rng.choices(
            [SignalType.EXPLICIT, SignalType.IMPLICIT, SignalType.CORRECTION],
            weights=[0.25, 0.65, 0.10], k=1
        )[0]
        wrong = rng.random() < noise * (1.4 if signal == SignalType.IMPLICIT else 0.45)
        if wrong:
            vals = [str(v) for v in PREFERENCE_SPACE.get(key, ['other']) if str(v) != true]
            observed = rng.choice(vals) if vals else 'other'
        else:
            observed = true
        events.append(InteractionEvent(
            event_id=f'{state.user_id}-e{i:04d}', user_id=state.user_id,
            preference_key=key, observed_value=observed, signal_type=signal,
            reliability=SOURCE_RELIABILITY[signal], context=ctx,
            metadata={'ground_truth': true, 'noisy': wrong}
        ))
    return events
