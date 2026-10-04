from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from user_simulator.profiles import SyntheticProfileConfig, generate_user_state
from interaction_engine.simulator import simulate_interactions
from inference.engine import PreferenceInferenceEngine
from synthetic_experience.generator.engine import CounterfactualGenerator
from synthetic_experience.verifier.engine import ExperienceVerifier
from synthetic_experience.selection.engine import select_experiences
from personalization.gate import PersonalizationGate, GateExample
from backends import AgentRequest, LocalPersonalAgentBackend

app=FastAPI(title='The Unfixed User',version='3.0.0',description='Offline reference API for calibrated, context-aware personalization research.')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=False, allow_methods=['*'], allow_headers=['*'])

class SimRequest(BaseModel):
    user_id:str='demo'
    seed:int=42
    interactions:int=5

class RespondRequest(SimRequest):
    prompt:str='Choose a flight for my trip.'
    context:str='travel'
    relevant_preference:str|None='travel_priority'


def _reference_gate():
    return PersonalizationGate(dim=128,epochs=220).fit([
        GateExample('choose a flight for my trip','travel_priority',True),
        GateExample('pick a hotel for travel','travel_priority',True),
        GateExample('schedule my deep work','work_time',True),
        GateExample('match my usual answer detail','answer_detail',True),
        GateExample('what is 2 plus 2','travel_priority',False),
        GateExample('define photosynthesis','answer_detail',False),
        GateExample('capital of Japan','work_time',False),
    ])

@app.get('/health')
def health(): return {'status':'ok','version':'3.0.0'}

@app.post('/simulate')
def simulate(req:SimRequest):
    truth=generate_user_state(req.user_id,SyntheticProfileConfig(n_preferences=7,seed=req.seed,context_dependence_rate=.45))
    events=simulate_interactions(truth,req.interactions,seed=req.seed+1)
    inferred=PreferenceInferenceEngine().infer(req.user_id,events)
    return {'ground_truth':truth.model_dump(mode='json'),'events':[e.model_dump(mode='json') for e in events],'inferred':inferred.model_dump(mode='json')}

@app.post('/synthetic')
def synthetic(req:SimRequest):
    truth=generate_user_state(req.user_id,SyntheticProfileConfig(n_preferences=7,seed=req.seed,context_dependence_rate=.45))
    events=simulate_interactions(truth,req.interactions,seed=req.seed+1)
    inferred=PreferenceInferenceEngine().infer(req.user_id,events)
    candidates=CounterfactualGenerator().generate(inferred,6,req.seed)
    checked=[ExperienceVerifier().verify(x,inferred) for x in candidates]
    selected=select_experiences(checked,min(12,len(checked)),'decision_boundary',req.seed)
    return {'candidate_count':len(candidates),'accepted_count':sum(x.accepted for x in checked),'selected':[{'experience':r.experience.__dict__,'scores':{'plausibility':r.plausibility,'consistency':r.consistency,'novelty':r.novelty,'information_value':r.information_value,'hallucination_risk':r.hallucination_risk}} for r in selected]}

@app.post('/respond')
def respond(req:RespondRequest):
    truth=generate_user_state(req.user_id,SyntheticProfileConfig(n_preferences=7,seed=req.seed,context_dependence_rate=.45))
    events=simulate_interactions(truth,req.interactions,seed=req.seed+1)
    state=PreferenceInferenceEngine().infer(req.user_id,events)
    result=LocalPersonalAgentBackend(_reference_gate()).respond(AgentRequest(req.prompt,req.context,req.relevant_preference),state)
    return {'response':result.__dict__,'inferred_state':state.model_dump(mode='json')}

@app.get('/demo')
def demo_page():
    return FileResponse('demo/index.html')
