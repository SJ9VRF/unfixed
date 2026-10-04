from __future__ import annotations
import csv, json, random
from dataclasses import dataclass
from pathlib import Path
from collections import Counter, defaultdict
from interaction_engine.models import InteractionEvent
from user_simulator.profiles import SyntheticProfileConfig, generate_user_state
from interaction_engine.simulator import simulate_interactions
from inference.engine import PreferenceInferenceEngine
from user_model.probabilistic import CategoricalUserPosterior
from training.preference_model import TrainablePreferenceModel, build_training_rows
from training.neural_response_ranker import NeuralResponseRanker, RankingExample
from personalization.gate import PersonalizationGate, GateExample
from evals.suite.statistics import mean, bootstrap_ci

CONTEXTS=['general','work','travel','high_stakes','casual']
TASKS={
 'answer_detail':('Explain the recommendation to me.',['Keep it concise: give the decision and one reason.','Give a balanced answer with the main trade-offs.','Give a detailed explanation with assumptions, trade-offs, and edge cases.']),
 'planning_style':('Plan the next block of time.',['Keep it spontaneous with a few flexible options.','Use a structured plan with ordered steps and checkpoints.']),
 'risk_tolerance':('Choose an approach for this uncertain decision.',['Prefer the lower-risk option and preserve reversibility.','Balance upside and downside with a moderate-risk choice.','Prefer the higher-upside option even with more uncertainty.']),
 'travel_priority':('Choose between otherwise viable travel options.',['Choose the lowest-price option.','Choose the most convenient itinerary.','Choose the most comfortable itinerary.']),
 'autonomy':('How should the assistant proceed?',['Ask me before taking action.','Suggest the next action, but let me decide.','Act directly when the action is reversible.']),
 'privacy_sensitivity':('How much personal context should be used here?',['Use minimal personal context and avoid sensitive inference.','Use relevant context, but keep personalization bounded.','Use available personal context aggressively when it improves the answer.']),
 'work_time':('When should focused work be scheduled?',['Schedule it in the morning.','Schedule it in the afternoon.','Schedule it in the evening.']),
}
VALUE_TO_INDEX={
 'answer_detail':{'concise':0,'balanced':1,'detailed':2},
 'planning_style':{'spontaneous':0,'structured':1},
 'risk_tolerance':{'low':0,'medium':1,'high':2},
 'travel_priority':{'price':0,'convenience':1,'comfort':2},
 'autonomy':{'ask_first':0,'suggest_first':1,'act_when_reversible':2},
 'privacy_sensitivity':{'low':0,'medium':1,'high':2},
 'work_time':{'morning':0,'afternoon':1,'evening':2},
}
NO_PERSONALIZE=[
 ('What is 7 multiplied by 8?',['56','Because you like concise answers: 56','Because of your travel preferences: 56']),
 ('Which planet is known as the Red Planet?',['Mars','Given your work schedule, Mars','Since you prefer structured plans, Mars']),
 ('What is the chemical symbol for water?',['H2O','For a privacy-sensitive user: H2O','In your preferred communication style: H2O']),
]

def history_text(events:list[InteractionEvent])->str:
    parts=[]
    for e in events:
        if not e.preference_key or e.observed_value is None: continue
        parts.append(f"In {e.context}, the user signaled {e.preference_key} = {e.observed_value} with {e.signal_type.value} evidence.")
    return ' '.join(parts) if parts else 'No user preference evidence is available.'

@dataclass
class ResponseCase:
    case_id:str; user_id:str; key:str|None; context:str; history:str; query:str; candidates:list[str]; target:int; should_personalize:bool


def build_cases(state,events,n_history:int,seed:int)->list[ResponseCase]:
    cases=[]; hist=history_text(events[:n_history])
    for key,p in state.preferences.items():
        if key not in TASKS: continue
        q,opts=TASKS[key]
        for ctx in CONTEXTS:
            truth=str(p.value_for_context(ctx)[0]); idx=VALUE_TO_INDEX[key][truth]
            cases.append(ResponseCase(f'{state.user_id}-{key}-{ctx}',state.user_id,key,ctx,hist,q,list(opts),idx,True))
    rng=random.Random(seed)
    for j,(q,opts) in enumerate(NO_PERSONALIZE):
        opts=list(opts); # target intentionally fixed at 0; distractors are gratuitous personalization
        cases.append(ResponseCase(f'{state.user_id}-np-{j}',state.user_id,None,'general',hist,q,opts,0,False))
    rng.shuffle(cases)
    return cases


def _fit_gate()->PersonalizationGate:
    ex=[]
    for key,(q,_) in TASKS.items():
        ex.append(GateExample(q,key,True))
        # unrelated preferences should not trigger on a task simply because a user has them
        for other in TASKS:
            if other!=key: ex.append(GateExample(q,other,False))
    for q,_ in NO_PERSONALIZE:
        for key in TASKS: ex.append(GateExample(q,key,False))
    return PersonalizationGate(epochs=160).fit(ex)

def _route(gate:PersonalizationGate,query:str)->tuple[str|None,float]:
    scored=[(gate.score(query,key),key) for key in TASKS]
    score,key=max(scored)
    return (key,score) if score>=.5 else (None,score)

def candidate_text(c:ResponseCase,cand:str)->str:
    return f"HISTORY: {c.history}\nCONTEXT: {c.context}\nQUERY: {c.query}\nCANDIDATE: {cand}"


