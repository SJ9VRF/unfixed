from __future__ import annotations
from interaction_engine.models import InteractionEvent,SignalType
from inference.engine import PreferenceInferenceEngine

def evaluate_conflicts(n=100):
    correct=0
    for i in range(n):
        ev=[
          InteractionEvent(event_id=f'{i}a',user_id=str(i),preference_key='travel_priority',observed_value='price',signal_type=SignalType.IMPLICIT,reliability=.6),
          InteractionEvent(event_id=f'{i}b',user_id=str(i),preference_key='travel_priority',observed_value='comfort',signal_type=SignalType.EXPLICIT,reliability=.95),
          InteractionEvent(event_id=f'{i}c',user_id=str(i),preference_key='travel_priority',observed_value='comfort',signal_type=SignalType.CORRECTION,reliability=.99),]
        p=PreferenceInferenceEngine().infer(str(i),ev).preferences['travel_priority']; correct+=str(p.value)=='comfort'
    return {'explicit_correction_resolution_accuracy':correct/n}
