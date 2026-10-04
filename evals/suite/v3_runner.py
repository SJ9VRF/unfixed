from __future__ import annotations
import csv, json, random
from pathlib import Path
from sklearn.metrics import roc_auc_score
from user_simulator.profiles import SyntheticProfileConfig, generate_user_state
from interaction_engine.simulator import simulate_interactions
from interaction_engine.models import InteractionEvent, SignalType
from inference.engine import PreferenceInferenceEngine
from training.preference_model import TrainablePreferenceModel, build_training_rows
from synthetic_experience.generator.engine import CounterfactualGenerator
from synthetic_experience.verifier.engine import ExperienceVerifier
from synthetic_experience.selection.engine import select_experiences
from evals.suite.statistics import mean, bootstrap_ci, paired_bootstrap_delta, standard_error

CONTEXTS=['general','work','travel','high_stakes','casual']
POLICIES=['random','uncertainty','diversity','failure_driven','information_gain','decision_boundary']


def _user_context_accuracy(model, state, events, n:int)->float:
    ok=tot=0; ev=events[:n]
    for key,p in state.preferences.items():
        for ctx in CONTEXTS:
            truth,_=p.value_for_context(ctx); pred,_=model.predict(key,ev,ctx)
            if pred is not None: ok+=int(pred==str(truth)); tot+=1
    return ok/max(1,tot)


