from __future__ import annotations
import csv, json, statistics
from pathlib import Path
from user_simulator.profiles import SyntheticProfileConfig, generate_user_state
from interaction_engine.simulator import simulate_interactions
from inference.engine import PreferenceInferenceEngine
from training.preference_model import TrainablePreferenceModel, build_training_rows
from personalization.gate import PersonalizationGate, GateExample
from user_simulator.scenarios.templates import SCENARIOS
from synthetic_experience.generator.engine import CounterfactualGenerator
from synthetic_experience.verifier.engine import ExperienceVerifier
from synthetic_experience.selection.engine import select_experiences

CONTEXTS=['general','work','travel','high_stakes','casual']


def _context_accuracy(states, events, n:int):
    engine=PreferenceInferenceEngine(); correct=total=0; context_correct=context_total=0
    for s in states:
        pred=engine.infer(s.user_id,events[s.user_id][:n])
        for key,true_pref in s.preferences.items():
            p=pred.preferences.get(key)
            if not p: continue
            correct += int(str(p.value)==str(true_pref.value)); total += 1
            for ctx in CONTEXTS:
                true_value,_=true_pref.value_for_context(ctx)
                pred_value,_=p.value_for_context(ctx)
                context_correct += int(str(pred_value)==str(true_value)); context_total += 1
    return {'global_accuracy':correct/max(total,1),'context_accuracy':context_correct/max(context_total,1)}


def _trainable_context_accuracy(model,states,events,n:int):
    correct=total=0
    for s in states:
        ev=events[s.user_id][:n]
        for key,p in s.preferences.items():
            for ctx in CONTEXTS:
                true,_=p.value_for_context(ctx); pred,_=model.predict(key,ev,ctx)
                if pred is not None:
                    correct+=int(pred==str(true)); total+=1
    return correct/max(total,1)


def _gate_eval(seed:int=0):
    # Train on candidate (prompt, preference) relevance pairs and evaluate on held-out paraphrases.
    train=[
      GateExample('Choose a cheap or direct flight based on my usual travel tradeoff.','travel_priority',True),
      GateExample('Pick a hotel that matches how I normally balance price and comfort.','travel_priority',True),
      GateExample('Schedule my focused work at the time I tend to perform best.','work_time',True),
      GateExample('Choose a time for deep work tomorrow.','work_time',True),
      GateExample('Make this explanation as concise or detailed as I usually like.','answer_detail',True),
      GateExample('Explain this topic using my normal level of detail.','answer_detail',True),
      GateExample('Decide whether to ask before taking this reversible action.','autonomy',True),
      GateExample('Should the assistant act or ask first here?','autonomy',True),
      GateExample('Handle this sensitive information according to my privacy preferences.','privacy_sensitivity',True),
      GateExample('Should this personal detail be mentioned in a shared context?','privacy_sensitivity',True),
      GateExample('Tailor this decision to how much risk I usually accept.','risk_tolerance',True),
      GateExample('Pick the option that fits my normal risk tolerance.','risk_tolerance',True),
      GateExample('Plan this according to whether I like structure or spontaneity.','planning_style',True),
      GateExample('Use my usual planning style for the weekend.','planning_style',True),
    ]
    keys=['travel_priority','work_time','answer_detail','autonomy','privacy_sensitivity','risk_tolerance','planning_style']
    # Cross-key negatives force semantic relevance rather than a mere has-profile check.
    negative=[]
    for ex in train:
        wrong=next(k for k in keys if k!=ex.preference_key)
        negative.append(GateExample(ex.prompt,wrong,False))
    generic=[
      GateExample('What year was the Eiffel Tower completed?',k,False) for k in keys
    ] + [GateExample('Compute 17 times 24.',k,False) for k in keys]
    gate=PersonalizationGate(dim=256,epochs=320,lr=.14).fit(train+negative+generic)
    test=[
      GateExample('I am booking a trip; optimize the choice using what you know about my travel tradeoffs.','travel_priority',True),
      GateExample('Find the part of the day that best matches when I usually work well.','work_time',True),
      GateExample('Adjust the depth of this technical answer to my preference.','answer_detail',True),
      GateExample('For this harmless reversible change, use my preferred level of assistant autonomy.','autonomy',True),
      GateExample('This might expose personal information; use my privacy preference.','privacy_sensitivity',True),
      GateExample('Use my risk appetite to choose between these two options.','risk_tolerance',True),
      GateExample('Build the itinerary in the planning style I normally prefer.','planning_style',True),
      GateExample('What is the capital of Japan?','travel_priority',False),
      GateExample('Explain gradient descent.','work_time',False),
      GateExample('What is 144 divided by 12?','answer_detail',False),
      GateExample('When was the first moon landing?','autonomy',False),
      GateExample('Define photosynthesis.','privacy_sensitivity',False),
      GateExample('Translate hello into French.','risk_tolerance',False),
      GateExample('What is the boiling point of water?','planning_style',False),
      GateExample('Pick a flight based on my normal tradeoffs.','answer_detail',False),
      GateExample('Make this explanation match my usual detail level.','travel_priority',False),
    ]
    probs=[]; correct=0
    for ex in test:
        p=gate.score(ex.prompt,ex.preference_key); pred=p>=.5
        probs.append((p,int(ex.should_personalize))); correct+=int(pred==ex.should_personalize)
    brier=sum((p-y)**2 for p,y in probs)/len(probs)
    return {'held_out_accuracy':correct/len(test),'brier_score':brier,'n_train':len(train+negative+generic),'n_test':len(test)}

def _boundary_selection_eval(states,events,seed:int):
    scores={p:[] for p in ['random','information_gain','decision_boundary']}
    for i,s in enumerate(states[:40]):
        inferred=PreferenceInferenceEngine().infer(s.user_id,events[s.user_id][:5])
        candidates=CounterfactualGenerator().generate(inferred,8,seed+i)
        checked=[ExperienceVerifier().verify(x,inferred) for x in candidates]
        for policy in scores:
            picked=select_experiences(checked,min(10,len(checked)),policy,seed+i)
            if picked:
                scores[policy].append(sum(r.experience.metadata.get('boundary_score',0.0) for r in picked)/len(picked))
    return {k:sum(v)/max(1,len(v)) for k,v in scores.items()}


def run_v2_benchmark(out_dir='results',n_train=220,n_test=90,seed=29):
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    states=[generate_user_state(f'v2u{i:04d}',SyntheticProfileConfig(n_preferences=7,seed=seed+i,context_dependence_rate=.45)) for i in range(n_train+n_test)]
    events={s.user_id:simulate_interactions(s,60,seed=seed*100+i) for i,s in enumerate(states)}
    train,test=states[:n_train],states[n_train:]
    train_events={s.user_id:events[s.user_id][:20] for s in train}
    model=TrainablePreferenceModel().fit(build_training_rows(train,train_events))
    rows=[]
    for n in [1,3,5,10,20,50]:
        h=_context_accuracy(test,events,n)
        rows.append({'method':'context_aware_inference','n_interactions':n,**h})
        rows.append({'method':'trainable_context_model','n_interactions':n,'global_accuracy':'','context_accuracy':_trainable_context_accuracy(model,test,events,n)})
    gate=_gate_eval(seed)
    boundary=_boundary_selection_eval(test,events,seed)
    with open(out/'v2_context_benchmark.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['method','n_interactions','global_accuracy','context_accuracy']); w.writeheader(); w.writerows(rows)
    payload={'context_benchmark':rows,'anti_personalization_gate':gate,'boundary_selection':boundary}
    (out/'v2_results.json').write_text(json.dumps(payload,indent=2))
    return payload
