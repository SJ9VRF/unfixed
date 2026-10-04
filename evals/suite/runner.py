from __future__ import annotations
import json, csv, random
from pathlib import Path
from collections import defaultdict
from user_simulator.profiles import SyntheticProfileConfig, generate_user_state
from interaction_engine.simulator import simulate_interactions
from inference.engine import PreferenceInferenceEngine
from training.preference_model import TrainablePreferenceModel, build_training_rows
from synthetic_experience.generator.engine import CounterfactualGenerator
from synthetic_experience.verifier.engine import ExperienceVerifier
from synthetic_experience.selection.engine import select_experiences
from interaction_engine.models import InteractionEvent, SignalType
from evals.suite.metrics import expected_calibration_error

COUNTS=[0,1,3,5,10,20,50]

def _evaluate_heuristic(states,events_by_user,n):
    engine=PreferenceInferenceEngine(); correct=covered=total=hi_err=0; cc=[]
    for st in states:
        pred=engine.infer(st.user_id,events_by_user[st.user_id][:n])
        total+=len(st.preferences)
        for k,true in st.preferences.items():
            p=pred.preferences.get(k)
            if p:
                covered+=1; ok=int(str(p.value)==str(true.value)); correct+=ok
                cc.append((p.confidence,ok)); hi_err+=int((not ok) and p.confidence>=.8)
    return {'accuracy':correct/max(1,total),'coverage':covered/max(1,total),'calibration_error':expected_calibration_error(cc),'high_confidence_error_rate':hi_err/max(1,covered)}

def _evaluate_trainable(model,states,events_by_user,n):
    correct=covered=total=hi_err=0; cc=[]
    for st in states:
        ev=events_by_user[st.user_id][:n]; total+=len(st.preferences)
        for k,true in st.preferences.items():
            value,conf=model.predict(k,ev)
            if value is not None:
                covered+=1; ok=int(value==str(true.value)); correct+=ok; cc.append((conf,ok)); hi_err+=int((not ok) and conf>=.8)
    return {'accuracy':correct/max(1,total),'coverage':covered/max(1,total),'calibration_error':expected_calibration_error(cc),'high_confidence_error_rate':hi_err/max(1,covered)}

def _augment_events_from_synthetic(state,events,seed=0):
    inferred=PreferenceInferenceEngine().infer(state.user_id,events)
    gen=CounterfactualGenerator(); verifier=ExperienceVerifier()
    candidates=gen.generate(inferred,n_per_preference=5,seed=seed)
    checked=[verifier.verify(x,inferred) for x in candidates]
    selected=select_experiences(checked,k=min(10,len(checked)),policy='information_gain',seed=seed)
    out=list(events)
    # Accepted non-counterfactual synthetic experience becomes low-reliability training evidence.
    for i,r in enumerate(selected):
        x=r.experience
        if x.counterfactual: continue
        out.append(InteractionEvent(event_id=f'{state.user_id}-s{i}',user_id=state.user_id,
            preference_key=x.preference_key,observed_value=x.assumed_value,signal_type=SignalType.IMPLICIT,
            reliability=0.42,context=x.context,metadata={'synthetic':True}))
    return out

def run_full_benchmark(out_dir:str|Path='results',n_train:int=240,n_test:int=100,seed:int=13):
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    states=[generate_user_state(f'u{i:04d}',SyntheticProfileConfig(n_preferences=7,seed=seed+i)) for i in range(n_train+n_test)]
    events={s.user_id:simulate_interactions(s,50,seed=seed*100+i) for i,s in enumerate(states)}
    train,test=states[:n_train],states[n_train:]
    train_events={s.user_id:events[s.user_id][:5] for s in train}
    model=TrainablePreferenceModel().fit(build_training_rows(train,train_events))
    augmented={s.user_id:_augment_events_from_synthetic(s,train_events[s.user_id],seed+i) for i,s in enumerate(train)}
    aug_model=TrainablePreferenceModel().fit(build_training_rows(train,augmented))
    rows=[]
    for n in COUNTS:
        for name,metrics in [('retrieval_weighted_vote',_evaluate_heuristic(test,events,n)),('learned_real_only',_evaluate_trainable(model,test,events,n)),('learned_synthetic_augmented',_evaluate_trainable(aug_model,test,events,n))]:
            rows.append({'method':name,'n_interactions':n,**metrics})
    with open(out/'benchmark.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    with open(out/'benchmark.json','w') as f: json.dump(rows,f,indent=2)
    # Selection ablation using representative inferred states.
    sel=[]
    for policy in ['random','uncertainty','diversity','failure_driven','information_gain']:
        vals=[]
        for i,s in enumerate(test[:30]):
            inf=PreferenceInferenceEngine().infer(s.user_id,events[s.user_id][:5]); c=CounterfactualGenerator().generate(inf,5,seed+i)
            v=[ExperienceVerifier().verify(x,inf) for x in c]; picked=select_experiences(v,min(8,len(v)),policy,seed+i)
            vals.append(sum(r.information_value*(1-r.hallucination_risk) for r in picked)/max(1,len(picked)))
        sel.append({'policy':policy,'mean_verified_information_value':sum(vals)/len(vals)})
    with open(out/'selection_ablation.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=sel[0].keys()); w.writeheader(); w.writerows(sel)
    return rows,sel