def repeated_seed_stability(out:Path, seeds=(7,13,29,41,73), n_train=140, n_test=60):
    records=[]; by_n={n:[] for n in [3,5,10,20,50]}
    for seed in seeds:
        states=[generate_user_state(f's{seed}u{i:04d}',SyntheticProfileConfig(n_preferences=7,seed=seed*1000+i,context_dependence_rate=.45)) for i in range(n_train+n_test)]
        events={s.user_id:simulate_interactions(s,60,seed=seed*10000+i) for i,s in enumerate(states)}
        train,test=states[:n_train],states[n_train:]
        model=TrainablePreferenceModel().fit(build_training_rows(train,{s.user_id:events[s.user_id][:20] for s in train}))
        for n in by_n:
            vals=[_user_context_accuracy(model,s,events[s.user_id],n) for s in test]
            score=mean(vals); by_n[n].append(score)
            records.append({'seed':seed,'n_interactions':n,'context_accuracy':score})
    summary=[]
    for n,vals in by_n.items():
        lo,hi=bootstrap_ci(vals,seed=100+n)
        summary.append({'n_interactions':n,'mean_context_accuracy':mean(vals),'standard_error':standard_error(vals),'ci95_low':lo,'ci95_high':hi,'n_seeds':len(vals)})
    with open(out/'v3_seed_stability.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
    with open(out/'v3_seed_summary.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
    return {'runs':records,'summary':summary}


def _synthetic_to_event(user_id:str, r, idx:int)->InteractionEvent|None:
    x=r.experience
    # Counterfactual candidates are probes, not pseudo-labels. Only anchor-consistent samples become training evidence.
    if x.counterfactual:return None
    rel=max(.28,min(.58,.32+.22*r.consistency-.10*r.hallucination_risk))
    return InteractionEvent(event_id=f'{user_id}-v3syn-{idx}',user_id=user_id,preference_key=x.preference_key,
        observed_value=x.assumed_value,signal_type=SignalType.IMPLICIT,reliability=rel,context=x.context,
        metadata={'synthetic':True,'selection_policy':None,'verification':{'consistency':r.consistency,'risk':r.hallucination_risk}})


def downstream_synthetic_utility(out:Path, seed=91, n_train=180, n_test=80):
    states=[generate_user_state(f'pu{i:04d}',SyntheticProfileConfig(n_preferences=7,seed=seed+i,context_dependence_rate=.45)) for i in range(n_train+n_test)]
    events={s.user_id:simulate_interactions(s,50,seed=seed*100+i) for i,s in enumerate(states)}
    train,test=states[:n_train],states[n_train:]
    base={s.user_id:events[s.user_id][:5] for s in train}
    gen=CounterfactualGenerator(); verifier=ExperienceVerifier()
    models={}
    models['real_only']=TrainablePreferenceModel().fit(build_training_rows(train,base))
    for policy in POLICIES:
        aug={}
        for i,s in enumerate(train):
            real=base[s.user_id]; inf=PreferenceInferenceEngine().infer(s.user_id,real)
            checked=[verifier.verify(x,inf) for x in gen.generate(inf,8,seed+i)]
            picked=select_experiences(checked,min(12,len(checked)),policy,seed+i)
            syn=[]
            for j,r in enumerate(picked):
                e=_synthetic_to_event(s.user_id,r,j)
                if e:
                    e.metadata['selection_policy']=policy; syn.append(e)
            aug[s.user_id]=real+syn
        models[policy]=TrainablePreferenceModel().fit(build_training_rows(train,aug))
    rows=[]; per_user={}
    for name,model in models.items():
        vals=[_user_context_accuracy(model,s,events[s.user_id],10) for s in test]
        per_user[name]=vals; lo,hi=bootstrap_ci(vals,seed=seed+len(name))
        rows.append({'method':name,'mean_context_accuracy':mean(vals),'ci95_low':lo,'ci95_high':hi})
    comparisons={p:paired_bootstrap_delta(per_user[p],per_user['real_only'],seed=seed+i) for i,p in enumerate(POLICIES)}
    with open(out/'v3_synthetic_utility.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    (out/'v3_synthetic_comparisons.json').write_text(json.dumps(comparisons,indent=2))
    return {'summary':rows,'paired_vs_real_only':comparisons}


def noise_stress(out:Path, seed=111):
    noise_levels=[0.0,.08,.16,.24,.32]; rows=[]
    for noise in noise_levels:
        states=[generate_user_state(f'nu{i:03d}',SyntheticProfileConfig(n_preferences=7,seed=seed+i,context_dependence_rate=.45)) for i in range(70)]
        vals=[]
        for i,s in enumerate(states):
            ev=simulate_interactions(s,30,seed=seed*100+i,noise=noise)
            pred=PreferenceInferenceEngine().infer(s.user_id,ev); ok=tot=0
            for k,p in s.preferences.items():
                q=pred.preferences.get(k)
                if q: ok+=int(str(q.value)==str(p.value));tot+=1
            vals.append(ok/max(1,tot))
        lo,hi=bootstrap_ci(vals,seed=seed+int(noise*100))
        rows.append({'noise':noise,'mean_global_accuracy':mean(vals),'ci95_low':lo,'ci95_high':hi})
    with open(out/'v3_noise_stress.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    return rows


def change_detection_eval(out:Path, seed=131):
    """Evaluate whether drift_score separates induced reversals from stationary controls."""
    rng=random.Random(seed); scores=[]; labels=[]; rows=[]
    for i in range(180):
        s=generate_user_state(f'du{i:03d}',SyntheticProfileConfig(n_preferences=5,seed=seed+i,context_dependence_rate=.15))
        key=rng.choice(list(s.preferences)); original=str(s.preferences[key].value)
        alternatives=['low','medium','high','concise','balanced','detailed','price','comfort','directness','morning','afternoon','evening','ask_first','act_if_reversible','structured','flexible']
        alternatives=[x for x in alternatives if x!=original]
        changed=(i%2==0); target=rng.choice(alternatives)
        ev=[]
        for j in range(8):
            ev.append(InteractionEvent(event_id=f'{i}-pre-{j}',user_id=s.user_id,preference_key=key,observed_value=original,signal_type=SignalType.EXPLICIT,reliability=.95,context='general'))
        for j in range(5):
            val=target if changed else original
            sig=SignalType.CORRECTION if changed and j<2 else SignalType.EXPLICIT
            ev.append(InteractionEvent(event_id=f'{i}-post-{j}',user_id=s.user_id,preference_key=key,observed_value=val,signal_type=sig,reliability=.99 if sig==SignalType.CORRECTION else .95,context='general'))
        pred=PreferenceInferenceEngine().infer(s.user_id,ev); score=pred.preferences[key].drift_score
        scores.append(score);labels.append(int(changed));rows.append({'case':i,'changed':int(changed),'drift_score':score})
    auc=roc_auc_score(labels,scores)
    thresholds=[i/100 for i in range(20,91,5)]; best=None
    for t in thresholds:
        tp=sum(y and s>=t for y,s in zip(labels,scores)); fp=sum((not y) and s>=t for y,s in zip(labels,scores)); fn=sum(y and s<t for y,s in zip(labels,scores))
        precision=tp/max(1,tp+fp);recall=tp/max(1,tp+fn);f1=2*precision*recall/max(1e-9,precision+recall)
        cand={'threshold':t,'precision':precision,'recall':recall,'f1':f1}
        if best is None or f1>best['f1']:best=cand
    with open(out/'v3_change_detection.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    return {'roc_auc':auc,'best_operating_point':best,'n_cases':len(rows)}


def run_v3_benchmark(out_dir='results'):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    payload={
      'seed_stability':repeated_seed_stability(out),
      'synthetic_downstream_utility':downstream_synthetic_utility(out),
      'noise_stress':noise_stress(out),
      'change_detection':change_detection_eval(out),
    }
    (out/'v3_results.json').write_text(json.dumps(payload,indent=2))
    return payload
