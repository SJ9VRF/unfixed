from __future__ import annotations
from user_simulator.profiles import SyntheticProfileConfig,generate_user_state
from user_simulator.drift import apply_preference_drift
from interaction_engine.simulator import simulate_interactions
from inference.engine import PreferenceInferenceEngine

def evaluate_drift(n_users=80,seed=101):
    recovered=[]
    for i in range(n_users):
        s=generate_user_state(f'd{i}',SyntheticProfileConfig(n_preferences=7,seed=seed+i)); key=list(s.preferences)[0]
        vals={'answer_detail':['concise','balanced','detailed'],'planning_style':['spontaneous','structured'],'risk_tolerance':['low','medium','high'],'travel_priority':['price','convenience','comfort'],'autonomy':['ask_first','suggest_first','act_when_reversible'],'privacy_sensitivity':['low','medium','high'],'work_time':['morning','afternoon','evening']}[key]
        new=next(v for v in vals if v!=str(s.preferences[key].value)); before=simulate_interactions(s,12,seed+i)
        changed=apply_preference_drift(s,key,new); after=simulate_interactions(changed,30,seed+1000+i)
        steps=None
        for n in [1,3,5,10,20,30]:
            p=PreferenceInferenceEngine().infer(s.user_id,before[-4:]+after[:n]).preferences.get(key)
            if p and str(p.value)==new: steps=n; break
        recovered.append(steps if steps is not None else 31)
    return {'median_recovery_interactions':sorted(recovered)[len(recovered)//2],'recovered_within_10':sum(x<=10 for x in recovered)/len(recovered)}
