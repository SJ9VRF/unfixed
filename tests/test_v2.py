from interaction_engine.models import InteractionEvent, SignalType
from inference.engine import PreferenceInferenceEngine
from personalization.gate import PersonalizationGate, GateExample
from backends import AgentRequest, CompletionAdapter, GroundedFoundationBackend
from user_model.schema import PreferenceRecord, PreferenceSource, UserState
from synthetic_experience.generator.engine import CounterfactualGenerator
from synthetic_experience.verifier.engine import ExperienceVerifier
from synthetic_experience.selection.engine import select_experiences


def test_context_conditioned_inference():
    events=[]
    for i in range(4):
        events.append(InteractionEvent(event_id=f'g{i}',user_id='u',preference_key='answer_detail',observed_value='concise',signal_type=SignalType.EXPLICIT,reliability=.95,context='general'))
    for i in range(4):
        events.append(InteractionEvent(event_id=f'w{i}',user_id='u',preference_key='answer_detail',observed_value='detailed',signal_type=SignalType.EXPLICIT,reliability=.95,context='work'))
    state=PreferenceInferenceEngine().infer('u',events)
    pref=state.preferences['answer_detail']
    assert pref.value_for_context('work')[0]=='detailed'
    assert pref.value_for_context('general')[0]=='concise'


def test_drift_score_flags_recent_reversal():
    events=[]
    for i in range(8):
        events.append(InteractionEvent(event_id=f'a{i}',user_id='u',preference_key='travel_priority',observed_value='price',signal_type=SignalType.IMPLICIT,reliability=.72,context='travel'))
    for i in range(4):
        events.append(InteractionEvent(event_id=f'b{i}',user_id='u',preference_key='travel_priority',observed_value='comfort',signal_type=SignalType.CORRECTION,reliability=.99,context='travel'))
    pref=PreferenceInferenceEngine().infer('u',events).preferences['travel_priority']
    assert pref.drift_score >= .62


def test_semantic_gate_and_grounded_backend():
    gate=PersonalizationGate(dim=128,epochs=250).fit([
        GateExample('pick a flight for my trip','travel_priority',True),
        GateExample('choose a hotel for travel','travel_priority',True),
        GateExample('what is 2 plus 2','travel_priority',False),
        GateExample('define photosynthesis','travel_priority',False),
    ])
    state=UserState(user_id='u',preferences={'travel_priority':PreferenceRecord(key='travel_priority',value='comfort',confidence=.9,source=PreferenceSource.EXPLICIT)})
    backend=GroundedFoundationBackend(CompletionAdapter(lambda p:'ok'),gate)
    r=backend.respond(AgentRequest('choose a flight for my trip',context='travel',relevant_preference='travel_priority'),state)
    assert r.personalized and r.preference_used=='travel_priority' and r.text=='ok'


def test_decision_boundary_selection_targets_boundary():
    state=UserState(user_id='u',preferences={'answer_detail':PreferenceRecord(key='answer_detail',value='balanced',confidence=.52,source=PreferenceSource.INFERRED)})
    candidates=CounterfactualGenerator().generate(state,12,3)
    checked=[ExperienceVerifier().verify(x,state) for x in candidates]
    picked=select_experiences(checked,4,'decision_boundary',3)
    random=select_experiences(checked,4,'random',3)
    assert sum(x.experience.metadata['boundary_score'] for x in picked)/len(picked) >= sum(x.experience.metadata['boundary_score'] for x in random)/len(random)