def _last_event_choice(case:ResponseCase,events:list[InteractionEvent],routed_key:str|None)->int:
    if routed_key is None: return 0
    if case.key is None or routed_key!=case.key: return 1 if case.key is None and len(case.candidates)>1 else 0
    rel=[e for e in events if e.preference_key==routed_key and e.observed_value is not None]
    if not rel: return 0
    contextual=[e for e in rel if e.context==case.context]
    val=str((contextual or rel)[-1].observed_value)
    return VALUE_TO_INDEX[routed_key].get(val,0)


def _inferred_choice(case:ResponseCase,events:list[InteractionEvent],routed_key:str|None,st=None)->int:
    if routed_key is None:return 0
    if case.key is None or routed_key!=case.key:return 1 if case.key is None and len(case.candidates)>1 else 0
    st=st or PreferenceInferenceEngine().infer(case.user_id,events)
    p=st.preferences.get(routed_key)
    if not p:return 0
    val=str(p.value_for_context(case.context)[0])
    return VALUE_TO_INDEX[routed_key].get(val,0)


def _posterior_choice(case:ResponseCase,events:list[InteractionEvent],routed_key:str|None)->int:
    if routed_key is None:return 0
    if case.key is None or routed_key!=case.key:return 1 if case.key is None and len(case.candidates)>1 else 0
    pred=CategoricalUserPosterior().predict(events,routed_key,case.context)
    return VALUE_TO_INDEX[routed_key].get(pred.value,0) if pred else 0


def _trainable_choice(case:ResponseCase,events:list[InteractionEvent],model:TrainablePreferenceModel,routed_key:str|None)->int:
    if routed_key is None:return 0
    if case.key is None or routed_key!=case.key:return 1 if case.key is None and len(case.candidates)>1 else 0
    val,_=model.predict(routed_key,events,case.context)
    return VALUE_TO_INDEX[routed_key].get(str(val),0)


def run_response_level_benchmark(out_dir='results',seed=401,n_train=70,n_test=35,n_history=8):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    states=[generate_user_state(f'rl{i:04d}',SyntheticProfileConfig(n_preferences=7,seed=seed+i,context_dependence_rate=.55)) for i in range(n_train+n_test)]
    events={s.user_id:simulate_interactions(s,40,seed=seed*100+i) for i,s in enumerate(states)}
    train,test=states[:n_train],states[n_train:]
    train_ev={s.user_id:events[s.user_id][:n_history] for s in train}
    structured=TrainablePreferenceModel().fit(build_training_rows(train,train_ev))
    gate=_fit_gate()
    # Response-level natural-language training examples.
    rank_ex=[]
    for i,s in enumerate(train):
        for c in build_cases(s,events[s.user_id],n_history,seed+i):
            for j,cand in enumerate(c.candidates):
                rank_ex.append(RankingExample(c.case_id,candidate_text(c,cand),int(j==c.target)))
    neural=NeuralResponseRanker.fit(rank_ex,seed=seed,epochs=4)
    methods=defaultdict(list); personalize_only=defaultdict(list); np_only=defaultdict(list)
    rows=[]
    for i,s in enumerate(test):
        ev=events[s.user_id][:n_history]
        cases=build_cases(s,events[s.user_id],n_history,seed+1000+i)
        inferred_state=PreferenceInferenceEngine().infer(s.user_id,ev)
        # Score all natural-language candidates for this user in one neural batch.
        flat_texts=[]; spans=[]
        for c in cases:
            a=len(flat_texts); flat_texts.extend(candidate_text(c,x) for x in c.candidates); spans.append((a,len(flat_texts)))
        neural_scores=neural.score(flat_texts)
        for c,(a,b) in zip(cases,spans):
            ns=neural_scores[a:b]
            routed_key,route_score=_route(gate,c.query)
            preds={
              'generic':0,
              'always_personalize_state':(_inferred_choice(c,ev,c.key if c.key is not None else next(iter(TASKS)),inferred_state) if c.key is not None else 1),
              'last_event':_last_event_choice(c,ev,routed_key),
              'inferred_state':_inferred_choice(c,ev,routed_key,inferred_state),
              'bayesian_state':_posterior_choice(c,ev,routed_key),
              'structured_learner':_trainable_choice(c,ev,structured,routed_key),
              'neural_response_ranker':max(range(len(ns)),key=lambda j:ns[j]),
            }
            for name,pred in preds.items():
                ok=int(pred==c.target);methods[name].append(ok)
                (personalize_only if c.should_personalize else np_only)[name].append(ok)
            if len(rows)<180:
                rows.append({'case_id':c.case_id,'key':c.key or 'none','context':c.context,'should_personalize':c.should_personalize,'target':c.target,'neural_pred':preds['neural_response_ranker'],'query':c.query})
    summary=[]
    for name,vals in methods.items():
        lo,hi=bootstrap_ci(vals,seed=seed+len(name))
        p=mean(personalize_only[name]);npa=mean(np_only[name]);over=1-npa
        summary.append({'method':name,'overall_accuracy':mean(vals),'ci95_low':lo,'ci95_high':hi,'personalized_choice_accuracy':p,'no_personalize_accuracy':npa,'overpersonalization_rate':over,'response_regret':1-mean(vals)})
    with open(out/'paper_response_level.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
    with open(out/'paper_response_cases.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    payload={'summary':summary,'n_train_users':n_train,'n_test_users':n_test,'n_history':n_history,'torch_version':__import__('torch').__version__}
    (out/'paper_response_level.json').write_text(json.dumps(payload,indent=2))
    return payload

if __name__=='__main__':
    print(json.dumps(run_response_level_benchmark(),indent=2))
