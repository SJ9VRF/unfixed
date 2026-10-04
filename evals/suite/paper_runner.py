from __future__ import annotations
import csv, json, math, random
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
from synthetic_experience.utility import UtilityCalibratedScorer
from synthetic_experience.mass_control import cap_synthetic_mass
from user_model.probabilistic import CategoricalUserPosterior
from evals.suite.statistics import mean, bootstrap_ci, paired_bootstrap_delta

CONTEXTS=['general','work','travel','high_stakes','casual']

def context_accuracy(model, state, events, n=10):
    ok=tot=0; ev=events[:n]
    for key,p in state.preferences.items():
        for ctx in CONTEXTS:
            truth,_=p.value_for_context(ctx); pred,_=model.predict(key,ev,ctx)
            if pred is not None: ok += int(pred==str(truth)); tot += 1
    return ok/max(1,tot)

def synthetic_event(uid, r, idx, label, policy, reliability=.55):
    x=r.experience
    return InteractionEvent(event_id=f'{uid}-{policy}-{idx}',user_id=uid,preference_key=x.preference_key,
        observed_value=label,signal_type=SignalType.IMPLICIT,reliability=reliability,context=x.context,
        metadata={'synthetic':True,'policy':policy,'oracle':policy=='oracle'})

def oracle_vs_pseudo(out:Path, seed=211, n_train=220, n_test=100):
    states=[generate_user_state(f'op{i:04d}',SyntheticProfileConfig(n_preferences=7,seed=seed+i,context_dependence_rate=.55)) for i in range(n_train+n_test)]
    events={s.user_id:simulate_interactions(s,50,seed=seed*100+i) for i,s in enumerate(states)}
    train,test=states[:n_train],states[n_train:]
    base={s.user_id:events[s.user_id][:5] for s in train}
    gen=CounterfactualGenerator(); verifier=ExperienceVerifier(); scorer=UtilityCalibratedScorer()
    aug={'real_only':base.copy(),'pseudo':{},'oracle':{},'uces':{}}
    label_stats={'pseudo_wrong':0,'pseudo_total':0,'uces_wrong':0,'uces_total':0}
    for i,s in enumerate(train):
        real=base[s.user_id]; inferred=PreferenceInferenceEngine().infer(s.user_id,real)
        checked=[verifier.verify(x,inferred) for x in gen.generate(inferred,12,seed+i)]
        pool=[r for r in checked if r.accepted and not r.experience.counterfactual]
        picked=select_experiences(pool,min(10,len(pool)),'decision_boundary',seed+i)
        pseudo=[]; oracle=[]
        for j,r in enumerate(picked):
            truth=str(r.experience.metadata.get('contextual_anchor',r.experience.metadata.get('true_anchor')))
            plabel=str(r.experience.assumed_value)
            pseudo.append(synthetic_event(s.user_id,r,j,plabel,'pseudo'))
            oracle.append(synthetic_event(s.user_id,r,j,truth,'oracle',.62))
            label_stats['pseudo_total']+=1; label_stats['pseudo_wrong']+=int(plabel!=truth)
        uces=[]
        for j,(r,est) in enumerate(scorer.rank(checked,real,10)):
            plabel=str(r.experience.assumed_value); truth=str(r.experience.metadata.get('contextual_anchor',r.experience.metadata.get('true_anchor')))
            rel=max(.35,min(.72,.35+.42*est.label_probability))
            uces.append(synthetic_event(s.user_id,r,j,plabel,'uces',rel))
            label_stats['uces_total']+=1; label_stats['uces_wrong']+=int(plabel!=truth)
        aug['pseudo'][s.user_id]=real+pseudo; aug['oracle'][s.user_id]=real+oracle; aug['uces'][s.user_id]=real+uces
    models={name:TrainablePreferenceModel().fit(build_training_rows(train,data)) for name,data in aug.items()}
    rows=[]; per={}
    for name,m in models.items():
        vals=[context_accuracy(m,s,events[s.user_id],10) for s in test]; per[name]=vals
        lo,hi=bootstrap_ci(vals,seed=seed+len(name)); rows.append({'method':name,'accuracy':mean(vals),'ci95_low':lo,'ci95_high':hi})
    comps={name:paired_bootstrap_delta(vals,per['real_only'],seed=seed+i) for i,(name,vals) in enumerate(per.items()) if name!='real_only'}
    stats={**label_stats,
           'pseudo_label_error_rate':label_stats['pseudo_wrong']/max(1,label_stats['pseudo_total']),
           'uces_label_error_rate':label_stats['uces_wrong']/max(1,label_stats['uces_total'])}
    with open(out/'paper_oracle_vs_pseudo.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
    (out/'paper_oracle_vs_pseudo.json').write_text(json.dumps({'summary':rows,'paired':comps,'label_stats':stats},indent=2))
    return {'summary':rows,'paired':comps,'label_stats':stats}

def selective_risk(out:Path, seed=223, n_users=250):
    posterior=CategoricalUserPosterior(); points=[]
    records=[]
    for i in range(n_users):
        s=generate_user_state(f'sr{i:04d}',SyntheticProfileConfig(n_preferences=6,seed=seed+i,context_dependence_rate=.5))
        ev=simulate_interactions(s,25,seed=seed*100+i)
        for key,p in s.preferences.items():
            for ctx in CONTEXTS:
                pred=posterior.predict(ev[:8],key,ctx)
                if not pred: continue
                truth=str(p.value_for_context(ctx)[0]); records.append((pred.probability,int(pred.value==truth)))
    for t in [0.35,0.45,0.55,0.65,0.75,0.85,0.9]:
        kept=[ok for conf,ok in records if conf>=t]
        coverage=len(kept)/max(1,len(records)); risk=1-mean(kept) if kept else None
        points.append({'threshold':t,'coverage':coverage,'risk':risk,'selective_accuracy':None if risk is None else 1-risk})
    with open(out/'paper_risk_coverage.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=points[0]); w.writeheader(); w.writerows(points)
    return points

def personalization_regret(out:Path, seed=227, n_users=180):
    rows=[]
    for n in [1,3,5,10,20]:
        regrets=[]
        for i in range(n_users):
            s=generate_user_state(f'rg{i:04d}',SyntheticProfileConfig(n_preferences=6,seed=seed+i,context_dependence_rate=.5))
            ev=simulate_interactions(s,30,seed=seed*100+i)
            inferred=PreferenceInferenceEngine().infer(s.user_id,ev[:n])
            loss=tot=0
            for key,p in s.preferences.items():
                q=inferred.preferences.get(key)
                for ctx in CONTEXTS:
                    truth=str(p.value_for_context(ctx)[0]); pred=str(q.value_for_context(ctx)[0]) if q else None
                    loss += 0 if pred==truth else 1; tot += 1
            regrets.append(loss/max(1,tot))
        lo,hi=bootstrap_ci(regrets,seed=seed+n); rows.append({'n_interactions':n,'mean_regret':mean(regrets),'ci95_low':lo,'ci95_high':hi})
    with open(out/'paper_regret.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    return rows

def synthetic_mass_sweep(out:Path, seed=313, n_train=180, n_test=80):
    states=[generate_user_state(f'ms{i:04d}',SyntheticProfileConfig(n_preferences=7,seed=seed+i,context_dependence_rate=.55)) for i in range(n_train+n_test)]
    events={s.user_id:simulate_interactions(s,50,seed=seed*100+i) for i,s in enumerate(states)}
    train,test=states[:n_train],states[n_train:]
    base={s.user_id:events[s.user_id][:5] for s in train}
    gen=CounterfactualGenerator(); verifier=ExperienceVerifier(); scorer=UtilityCalibratedScorer()
    base_model=TrainablePreferenceModel().fit(build_training_rows(train,base))
    base_score=mean([context_accuracy(base_model,s,events[s.user_id],10) for s in test])
    rows=[{'k':0,'reliability':0.0,'synthetic_mass':0.0,'accuracy':base_score,'delta_vs_real':0.0}]
    for k in [1,2,3,5,8]:
        for rel in [.08,.15,.25,.35,.50]:
            aug={}
            for i,s in enumerate(train):
                real=base[s.user_id]; inf=PreferenceInferenceEngine().infer(s.user_id,real)
                checked=[verifier.verify(x,inf) for x in gen.generate(inf,12,seed+i)]
                picked=scorer.rank(checked,real,k)
                syn=[synthetic_event(s.user_id,r,j,str(r.experience.assumed_value),'mass_sweep',rel) for j,(r,_) in enumerate(picked)]
                aug[s.user_id]=real+syn
            m=TrainablePreferenceModel().fit(build_training_rows(train,aug))
            score=mean([context_accuracy(m,s,events[s.user_id],10) for s in test])
            rows.append({'k':k,'reliability':rel,'synthetic_mass':k*rel,'accuracy':score,'delta_vs_real':score-base_score})
    with open(out/'paper_synthetic_mass_sweep.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    return rows

def drift_baselines(out:Path, seed=229, n_cases=320):
    rng=random.Random(seed); labels=[]; methods={'heuristic':[],'ewma':[],'cusum':[],'bayes_shift':[]}
    for i in range(n_cases):
        s=generate_user_state(f'db{i:04d}',SyntheticProfileConfig(n_preferences=4,seed=seed+i,context_dependence_rate=.1))
        key=rng.choice(list(s.preferences)); original=str(s.preferences[key].value)
        alt=[x for x in ['low','medium','high','concise','balanced','detailed','price','comfort','morning','afternoon','ask_first','structured','flexible'] if x!=original]; target=rng.choice(alt)
        changed=i%2==0
        # Imperfect observations: historical evidence has occasional noise; after a true
        # change the new preference dominates but is not observed perfectly.
        old=[]
        for _ in range(10): old.append(target if rng.random()<.12 else original)
        recent=[]
        for _ in range(6):
            if changed: recent.append(target if rng.random()<.76 else original)
            else: recent.append(target if rng.random()<.18 else original)
        seq=old+recent; ev=[]
        for j,val in enumerate(seq):
            sig=SignalType.CORRECTION if changed and j>=10 and val==target and rng.random()<.35 else SignalType.EXPLICIT
            rel=.99 if sig==SignalType.CORRECTION else rng.uniform(.78,.96)
            ev.append(InteractionEvent(event_id=f'{i}-{j}',user_id=s.user_id,preference_key=key,observed_value=val,signal_type=sig,reliability=rel,context='general'))
        labels.append(int(changed))
        methods['heuristic'].append(PreferenceInferenceEngine().infer(s.user_id,ev).preferences[key].drift_score)
        old_mode=max(set(old),key=old.count); mismatch=[int(v!=old_mode) for v in recent]
        # exponentially emphasize recent mismatches
        weights=[.45,.55,.67,.78,.9,1.0]; methods['ewma'].append(sum(w*m for w,m in zip(weights,mismatch))/sum(weights))
        c=0.0; peak=0.0
        for m in mismatch: c=max(0.0,c+(1.0 if m else -.45)); peak=max(peak,c)
        methods['cusum'].append(min(1.0,peak/3.6))
        post=CategoricalUserPosterior(); p_before=post.posterior(ev[:10],key); p_after=post.posterior(ev[10:],key); keys=set(p_before)|set(p_after); tv=.5*sum(abs(p_before.get(k,0)-p_after.get(k,0)) for k in keys); methods['bayes_shift'].append(tv)
    rows=[]
    for name,scores in methods.items(): rows.append({'method':name,'roc_auc':roc_auc_score(labels,scores)})
    with open(out/'paper_drift_baselines.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    return rows



def mass_aware_mitigation(out:Path, seeds=(701,733,761,797,823), n_train=140, n_test=70):
    """Test whether dataset-level evidence-mass control mitigates augmentation harm."""
    per_seed=[]
    for seed in seeds:
        states=[generate_user_state(f'mc{i:04d}',SyntheticProfileConfig(n_preferences=7,seed=seed+i,context_dependence_rate=.55)) for i in range(n_train+n_test)]
        events={s.user_id:simulate_interactions(s,50,seed=seed*100+i) for i,s in enumerate(states)}
        train,test=states[:n_train],states[n_train:]
        base={s.user_id:events[s.user_id][:5] for s in train}
        gen=CounterfactualGenerator(); verifier=ExperienceVerifier(); scorer=UtilityCalibratedScorer()
        datasets={'real_only':base,'uces_raw':{},'mass_capped_uces':{}}
        for i,state in enumerate(train):
            real=base[state.user_id]; inferred=PreferenceInferenceEngine().infer(state.user_id,real)
            checked=[verifier.verify(x,inferred) for x in gen.generate(inferred,12,seed+i)]
            picked=scorer.rank(checked,real,6)
            raw=[synthetic_event(state.user_id,r,j,str(r.experience.assumed_value),'uces_raw',.35) for j,(r,_) in enumerate(picked)]
            capped=cap_synthetic_mass(raw,max_total_mass=.16,per_signature_cap=.10)
            datasets['uces_raw'][state.user_id]=real+raw
            datasets['mass_capped_uces'][state.user_id]=real+capped
        row={'seed':seed}
        for name,data in datasets.items():
            model=TrainablePreferenceModel().fit(build_training_rows(train,data))
            row[name]=mean([context_accuracy(model,st,events[st.user_id],10) for st in test])
        per_seed.append(row)
    summary=[]
    real=[r['real_only'] for r in per_seed]
    for name in ('real_only','uces_raw','mass_capped_uces'):
        vals=[r[name] for r in per_seed]; lo,hi=bootstrap_ci(vals,seed=991+len(name))
        summary.append({'method':name,'mean_accuracy':mean(vals),'ci95_low':lo,'ci95_high':hi,'delta_vs_real':mean([v-b for v,b in zip(vals,real)])})
    raw_harm=max(1e-12,-next(r['delta_vs_real'] for r in summary if r['method']=='uces_raw'))
    cap_harm=max(0.0,-next(r['delta_vs_real'] for r in summary if r['method']=='mass_capped_uces'))
    recovered=1.0-cap_harm/raw_harm
    with open(out/'paper_mass_control.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
    with open(out/'paper_mass_control_seeds.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=per_seed[0]);w.writeheader();w.writerows(per_seed)
    payload={'summary':summary,'per_seed':per_seed,'fraction_harm_recovered':recovered,'max_total_mass':.16,'per_signature_cap':.10}
    (out/'paper_mass_control.json').write_text(json.dumps(payload,indent=2))
    return payload

def run_paper_suite(out_dir='results'):
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    from evals.response_level.benchmark import run_response_level_benchmark
    payload={'oracle_vs_pseudo':oracle_vs_pseudo(out),'synthetic_mass_sweep':synthetic_mass_sweep(out),'mass_aware_mitigation':mass_aware_mitigation(out),'risk_coverage':selective_risk(out),'regret':personalization_regret(out),'drift_baselines':drift_baselines(out),'response_level':run_response_level_benchmark(out)}
    (out/'paper_results.json').write_text(json.dumps(payload,indent=2))
    return payload

if __name__=='__main__': run_paper_suite()
