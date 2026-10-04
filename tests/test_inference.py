from interaction_engine.models import InteractionEvent,SignalType
from inference.engine import PreferenceInferenceEngine

def test_correction_dominates_conflicting_implicit_signal():
    ev=[InteractionEvent(event_id='a',user_id='u',preference_key='answer_detail',observed_value='detailed',signal_type=SignalType.IMPLICIT,reliability=.55),InteractionEvent(event_id='b',user_id='u',preference_key='answer_detail',observed_value='concise',signal_type=SignalType.CORRECTION,reliability=.99)]
    state=PreferenceInferenceEngine().infer('u',ev)
    assert state.preferences['answer_detail'].value=='concise'
    assert state.preferences['answer_detail'].confidence>=.5
