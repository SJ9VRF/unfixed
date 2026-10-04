from user_simulator.profiles import SyntheticProfileConfig,generate_user_state
from synthetic_experience.generator.engine import CounterfactualGenerator
from synthetic_experience.verifier.engine import ExperienceVerifier
from synthetic_experience.selection.engine import select_experiences

def test_synthetic_pipeline_accepts_and_selects():
    s=generate_user_state('u',SyntheticProfileConfig(n_preferences=7,seed=4))
    c=CounterfactualGenerator().generate(s,6,seed=2)
    v=[ExperienceVerifier().verify(x,s) for x in c]
    selected=select_experiences(v,8,'information_gain')
    assert len(c)==42
    assert selected
    assert all(x.accepted for x in selected)
