from user_simulator.profiles import SyntheticProfileConfig,generate_user_state
from interaction_engine.simulator import simulate_interactions
from training.preference_model import TrainablePreferenceModel,build_training_rows

def test_trainable_model_fits_and_predicts():
    ss=[generate_user_state(f'u{i}',SyntheticProfileConfig(n_preferences=7,seed=i)) for i in range(35)]
    ev={s.user_id:simulate_interactions(s,15,seed=100+i) for i,s in enumerate(ss)}
    m=TrainablePreferenceModel().fit(build_training_rows(ss,ev))
    value,conf=m.predict('travel_priority',ev[ss[0].user_id])
    assert value is not None and 0<=conf<=1
