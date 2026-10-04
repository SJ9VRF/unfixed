from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from user_simulator.profiles import SyntheticProfileConfig,generate_user_state
from interaction_engine.simulator import simulate_interactions
from inference.engine import PreferenceInferenceEngine

def main():
    truth=generate_user_state('demo-user',SyntheticProfileConfig(n_preferences=7,seed=42)); events=simulate_interactions(truth,10,seed=9)
    print('THE UNFIXED USER — visible adaptation demo\n')
    for n in [0,1,3,5,10]:
        pred=PreferenceInferenceEngine().infer(truth.user_id,events[:n])
        print(f'After {n} interactions | uncertainty={pred.global_uncertainty:.2f}')
        for k,p in sorted(pred.preferences.items()): print(f'  {k:20s} -> {p.value:22s} confidence={p.confidence:.2f}')
        print()
if __name__=='__main__': main()
