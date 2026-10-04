from user_model.probabilistic import CategoricalUserPosterior
from interaction_engine.models import InteractionEvent, SignalType
from synthetic_experience.utility import UtilityCalibratedScorer

def test_probabilistic_posterior_prefers_supported_value():
    ev=[InteractionEvent(event_id=str(i),user_id='u',preference_key='k',observed_value='a',signal_type=SignalType.EXPLICIT,reliability=.9,context='work') for i in range(3)]
    ev.append(InteractionEvent(event_id='x',user_id='u',preference_key='k',observed_value='b',signal_type=SignalType.IMPLICIT,reliability=.4,context='work'))
    p=CategoricalUserPosterior().posterior(ev,'k','work')
    assert p['a']>p['b'] and abs(sum(p.values())-1)<1e-9

def test_utility_scorer_available():
    assert UtilityCalibratedScorer(harm_weight=1.2).harm_weight==1.2
