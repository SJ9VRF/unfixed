from __future__ import annotations
from user_simulator.profiles import SyntheticProfileConfig,generate_user_state
from interaction_engine.simulator import simulate_interactions
from inference.engine import PreferenceInferenceEngine

def evaluate_long_horizon(n_users=50,turns=(20,50,100,250),seed=70):
    rows=[]
    for t in turns:
        acc=[]
        for i in range(n_users):
            s=generate_user_state(f'l{i}',SyntheticProfileConfig(n_preferences=7,seed=seed+i)); ev=simulate_interactions(s,t,seed+i)
            p=PreferenceInferenceEngine().infer(s.user_id,ev); acc.append(sum(str(p.preferences[k].value)==str(v.value) for k,v in s.preferences.items() if k in p.preferences)/len(s.preferences))
        rows.append({'turns':t,'preference_state_accuracy':sum(acc)/len(acc)})
    return rows
