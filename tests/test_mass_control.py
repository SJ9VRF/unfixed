from interaction_engine.models import InteractionEvent, SignalType
from synthetic_experience.mass_control import cap_synthetic_mass

def test_mass_cap_bounds_total_reliability():
    ev=[InteractionEvent(event_id=str(i),user_id='u',preference_key='k',observed_value='x',signal_type=SignalType.IMPLICIT,reliability=.8,context='work') for i in range(5)]
    out=cap_synthetic_mass(ev,.16,.10)
    assert sum(x.reliability for x in out) <= .1600001
    assert out[-1].reliability <= out[0].reliability
